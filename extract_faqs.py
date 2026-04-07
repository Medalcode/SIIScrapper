#!/usr/bin/env python3
"""
Extrae preguntas frecuentes simples desde los archivos Markdown generados.

Estrategia:
- Busca líneas que contienen '?' y las toma como pregunta.
- La(s) siguientes líneas no vacías hasta la próxima pregunta se toman como respuesta.

Salida: `data/faqs.json` (lista de {question, answer, source, path}).
"""
import json
import os
import re
from pathlib import Path


def extract_from_md(path: Path):
    text = path.read_text(encoding='utf-8')
    faqs = []

    # 1) detectar preguntas explícitas por oraciones
    sentences = re.split(r'(?<=[\\.!?])\\s+', text)
    for i, s in enumerate(sentences):
        s_stripped = s.strip()
        if not s_stripped:
            continue
        if '?' in s_stripped and len(s_stripped) > 8:
            ans_parts = []
            for j in range(i+1, min(i+4, len(sentences))):
                nxt = sentences[j].strip()
                if not nxt:
                    continue
                if '?' in nxt:
                    break
                ans_parts.append(nxt)
            answer = ' '.join(ans_parts).strip()
            faqs.append({
                'question': s_stripped,
                'answer': answer,
                'source': path.parent.name,
                'path': str(path)
            })

    # 2) convertir encabezados en preguntas con el bloque siguiente como respuesta
    lines = text.splitlines()
    i = 0
    header_re = re.compile(r'^(#{1,6})\s*(.+)$')
    while i < len(lines):
        m = header_re.match(lines[i].strip())
        if m:
            header_text = m.group(2).strip()
            # construir pregunta a partir del encabezado
            question = header_text
            if not question.endswith('?'):
                question = f"¿{question}?"

            # recolectar respuesta: líneas hasta el próximo encabezado
            j = i + 1
            ans_lines = []
            while j < len(lines):
                if header_re.match(lines[j].strip()):
                    break
                ans_lines.append(lines[j])
                j += 1
            # limpiar respuesta
            ans = '\n'.join([a.strip() for a in ans_lines]).strip()
            if ans:
                faqs.append({
                    'question': question,
                    'answer': ans,
                    'source': path.parent.name,
                    'path': str(path)
                })
            i = j
        else:
            i += 1

    # dedup by question text preserving order
    seen = set()
    out = []
    for f in faqs:
        q = f['question'].strip()
        if q in seen:
            continue
        seen.add(q)
        out.append(f)
    return out


def run(data_dir='data', out_file='data/faqs.json'):
    p = Path(data_dir)
    out = []
    if not p.exists():
        print('No existe carpeta data/. Ejecuta el scraper primero.')
        return
    for categoria in p.iterdir():
        if not categoria.is_dir():
            continue
        for f in categoria.iterdir():
            if f.suffix.lower() != '.md':
                continue
            try:
                faqs = extract_from_md(f)
                out.extend(faqs)
            except Exception as e:
                print('error leyendo', f, e)

    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Exportadas {len(out)} FAQs a {out_file}')


if __name__ == '__main__':
    run()
