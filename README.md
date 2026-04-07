# Scraper SII — extracción de texto para NotebookLM

Proyecto pequeño para extraer texto público del sitio del SII, limpiarlo y guardarlo en archivos Markdown listos para importar a NotebookLM.

Pasos rápidos:

1. Crear entorno y dependencias

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Si usarás Playwright (opcional, sólo si necesita JS):

```bash
pip install playwright
playwright install
```

3. Ejecutar el scraper

```bash
python scraper_sii.py --start-url "https://www.sii.cl/servicios_online/renta/" --max-pages 30
```

Opciones importantes:
- `--use-playwright`: renderiza JS con Playwright (si está instalado)
- `--max-pages`: límite de páginas a scrapear
- `--min-line-len`: filtra líneas cortas (reduce ruido)
- `--output-dir`: carpeta donde se guardan los .md

Salida:

Carpeta `data/` con subcarpetas por categoría (ej. `declaracion_renta`, `boletas`, `otros`) y archivos `.md` que contienen la URL y el contenido limpio.

4. Construir índice para búsquedas / NotebookLM

```bash
python build_index.py
# crea `data/index.jsonl` con una línea JSON por documento
```

5. Buscar en el índice (CLI simple)

```bash
python search_index.py "renta" --top 5
```

Notas de responsabilidad:
- Respeta términos de uso del sitio y evita sobrecargarlo: usa `--max-pages` bajo y latencia (el script ya duerme 1s entre peticiones).

Si quieres, puedo:
- Añadir export JSON/CSV
- Indexar los archivos para búsquedas locales o un pequeño chatbot RAG
- Ajustar reglas de limpieza para tu tipo de preguntas en la mesa de ayuda

Archivos y utilidades añadidas
- `scraper_sii.py`: scraper principal (requests + BeautifulSoup + opción Playwright).
- `build_index.py`: genera `data/index.jsonl` a partir de los `.md`/`.json` scrapeados.
- `search_index.py`: buscador CLI sencillo sobre el índice.
- `export_notebooklm.py`: exporta todo a `data/notebooklm_export.json` listo para NotebookLM.
- `extract_faqs.py`: heurística para extraer preguntas/respuestas desde los `.md` y generar `data/faqs.json`.

Flujo recomendado rápido:
1. Ejecutar el scraper (usar `--use-playwright` si la página carga JS):

```bash
python scraper_sii.py --start-url "https://www.sii.cl/servicios_online/renta/" --max-pages 50 --use-playwright
```

2. Construir índice y probar búsquedas:

```bash
python build_index.py
python search_index.py "consulta" --top 5
```

3. Exportar para NotebookLM:

```bash
python export_notebooklm.py
```

4. Extraer FAQs heurísticas:

```bash
python extract_faqs.py
```

Donde se guardan los resultados:
- `data/`: salida por categoría (`*.md`, `*.json`)
- `data/index.jsonl`: índice línea-por-documento
- `data/notebooklm_export.json`: export para NotebookLM
- `data/faqs.json`: preguntas/respuestas extraídas

Contribuye atentamente: evita usar `--max-pages` muy alto y respeta pausas entre peticiones.
