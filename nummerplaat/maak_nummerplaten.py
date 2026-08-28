#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import numpy as np
import os



first_names = [name.split()[0].upper() for name in NAMES]

# --- Arial Bold font ---
FONT_PATH = "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"

# --- Base image ---
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "auto.png")
base_img = Image.open(IMAGE_PATH).convert("RGB")
IMG_W, IMG_H = base_img.size  # 265 x 355

# --- Schaal naar 9x14 cm ---
DPI = 300
CM_TO_INCH = 0.393701
RECT_W_CM = 9.0
RECT_H_CM = 14.0
RECT_W_PX = int(RECT_W_CM * DPI * CM_TO_INCH)   # 1062 px
RECT_H_PX = int(RECT_H_CM * DPI * CM_TO_INCH)   # 1654 px
SCALE = RECT_W_PX / IMG_W

print(f"Rechthoek: {RECT_W_CM} x {RECT_H_CM} cm ({RECT_W_PX} x {RECT_H_PX} px)")
print(f"Schaalfactor: {SCALE:.2f}")

# --- Nummerplaat gebied (in uiteindelijke afbeelding) ---
PLATE_X1 = int(RECT_W_PX * 0.10)
PLATE_Y1 = int(RECT_H_PX * 0.72)
PLATE_X2 = int(RECT_W_PX * 0.90)
PLATE_Y2 = int(RECT_H_PX * 0.88)

# Fontgrootte direct op grote afbeelding (crisp rendering)
FONT_SIZE_ORIG = 16
font_size_large = int(FONT_SIZE_ORIG * SCALE)
print(f"Fontgrootte op grote afbeelding: {font_size_large}")

# --- Afbeeldingen met tekst aanmaken ---
annotated = []
for name in first_names:
    img = base_img.resize((RECT_W_PX, RECT_H_PX), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    
    f = ImageFont.truetype(FONT_PATH, font_size_large)
    bbox = f.getbbox(name)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Positie: -58px horizontaal, 10px omhoog (-10) van midden
    x = PLATE_X1 + (PLATE_X2 - PLATE_X1 - text_w) / 2 - 58
    y = PLATE_Y1 + (PLATE_Y2 - PLATE_Y1 - text_h) / 2 - 10
    
    draw.text((x, y), name, fill="black", font=f)
    annotated.append(img)

# --- PDF opstellen: Landscape A4, 3 naast elkaar ---
OUTPUT_PDF = os.path.join(os.path.dirname(__file__), "nummerplaten.pdf")

PAGE_W_CM = 29.7  # landscape A4 breedte
PAGE_H_CM = 21.0  # landscape A4 hoogte
MARGIN = 0.5      # cm
GAP = 0.3         # cm tussen de rechthoeken

# Bepaal posities voor 3 naast elkaar
total_width = 3 * RECT_W_CM + 2 * GAP
start_x = (PAGE_W_CM - total_width) / 2
y = (PAGE_H_CM - RECT_H_CM) / 2

positions = [
    (start_x, y),
    (start_x + RECT_W_CM + GAP, y),
    (start_x + 2 * (RECT_W_CM + GAP), y),
]

with PdfPages(OUTPUT_PDF) as pdf:
    for i in range(0, len(annotated), 3):
        fig = plt.figure(figsize=(PAGE_W_CM * CM_TO_INCH, PAGE_H_CM * CM_TO_INCH))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PAGE_W_CM)
        ax.set_ylim(PAGE_H_CM, 0)
        ax.axis("off")
        
        for j in range(3):
            idx = i + j
            if idx >= len(annotated):
                break
            x, y = positions[j]
            # Teken rechthoek
            rect = Rectangle(
                (x, y), RECT_W_CM, RECT_H_CM,
                linewidth=3, edgecolor="black", facecolor="none"
            )
            ax.add_patch(rect)
            # Plaats afbeelding met extent (in cm)
            img_data = np.array(annotated[idx])
            ax.imshow(
                img_data,
                extent=(x, x + RECT_W_CM, y + RECT_H_CM, y),
                aspect="auto",
                interpolation="bilinear"
            )
        
        pdf.savefig(fig, dpi=DPI)
        plt.close(fig)
        print(f"Pagina {i // 3 + 1} klaar")

print(f"PDF opgeslagen als: {OUTPUT_PDF}")
