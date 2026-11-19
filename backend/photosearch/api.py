"""The web API. `create_app` takes the store and a text encoder as arguments,
so tests can plug in a fake encoder instead of loading a real model."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .store import PhotoStore, first_of_each_group

EncodeText = Callable[[str], np.ndarray]


class PhotoOut(BaseModel):
    id: int
    thumb_url: str
    folder: str             # caption: folder inside the collection ("" = main folder)
    path: str               # full path including the collection name and file name
    copies: int             # how many other copies of this picture exist
    also_found: list[str]   # full paths of those copies


class SearchOut(BaseModel):
    total: int              # number of photos that can be shown, best match first
    results: list[PhotoOut]


class InfoOut(BaseModel):
    count: int
    root_name: str


def create_app(store: PhotoStore, encode_text: EncodeText, frontend_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="Forest photo search")

    @lru_cache(maxsize=64)
    def ranked(query: str, hide_duplicates: bool) -> tuple[int, ...]:
        order = store.rank(encode_text(query))
        ids = first_of_each_group(order, store.groups) if hide_duplicates else [int(i) for i in order]
        return tuple(ids)

    def to_out(i: int) -> PhotoOut:
        others = store.copies_of(i)
        return PhotoOut(
            id=i,
            thumb_url=f"/thumbs/{store.rows[i]['thumb']}",
            folder=store.rows[i]["folder"],
            path=store.full_path(i),
            copies=len(others),
            also_found=[store.full_path(j) for j in others],
        )

    @app.get("/api/info", response_model=InfoOut)
    def info() -> InfoOut:
        return InfoOut(count=len(store), root_name=store.root_name)

    @app.get("/api/search", response_model=SearchOut)
    def search(
        q: str = Query(..., max_length=200),
        hide_duplicates: bool = True,
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
    ) -> SearchOut:
        q = q.strip()
        if not q:
            raise HTTPException(status_code=422, detail="Query must not be empty")
        ids = ranked(q, hide_duplicates)
        return SearchOut(total=len(ids), results=[to_out(i) for i in ids[offset:offset + limit]])

    app.mount("/thumbs", StaticFiles(directory=store.data_dir / "thumbs"), name="thumbs")
    if frontend_dir is not None and frontend_dir.is_dir():   # serve the built React app too
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    return app
