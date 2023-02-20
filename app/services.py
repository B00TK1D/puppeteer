import flask

import db


# Helper functions


# Frontend views
def view_services():
    services = db.data["services"]
    return flask.render_template("services.html", services = services)


# Backend functions
def create_service():
    name = flask.request.form.get("name")
    notes = flask.request.form.get("notes")

    id = next(iter(db.data["services"]), 0)
    service = {
        "id": id,
        "name": name,
        "notes": notes,
        "flags_collected": 0
    }

    db.data["services"][id] = service
    services = db.data["services"]

    print(services)

    return flask.render_template("services.html", services = services, messages = ["Service " + name + " created"])

def update_service():
    id = int(flask.request.form.get("id"))
    name = str(flask.request.form.get("name"))
    notes = str(flask.request.form.get("notes"))
    
    try:
        db.data["services"][id]["name"] = name
        db.data["services"][id]["notes"] = notes
        services = db.data["services"]

        return flask.render_template("services.html", services = services, messages = ["Service " + name + " updated"])
    except KeyError:
        services = db.data["services"]
        return flask.render_template("services.html", services = services, messages = ["Service " + int(id) + " does not exist"])

def delete_service():
    id = int(flask.request.args.get("id"))

    try:
        del db.data["services"][id]
        services = db.data["services"]

        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " deleted"])
    except KeyError:
        services = db.data["services"]
        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " does not exist"])



# Thread functions