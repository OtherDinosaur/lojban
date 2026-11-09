import unittest

from skamban.lexer.lexer import Lexer, LexerError
from skamban.lexer.tokens import TokenType


class LexerTests(unittest.TestCase):
    def types(self, source):
        return [token.type for token in Lexer(source).tokenize()]

    def test_reserved_words(self):
        source = "brivla ganai gi gi'e nerbei li la xu ma be be'o du na"
        result = self.types(source)
        self.assertEqual(
            result[:-2],
            [
                TokenType.BRIVLA,
                TokenType.GANAI,
                TokenType.GI,
                TokenType.GI_E,
                TokenType.NERBEI,
                TokenType.LI,
                TokenType.LA,
                TokenType.XU,
                TokenType.MA,
                TokenType.BE,
                TokenType.BE_O,
                TokenType.DU,
                TokenType.NA,
            ],
        )

    def test_identifier_is_not_classified_as_brivla(self):
        tokens = Lexer("cmadi").tokenize()
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "cmadi")

    def test_numbers(self):
        tokens = Lexer("li 10\nli pano\nli 3.14").tokenize()
        self.assertEqual(tokens[1].value, 10)
        self.assertEqual(tokens[4].value, 10)
        self.assertEqual(tokens[7].value, 3.14)

    def test_dot_is_not_statement_terminator(self):
        tokens = Lexer("li nota. du li pano").tokenize()
        self.assertEqual(
            [t.type for t in tokens],
            [
                TokenType.LI, TokenType.IDENTIFIER, TokenType.DOT,
                TokenType.DU, TokenType.LI, TokenType.NUMBER,
                TokenType.NEWLINE, TokenType.EOF,
            ],
        )

    def test_string(self):
        tokens = Lexer("zo'e cusku lu coi rodo lu'o").tokenize()
        self.assertEqual(tokens[0].type, TokenType.ZO_E)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].type, TokenType.STRING)
        self.assertEqual(tokens[2].value, "coi rodo")

    def test_indentation(self):
        source = "brivla cmadi\n    x1 jalge\n    x2 nota\nbrivla outro"
        types = self.types(source)
        self.assertIn(TokenType.INDENT, types)
        self.assertIn(TokenType.DEDENT, types)

    def test_nested_indentation(self):
        source = "ganai\n    cond\ngi\n    ganai\n        outra\n    gi\n        acao"
        types = self.types(source)
        self.assertEqual(types.count(TokenType.INDENT), 4)
        self.assertEqual(types.count(TokenType.DEDENT), 4)

    def test_invalid_apostrophe(self):
        with self.assertRaises(LexerError):
            Lexer("foo'").tokenize()

    def test_mixed_indentation(self):
        with self.assertRaises(LexerError):
            Lexer("brivla x\n    x1 y\n\tx2 z").tokenize()

    def test_inconsistent_dedent(self):
        with self.assertRaises(LexerError):
            Lexer("brivla x\n    x1 y\n  x2 z").tokenize()

    def test_lojban_digits_separated_by_space(self):
        tokens = Lexer("li ci pi pa").tokenize()
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].value, 3.1)
        self.assertEqual(
            [token.type for token in tokens[2:]],
            [TokenType.NEWLINE, TokenType.EOF],
        )

    def test_isolated_pi_raises_error(self):
        with self.assertRaises(LexerError):
            Lexer("pi").tokenize()
        with self.assertRaises(LexerError):
            Lexer("ci pi").tokenize()
        with self.assertRaises(LexerError):
            Lexer("pi pa").tokenize()


if __name__ == "__main__":
    unittest.main()
