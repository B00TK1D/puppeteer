import flask

import db


# Helper functions


# Frontend views
def view_teams():
    teams = db.data["teams"]
    return flask.render_template("teams.html", teams = teams)

def sort_teams():
    teams = db.data["teams"]
    db.data["teams"] = dict(sorted(teams.items()))


# Backend functions
def create_team():
    id = flask.request.form.get("id")
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

    sort_teams()

    teams = db.data["teams"]

    print(teams)

    return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " created"])

def update_team():
    id = flask.request.form.get("id")
    newid = flask.request.form.get("newid")
    name = str(flask.request.form.get("name"))
    
    if newid != id and newid in db.data["teams"]:
        teams = db.data["teams"]
        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(newid) + " already exists"])

    try:
        team = db.data["teams"][id]

        team["id"] = newid
        team["name"] = name

        del db.data["teams"][id]
        db.data["teams"][newid] = team

        sort_teams()
        teams = db.data["teams"]

        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " updated"])

    except KeyError:
        teams = db.data["teams"]
        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " does not exist"])

def delete_team():
    id = flask.request.args.get("id")

    try:
        del db.data["teams"][id]
        teams = db.data["teams"]

        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " deleted"])
    except KeyError:
        teams = db.data["teams"]
        return flask.render_template("teams.html", teams = teams, messages = ["Team " + str(id) + " does not exist"])



# Thread functions