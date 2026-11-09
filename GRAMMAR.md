# Gramática Skamban 0.1

Este documento define a sintaxe de referência da versão 0.1. O lexer e o
parser devem seguir estas regras; a análise semântica valida nomes, tipos,
aridade e definições de predicados depois da análise sintática.

As regras abaixo descrevem os tokens emitidos pelo lexer. `IDENTIFIER("dunli")`
significa um token `IDENTIFIER` cujo texto é `dunli`; `NUMBER(v)` representa
um token numérico com valor `v`.

## Convenções léxicas relevantes

- Espaços separam tokens. Cada linha significativa produz `NEWLINE`.
- Linhas vazias e linhas de comentário não produzem tokens.
- A indentação gera `INDENT` e `DEDENT`. Um arquivo usa espaços ou tabs, sem
  misturar os dois estilos; cada tab vale quatro colunas.
- `#` inicia um comentário até o fim da linha.
- `.` é um token `DOT` que fecha referências escritas com identificador. Não
  termina uma sentença.
- `lu texto lu'o` é emitido pelo lexer como um único token `STRING(texto)`.
  Strings são de uma linha; `lu'o` encerra no primeiro delimitador e não há
  mecanismo de escape na versão 0.1.
- `pi` só ocorre dentro de um numeral decimal Lojban e não é emitido
  separadamente.
- Palavras reservadas são sensíveis a maiúsculas e minúsculas e devem ser
  escritas na forma minúscula mostrada neste documento.
- Palavras Lojban que não sejam palavras reservadas, incluindo nomes de
  predicados, são emitidas como `IDENTIFIER`.

## Gramática em EBNF

`NEWLINE`, `INDENT`, `DEDENT` e `EOF` são tokens estruturais. `{ X }` significa
zero ou mais repetições, `[ X ]` significa opcional e `|` indica alternativa.

```ebnf
program             = { (simple_statement, NEWLINE)
                      | predicate_definition
                      | conditional }, EOF ;

simple_statement    = import_statement | query | assignment | predicate_call ;

import_statement    = NERBEI, IDENTIFIER ;

predicate_definition
                    = BRIVLA, IDENTIFIER, NEWLINE,
                      INDENT, place_declaration, NEWLINE,
                      { place_declaration, NEWLINE },
                      { block_item },
                      DEDENT ;

place_declaration   = place, IDENTIFIER ;
place               = X1 | X2 | X3 | X4 | X5 ;

block_statement     = query | assignment | predicate_call ;
block_item          = (block_statement, NEWLINE) | conditional ;

conditional         = GANAI, condition, GI, NEWLINE,
                      block, [ GI_E, NEWLINE, block ] ;

block               = INDENT, block_item, { block_item }, DEDENT ;

condition           = query | predicate_call | expression ;

query               = XU, predicate_call
                    | MA, IDENTIFIER, [ term ], [ term ], [ term ], [ term ] ;

predicate_call      = term, IDENTIFIER, [ term ], [ term ], [ term ], [ term ] ;

assignment          = assignable, DU, expression ;
assignable          = numeric_reference | name_reference
                    | place_reference | IDENTIFIER ;

expression          = comparison ;
comparison          = additive, [ comparison_operator, additive ] ;
comparison_operator = IDENTIFIER("dunli")
                    | ZMADU, [ DU ]
                    | MLECA, [ DU ] ;

additive            = multiplicative, { (SU_I | VU_U), multiplicative } ;
multiplicative      = unary, { (PI_I | FE_I), unary } ;
unary               = [ NA ], primary ;

primary             = term
                    | place_reference
                    | BE, expression, BE_O ;

term                = numeric_literal
                    | numeric_reference
                    | name_reference
                    | STRING
                    | ZO_E
                    | IDENTIFIER, [ DOT ] ;

numeric_literal    = LI, NUMBER ;
numeric_reference  = LI, IDENTIFIER, DOT ;
name_reference     = LA, IDENTIFIER, DOT ;
place_reference    = place ;
```

Na consulta iniciada por `ma`, o parser interpreta `ma` como o valor
desconhecido no primeiro lugar da relação. Assim, `ma patfu la mark.` equivale
sintaticamente a uma chamada de `patfu` cujo x1 é uma incógnita.

As formas reconhecidas como `NUMBER` são inteiros e decimais em algarismos,
sequências de dígitos Lojban de 0 a 9 concatenados (por exemplo, `pano`) e
sequências Lojban com `pi` entre as partes inteira e fracionária (por exemplo,
`ci pi pa` ou `cipipa`). O sinal de menos não faz parte do literal; a versão
0.1 não define números negativos como forma lexical.

