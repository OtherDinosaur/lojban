# Skamban

Protótipo da linguagem declarativa Skamban, baseada em Lojban.

## Estado

Versão de trabalho: 0.2 (lexer, parser e AST inicial).

O projeto implementa o lexer, um parser recursivo descendente e as estruturas
iniciais da AST. Análise semântica, motor de inferência e runtime ainda serão
desenvolvidos.

Consulte [GRAMMAR.md](GRAMMAR.md) para a sintaxe de referência da versão 0.1.

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

Para analisar código Python:

```python
from pathlib import Path
from skamban.parser import parse

program = parse(Path("examples/basico.ban").read_text(encoding="utf-8"))
print(program)
```

## Próximas etapas

1. manter exemplos e parser alinhados com [GRAMMAR.md](GRAMMAR.md);
2. implementar tabela de símbolos/análise semântica;
3. implementar inferência;
4. implementar runtime.
