#!/usr/bin/env python3
"""Merge a generated intro clip onto the wallpaper it belongs to.

Omarchy 4.5 plays `backgrounds/intros/<stem>.mp4` before it shows the still
`backgrounds/<stem>.png`. The clip must therefore end on the still, or the swap
shows a jump. A generated clip drifts: measured on the Kling source, the last
frame sat 11 % larger than the still about the vanishing point, with the limb
20 px lower at 1080p.

This script removes that drift and lands the clip on the still:

  1. extract the frames at the theme's output size with ffmpeg
  2. resample every frame with one constant similarity (scale about the
     vanishing point + translation), which is the transform that maps the last
     frame onto the wallpaper. The constant is used for the whole clip, so the
     clip's own motion survives and no frame is compared against the still.
  3. pad the source by reflection on top and at the sides, and continue the
     bottom rows along their measured gradient. Shrinking content widens the
     field of view past the frame, and a flat replicated band would read as a
     frozen stripe in the planet body.
  4. over the last `--settle` seconds, blend the corrected frames into the
     still with a smoothstep, and write the still itself as the final frame.

The last frame then equals the wallpaper bit for bit; the frames before it
differ by a fading residue instead of a step.

Measure the constants first (fit scale + translation that minimises the mean
absolute difference between the clip's last frame and the wallpaper at the
output size). Guessed constants give a visible hop.

    python3 tools/merge-intro.py --src /tmp/source.mp4 \\
      --wallpaper backgrounds/1-horisont.png --out /tmp/merged \\
      --width 2560 --height 1440 --fps 24 \\
      --scale 0.898 --tx -1.3333 --ty -6.6667 --vp 0.50,0.62 --settle 0.5

    ffmpeg -framerate 24 -i /tmp/merged/%03d.png -c:v libx264 -profile:v high \\
      -pix_fmt yuv420p -crf 18 -movflags +faststart backgrounds/intros/horisont.mp4

Needs Pillow and NumPy; ffmpeg for the extraction.
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image


def extract(src, out_dir, width, height, fps):
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "*.png")):
        os.remove(old)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", src,
         "-vf", f"scale={width}:{height}:flags=lanczos", "-vsync", "0",
         os.path.join(out_dir, "%03d.png")],
        check=True)
    frames = sorted(glob.glob(os.path.join(out_dir, "*.png")))
    if not frames:
        sys.exit("no frames extracted")
    return frames


def pad_frame(a, pad, pad_top, pad_side, pad_bottom):
    """Reflect above and at the sides; continue the bottom along its gradient."""
    A = a.astype(np.float32)
    P = np.pad(A, ((pad_top, 0), (pad_side, pad_side), (0, 0)), mode="reflect")
    slope = (A[-1] - A[-21]) / 20.0
    k = np.arange(1, pad_bottom + 1, dtype=np.float32)[:, None, None]
    extra = A[-1][None, :, :] + slope[None, :, :] * k * np.power(0.985, k)
    extra = np.pad(np.clip(extra, 0, 255), ((0, 0), (pad_side, pad_side), (0, 0)),
                   mode="reflect")
    return np.concatenate([P, extra], axis=0)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="generated clip")
    ap.add_argument("--wallpaper", required=True, help="the still the clip must end on")
    ap.add_argument("--out", required=True, help="directory for the merged frames")
    ap.add_argument("--frames-dir", default="/tmp/merge-intro-src",
                    help="scratch directory for the extracted frames")
    ap.add_argument("--width", type=int, default=2560)
    ap.add_argument("--height", type=int, default=1440)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--scale", type=float, default=0.898,
                    help="sampling scale about the vanishing point (fitted)")
    ap.add_argument("--tx", type=float, default=-1.3333, help="x translation, output px")
    ap.add_argument("--ty", type=float, default=-6.6667, help="y translation, output px")
    ap.add_argument("--vp", default="0.50,0.62", help="vanishing point as fractions of w,h")
    ap.add_argument("--settle", type=float, default=0.5,
                    help="seconds of the closing blend into the still")
    ap.add_argument("--pad", type=int, default=200)
    args = ap.parse_args()

    W, H = args.width, args.height
    s = args.scale
    tx, ty = args.tx, args.ty
    vpx, vpy = (float(v) for v in args.vp.split(","))
    cx, cy = vpx * W, vpy * H

    frames = extract(args.src, args.frames_dir, W, H, args.fps)
    os.makedirs(args.out, exist_ok=True)
    for old in glob.glob(os.path.join(args.out, "*.png")):
        os.remove(old)

    still = np.asarray(Image.open(args.wallpaper).convert("RGB")
                       .resize((W, H), Image.LANCZOS)).astype(np.float32)

    Tx = Ty = args.pad
    xs = (np.arange(W, dtype=np.float32) - cx - tx) / s + cx
    ys = (np.arange(H, dtype=np.float32) - cy - ty) / s + cy
    if xs.min() < -Tx or ys.min() < -Ty or xs.max() > W - 1 + Tx or ys.max() > H - 1 + Ty:
        sys.exit(f"pad {args.pad} too small: x {xs.min():.0f}..{xs.max():.0f}, "
                 f"y {ys.min():.0f}..{ys.max():.0f}")

    xi = xs + Tx
    yi = ys + Ty
    x0 = np.floor(xi).astype(np.int32)
    y0 = np.floor(yi).astype(np.int32)
    fx = (xi - x0)[None, :, None].astype(np.float32)
    fy = (yi - y0)[:, None, None].astype(np.float32)

    blend = max(1, int(round(args.settle * args.fps)))
    n = len(frames)
    for i, path in enumerate(frames):
        a = np.asarray(Image.open(path).convert("RGB"))
        P = pad_frame(a, args.pad, Ty, Tx, args.pad)
        p00 = P[np.ix_(y0, x0)]
        p01 = P[np.ix_(y0, x0 + 1)]
        p10 = P[np.ix_(y0 + 1, x0)]
        p11 = P[np.ix_(y0 + 1, x0 + 1)]
        out = ((p00 * (1 - fx) + p01 * fx) * (1 - fy)
               + (p10 * (1 - fx) + p11 * fx) * fy)
        k = i - (n - blend)
        if k >= 0:
            u = (k + 1) / blend
            u = u * u * (3 - 2 * u)
            out = (1 - u) * out + u * still
        frame = still.copy() if i == n - 1 else np.clip(np.round(out), 0, 255)
        Image.fromarray(frame.astype(np.uint8)).save(
            os.path.join(args.out, "%03d.png" % (i + 1)))
    print(f"{n} frames, {W}x{H} at {args.fps} fps, scale {s}, "
          f"vp {vpx}/{vpy}, settle {args.settle}s -> {args.out}")


if __name__ == "__main__":
    main()
