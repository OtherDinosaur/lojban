from __future__ import annotations

import re
import sys

from .tokens import Token, TokenType


class LexerError(Exception):
    """Erro encontrado durante a análise lexical."""


KEYWORDS: dict[str, TokenType] = {
    "brivla": TokenType.BRIVLA,
    "ganai": TokenType.GANAI,
    "gi": TokenType.GI,
    "gi'e": TokenType.GI_E,
    "nerbei": TokenType.NERBEI,
    "li": TokenType.LI,
    "la": TokenType.LA,
    "lu": TokenType.LU,
    "lu'o": TokenType.LU_O,
    "zo'e": TokenType.ZO_E,
    "xu": TokenType.XU,
    "ma": TokenType.MA,
    "be": TokenType.BE,
    "be'o": TokenType.BE_O,
    "du": TokenType.DU,
    "na": TokenType.NA,
    "su'i": TokenType.SU_I,
    "vu'u": TokenType.VU_U,
    "pi'i": TokenType.PI_I,
    "fe'i": TokenType.FE_I,
    "zmadu": TokenType.ZMADU,
    "mleca": TokenType.MLECA,
    "x1": TokenType.X1,
    "x2": TokenType.X2,
    "x3": TokenType.X3,
    "x4": TokenType.X4,
    "x5": TokenType.X5,
}

ASCII_NUMBER_RE = re.compile(r"(?:\d+\.\d+|\d+)")

LOJBAN_DIGITS = {
    "no": 0,
    "pa": 1,
    "re": 2,
    "ci": 3,
    "vo": 4,
    "mu": 5,
    "xa": 6,
    "ze": 7,
    "bi": 8,
    "so": 9,
}


def parse_lojban_number(word: str) -> float | int | None:
    if not word or word == "pi":
        return None

    parts = word.split("pi")
    if len(parts) > 2:
        return None

    def parse_seq(s: str) -> list[int] | None:
        if not s:
            return []
        idx = 0
        digits = []
        while idx < len(s):
            if s.startswith("dau", idx):
                digits.append(10)
                idx += 3
            else:
                d = s[idx:idx+2]
                if d in LOJBAN_DIGITS:
                    digits.append(LOJBAN_DIGITS[d])
                    idx += 2
                else:
                    return None
        return digits

    int_digits = parse_seq(parts[0])
    if int_digits is None:
        return None

    if len(parts) == 2:
        frac_digits = parse_seq(parts[1])
        if frac_digits is None or len(frac_digits) == 0:
            return None
    else:
        frac_digits = []

    if not int_digits and not frac_digits:
        return None

    int_val = 0
    for d in int_digits:
        int_val = int_val * 10 + d

    if frac_digits:
        frac_val = 0.0
        for idx, d in enumerate(frac_digits, start=1):
            frac_val += d * (10 ** -idx)
        return int_val + frac_val
    else:
        return int_val


