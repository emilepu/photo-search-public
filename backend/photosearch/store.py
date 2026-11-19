"""Loads the search index and does the maths: ranking and duplicate grouping.

No web code and no model code in here, so it is easy to test.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def duplicate_groups(embs: np.ndarray, threshold: float, block: int = 1024) -> np.ndarray:
    """Return one group id per photo. Photos whose embeddings have a cosine
    similarity >= threshold end up in the same group (they are copies or
    near-copies of the same picture). Works in blocks so memory stays small."""
    n = len(embs)
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for start in range(0, n, block):
        sims = embs[start:start + block] @ embs.T
        rows, cols = np.nonzero(sims >= threshold)
        for r, c in zip(rows, cols):
            a, b = start + int(r), int(c)
            if b > a:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra
    return np.array([find(i) for i in range(n)])


def first_of_each_group(order, groups) -> list[int]:
    """Keep only the best-ranked photo of every duplicate group."""
    seen: set[int] = set()
    kept: list[int] = []
    for i in order:
        g = int(groups[i])
        if g not in seen:
            seen.add(g)
            kept.append(int(i))
    return kept


class PhotoStore:
    """Everything the API needs to know about the indexed photos."""

    def __init__(self, data_dir: str | Path, duplicate_threshold: float = 0.98):
        self.data_dir = Path(data_dir)
        config = json.loads((self.data_dir / "config.json").read_text(encoding="utf-8"))
        self.model_name: str = config["model"]
        self.pretrained: str = config["pretrained"]
        self.root_name: str = config["root_name"]

        with open(self.data_dir / "index.csv", newline="", encoding="utf-8") as f:
            self.rows: list[dict[str, str]] = list(csv.DictReader(f))
        self.embs = np.load(self.data_dir / "embeddings.npy").astype("float32")
        if len(self.rows) != len(self.embs):
            raise ValueError("index.csv and embeddings.npy have different lengths")

        self.groups = duplicate_groups(self.embs, duplicate_threshold)
        self.members: dict[int, list[int]] = defaultdict(list)
        for i, g in enumerate(self.groups):
            self.members[int(g)].append(i)

    def __len__(self) -> int:
        return len(self.rows)

    def full_path(self, i: int) -> str:
        return f"{self.root_name}/{self.rows[i]['rel']}"

    def copies_of(self, i: int) -> list[int]:
        return [j for j in self.members[int(self.groups[i])] if j != i]

    def rank(self, text_vec: np.ndarray) -> np.ndarray:
        """All photo numbers, best match first."""
        scores = self.embs @ text_vec
        return np.argsort(scores)[::-1]
