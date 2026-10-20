"""
demo.py · Demostración del modelo final: base vs. destilado lado a lado (sección 6 del informe).

  python demo.py                 # usa salidas/checkpoint (el modelo final)

Responde 5 preguntas NUEVAS en inglés (3 dentro del dominio, 2 fuera) y guarda salidas/demo.md.
"""
from __future__ import annotations

import json

import destila as D

PREGUNTAS = [
    ("dentro", "What is a hallucination in a large language model, and how can a company reduce it?"),
    ("dentro", "When should a company use RAG instead of fine-tuning a model?"),
    ("dentro", "What is a context window and why does it matter for business documents?"),
    ("fuera", "What is the capital of Australia?"),
    ("fuera", "Give me a short recipe for pancakes."),
]


def main() -> None:
    ck = D.SALIDAS / "checkpoint"
    conf = json.loads((ck / "adapter_config.json").read_text(encoding="utf-8"))
    cfg = D.configurar(estudiante=conf.get("base_model_name_or_path") or None)
    cfg["lora_r"] = conf["r"]
    est = D.cargar_estudiante(cfg)
    est.cargar_adaptador(ck)
    preguntas = [q for _, q in PREGUNTAS]
    destilado = est.responder(preguntas, lote=1)
    base = est.responder(preguntas, lote=1, base=True)
    md = ["# Demostración · modelo base vs. destilado", "", f"Estudiante: `{cfg['estudiante']}` · checkpoint: `salidas/checkpoint`", ""]
    for (tipo, q), b, d in zip(PREGUNTAS, base, destilado):
        md += [f"## ({tipo} del dominio) {q}", "", f"**Base:** {b}", "", f"**Destilado:** {d}", ""]
        print(f"\n[{tipo}] {q}\n  Base      › {b[:300]}\n  Destilado › {d[:300]}")
    (D.SALIDAS / "demo.md").write_text("\n".join(md), encoding="utf-8")
    print("\n✔ salidas/demo.md")


if __name__ == "__main__":
    main()
