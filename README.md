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

Notas de responsabilidad:
- Respeta términos de uso del sitio y evita sobrecargarlo: usa `--max-pages` bajo y latencia (el script ya duerme 1s entre peticiones).

Si quieres, puedo:
- Añadir export JSON/CSV
- Indexar los archivos para búsquedas locales o un pequeño chatbot RAG
- Ajustar reglas de limpieza para tu tipo de preguntas en la mesa de ayuda
