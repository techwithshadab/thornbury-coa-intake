"""Single owner of root / config-path derivation — the ONE config boundary.

This module is the only place in `src/` that reads the environment. Every other module takes
resolved paths as arguments. `tests/test_path_ownership.py` enforces that.

Resolution order for each root is explicit and has exactly one step of fallback, documented here so
it is a contract rather than a surprise:

    1. the value passed on the command line (`--documents`, `--reference`)
    2. `$COA_WORKSPACE_ROOT/<subdir>`
    3. no third step — raise

There is no repo-relative default. A run that cannot say where its documents came from must fail,
not quietly read a copy that happens to sit next to the code: the capstone runs this pipeline
against documents it has not shown us, so a constant inside the program is a wrong answer waiting.
"""

from __future__ import annotations

import os
import pathlib

# The one config root. Exactly one env var points at the workspace. No second root, no fallback.
WORKSPACE_ENV = "COA_WORKSPACE_ROOT"

DOCUMENTS_SUBDIR = "documents"
REFERENCE_SUBDIR = "reference"


def repo_root() -> pathlib.Path:
    """The app repo root (this file is src/coa_intake/paths.py → parents[2] is the repo)."""
    return pathlib.Path(__file__).resolve().parents[2]


def workspace_root() -> pathlib.Path:
    """The one workspace root, from WORKSPACE_ENV. Fail loud if unset — no app-repo fallback."""
    raw = os.environ.get(WORKSPACE_ENV)
    if not raw or not raw.strip():
        raise RuntimeError(
            f"{WORKSPACE_ENV} is unset and no path was given on the command line. "
            f"Point it at the workspace root (it must contain {DOCUMENTS_SUBDIR}/ and "
            f"{REFERENCE_SUBDIR}/), or pass --documents/--reference explicitly. "
            f"There is no default and no app-repo fallback."
        )
    root = pathlib.Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError(f"{WORKSPACE_ENV}={raw!r} does not resolve to a directory.")
    return root


def _resolve(override: str | None, subdir: str) -> pathlib.Path:
    if override is not None and str(override).strip():
        path = pathlib.Path(override).expanduser().resolve()
    else:
        path = workspace_root() / subdir
    if not path.is_dir():
        raise RuntimeError(f"{subdir} root does not resolve to a directory: {path}")
    return path


def documents_root(override: str | None = None) -> pathlib.Path:
    """Where the certificates are. An INPUT to the program, never a constant inside it."""
    return _resolve(override, DOCUMENTS_SUBDIR)


def reference_root(override: str | None = None) -> pathlib.Path:
    """Reviewed reference data: the SPEC-7 acceptance table, the supplier master, the synonym map."""
    return _resolve(override, REFERENCE_SUBDIR)
