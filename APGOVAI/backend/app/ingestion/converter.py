"""
Direct text extraction for Telugu, English, and mixed documents.

The extractor preserves Unicode and paragraph boundaries so the chunker can
split government documents on meaningful Telugu/English sentence boundaries.
"""

from pathlib import Path
import re
import unicodedata

import fitz
import pandas as pd
import docx2txt
import pytesseract

from pdf2image import (
    convert_from_path,
)

from app.utils.language import (
    count_telugu_chars,
)

MOJIBAKE_MARKERS = (
    "à°",
    "à±",
    "â‚¹",
    "â€“",
    "â€”",
    "â€œ",
    "â€",
    "Ã",
)

TELUGU_COMBINING = "\u0c3e-\u0c4d\u0c55\u0c56"


def repair_mojibake(
    text: str,
) -> str:
    """
    Repair common UTF-8-as-Latin-1 mojibake without touching valid text.

    Example broken Telugu often appears as "à°¤à±†...". Re-decoding through
    Latin-1 restores the original Telugu code points when that is the issue.
    """
    if not text:
        return ""

    marker_score = sum(text.count(marker) for marker in MOJIBAKE_MARKERS)

    if marker_score < 3:
        return text

    try:
        repaired = text.encode(
            "latin-1",
            errors="ignore",
        ).decode(
            "utf-8",
            errors="ignore",
        )
    except UnicodeError:
        return text

    if count_telugu_chars(repaired) > count_telugu_chars(text):
        return repaired

    if sum(repaired.count(marker) for marker in MOJIBAKE_MARKERS) < marker_score:
        return repaired

    return text


def clean_text(
    text,
):
    """Normalize extracted text while preserving document structure."""
    if not text:
        return ""

    text = repair_mojibake(str(text))
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\x00", " ")
    text = text.replace("\ufeff", "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\t", " ")

    # Remove OCR spaces that split Telugu vowel signs or virama sequences.
    text = re.sub(
        rf"([\u0C00-\u0C7F])\s+([{TELUGU_COMBINING}])",
        r"\1\2",
        text,
    )
    text = re.sub(
        r"(\u0C4D)\s+([\u0C00-\u0C7F])",
        r"\1\2",
        text,
    )

    lines = []

    for line in text.split("\n"):
        normalized_line = re.sub(
            r"[ \f\v]+",
            " ",
            line,
        ).strip()
        lines.append(normalized_line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def looks_corrupted(
    text,
):
    """Detect unusable PDF text extraction that needs OCR fallback."""
    if not text:
        return True

    cleaned = clean_text(text)

    if len(cleaned) < 50:
        return True

    marker_score = sum(cleaned.count(marker) for marker in MOJIBAKE_MARKERS)
    replacement_count = cleaned.count("\ufffd")

    return marker_score > 10 or replacement_count > 10


def ocr_pdf(
    pdf_path,
):
    """OCR fallback for scanned PDFs using Telugu and English when available."""
    text = []

    images = convert_from_path(
        pdf_path,
        dpi=200,
    )

    for image in images:
        image = image.convert("L")

        try:
            extracted = pytesseract.image_to_string(
                image,
                lang="tel+eng",
                config="--psm 6",
            )
        except pytesseract.TesseractError as exc:
            print(f"[ocr] tel+eng failed, falling back to eng: {exc}")
            extracted = pytesseract.image_to_string(
                image,
                lang="eng",
                config="--psm 6",
            )

        text.append(extracted)

    return "\n".join(text)


def extract_pdf(
    path,
):
    """Extract PDF text, falling back to OCR for scanned/corrupt PDFs."""
    text = []

    doc = fitz.open(path)

    for page_number, page in enumerate(
        doc,
        start=1,
    ):
        extracted = page.get_text("text")

        if extracted:
            text.append(f"\n[PAGE {page_number}]\n{extracted}")

    text = "\n".join(text)

    if looks_corrupted(text):
        print("[extract] OCR fallback")
        text = ocr_pdf(path)

    return clean_text(text)


def extract_docx(
    path,
):
    """DOCX extraction."""
    text = docx2txt.process(path)
    return clean_text(text)


def extract_excel(
    path,
):
    """Excel extraction across all sheets."""
    sheets = pd.read_excel(
        path,
        sheet_name=None,
    )

    text = []

    for sheet_name, df in sheets.items():
        text.append(f"[SHEET {sheet_name}]")
        text.append(df.to_string(index=False))

    return clean_text("\n".join(text))


def extract_csv(
    path,
):
    """CSV extraction with UTF-8-first encoding handling."""
    last_error = None

    for encoding in (
        "utf-8-sig",
        "utf-8",
        "cp1252",
    ):
        try:
            df = pd.read_csv(
                path,
                encoding=encoding,
            )
            return clean_text(df.to_string(index=False))
        except UnicodeDecodeError as exc:
            last_error = exc

    raise last_error


def extract_txt(
    path,
):
    """Plain-text extraction with UTF-8-first encoding handling."""
    file_path = Path(path)

    for encoding in (
        "utf-8-sig",
        "utf-8",
        "cp1252",
    ):
        try:
            return clean_text(
                file_path.read_text(
                    encoding=encoding,
                )
            )
        except UnicodeDecodeError:
            continue

    return clean_text(
        file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    )


def extract_text(
    file_path,
):
    """Universal extractor."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            return extract_pdf(str(path))

        if suffix in [
            ".docx",
            ".doc",
        ]:
            return extract_docx(str(path))

        if suffix in [
            ".xlsx",
            ".xls",
        ]:
            return extract_excel(str(path))

        if suffix == ".csv":
            return extract_csv(str(path))

        if suffix in [
            ".txt",
            ".md",
            ".html",
        ]:
            return extract_txt(str(path))

        return ""

    except Exception as e:
        print(f"[extract] {path.name}: {e}")
        return ""
