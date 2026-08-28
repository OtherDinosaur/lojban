# Skamban

Protótipo inicial do lexer da linguagem Skamban.

## Estado

Versão de trabalho: 0.1 (lexer).

O projeto implementa apenas a etapa lexical. Parser, AST, análise semântica,
motor de inferência e runtime ainda serão desenvolvidos.

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

1. estabilizar o lexer;
2. especificar e implementar o parser;
3. criar a AST;
4. implementar tabela de símbolos/análise semântica;
5. implementar inferência;
6. implementar runtime.
