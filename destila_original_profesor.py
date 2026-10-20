"""
destila.py · Taller de destilación en pequeño: un LLM grande (profesor, API de OpenAI)
enseña a un modelo pequeño (estudiante, ~135 M parámetros) que corre en tu CPU.

Todo el kit cabe en este archivo. Se usa de dos formas:
  · Desde el notebook  taller_destilacion.ipynb  (paso a paso, recomendado para el taller)
  · Desde la terminal:  python destila.py             (todo de una vez)
                        python destila.py --sin-internet   (sin clave, sin descargas: profesor y estudiante locales)

Las 6 etapas:
  1) configurar      → lee .env, decide profesor (OpenAI u offline) y dispositivo (CPU/GPU/Mac)
  2) generar_datos   → el profesor escribe preguntas y respuestas del dominio (entrenamiento + examen)
  3) cargar_estudiante → descarga el modelo pequeño y le agrega adaptadores LoRA
  4) evaluar         → el estudiante rinde el examen y el juez (profesor) lo califica de 1 a 10
  5) entrenar        → ajuste fino supervisado (SFT) con LoRA sobre las respuestas del profesor
  6) comparar        → nota antes vs. después, gráfico, checkpoint y ejemplos lado a lado
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "datos"
SALIDAS = AQUI / "salidas"

# =============================================================================
# 0 · CONFIGURACIÓN  (todo lo ajustable del taller está aquí)
# =============================================================================
CONFIG = {
    # --- qué debe aprender el estudiante ---
    "dominio": "asistente que explica conceptos de inteligencia artificial generativa a ejecutivos "
               "de empresas chilenas, con ejemplos de negocio",
    "temas": ["Fundamentos de LLM", "Ingeniería de prompts", "RAG", "Agentes de IA", "Ajuste fino",
              "Evaluación y LLMOps"],
    "idioma": "español neutro (Chile)",
    # --- tamaño del taller (pensado para CPU, ≈ 10 minutos) ---
    "n_entrenamiento": 60,      # pares pregunta-respuesta que escribe el profesor
    "n_examen": 12,             # preguntas del examen (nunca se entrena con ellas)
    "epocas": 3,                # pasadas de entrenamiento
    "lote": 4,
    "tasa_aprendizaje": 5e-4,
    "lora_r": 16,
    "max_tokens_ejemplo": 320,  # largo máximo (pregunta + respuesta) al entrenar
    "max_tokens_respuesta": 120,  # largo máximo de respuesta del estudiante
    "max_palabras_profesor": 90,  # respuestas cortas = estudiante pequeño aprende mejor
    # --- modelos ---
    "estudiante": "HuggingFaceTB/SmolLM2-135M-Instruct",   # Llama de 135 M · 270 MB · corre en CPU
    #   alternativas: "HuggingFaceTB/SmolLM2-360M-Instruct" (mejor, 2–3× más lento)
    #                 "tiny" (modelo diminuto creado localmente, sin internet)
    "profesor": os.getenv("OPENAI_MODEL", "gpt-6-luna"),   # barato: US$ 0,10 / 0,50 por millón de tokens
    "juez": os.getenv("OPENAI_MODEL_JUDGE", "gpt-6-luna"),
    "semilla": 42,
}

SISTEMA_ESTUDIANTE = "Eres un asistente experto en IA generativa. Responde en español, de forma clara y breve."


def configurar(sin_internet: bool = False, estudiante: str | None = None) -> dict:
    """Lee .env, fija semillas y decide el modo de trabajo. Devuelve la configuración efectiva."""
    cfg = dict(CONFIG)
    _cargar_env(AQUI / ".env")
    cfg["api_key"] = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    cfg["sin_internet"] = sin_internet
    if estudiante:
        cfg["estudiante"] = estudiante
    if sin_internet:
        cfg["estudiante"] = "tiny"
        cfg["profesor_modo"] = "offline"
    elif cfg["api_key"]:
        cfg["profesor_modo"] = "openai"
    else:
        cfg["profesor_modo"] = "offline"
        print("⚠  Sin OPENAI_API_KEY en .env → se usa el profesor OFFLINE (simulado). "
              "Para el profesor real, pega tu clave en .env.")
    if cfg["estudiante"] == "tiny":  # modelo diminuto desde cero: necesita más épocas y tasa más alta
        cfg.update({"epocas": 15, "tasa_aprendizaje": 3e-3, "lora_r": 16, "n_entrenamiento": 80, "max_tokens_respuesta": 70})
    import torch

    torch.manual_seed(cfg["semilla"])
    random.seed(cfg["semilla"])
    cfg["dispositivo"] = ("cuda" if torch.cuda.is_available()
                          else "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
                          else "cpu")
    if cfg["dispositivo"] == "cpu":
        torch.set_num_threads(max(1, os.cpu_count() or 1))
    DATOS.mkdir(exist_ok=True)
    SALIDAS.mkdir(exist_ok=True)
    print(f"✔ Configuración: profesor = {cfg['profesor_modo']} ({cfg['profesor'] if cfg['profesor_modo']=='openai' else 'simulado'}) · "
          f"estudiante = {cfg['estudiante']} · dispositivo = {cfg['dispositivo']}")
    return cfg


def _cargar_env(ruta: Path) -> None:
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            k, v = linea.split("=", 1)
            v = v.split(" #")[0].strip().strip('"').strip("'")
            if v:
                os.environ[k.strip()] = v


# =============================================================================
# 1 · PROFESOR  (OpenAI)  y  PROFESOR OFFLINE  (sin red, para practicar)
# =============================================================================
class Profesor:
    """Llama a la API de OpenAI y pide siempre JSON. Lleva la cuenta de tokens y costo."""

    PRECIOS = {"gpt-6-luna": (0.10, 0.50), "gpt-6-sol": (2.0, 10.0), "gpt-5-mini": (0.25, 2.0),
               "gpt-4.1-mini": (0.40, 1.60), "gpt-4o-mini": (0.15, 0.60)}

    def __init__(self, cfg: dict):
        from openai import OpenAI

        self.cfg = cfg
        self.cliente = OpenAI(api_key=cfg["api_key"], base_url=os.getenv("OPENAI_BASE_URL") or None, max_retries=3)
        self.tokens_entrada = self.tokens_salida = 0
        self.llamadas = 0
        self.costo = 0.0

    def json(self, modelo: str, sistema: str, usuario: str, max_tokens: int = 1500) -> dict:
        for intento in range(3):
            r = self.cliente.chat.completions.create(
                model=modelo, max_completion_tokens=max_tokens, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": sistema + "\nResponde ÚNICAMENTE con un objeto JSON válido."},
                          {"role": "user", "content": usuario}])
            self.llamadas += 1
            if r.usage:
                self.tokens_entrada += r.usage.prompt_tokens
                self.tokens_salida += r.usage.completion_tokens
                pe, ps = self.PRECIOS.get(modelo, (0.5, 2.0))
                self.costo += (r.usage.prompt_tokens * pe + r.usage.completion_tokens * ps) / 1e6
            texto = r.choices[0].message.content or ""
            try:
                return json.loads(texto)
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", texto, flags=re.DOTALL)
                if m:
                    try:
                        return json.loads(m.group(0))
                    except json.JSONDecodeError:
                        pass
        raise RuntimeError("El profesor no devolvió JSON válido tras 3 intentos.")

    def resumen(self) -> str:
        return (f"{self.llamadas} llamadas · {self.tokens_entrada:,} tokens de entrada · "
                f"{self.tokens_salida:,} de salida · ≈ US$ {self.costo:.4f}")


# Base de conocimiento del profesor offline: (concepto → definición, dato clave, uso)
_KB = {
    "Fundamentos de LLM": {
        "transformer": ("Un transformer es una red neuronal basada en atención que procesa secuencias en paralelo.", "Reemplazó a las redes recurrentes porque escala mejor con datos y cómputo.", "sirve de base a los asistentes que redactan y resumen documentos"),
        "atención": ("La atención pondera qué partes del contexto son relevantes para cada palabra generada.", "Su costo crece con el cuadrado del largo del texto.", "permite relacionar una consulta con la cláusula exacta de un reglamento"),
        "tokenización": ("La tokenización divide el texto en unidades llamadas tokens antes de entrar al modelo.", "El costo y el límite de contexto se miden en tokens, no en palabras.", "ayuda a estimar el costo mensual de procesar miles de solicitudes"),
        "ventana de contexto": ("La ventana de contexto es la cantidad máxima de tokens que el modelo considera a la vez.", "Si la información no cabe, el modelo no puede usarla.", "obliga a resumir o recuperar solo los documentos pertinentes"),
        "temperatura": ("La temperatura controla la aleatoriedad al generar texto.", "Valores bajos dan respuestas estables y valores altos, respuestas creativas.", "conviene usar temperatura baja en respuestas normativas"),
    },
    "Ingeniería de prompts": {
        "few-shot": ("Few-shot consiste en incluir ejemplos resueltos dentro del prompt.", "El modelo imita el patrón sin reentrenarse.", "mejora la clasificación de reclamos con pocos casos de muestra"),
        "cadena de pensamiento": ("La cadena de pensamiento pide al modelo razonar por pasos antes de responder.", "Mejora problemas de varios pasos a cambio de más tokens.", "es útil para cálculos de cuotas o plazos"),
        "rol de sistema": ("El rol de sistema fija la identidad, el tono y las reglas del asistente.", "Tiene prioridad sobre las instrucciones del usuario.", "asegura que el asistente respete las políticas internas"),
        "formato de salida": ("Definir el formato de salida indica la estructura exacta de la respuesta.", "Un esquema JSON facilita integrarla con otros sistemas.", "permite cargar resultados directo en un tablero"),
    },
    "RAG": {
        "embeddings": ("Un embedding es un vector numérico que representa el significado de un texto.", "Textos parecidos quedan cerca en el espacio vectorial.", "permite encontrar documentos similares a la pregunta del cliente"),
        "base vectorial": ("Una base vectorial almacena embeddings y busca los más cercanos a una consulta.", "Es el motor de recuperación de un sistema RAG.", "indexa manuales y políticas para responder con evidencia"),
        "chunking": ("El chunking divide los documentos en fragmentos antes de indexarlos.", "Fragmentos muy grandes diluyen la relevancia y muy pequeños pierden contexto.", "se ajusta según la estructura de cada documento"),
        "alucinación": ("Una alucinación es una respuesta fluida pero falsa o sin respaldo.", "RAG la reduce al obligar al modelo a citar fuentes.", "se controla exigiendo citas y validando contra documentos"),
    },
    "Agentes de IA": {
        "herramientas": ("Las herramientas son funciones externas que el agente puede invocar, como APIs o bases de datos.", "Extienden al modelo más allá del texto.", "permiten consultar saldos o crear tickets"),
        "planificación": ("La planificación descompone un objetivo en pasos ordenados antes de ejecutarlos.", "Reduce errores en tareas largas.", "organiza un flujo de varias aprobaciones"),
        "memoria": ("La memoria guarda información de interacciones previas para usarla después.", "Puede ser de corto plazo en el contexto o de largo plazo en una base externa.", "recuerda las preferencias de cada cliente"),
        "guardrails": ("Los guardrails son controles que limitan lo que el agente puede decir o hacer.", "Incluyen validaciones, acciones permitidas y aprobación humana.", "evitan operaciones riesgosas sin supervisión"),
    },
    "Ajuste fino": {
        "LoRA": ("LoRA entrena matrices pequeñas de bajo rango y deja congelados los pesos originales.", "Entrena menos del uno por ciento de los parámetros.", "permite especializar un modelo con una sola GPU"),
        "destilación": ("La destilación transfiere el conocimiento de un modelo grande profesor a uno pequeño estudiante.", "El estudiante aprende de las respuestas del profesor.", "produce un modelo local más barato y rápido"),
        "sobreajuste": ("El sobreajuste ocurre cuando el modelo memoriza el entrenamiento y generaliza mal.", "Se detecta con un examen separado.", "se evita con más datos variados y menos épocas"),
        "olvido catastrófico": ("El olvido catastrófico es la pérdida de habilidades previas al entrenar con datos nuevos.", "Se mitiga repasando datos antiguos.", "protege lo aprendido en rondas anteriores"),
    },
    "Evaluación y LLMOps": {
        "LLM como juez": ("Un LLM como juez califica respuestas con una rúbrica y una referencia.", "Escala la evaluación pero puede tener sesgos.", "mide la calidad de cada versión del modelo"),
        "examen fijo": ("Un examen fijo es un conjunto de preguntas que nunca se usa para entrenar.", "Hace comparables las notas entre versiones.", "verifica si el entrenamiento mejoró al modelo"),
        "monitoreo": ("El monitoreo registra métricas de calidad, costo y latencia en operación.", "Permite detectar degradaciones a tiempo.", "alerta cuando la calidad cae bajo el umbral"),
        "checkpoint": ("Un checkpoint es una copia guardada de los pesos del modelo durante el entrenamiento.", "Permite reanudar o volver a una versión mejor.", "permite revertir si una ronda empeora la calidad"),
    },
}
_CONTEXTOS = ["un banco", "una AFP", "un retail", "una clínica", "una universidad", "una empresa de logística"]
_PLANTILLAS = ["Explica qué es {c} y para qué sirve en {x}.", "¿Cómo aplicarías {c} en {x}?",
               "Describe {c} con un ejemplo para {x}.", "¿Qué ventajas tiene {c} para {x}?",
               "Resume el concepto de {c} pensando en {x}."]


class ProfesorOffline:
    """Imita al profesor sin red: respuestas desde una base de conocimiento y juez por solapamiento de palabras."""

    def __init__(self, cfg: dict):
        self.rng = random.Random(cfg["semilla"])
        self.llamadas = 0

    def preguntas(self, tema: str, n: int) -> list[str]:
        conceptos = list(_KB.get(tema, next(iter(_KB.values()))))
        return [self.rng.choice(_PLANTILLAS).format(c=self.rng.choice(conceptos), x=self.rng.choice(_CONTEXTOS))
                for _ in range(n)]

    def responder(self, pregunta: str) -> str:
        self.llamadas += 1
        for conceptos in _KB.values():
            for c in sorted(conceptos, key=len, reverse=True):
                if c in pregunta:
                    d, k, u = conceptos[c]
                    x = next((x for x in _CONTEXTOS if x in pregunta), _CONTEXTOS[0])
                    return f"{d} {k} En {x}, {u}."
        return "No tengo información sobre ese concepto."

    def juzgar(self, pregunta: str, referencia: str, respuesta: str) -> tuple[int, str]:
        self.llamadas += 1
        ref, est = Counter(_palabras(referencia)), Counter(_palabras(respuesta))
        comun = sum((ref & est).values())
        p = comun / max(sum(est.values()), 1)
        r = comun / max(sum(ref.values()), 1)
        f1 = 2 * p * r / max(p + r, 1e-9)
        faltan = [w for w, _ in (ref - est).most_common(3)]
        return max(1, min(10, round(1 + 9 * f1))), ("Faltan ideas clave: " + ", ".join(faltan) if faltan else "Cubre lo esencial.")

    def resumen(self) -> str:
        return f"{self.llamadas} respuestas simuladas · costo US$ 0"


_STOP = set("el la los las un una unos unas de del en y o que a al para por con se es su sus lo como mas más este esta pero sin sobre entre cada ya muy no".split())


def _palabras(s: str) -> list[str]:
    import unicodedata

    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return [w for w in re.findall(r"[a-z0-9ñ]+", s) if w not in _STOP and len(w) > 2]


# =============================================================================
# 2 · GENERAR DATOS  (entrenamiento + examen)
# =============================================================================
def generar_datos(cfg: dict, profesor, forzar: bool = False) -> tuple[list[dict], list[dict]]:
    """El profesor escribe preguntas por tema y luego las responde. Guarda datos/entrenamiento.jsonl y datos/examen.jsonl."""
    f_tr, f_ex = DATOS / "entrenamiento.jsonl", DATOS / "examen.jsonl"
    if f_tr.exists() and f_ex.exists() and not forzar:
        tr, ex = _leer(f_tr), _leer(f_ex)
        print(f"✔ Datos existentes reutilizados: {len(tr)} de entrenamiento · {len(ex)} de examen (borra datos/ para regenerar)")
        return tr, ex
    t0 = time.time()
    total = cfg["n_entrenamiento"] + cfg["n_examen"]
    por_tema = -(-total // len(cfg["temas"]))  # redondeo hacia arriba
    preguntas: list[dict] = []
    if isinstance(profesor, ProfesorOffline):
        for tema in cfg["temas"]:
            preguntas += [{"tema": tema, "pregunta": q} for q in profesor.preguntas(tema, por_tema)]
    else:
        print(f"→ El profesor ({cfg['profesor']}) escribe {total} preguntas sobre {len(cfg['temas'])} temas…")

        def _tema(tema):
            d = profesor.json(cfg["profesor"],
                              "Eres un diseñador instruccional. Escribes preguntas realistas, variadas y autocontenidas.",
                              f"Dominio del asistente: {cfg['dominio']}\nTema: {tema}\nIdioma: {cfg['idioma']}\n"
                              f"Escribe exactamente {por_tema} preguntas distintas que un usuario real haría sobre este tema "
                              f"(explicaciones, comparaciones, casos aplicados, errores comunes). Una a dos oraciones cada una.\n"
                              'Formato: {"preguntas": ["...", "..."]}', max_tokens=1500)
            return [{"tema": tema, "pregunta": q.strip()} for q in d.get("preguntas", []) if len(q.strip()) > 10]

        with ThreadPoolExecutor(6) as ex:
            for lote in ex.map(_tema, cfg["temas"]):
                preguntas += lote
    # sin duplicados exactos
    vistas, unicas = set(), []
    for p in preguntas:
        k = p["pregunta"].lower()
        if k not in vistas:
            vistas.add(k)
            unicas.append(p)
    preguntas = unicas
    print(f"→ {len(preguntas)} preguntas. El profesor las responde…")

    def _resp(p):
        if isinstance(profesor, ProfesorOffline):
            return profesor.responder(p["pregunta"])
        d = profesor.json(cfg["profesor"],
                          f"Eres un experto. Dominio: {cfg['dominio']}. Responde en {cfg['idioma']}, de forma correcta, "
                          f"concreta y clara, en máximo {cfg['max_palabras_profesor']} palabras, sin preámbulos.",
                          f'Pregunta: {p["pregunta"]}\nFormato: {{"respuesta": "..."}}', max_tokens=600)
        return (d.get("respuesta") or "").strip()

    with ThreadPoolExecutor(8) as ex:
        respuestas = list(ex.map(_resp, preguntas))
    datos = [{**p, "respuesta": r} for p, r in zip(preguntas, respuestas) if 20 <= len(r) <= 1500]
    rng = random.Random(cfg["semilla"])
    rng.shuffle(datos)
    examen, entrenamiento = datos[: cfg["n_examen"]], datos[cfg["n_examen"]:]
    _escribir(f_tr, entrenamiento)
    _escribir(f_ex, examen)
    print(f"✔ {len(entrenamiento)} pares de entrenamiento · {len(examen)} preguntas de examen · "
          f"{time.time()-t0:.0f} s · profesor: {profesor.resumen()}")
    return entrenamiento, examen


def _leer(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def _escribir(ruta: Path, filas: list[dict]) -> None:
    ruta.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")


# =============================================================================
# 3 · ESTUDIANTE  (modelo pequeño + LoRA)
# =============================================================================
class Estudiante:
    def __init__(self, cfg: dict):
        import torch
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.cfg = cfg
        self.dev = cfg["dispositivo"]
        origen = _modelo_tiny() if cfg["estudiante"] == "tiny" else cfg["estudiante"]
        print(f"→ Cargando estudiante '{cfg['estudiante']}' (la primera vez se descarga desde Hugging Face)…")
        self.tok = AutoTokenizer.from_pretrained(origen)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        modelo = AutoModelForCausalLM.from_pretrained(origen, **{_dtype_kw(): torch.float32}).to(self.dev)
        total = sum(p.numel() for p in modelo.parameters())
        lora = LoraConfig(r=cfg["lora_r"], lora_alpha=2 * cfg["lora_r"], lora_dropout=0.05, task_type="CAUSAL_LM",
                          target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                          modules_to_save=["embed_tokens", "lm_head"] if cfg["estudiante"] == "tiny" else None)
        self.modelo = get_peft_model(modelo, lora)
        entrenables = sum(p.numel() for p in self.modelo.parameters() if p.requires_grad)
        print(f"✔ Estudiante listo: {total/1e6:.0f} M parámetros · LoRA entrena {entrenables/1e6:.2f} M ({100*entrenables/total:.1f} %)")

    # --- formato de chat ---
    def prompt(self, pregunta: str) -> str:
        msgs = [{"role": "system", "content": SISTEMA_ESTUDIANTE}, {"role": "user", "content": pregunta}]
        return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

    def ejemplo(self, pregunta: str, respuesta: str) -> dict | None:
        """Tokens de la conversación; la pregunta lleva etiqueta -100 (no se aprende), solo la respuesta."""
        p = self.tok(self.prompt(pregunta), add_special_tokens=False)["input_ids"]
        r = self.tok(respuesta.strip() + self.tok.eos_token, add_special_tokens=False)["input_ids"]
        if len(p) >= self.cfg["max_tokens_ejemplo"] - 16:
            return None
        r = r[: self.cfg["max_tokens_ejemplo"] - len(p)]
        return {"input_ids": p + r, "labels": [-100] * len(p) + r}

    # --- generación ---
    def responder(self, preguntas: list[str], lote: int = 8, base: bool = False) -> list[str]:
        import contextlib

        import torch

        self.modelo.eval()
        self.tok.padding_side = "left"
        salidas = []
        ctx = self.modelo.disable_adapter() if base else contextlib.nullcontext()
        with torch.no_grad(), ctx:
            for i in range(0, len(preguntas), lote):
                enc = self.tok([self.prompt(q) for q in preguntas[i:i + lote]], return_tensors="pt", padding=True,
                               add_special_tokens=False)
                enc = {k: enc[k].to(self.dev) for k in ("input_ids", "attention_mask")}
                gen = self.modelo.generate(**enc, max_new_tokens=self.cfg["max_tokens_respuesta"], do_sample=False,
                                           repetition_penalty=1.15, pad_token_id=self.tok.pad_token_id,
                                           eos_token_id=self.tok.eos_token_id)
                nuevos = gen[:, enc["input_ids"].shape[1]:]
                salidas += [t.strip() for t in self.tok.batch_decode(nuevos, skip_special_tokens=True)]
        self.tok.padding_side = "right"
        return salidas

    def guardar(self, carpeta: Path) -> None:
        carpeta.mkdir(parents=True, exist_ok=True)
        self.modelo.save_pretrained(carpeta)

    def cargar_adaptador(self, carpeta: Path) -> None:
        from peft import set_peft_model_state_dict
        from safetensors.torch import load_file

        set_peft_model_state_dict(self.modelo, load_file(str(carpeta / "adapter_model.safetensors")))


def cargar_estudiante(cfg: dict) -> Estudiante:
    return Estudiante(cfg)


def _dtype_kw() -> str:
    import transformers

    try:
        v = tuple(int(x) for x in transformers.__version__.split(".")[:2])
    except ValueError:
        return "dtype"
    return "dtype" if v >= (4, 56) else "torch_dtype"


def _modelo_tiny() -> str:
    """Crea (una vez) un Llama diminuto local con tokenizador propio: sirve para practicar sin internet."""
    carpeta = SALIDAS / "modelo_tiny"
    if (carpeta / "config.json").exists():
        return str(carpeta)
    import torch
    from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers
    from transformers import LlamaConfig, LlamaForCausalLM, PreTrainedTokenizerFast

    corpus = [t for tema in _KB.values() for c, (d, k, u) in tema.items() for t in (c, d, k, u)] + _CONTEXTOS + _PLANTILLAS
    corpus += [SISTEMA_ESTUDIANTE] + [p.format(c=c, x=x) for p in _PLANTILLAS for x in _CONTEXTOS for c in ["LoRA", "RAG"]]
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    tok.train_from_iterator(corpus * 3, trainers.BpeTrainer(vocab_size=3000, special_tokens=["<|im_start|>", "<|im_end|>", "<|pad|>"],
                                                            initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
    fast = PreTrainedTokenizerFast(tokenizer_object=tok, bos_token="<|im_start|>", eos_token="<|im_end|>", pad_token="<|pad|>")
    fast.chat_template = ("{% for m in messages %}<|im_start|>{{ m['role'] }}\n{{ m['content'] }}<|im_end|>\n{% endfor %}"
                          "{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}")
    conf = LlamaConfig(vocab_size=len(fast), hidden_size=256, intermediate_size=688, num_hidden_layers=4, num_attention_heads=4,
                       num_key_value_heads=2, max_position_embeddings=2048, bos_token_id=fast.bos_token_id,
                       eos_token_id=fast.eos_token_id, pad_token_id=fast.pad_token_id, tie_word_embeddings=False)
    torch.manual_seed(0)
    LlamaForCausalLM(conf).save_pretrained(carpeta)
    fast.save_pretrained(carpeta)
    return str(carpeta)


# =============================================================================
# 4 · EVALUAR  (examen + juez)
# =============================================================================
def evaluar(cfg: dict, estudiante: Estudiante, profesor, examen: list[dict], etiqueta: str, base: bool = False) -> dict:
    """El estudiante responde el examen y el juez califica 1–10 comparando con la respuesta del profesor."""
    t0 = time.time()
    print(f"→ [{etiqueta}] el estudiante responde {len(examen)} preguntas…")
    respuestas = estudiante.responder([x["pregunta"] for x in examen], base=base)
    print(f"→ [{etiqueta}] el juez califica…")

    def _juzgar(i):
        x = examen[i]
        if isinstance(profesor, ProfesorOffline):
            return profesor.juzgar(x["pregunta"], x["respuesta"], respuestas[i])
        d = profesor.json(cfg["juez"],
                          "Eres un evaluador riguroso. Comparas la respuesta de un ESTUDIANTE con una REFERENCIA de alta calidad. "
                          "Calificas de 1 a 10 (7 = aceptable para un usuario real): corrección, completitud y claridad. "
                          "Penaliza inventos, texto incoherente, repeticiones u otro idioma (≤ 2). Evita premiar el largo.",
                          f"PREGUNTA:\n{x['pregunta']}\n\nREFERENCIA:\n{x['respuesta']}\n\nESTUDIANTE:\n{respuestas[i][:2000] or '(vacía)'}\n\n"
                          'Formato: {"nota": 7, "comentario": "una oración"}', max_tokens=300)
        try:
            nota = max(1, min(10, int(d.get("nota", 1))))
        except (TypeError, ValueError):
            nota = 1
        return nota, str(d.get("comentario", ""))

    with ThreadPoolExecutor(8) as ex:
        juicios = list(ex.map(_juzgar, range(len(examen))))
    detalle = [{**x, "etiqueta": etiqueta, "respuesta_estudiante": r, "nota": n, "comentario": c}
               for x, r, (n, c) in zip(examen, respuestas, juicios)]
    notas = [d["nota"] for d in detalle]
    res = {"etiqueta": etiqueta, "nota_media": round(statistics.mean(notas), 2),
           "aprobacion": round(sum(n >= 7 for n in notas) / len(notas), 2),
           "por_tema": {t: round(statistics.mean(d["nota"] for d in detalle if d["tema"] == t), 2)
                        for t in sorted({d["tema"] for d in detalle})},
           "detalle": detalle, "segundos": round(time.time() - t0, 1)}
    _escribir(SALIDAS / f"examen_{etiqueta}.jsonl", detalle)
    print(f"✔ [{etiqueta}] nota media {res['nota_media']}/10 · aprobación {res['aprobacion']:.0%} · {res['segundos']} s")
    return res


# =============================================================================
# 5 · ENTRENAR  (SFT con LoRA, bucle simple y transparente)
# =============================================================================
def entrenar(cfg: dict, estudiante: Estudiante, datos: list[dict], epocas: int | None = None) -> list[dict]:
    """Devuelve el historial de pérdida por paso y guarda el adaptador en salidas/checkpoint."""
    import torch
    from transformers import get_cosine_schedule_with_warmup

    epocas = epocas or cfg["epocas"]
    ejemplos = [e for d in datos if (e := estudiante.ejemplo(d["pregunta"], d["respuesta"]))]
    modelo, tok, dev = estudiante.modelo, estudiante.tok, estudiante.dev
    params = [p for p in modelo.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=cfg["tasa_aprendizaje"], weight_decay=0.0)
    pasos_por_epoca = -(-len(ejemplos) // cfg["lote"])
    sched = get_cosine_schedule_with_warmup(opt, max(1, pasos_por_epoca * epocas // 20), pasos_por_epoca * epocas)
    modelo.train()
    modelo.config.use_cache = False
    rng = random.Random(cfg["semilla"])
    historial, paso, t0 = [], 0, time.time()
    print(f"→ Entrenando: {len(ejemplos)} ejemplos · {epocas} épocas · {pasos_por_epoca*epocas} pasos · lote {cfg['lote']}")
    for ep in range(1, epocas + 1):
        idx = list(range(len(ejemplos)))
        rng.shuffle(idx)
        for i in range(0, len(idx), cfg["lote"]):
            lote = [ejemplos[j] for j in idx[i:i + cfg["lote"]]]
            L = max(len(e["input_ids"]) for e in lote)
            ids = torch.full((len(lote), L), tok.pad_token_id)
            lab = torch.full((len(lote), L), -100)
            att = torch.zeros((len(lote), L), dtype=torch.long)
            for k, e in enumerate(lote):
                n = len(e["input_ids"])
                ids[k, :n], lab[k, :n], att[k, :n] = torch.tensor(e["input_ids"]), torch.tensor(e["labels"]), 1
            out = modelo(input_ids=ids.to(dev), attention_mask=att.to(dev), labels=lab.to(dev))
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            paso += 1
            historial.append({"paso": paso, "epoca": ep, "perdida": round(out.loss.item(), 4), "segundos": round(time.time() - t0, 1)})
            if paso % max(5, (pasos_por_epoca * epocas) // 10) == 0 or paso == pasos_por_epoca * epocas:
                print(f"   época {ep} · paso {paso}/{pasos_por_epoca*epocas} · pérdida {out.loss.item():.3f} · {time.time()-t0:.0f} s")
    modelo.eval()
    modelo.config.use_cache = True
    estudiante.guardar(SALIDAS / "checkpoint")
    _escribir(SALIDAS / "entrenamiento_log.jsonl", historial)
    print(f"✔ Entrenamiento listo en {time.time()-t0:.0f} s · pérdida {historial[0]['perdida']} → {historial[-1]['perdida']} · "
          f"checkpoint en salidas/checkpoint")
    return historial


# =============================================================================
# 6 · COMPARAR  (gráfico + tabla + ejemplos lado a lado)
# =============================================================================
def comparar(antes: dict, despues: dict, historial: list[dict], profesor=None) -> Path:
    """Genera salidas/resultados.png y salidas/resultados.md. Devuelve la ruta del gráfico."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    C1, C2 = "#0099BF", "#D9653B"
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    # pérdida
    axs[0].plot([h["paso"] for h in historial], [h["perdida"] for h in historial], color=C1, lw=2)
    axs[0].set_title("Pérdida de entrenamiento"), axs[0].set_xlabel("paso"), axs[0].set_ylabel("entropía cruzada")
    # nota antes/después
    b = axs[1].bar(["Antes\n(modelo base)", "Después\n(destilado)"], [antes["nota_media"], despues["nota_media"]], color=[C2, C1], width=0.55)
    for r in b:
        axs[1].text(r.get_x() + r.get_width() / 2, r.get_height() + 0.15, f"{r.get_height():.1f}", ha="center", fontsize=12, fontweight="bold")
    axs[1].set_ylim(0, 10.8), axs[1].set_title("Nota media del juez (1–10)")
    axs[1].axhline(7, ls=":", color="#777"), axs[1].text(1.3, 7.1, "aprobado", fontsize=9, color="#777")
    # por tema
    temas = sorted(set(antes["por_tema"]) | set(despues["por_tema"]))
    y = range(len(temas))
    axs[2].barh([i + 0.2 for i in y], [antes["por_tema"].get(t, 0) for t in temas], height=0.38, color=C2, label="antes")
    axs[2].barh([i - 0.2 for i in y], [despues["por_tema"].get(t, 0) for t in temas], height=0.38, color=C1, label="después")
    axs[2].set_yticks(list(y)), axs[2].set_yticklabels(temas, fontsize=9), axs[2].set_xlim(0, 10), axs[2].legend(fontsize=9)
    axs[2].set_title("Nota por tema")
    for ax in axs:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    ruta = SALIDAS / "resultados.png"
    fig.savefig(ruta, dpi=150)
    plt.close(fig)

    lineas = ["# Resultados del taller de destilación", "",
              f"| | Antes (base) | Después (destilado) |", "|---|---|---|",
              f"| Nota media (1–10) | {antes['nota_media']} | **{despues['nota_media']}** |",
              f"| Aprobación (≥ 7) | {antes['aprobacion']:.0%} | **{despues['aprobacion']:.0%}** |",
              f"| Pérdida de entrenamiento | {historial[0]['perdida']} | {historial[-1]['perdida']} |", ""]
    if profesor is not None:
        lineas += [f"Uso del profesor: {profesor.resumen()}", ""]
    lineas += ["## Ejemplos lado a lado", ""]
    for a, d in list(zip(antes["detalle"], despues["detalle"]))[:5]:
        lineas += [f"**Pregunta:** {a['pregunta']}", "", f"- Referencia del profesor: {a['respuesta']}",
                   f"- Antes (nota {a['nota']}): {a['respuesta_estudiante'][:300]}",
                   f"- Después (nota {d['nota']}): {d['respuesta_estudiante'][:300]}", ""]
    (SALIDAS / "resultados.md").write_text("\n".join(lineas), encoding="utf-8")
    print(f"✔ Gráfico: {ruta} · tabla y ejemplos: {SALIDAS / 'resultados.md'}")
    return ruta


