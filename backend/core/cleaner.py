# backend/core/cleaner.py
import re

def clean_text(text: str) -> str:
    """
    Cleans raw extracted PDF text by removing noise
    and normalizing whitespace and characters.
    """

    # Step 1: Remove page labels we added during extraction
    # These look like "--- Page 1 ---" — useful for display
    # but noise for AI processing
    text = re.sub(r'--- Page \d+ ---', '', text)

    # Step 2: Remove page break characters
    # pdfplumber sometimes leaves \x0c (form feed / page break)
    text = text.replace('\x0c', ' ')

    # Step 3: Fix hyphenated line breaks
    # PDFs often break words across lines like "confi-\ndential"
    # We join them back into "confidential"
    text = re.sub(r'-\n', '', text)

    # Step 4: Replace multiple newlines with a single newline
    # Raw PDFs have lots of blank lines between paragraphs
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Step 5: Replace multiple spaces with a single space
    # PDFs sometimes encode spaces as ltiple characters
    text = re.sub(r' {2,}', ' ', text)

    # Step 6: Remove lines that are just numbers (page numbers)
    # These appear as standalone lines like "\n12\n"
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    # Step 7: Strip leading and trailing whitespace from the whole text
    text = text.strip()

    return text
