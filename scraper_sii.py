#!/usr/bin/env python3
"""
Scraper sencillo para extraer texto del sitio del SII.

Características:
- Crawl limitado por número de páginas
- Limpieza básica (elimina scripts, menús, headers, footers)
- Clasificación por palabras clave
- Detección de duplicados por hash
- Opción para usar Playwright si la página carga contenido por JS

Salida: archivos Markdown en `data/<categoria>/` con URL y contenido.
"""
import argparse
import hashlib
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

try:
    # opcional para similitud (puede ser lento/voluminoso)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def obtener_html_requests(url, timeout=10):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT)"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def obtener_html_playwright(url, timeout=15000):
    if not PLAYWRIGHT_AVAILABLE:
        return None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout)
            html = page.content()
            browser.close()
            return html
    except Exception:
        return None


def limpiar_texto(html, min_line_len=40):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    # eliminar comentarios
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.string)) and "<!--" in str(text)):
        try:
            comment.extract()
        except Exception:
            pass

    texto = soup.get_text(separator="\n")

    lineas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        # filtra líneas cortas que suelen ser menús o basura
        if len(linea) >= min_line_len:
            # normalizar espacios
            linea = re.sub(r"\s+", " ", linea)
            lineas.append(linea)

    return "\n\n".join(lineas)


def obtener_links(html, base_url, domain=None):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("mailto:") or href.endswith(".pdf"):
            continue
        try:
            enlace = urljoin(base_url, href)
        except Exception:
            continue
        if domain and domain not in enlace:
            continue
        links.add(enlace)
    return list(links)


def clasificar_texto(texto):
    categorias = {
        "boletas": ["boleta", "honorarios", "emisión", "retención"],
        "declaracion_renta": ["declaración", "renta", "formulario 22", "f22", "declarar"],
        "clave_tributaria": ["clave", "autenticación", "acceso", "clave tributaria"],
        "devoluciones": ["devolució", "excedente", "reembolso", "pago"],
        "empresas": ["empresa", "pyme", "sociedad", "inicio de actividades"],
    }

    texto_lower = texto.lower()
    for cat, keys in categorias.items():
        for k in keys:
            if k in texto_lower:
                return cat
    return "otros"


def safe_filename_from_url(url):
    path = urlparse(url).path
    if not path or path == "/":
        path = "index"
    name = re.sub(r"[^0-9a-zA-Z]+", "_", path).strip("_")
    # acortar si es muy largo
    if len(name) > 120:
        name = name[:120]
    return name or "page"


class Deduplicator:
    def __init__(self):
        self.hashes = set()
        self.texts = []

    def es_duplicado(self, texto):
        h = hashlib.md5(texto.encode("utf-8")).hexdigest()
        if h in self.hashes:
            return True
        self.hashes.add(h)
        return False

    def es_muy_similar(self, texto, umbral=0.92):
        if not SKLEARN_AVAILABLE:
            return False
        if not self.texts:
            self.texts.append(texto)
            return False
        try:
            vectorizer = TfidfVectorizer().fit_transform([texto] + self.texts)
            similitudes = cosine_similarity(vectorizer[0:1], vectorizer[1:])
            max_sim = max(similitudes[0]) if similitudes else 0
            if max_sim > umbral:
                return True
            self.texts.append(texto)
            return False
        except Exception:
            return False


def guardar_markdown(output_dir, categoria, url, contenido):
    carpeta = os.path.join(output_dir, categoria)
    os.makedirs(carpeta, exist_ok=True)
    nombre = safe_filename_from_url(url)
    ruta = os.path.join(carpeta, f"{nombre}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"# Página SII\n\n")
        f.write(f"## URL\n{url}\n\n")
        f.write(f"## Contenido\n\n{contenido}\n")


def crawl(start_url, max_pages=50, use_playwright=False, min_line_len=40, output_dir="data"):
    to_visit = [start_url]
    visited = set()
    deduper = Deduplicator()
    domain = urlparse(start_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print("Scrapeando:", url)
        visited.add(url)

        html = None
        if use_playwright:
            html = obtener_html_playwright(url)
        if not html:
            html = obtener_html_requests(url)
        if not html:
            continue

        texto = limpiar_texto(html, min_line_len=min_line_len)
        if len(texto) < 200:
            # demasiado corto para ser útil
            links = obtener_links(html, url, domain=domain)
            for l in links:
                if l not in visited and l not in to_visit and len(visited) + len(to_visit) < max_pages:
                    to_visit.append(l)
            time.sleep(1)
            continue

        if deduper.es_duplicado(texto):
            # salto si idéntico
            pass
        elif deduper.es_muy_similar(texto):
            pass
        else:
            categoria = clasificar_texto(texto)
            guardar_markdown(output_dir, categoria, url, texto)

        links = obtener_links(html, url, domain=domain)
        for l in links:
            if l not in visited and l not in to_visit and len(visited) + len(to_visit) < max_pages:
                to_visit.append(l)

        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Scraper para extraer texto del SII y guardarlo en .md")
    parser.add_argument("--start-url", default="https://www.sii.cl/servicios_online/renta/", help="URL inicial")
    parser.add_argument("--max-pages", type=int, default=30, help="Máximo de páginas a scrapear")
    parser.add_argument("--min-line-len", type=int, default=40, help="Longitud mínima de línea para filtro")
    parser.add_argument("--output-dir", default="data", help="Carpeta de salida")
    parser.add_argument("--use-playwright", action="store_true", help="Usar Playwright para render JS (si está instalado)")
    args = parser.parse_args()

    if args.use_playwright and not PLAYWRIGHT_AVAILABLE:
        print("Playwright no está instalado. Instala 'playwright' y ejecuta 'playwright install', o quita --use-playwright.")
        sys.exit(1)

    crawl(args.start_url, max_pages=args.max_pages, use_playwright=args.use_playwright, min_line_len=args.min_line_len, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
