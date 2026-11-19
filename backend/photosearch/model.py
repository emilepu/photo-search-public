"""Turns a search phrase into a vector with OpenCLIP (text half of the model only)."""
from __future__ import annotations

from typing import Callable

import numpy as np


def load_text_encoder(model_name: str, pretrained: str) -> Callable[[str], np.ndarray]:
    import open_clip  # imported here so tests and tooling don't need torch
    import torch

    model, _, _ = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
    model.eval()
    del model.visual  # we only encode text here, the image half is not needed
    tokenizer = open_clip.get_tokenizer(model_name)

    def encode(query: str) -> np.ndarray:
        with torch.no_grad():
            t = model.encode_text(tokenizer([query]))
            t = t / t.norm(dim=-1, keepdim=True)
        return t[0].numpy().astype("float32")

    return encode