class Lexer:
    """Lexer inicial do Skamban 0.1."""

    def __init__(self, source: str):
        self.source = source.replace("\r\n", "\n").replace("\r", "\n")
        self.lines = self.source.split("\n")
        self.indents = [0]
        self.tokens: list[Token] = []
        self.indent_style: str | None = None

    def tokenize(self) -> list[Token]:
        for line_no, raw_line in enumerate(self.lines, start=1):
            self._tokenize_line(raw_line, line_no)

        while len(self.indents) > 1:
            self.indents.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, len(self.lines), 1))

        self.tokens.append(Token(TokenType.EOF, None, len(self.lines), 1))
        return self.tokens

    def _tokenize_line(self, raw_line: str, line_no: int) -> None:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            return

        indent_text = raw_line[: len(raw_line) - len(raw_line.lstrip(" \t"))]
        if " " in indent_text and "\t" in indent_text:
            raise LexerError(
                f"mistura de tabs e espaços na indentação "
                f"(linha {line_no}, coluna 1)"
            )

        if indent_text:
            style = "tabs" if "\t" in indent_text else "spaces"
            if self.indent_style is None:
                self.indent_style = style
            elif style != self.indent_style:
                raise LexerError(
                    f"estilo de indentação inconsistente; use apenas "
                    f"{'tabs' if self.indent_style == 'tabs' else 'espaços'} "
                    f"(linha {line_no}, coluna 1)"
                )

        indent = self._indent_width(indent_text)
        current = self.indents[-1]

        if indent > current:
            self.indents.append(indent)
            self.tokens.append(Token(TokenType.INDENT, indent, line_no, 1))
        elif indent < current:
            while len(self.indents) > 1 and indent < self.indents[-1]:
                self.indents.pop()
                self.tokens.append(Token(TokenType.DEDENT, indent, line_no, 1))
            if indent != self.indents[-1]:
                raise LexerError(
                    f"indentação não corresponde a um nível anterior "
                    f"(linha {line_no}, coluna 1)"
                )

        content = raw_line[len(indent_text):]
        self._scan_content(content, line_no, len(indent_text) + 1)
        self.tokens.append(
            Token(TokenType.NEWLINE, None, line_no, len(raw_line) + 1)
        )

    @staticmethod
    def _indent_width(indent_text: str) -> int:
        return indent_text.count("\t") * 4 if "\t" in indent_text else len(indent_text)

    def _scan_content(self, text: str, line_no: int, start_column: int) -> None:
        i = 0
        while i < len(text):
            ch = text[i]

            if ch in " \t":
                i += 1
                continue

            if ch == "#":
                return

            if ch == ".":
                self.tokens.append(Token(TokenType.DOT, ".", line_no, start_column + i))
                i += 1
                continue

            if ch == "'":
                raise LexerError(
                    f"apóstrofo inesperado (linha {line_no}, "
                    f"coluna {start_column + i})"
                )

            if text.startswith("lu", i) and (
                i + 2 == len(text) or text[i + 2].isspace()
            ):
                token, i = self._scan_string(text, i, line_no, start_column)
                self.tokens.append(token)
                continue

            if ch.isdigit():
                token, i = self._scan_ascii_number(
                    text, i, line_no, start_column
                )
                self.tokens.append(token)
                continue

            word, i = self._scan_word(text, i, line_no, start_column)
            if word == "pi":
                raise LexerError(
                    f"'pi' precisa estar entre numerais na mesma linha "
                    f"(linha {line_no}, coluna {start_column + i - len(word)})"
                )

            lojban_value = parse_lojban_number(word)
            if lojban_value is not None and "pi" not in word:
                spaced_decimal = self._scan_spaced_decimal(
                    text, i, line_no, start_column, word
                )
                if spaced_decimal is not None:
                    token, i = spaced_decimal
                    self.tokens.append(token)
                    continue

            self.tokens.append(
                self._classify_word(word, line_no, start_column + i - len(word))
            )

    def _scan_spaced_decimal(self, text, end, line_no, start_column, integer_word):
        """Combine NUMERAL pi NUMERAL into one NUMBER token."""
        pi_start = end
        while pi_start < len(text) and text[pi_start] in " \t":
            pi_start += 1
        if pi_start == end or text[pi_start:pi_start + 2] != "pi":
            return None
        pi_end = pi_start + 2
        if pi_end < len(text) and not (text[pi_end].isspace() or text[pi_end] in ".#"):
            return None

        frac_start = pi_end
        while frac_start < len(text) and text[frac_start] in " \t":
            frac_start += 1
        if frac_start == pi_end or frac_start >= len(text) or text[frac_start] in ".#":
            return None
        frac_end = frac_start
        while frac_end < len(text) and not text[frac_end].isspace() and text[frac_end] not in ".#":
            frac_end += 1
        fraction_word = text[frac_start:frac_end]

        integer_value = parse_lojban_number(integer_word)
        fraction_value = parse_lojban_number(fraction_word)
        if integer_value is None or fraction_value is None or "pi" in fraction_word:
            return None
        fraction_digits = len(fraction_word) // 2
        value = integer_value + fraction_value / (10 ** fraction_digits)
        return (
            Token(TokenType.NUMBER, value, line_no, start_column + end - len(integer_word)),
            frac_end,
        )

    def _scan_string(self, text, i, line_no, start_column):
        content_start = i + 2
        if content_start < len(text) and not text[content_start].isspace():
            return self._classify_word("lu", line_no, start_column + i), content_start

        while content_start < len(text) and text[content_start] in " \t":
            content_start += 1

        closing = text.find("lu'o", content_start)
        if closing == -1:
            raise LexerError(
                f"string sem fechamento lu'o "
                f"(linha {line_no}, coluna {start_column + i})"
            )

        content = text[content_start:closing].rstrip(" \t")
        return (
            Token(TokenType.STRING, content, line_no, start_column + i),
            closing + 4,
        )

    def _scan_ascii_number(self, text, i, line_no, start_column):
        match = ASCII_NUMBER_RE.match(text, i)
        raw = match.group(0)

        end = i + len(raw)
        if end < len(text) and (text[end].isalpha() or text[end] == "_"):
            raise LexerError(
                f"número colado a identificador: {raw!r} "
                f"(linha {line_no}, coluna {start_column + i})"
            )

        value = float(raw) if "." in raw else int(raw)
        return Token(TokenType.NUMBER, value, line_no, start_column + i), end

    def _scan_word(self, text, i, line_no, start_column):
        j = i
        while j < len(text) and not text[j].isspace() and text[j] not in ".#":
            j += 1

        word = text[i:j]
        if "'" in word and word not in KEYWORDS:
            raise LexerError(
                f"apóstrofo inválido em {word!r} "
                f"(linha {line_no}, coluna {start_column + i})"
            )
        return word, j

    @staticmethod
    def _classify_word(word, line, column):
        if word in KEYWORDS:
            return Token(KEYWORDS[word], word, line, column)

        lojban_val = parse_lojban_number(word)
        if lojban_val is not None:
            return Token(TokenType.NUMBER, lojban_val, line, column)

        return Token(TokenType.IDENTIFIER, word, line, column)


def lex(source: str) -> list[Token]:
    return Lexer(source).tokenize()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: python -m skamban.lexer.lexer <arquivo.ban>")
        return 2

    with open(argv[1], "r", encoding="utf-8") as f:
        source = f.read()

    try:
        for token in lex(source):
            print(token)
    except LexerError as exc:
        print(f"LexerError: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
