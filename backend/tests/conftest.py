import csv
import json

import numpy as np
import pytest

from photosearch.store import PhotoStore


def unit(v):
    v = np.array(v, dtype="float32")
    return v / np.linalg.norm(v)


# photo 0 and 1 are near-copies; 2 and 3 are unrelated; 4 is half owl, half fox
VECTORS = [[1, 0, 0], [0.999, 0.0447, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]]
ROWS = [
    ("Birds/owl1.jpg", "Birds"),
    ("Birds/owl1_copy.jpg", "Birds"),
    ("Mammals/fox.jpg", "Mammals"),
    ("Plants/oak.jpg", "Plants"),
    ("mixed.jpg", ""),
]
QUERIES = {"owl": [1, 0, 0], "fox": [0, 1, 0]}


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "thumbs").mkdir()
    with open(tmp_path / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rel", "folder", "thumb"])
        for k, (rel, folder) in enumerate(ROWS):
            w.writerow([rel, folder, f"t{k}.jpg"])
    np.save(tmp_path / "embeddings.npy", np.stack([unit(v) for v in VECTORS]))
    (tmp_path / "config.json").write_text(
        json.dumps({"model": "fake", "pretrained": "fake", "root_name": "Demo"}), encoding="utf-8")
    return tmp_path


@pytest.fixture
def store(data_dir):
    return PhotoStore(data_dir, duplicate_threshold=0.98)


@pytest.fixture
def encode():
    return lambda q: unit(QUERIES[q])
