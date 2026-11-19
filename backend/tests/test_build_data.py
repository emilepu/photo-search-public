import csv

import numpy as np
from PIL import Image

from build_data import build


def fake_embed(paths, model_name, pretrained):
    rng = np.random.default_rng(0)
    v = rng.normal(size=(len(paths), 8)).astype("float32")
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def test_build_makes_thumbs_index_and_embeddings(tmp_path):
    photos = tmp_path / "My Photos"
    (photos / "Birds").mkdir(parents=True)
    Image.new("RGB", (1600, 1200), "green").save(photos / "Birds" / "owl.jpg")
    Image.new("RGB", (300, 900), "brown").save(photos / "top.png")
    (photos / "broken.jpg").write_text("not an image")

    out = tmp_path / "data"
    count = build(photos, out, size=400, embed=fake_embed)

    assert count == 2
    rows = list(csv.DictReader(open(out / "index.csv", encoding="utf-8")))
    assert sorted(r["rel"] for r in rows) == ["Birds/owl.jpg", "top.png"]
    assert {r["folder"] for r in rows} == {"Birds", ""}
    assert np.load(out / "embeddings.npy").shape == (2, 8)
    for r in rows:
        with Image.open(out / "thumbs" / r["thumb"]) as im:
            assert max(im.size) <= 400
    assert '"root_name": "My Photos"' in (out / "config.json").read_text(encoding="utf-8")
