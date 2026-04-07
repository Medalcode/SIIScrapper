#!/usr/bin/env python3
"""
Construye un índice `data/index.jsonl` a partir de los archivos generados en `data/`.

Lee archivos `data/<categoria>/*.md` y `*.json` y escribe una línea JSON por documento.
Cada objeto contiene: id, title, url, category, content, path
"""
import json
import os
import re
from pathlib import Path


def parse_md(path):
    text = path.read_text(encoding="utf-8")
    title = None
    url = None
    # buscar título '# '
    for line in text.splitlines():
        if line.startswith('# '):
            title = line[2:].strip()
            break
    # buscar '## URL' sección
    m = re.search(r"## URL\n(.+)", text)
    if m:
        url = m.group(1).strip()
    # contenido: después de '## Contenido' si existe
    content = text
    m2 = re.search(r"## Contenido\n([\s\S]+)", text)
    if m2:
        content = m2.group(1).strip()
    return title or path.stem, url or "", content


def parse_json(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("categoria") or path.stem
    url = data.get("url") or ""
    content = data.get("contenido") or data.get("content") or ""
    return title, url, content


def build_index(data_dir="data", out_path="data/index.jsonl"):
    p = Path(data_dir)
    if not p.exists():
        print("No existe la carpeta data/ — ejecuta el scraper primero.")
        return

    items = []
    for categoria_dir in sorted(p.iterdir()):
        if not categoria_dir.is_dir():
            continue
        categoria = categoria_dir.name
        for f in sorted(categoria_dir.iterdir()):
            if f.suffix.lower() == ".md":
                title, url, content = parse_md(f)
            elif f.suffix.lower() == ".json":
                title, url, content = parse_json(f)
            else:
                continue

            item = {
                "id": f"{categoria}/{f.name}",
                "title": title,
                "url": url,
                "category": categoria,
                "content": content,
                "path": str(f)
            }
            items.append(item)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"Índice creado: {out} ({len(items)} documentos)")


if __name__ == "__main__":
    build_index()
