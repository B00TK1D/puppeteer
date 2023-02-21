import flask

import db
import submitter
import targets

def view_home():
    return flask.render_template(
        "index.html",
        total_targets = len(targets.list_targets()),
        total_teams = len(db.data["teams"]),
        total_services = len(db.data["services"]),
        total_exploits = len(db.data["exploits"]),
        total_found = submitter.total_found,
        total_submitted = submitter.total_submitted,
    )