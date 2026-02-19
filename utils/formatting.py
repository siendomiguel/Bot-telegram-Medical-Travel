import re


def clean_for_telegram(text: str) -> str:
    """
    Clean LLM output for Telegram display.
    Strips markdown formatting and converts to clean plain text with emojis.
    """
    if not text:
        return "No response generated."

    # Remove markdown headers (## Header -> Header)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bold markers (**text** -> text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)

    # Remove italic markers (*text* -> text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    # Remove inline code (`text` -> text)
    text = re.sub(r'`(.+?)`', r'\1', text)

    # Remove code blocks (```...``` -> content)
    text = re.sub(r'```[\w]*\n?', '', text)

    # Remove markdown links [text](url) -> text (url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text)

    # Remove markdown table formatting
    text = re.sub(r'\|?\s*-{3,}\s*\|?', '', text)
    text = re.sub(r'^\|(.+)\|$', lambda m: m.group(1).replace('|', '  -  ').strip(), text, flags=re.MULTILINE)

    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Truncate very long responses
    if len(text) > 10000:
        text = text[:10000] + "\n\n... (response truncated)"

    return text.strip()


def split_text(text: str, max_length: int = 4096) -> list[str]:
    """
    Split long text into Telegram-safe chunks (max 4096 chars each).
    Tries to split at newline boundaries for clean breaks.
    """
    if not text:
        return ["No response generated."]

    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Find the best split point (prefer newline boundaries)
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1 or split_at < max_length // 2:
            # No good newline found, try space
            split_at = text.rfind(" ", 0, max_length)
        if split_at == -1:
            # No space found either, hard cut
            split_at = max_length

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    return chunks
