#!/usr/bin/env python3
"""
Normaliza las preguntas extraídas en `data/faqs.json` para hacerlas más útiles.

Salida: `data/faqs_normalized.json` con campo `normalized_question`.
"""
import json
import re
from pathlib import Path


def normalize_question(q: str) -> str:
    if not q:
        return q
    s = q.strip()
    # remover espacios redundantes
    s = re.sub(r"\s+", " ", s)
    # quitar comillas sobrantes
    s = s.strip('"\'')
    # asegurar inicio y fin de pregunta
    # detectar casos comunes
    low = s.lower()
    if 'url' in low:
        return '¿Cuál es la URL de esta página?'
    if 'contenido' in low or 'contiene' in low:
        return '¿Qué contiene esta página?'
    if 'cómo' in low or 'como ' in low:
        # ya es una pregunta de cómo
        if not s.endswith('?'):
            s = s + '?'
        if not s.startswith('¿'):
            s = '¿' + s[0].lower() + s[1:]
        return s
    # si es un encabezado muy corto, transformarlo en pregunta natural
    words = s.strip(' ?¿!¡.').split()
    if len(words) <= 5:
        base = ' '.join(words)
        # capitalizar primera letra
        base = base[0].upper() + base[1:] if base else base
        if not base.endswith('?'):
            return f'¿{base}?' 
        return base

    # por defecto, añadir signos de interrogación si no los tiene
    if not s.endswith('?'):
        s = s + '?'
    if not s.startswith('¿'):
        s = '¿' + s[0].lower() + s[1:]
    return s


def run(input_path='data/faqs.json', output_path='data/faqs_normalized.json'):
    p = Path(input_path)
    if not p.exists():
        print(f'No existe {input_path}. Ejecuta `extract_faqs.py` primero.')
        return
    faqs = json.loads(p.read_text(encoding='utf-8'))
    out = []
    for f in faqs:
        q = f.get('question','')
        norm = normalize_question(q)
        f2 = dict(f)
        f2['normalized_question'] = norm
        out.append(f2)
    Path(output_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Normalizadas {len(out)} preguntas -> {output_path}')


if __name__ == '__main__':
    run()
