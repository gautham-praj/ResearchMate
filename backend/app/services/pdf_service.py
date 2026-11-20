from pathlib import Path

import pymupdf


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
