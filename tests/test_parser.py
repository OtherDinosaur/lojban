from pathlib import Path
import unittest

from skamban.parser import (
    Assignment,
    BinaryOp,
    Conditional,
    ImportStatement,
    NameTerm,
    NullTerm,
    PredicateDef,
    PredicateCall,
    Program,
    QueryStatement,
    StringTerm,
    VariableTerm,
    UnaryOp,
    parse,
)
from skamban.parser.parser import ParseError


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_all_valid_examples_parse(self):
        for path in sorted((ROOT / "examples").glob("*.ban")):
            with self.subTest(example=path.name):
                program = parse(path.read_text(encoding="utf-8"))
                self.assertIsInstance(program, Program)

    def test_all_intentionally_invalid_examples_fail(self):
        for path in sorted((ROOT / "examples" / "invalidos").glob("*.ban")):
            with self.subTest(example=path.name):
                with self.assertRaises(ParseError):
                    parse(path.read_text(encoding="utf-8"))

    def test_precedence_and_left_associativity(self):
        program = parse("li resultado. du li pa su'i li re pi'i li ci")
        assignment = program.statements[0]
        self.assertIsInstance(assignment, Assignment)
        self.assertIsInstance(assignment.value, BinaryOp)
        self.assertEqual(assignment.value.op, "su'i")
        self.assertIsInstance(assignment.value.right, BinaryOp)
        self.assertEqual(assignment.value.right.op, "pi'i")

        left_associative = parse("li r. du li vo vu'u li re vu'u li pa")
        expression = left_associative.statements[0].value
        self.assertEqual(expression.op, "vu'u")
        self.assertIsInstance(expression.left, BinaryOp)
        self.assertEqual(expression.left.op, "vu'u")

    def test_grouped_expression(self):
        program = parse("li r. du be li pa su'i li re be'o pi'i li ci")
        expression = program.statements[0].value
        self.assertEqual(expression.op, "pi'i")
        self.assertEqual(expression.left.__class__.__name__, "GroupedExpr")

        negation = parse("resultado du na ietnu").statements[0].value
        self.assertIsInstance(negation, UnaryOp)

    def test_declaration_and_queries(self):
        predicate = parse((ROOT / "examples" / "predicado.ban").read_text(encoding="utf-8"))
        self.assertIsInstance(predicate.statements[0], PredicateDef)
        self.assertEqual(predicate.statements[0].places, {1: "jalge", 2: "pa_nota", 3: "re_nota"})

        queries = parse((ROOT / "examples" / "consultas.ban").read_text(encoding="utf-8"))
        self.assertEqual([item.query_type for item in queries.statements], ["xu", "ma"])
        self.assertTrue(all(isinstance(item, QueryStatement) for item in queries.statements))
        self.assertIsInstance(queries.statements[1].relation.x1, VariableTerm)

    def test_term_kinds_and_maximum_call_arity(self):
        program = parse((ROOT / "examples" / "termos.ban").read_text(encoding="utf-8"))
        named_call, null_call, full_call = program.statements
        self.assertIsInstance(named_call, PredicateCall)
        self.assertIsInstance(named_call.x1, NameTerm)
        self.assertIsInstance(named_call.arguments[0], StringTerm)
        self.assertIsInstance(null_call.x1, NullTerm)
        self.assertEqual(len(full_call.arguments), 4)

    def test_import_and_nested_conditional(self):
        imports = parse((ROOT / "examples" / "modulos.ban").read_text(encoding="utf-8"))
        self.assertIsInstance(imports.statements[0], ImportStatement)

        conditionals = parse((ROOT / "examples" / "condicionais.ban").read_text(encoding="utf-8"))
        outer = conditionals.statements[0]
        self.assertIsInstance(outer, Conditional)
        self.assertIsNotNone(outer.else_branch)
        self.assertIsInstance(outer.else_branch[0], Conditional)

    def test_errors_include_line_and_column(self):
        with self.assertRaisesRegex(ParseError, r"linha 1, coluna"):
            parse("li nota du li pano")

    def test_condition_can_be_an_expression(self):
        program = parse("ganai li pa zmadu li no gi\n    li r. du li pa")
        self.assertIsInstance(program.statements[0], Conditional)


if __name__ == "__main__":
    unittest.main()
