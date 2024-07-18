import os
import sys
import toml
import django

project = "Django Anchor"
copyright = "2024, Elias Hernandis"
author = "Elias Hernandis"

# Read version from pyproject.toml
with open("../pyproject.toml", "r") as f:
    pyproject = toml.load(f)
    release = pyproject["tool"]["poetry"]["version"]

# Make source available for autodoc
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"
sys.path.insert(0, os.path.abspath(".."))
django.setup()


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

# -- Napoleon extension configuration ----------------------------------------

# This extension allows using Google and NumPy-style docstrings in docstrings.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
