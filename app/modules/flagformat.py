import re
import flask

from modules import db

# Helper functions
def extract_flags(text):
    regex = re.compile(db.data["settings"]["flagformat"])
    return re.findall(regex, text)


def extract_flags_bytes(text):
    regex = re.compile(db.data["settings"]["flagformat"].encode("utf-8"))
    return re.findall(regex, text)



# Frontend views
def view_flag_format():
    return flask.render_template("flagformat.html", regex = db.data["settings"]["flagformat"])


# Backend functions
def update_flag_format():
    db.data["settings"]["flagformat"] = flask.request.form.get("regex")

    return flask.render_template("flagformat.html", regex =  db.data["settings"]["flagformat"], messages = ["Flag format saved"])



# Thread functions