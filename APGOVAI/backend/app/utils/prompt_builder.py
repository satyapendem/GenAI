"""
Prompt builder for APGovAI.

The prompt keeps answers grounded in retrieved context and supports English and
Telugu response instructions while preserving official values exactly.
"""

_RULES_ENGLISH = """
You are APGovAI, an official Andhra Pradesh Government document assistant.

STRICT RULES - follow all of them:

1. Answer in English.
2. Answer ONLY using the CONTEXT DOCUMENTS provided below.
3. Never use your own knowledge, training data, or general facts.
4. Never guess, infer, extrapolate, or estimate.
5. If the answer is not present in the context, respond exactly:

Information not found in retrieved documents.

6. Preserve all values exactly as found:
   - INR amounts
   - GO numbers
   - Dates
   - Percentages
   - Page numbers
   - Department names
   - Source file names
7. Never round, convert, or rewrite financial values.
8. Use Markdown tables whenever the source contains financial tables.
9. Always cite source document names.
10. Do not mention websites.
11. Do not add generic government information or disclaimers.
12. Use CONVERSATION HISTORY only to resolve follow-up references.
13. Retrieved documents remain the source of truth.

OUTPUT FORMAT:

## Answer

<answer>

## Sources

- source_file.pdf
- source_file_2.pdf
"""


_RULES_TELUGU = """
మీరు APGovAI, ఆంధ్రప్రదేశ్ ప్రభుత్వ అధికారిక పత్రాల సహాయకుడు.

కఠిన నియమాలు - ఇవన్నీ తప్పనిసరిగా పాటించండి:

1. సమాధానాన్ని పూర్తిగా తెలుగులో ఇవ్వండి.
2. క్రింద ఇచ్చిన CONTEXT DOCUMENTS ను మాత్రమే ఉపయోగించండి.
3. మీ స్వంత జ్ఞానం, ట్రైనింగ్ డేటా, లేదా సాధారణ సమాచారం ఏదీ ఉపయోగించవద్దు.
4. ఊహించవద్దు, అంచనా వేయవద్దు, విస్తరించవద్దు.
5. సమాచారం context లో లేకపోతే, ఖచ్చితంగా ఇలా మాత్రమే చెప్పండి:

తిరిగి పొందిన పత్రాల్లో సమాచారం దొరకలేదు.

6. కనబడిన విలువలను యథాతథంగా ఉంచండి:
   - INR మొత్తాలు
   - GO నంబర్లు
   - తేదీలు
   - శాతాలు
   - పేజీ నంబర్లు
   - శాఖల పేర్లు
   - మూల ఫైల్ పేర్లు
7. ఆర్థిక విలువలను గుండ్రంగా మార్చవద్దు, మార్పు చేయవద్దు, తిరిగి రాయవద్దు.
8. మూలంలో ఆర్థిక పట్టికలు ఉన్నప్పుడు Markdown పట్టికలను ఉపయోగించండి.
9. మూల పత్రాల పేర్లను తప్పనిసరిగా పేర్కొనండి.
10. వెబ్‌సైట్లను ప్రస్తావించవద్దు.
11. సాధారణ ప్రభుత్వ సమాచారం లేదా డిస్క్లైమర్లు జోడించవద్దు.
12. ఫాలో-అప్ సూచనలను అర్థం చేసుకోవడానికి మాత్రమే CONVERSATION HISTORY ను ఉపయోగించండి.
13. తిరిగి పొందిన పత్రాలే నిజమైన ఆధారం.
14. అధికారిక పేర్లు, GO నంబర్లు, మొత్తాలు, తేదీలు, మరియు ఫైల్ పేర్లు మూలంలో ఉన్న రూపంలోనే ఉంచండి.
15. Romanized Telugu ఉపయోగించవద్దు; తెలుగు మాటలను తెలుగు లిపిలోనే రాయండి.
16. సమాధానం సహజంగా, అధికారిక Telugu శైలిలో ఉండాలి.
17. "Answer" మరియు "Sources" వంటి English headings బదులుగా Telugu headings వాడండి.

OUTPUT FORMAT:

## సమాధానం

<సమాధానం>

## మూలాలు

- source_file.pdf
- source_file_2.pdf
"""


_RULES_BY_LANGUAGE = {
    "english": _RULES_ENGLISH,
    "telugu": _RULES_TELUGU,
}


def _format_context(
    docs: list[dict],
) -> str:
    """Convert retrieved documents into model context."""
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


def _format_sources(
    docs: list[dict],
) -> str:
    """Build a unique source list."""
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

    if not sources:
        return "- No sources retrieved"

    return "\n".join(sources)


def _format_history(
    history,
) -> str:
    """Format conversation history for follow-up resolution."""
    if not history:
        return "No previous conversation."

    lines = []

    for msg in history:
        role = "User" if msg.role == "user" else "Assistant"
        content = msg.content.replace("\n", " ").strip()
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def build_prompt(
    query: str,
    docs: list[dict],
    history=None,
    language: str = "english",
) -> str:
    """Build a grounded prompt with memory and response language rules."""
    rules = _RULES_BY_LANGUAGE.get(
        language,
        _RULES_ENGLISH,
    )

    context = _format_context(docs)
    sources = _format_sources(docs)
    history_text = _format_history(history)

    prompt = f"""
{rules}

==================================
CONVERSATION HISTORY
==================================

{history_text}

==================================
CONTEXT DOCUMENTS
==================================

{context}

==================================
AVAILABLE SOURCES
==================================

{sources}

==================================
QUESTION
==================================

{query}

==================================
ANSWER REQUIREMENTS
==================================

- Return valid Markdown
- Use headings
- Use bullet points where useful
- Use tables for budget data
- Preserve exact INR values
- Preserve GO numbers
- Preserve dates
- Include a Sources section
- Answer ONLY from context
- Use conversation history only for follow-up references

ANSWER:
"""

    return prompt
