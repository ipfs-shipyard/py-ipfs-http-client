#!/usr/bin/env python3
#
# Python IPFS HTTP Client documentation build configuration file, created by
# sphinx-quickstart on Wed Aug 17 20:41:53 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import os
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('..'))

# Make current version number as `__version__` available
with open(os.path.join(sys.path[0], 'ipfshttpclient', 'version.py')) as file:
	exec(file.read())

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = '3.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.doctest',
	'sphinx.ext.todo',
	'sphinx.ext.intersphinx',
	'sphinx.ext.napoleon',
	'sphinx.ext.coverage',
	'sphinx.ext.viewcode',
	'recommonmark',
	'sphinx_autodoc_typehints'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of strings:
source_suffix = ['.rst', '.md']

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Python IPFS HTTP Client'
copyright = '2020, py-ipfs-http-client team'
author = 'py-ipfs-http-client team'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '.'.join(__version__.split('.')[0:2])
# The full version, including alpha/beta/rc tags.
release = __version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#
# today = ''
#
# Else, today_fmt is used as the format for a strftime call.
#
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'nature'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.
# "<project> v<release> documentation" by default.
# html_title = 'Python IPFS HTTP Client v0.2.4'

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
# html_last_updated_fmt = None

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr', 'zh'
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
# html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'py-ipfs-http-client'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
	# The paper size ('letterpaper' or 'a4paper').
	# 'papersize': 'letterpaper',

	# The font size ('10pt', '11pt' or '12pt').
	# 'pointsize': '10pt',

	# Additional stuff for the LaTeX preamble.
	# 'preamble': '',

	# Latex figure (float) alignment
	# 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
	(master_doc, 'PythonIPFSHTTPClient.tex', 'Python IPFS HTTP Client Documentation',
	 'py-ipfs-http-client team', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
	(master_doc, 'py-ipfs-http-client', 'Python IPFS HTTP Client Documentation',
	 [author], 1)
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
	(master_doc, 'py-ipfs-http-client', 'Python IPFS HTTP Client Documentation',
	 author, 'py-ipfs-http-client', 'One line description of project.',
	 'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

# -- AutoDoc settings -----------------------------------------------------

autodoc_member_order = 'groupwise'

# -- InterSphinx settings -------------------------------------------------

# External documentation link mapping
intersphinx_mapping = {
	'python': ('https://docs.python.org/3', None),
	'cid': ('https://py-cid.readthedocs.io/en/master/', (None, "py-cid.inv")),
	'multiaddr': ('https://multiaddr.readthedocs.io/en/latest/', None)
}

# -- Napoleon settings ----------------------------------------------------

# Parse Google style docstrings.
napoleon_google_docstring = False

# Parse NumPy style docstrings.
napoleon_numpy_docstring = True

# Include private members (like _membername) with docstrings in the documentation.
napoleon_include_private_with_doc = False

# Include special members (like __membername__) with docstrings in the documentation.
napoleon_include_special_with_doc = True

# Use the .. admonition:: directive for the Example and Examples sections.
# False to use the .. rubric:: directive instead.
# One may look better than the other depending on what HTML theme is used.
napoleon_use_admonition_for_examples = False

# Use the .. admonition:: directive for Notes sections.
# False to use the .. rubric:: directive instead.
napoleon_use_admonition_for_notes = False

# Use the .. admonition:: directive for References sections.
# False to use the .. rubric:: directive instead.
napoleon_use_admonition_for_references = False

# Use the :ivar: role for instance variables.
# False to use the .. attribute:: directive instead.
napoleon_use_ivar = False

# Use a :param: role for each function parameter.
# False to use a single :parameters: role for all the parameters.
napoleon_use_param = True

# Use the :rtype: role for the return type.
# False to output the return type inline with the description.
napoleon_use_rtype = False


# Add a list of custom sections to include, expanding the list of
# parsed sections.
#
# The entries can either be strings or tuples, depending on the
# intention:
#   • To create a custom “generic” section, just pass a string.
#   • To create an alias for an existing section, pass a tuple
#     containing the alias name and the original, in that order.
napoleon_custom_sections = [
	"Directory uploads",  # Used in ipfshttpclient/client/files.py
]


# -- AutoDoc extension for documenting our main `Client` object -----------

import sphinx.ext.autodoc


class ClientClassDocumenterBase(sphinx.ext.autodoc.ClassDocumenter):
	directivetype = "class"

	@property
	def documenters(self):
		"""Ensure that all subclasses within a ``clientclass`` documentation
		object will definitely be handled by this documenter again."""
		documenters = {
			"clientsubclass": ClientSubClassDocumenter
		}
		documenters.update(super().documenters)
		return documenters

	def import_object(self):
		"""Prevent client class objects from being marked as “properties”."""
		if super().import_object():
			# Document the shadowed `ipfshttpclient.client.base.Section` type
			# rather then its (uninteresting) property wrapper
			self.doc_as_attr = False
			return True
		return False
	
	def format_signature(self):
		"""Hide inheritance signature since it's not applicable helpful for
		these classes."""
		return "({0})".format(self.args) if self.args is not None else ""


class ClientClassDocumenter(ClientClassDocumenterBase):
	objtype = "clientclass"
	priority = -100


class ClientSubClassDocumenter(ClientClassDocumenterBase):
	objtype = "clientsubclass"
	priority = 100


import sphinx.util.inspect


def section_property_attrgetter(object, name, default=None):
	try:
		prop = sphinx.util.inspect.safe_getattr(object, name)
		
		# Try returning the underlying section property class
		try:
			return sphinx.util.inspect.safe_getattr(prop, "__prop_cls__")
		except AttributeError:
			pass
		
		# Return object itself
		return prop
	except AttributeError as e:
		pass
	
	# Nothing found: Return default
	return default


# app setup hook for reCommonMark's AutoStructify and our own extension
def setup(app):
	# Import the CID library so that its types will be included in the
	# analyzed typings (has `sys.modules` detection)
	import cid
	
	# Ensure we are building with reCommonMark 0.5+
	import recommonmark
	assert tuple(int(v) for v in recommonmark.__version__.split(".", 2)[0:2]) >= (0, 5)
	
	from recommonmark.transform import AutoStructify
	app.add_config_value("recommonmark_config", {
		"auto_toc_tree_section": "Contents",
	}, True)
	app.add_transform(AutoStructify)
	
	# Add special documentation for `Client` class
	app.add_autodocumenter(ClientClassDocumenter)
	# Allow names to be resolved through the property objects of the client
	# class without resorting to lots of name rewriting (as was the case with
	# the previous implementation)
	app.add_autodoc_attrgetter(object, section_property_attrgetter)
