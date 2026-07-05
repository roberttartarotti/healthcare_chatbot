"""Sphinx configuration for the Healthcare Assistant documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Healthcare Assistant"
author = "Robert Tartarotti"
copyright = "2026, Robert Tartarotti"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_mock_imports = ["chromadb", "pypdf", "fastapi"]
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

try:
    import sphinx_rtd_theme  # noqa: F401

    html_theme = "sphinx_rtd_theme"
except ImportError:
    html_theme = "alabaster"

html_static_path = []
