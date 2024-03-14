"""Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke
"""

import platform
import webbrowser
from pathlib import Path

from invoke import call, task
from invoke.context import Context
from invoke.runners import Result

ROOT_DIR = Path(__file__).parent
COVERAGE_FILE = ROOT_DIR.joinpath(".coverage")
COVERAGE_DIR = ROOT_DIR.joinpath("htmlcov")
COVERAGE_REPORT = COVERAGE_DIR.joinpath("index.html")
SOURCE_DIR = ROOT_DIR.joinpath("src/dockerize_poetry")
TEST_DIR = ROOT_DIR.joinpath("tests")
PYTHON_TARGETS = [
    SOURCE_DIR,
    TEST_DIR,
    ROOT_DIR.joinpath("noxfile.py"),
    Path(__file__),
]
PYTHON_TARGETS_STR = " ".join([str(p) for p in PYTHON_TARGETS])


def _run(c: Context, command: str) -> Result | None:
    return c.run(command, pty=platform.system() != "Windows")


@task()
def clean_build(c: Context) -> None:
    """Clean up files from package building."""
    _run(c, "rm -fr build/")
    _run(c, "rm -fr dist/")
    _run(c, "rm -fr .eggs/")
    _run(c, "find . -name '*.egg-info' -exec rm -fr {} +")
    _run(c, "find . -name '*.egg' -exec rm -f {} +")


@task()
def clean_python(c: Context) -> None:
    """Clean up python file artifacts."""
    _run(c, "find . -name '*.pyc' -exec rm -f {} +")
    _run(c, "find . -name '*.pyo' -exec rm -f {} +")
    _run(c, "find . -name '*~' -exec rm -f {} +")
    _run(c, "find . -name '__pycache__' -exec rm -fr {} +")


@task()
def clean_tests(c: Context) -> None:
    """Clean up files from testing."""
    _run(c, f"rm -f {COVERAGE_FILE}")
    _run(c, f"rm -fr {COVERAGE_DIR}")
    _run(c, "rm -fr .pytest_cache")


@task(pre=[clean_build, clean_python, clean_tests])
def clean(_: Context) -> None:
    """Run all clean sub-tasks."""


@task()
def install_hooks(c: Context) -> None:
    """Install pre-commit hooks."""
    _run(c, "poetry run pre-commit install")


@task()
def hooks(c: Context) -> None:
    """Run pre-commit hooks."""
    _run(c, "poetry run pre-commit run --all-files")


@task(name="format", help={
    "check": "Checks if source is formatted without applying changes",
})
def format_(c: Context, check: bool = False) -> None:
    """Format code."""
    isort_options = ["--check-only", "--diff"] if check else []
    _run(c, f"poetry run isort {' '.join(isort_options)} {PYTHON_TARGETS_STR}")
    black_options = ["--diff", "--check"] if check else ["--quiet"]
    _run(c, f"poetry run black {' '.join(black_options)} {PYTHON_TARGETS_STR}")


@task()
def ruff(c: Context) -> None:
    """Run ruff."""
    _run(c, f"poetry run ruff check {PYTHON_TARGETS_STR}")


@task(pre=[ruff, call(format_, check=True)])
def lint(_: Context) -> None:
    """Run all linting."""


@task()
def mypy(c: Context) -> None:
    """Run mypy."""
    _run(c, f"poetry run mypy {PYTHON_TARGETS_STR}")


@task()
def tests(c: Context) -> None:
    """Run tests."""
    pytest_options = ["--xdoctest", "--cov", "--cov-report=", "--cov-fail-under=0"]
    _run(c, f"poetry run pytest {' '.join(pytest_options)} {TEST_DIR} {SOURCE_DIR}")


@task(
    help={
        "fmt": "Build a local report: report, html, json, annotate, html, xml.",
        "open_browser":
            "Open the coverage report in the web browser (requires --fmt html)",
    },
)
def coverage(c: Context, fmt: str = "report", open_browser: bool = False) -> None:
    """Create coverage report."""
    if any(Path().glob(".coverage.*")):
        _run(c, "poetry run coverage combine")
    _run(c, f"poetry run coverage {fmt} -i")
    if fmt == "html" and open_browser:
        webbrowser.open(COVERAGE_REPORT.as_uri())


@task(
    help={
        "part": "Part of the version to be bumped.",
        "dry_run": "Don't write any files, just pretend. (default: False)",
    },
)
def version(c: Context, part: str, dry_run: bool = False) -> None:
    """Bump version."""
    bump_options = ["--dry-run"] if dry_run else []
    _run(c, f"poetry run bump2version {' '.join(bump_options)} {part}")
