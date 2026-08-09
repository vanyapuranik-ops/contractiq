import pdfplumber
from typing import Optional

def extract_text_from_pdf(file) -> Optional[str]:
    extracted_pages = []
    try:
        with pdfplumber.open(file) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(f"--- Page {page_number} ---\n{page_text}")
                else:
                    extracted_pages.append(f"--- Page {page_number} --- [No extractable text]")
    except Exception as e:
        print(f"[pdf_extractor] ERROR: {e}")
        return None
    return "\n\n".join(extracted_pages)

def get_page_count(file) -> int:
    try:
        with pdfplumber.open(file) as pdf:
            return len(pdf.pages)
    except Exception as e:
        print(f"[pdf_extractor] ERROR: {e}")
        return 0
