import os
import flask

import db
import settings

# Helper functions
def get_submitter_templates():
    return os.listdir(settings.SUBMITTER_TEMPLATES_DIR)

def get_submitter_template_contents(template):
    with open(os.path.join(settings.SUBMITTER_TEMPLATES_DIR, template), "r") as f:
        return f.read()

def get_submitter_contents():
    with open(settings.SUBMITTER_FILE, "r") as f:
        return f.read()

def submit_flag(flag):
    os.system("chmod +x " + settings.SUBMITTER_FILE)
    result = os.system(settings.SUBMITTER_FILE + " " + flag)
    db.data["submissions"].append(result)


# Frontend views
def view_submitter():
    template = flask.request.args.get("template")
    code = ""
    rate = db.data["settings"]["submitrate"]
    correctregex = db.data["settings"]["correctregex"]
    incorrectregex = db.data["settings"]["incorrectregex"]
    if template:
        code = get_submitter_template_contents(template)
    else:
        code = get_submitter_contents()
    templates = get_submitter_templates()
    return flask.render_template("submitter.html",
                templates = templates,
                code = code,
                rate = rate,
                correctregex = correctregex,
                incorrectregex = incorrectregex
            )


# Backend functions
def update_submitter():
    code = flask.request.form.get("code")
    db.data["settings"]["submitrate"] = int(flask.request.form.get("rate"))
    db.data["settings"]["correctregex"] = flask.request.form.get("correctregex")
    db.data["settings"]["incorrectregex"] = flask.request.form.get("incorrectregex")

    with open(settings.SUBMITTER_FILE, "w", newline='\n') as f:
        code = code.replace('\r', '')
        f.write(code)

    return flask.render_template("submitter.html",
            templates = get_submitter_templates(),
            code = code,
            rate = db.data["settings"]["submitrate"],
            correctregex = db.data["settings"]["correctregex"],
            incorrectregex = db.data["settings"]["incorrectregex"],
            messages = ["Submitter saved"]
        )



# Thread functions