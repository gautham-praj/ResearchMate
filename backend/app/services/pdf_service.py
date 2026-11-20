from pathlib import Path

import pymupdf

class InvalidPDFError(ValueError):
    pass

def extract_text_by_page(pdf_path: str | Path) -> list[dict]:

    extracted_pages = []

    with pymupdf.open(pdf_path) as document:

        for page_number, page in enumerate(document, start=1):

            text = page.get_text()

            extracted_pages.append({
                "page_number": page_number,
                "text": text
            })

    return extracted_pages

def validate_pdf(pdf_path: str | Path) -> None:

    with open(pdf_path, "rb") as file:
        signature = file.read(5)

    if signature != b"%PDF-":
        raise InvalidPDFError("File is not a valid PDF.")

    try:
        with pymupdf.open(pdf_path) as document:

            if document.is_encrypted:
                raise InvalidPDFError("Encrypted PDFs are not supported.")

    except pymupdf.FileDataError as error:
        raise InvalidPDFError("File is not a readable PDF.") from error
