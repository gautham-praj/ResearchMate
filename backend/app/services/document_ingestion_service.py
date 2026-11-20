from pathlib import Path

from app.services.pdf_service import extract_text_by_page
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import generate_embeddings
from app.services.vector_store_service import save_vectors

async def ingest_document(
    pdf_path: Path,
    document_id: str,
    vector_store_dir: Path
) -> dict:

    # 1. Extract text from every PDF page.
    pages = extract_text_by_page(pdf_path)

    # 2. Split extracted text into chunks.
    chunks = chunk_pages(pages)

    if not chunks:
        raise ValueError("PDF contains no extractable text.")

    # 3. Generate one embedding per chunk.
    texts = [chunk["text"] for chunk in chunks]
    vectors = await generate_embeddings(texts)

    # 4. Save vectors and metadata in a document-specific directory.
    document_store = vector_store_dir / document_id
    save_vectors(vectors, chunks, document_store)

    return {
        "page_count": len(pages),
        "chunk_count": len(chunks)
    }