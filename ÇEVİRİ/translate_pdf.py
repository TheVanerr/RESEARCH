# -*- coding: utf-8 -*-
"""Append English-translated pages to schematic PDFs, preserving text positions."""
from __future__ import annotations

import json
from pathlib import Path

import fitz

INPUT_PDF = Path(r"c:\Users\fatih.gural\Desktop\PROJECTS\RESEARCH\ÇEVİRİ\CNK KBN 1B ORDEL SIYIRICI BLOEWR 2026.pdf")
OUTPUT_PDF = Path(r"c:\Users\fatih.gural\Desktop\PROJECTS\RESEARCH\ÇEVİRİ\CNK KBN 1B ORDEL SIYIRICI BLOEWR 2026 (TR+EN).pdf")
GLOSSARY_PATH = Path(__file__).with_name("translations.json")


def load_glossary() -> dict[str, str]:
    with GLOSSARY_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def color_to_rgb(value: int) -> tuple[float, float, float]:
    if value == 0:
        return (0, 0, 0)
    r = (value >> 16) & 255
    g = (value >> 8) & 255
    b = value & 255
    return (r / 255, g / 255, b / 255)


def cover_rect(bbox: fitz.Rect, translated: str, original: str, page_rect: fitz.Rect) -> fitz.Rect:
    width = bbox.width
    if len(translated.strip()) > len(original.strip()):
        width *= len(translated) / max(len(original), 1)
    width = max(width, bbox.width * 1.1)
    return fitz.Rect(bbox.x0, bbox.y0, bbox.x0 + width, bbox.y1) & page_rect


def fit_fontsize(page: fitz.Page, text: str, fontsize: float, max_width: float) -> float:
    size = fontsize
    while size > 4.0:
        width = fitz.get_text_length(text, fontname="helv", fontsize=size)
        if width <= max_width:
            return size
        size *= 0.92
    return size


def overlay_translation(page: fitz.Page, text: str, span: dict, translated: str) -> bool:
    bbox = fitz.Rect(span["bbox"])
    cover = cover_rect(bbox, translated, text, page.rect)
    pad = 1.2
    white = fitz.Rect(cover.x0 - pad, cover.y0 - pad, cover.x1 + pad, cover.y1 + pad)
    page.draw_rect(white, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    base_size = span.get("size", 10)
    fontsize = fit_fontsize(page, translated, base_size, max(cover.width, bbox.width))
    rgb = color_to_rgb(span.get("color", 0))
    origin = span.get("origin")
    point = fitz.Point(origin[0], origin[1]) if origin else fitz.Point(bbox.x0, bbox.y1 - 1)

    return bool(
        page.insert_text(
            point,
            translated,
            fontname="helv",
            fontsize=fontsize,
            color=rgb,
            overlay=True,
        )
    )


def main() -> None:
    glossary = load_glossary()
    src = fitz.open(INPUT_PDF)
    out = fitz.open()
    out.insert_pdf(src)

    applied = 0
    missing: set[str] = set()

    for page_index in range(src.page_count):
        src_page = src[page_index]
        new_page = out.new_page(width=src_page.rect.width, height=src_page.rect.height)
        new_page.show_pdf_page(new_page.rect, src, page_index)

        for block in src_page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if text not in glossary:
                        continue
                    if overlay_translation(new_page, text, span, glossary[text]):
                        applied += 1

    out.save(OUTPUT_PDF, garbage=4, deflate=True)
    out.close()
    src.close()

    print(f"Saved: {OUTPUT_PDF}")
    print(f"Glossary entries: {len(glossary)}")
    print(f"Applied overlays: {applied}")
    print(f"Pages: {fitz.open(OUTPUT_PDF).page_count}")


if __name__ == "__main__":
    main()
