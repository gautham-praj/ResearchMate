
import json
from pathlib import Path

import faiss
import numpy as np


def save_vectors(
    vectors: list[list[float]],
    chunks: list[dict],
    store_dir: Path
) -> None:

    if len(vectors) != len(chunks):
        raise ValueError("Vectors and chunks must have the same length.")

    if not vectors:
        raise ValueError("Cannot save an empty vector store.")

    embeddings = np.asarray(vectors, dtype="float32")

    if embeddings.ndim != 2 or embeddings.shape[1] == 0:
        raise ValueError("Vectors must be non-empty, equally sized vectors.")

    if not np.isfinite(embeddings).all():
        raise ValueError("Vectors must contain only finite values.")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    store_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(
        index,
        str(store_dir / "index.faiss")
    )

    with (store_dir / "metadata.json").open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)


def load_vectors(store_dir: Path) -> tuple[faiss.Index, list[dict]]:

    index_path = store_dir / "index.faiss"
    metadata_path = store_dir / "metadata.json"

    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError("Vector store does not exist.")

    index = faiss.read_index(str(index_path))

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if index.ntotal != len(metadata):
        raise ValueError("FAISS index and metadata are inconsistent.")

    return index, metadata


def search_vectors(
    query_vector: list[float],
    store_dir: Path,
    top_k: int = 5
) -> list[dict]:

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    index, metadata = load_vectors(store_dir)

    if index.ntotal == 0:
        return []

    query = np.asarray([query_vector], dtype="float32")

    if query.shape[1] != index.d:
        raise ValueError("Query vector dimension does not match index.")

    if not np.isfinite(query).all():
        raise ValueError("Query vector must contain only finite values.")

    faiss.normalize_L2(query)

    k = min(top_k, index.ntotal)

    scores, indices = index.search(query, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        results.append({
            "score": float(score),
            "chunk": metadata[int(idx)]
        })

    return results
