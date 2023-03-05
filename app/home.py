import flask

import db
import update
import targets
import submitter

def view_home():
    return flask.render_template(
        "index.html",
        total_targets = len(targets.list_targets()),
        total_teams = len(db.data["teams"]),
        total_services = len(db.data["services"]),
        total_exploits = len(db.data["exploits"]),
        total_found = submitter.total_found,
        total_submitted = submitter.total_submitted,
        update_status = update.update_status
    )


def reset_counters():
    for id in db.data["exploits"]:
        db.data["exploits"][id]["flags_captured"] = 0
        db.data["exploits"][id]["services_vulnerable"] = 0

    for id in db.data["services"]:
        db.data["services"][id]["flags_captured"] = 0
    
    for id in db.data["teams"]:
        db.data["teams"][id]["flags_captured"] = 0

    submitter.total_found = 0
    submitter.total_submitted = 0

    return flask.redirect("/")