def chatear(estudiante: Estudiante, pregunta: str, comparar_base: bool = True) -> None:
    """Pregunta algo al estudiante entrenado (y opcionalmente al modelo base, para comparar)."""
    print(f"Tú › {pregunta}\n")
    print(f"Destilado › {estudiante.responder([pregunta], lote=1)[0]}\n")
    if comparar_base:
        print(f"Base (sin entrenar) › {estudiante.responder([pregunta], lote=1, base=True)[0]}\n")


# =============================================================================
# TODO DE UNA VEZ  (python destila.py)
# =============================================================================
def correr_todo(sin_internet: bool = False, estudiante: str | None = None, epocas: int | None = None) -> dict:
    t0 = time.time()
    cfg = configurar(sin_internet, estudiante)
    profesor = ProfesorOffline(cfg) if cfg["profesor_modo"] == "offline" else Profesor(cfg)
    entrenamiento, examen = generar_datos(cfg, profesor)
    est = cargar_estudiante(cfg)
    antes = evaluar(cfg, est, profesor, examen, "antes")
    historial = entrenar(cfg, est, entrenamiento, epocas)
    despues = evaluar(cfg, est, profesor, examen, "despues")
    comparar(antes, despues, historial, profesor)
    print(f"\n{'='*64}\nRESULTADO: nota {antes['nota_media']} → {despues['nota_media']} · "
          f"aprobación {antes['aprobacion']:.0%} → {despues['aprobacion']:.0%} · {(time.time()-t0)/60:.1f} min en total\n{'='*64}")
    chatear(est, "Explica qué es LoRA y para qué sirve en un banco.")
    return {"antes": antes, "despues": despues, "historial": historial, "estudiante": est, "cfg": cfg}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Taller de destilación en pequeño")
    ap.add_argument("--sin-internet", action="store_true", help="profesor simulado + modelo diminuto local (sin clave ni descargas)")
    ap.add_argument("--estudiante", default=None, help="id de Hugging Face del modelo estudiante (o 'tiny')")
    ap.add_argument("--epocas", type=int, default=None)
    a = ap.parse_args()
    correr_todo(a.sin_internet, a.estudiante, a.epocas)
