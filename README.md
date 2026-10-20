# Taller · Destilación en pequeño (CPU)

**Formato:** 15 horas en clases (cinco bloques de 3 h) · **entrega individual** (informe PDF + carpeta del proyecto).
La pauta completa, el plan por bloque y la rúbrica están en `Guia_Taller_Destilacion.pdf`; la estructura del informe en `PLANTILLA_INFORME.md`.

Un LLM grande (**profesor**, API de OpenAI) enseña a un modelo de 135 M parámetros (**estudiante**, SmolLM2)
que corre en tu notebook sin GPU. En 6 etapas y ~10 minutos ves el ciclo completo: datos del profesor →
examen antes → entrenamiento LoRA → examen después → comparación.

## Instalación (una vez, 5 minutos)

```bash
# 1) Python 3.10 a 3.13 (en Mac: brew install python@3.12 · en Windows: python.org, marca "Add to PATH")
python --version

# 2) Entorno virtual
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1

# 3) Dependencias (≈ 800 MB, incluye PyTorch para CPU)
pip install -r requirements.txt

# 4) Clave de OpenAI (opcional): abre .env y pega  OPENAI_API_KEY=sk-...
```

## Correr

| Cómo | Comando |
|---|---|
| Notebook paso a paso (recomendado para el taller) | `jupyter notebook taller_destilacion.ipynb` → *Run all* o celda por celda |
| Todo de una vez en la terminal | `python destila.py` |
| Sin clave y sin internet (profesor simulado + modelo diminuto) | `python destila.py --sin-internet` · en el notebook: `SIN_INTERNET = True` |
| Estudiante más capaz (2–3× más lento) | `python destila.py --estudiante HuggingFaceTB/SmolLM2-360M-Instruct` |

La primera corrida descarga el estudiante (270 MB) desde Hugging Face; queda en caché.

## Qué produce

```
datos/entrenamiento.jsonl   pares pregunta-respuesta del profesor
datos/examen.jsonl          examen fijo (nunca se entrena con él)
salidas/examen_antes.jsonl  respuestas del estudiante base + nota y comentario del juez
salidas/examen_despues.jsonl  ídem, después de entrenar
salidas/entrenamiento_log.jsonl  pérdida por paso
salidas/checkpoint/         adaptador LoRA entrenado (≈ 5 MB)
salidas/resultados.png      gráfico: pérdida · nota antes/después · nota por tema
salidas/resultados.md       tabla + 5 ejemplos lado a lado
```

## Costo del profesor real

Con `gpt-6-luna` (US$ 0,10 / 0,50 por millón de tokens) una corrida completa (72 preguntas, 72 respuestas,
24 juicios) cuesta **menos de US$ 0,05**. El modelo se cambia en `.env` (`OPENAI_MODEL`).

## Ajustes

Todo lo ajustable está en `CONFIG`, al inicio de `destila.py`: dominio, temas, cantidad de datos, épocas,
tasa de aprendizaje, rango LoRA y largos. Para regenerar datos después de cambiar el dominio, borra `datos/`.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `401 invalid_api_key` | La clave de `.env` es inválida o hay una `OPENAI_API_KEY` antigua en la terminal (`echo $OPENAI_API_KEY`). `.env` tiene prioridad. |
| `404 model not found` | Tu cuenta no tiene ese modelo: en `.env` pon `OPENAI_MODEL=gpt-5-mini` |
| Descarga del modelo falla | Red corporativa bloquea Hugging Face: usa `--sin-internet` o descarga desde otra red |
| Muy lento | Baja `n_entrenamiento` a 40 y `epocas` a 2, o usa `--sin-internet` para practicar el flujo |
| `No module named torch` | Activa el entorno virtual antes de correr |

## Licencias y uso responsable

SmolLM2: Apache 2.0. Términos de OpenAI: restringen usar sus salidas para desarrollar modelos que compitan con
OpenAI; úsalo con fines educativos/internos y revisa los términos vigentes. No envíes datos personales al profesor.
