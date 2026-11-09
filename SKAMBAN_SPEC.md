# Skamban — Especificação de Projeto 0.1

## Objetivo

Skamban é uma linguagem de programação declarativa baseada em Lojban.
O objetivo é permitir que um lojbanista descreva relações, fatos, regras e
ações com construções próximas da língua, mantendo uma representação
executável.

Extensão dos arquivos: `.ban`.

## Princípios

- Predicados são a unidade fundamental da linguagem.
- Predicados possuem x1 obrigatório e até x5.
- x1 representa o resultado; x2–x5 são argumentos.
- Os nomes escritos depois de x1–x5 na declaração são rótulos documentais;
  não criam variáveis nem alteram a semântica dos lugares.
- `zo'e` representa resultado nulo/irrelevante.
- Indentação delimita blocos.
- `.` não termina frases; marca o termo conforme a convenção adotada.
- O lexer não decide se um identificador é brivla, predicado nativo ou
  predicado definido pelo usuário. Essa decisão pertence à análise semântica.
- Palavras reservadas são reconhecidas lexicalmente.
- `pinai` é um predicado nativo, não uma palavra reservada.
- `ietnu` e `iitfa` são valores booleanos nativos.

## Tipos

- `li` introduz valores numéricos.
- `la` introduz valores não numéricos.
- `lu ... lu'o` delimita strings.
- `zo'e` representa nulo.

`le` fica fora da versão 0.1 até que sua semântica seja definida.

## Números

São aceitos números em algarismos e numerais Lojban.

Exemplos:

    li 10
    li pano
    li 3.14
    li ci pi pa

A representação interna é `NUMBER`.

`pi` pode participar da escrita de números Lojban com parte fracionária. A
sequência `ci pi pa` é um único número e produz um único token `NUMBER`.
Numerais Lojban usam somente dígitos decimais de 0 a 9 nesta versão; `dau`
e os demais dígitos acima de 9 ficam fora do escopo.
`pi'i` continua sendo o operador de multiplicação.

## Consultas

- `xu` inicia uma consulta booleana.
- `ma` representa uma incógnita.
- Consulta booleana retorna `ietnu` ou `iitfa`.

Não existe equivalente obrigatório a `?-` do Prolog.

## Agrupamento

`be ... be'o` funciona como agrupamento de expressão.

## Condicionais

- `ganai`
- `gi`
- `gi'e`

`gi'e` permite ramo alternativo, inclusive outro `ganai`.

## Módulos

`nerbei` introduz importação de módulo.

## Operadores iniciais

- `du` — atribuição.
- `dunli` — igualdade entre valores em expressões.
- `na` — negação.
- `su'i` — adição.
- `vu'u` — subtração.
- `pi'i` — multiplicação.
- `fe'i` — divisão.
- `zmadu` — maior que.
- `mleca` — menor que.

`zmadu du` e `mleca du` serão interpretados pelo parser/análise semântica
como `>=` e `<=`.

`dunli` permanece um identificador lexical comum, como os demais predicados
nativos. O parser o interpreta como igualdade apenas na posição de operador.

## Predicados

Declaração:

    brivla cmadi
        x1 jalge
        x2 pa_nota
        x3 re_nota

Chamada:

    li media. cmadi li nota1. li nota2.

A palavra `brivla` é reservada por estilo e explicita uma declaração.

## Lexemas compostos

- `gi'e`
- `be'o`
- `lu'o`
- `zo'e`
- `pi'i`
- `pi` (somente dentro de numeral decimal)
- `su'i`
- `vu'u`
- `fe'i`

O lexer deve priorizar formas compostas antes de formas menores que poderiam
ser prefixos delas.

## Apóstrofo

Um apóstrofo não é separador genérico de palavras.

Ele só aparece em lexemas permitidos pela gramática lexical, como `gi'e`,
`be'o` e `lu'o`.

Um apóstrofo isolado ou terminando um identificador deve produzir erro léxico.

## Espaços e frases

Espaços separam lexemas, mas não terminam frases por si mesmos.

Quebras de linha são significativas para `NEWLINE`, e a indentação produz
`INDENT`/`DEDENT`. Um arquivo deve usar apenas espaços ou apenas tabs na
indentação; misturar estilos, inclusive entre níveis, é erro lexical.

Uma frase pode terminar por quebra de linha ou pela redução do nível de
indentação; `.` não é terminador de sentença.