## Regras de estrutura

## AST produzida pelo parser

- O programa contém suas declarações e sentenças em `Program.statements`.
- Uma atribuição `du` produz `Assignment(target, value)`.
- Uma chamada produz `PredicateCall`; o primeiro termo é `x1` e os termos
  seguintes ficam em `arguments`.
- Uma declaração produz `PredicateDef`. Seus rótulos ficam em `places` e as
  sentenças executáveis ficam em `body`.
- Consultas produzem `QueryStatement`. Na forma com `ma`, o x1 da relação é
  uma `VariableTerm` chamada `ma`.
- Operações produzem `UnaryOp` ou `BinaryOp`; grupos explícitos produzem
  `GroupedExpr`.
- Condicionais produzem `Conditional`, e importações produzem
  `ImportStatement`.

### Sentenças e chamadas

Uma quebra de linha significativa encerra uma sentença. Espaços não encerram
sentenças, e o ponto após uma referência apenas fecha o identificador daquela
referência. Uma chamada contém o valor de x1 antes do nome do predicado e de
zero a quatro argumentos depois dele:

```text
li media. cmadi li nota1. li nota2.
la djan. patfu la mark.
```

O limite de quatro argumentos depois do nome mantém o máximo de cinco lugares
da especificação. A existência e a aridade real do predicado são verificadas
semanticamente.

### Declarações de predicados

Uma declaração começa com `brivla` e tem um bloco indentado. As declarações
de lugar vêm antes das regras do bloco, começam obrigatoriamente em x1 e não
podem saltar ou repetir lugares. O identificador após cada lugar é um rótulo
documental; o corpo referencia os lugares por `x1`–`x5`. Referências `x1`–`x5`
só são válidas dentro do corpo de uma declaração `brivla`.

```text
brivla cmadi
    x1 jalge
    x2 pa_nota
    x3 re_nota
    x1 du be x2 su'i x3 be'o fe'i li re
```

Linhas vazias não separam a seção de lugares do corpo, pois são ignoradas pelo
lexer. A distinção é sintática: `xN IDENTIFIER` declara um rótulo; `xN du ...`
é uma atribuição no corpo.

### Expressões

Os operadores são avaliados nesta ordem, da maior para a menor precedência:

1. Agrupamento `be ... be'o` e referências/termos.
2. Negação prefixa `na`.
3. Multiplicação `pi'i` e divisão `fe'i`.
4. Adição `su'i` e subtração `vu'u`.
5. Comparações `dunli`, `zmadu`, `mleca`, `zmadu du` e `mleca du`.
6. Atribuição `du`, que só aparece como sentença e não como operador dentro
   de uma expressão.

Operadores aritméticos do mesmo nível associam à esquerda. Uma comparação por
expressão é permitida; comparações encadeadas devem ser agrupadas
explicitamente. `zmadu du` significa maior ou igual e `mleca du` significa
menor ou igual. `dunli` é um identificador comum lexicalmente e funciona como
igualdade quando aparece na posição de operador.

### Consultas

- `xu` inicia uma consulta booleana sobre uma chamada de predicado.
- `ma` inicia uma consulta que procura valores para o x1 desconhecido.
- Resultados booleanos são `ietnu` e `iitfa`; sua produção e uso são regras
  semânticas/runtime, não uma forma sintática especial nesta versão.

```text
xu la djan. patfu la mark.
ma patfu la mark.
```

### Condicionais

`ganai` introduz a condição e `gi` inicia o bloco verdadeiro na mesma linha.
Opcionalmente, `gi'e` inicia o bloco alternativo no nível de indentação do
`ganai`. Um ramo pode conter outro condicional. Importações e declarações
`brivla` só são permitidas no nível superior.

```text
ganai xu la djan. patfu la mark. gi
    li resultado. du li pa
gi'e
    li resultado. du li no
```

## Exemplos cobertos

Todos os arquivos `.ban` diretamente em `examples/` são exemplos válidos e
devem ser aceitos pelo parser. Os arquivos em `examples/invalidos/` são
contraexemplos intencionais e devem gerar `ParseError`. Os testes do parser
validam ambos os grupos.

A gramática não define ainda a resolução de módulos, a inferência lógica,
tipos estáticos nem o comportamento de runtime.
