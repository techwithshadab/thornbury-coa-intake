"""Internal markdown links must resolve.

This repo is public and its README is the front page. A dangling link there is a first-impression
defect, and one shipped: the README's "Architecture sketch" section still carried the scaffold's
placeholder diagram (`Source System -> This Repo -> Downstream Consumer`) and a link to a
`docs/architecture.md` that had never been written.

`make placeholders` did not catch it, and could not: an unfilled *section* carries no placeholder
*marker*. That gate checks for template text; this one checks that what the docs promise exists.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Skip image embeds (![...]) and strip anchors; HTML comments are template instructions, not claims.
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)#]+?)(?:#[^)]*)?\)")
COMMENT = re.compile(r"<!--.*?-->", re.S)


def _markdown_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.split()


@pytest.mark.parametrize("relative", _markdown_files(), ids=lambda p: p)
def test_every_internal_link_resolves(relative):
    path = ROOT / relative
    body = COMMENT.sub("", path.read_text(encoding="utf-8"))
    broken = [
        target
        for target in LINK.findall(body)
        if not target.startswith(("http://", "https://", "mailto:"))
        and not (path.parent / target).resolve().exists()
    ]
    assert not broken, f"{relative} links to files that do not exist: {broken}"


def test_the_scaffold_placeholder_diagram_is_gone():
    """The template ships a three-box diagram that says nothing. It rendered on the front page of a
    public repo for eleven days, which is the kind of thing a reader judges the rest by."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Source System" not in readme
    assert "Downstream Consumer" not in readme
