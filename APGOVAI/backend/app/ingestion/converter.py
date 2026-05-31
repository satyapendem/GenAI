"""
Direct text extraction.

NO markdown conversion.
"""

from pathlib import Path

import fitz

import pandas as pd

import docx2txt

import pytesseract

from pdf2image import (
    convert_from_path,
)


def clean_text(
    text,
):
    """
    Cleanup extracted text.
    """

    if not text:

        return ""

    text = text.replace(
        "\x00",
        " ",
    )

    text = text.replace(
        "\t",
        " ",
    )

    #
    # Remove repeated spaces
    #

    text = " ".join(text.split())

    return text.strip()


def looks_corrupted(
    text,
):
    """
    Detect broken extraction.
    """

    if not text:

        return True

    if len(text) < 50:

        return True

    broken = [
        "ð",
        "Ÿ",
        "¥",
        "Î",
        "Ç",
        "Ł",
    ]

    score = sum(text.count(c) for c in broken)

    return score > 10


def ocr_pdf(
    pdf_path,
):
    """
    OCR fallback.
    """

    text = []

    images = convert_from_path(
        pdf_path,
        dpi=150,
    )

    for image in images:

        image = image.convert("L")

        extracted = pytesseract.image_to_string(
            image,
            lang="eng+tel",
            config="--psm 6",
        )

        text.append(extracted)

    return "\n".join(text)


def extract_pdf(
    path,
):
    """
    Extract PDF text.
    """

    text = []

    doc = fitz.open(path)

    for page in doc:

        extracted = page.get_text()

        text.append(extracted)

    text = "\n".join(text)

    #
    # OCR fallback
    #

    if looks_corrupted(text):

        print("OCR fallback")

        text = ocr_pdf(path)

    return clean_text(text)


def extract_docx(
    path,
):
    """
    DOCX extraction.
    """

    text = docx2txt.process(path)

    return clean_text(text)


def extract_excel(
    path,
):
    """
    Excel extraction.
    """

    sheets = pd.read_excel(
        path,
        sheet_name=None,
    )

    text = []

    for _, df in sheets.items():

        text.append(df.to_string())

    return clean_text("\n".join(text))


def extract_csv(
    path,
):
    """
    CSV extraction.
    """

    df = pd.read_csv(path)

    return clean_text(df.to_string())


def extract_txt(
    path,
):
    """
    TXT extraction.
    """

    return clean_text(
        Path(path).read_text(
            encoding="utf-8",
            errors="ignore",
        )
    )


def extract_text(
    file_path,
):
    """
    Universal extractor.
    """

    path = Path(file_path)

    suffix = path.suffix.lower()

    try:

        #
        # PDF
        #

        if suffix == ".pdf":

            return extract_pdf(str(path))

        #
        # DOCX
        #

        elif suffix in [
            ".docx",
            ".doc",
        ]:

            return extract_docx(str(path))

        #
        # Excel
        #

        elif suffix in [
            ".xlsx",
            ".xls",
        ]:

            return extract_excel(str(path))

        #
        # CSV
        #

        elif suffix == ".csv":

            return extract_csv(str(path))

        #
        # Text
        #

        elif suffix in [
            ".txt",
            ".md",
            ".html",
        ]:

            return extract_txt(str(path))

        return ""

    except Exception as e:

        print(e)

        return ""
