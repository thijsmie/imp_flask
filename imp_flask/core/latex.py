"""Latex templating engine, available application-wide."""

import re
import jinja2
import latex
from flask import make_response
import datetime


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


def format_date(value, date_format='%Y-%m-%d'):
    return value.strftime(date_format)


class TexRenderer:
    def __init__(self):
        self.jinja2env = None
        self.static_path = ""

    def render_template(self, template, *args, **kwargs):
        lt_template = self.jinja2env.get_template(template)
        return lt_template.render(*args, **kwargs)

    def init_path(self, template_path, static_path, strings):
        self.jinja2env = jinja2.Environment(
          block_start_string='(%',
          block_end_string='%)',
          variable_start_string='((%',
          variable_end_string='%))',
          comment_start_string='(//',
          comment_end_string='//)',
          loader=jinja2.FileSystemLoader(template_path)
        )
        self.jinja2env.filters['escape_tex'] = escape_tex
        self.jinja2env.filters['format_date'] = format_date
        self.jinja2env.globals['strings'] = strings
        self.static_path = static_path

    def make_attachable_pdf(self, filename, texstring):
        pdf = latex.build_pdf(texstring, [self.static_path])
        return {
            "filename": filename,
            "mimetype": "application/pdf",
            "data": str(pdf)
        }

    def make_downloadable_pdf(self, filename, texstring):
        pdf = latex.build_pdf(texstring, [self.static_path])
        response = make_response(str(pdf))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        response.headers["Content-Type"] = "application/pdf"
        return response


texenv = TexRenderer()
