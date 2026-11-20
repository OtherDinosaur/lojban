from dataclasses import asdict
from pathlib import Path
from pprint import pprint

from skamban.parser import parse

source = Path("examples/basico.ban").read_text(encoding="utf-8")
program = parse(source)

pprint(asdict(program), sort_dicts=False)

for statement in program.statements:
    print(type(statement).__name__, statement)