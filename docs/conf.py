import os
import sys

import django

project = "Django Anchor"
copyright = "2024, Elias Hernandis"
author = "Elias Hernandis"


# Make source available for autodoc
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
sys.path.insert(0, os.path.abspath(".."))
django.setup()

import anchor  # noqa: E402

release = anchor.__version__


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# -- Napoleon extension configuration ----------------------------------------

# This extension allows using Google and NumPy-style docstrings in docstrings.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
