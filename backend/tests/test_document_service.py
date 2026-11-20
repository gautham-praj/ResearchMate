import pytest
import pymupdf

from io import BytesIO

from app.services.document_service import save_uploaded_file

def create_test_pdf():

    with pymupdf.open() as document:
        document.new_page()
        return document.tobytes()
    
def test_save_uploaded_file(tmp_path):

    # Simulate an uploaded PDF
    content = create_test_pdf()
    source = BytesIO(content)

    # Save the uploaded file
    document_id, saved_path = save_uploaded_file(
        source,
        tmp_path,
        max_size_bytes=5 * 1024 * 1024
    )

    # Verify the generated ID
    assert len(document_id) == 32

    # Verify the file exists
    assert saved_path.exists()

    # Verify the saved content
    assert saved_path.read_bytes() == content

    # Verify the generated filename
    assert saved_path.name == f"{document_id}.pdf"


def test_save_uploaded_file_rejects_oversized_file(tmp_path):

    content = b"A" * 100
    source = BytesIO(content)

    with pytest.raises(ValueError, match="exceeds size limit"):
        save_uploaded_file(
            source,
            tmp_path,
            max_size_bytes=50
        )

    # No incomplete files should remain
    assert list(tmp_path.iterdir()) == []

def test_save_uploaded_file_rejects_invalid_pdf(tmp_path):

    content = b"This is not a PDF."
    source = BytesIO(content)

    with pytest.raises(ValueError, match="not a valid PDF"):
        save_uploaded_file(
            source,
            tmp_path,
            max_size_bytes=5 * 1024 * 1024
        )

    # No permanent or temporary files should remain
    assert list(tmp_path.iterdir()) == []