"""Shared commands. CI runs the same ones."""

from invoke.context import Context
from invoke.tasks import task


@task
def format(c: Context) -> None:
    c.run("ruff check --fix .")
    c.run("ruff format .")


@task
def lint(c: Context) -> None:
    c.run("ruff check .")
    c.run("ruff format --check .")
    c.run("mypy")


@task
def audit(c: Context) -> None:
    """Check locked dependencies for known vulnerabilities."""
    c.run("uv audit --preview-features audit-command")


@task
def test(c: Context) -> None:
    c.run("pytest")


@task(pre=[lint, audit, test], default=True)
def check(c: Context) -> None:
    """Everything CI runs."""
