from dataclasses import dataclass, field
from typing import Optional, List, Union


@dataclass
class ASTNode:
    """Nó base para todos os elementos da Árvore Sintática Abstrata (AST)."""
    line: int = 0
    column: int = 0


# ==============================================================================
# Termos / Argumentos (Sumti)
# ==============================================================================

@dataclass
class NumberTerm(ASTNode):
    """
    Termo numérico introduzido por 'li'.
    Pode ser um valor numérico literal (ex: 'li 10', 'li 3.14') ou 
    uma referência a uma variável numérica (ex: 'li nota1.').
    """
    value: Union[int, float, str] = 0
    is_variable: bool = False


@dataclass
class NameTerm(ASTNode):
    """
    Termo nominal/não-numérico introduzido por 'la' (ex: 'la djan.').
    """
    name: str = ""


@dataclass
class StringTerm(ASTNode):
    """
    Termo literal de texto delimitado por 'lu ... lu'o'.
    """
    value: str = ""


@dataclass
class NullTerm(ASTNode):
    """
    Termo 'zo'e' representando valor nulo, irrelevante ou não especificado.
    """
    pass


@dataclass
class PlaceRef(ASTNode):
    """
    Referência direta a um slot posicional (x1, x2, x3, x4, x5)
    dentro da definição de um predicado.
    """
    slot: int = 1  # 1 a 5


@dataclass
class VariableTerm(ASTNode):
    """
    Termo de incógnita ou variável genérica (ex: 'ma' em consultas ou identificador puro).
    """
    name: str = ""


@dataclass
class GroupedExpr(ASTNode):
    """
    Expressão agrupada delimitada por 'be ... be'o'.
    """
    expression: ASTNode = field(default_factory=ASTNode)


# ==============================================================================
# Expressões e Operações
# ==============================================================================

@dataclass
class BinaryOp(ASTNode):
    """
    Operação binária (aritmética, lógica ou comparação).
    Operadores suportados:
      - su'i (+)
      - vu'u (-)
      - pi'i (*)
      - fe'i (/)
      - dunli (==)
      - zmadu (>)
      - mleca (<)
      - zmadu du (>=)
      - mleca du (<=)
    """
    left: ASTNode = field(default_factory=ASTNode)
    op: str = ""
    right: ASTNode = field(default_factory=ASTNode)


@dataclass
class UnaryOp(ASTNode):
    """
    Operação unária (ex: negação com 'na').
    """
    op: str = ""
    operand: ASTNode = field(default_factory=ASTNode)


# ==============================================================================
# Declarações, Relações e Consultas
# ==============================================================================

@dataclass
class PredicateCall(ASTNode):
    """
    Relação ou invocação de predicado no formato Lojban:
    x1 <nome_do_predicado> x2 x3 ... x5
    Exemplos:
      - 'li media. cmadi li nota1. li nota2.'
      - 'la djan. patfu la mark.'
    """
    name: str = ""
    x1: ASTNode = field(default_factory=ASTNode)
    arguments: List[ASTNode] = field(default_factory=list)  # x2, x3, x4, x5


@dataclass
class PredicateDef(ASTNode):
    """
    Declaração de predicado de usuário com a palavra reservada 'brivla'.
    Exemplo:
      brivla cmadi
          x1 jalge
          x2 pa_nota
          x3 re_nota

          x1 du be x2 su'i x3 be'o fe'i li re
    """
    name: str = ""
    places: dict[int, str] = field(default_factory=dict)  # Ex: {1: "jalge", 2: "pa_nota", 3: "re_nota"}
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class QueryStatement(ASTNode):
    """
    Consulta declarativa iniciada por 'xu' (booleana) ou contendo 'ma' (incógnita).
    Exemplos:
      - 'xu la djan. patfu la mark.' (Retorna ietnu/iitfa)
      - 'ma patfu la mark.' (Busca unificação para ma)
    """
    query_type: str = "xu"  # 'xu' ou 'ma'
    relation: ASTNode = field(default_factory=ASTNode)


@dataclass
class Conditional(ASTNode):
    """
    Estrutura condicional declarativa:
    ganai <condição> gi <ramo_verdadeiro> [gi'e <ramo_alternativo>]
    """
    condition: ASTNode = field(default_factory=ASTNode)
    then_branch: List[ASTNode] = field(default_factory=list)
    else_branch: Optional[List[ASTNode]] = None


@dataclass
class ImportStatement(ASTNode):
    """
    Importação de módulo introduzida por 'nerbei <modulo>'.
    """
    module_name: str = ""


# ==============================================================================
# Raiz do Programa
# ==============================================================================

@dataclass
class Program(ASTNode):
    """
    Nó raiz que contém a lista de sentenças/declarações do programa.
    """
    statements: List[ASTNode] = field(default_factory=list)
