#!/usr/bin/env python3
"""
Pequeño buscador sobre `data/index.jsonl`.

Uso:
  python search_index.py "término" --top 5

Busca por ocurrencias simples en título y contenido y muestra snippets.
"""
import argparse
import json
import os
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


def snippet_for(text, q, radius=120):
    t = text.lower()
    qi = q.lower()
    i = t.find(qi)
    if i == -1:
        return text[:radius].replace('\n', ' ')
    start = max(0, i - radius//2)
    end = min(len(text), i + radius//2)
    s = text[start:end].replace('\n', ' ')
    return ('...' if start>0 else '') + s + ('...' if end < len(text) else '')


def search(query, top=5):
    docs = load_index()
    results = []
    for d in docs:
        score = 0
        title = d.get('title','') or ''
        content = d.get('content','') or ''
        score += title.lower().count(query.lower()) * 3
        score += content.lower().count(query.lower())
        if score > 0:
            results.append((score, d))
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('query')
    parser.add_argument('--top', type=int, default=5)
    args = parser.parse_args()

    res = search(args.query, top=args.top)
    if not res:
        print('No se encontraron resultados.')
        return
    for score, d in res:
        print(f"[{score}] {d.get('title')} ({d.get('category')})\n  {d.get('url')}\n  {snippet_for(d.get('content',''), args.query)}\n")


if __name__ == '__main__':
    main()
