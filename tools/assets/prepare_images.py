"""Turn the three mascot JPEGs and the logo JPEG into transparent PNGs.

    python tools/assets/prepare_images.py <folder-with-jpegs>

Mascots (white background, a 1px grey frame on some): the frame is cropped
away, the white that is connected to the border becomes transparent (white
inside the figure, e.g. the robot's face, is kept), the edge is eroded by a
pixel to drop the white fringe and feathered.

Logo (light letters on a dark circuit-board picture): the word is cut out of
the picture, solid letters are kept, everything else (circuit lines, glow,
tagline) is dropped, and a thin dark outline is added so the neon colours stay
readable on the light header.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

OUT = Path(__file__).resolve().parents[2] / "frontend" / "src" / "assets" / "brand"
FRAME = 8  # px cropped off every side: removes the grey frame


def cut_mascot(src: Path, name: str, size: int = 320, white_min: int = 238) -> None:
    rgb = np.array(Image.open(src).convert("RGB"))[FRAME:-FRAME, FRAME:-FRAME]
    near_white = rgb.min(axis=2) >= white_min
    labels, _ = ndimage.label(near_white)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    background = np.isin(labels, border[border > 0])
    fg = ~background
    # keep only the biggest blob: drops stray specks and the faint ground shadow
    lab, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        fg = lab == (1 + int(np.argmax(sizes)))
    fg = ndimage.binary_fill_holes(fg)
    fg = ndimage.binary_erosion(fg, iterations=1)  # drop the whitish anti-alias fringe
    alpha = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.0)
    rgba = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    ys, xs = np.where(alpha > 0.02)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    img = Image.fromarray(rgba, "RGBA").crop(box)
    img.thumbnail((size, size), Image.LANCZOS)
    img.save(OUT / f"{name}.png", optimize=True)
    print(name, img.size)


def cut_logo(src: Path, name: str = "logo-wordmark", height: int = 100) -> None:
    rgb = np.array(Image.open(src).convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    # the word: bright AND saturated, inside the band where it sits
    band = np.zeros(rgb.shape[:2], bool)
    band[470:660, 180:1160] = True
    letters = band & (hsv[..., 2] > 150) & (hsv[..., 1] > 90)
    letters = ndimage.binary_closing(letters, iterations=1)
    # drop everything that is not a letter-sized blob (circuit traces are thin)
    lab, n = ndimage.label(letters)
    sizes = ndimage.sum(letters, lab, range(1, n + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s > 1500]
    letters = np.isin(lab, keep)
    # small compact marks that belong to the letters (the breve over "Й"):
    # inside the word's span, close above it, and blob-shaped, unlike traces
    ys, xs = np.where(letters)
    top, left, right = ys.min(), xs.min(), xs.max()
    for i, s in enumerate(sizes):
        if 1500 >= s > 250:
            yy, xx = np.where(lab == i + 1)
            h, w = np.ptp(yy) + 1, np.ptp(xx) + 1
            if (
                xx.min() > left and xx.max() < right
                and yy.min() > top - 70 and yy.max() < top + 40
                and s / (h * w) > 0.3
            ):
                letters |= lab == i + 1
    ys, xs = np.where(letters)
    # the tagline sits below the word: cut at the word's own bottom edge
    word_bottom = int(np.percentile(ys, 99.5))
    letters[word_bottom + 1 :] = False
    ys, xs = np.where(letters)
    pad = 14
    y0, y1, x0, x1 = ys.min() - pad, ys.max() + pad, xs.min() - pad, xs.max() + pad
    letters, rgb = letters[y0:y1, x0:x1], rgb[y0:y1, x0:x1]

    # 1) letters: keep the neon gradient, but deepen it so it holds on a light background
    f = rgb.astype(np.float32) / 255
    f = np.clip(f * 0.82, 0, 1)
    lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
    f = np.clip(lum[..., None] + (f - lum[..., None]) * 1.25, 0, 1)
    body = ndimage.binary_erosion(letters, iterations=1)
    # 2) outline: dark navy ring around the letters
    ring = ndimage.binary_dilation(letters, iterations=5)
    navy = np.array([22, 20, 58], np.float32) / 255
    out = np.where(body[..., None], f, navy)
    a_ring = cv2.GaussianBlur(ring.astype(np.float32), (0, 0), 1.2)
    # letters stay fully opaque over the ring
    a_body = cv2.GaussianBlur(body.astype(np.float32), (0, 0), 0.8)
    alpha = np.maximum(a_ring, a_body)
    rgba = np.dstack([(out * 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    img = Image.fromarray(rgba, "RGBA")
    w = round(img.width * height / img.height)
    img = img.resize((w, height), Image.LANCZOS)
    img.save(OUT / f"{name}.png", optimize=True)
    print(name, img.size)


if __name__ == "__main__":
    folder = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    cut_mascot(folder / "5393575572354570933.jpg", "mascot-coin")
    cut_mascot(folder / "5393575572354570934.jpg", "mascot-shield")
    cut_mascot(folder / "5393575572354570935.jpg", "mascot-robot")
    cut_logo(folder / "5393575572354570938.jpg")
