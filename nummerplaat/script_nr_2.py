#!/usr/bin/env python3
"""
script_nr_2.py - Voeg een pagina met kaders toe na elke nummerplaat-pagina.

De kaders op de lege pagina's matchen precies op de kaders van de nummerplaten,
zodat ze als raster/hulplijnen kunnen dienen bij afknippen of plaatsen.

Gebruik:
    python3 script_nr_2.py
"""
import os
import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
from pypdf import PdfReader, PdfWriter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PDF = os.path.join(SCRIPT_DIR, "nummerplaten.pdf")
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "nummerplaten_met_kader_paginas.pdf")
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
    tekst_path = os.path.join(SCRIPT_DIR, "tekst.txt")
    theme_lines = []
    if os.path.exists(tekst_path):
        with open(tekst_path, "r", encoding="utf-8") as f:
            all_lines = [line.strip() for line in f if line.strip()]
        # Lines after "mijn symbool" and "5 cm" headers
        in_theme = False
        for line in all_lines:
            if line == "Ons jaar thema:":
                in_theme = True
            elif in_theme:
                theme_lines.append(line)
    return theme_lines


def make_frame_only_page(theme_lines):
    """Create a portrait A4 page with empty frames + rotated text.
    Top: 'mijn symbool' (Arial Bold, groot). Bottom: theme text.
    Tekst staat gedraaid 90° met de bovenkant links."""
    fig = plt.figure(figsize=(PAGE_W_CM * CM_TO_INCH, PAGE_H_CM * CM_TO_INCH))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W_CM)
    ax.set_ylim(PAGE_H_CM, 0)
    ax.axis("off")

    for fx, fy in FRAME_POSITIONS:
        rect = Rectangle(
            (fx, fy), FRAME_W_CM, FRAME_H_CM,
            linewidth=3, edgecolor="black", facecolor="none"
        )
        ax.add_patch(rect)

    # Top text: "mijn symbool" — rotated 90° CW (bovenkant links)
    top_font = FontProperties(fname=FONT_PATH, size=24)
    ax.text(
        1.5, PAGE_W_CM / 2,
        "mijn symbool",
        fontproperties=top_font,
        rotation=-90, ha="center", va="center",
        color="black",
    )

    # Bottom text: theme lines — rotated 90° CW (bovenkant links)
    bottom_font = FontProperties(fname=FONT_PATH, size=12)
    # Position text block center near bottom-left
    n = len(theme_lines)
    block_height_cm = n * 0.5  # approx height of multi-line vertical text
    text_y = PAGE_H_CM - 3.0 - block_height_cm / 2
    theme_text = "\n".join(theme_lines)
    ax.text(
        1.5, text_y,
        theme_text,
        fontproperties=bottom_font,
        rotation=-90, ha="center", va="center",
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
        # Add frame-only page with frames + rotated text
        frame_reader = make_frame_only_page(theme_lines)
        writer.add_page(frame_reader.pages[0])

    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)

    total = len(reader.pages)
    print(f"PDF opgeslagen als: {OUTPUT_PDF}")
    print(f"  {total} nummerplaten-pagina's + {total} kader-pagina's = {total * 2} pagina's totaal")


if __name__ == "__main__":
    main()
