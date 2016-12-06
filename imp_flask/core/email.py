"""Convenience functions for sending email from any view."""

from contextlib import contextmanager
from logging import getLogger

from flask import current_app
from flask_mail import Message
from werkzeug.debug import tbtools

from imp_flask.extensions import mail

LOG = getLogger(__name__)


@contextmanager
def _override_html():
    """Temporarily changes the module constants in `tbtools` to make it email-friendly.

    Gmail strips out everything between <style></style>, so all styling has to be inline using the style="" attribute in
    HTML tags. These changes makes the Flask debugging page HTML (shown when unhandled exceptions are raised with
    DEBUG = True) email-friendly. Designed to be used with the `with` statement.

    It's too bad `tbtools.Traceback` doesn't copy module constants to instance variables where they can be easily
    overridden, ugh!
    """
    # Backup.
    old_page_html = tbtools.PAGE_HTML
    old_summary = tbtools.SUMMARY_HTML
    old_frame = tbtools.FRAME_HTML
    # Get new HTML.
    email_template = current_app.jinja_env.get_template('email.html')
    email_context = email_template.new_context()
    page_html = email_template.blocks['page_html'](email_context).next()
    summary_html = email_template.blocks['summary_html'](email_context).next()
    frame_html = email_template.blocks['frame_html'](email_context).next()
    # Change module variables.
    tbtools.PAGE_HTML = page_html
    tbtools.SUMMARY_HTML = summary_html
    tbtools.FRAME_HTML = frame_html
    yield  # Let `with` block execute.
    # Revert changes.
    tbtools.PAGE_HTML = old_page_html
    tbtools.SUMMARY_HTML = old_summary
    tbtools.FRAME_HTML = old_frame


def send_exception(subject):
    """Send Python exception tracebacks via email to the ADMINS list.

    Use the same HTML styling as Flask tracebacks in debug web servers.

    This function must be called while the exception is happening. It picks up the raised exception with sys.exc_info().

    Positional arguments:
    subject -- subject line of the email (to be prepended by 'Application Error: ').
    """
    # Generate and modify html.
    tb = tbtools.get_current_traceback()  # Get exception information.
    with _override_html():
        html = tb.render_full().encode('utf-8', 'replace')
    html = html.replace('<blockquote>', '<blockquote style="margin: 1em 0 0; padding: 0;">')
    subject = 'Application Error: {}'.format(subject)

    # Apply throttle.
    # I should apply a throttle here, but the template uses redis, and I'm not planning on having that...

    # Send email.
    msg = Message(subject=subject, recipients=current_app.config['ADMINS'], html=html)
    mail.send(msg)


def send_email(subject, body=None, html=None, recipients=None, attachments=None, bcc=None):
    """Send an email.

    Positional arguments:
    subject -- the subject line of the email.

    Keyword arguments.
    body -- the body of the email (no HTML).
    html -- the body of the email, can be HTML (overrides body).
    recipients -- list or set (not string) of email addresses to send the email to. Defaults to the ADMINS list in the
        Flask config.
    attachments -- list of attachments to add to the email. Must include filename, mimetype and data.
    """
    recipients = recipients or current_app.config['ADMINS']

    msg = Message(subject=subject, recipients=recipients, body=body, html=html, bcc=bcc)

    if attachments is not None:
        for at in attachments:
            msg.attach(at["filename"], at["mimetype"], at["data"])

    mail.send(msg)
