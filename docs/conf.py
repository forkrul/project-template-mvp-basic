"""Sphinx configuration.

Markdown-only via myst-parser: pages under docs/ are the same files GitHub
renders, so there is no second copy of the documentation to keep in sync.
Root-level documents (PACKAGES.md, TEMPLATE_CHECKLIST.md, CHANGELOG.md) are
pulled in with ``{include}`` for the same reason.

Build: ``make docs`` — ``sphinx-build -W --keep-going``. Zero warnings is the
gate; fix warnings rather than relaxing the flag.
"""

from __future__ import annotations

import pathlib
import tomllib

# Name and version come from pyproject.toml rather than being restated here:
# a string maintained in two places is one that disagrees.
_pyproject = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
_meta = tomllib.loads(_pyproject.read_text())["project"]

project = _meta["name"]
release = _meta["version"]
version = release
author = "forkrul"
copyright = "forkrul"  # noqa: A001 - Sphinx config name

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

source_suffix = {".md": "markdown"}
root_doc = "index"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = [
    "colon_fence",  # ::: fences, which GitHub renders as text rather than breaking
    "deflist",
    "tasklist",
]

# GitHub renders headings as anchors; match it so a link that works in the
# repository also works on the built site.
myst_heading_anchors = 4

autodoc_typehints = "description"

html_theme = "furo"
html_title = f"{project} {release}"
