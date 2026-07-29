from PIL import Image
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
import os

IMAGE_FOLDER = "images"
OUTPUT_PDF = "output.pdf"

SQUARE_CM = 5
SQUARE_MM = SQUARE_CM * 10
GAP_MM = 10
MARGIN_MM = 20
INTERNAL_MARGIN_MM = 4

PAGE_WIDTH_MM = 210
PAGE_HEIGHT_MM = 297


def get_content_bounds(img):
    bg = img.getpixel((0, 0))
    w, h = img.size
    x_min = w
    y_min = h
    x_max = 0
    y_max = 0
    threshold = 30
    for y in range(h):
        for x in range(w):
            p = img.getpixel((x, y))
            dist = sum((a - b) ** 2 for a, b in zip(p, bg)) ** 0.5
            if dist > threshold:
                if x < x_min:
                    x_min = x
                if y < y_min:
                    y_min = y
                if x > x_max:
                    x_max = x
                if y > y_max:
                    y_max = y
    if x_min > x_max or y_min > y_max:
        return (0, 0, w, h)
    margin = int(min(w, h) * 0.02)
    x_min = max(0, x_min - margin)
    y_min = max(0, y_min - margin)
    x_max = min(w - 1, x_max + margin)
    y_max = min(h - 1, y_max + margin)
    return (x_min, y_min, x_max + 1, y_max + 1)


def clean_background(img):
    img = img.convert('RGB')
    bounds = get_content_bounds(img)
    img = img.crop(bounds)
    bg = img.getpixel((0, 0))
    pixels = img.load()
    w, h = img.size
    threshold = 30
    for y in range(h):
        for x in range(w):
            p = pixels[x, y]
            dist = sum((a - b) ** 2 for a, b in zip(p, bg)) ** 0.5
            if dist <= threshold:
                pixels[x, y] = (255, 255, 255)
    return img


images = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith('.png')])

c = canvas.Canvas(OUTPUT_PDF, pagesize=(PAGE_WIDTH_MM * mm, PAGE_HEIGHT_MM * mm))

cols = max(1, (PAGE_WIDTH_MM - 2 * MARGIN_MM + GAP_MM) // (SQUARE_MM + GAP_MM))
rows = max(1, (PAGE_HEIGHT_MM - 2 * MARGIN_MM + GAP_MM) // (SQUARE_MM + GAP_MM))

usable_w = PAGE_WIDTH_MM - 2 * MARGIN_MM
usable_h = PAGE_HEIGHT_MM - 2 * MARGIN_MM
grid_w = cols * SQUARE_MM + (cols - 1) * GAP_MM
grid_h = rows * SQUARE_MM + (rows - 1) * GAP_MM
offset_x = (usable_w - grid_w) / 2
offset_y = (usable_h - grid_h) / 2

page = 0
col = 0
row = 0

for img_name in images:
    img_path = os.path.join(IMAGE_FOLDER, img_name)
    img = Image.open(img_path)
    img = clean_background(img)

    img_path_tmp = f"/tmp/{img_name}"
    img.save(img_path_tmp)

    x = MARGIN_MM + offset_x + col * (SQUARE_MM + GAP_MM)
    y = PAGE_HEIGHT_MM - MARGIN_MM - offset_y - (row + 1) * SQUARE_MM - row * GAP_MM

    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(x * mm, y * mm, SQUARE_MM * mm, SQUARE_MM * mm)

    img_draw_size = SQUARE_MM - 2 * INTERNAL_MARGIN_MM
    c.drawImage(
        img_path_tmp,
        (x + INTERNAL_MARGIN_MM) * mm,
        (y + INTERNAL_MARGIN_MM) * mm,
        width=img_draw_size * mm,
        height=img_draw_size * mm,
        preserveAspectRatio=True
    )

    os.remove(img_path_tmp)

    col += 1
    if col == cols:
        col = 0
        row += 1
        if row == rows:
            row = 0
            c.showPage()
            page += 1

c.save()
print(f"Saved {OUTPUT_PDF} with {len(images)} images across {page + 1} page(s).")
