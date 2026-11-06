#!/usr/bin/env python3
"""Render an Omarchy theme intro clip out of a single shipped wallpaper.

The shot is the wallpaper brought to life.  Two things move, both as a deviation
from the shipped image that decays to nothing:

  star field : starts at `--growth0` of its final radius around the vanishing
               point, so the stars sit near the point on short streaks and stream
               outward while their streaks lengthen: forward flight.
  planet     : the limb's highlight slides by `--turn` degrees about the planet's
               centre: the planet turns.

Every frame is base + stars, and base + stars == the wallpaper at rest, so the last
frame IS the still that OWE swaps to.  The star layer is padded by reflection,
because a star field that starts closer to the vanishing point must draw content
from outside the frame; the ground is flat, so a reflected margin is indistinguishable
from the real field.

Inputs: <bg>/<tag>-1-horisont.png (6016x3384).
"""

import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None

FULL = (6016, 3384)
# Circle fit to the limb's upper edge on the shipped wallpapers, 6016x3384 coordinates.
GEOMETRY = {
    "T1": {"cx": 3008.3, "cy": 10213.7, "R": 7697.9, "thick": 206.0},
    "T2": {"cx": 3008.9, "cy": 10384.9, "R": 8001.8, "thick": 367.0},
}
VP = (0.539, 0.685)     # vanishing point of the star field, fraction of the frame
PAD = 0.45              # reflected star-layer margin, fraction of the frame
SIGMA_PER_PX = 0.00355  # high-pass radius that separates stars from the ground
STAR_MARGIN = 0.02      # keep the star layer this far above the limb, fraction of height


def ease(t):
    return t * t * (3.0 - 2.0 * t)


def load_ref(path, size):
    return np.asarray(Image.open(path).convert("RGB").resize(size, Image.LANCZOS))


