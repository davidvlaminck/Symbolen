import os
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from symbol_pdf import compute_grid, cell_xy, draw_square, draw_header

IMAGE_FOLDER = "images"
OUTPUT_PDF = "square_5.pdf"

SQUARE_CM = 5
SQUARE_MM = SQUARE_CM * 10
GAP_MM = 10
MARGIN_MM = 20
INTERNAL_MARGIN_MM = 3

PAGE_WIDTH_MM = 210
PAGE_HEIGHT_MM = 297

HEADER = "square 5x5 x 3"
HEADER_Y_MM = 15

images = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(".png")])

c = canvas.Canvas(OUTPUT_PDF, pagesize=(PAGE_WIDTH_MM * mm, PAGE_HEIGHT_MM * mm))

cols, rows, offset_x, offset_y = compute_grid(
    PAGE_WIDTH_MM, PAGE_HEIGHT_MM, SQUARE_MM, SQUARE_MM, GAP_MM, MARGIN_MM
)

draw_header(c, HEADER, PAGE_WIDTH_MM, PAGE_HEIGHT_MM, HEADER_Y_MM)

page = 0
col = 0
row = 0

for img_name in images:
    img_path = os.path.join(IMAGE_FOLDER, img_name)
    x, y = cell_xy(
        col, row, SQUARE_MM, SQUARE_MM, GAP_MM, MARGIN_MM, offset_x, offset_y, page_h_mm=PAGE_HEIGHT_MM
    )
    draw_square(c, x, y, SQUARE_MM, SQUARE_MM, img_path, INTERNAL_MARGIN_MM)

    col += 1
    if col == cols:
        col = 0
        row += 1
        if row == rows:
            row = 0
            c.showPage()
            page += 1
            draw_header(c, HEADER, PAGE_WIDTH_MM, PAGE_HEIGHT_MM, HEADER_Y_MM)

c.save()
print(f"Saved {OUTPUT_PDF} with {len(images)} images across {page + 1} page(s).")
