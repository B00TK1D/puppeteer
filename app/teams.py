import flask

import db


# Helper functions


# Frontend views
def view_teams():
    teams = db.data["teams"]
    return flask.render_template("teams.html", teams = teams)


# Backend functions
def create_team():
    id = int(flask.request.form.get("id"))
    name = flask.request.form.get("name")

    if id in db.data["teams"]:
        teams = db.data["teams"]
        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " already exists"])

    team = {
        "id": id,
        "name": name,
        "flags_collected": 0
    }

    db.data["teams"][id] = team
    teams = db.data["teams"]

    print(teams)

    return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " created"])

def update_team():
    id = int(flask.request.form.get("id"))
    name = str(flask.request.form.get("name"))
    
    try:
        db.data["teams"][id]["name"] = name
        teams = db.data["teams"]

        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " updated"])
    except KeyError:
        teams = db.data["teams"]
        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " does not exist"])

def delete_team():
    id = int(flask.request.args.get("id"))

    try:
        del db.data["teams"][id]
        teams = db.data["teams"]

        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " deleted"])
    except KeyError:
        teams = db.data["teams"]
        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " does not exist"])



# Thread functions