import re
import flask

import settings


regex = re.compile(settings.FLAGFORMAT_DEFAULT_REGEX)

# Helper functions
def extract_flags(text):
    return re.findall(regex, text)


# Frontend views
def view_flag_format():
    return flask.render_template("flagformat.html", regex = regex.pattern)


# Backend functions
def update_flag_format():
    global regex
    regex = re.compile(flask.request.form.get("regex"))

    return flask.render_template("flagformat.html", regex = regex.pattern, messages = ["Flag format saved"])



# Thread functions