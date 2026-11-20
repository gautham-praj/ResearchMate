import shutil

from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.services.pdf_service import validate_pdf

class UploadTooLargeError(ValueError):
    pass

def save_uploaded_file(
    source: BinaryIO,
    documents_dir: Path,
    max_size_bytes: int
) -> tuple[str, Path]:

    document_id = uuid4().hex

    documents_dir.mkdir(parents=True, exist_ok=True)

    destination = documents_dir / f"{document_id}.pdf"
    temporary_path = documents_dir / f"{document_id}.tmp"

    total_bytes = 0

    try:
        with temporary_path.open("wb") as output_file:

            while True:
                chunk = source.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > max_size_bytes:
                    raise UploadTooLargeError("Uploaded file exceeds size limit.")
                output_file.write(chunk)

        validate_pdf(temporary_path)

        temporary_path.replace(destination)

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return document_id, destination

def cleanup_document_artifacts(
    document_id: str | None,
    saved_path: Path | None,
    vector_store_dir: Path
) -> None:

    if saved_path is not None:
        saved_path.unlink(missing_ok=True)

    if document_id is not None:
        shutil.rmtree(
            vector_store_dir / document_id,
            ignore_errors=True
        )