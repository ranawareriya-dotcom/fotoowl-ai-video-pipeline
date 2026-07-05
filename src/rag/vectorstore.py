"""
Local Chroma vector store with TWO SEPARATE COLLECTIONS, not one shared
collection with a type filter. Style guides and code snippets have
different embedding geometry (prose semantics vs. API/code semantics) -
mixing them in one collection with metadata filtering means the
embedding model still has to compete against irrelevant vectors during
the ANN search itself. Separate collections = separate, cleaner spaces.
"""
from __future__ import annotations
import chromadb
from chromadb.utils import embedding_functions

from src.rag.seed_data.style_guides import STYLE_GUIDE_DOCS
from src.rag.seed_data.remotion_snippets import REMOTION_SNIPPETS

_DB_PATH = ".chroma_db"

_embedder = embedding_functions.DefaultEmbeddingFunction()  # local, no API key needed


def get_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=_DB_PATH)


def seed_collections(client: chromadb.ClientAPI | None = None) -> None:
    client = client or get_client()

    style_col = client.get_or_create_collection("style_guides", embedding_function=_embedder)
    if style_col.count() == 0:
        style_col.add(
            ids=[d["id"] for d in STYLE_GUIDE_DOCS],
            documents=[d["text"] for d in STYLE_GUIDE_DOCS],
            metadatas=[{"style": d["style"], "facet": d["facet"]} for d in STYLE_GUIDE_DOCS],
        )

    snippet_col = client.get_or_create_collection("remotion_snippets", embedding_function=_embedder)
    if snippet_col.count() == 0:
        snippet_col.add(
            ids=[d["id"] for d in REMOTION_SNIPPETS],
            documents=[d["text"] for d in REMOTION_SNIPPETS],
            metadatas=[{"topic": d["topic"], "error_types": ",".join(d["error_types"])}
                       for d in REMOTION_SNIPPETS],
        )
