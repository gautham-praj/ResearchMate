import pymupdf
import pytest

from app.services.pdf_service import extract_text_by_page, validate_pdf


def test_extract_text_by_page(tmp_path):

    # Create a temporary PDF for testing
    pdf_path = tmp_path / "test_document.pdf"

    with pymupdf.open() as document:

        page1 = document.new_page()
        page1.insert_text((72, 72), "This is page one.")

        # Page two is intentionally blank
        document.new_page()

        page3 = document.new_page()
        page3.insert_text((72, 72), "This is page three.")

        document.save(pdf_path)

    # Test our extraction service
    pages = extract_text_by_page(pdf_path)

    assert len(pages) == 3

    assert pages[0]["page_number"] == 1
    assert "This is page one." in pages[0]["text"]

    assert pages[1]["page_number"] == 2
    assert pages[1]["text"].strip() == ""

    assert pages[2]["page_number"] == 3
    assert "This is page three." in pages[2]["text"]

def test_validate_pdf_accepts_valid_pdf(tmp_path):

    pdf_path = tmp_path / "valid.pdf"

    # Create a genuine PDF
    with pymupdf.open() as document:
        document.new_page()
        document.save(pdf_path)

    # Should not raise an exception
    validate_pdf(pdf_path)


def test_validate_pdf_rejects_non_pdf(tmp_path):

    file_path = tmp_path / "invalid.pdf"

    file_path.write_text("This is not a PDF.")

    with pytest.raises(ValueError, match="not a valid PDF"):
        validate_pdf(file_path)
