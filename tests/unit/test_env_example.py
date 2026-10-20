"""Anyone running Mallard starts by copying .env.example to .env, so it has to name every variable the code reads."""

import ast
from pathlib import Path

ROOT = Path(__file__).parents[2]
ENV_READERS = {"env", "os.environ.get", "os.getenv"}


def variables_read_in(path: Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if not (isinstance(node, ast.Call) and node.args and ast.unparse(node.func) in ENV_READERS):
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            names.add(first.value)
    return names


def variables_in_env_example() -> set[str]:
    lines = (ROOT / ".env.example").read_text().splitlines()
    return {line.split("=", 1)[0] for line in lines if "=" in line and not line.startswith("#")}


def test_env_example_lists_every_variable_the_code_reads() -> None:
    read = set().union(*(variables_read_in(path) for path in (ROOT / "src").rglob("*.py")))

    assert "CATALOG_PASSWORD" in read, "the scan should find the lake's variables"
    assert read - variables_in_env_example() == set()
