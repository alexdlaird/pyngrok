__copyright__ = "Copyright (c) 2018-2025 Alex Laird"
__license__ = "MIT"

import datetime
import os
import sys

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.insert(0, os.path.abspath(".."))

# This import must happen after adding to sys.path so docs build is consistent across environments
from pyngrok import __version__

# -- Project information -----------------------------------------------------

project = "pyngrok"
description = ("A Python wrapper for ngrok that manages its own binary, making ngrok available via a convenient "
               "Python API and the command line.")
github_url = "https://github.com/alexdlaird/pyngrok"
copyright = f"2018-{datetime.date.today().year}, Alex Laird"
author = "Alex Laird"

# The short X.Y version
version = __version__
# The full version, including alpha/beta/rc tags
release = version

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = "1.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "notfound.extension",
    "sphinx_autodoc_typehints",
    "sphinx_substitution_extensions",
    "sphinx_sitemap",
    "sphinxext.opengraph",
    "sphinxcontrib.googleanalytics",
]
autodoc_member_order = "bysource"

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = [
    ".rst"
]

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["build", "Thumbs.db", ".DS_Store", "venv"]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# -- Options for HTML output -------------------------------------------------

html_baseurl = "https://pyngrok.readthedocs.io/en/stable/"
sitemap_url_scheme = "{link}"

ogp_site_url = html_baseurl
ogp_image = f"{html_baseurl}_images/logo.png"
ogp_image_alt = "pyngrok - A Python wrapper for ngrok; programmatic tunnels for ingress, webhooks, demos, and APIs"
ogp_type = "website"
ogp_social_cards = {"enable": False}
ogp_enable_meta_description = False

ogp_custom_meta_tags = [
    f'<meta name="description" content="{description}">',
    '<meta name="twitter:card" content="summary_large_image">',
    '<meta name="yandex-verification" content="ac8f18b56add6591">',
]

googleanalytics_id = "G-98DG8TRJJP"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_logo = "_static/logo-transparent.png"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "source_repository": github_url,
    "source_branch": "main",
    "source_directory": "docs/",
    "sidebar_hide_name": True,
    "top_of_page_buttons": ["edit"],
    "footer_icons": [
        {
            "name": "GitHub",
            "url": github_url,
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_extra_path = ["_html"]

html_css_files = [
    "custom.css",
]

templates_path = ["_templates"]

html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/getting-around.html",
        "sidebar/useful-links.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
    ],
}

toc_object_entries = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "pyngrokdoc"

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    #
    # "papersize": "letterpaper",

    # The font size ("10pt", "11pt" or "12pt").
    #
    # "pointsize": "10pt",

    # Additional stuff for the LaTeX preamble.
    #
    # "preamble": "",

    # Latex figure (float) alignment
    #
    # "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "pyngrok.tex", "pyngrok Documentation",
     author, "manual"),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, "pyngrok", "pyngrok Documentation",
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, "pyngrok", "pyngrok Documentation",
     author, "pyngrok", "A Python wrapper for ngrok; programmatic tunnels for ingress, webhooks, demos, and APIs",
     "Miscellaneous"),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ""

# A unique identification for the text.
#
# epub_uid = ""

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

rst_prolog = """
.. |pyngrok_version| replace:: {pyngrok_version}
""".format(pyngrok_version=version)
