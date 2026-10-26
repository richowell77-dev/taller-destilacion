"""
subir_hf.py · Publica el adaptador LoRA del taller en el Hugging Face Hub, con una tarjeta (README) hecha con datos reales.

  python subir_hf.py --repo USUARIO/finbot-slm --simular     # solo arma salidas/para_hf_adaptador/ y muestra la tarjeta
  python subir_hf.py --repo USUARIO/finbot-slm --privado     # publica en un repositorio privado (para iterar)
  python subir_hf.py --repo USUARIO/finbot-slm               # publica en un repositorio público

Requiere HF_TOKEN (permiso de escritura) en .env. Las métricas salen de salidas/examen_antes.jsonl y examen_despues.jsonl:
no se inventa ninguna cifra.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDAS, DATOS = AQUI / "salidas", AQUI / "datos"
DESTINO = SALIDAS / "para_hf_adaptador"


def _leer(r: Path) -> list[dict]:
    return [json.loads(l) for l in r.read_text(encoding="utf-8").splitlines() if l.strip()]


def _env() -> None:
    ruta = AQUI / ".env"
    if ruta.exists():
        for l in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in l and not l.lstrip().startswith("#"):
                k, v = l.split("=", 1)
                v = v.strip().strip('"').strip("'")
                if v:
                    os.environ[k.strip()] = v


def _resumen(filas: list[dict]) -> dict:
    n = [f["nota"] for f in filas]
    temas = sorted({f["tema"] for f in filas})
    return {"media": statistics.mean(n), "aprob": sum(x >= 7 for x in n) / len(n),
            "tema": {t: statistics.mean(f["nota"] for f in filas if f["tema"] == t) for t in temas}}


def tarjeta(repo: str) -> str:
    conf = json.loads((SALIDAS / "checkpoint" / "adapter_config.json").read_text(encoding="utf-8"))
    base = conf["base_model_name_or_path"]
    antes, despues = _resumen(_leer(SALIDAS / "examen_antes.jsonl")), _resumen(_leer(SALIDAS / "examen_despues.jsonl"))
    n_ex = len(_leer(SALIDAS / "examen_despues.jsonl"))
    n_tr = len(_leer(DATOS / "entrenamiento.jsonl"))
    log = _leer(SALIDAS / "entrenamiento_log.jsonl")
    f = lambda x: f"{x:.2f}"
    filas_tema = "\n".join(f"| {t} | {f(antes['tema'].get(t, 0))} | {f(v)} |" for t, v in despues["tema"].items())
    return f"""---
language: [en]
license: apache-2.0
library_name: peft
base_model: {base}
tags: [destilacion, distillation, lora, slm, educacion, uai]
pipeline_tag: text-generation
---

# {repo.split('/')[-1]}

Adaptador **LoRA** sobre `{base}` (135 M parámetros), destilado en el *Taller de destilación en pequeño*
(Tópicos Avanzados en IA 2, Máster en IA, UAI). Un LLM grande (profesor, API de OpenAI `gpt-6-luna`) escribió preguntas y
respuestas, y el modelo pequeño aprendió a imitarlas con ajuste fino supervisado (SFT) en CPU.

**Dominio:** asistente que explica conceptos de IA generativa (fundamentos de LLM, prompts, RAG, agentes, ajuste fino y evaluación)
a ejecutivos de empresas chilenas, con ejemplos de negocio. Responde en inglés, porque SmolLM2 entiende mal el español
(en español la nota del modelo no superó 1,1 sobre 10).

## Datos de entrenamiento
- {n_tr} pares pregunta-respuesta en inglés generados por `gpt-6-luna` (respuestas de máximo 90 palabras), en 6 temas.
- Examen fijo de {n_ex} preguntas, separado del entrenamiento, calificado de 1 a 10 por un LLM juez (`gpt-6-luna`) contra la respuesta de referencia.
- Entrenamiento: LoRA r={conf['r']}, alpha={conf['lora_alpha']}, 3 épocas, lote 4, tasa de aprendizaje 5e-4; pérdida {log[0]['perdida']} → {log[-1]['perdida']}.

