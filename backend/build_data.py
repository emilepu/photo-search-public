"""Builds the data/ folder the API reads, from a folder of photos.

For every photo it makes a small preview picture (re-saved, so camera metadata
such as GPS is dropped), computes a CLIP embedding, and writes:

    data/index.csv        one row per photo: rel (path inside the folder), folder, thumb
    data/embeddings.npy   one vector per photo, same order as index.csv
    data/config.json      which model made the vectors, and the collection name
    data/thumbs/*.jpg     the preview pictures

Example:
    python build_data.py --photos ../demo_photos --out data
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()   # lets Pillow open .heic photos
except ImportError:
    pass

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}


def find_photos(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)


def make_thumb(src: Path, dest: Path, size: int) -> None:
    img = Image.open(src)
    img.draft("RGB", (size * 2, size * 2))                 # fast downscaled decode for JPEGs
    img = ImageOps.exif_transpose(img).convert("RGB")      # bake in the rotation
    img.thumbnail((size, size))
    img.save(dest, format="JPEG", quality=80)              # saving fresh drops EXIF/GPS


def embed_images(paths: list[Path], model_name: str, pretrained: str, batch_size: int = 32) -> np.ndarray:
    import open_clip   # imported here so tests don't need torch
    import torch

    model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
    model.eval()
    chunks = []
    with torch.no_grad():
        for start in range(0, len(paths), batch_size):
            batch = [preprocess(Image.open(p).convert("RGB")) for p in paths[start:start + batch_size]]
            feats = model.encode_image(torch.stack(batch))
            feats = feats / feats.norm(dim=-1, keepdim=True)
            chunks.append(feats.numpy())
            print(f"  embedded {min(start + batch_size, len(paths))}/{len(paths)}")
    return np.concatenate(chunks).astype("float32")


def build(
    photos_dir: Path,
    out_dir: Path,
    model_name: str = "ViT-B-32",
    pretrained: str = "laion2b_s34b_b79k",
    size: int = 800,
    embed: Callable[..., np.ndarray] = embed_images,
) -> int:
    thumbs_dir = out_dir / "thumbs"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    rows, thumb_paths = [], []
    for src in find_photos(photos_dir):
        rel = src.relative_to(photos_dir).as_posix()
        name = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:16] + ".jpg"
        try:
            make_thumb(src, thumbs_dir / name, size)
        except Exception as err:   # a broken file should not stop the whole build
            print(f"  skipped {rel}: {str(err)[:80]}")
            continue
        parent = Path(rel).parent.as_posix()
        rows.append({"rel": rel, "folder": "" if parent == "." else parent, "thumb": name})
        thumb_paths.append(thumbs_dir / name)
    if not rows:
        raise SystemExit(f"No readable photos found in {photos_dir}")

    embs = embed(thumb_paths, model_name, pretrained)

    with open(out_dir / "index.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rel", "folder", "thumb"])
        writer.writeheader()
        writer.writerows(rows)
    np.save(out_dir / "embeddings.npy", embs)
    (out_dir / "config.json").write_text(
        json.dumps({"model": model_name, "pretrained": pretrained, "root_name": photos_dir.resolve().name}, indent=2),
        encoding="utf-8",
    )

    used = {r["thumb"] for r in rows}
    for p in thumbs_dir.glob("*.jpg"):   # remove previews of photos that no longer exist
        if p.name not in used:
            p.unlink()
    return len(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photos", required=True, type=Path, help="folder with the photos (subfolders are fine)")
    ap.add_argument("--out", default=Path("data"), type=Path, help="output folder (default: data)")
    ap.add_argument("--model", default="ViT-B-32")
    ap.add_argument("--pretrained", default="laion2b_s34b_b79k")
    ap.add_argument("--size", default=800, type=int, help="longest side of previews, in pixels")
    args = ap.parse_args()
    count = build(args.photos, args.out, args.model, args.pretrained, args.size)
    print(f"Done: {count} photos indexed into {args.out}")
