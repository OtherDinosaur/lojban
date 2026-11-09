from __future__ import annotations

from collections.abc import Iterable

from skamban.lexer.lexer import Lexer
from skamban.lexer.tokens import Token, TokenType
from skamban.parser.ast import (
    ASTNode,
    Assignment,
    BinaryOp,
    Conditional,
    GroupedExpr,
    ImportStatement,
    NameTerm,
    NullTerm,
    NumberTerm,
    PlaceRef,
    PredicateCall,
    PredicateDef,
    Program,
    QueryStatement,
    StringTerm,
    UnaryOp,
    VariableTerm,
)


class ParseError(Exception):
    """Erro sintático com localização no arquivo de origem."""


_PLACE_SLOTS = {
    TokenType.X1: 1,
    TokenType.X2: 2,
    TokenType.X3: 3,
    TokenType.X4: 4,
    TokenType.X5: 5,
}

_TERM_STARTS = {
    TokenType.LI,
    TokenType.LA,
    TokenType.STRING,
    TokenType.ZO_E,
    TokenType.IDENTIFIER,
}


class Parser:
    """Parser recursivo descendente para a gramática Skamban 0.1."""

    def __init__(self, tokens: Iterable[Token]):
        self.tokens = list(tokens)
        if not self.tokens or self.tokens[-1].type != TokenType.EOF:
            raise ValueError("a lista de tokens deve terminar com EOF")
        self.current = 0
        self.in_predicate_body = False

    def parse(self) -> Program:
        statements: list[ASTNode] = []
        first = self.peek()

        while not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            if self.match(TokenType.DEDENT):
                self.error("DEDENT sem bloco correspondente", self.previous())

            statement = self.parse_statement(top_level=True)
            statements.append(statement)

        return Program(
            line=first.line if first else 1,
            column=first.column if first else 1,
            statements=statements,
        )

    def parse_statement(self, *, top_level: bool = False) -> ASTNode:
        if self.match(TokenType.BRIVLA):
            if not top_level:
                self.error("declarações brivla só podem aparecer no nível superior")
            return self.parse_predicate_definition(self.previous())

        if self.match(TokenType.GANAI):
            return self.parse_conditional(self.previous())

        if self.match(TokenType.NERBEI):
            if not top_level:
                self.error("nerbei só pode aparecer no nível superior")
            return self.parse_import(self.previous())

        if self.match(TokenType.XU):
            return self.parse_boolean_query(self.previous())

        if self.match(TokenType.MA):
            return self.parse_variable_query(self.previous())

        if self.check(TokenType.INDENT):
            self.error("bloco indentado sem uma construção que o introduza")

        if self.check(TokenType.DEDENT):
            self.error("bloco terminou antes de uma sentença")

        if self._looks_like_assignment():
            return self.parse_assignment_statement()

        relation = self.parse_predicate_call()
        self.expect(TokenType.NEWLINE, "esperava quebra de linha após a chamada")
        return relation

    def parse_import(self, start: Token) -> ImportStatement:
        module = self.expect(TokenType.IDENTIFIER, "esperava o nome do módulo")
        self.expect(TokenType.NEWLINE, "esperava quebra de linha após nerbei")
        return ImportStatement(
            line=start.line,
            column=start.column,
            module_name=str(module.value),
        )

    def parse_predicate_definition(self, start: Token) -> PredicateDef:
        name = self.expect(TokenType.IDENTIFIER, "esperava o nome do predicado")
        self.expect(TokenType.NEWLINE, "esperava quebra de linha após brivla")
        self.expect(TokenType.INDENT, "esperava bloco indentado para a declaração")

        places: dict[int, str] = {}
        expected_slot = 1
        while self._looks_like_place_declaration():
            place_token = self.advance()
            label = self.advance()
            slot = _PLACE_SLOTS[place_token.type]
            if slot != expected_slot:
                self.error(
                    f"lugares devem ser declarados em ordem; esperava x{expected_slot}",
                    place_token,
                )
            places[slot] = str(label.value)
            expected_slot += 1
            self.expect(TokenType.NEWLINE, "esperava quebra após o rótulo do lugar")

        if 1 not in places:
            self.error("a declaração precisa definir x1")

        body: list[ASTNode] = []
        was_in_predicate_body = self.in_predicate_body
        self.in_predicate_body = True
        try:
            while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
                if self.match(TokenType.NEWLINE):
                    continue
                body.append(self.parse_statement())
        finally:
            self.in_predicate_body = was_in_predicate_body

        self.expect(TokenType.DEDENT, "esperava fim do bloco da declaração")
        return PredicateDef(
            line=start.line,
            column=start.column,
            name=str(name.value),
            places=places,
            body=body,
        )

    def parse_conditional(self, start: Token) -> Conditional:
        condition = self.parse_condition()
        self.expect(TokenType.GI, "esperava 'gi' após a condição")
        self.expect(TokenType.NEWLINE, "esperava quebra após o cabeçalho condicional")
        then_branch = self.parse_indented_block("ramo verdadeiro")

        else_branch = None
        if self.match(TokenType.GI_E):
            self.expect(TokenType.NEWLINE, "esperava quebra após 'gi'e'")
            else_branch = self.parse_indented_block("ramo alternativo")

        return Conditional(
            line=start.line,
            column=start.column,
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def parse_indented_block(self, description: str) -> list[ASTNode]:
        self.expect(TokenType.INDENT, f"esperava bloco indentado para {description}")
        statements: list[ASTNode] = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                continue
            statements.append(self.parse_statement())
        if not statements:
            self.error(f"{description} não pode ser vazio")
        self.expect(TokenType.DEDENT, f"esperava fim de {description}")
        return statements

    def parse_condition(self) -> ASTNode:
        if self.match(TokenType.XU):
            query_start = self.previous()
            relation = self.parse_predicate_call(stop=TokenType.GI)
            return QueryStatement(
                line=query_start.line,
                column=query_start.column,
                query_type="xu",
                relation=relation,
            )

        if self._looks_like_predicate_call():
            return self.parse_predicate_call(stop=TokenType.GI)

        return self.parse_expression()

    def parse_boolean_query(self, start: Token) -> QueryStatement:
        relation = self.parse_predicate_call()
        self.expect(TokenType.NEWLINE, "esperava quebra de linha após a consulta")
        return QueryStatement(
            line=start.line,
            column=start.column,
            query_type="xu",
            relation=relation,
        )

    def parse_variable_query(self, start: Token) -> QueryStatement:
        name = self.expect(TokenType.IDENTIFIER, "esperava o predicado após 'ma'")
        arguments = self.parse_call_arguments(stop=TokenType.NEWLINE)
        relation = PredicateCall(
            line=name.line,
            column=name.column,
            name=str(name.value),
            x1=VariableTerm(line=start.line, column=start.column, name="ma"),
            arguments=arguments,
        )
        self.expect(TokenType.NEWLINE, "esperava quebra de linha após a consulta")
        return QueryStatement(
            line=start.line,
            column=start.column,
            query_type="ma",
            relation=relation,
        )

    def parse_assignment_statement(self) -> Assignment:
        target = self.parse_assignable()
        self.expect(TokenType.DU, "esperava 'du' na atribuição")
        value = self.parse_expression()
        self.expect(TokenType.NEWLINE, "esperava quebra de linha após a atribuição")
        return Assignment(
            line=target.line,
            column=target.column,
            target=target,
            value=value,
        )

    def parse_assignable(self) -> ASTNode:
        if self.check(TokenType.LI):
            start = self.advance()
            name = self.expect(TokenType.IDENTIFIER, "esperava variável após 'li'")
            self.expect(TokenType.DOT, "esperava '.' após a variável numérica")
            return NumberTerm(
                line=start.line,
                column=start.column,
                value=str(name.value),
                is_variable=True,
            )
        if self.check(TokenType.LA):
            return self.parse_name_reference()
        if self.check(TokenType.X1, TokenType.X2, TokenType.X3, TokenType.X4, TokenType.X5):
            return self.parse_place_reference()
        if self.check(TokenType.IDENTIFIER):
            token = self.advance()
            return VariableTerm(
                line=token.line,
                column=token.column,
                name=str(token.value),
            )
        self.error("o lado esquerdo de uma atribuição precisa ser uma referência")

    def parse_predicate_call(self, stop: TokenType = TokenType.NEWLINE) -> PredicateCall:
        x1 = self.parse_term()
        name = self.expect(TokenType.IDENTIFIER, "esperava o nome do predicado após x1")
        arguments = self.parse_call_arguments(stop=stop)
        return PredicateCall(
            line=x1.line,
            column=x1.column,
            name=str(name.value),
            x1=x1,
            arguments=arguments,
        )

    def parse_call_arguments(self, *, stop: TokenType) -> list[ASTNode]:
        arguments: list[ASTNode] = []
        while not self.check(stop) and not self.check(TokenType.EOF):
            if len(arguments) == 4:
                self.error("uma chamada pode ter no máximo quatro argumentos após o predicado")
            arguments.append(self.parse_term())
        return arguments

    def parse_expression(self) -> ASTNode:
        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        operator = self._match_comparison_operator()
        if operator is None:
            return left
        right = self.parse_additive()
        if self._at_comparison_operator():
            self.error("comparações encadeadas precisam ser agrupadas com 'be ... be'o'")
        return BinaryOp(
            line=operator.line,
            column=operator.column,
            left=left,
            op=str(operator.value),
            right=right,
        )

    def parse_additive(self) -> ASTNode:
        expression = self.parse_multiplicative()
        while self.check(TokenType.SU_I, TokenType.VU_U):
            operator = self.advance()
            right = self.parse_multiplicative()
            expression = BinaryOp(
                line=operator.line,
                column=operator.column,
                left=expression,
                op=str(operator.value),
                right=right,
            )
        return expression

    def parse_multiplicative(self) -> ASTNode:
        expression = self.parse_unary()
        while self.check(TokenType.PI_I, TokenType.FE_I):
            operator = self.advance()
            right = self.parse_unary()
            expression = BinaryOp(
                line=operator.line,
                column=operator.column,
                left=expression,
                op=str(operator.value),
                right=right,
            )
        return expression

    def parse_unary(self) -> ASTNode:
        if self.match(TokenType.NA):
            operator = self.previous()
            return UnaryOp(
                line=operator.line,
                column=operator.column,
                op=str(operator.value),
                operand=self.parse_primary(),
            )
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        if self.match(TokenType.BE):
            start = self.previous()
            expression = self.parse_expression()
            self.expect(TokenType.BE_O, "esperava 'be'o' para fechar a expressão")
            return GroupedExpr(
                line=start.line,
                column=start.column,
                expression=expression,
            )
        if self.check(TokenType.X1, TokenType.X2, TokenType.X3, TokenType.X4, TokenType.X5):
            return self.parse_place_reference()
        return self.parse_term()

    def parse_term(self) -> ASTNode:
        if self.match(TokenType.LI):
            start = self.previous()
            if self.match(TokenType.NUMBER):
                token = self.previous()
                return NumberTerm(
                    line=start.line,
                    column=start.column,
                    value=token.value,
                    is_variable=False,
                )
            name = self.expect(TokenType.IDENTIFIER, "esperava número ou variável após 'li'")
            self.expect(TokenType.DOT, "esperava '.' após a variável numérica")
            return NumberTerm(
                line=start.line,
                column=start.column,
                value=str(name.value),
                is_variable=True,
            )

        if self.check(TokenType.LA):
            return self.parse_name_reference()

        if self.match(TokenType.STRING):
            token = self.previous()
            return StringTerm(
                line=token.line,
                column=token.column,
                value=str(token.value),
            )

        if self.match(TokenType.ZO_E):
            token = self.previous()
            return NullTerm(line=token.line, column=token.column)

        if self.match(TokenType.IDENTIFIER):
            token = self.previous()
            self.match(TokenType.DOT)
            return VariableTerm(
                line=token.line,
                column=token.column,
                name=str(token.value),
            )

        self.error("esperava um termo")

    def parse_name_reference(self) -> NameTerm:
        start = self.expect(TokenType.LA, "esperava 'la'")
        name = self.expect(TokenType.IDENTIFIER, "esperava um identificador após 'la'")
        self.expect(TokenType.DOT, "esperava '.' após o nome")
        return NameTerm(
            line=start.line,
            column=start.column,
            name=str(name.value),
        )

    def parse_place_reference(self) -> PlaceRef:
        token = self.advance()
        if not self.in_predicate_body:
            self.error("referências x1–x5 só podem ser usadas no corpo de um predicado", token)
        slot = _PLACE_SLOTS.get(token.type)
        if slot is None:
            self.error("esperava uma referência de lugar x1–x5", token)
        return PlaceRef(line=token.line, column=token.column, slot=slot)

    def _looks_like_assignment(self) -> bool:
        index = self.current
        token_type = self.tokens[index].type

        if token_type == TokenType.LI:
            if index + 2 >= len(self.tokens):
                return False
            return (
                self.tokens[index + 1].type == TokenType.IDENTIFIER
                and self.tokens[index + 2].type == TokenType.DOT
                and index + 3 < len(self.tokens)
                and self.tokens[index + 3].type == TokenType.DU
            )
        if token_type == TokenType.LA:
            return (
                index + 3 < len(self.tokens)
                and self.tokens[index + 1].type == TokenType.IDENTIFIER
                and self.tokens[index + 2].type == TokenType.DOT
                and self.tokens[index + 3].type == TokenType.DU
            )
        if token_type in _PLACE_SLOTS:
            return index + 1 < len(self.tokens) and self.tokens[index + 1].type == TokenType.DU
        if token_type == TokenType.IDENTIFIER:
            return index + 1 < len(self.tokens) and self.tokens[index + 1].type == TokenType.DU
        return False

    def _looks_like_place_declaration(self) -> bool:
        return (
            self.peek().type in _PLACE_SLOTS
            and self.peek(1).type == TokenType.IDENTIFIER
            and self.peek(2).type == TokenType.NEWLINE
        )

    def _looks_like_predicate_call(self) -> bool:
        if not self._can_start_term(self.peek().type):
            return False
        index = self.current
        if self.tokens[index].type in (TokenType.LI, TokenType.LA):
            if index + 1 >= len(self.tokens):
                return False
            index += 2
            if index < len(self.tokens) and self.tokens[index].type == TokenType.DOT:
                index += 1
        else:
            index += 1
            if index < len(self.tokens) and self.tokens[index].type == TokenType.DOT:
                index += 1
        return (
            index < len(self.tokens)
            and self.tokens[index].type == TokenType.IDENTIFIER
            and self.tokens[index].value != "dunli"
        )

    def _match_comparison_operator(self) -> Token | None:
        if self.check(TokenType.IDENTIFIER) and self.peek().value == "dunli":
            return self.advance()
        if self.match(TokenType.ZMADU):
            operator = self.previous()
            if self.match(TokenType.DU):
                return Token(
                    TokenType.ZMADU,
                    "zmadu du",
                    operator.line,
                    operator.column,
                )
            return operator
        if self.match(TokenType.MLECA):
            operator = self.previous()
            if self.match(TokenType.DU):
                return Token(
                    TokenType.MLECA,
                    "mleca du",
                    operator.line,
                    operator.column,
                )
            return operator
        return None

    def _at_comparison_operator(self) -> bool:
        return (
            (self.check(TokenType.IDENTIFIER) and self.peek().value == "dunli")
            or self.check(TokenType.ZMADU, TokenType.MLECA)
        )

    @staticmethod
    def _can_start_term(token_type: TokenType) -> bool:
        return token_type in _TERM_STARTS

    def expect(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        self.error(message)

    def match(self, *token_types: TokenType) -> bool:
        if self.check(*token_types):
            self.advance()
            return True
        return False

    def check(self, *token_types: TokenType) -> bool:
        if self.is_at_end():
            return TokenType.EOF in token_types
        return self.peek().type in token_types

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self, distance: int = 0) -> Token:
        index = min(self.current + distance, len(self.tokens) - 1)
        return self.tokens[index]

    def previous(self) -> Token:
        return self.tokens[max(0, self.current - 1)]

    def error(self, message: str, token: Token | None = None):
        token = token or self.peek()
        raise ParseError(
            f"{message} (linha {token.line}, coluna {token.column}; "
            f"recebi {token.type.name} {token.value!r})"
        )


def parse(source: str) -> Program:
    """Analisa uma string fonte Skamban e devolve sua AST."""
    return Parser(Lexer(source).tokenize()).parse()
