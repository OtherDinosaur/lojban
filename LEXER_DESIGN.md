# Skamban — Design do Lexer 0.1

## Responsabilidade

O lexer transforma caracteres do arquivo `.ban` em tokens.

Ele NÃO deve:

- resolver nomes;
- verificar se um identificador é brivla;
- verificar se um predicado existe;
- inferir tipos;
- executar expressões.

## Tokens previstos

### Reservados

BRIVLA, GANAI, GI, GI_E, NERBEI,
LI, LA, LU, LU_O, ZO_E,
XU, MA,
BE, BE_O,
DU, NA, SU_I, VU_U, PI_I, FE_I, ZMADU, MLECA.

### Estruturais

NEWLINE, INDENT, DEDENT, EOF, DOT.

### Dinâmicos

IDENTIFIER, NUMBER, STRING.

### Lugares

X1, X2, X3, X4, X5.

## Regra de classificação

O lexer primeiro reconhece uma sequência lexicalmente válida. Se o texto
coincidir exatamente com palavra reservada, produz o token reservado.
Caso contrário, produz IDENTIFIER.

A validade morfológica de brivla fica para a análise semântica.

## Indentação

Usar uma pilha de colunas. A coluna inicial é 0.

Aumento de nível produz INDENT.
Redução produz um ou mais DEDENT.
Redução para um nível inexistente é erro.

Tabs devem ser tratados de forma consistente; a implementação inicial
recomenda rejeitar mistura de tabs e espaços na indentação.

## Comentários

`#` inicia comentário até o fim da linha.

## Fim de arquivo

Após processar o conteúdo, todos os níveis de indentação pendentes devem
gerar DEDENT, seguido de EOF.

## Números

A implementação inicial aceita:

- inteiros em algarismos;
- ponto flutuante decimal em algarismos;
- numerais Lojban básicos;
- combinação `NUMERAL pi NUMERAL` como número decimal.

A conversão de numerais Lojban deve ficar isolada em uma função para poder
ser expandida sem alterar o lexer principal.

## Observação

A gramática numérica de `pi` ainda será refinada no parser. O lexer inicial
mantém o tratamento simples e testável.