def split_stars(ref_u8, g, size):
    """base (ground + limb) and layer (stars), with base + layer == ref."""
    sigma = max(1.2, SIGMA_PER_PX * size[0])
    sm = np.asarray(Image.fromarray(ref_u8).filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    ref = ref_u8.astype(np.float32)
    layer = ref - sm
    layer *= star_region(g, size)[..., None]
    return ref - layer, layer


def star_region(g, size):
    w, h = size
    x = np.arange(w, dtype=np.float32)[None, :]
    top = g["cy"] - np.sqrt(np.maximum(g["R"] ** 2 - (x - g["cx"]) ** 2, 0.0))
    y = np.arange(h, dtype=np.float32)[:, None]
    edge = top - STAR_MARGIN * h
    return np.clip((edge - y) / (0.01 * h), 0, 1).astype(np.float32)


def band_weight(g, size):
    w, h = size
    feather = max(2.0, g["thick"] * 0.32)
    x = np.arange(w, dtype=np.float32)[None, :]
    y = np.arange(h, dtype=np.float32)[:, None]
    top = g["cy"] - np.sqrt(np.maximum(g["R"] ** 2 - (x - g["cx"]) ** 2, 0.0))
    depth = y - top
    wgt = np.minimum(np.clip(depth / feather, 0, 1), np.clip((g["thick"] + feather - depth) / feather, 0, 1))
    wgt[depth < 0] = 0.0
    return wgt.astype(np.float32)


def bilinear(img, xs, ys):
    h, w, _ = img.shape
    x0 = np.clip(np.floor(xs).astype(np.int32), 0, w - 1)
    y0 = np.clip(np.floor(ys).astype(np.int32), 0, h - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)
    y1 = np.clip(y0 + 1, 0, h - 1)
    fx = np.clip(xs - x0, 0, 1)[..., None]
    fy = np.clip(ys - y0, 0, 1)[..., None]
    return (img[y0, x0] * (1 - fx) + img[y0, x1] * fx) * (1 - fy) + (img[y1, x0] * (1 - fx) + img[y1, x1] * fx) * fy


def render(tag, args, report):
    w, h = args.width, args.height
    src = os.path.join(args.bg, f"{tag}-1-horisont.png")
    if not os.path.exists(src):
        src = os.path.join(args.bg, "1-horisont.png")
    ref_u8 = load_ref(src, (w, h))
    k = w / FULL[0]
    g = {key: GEOMETRY[tag][key] * k for key in GEOMETRY[tag]}
    base, layer = split_stars(ref_u8, g, (w, h))

    pad = int(round(PAD * max(w, h)))
    layer_pad = np.pad(layer, ((pad, pad), (pad, pad), (0, 0)), mode="reflect")
    band = band_weight(g, (w, h))
    # The rotation slides the band's content along the arc.  Near the frame's left and
    # right edges the arc runs out of frame, so fade the rotation out there instead of
    # sampling clamped pixels: a strong turn would otherwise distort the horizon corners.
    taper = np.clip((np.minimum(np.arange(w), np.arange(w)[::-1]) / (0.18 * w)), 0, 1)[None, :]
    band *= taper.astype(np.float32)
    pivot = (VP[0] * w, VP[1] * h)

    out_dir = os.path.join(args.out, tag)
    os.makedirs(out_dir, exist_ok=True)
    n = args.frames
    xs = np.arange(w, dtype=np.float32)[None, :] + 0.5
    ys = np.arange(h, dtype=np.float32)[:, None] + 0.5
    for i in range(args.count):
        t = i / (n - 1)
        if t <= args.hold:
            e = 0.0
        elif t >= args.settle:
            e = 1.0
        else:
            e = ease((t - args.hold) / (args.settle - args.hold))
        scale = args.growth0 + (1.0 - args.growth0) * e
        turn = args.turn * (1.0 - e)

        if i == n - 1:
            frame = ref_u8
        else:
            px = pivot[0] + (xs - pivot[0]) / scale + pad
            py = pivot[1] + (ys - pivot[1]) / scale + pad
            stars = bilinear(layer_pad, px, py)
            if turn:
                rad = math.radians(turn)
                cos, sin = math.cos(rad), math.sin(rad)
                yy = ys - g["cy"]
                xx = xs - g["cx"]
                rx = np.clip(g["cx"] + xx * cos - yy * sin - 0.5, 0, w - 1)
                ry = np.clip(g["cy"] + xx * sin + yy * cos - 0.5, 0, h - 1)
                rotated = bilinear(base, rx, ry)
                frame_src = base * (1 - band[..., None]) + rotated * band[..., None]
            else:
                frame_src = base
            frame = np.clip(frame_src + stars, 0, 255).astype(np.uint8)
        Image.fromarray(frame).save(os.path.join(out_dir, f"f{i:04d}.png"), compress_level=1)
        if i in (0, n - 1) or args.probe:
            d = np.abs(frame.astype(np.int16) - ref_u8.astype(np.int16))
            report[tag].append({"frame": i, "max": int(d.max()), "mean": round(float(d.mean()), 3),
                                "p99": int(np.percentile(d, 99)), "scale": round(scale, 3),
                                "turn": round(turn, 3)})
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", default=os.path.expanduser("~/.hermes/cache/scratch/omarchy-intro/bg"))
    ap.add_argument("--out", default=os.path.expanduser("~/.hermes/cache/scratch/omarchy-intro/out3"))
    ap.add_argument("--themes", default="T1,T2")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--frames", type=int, default=144)
    ap.add_argument("--count", type=int, default=0)
    ap.add_argument("--growth0", type=float, default=0.70)
    ap.add_argument("--turn", type=float, default=-0.9)
    ap.add_argument("--hold", type=float, default=0.08)
    ap.add_argument("--settle", type=float, default=0.92)
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()
    if not args.count:
        args.count = args.frames
    report = {tag: [] for tag in args.themes.split(",")}
    for tag in args.themes.split(","):
        render(tag, args, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
