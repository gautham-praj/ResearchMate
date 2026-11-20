import httpx

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.services.document_service import (
    save_uploaded_file,
    UploadTooLargeError,
    cleanup_document_artifacts
)
from app.services.pdf_service import InvalidPDFError
from app.services.document_ingestion_service import ingest_document

router = APIRouter()

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    document_id = None
    saved_path = None

    try:
        document_id, saved_path = save_uploaded_file(
            file.file,
            settings.documents_dir,
            settings.max_upload_size_bytes
        )

        ingestion_result = await ingest_document(
            saved_path,
            document_id,
            settings.vector_store_dir
        )

    except Exception as error:

        cleanup_document_artifacts(
            document_id,
            saved_path,
            settings.vector_store_dir
        )

        if isinstance(error, InvalidPDFError):
            raise HTTPException(status_code=400, detail=str(error))

        if isinstance(error, UploadTooLargeError):
            raise HTTPException(status_code=413, detail=str(error))

        if isinstance(error, ValueError):
            raise HTTPException(status_code=422, detail=str(error))

        if isinstance(error, httpx.ConnectError):
            raise HTTPException(
                status_code=503,
                detail="Could not connect to Ollama. Is Ollama running?"
            )

        if isinstance(error, httpx.TimeoutException):
            raise HTTPException(
                status_code=504,
                detail="Ollama took too long to respond."
            )

        if isinstance(error, httpx.HTTPStatusError):
            raise HTTPException(
                status_code=502,
                detail="Ollama returned an error."
            )

        raise

    finally:
        await file.close()

    return {
        "document_id": document_id,
        "filename": file.filename,
        "page_count": ingestion_result["page_count"],
        "chunk_count": ingestion_result["chunk_count"]
    }