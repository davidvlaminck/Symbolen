#!/usr/bin/env python3
import sys
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import numpy as np
import os
import re


def main():
    # --- Namen uit bestand ---
    NAMES = []
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "namen.txt"), "r", encoding="utf-8") as f:
        content = f.read()
        matches = re.findall(r'"([^"]+)"', content)
        NAMES = matches

    first_names = [name.split()[0].upper() for name in NAMES]
    longest_name = max(first_names, key=len)
    print(f"Gelezen namen: {len(NAMES)}")
    print(f"Langste voornaam: {longest_name}")

    # --- Arial Bold font ---
    FONT_PATH = "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"

    # --- Base image ---
    IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uil_auto_opgeschoond_4x.png")
    base_img = Image.open(IMAGE_PATH).convert("RGB")
    IMG_W, IMG_H = base_img.size

    # --- Schaal naar 10 cm breedte (aspect ratio behouden) ---
    DPI = 300
    CM_TO_INCH = 0.393701
    RECT_W_CM = 10.0
    RECT_W_PX = int(RECT_W_CM * DPI * CM_TO_INCH)
    SCALE = RECT_W_PX / IMG_W
    RECT_H_PX = int(IMG_H * SCALE)
    RECT_H_CM = RECT_H_PX / (DPI * CM_TO_INCH)

    print(f"Rechthoek: {RECT_W_CM:.1f} x {RECT_H_CM:.1f} cm ({RECT_W_PX} x {RECT_H_PX} px)")
    print(f"Schaalfactor: {SCALE:.3f}")

    # --- Nummerplaat gebied (in uiteindelijke afbeelding) ---
    PLATE_X1 = int(RECT_W_PX * 0.10)
    PLATE_Y1 = int(RECT_H_PX * 0.72)
    PLATE_X2 = int(RECT_W_PX * 0.90)
    PLATE_Y2 = int(RECT_H_PX * 0.88)

    font_size_large = 64
    print(f"Fontgrootte op grote afbeelding: {font_size_large}")

    # --- Afbeeldingen met tekst aanmaken ---
    annotated = []
    ROTATION = -5.5
    PADDING_CM = 0.5
    PADDING_PX = int(PADDING_CM * DPI * CM_TO_INCH)

    for name in first_names:
        img = Image.new("RGB", (RECT_W_PX, RECT_H_PX), "white")
        img_w = RECT_W_PX - 2 * PADDING_PX
        img_h = RECT_H_PX - 2 * PADDING_PX
        car = base_img.resize((img_w, img_h), Image.LANCZOS)
        img.paste(car, (PADDING_PX, PADDING_PX))

        draw = ImageDraw.Draw(img)
        f = ImageFont.truetype(FONT_PATH, font_size_large)
        bbox = f.getbbox(name)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        y_offset = -126 - (len(name) - 4) * 2
        x = PLATE_X1 + (PLATE_X2 - PLATE_X1 - text_w) / 2 - 205
        y = PLATE_Y1 + (PLATE_Y2 - PLATE_Y1 - text_h) / 2 + y_offset

        text_layer = Image.new("RGBA", (text_w + 40, text_h + 40), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        text_draw.text((20, 20), name, fill="black", font=f)

        rotated_text = text_layer.rotate(ROTATION, resample=Image.Resampling.BICUBIC, expand=True)

        paste_x = int(x) - 20
        paste_y = int(y) - 20
        img.paste(rotated_text, (paste_x, paste_y), rotated_text)

        annotated.append(img)

    # --- PDF opstellen: Landscape A4, 2 naast elkaar ---
    OUTPUT_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nummerplaten.pdf")

    PAGE_W_CM = 29.7
    PAGE_H_CM = 21.0
    MARGIN = 0.5
    GAP = 4.0

    total_width = 2 * RECT_W_CM + GAP
    start_x = (PAGE_W_CM - total_width) / 2
    y = (PAGE_H_CM - RECT_H_CM) / 2

    positions = [
        (start_x, y),
        (start_x + RECT_W_CM + GAP, y),
    ]

    with PdfPages(OUTPUT_PDF) as pdf:
        for i in range(0, len(annotated), 2):
            fig = plt.figure(figsize=(PAGE_W_CM * CM_TO_INCH, PAGE_H_CM * CM_TO_INCH))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, PAGE_W_CM)
            ax.set_ylim(PAGE_H_CM, 0)
            ax.axis("off")

            for j in range(2):
                idx = i + j
                if idx >= len(annotated):
                    break
                x, y = positions[j]
                rect = Rectangle(
                    (x, y), RECT_W_CM, RECT_H_CM,
                    linewidth=3, edgecolor="black", facecolor="none"
                )
                ax.add_patch(rect)
                img_data = np.array(annotated[idx])
                ax.imshow(
                    img_data,
                    extent=(x, x + RECT_W_CM, y + RECT_H_CM, y),
                    aspect="auto",
                    interpolation="bilinear"
                )

            pdf.savefig(fig, dpi=DPI)
            plt.close(fig)
            print(f"Pagina {i // 2 + 1} klaar")

    print(f"PDF opgeslagen als: {OUTPUT_PDF}")

    # Rotate entire PDF 90° CCW: landscape -> portrait (frames + content rotate together)
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(OUTPUT_PDF)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(90)
        writer.add_page(page)
    with open(OUTPUT_PDF, "wb") as f:
        writer.write(f)
    print(f"PDF gedraaid naar portrait: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
