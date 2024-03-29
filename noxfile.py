"""Nox sessions."""

import platform

import nox
from nox_poetry import Session, session

nox.options.sessions = ["tests", "mypy"]
python_versions = ["3.12"]


@session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    session.install(".")
    session.install("invoke", "pytest", "xdoctest", "coverage[toml]", "pytest-cov")
    try:
        session.run(
            "inv",
            "tests",
            env={
                "COVERAGE_FILE":
                    f".coverage.{platform.system()}.{platform.python_version()}",
            },
        )
    finally:
        if session.interactive:
            session.notify("coverage")


@session
def coverage(session: Session) -> None:
    """Produce the coverage report."""
    args = []
    if session.posargs and len(session._runner.manifest) == 1:  # noqa: SLF001
        args = session.posargs
    session.install("invoke", "coverage[toml]")
    session.run("inv", "coverage", *args)


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    session.install(".")
    session.install("invoke", "mypy")
    session.run("inv", "mypy")
