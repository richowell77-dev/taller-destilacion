"""
aplicar_ingles.py · Pasa el taller a inglés (recomendación del profesor: SmolLM2 entiende mal el español).

Cambia en destila.py:  CONFIG["idioma"] → "English" · SISTEMA_ESTUDIANTE en inglés · pregunta de demostración de correr_todo
Cambia en el notebook: las dos preguntas de demostración (chatear) en inglés.
El dominio (IA generativa para ejecutivos) y todo lo demás quedan igual que el original del profesor.

Uso:  python aplicar_ingles.py      (idempotente)
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CAMBIOS = [
    ('"idioma": "español neutro (Chile)",', '"idioma": "English",'),
    ('SISTEMA_ESTUDIANTE = "Eres un asistente experto en IA generativa. Responde en español, de forma clara y breve."',
     'SISTEMA_ESTUDIANTE = "You are an expert assistant in generative AI. Answer in English, clearly and briefly."'),
    ('chatear(est, "Explica qué es LoRA y para qué sirve en un banco.")',
     'chatear(est, "Explain what LoRA is and what it is useful for in a bank.")'),
]
PREGUNTAS_NB = {
    "Explica qué es LoRA y para qué sirve en un banco.": "Explain what LoRA is and what it is useful for in a bank.",
    "¿Qué es una alucinación y cómo la controlo con RAG en una clínica?": "What is a hallucination and how can I control it with RAG in a clinic?",
}

ruta = AQUI / "destila.py"
s = ruta.read_text(encoding="utf-8")
for viejo, nuevo in CAMBIOS:
    if nuevo in s:
        continue
    if viejo not in s:
        raise SystemExit(f"No encontré en destila.py: {viejo[:60]}…")
    s = s.replace(viejo, nuevo)
ruta.write_text(s, encoding="utf-8")
print("✔ destila.py en inglés (idioma, SISTEMA_ESTUDIANTE, pregunta de demo)")

nb_ruta = AQUI / "taller_destilacion.ipynb"
nb = json.loads(nb_ruta.read_text(encoding="utf-8"))
for c in nb["cells"]:
    if c["cell_type"] == "code":
        src = "".join(c["source"])
        for es, en in PREGUNTAS_NB.items():
            src = src.replace(es, en)
        c["source"] = src
nb_ruta.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("✔ notebook: preguntas de demostración en inglés")
