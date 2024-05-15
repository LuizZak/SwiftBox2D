import re


class BaseWordCapitalizer:
    def suggest_capitalization(
        self, string: str, has_leading_string: bool
    ) -> tuple[str, int, int] | None:
        """
        Request that this word capitalizer suggest a capitalization for a given
        input string, with a flag used to indicate if the string is the continuation
        of a split string.

        Capitalization should be responded with the earliest substring instance
        that should be capitalized, as a tuple of ('word', string[startIndex:], string[:endIndex]).

        For no capitalization suggestions on a given string, 'None' can be returned.
        """
        raise NotImplementedError()

    @classmethod
    def from_string(cls, string: str) -> "BaseWordCapitalizer":
        """
        Returns a word capitalizer based on the given input string.
        If `string` is not surrounded by slashes (e.g. `/abc/`), then this method
        returns a `WordCapitalizer`, otherwise it returns a `PatternCapitalizer`
        based on the string interpreted as a regex.
        """
        if len(string) > 2 and string.startswith("/") and string.endswith("/"):
            regex = re.compile(string[1:-1], re.IGNORECASE)
            assert (
                regex.groups == 1
            ), "Expected regex form of capitalizer to have exactly one capture group to capitalize."

            return PatternCapitalizer(regex)

        return WordCapitalizer(string)


class WordCapitalizer(BaseWordCapitalizer):
    """
    Capitalizes an occurrence of a given word as a substring of an input string.

    E.g.: To uppercase 'sse2' in 'x86_sse2' into 'x86_SSE2, initialize as `WordCapitalizer(word="SSE2")`.
    """

    word: str

    def __init__(self, word: str) -> None:
        self.word = word
        self.pattern = re.compile(f"({self.word})", flags=re.IGNORECASE)

    def suggest_capitalization(
        self, string: str, has_leading_string: bool
    ) -> tuple[str, int, int] | None:
        if match := self.pattern.search(string):
            return (
                match.group(1).upper(),
                match.start(1),
                match.end(1),
            )

        return None


class PatternCapitalizer(BaseWordCapitalizer):
    """
    Capitalizes a word in a string using a regex matcher that will capitalize the
    terms in the match pattern that are enclosed in the first capture group, e.g.:

    `PatternCapitalizer(re.compile(r"rect(i)", flags=re.IGNORECASE))` will capitalize
    the '-i' in 'recti', but not 'rect-'.
    """

    pattern: re.Pattern
    """
    A regex pattern with at least one capture group to which capitalization will be done.
    """

    ignore_if_is_leading_string: bool = False
    """
    If `True`, capitalization suggestion is skipped if `has_leading_string` is `False` in
    `self.suggest_capitalization()`, indicating that the string is the start of a string that
    was previously split by a formatter.
    """

    def __init__(
        self, pattern: str | re.Pattern, ignore_if_is_leading_string: bool = False
    ) -> None:
        self.pattern = (
            pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        )
        self.ignore_if_is_leading_string = ignore_if_is_leading_string

    def suggest_capitalization(
        self, string: str, has_leading_string: bool
    ) -> tuple[str, int, int] | None:
        leftmost_interval = None

        if self.ignore_if_is_leading_string and not has_leading_string:
            return None

        for match in self.pattern.finditer(string):
            if leftmost_interval is None or match.start() < leftmost_interval[1]:
                leftmost_interval = (
                    match.group(1).upper(),
                    match.start(1),
                    match.end(1),
                )
            else:
                break

        return leftmost_interval
