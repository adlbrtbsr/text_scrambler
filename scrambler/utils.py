import random
import re
from typing import Optional


WORD_REGEX = re.compile(r"[A-Za-z]+")


def scramble_word(word: str, rng: random.Random) -> str:
    if len(word) < 4:
        return word
    first, last = word[0], word[-1]
    interior = list(word[1:-1])
    original_interior = interior[:]

    for _ in range(5):
        rng.shuffle(interior)
        if interior != original_interior:
            break
    return first + ''.join(interior) + last


def scramble_text(text: str, rng: Optional[random.Random] = None) -> str:
    if rng is None:
        rng = random.Random()

    def _scramble_match(m: re.Match) -> str:
        return scramble_word(m.group(0), rng)

    # Tokenize by words and non-words, applying to words only via sub
    # Use a function replacement to keep non-matching segments unchanged
    parts = []
    last_end = 0
    for match in WORD_REGEX.finditer(text):
        if match.start() > last_end:
            parts.append(text[last_end:match.start()])
        parts.append(_scramble_match(match))
        last_end = match.end()
    if last_end < len(text):
        parts.append(text[last_end:])
    return ''.join(parts)


