"""
Prompt builder for APGovAI.

Rules enforced in every prompt:
- Answer ONLY from retrieved context.
- Never use model knowledge.
- Never hallucinate figures, dates, GO numbers.
- Return exact INR values, dates, GO numbers from source.
- If evidence is absent → say so explicitly.
- Always include source citations.
"""

# ─────────────────────────────────────────────────────────────
# Instructions
# ─────────────────────────────────────────────────────────────

_RULES_ENGLISH = """
You are APGovAI, an official Andhra Pradesh Government document assistant.

STRICT RULES — you must follow all of them without exception:

1. Answer ONLY using the CONTEXT DOCUMENTS provided below.
2. Never use your own knowledge, training data, or general facts.
3. Never guess, infer, extrapolate, or estimate.
4. If the answer is not present in the context, respond exactly:

Information not found in retrieved documents.

5. Preserve all values exactly as found:
   - INR amounts
   - GO Numbers
   - Dates
   - Percentages
   - Page numbers
   - Department names

6. Never round financial values.
7. Never convert financial values.
8. Never modify commas in numbers.
9. Never create values that are not present.

10. When financial values exist, format them as:

   ₹3,22,359 Crore (INR 3,22,359 Crore)

   ₹15,000 Lakh (INR 15,000 Lakh)

   ₹1,25,00,000 (INR 1,25,00,000)

11. Use Markdown tables whenever the source contains financial tables.
12. Always cite source document names.
13. Do not mention websites.
14. Do not add generic government information.
15. Do not add disclaimers.

Financial Formatting Rules:

- Display all currency values in English.
- Replace:
  - "रू. कोटि" with "Crore"
  - "लाख" with "Lakh"
  - "₹" may be preserved.
- Preserve the numeric value exactly.
- Never output Hindi, Telugu, or any non-English currency labels.
- Example:

  Source:
  Total Revenue Receipts: 251,163 crore (रू. कोटि)

  Output:
  Total Revenue Receipts: ₹251,163 Crore (INR 251,163 Crore)

OUTPUT FORMAT:

## Answer

<answer>

## Sources

- source_file.pdf
- source_file_2.pdf
"""

# ─────────────────────────────────────────────────────────────
# Context Formatter
# ─────────────────────────────────────────────────────────────


def _format_context(
    docs: list[dict],
) -> str:
    """
    Convert retrieved documents into context.
    """

    if not docs:

        return "No documents retrieved."

    lines = []

    for idx, doc in enumerate(
        docs,
        start=1,
    ):

        metadata = doc.get(
            "metadata",
            {},
        )

        source = metadata.get(
            "source",
            "unknown",
        )

        score = round(
            doc.get(
                "score",
                0.0,
            ),
            3,
        )

        text = doc.get(
            "text",
            "",
        ).strip()

        go_number = metadata.get(
            "go_number",
            "",
        )

        department = metadata.get(
            "department",
            "",
        )

        year = metadata.get(
            "year",
            "",
        )

        page = metadata.get(
            "page",
            "",
        )

        document_type = metadata.get(
            "document_type",
            "",
        )

        meta_parts = []

        if document_type:

            meta_parts.append(f"type={document_type}")

        if department:

            meta_parts.append(f"department={department}")

        if go_number:

            meta_parts.append(f"go={go_number}")

        if year:

            meta_parts.append(f"year={year}")

        if page:

            meta_parts.append(f"page={page}")

        meta_string = " | ".join(meta_parts)

        lines.append(f"[DOCUMENT {idx}]")

        lines.append(f"SOURCE: {source}")

        if meta_string:

            lines.append(f"METADATA: {meta_string}")

        lines.append(f"RELEVANCE_SCORE: {score}")

        lines.append("CONTENT:")

        lines.append(text)

        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Sources Formatter
# ─────────────────────────────────────────────────────────────


def _format_sources(
    docs: list[dict],
) -> str:
    """
    Build unique source list.
    """

    seen = set()

    sources = []

    for doc in docs:

        source = doc.get(
            "metadata",
            {},
        ).get(
            "source",
            "unknown",
        )

        if source not in seen:

            seen.add(source)

            sources.append(f"- {source}")

    return "\n".join(sources)


# ─────────────────────────────────────────────────────────────
# Public Prompt Builder
# ─────────────────────────────────────────────────────────────


def build_prompt(
    query: str,
    docs: list[dict],
) -> str:
    """
    Build grounded prompt.
    """

    context = _format_context(docs)

    sources = _format_sources(docs)

    prompt = f"""
{_RULES_ENGLISH}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT DOCUMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVAILABLE SOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{sources}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{query}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANSWER REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Return valid Markdown
- Use headings
- Use bullet points
- Use tables for budget data
- Preserve exact INR values
- Show INR values in brackets
- Preserve GO Numbers
- Preserve dates
- Include Sources section
- Answer ONLY from context

ANSWER:
"""

    return prompt
