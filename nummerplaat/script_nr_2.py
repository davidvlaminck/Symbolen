#!/usr/bin/env python3
"""
script_nr_2.py - Voeg een pagina met kaders toe na elke nummerplaat-pagina.

De kader-pagina's hebben lege frames die exact matchen op de nummerplaat-kaders.
Binnen elk kader staat:
  - Bovenaan links: "mijn symbool" (Arial Bold, groot), gecentreerd in tekstvak
  - Onderaan rechts: thematekst uit tekst.txt, gecentreerd in tekstvak
Tekst is 90° tegenwijzerzin gedraaid.

Gebruik:
    python3 script_nr_2.py
"""
import os
import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from pypdf import PdfReader, PdfWriter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PDF = os.path.join(SCRIPT_DIR, "nummerplaten.pdf")
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "nummerplaten_met_kader_paginas.pdf")
TEKST_TXT = os.path.join(SCRIPT_DIR, "tekst.txt")
FONT_PATH = "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"

CM_TO_INCH = 0.393701
DPI = 300

# Match maak_nummerplaten.py dimensions
RECT_W_CM = 10.0
RECT_H_CM = 15.0
GAP = 4.0

# Original page was landscape (29.7 x 21.0), rotated 90° CCW -> portrait (21.0 x 29.7)
PAGE_W_CM = 21.0
PAGE_H_CM = 29.7

# After 90° CCW rotation: frame dims swap (15 x 10 cm)
FRAME_W_CM = RECT_H_CM  # 15.0
FRAME_H_CM = RECT_W_CM  # 10.0

# Vertical stacking positions on portrait page
total_height = 2 * FRAME_H_CM + GAP
start_x = (PAGE_W_CM - FRAME_W_CM) / 2
start_y = (PAGE_H_CM - total_height) / 2

FRAME_POSITIONS = [
    (start_x, start_y),
    (start_x, start_y + FRAME_H_CM + GAP),
]


def load_theme_text():
    """Read theme lines (lines 8-10) from tekst.txt."""
    theme_lines = []
    if os.path.exists(TEKST_TXT):
        with open(TEKST_TXT, "r", encoding="utf-8") as f:
            all_lines = [line.strip() for line in f if line.strip()]
        in_theme = False
        for line in all_lines:
            if line == "Ons jaar thema:":
                in_theme = True
                theme_lines.append(line)
            elif in_theme:
                theme_lines.append(line)
    return theme_lines


def make_frame_only_page(theme_lines):
    """Create a portrait A4 page with 2 empty frames + rotated text inside each frame.
    Text is rotated 90° CCW, centered within each frame.
    "mijn symbool" in top half, theme text in bottom half."""
    fig = plt.figure(figsize=(PAGE_W_CM * CM_TO_INCH, PAGE_H_CM * CM_TO_INCH))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W_CM)
    ax.set_ylim(PAGE_H_CM, 0)
    ax.axis("off")

    top_font = FontProperties(fname=FONT_PATH, size=28)
    bottom_font = FontProperties(fname=FONT_PATH, size=14)
    theme_text = "\n".join(theme_lines)

    for fx, fy in FRAME_POSITIONS:
        # Draw frame rectangle
        rect = Rectangle(
            (fx, fy), FRAME_W_CM, FRAME_H_CM,
            linewidth=3, edgecolor="black", facecolor="none"
        )
        ax.add_patch(rect)

        # "mijn symbool" — links in frame, gecentreerd in bovenste helft, 90° CCW
        ax.text(
            fx + 1.5, fy + FRAME_H_CM * 0.5,
            "mijn symbool",
            fontproperties=top_font,
            rotation=90, ha="center", va="center",
            color="black",
        )

        # Theme tekst — rechts in frame, gecentreerd in onderste helft, 90° CCW
        ax.text(
            fx + FRAME_W_CM - 1.5, fy + FRAME_H_CM * 0.5,
            theme_text,
            fontproperties=bottom_font,
            rotation=90, ha="center", va="center",
            color="black",
        )

    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", dpi=DPI)
    plt.close(fig)
    buf.seek(0)
    return PdfReader(buf)


def main():
    reader = PdfReader(INPUT_PDF)
    writer = PdfWriter()

    theme_lines = load_theme_text()

    for page in reader.pages:
        writer.add_page(page)
        frame_reader = make_frame_only_page(theme_lines)
        writer.add_page(frame_reader.pages[0])

    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)

    total = len(reader.pages)
    print(f"PDF opgeslagen als: {OUTPUT_PDF}")
    print(f"  {total} nummerplaten-pagina's + {total} kader-pagina's = {total * 2} pagina's totaal")


if __name__ == "__main__":
    main()
