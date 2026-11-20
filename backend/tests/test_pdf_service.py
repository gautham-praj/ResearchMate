import pymupdf

from app.services.pdf_service import extract_text_by_page


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
