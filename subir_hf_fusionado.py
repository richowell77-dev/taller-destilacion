"""
subir_hf_fusionado.py · Fusiona el modelo base + el adaptador LoRA en un modelo completo y lo publica en el Hub.

  python subir_hf_fusionado.py --repo USUARIO/taller-destilacion-slm-merged --adaptador USUARIO/taller-destilacion-slm [--simular]

Cuándo usar cada versión:
  · Adaptador (≈ 19 MB): liviano, versionable, requiere peft y descargar el modelo base aparte.
  · Fusionado (≈ 270 MB en bf16): se usa como cualquier modelo de transformers, sin peft; ocupa más espacio.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

import torch

import subir_hf as S

DESTINO = S.SALIDAS / "para_hf_fusionado"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--adaptador", required=True, help="repo del adaptador, para enlazarlo en la tarjeta")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    base = "HuggingFaceTB/SmolLM2-135M-Instruct"
    tok = AutoTokenizer.from_pretrained(base)
    modelo = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(base, dtype=torch.float32),
                                       str(S.SALIDAS / "checkpoint")).merge_and_unload()
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    modelo.to(torch.bfloat16).save_pretrained(DESTINO, safe_serialization=True)
    tok.save_pretrained(DESTINO)
    card = S.tarjeta(a.repo)
    card = card.replace("library_name: peft", "library_name: transformers")
    card = card.replace("Adaptador **LoRA** sobre", "Modelo **fusionado** (base + adaptador LoRA, bf16) a partir de")
    inicio, fin = card.index("## Uso"), card.index("## Limitaciones")
    uso = f'''## Uso

Versión fusionada: no necesita `peft`. El adaptador LoRA liviano (≈ 19 MB) está en [{a.adaptador}](https://huggingface.co/{a.adaptador}).

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("{a.repo}")
model = AutoModelForCausalLM.from_pretrained("{a.repo}")
msgs = [{{"role": "system", "content": "You are an expert assistant in generative AI. Answer in English, clearly and briefly."}},
        {{"role": "user", "content": "When should a company use RAG instead of fine-tuning?"}}]
enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
out = model.generate(**enc, max_new_tokens=120, do_sample=False, repetition_penalty=1.15)
print(tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True))
```

'''
    card = card[:inicio] + uso + card[fin:]
    (DESTINO / "README.md").write_text(card, encoding="utf-8")
    if (S.SALIDAS / "resultados.png").exists():
        shutil.copy2(S.SALIDAS / "resultados.png", DESTINO / "resultados.png")
    tam = sum(p.stat().st_size for p in DESTINO.iterdir()) / 1e6
    print(f"✔ Fusionado en {DESTINO} · {tam:.0f} MB · {sorted(p.name for p in DESTINO.iterdir())}")
    if a.simular:
        print("SIMULACIÓN: no se publicó nada.")
        return
    S._env()
    from huggingface_hub import HfApi

    api = HfApi(token=os.environ["HF_TOKEN"])
    api.create_repo(repo_id=a.repo, repo_type="model", private=False, exist_ok=True)
    api.upload_folder(folder_path=str(DESTINO), repo_id=a.repo, repo_type="model", commit_message="Modelo destilado del taller (fusionado)")
    print(f"✔ Publicado (público): https://huggingface.co/{a.repo}")


if __name__ == "__main__":
    main()
