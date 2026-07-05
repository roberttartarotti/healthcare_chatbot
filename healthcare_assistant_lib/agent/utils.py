"""Small shared helpers for the agent layer."""


def message_text(message: object) -> str:
    """Return the plain user-facing text of a message.

    Claude messages can be a plain string or a list of content blocks (text and
    'thinking'). This returns only the text, so callers never leak block plumbing.
    """
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(part for part in parts if part).strip()
