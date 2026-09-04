import os
from collections import deque

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation

INPUT_FOLDER = "images"
OUTPUT_FOLDER = "symbolen_improved"

FLOOD_THRESHOLD = 10
FAR_THRESHOLD = 20
NEAR_THRESHOLD = 10
NEAR_DILATION = 5


def remove_checkerboard(img_path, output_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img, dtype=float)
    rgb = arr[:, :, :3]
    h, w = rgb.shape[:2]

    corners = np.array(
        [
            rgb[0, 0],
            rgb[0, w - 1],
            rgb[h - 1, 0],
            rgb[h - 1, w - 1],
        ]
    )
    bg = np.mean(corners, axis=0)

    dist = np.linalg.norm(rgb - bg, axis=2)

    visited = np.zeros((h, w), dtype=bool)
    queue = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)])
    for y, x in queue:
        visited[y, x] = True

    while queue:
        y, x = queue.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < h
                and 0 <= nx < w
                and not visited[ny, nx]
                and dist[ny, nx] < FLOOD_THRESHOLD
            ):
                visited[ny, nx] = True
                queue.append((ny, nx))

    symbol_mask = ~visited
    near_symbol = binary_dilation(symbol_mask, iterations=NEAR_DILATION)
    far_mask = ~near_symbol

    bg_mask = visited | (far_mask & (dist < FAR_THRESHOLD)) | (near_symbol & (dist < NEAR_THRESHOLD))

    out = rgb.copy()
    out[bg_mask] = bg
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = out.astype(np.uint8)
    rgba[:, :, 3] = 255
    Image.fromarray(rgba, mode="RGBA").save(output_path)


def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    files = sorted([f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".png")])
    count = 0
    for name in files:
        src = os.path.join(INPUT_FOLDER, name)
        dst = os.path.join(OUTPUT_FOLDER, name)
        remove_checkerboard(src, dst)
        count += 1
    print(f"Verwerkt {count} afbeeldingen naar {OUTPUT_FOLDER}/")


if __name__ == "__main__":
    main()
