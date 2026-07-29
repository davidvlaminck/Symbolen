from PIL import Image
from reportlab.lib.units import mm


def clean_symbol(img, threshold=30, margin_pct=0.02):
    img = img.convert("RGB")
    w, h = img.size
    bg = img.getpixel((0, 0))
    x_min, y_min, x_max, y_max = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            p = img.getpixel((x, y))
            dist = sum((a - b) ** 2 for a, b in zip(p, bg)) ** 0.5
            if dist > threshold:
                if x < x_min: x_min = x
                if y < y_min: y_min = y
                if x > x_max: x_max = x
                if y > y_max: y_max = y
    if x_min > x_max or y_min > y_max:
        return img
    m = int(min(w, h) * margin_pct)
    x_min = max(0, x_min - m)
    y_min = max(0, y_min - m)
    x_max = min(w - 1, x_max + m)
    y_max = min(h - 1, y_max + m)
    img = img.crop((x_min, y_min, x_max + 1, y_max + 1))
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            p = pixels[x, y]
            dist = sum((a - b) ** 2 for a, b in zip(p, bg)) ** 0.5
            if dist <= threshold:
                pixels[x, y] = (255, 255, 255)
    return img


def compute_grid(page_w_mm, page_h_mm, cell_w_mm, cell_h_mm, gap_mm, margin_mm):
    usable_w = page_w_mm - 2 * margin_mm
    usable_h = page_h_mm - 2 * margin_mm
    cols = max(1, (usable_w + gap_mm) // (cell_w_mm + gap_mm))
    rows = max(1, (usable_h + gap_mm) // (cell_h_mm + gap_mm))
    grid_w = cols * cell_w_mm + (cols - 1) * gap_mm
    grid_h = rows * cell_h_mm + (rows - 1) * gap_mm
    offset_x = (usable_w - grid_w) / 2
    offset_y = (usable_h - grid_h) / 2
    return cols, rows, offset_x, offset_y


def cell_xy(
    col, row, cell_w_mm, cell_h_mm, gap_mm, margin_mm, offset_x, offset_y, page_h_mm=None
):
    x = margin_mm + offset_x + col * (cell_w_mm + gap_mm)
    y_from_top = offset_y + (row + 1) * cell_h_mm + row * gap_mm
    y = (page_h_mm - margin_mm - y_from_top) if page_h_mm is not None else y_from_top
    return x, y


def draw_header(c, text, page_w_mm, page_h_mm, y_mm_from_top=15, font_size=12):
    from reportlab.lib.colors import black
    c.setFillColor(black)
    c.setFont("Helvetica", font_size)
    c.drawCentredString(
        (page_w_mm / 2) * mm,
        (page_h_mm - y_mm_from_top) * mm,
        text,
    )


def draw_square(c, x, y, w, h, img_path, internal_margin_mm=0):
    from reportlab.lib.colors import black
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(x * mm, y * mm, w * mm, h * mm)
    img = Image.open(img_path)
    img = clean_symbol(img)
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img.save(tmp)
    draw_w = w - 2 * internal_margin_mm
    draw_h = h - 2 * internal_margin_mm
    c.drawImage(
        tmp,
        (x + internal_margin_mm) * mm,
        (y + internal_margin_mm) * mm,
        width=draw_w * mm,
        height=draw_h * mm,
        preserveAspectRatio=True,
    )
    os.remove(tmp)


def draw_circle(c, x, y, size_mm, img_path, internal_margin_mm=0):
    from reportlab.lib.colors import black
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.circle(
        (x + size_mm / 2) * mm,
        (y + size_mm / 2) * mm,
        (size_mm / 2) * mm,
        stroke=1,
        fill=0,
    )
    img = Image.open(img_path)
    img = clean_symbol(img)
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img.save(tmp)
    draw_size = size_mm - 2 * internal_margin_mm
    c.drawImage(
        tmp,
        (x + internal_margin_mm) * mm,
        (y + internal_margin_mm) * mm,
        width=draw_size * mm,
        height=draw_size * mm,
        preserveAspectRatio=True,
    )
    os.remove(tmp)
