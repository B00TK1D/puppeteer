import os
import flask

import settings


rate = settings.SUBMITTER_DEFAULT_RATE

responses = []


# Helper functions
def get_submitter_templates():
    return os.listdir(settings.SUBMITTER_TEMPLATES_DIR)

def get_submitter_template_contents(template):
    with open(os.path.join(settings.SUBMITTER_TEMPLATES_DIR, template), "r") as f:
        return f.read()

def get_submitter_contents():
    with open(settings.SUBMITTER_FILE, "r") as f:
        return f.read()


# Frontend views
def view_submitter():
    template = flask.request.args.get("template")
    code = ""
    if template:
        code = get_submitter_template_contents(template)
    else:
        code = get_submitter_contents()
    templates = get_submitter_templates()
    return flask.render_template("submitter.html", templates = templates, code = code, rate = rate)


# Backend functions
def update_submitter():
    global rate
    code = flask.request.form.get("code")
    rate = int(flask.request.form.get("rate"))

    with open(settings.SUBMITTER_FILE, "w") as f:
        f.write(code)

    return flask.render_template("submitter.html", templates = get_submitter_templates(), code = code, rate = rate, messages = ["Submitter saved"])



# Thread functions