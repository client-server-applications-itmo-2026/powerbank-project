import random

ADJECTIVES = [
    "silent",
    "brave",
    "dark",
    "bright",
    "iron",
    "swift",
    "wild",
    "frozen",
    "hidden",
    "storm",
    "crimson",
    "golden",
    "shadow",
    "ember",
    "silver",
    "ancient",
    "lucky",
    "rapid",
    "mighty",
    "gentle",
]

NOUNS = [
    "fox",
    "wolf",
    "raven",
    "falcon",
    "tiger",
    "otter",
    "viper",
    "dragon",
    "storm",
    "river",
    "blade",
    "ember",
    "stone",
    "forest",
    "hawk",
    "moon",
    "comet",
    "flame",
    "thorn",
    "dust",
]

EXTRA = [
    "prime",
    "nova",
    "zero",
    "echo",
    "core",
    "pulse",
    "spark",
    "drift",
    "void",
    "fury",
    "glow",
    "crest",
    "forge",
    "strike",
    "mist",
]


class HyphenNameGenerator:
    def __init__(
        self,
        dictionaries: list[list[str]] | None = None,
        max_length: int = 100,
        separator: str = "-",
    ) -> None:
        self.dictionaries = dictionaries or [ADJECTIVES, NOUNS, EXTRA]
        self.max_length = max_length
        self.separator = separator

        if max_length <= 0:
            raise ValueError("max_length must be > 0")
        if not separator:
            raise ValueError("separator must not be empty")
        if not self.dictionaries:
            raise ValueError("dictionaries must not be empty")

    def __call__(
        self,
        min_words: int = 2,
        max_words: int = 4,
        unique_against: set[str] | None = None,
        max_attempts: int = 1000,
    ) -> str:
        return self.generate(
            min_words=min_words,
            max_words=max_words,
            unique_against=unique_against,
            max_attempts=max_attempts,
        )

    def generate(
        self,
        min_words: int = 2,
        max_words: int = 4,
        unique_against: set[str] | None = None,
        max_attempts: int = 1000,
    ) -> str:
        if min_words <= 0 or max_words <= 0:
            raise ValueError("min_words and max_words must be > 0")
        if min_words > max_words:
            raise ValueError("min_words cannot be greater than max_words")

        unique_against = unique_against or set()

        for _ in range(max_attempts):
            target_words = random.randint(min_words, max_words)
            result = self._build_name(target_words)

            if len(result.split(self.separator)) < min_words:
                continue

            if result not in unique_against:
                return result

        raise RuntimeError("Could not generate a unique name within max_attempts")

    def _build_name(self, target_words: int) -> str:
        parts: list[str] = []

        for i in range(target_words):
            dictionary = self.dictionaries[i % len(self.dictionaries)]
            word = random.choice(dictionary).strip().lower()

            if not word:
                continue

            candidate = self.separator.join(parts + [word])

            if len(candidate) > self.max_length:
                break

            parts.append(word)

        return self.separator.join(parts)
