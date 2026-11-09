# Skamban

Protótipo inicial do lexer da linguagem Skamban.

## Estado

Versão de trabalho: 0.1 (lexer).

O projeto implementa o lexer e as estruturas iniciais da AST. O parser,
análise semântica, motor de inferência e runtime ainda serão desenvolvidos.

## Requisitos

Python 3.10+.

## Executar os testes

```bash
python -m unittest discover -s tests -v
```

## Testar um arquivo

```bash
python -m skamban.lexer.lexer examples/basico.ban
```

## Próximas etapas

1. estabilizar a gramática da versão 0.1 e o lexer;
2. especificar e implementar o parser usando a AST existente;
3. implementar tabela de símbolos/análise semântica;
4. implementar inferência;
5. implementar runtime.
