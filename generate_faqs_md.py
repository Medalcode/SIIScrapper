#!/usr/bin/env python3
"""
Genera `FAQS.md` completo a partir de `data/faqs_final.json`.
"""
import json
from pathlib import Path


def run(input_path='data/faqs_final.json', out_md='FAQS.md'):
    p = Path(input_path)
    if not p.exists():
        print(f'No existe {input_path}. Ejecuta extract_faqs.py primero.')
        return
    faqs = json.loads(p.read_text(encoding='utf-8'))
    lines = [
        '# Preguntas Frecuentes extraídas del SII',
        '',
        'Este documento contiene las FAQs extraídas y normalizadas desde el scraping ampliado.',
        '',
        '---',
        ''
    ]
    for i, f in enumerate(faqs, start=1):
        q = f.get('normalized_question') or f.get('question')
        a = f.get('answer') or ''
        src = f.get('source','')
        path = f.get('path','')
        lines.append(f'## {i}. {q}')
        lines.append('')
        lines.append(f'- Fuente: `{src}`')
        lines.append(f'- Archivo origen: `{path}`')
        lines.append('')
        lines.append('Respuesta:')
        lines.append('')
        # preserve paragraphs
        for para in a.split('\n\n'):
            lines.append(para.strip())
            lines.append('')
        lines.append('---')
        lines.append('')

    Path(out_md).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Generado {out_md} con {len(faqs)} FAQs')


if __name__ == '__main__':
    run()
