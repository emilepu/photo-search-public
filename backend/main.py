"""Start with:  uvicorn main:app --reload --port 8000   (from the backend/ folder)"""
import os
from pathlib import Path

from photosearch.api import create_app
from photosearch.model import load_text_encoder
from photosearch.store import PhotoStore

HERE = Path(__file__).parent
DATA_DIR = Path(os.environ.get("DATA_DIR", HERE / "data"))
DUPLICATE_THRESHOLD = float(os.environ.get("DUPLICATE_THRESHOLD", "0.98"))

store = PhotoStore(DATA_DIR, DUPLICATE_THRESHOLD)
app = create_app(
    store,
    load_text_encoder(store.model_name, store.pretrained),
    frontend_dir=HERE.parent / "frontend" / "dist",
)
