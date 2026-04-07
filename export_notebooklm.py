#!/usr/bin/env python3
"""
Exporta `data/index.jsonl` a un único archivo JSON listo para cargar en NotebookLM.

Cada documento tendrá: title, url, category, content, questions_clave
"""
import json
import re
from pathlib import Path


def load_index(path="data/index.jsonl"):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe índice en {path}")
    docs = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        docs.append(json.loads(line))
    return docs


def extract_questions(text):
    # extrae oraciones que contienen '?'
    candidates = re.split(r"(?<=[\.!?])\s+", text)
    qs = [c.strip() for c in candidates if '?' in c and len(c.strip())>10]
    # dedupe manteniendo orden
    seen = set()
    out = []
    for q in qs:
        if q in seen:
            continue
        seen.add(q)
        out.append(q)
    return out


def export(out_path="data/notebooklm_export.json"):
    docs = load_index()
    out_docs = []
    for d in docs:
        content = d.get('content','') or ''
        qs = extract_questions(content)
        out_docs.append({
            'title': d.get('title') or d.get('id'),
            'url': d.get('url',''),
            'category': d.get('category',''),
            'content': content,
            'questions_clave': qs
        })

    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out_docs, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Exportado {len(out_docs)} documentos a {p}")


if __name__ == '__main__':
    export()