## Resultados en el examen fijo

| | Antes (modelo base) | Después (destilado) |
|---|---|---|
| Nota media del juez (1–10) | {f(antes['media'])} | **{f(despues['media'])}** |
| Aprobación (nota ≥ 7) | {antes['aprob']:.0%} | {despues['aprob']:.0%} |

| Tema | Antes | Después |
|---|---|---|
{filas_tema}

Cifras calculadas desde `salidas/examen_antes.jsonl` y `salidas/examen_despues.jsonl`. El juez es otro LLM: su nota tiene ruido
(≈ ±0,3 entre corridas) y, en una auditoría manual de 10 ítems, resultó levemente más generoso que un humano.

## Uso

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = "{base}"
tok = AutoTokenizer.from_pretrained(base)
model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(base), "{repo}")

msgs = [{{"role": "system", "content": "You are an expert assistant in generative AI. Answer in English, clearly and briefly."}},
        {{"role": "user", "content": "When should a company use RAG instead of fine-tuning?"}}]
enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
out = model.generate(**enc, max_new_tokens=120, do_sample=False, repetition_penalty=1.15)
print(tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True))
```

## Limitaciones y uso responsable
- **Lo que este modelo NO es:** con 135 M parámetros y {n_tr} ejemplos, repite frases, se equivoca e **inventa definiciones con seguridad**.
  Ninguna respuesta del examen llegó al nivel aceptable (7/10). **No lo uses para tomar decisiones reales**: es un modelo educativo.
- Fuera del dominio responde como un modelo genérico y puede inventar datos.
- **Licencia y origen:** el modelo base SmolLM2 es Apache 2.0, y este derivado se publica con la misma licencia. **Los datos de entrenamiento los
  generó un LLM comercial (OpenAI)**, cuyos términos restringen usar sus salidas para desarrollar modelos que compitan con OpenAI.
  Uso educativo; revisa esos términos antes de cualquier uso no educativo.
- Puede heredar sesgos y errores del profesor y del juez.
"""


def preparar(repo: str) -> str:
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)
    for n in ("adapter_config.json", "adapter_model.safetensors"):
        shutil.copy2(SALIDAS / "checkpoint" / n, DESTINO / n)
    for r in ("resultados.png",):
        if (SALIDAS / r).exists():
            shutil.copy2(SALIDAS / r, DESTINO / r)
    readme = tarjeta(repo)
    (DESTINO / "README.md").write_text(readme, encoding="utf-8")
    return readme


def main() -> None:
    ap = argparse.ArgumentParser(description="Publica el adaptador del taller en Hugging Face")
    ap.add_argument("--repo", required=True, help="USUARIO/nombre-del-modelo")
    ap.add_argument("--simular", action="store_true", help="no publica: solo arma la carpeta y muestra la tarjeta")
    ap.add_argument("--privado", action="store_true", help="crea el repositorio como privado")
    a = ap.parse_args()
    readme = preparar(a.repo)
    print(readme)
    print(f"✔ Carpeta lista: {DESTINO} · archivos: {sorted(p.name for p in DESTINO.iterdir())}")
    if a.simular:
        print("SIMULACIÓN: no se publicó nada.")
        return
    _env()
    token = os.getenv("HF_TOKEN")
    if not token:
        raise SystemExit("Falta HF_TOKEN en .env (token de Hugging Face con permiso de escritura).")
    from huggingface_hub import HfApi

    api = HfApi(token=token)
    api.create_repo(repo_id=a.repo, repo_type="model", private=a.privado, exist_ok=True)
    api.upload_folder(folder_path=str(DESTINO), repo_id=a.repo, repo_type="model", commit_message="Modelo destilado del taller")
    print(f"✔ Publicado ({'privado' if a.privado else 'público'}): https://huggingface.co/{a.repo}")


if __name__ == "__main__":
    main()
