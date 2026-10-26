# Taller · Destilación en pequeño — resultados

Un LLM grande (**profesor y juez**: API de OpenAI, `gpt-6-luna`) enseña a **SmolLM2-135M-Instruct** (estudiante, 135 M parámetros)
que corre en CPU, con ajuste fino LoRA. Configuración y dominio **por defecto del profesor** (IA generativa para ejecutivos de empresas chilenas).

## Resumen

| Corrida | Idioma | Nota antes | Nota después | Aprobación (≥ 7) | Pérdida | Costo API | Tiempo |
|---|---|---|---|---|---|---|---|
| 1 · tal cual | español | 1,00 | 1,08 | 0 % → 0 % | 3,147 → 2,652 | ≈ US$ 0,010 | 23,7 min |
| 2 · recomendación del profesor | inglés | 2,33 | **2,50** | 0 % → 0 % | 3,817 → 2,902 | ≈ US$ 0,011 | 14,1 min |
| **Modelo final** (notebook ejecutado) | inglés | 2,00 | **2,75** | 0 % → 0 % | 3,817 → 2,902 | ≈ US$ 0,003* | — |
| Colab GPU · español | español | 1,00 | 1,08 | 0 % → 0 % | 3,171 → 2,461 | ≈ US$ 0,010 | 2,2 min |
| Colab GPU · inglés | inglés | 2,08 | 2,83 | 0 % → 0 % | 3,790 → 2,935 | ≈ US$ 0,011 | 1,9 min |
| Colab GPU · inglés + **SmolLM2-360M** (propuesta) | inglés | 4,08 | **4,58** | 8 % → 0 % | 3,558 → 2,260 | ≈ US$ 0,011 | 2,1 min |

\* El notebook reutiliza los datos de la corrida 2; solo paga los juicios del examen.

- **Meta del profesor (nota después > 2/10): cumplida en inglés.** En español el estudiante no supera 2, porque entiende mal el idioma.
- La variación de la "nota antes" entre la corrida 2 y el notebook (2,33 vs. 2,00), con el mismo modelo base y el mismo examen, muestra el ruido del juez.
- **CPU vs. GPU:** la GPU T4 entrena ≈ 60× más rápido (10 s vs. ≈ 10 min), pero la calidad es la misma con la misma configuración. Lo que mejora la nota es el idioma (inglés) y el tamaño del estudiante (360M).
- Antes de las corridas reales se validó la instalación con `python destila.py --sin-internet` (simulado, nota 1 → 9,33). No se incluye en los resultados porque no usa la API.

## Modelo publicado en Hugging Face

- **Adaptador LoRA** (≈ 19 MB, requiere `peft`): https://huggingface.co/richowell7/taller-destilacion-slm
- **Versión fusionada** (≈ 270 MB, sin `peft`): https://huggingface.co/richowell7/taller-destilacion-slm-merged

Publicados con `subir_hf.py` y `subir_hf_fusionado.py`; ambos se probaron descargándolos desde cero, sin token.

## Cómo reproducir

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows
pip install -r requirements.txt
# .env  →  OPENAI_API_KEY=sk-...   (sin comillas; no se sube al repositorio)
python destila.py --sin-internet      # prueba simulada (sin costo)
python destila.py                     # corrida real (destila.py ya está en inglés)
python demo.py                        # 5 preguntas nuevas, base vs. destilado
```

`destila_original_profesor.py` y `taller_destilacion_original_profesor.ipynb` son las versiones originales en español (corrida 1).
`aplicar_ingles.py` aplica el cambio a inglés sobre esos originales.

## Estructura

| Ruta | Contenido |
|---|---|
| `destila.py` · `taller_destilacion.ipynb` | Código y notebook **ejecutado** del modelo final (inglés) |
| `datos/` | Pares pregunta-respuesta del profesor y examen fijo del modelo final |
| `salidas/` | Exámenes antes/después, log de pérdida, `checkpoint/` (adaptador LoRA), `resultados.png/.md`, `demo.md` |
| `corridas/c1_espanol/`, `corridas/c2_ingles/` | Datos, salidas y log de cada corrida local (CPU) |
| `corridas/colab/` · `colab_taller_destilacion_gpu.ipynb` | Corridas en Google Colab con GPU (incluye SmolLM2-360M) y el notebook usado |
| `informe/` | Informe individual (PDF) |

Licencias: SmolLM2 tiene licencia Apache 2.0. Los términos de OpenAI restringen usar sus salidas para crear modelos que compitan con OpenAI; este trabajo es de uso educativo.


