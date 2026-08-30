"""Invariant enforced by a test (Bar A: A4) — `paths.py` is the SOLE owner of root/config derivation,
runtime fails loud when the workspace is unset (A5), and there are no obvious silent fallbacks (A1/A5).

This is the exemplar A4 test: it fails when someone reintroduces a second config root, reads the env var
outside paths.py, or adds a `except: return None` silent-skip. Keep it green. Source-grep based, so it needs
no third-party deps — it runs even before the package's own dependencies are installed.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from coa_intake import paths

SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
PKG_FILES = sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)
PATHS_FILE = pathlib.Path(paths.__file__).resolve()


def _src(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def test_only_paths_reads_the_workspace_env():
    """The workspace env var name appears in src only in paths.py (single config root, A1)."""
    offenders = [
        p.relative_to(SRC).as_posix() for p in PKG_FILES if p != PATHS_FILE and paths.WORKSPACE_ENV in _src(p)
    ]
    assert not offenders, (
        f"{paths.WORKSPACE_ENV} is referenced outside paths.py: {offenders}. "
        "Resolve roots through paths.py resolvers; don't read the env var elsewhere."
    )


def test_only_paths_touches_os_environ():
    """No module but paths.py reads os.environ / getenv directly (no second root, no fallback)."""
    env_read = re.compile(r"\b(os\.environ|os\.getenv|environ\[)")
    offenders = [
        p.relative_to(SRC).as_posix() for p in PKG_FILES if p != PATHS_FILE and env_read.search(_src(p))
    ]
    assert not offenders, f"env access outside paths.py: {offenders} — route config through paths.py."


def test_workspace_root_fails_loud_when_unset(monkeypatch):
    """Unset workspace -> a structured error, never a default (A5: fail-closed boot)."""
    monkeypatch.delenv(paths.WORKSPACE_ENV, raising=False)
    with pytest.raises(RuntimeError):
        paths.workspace_root()


def test_no_obvious_silent_fallback():
    """Flag the classic silent-skip shapes (`except: pass`, `except ...: return None`) in src (A5)."""
    silent = re.compile(r"except[^\n:]*:\s*\n\s*(pass|return\s+None)\b")
    offenders = [p.relative_to(SRC).as_posix() for p in PKG_FILES if silent.search(_src(p))]
    assert not offenders, (
        f"possible silent fallback in {offenders} — surface a structured error instead of swallowing it."
    )
