"""Latex templating engine, available application-wide."""

import os
import re
import jinja2
import latex
from flask import make_response


# Note that the path to tex templates is hardcoded. This should somehow be instantiated after app init with the
# app level variable TEXTEMPLATE_FOLDER. Pull-requests fixing this are welcome. (TODO)
LATEX_SUBS = (
    (re.compile(r'\n'), r'\\\\'),
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)


def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

texenv = jinja2.Environment(
  block_start_string='(%',
  block_end_string='%)',
  variable_start_string='((%',
  variable_end_string='%))',
  comment_start_string='(//',
  comment_end_string='//)',
  loader=jinja2.FileSystemLoader(os.path.abspath('../textemplates'))
)

texenv.filters['escape_tex'] = escape_tex


def make_attachable_pdf(filename, texstring):
    pdf = latex.build_pdf(texstring, os.path.abspath('../texstatic'))
    return {
        "filename": filename,
        "mimetype": "application/pdf",
        "data": str(pdf)
    }


def make_downloadable_pdf(filename, texstring):
    pdf = latex.build_pdf(texstring, os.path.abspath('../texstatic'))
    response = make_response(str(pdf))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
    response.headers["Content-Type"] = "application/pdf"
    return response
