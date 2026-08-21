import os
import numpy as np
from PIL import Image
import scipy.ndimage

INPUT_FOLDER = "images"
OUTPUT_FOLDER = "output_contouren"

BG_THRESHOLD = 20
DARK_THRESHOLD = 40


def extract_contours(img_path, output_path):
    img = Image.open(img_path).convert("RGBA")
    rgba = np.array(img)
    rgb = rgba[:, :, :3]

    h, w = rgb.shape[:2]
    corners = np.array([
        rgb[0, 0],
        rgb[0, w - 1],
        rgb[h - 1, 0],
        rgb[h - 1, w - 1],
    ])
    bg_color = np.mean(corners, axis=0)

    dist = np.linalg.norm(rgb - bg_color, axis=2)
    bg_mask = dist < BG_THRESHOLD

    gray = np.mean(rgb, axis=2)

    out = np.zeros((h, w, 4), dtype=np.uint8)
    keep = (gray < DARK_THRESHOLD) & ~bg_mask
    keep = scipy.ndimage.binary_closing(keep, structure=np.ones((3, 3)))
    out[keep] = [0, 0, 0, 255]

    Image.fromarray(out, mode="RGBA").save(output_path)


def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    files = sorted([f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".png")])
    count = 0
    for name in files:
        src = os.path.join(INPUT_FOLDER, name)
        dst = os.path.join(OUTPUT_FOLDER, name)
        extract_contours(src, dst)
        count += 1
    print(f"Verwerkt {count} afbeeldingen naar {OUTPUT_FOLDER}/")


if __name__ == "__main__":
    main()
