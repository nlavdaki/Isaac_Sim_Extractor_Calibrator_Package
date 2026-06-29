r"""Compose native-Isaac illuminance figures (uv, GPU-free).

Lays out one or more native NVIDIA Isaac Sim RTX PtIlluminance screenshots into a
publication figure with a shared jet colour bar (0-35 klux by default) matching the
Isaac illuminance legend. Two uses:

  F7   single-panel rooftop lux map (e.g. Location A at solar noon)
  F9b  three-panel Location-J inter-building occlusion: the three low-sun timestamps
       that are the largest leave-location-out scatter outliers, where the monitored
       pixel (red marker, pixel 618,346) is shadowed by neighbouring buildings

Using native screenshots keeps F7/F9b colour-harmonic with the other Isaac renders
(F10/F10b, F16b). Panel titles come from --panel-titles if given, else from a
Location_<ID>_YYYYMMDD_HH_MM filename, else blank. A legend grab (legend_lux.png)
is skipped automatically.

Usage:
  # F7 lux map (single screenshot):
  uv run python scripts/make_j_occlusion_figure.py \
    --images data/results/figures/F7_lux_map_screenshot.png \
    --panel-titles "Location A, 2025-06-21, solar noon" --suptitle "" \
    --out data/results/figures/F7_lux_map.png

  # F9b J occlusion (three screenshots; auto timestamps + default caption):
  uv run python scripts/make_j_occlusion_figure.py \
    --img-dir data/results/figures --pattern "Location_J_*.png" \
    --out data/results/figures/F9b_J_occlusion.png
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import os

_J_SUPTITLE = ("Location J: monitored roof pixel (red marker) shadowed by "
               "neighbouring buildings on the three low-sun outlier days")


def _parse_ts(path):
    """Location_<ID>_YYYYMMDD_HH_MM(.png) -> datetime, or None if it does not match."""
    try:
        ymd, hh, mm = os.path.splitext(os.path.basename(path))[0].split("_")[-3:]
        return dt.datetime.strptime(f"{ymd}{hh}{mm}", "%Y%m%d%H%M")
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--img-dir", help="dir to glob with --pattern")
    p.add_argument("--pattern", default="Location_J_*.png")
    p.add_argument("--images", nargs="*", help="explicit image paths (overrides --img-dir)")
    p.add_argument("--out", required=True)
    p.add_argument("--cmap", default="jet", help="match the Isaac illuminance legend (jet)")
    p.add_argument("--vmax-klux", type=float, default=35.0, help="legend max (Isaac default 35000 lux)")
    p.add_argument("--panel-titles", nargs="*", default=None, help="explicit per-panel titles (image order)")
    p.add_argument("--suptitle", default=None,
                   help="figure suptitle; '' for none; defaults to the J caption for Location_J panels")
    p.add_argument("--annot", nargs="*", default=None, help="optional per-panel annotation (appended to title)")
    args = p.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    matplotlib.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm",
                                "savefig.dpi": 300, "savefig.bbox": "tight"})

    if args.images:
        imgs = list(args.images)
    elif args.img_dir:
        imgs = glob.glob(os.path.join(args.img_dir, args.pattern))
    else:
        raise SystemExit("provide --images or --img-dir")
    imgs = [f for f in imgs if "legend" not in os.path.basename(f).lower()]
    if not imgs:
        raise SystemExit("no input images found")
    imgs.sort(key=lambda f: (_parse_ts(f) or dt.datetime.min, f))

    n = len(imgs)
    fig, axes = plt.subplots(1, n, figsize=(max(6.0, 4.4 * n), 3.6))
    axes = [axes] if n == 1 else list(axes)
    for i, (ax, f) in enumerate(zip(axes, imgs)):
        ax.imshow(plt.imread(f)); ax.set_xticks([]); ax.set_yticks([])
        if args.panel_titles and i < len(args.panel_titles):
            title = args.panel_titles[i]
        else:
            ts = _parse_ts(f)
            title = ts.strftime("%d %b %Y, %H:%M") if ts else ""
        if args.annot and i < len(args.annot):
            title = (title + "\n" + args.annot[i]).strip()
        if title:
            ax.set_title(title, fontsize=11)

    fig.subplots_adjust(left=0.01, right=0.88, wspace=0.04, bottom=0.05, top=0.85)
    cax = fig.add_axes([0.905, 0.12, 0.014, 0.70])
    cb = fig.colorbar(ScalarMappable(norm=Normalize(0, args.vmax_klux), cmap=args.cmap), cax=cax)
    cb.set_label("illuminance (klux)", fontsize=11)

    if args.suptitle is not None:
        sup = args.suptitle
    elif any(os.path.basename(f).startswith("Location_J") for f in imgs):
        sup = _J_SUPTITLE
    else:
        sup = ""
    if sup:
        fig.suptitle(sup, y=0.99, fontsize=12)

    base = os.path.splitext(args.out)[0]
    for ext in (".png", ".pdf"):
        fig.savefig(base + ext)
        print(f"[wrote] {base + ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
