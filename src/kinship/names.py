"""Non-destructive Latin name query variants; not identity matching."""
from __future__ import annotations

import unicodedata


def _latin_search_fold(text: str) -> str:
    # Protect original Hangul, Hanja, Cyrillic and other scripts. Only Latin
    # characters have diacritics stripped for an *additional* search query.
    text = unicodedata.normalize("NFC", text)
    out = []
    for c in text:
        if c in ("đ", "Đ"):
            out.append("d" if c == "đ" else "D")
        elif "LATIN" in unicodedata.name(c, ""):
            out.extend(x for x in unicodedata.normalize("NFD", c) if unicodedata.category(x) != "Mn")
        else:
            out.append(c)
    return "".join(out)


def query_variants(original: str, supplied: list[str] | None = None) -> list[str]:
    """Preserve the exact original; output supplementary search forms only.

    This NEVER equates identities, invents Hanja, or guesses Nôm spellings.
    """
    values = [original, *(supplied or [])]
    out: list[str] = []
    for text in values:
        if not isinstance(text, str) or not text.strip():
            continue
        normalized_space = " ".join(text.split())
        for variant in (normalized_space, _latin_search_fold(normalized_space)):
            if variant and variant not in out:
                out.append(variant)
    return out
