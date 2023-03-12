import flask

from modules import db


# Helper functions
def sort_services():
    services = db.data["services"]
    db.data["services"] = dict(sorted(services.items()))

def service_from_ip(ip):
    services = db.data["services"]
    target_format = db.data["settings"]["targetformat"]
    for i in range(255):
        team = target_format.replace("T", str(i))
        for service in services.values():
            test = team.replace("S", service["id"])
            if test == ip:
                return service["id"]
    return None


# Frontend views
def view_services():
    services = db.data["services"]
    return flask.render_template("services.html", services = services)


# Backend functions
def create_service():
    id = str(flask.request.form.get("id"))
    name = flask.request.form.get("name")
    notes = flask.request.form.get("notes")

    if id in db.data["services"]:
        services = db.data["services"]
        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " already exists"])

    service = {
        "id": id,
        "name": name,
        "notes": notes,
        "flags_captured": 0
    }

    db.data["services"][id] = service

    sort_services()

    services = db.data["services"]

    print(services)

    return flask.render_template("services.html", services = services, messages = ["Service " + name + " created"])

def update_service():
    id = str(flask.request.form.get("id"))
    newid = str(flask.request.form.get("newid"))
    name = str(flask.request.form.get("name"))
    notes = str(flask.request.form.get("notes"))
    
    if newid != id and newid in db.data["services"]:
        services = db.data["services"]
        return flask.render_template("services.html", services = services, messages = ["Service " + str(newid) + " already exists"])

    try:
        service = db.data["services"][id]

        service["id"] = newid
        service["name"] = name
        service["notes"] = notes

        del db.data["services"][id]
        db.data["services"][newid] = service

        sort_services()

        services = db.data["services"]

        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " updated"])

    except KeyError:
        services = db.data["services"]
        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " does not exist"])

def delete_service():
    id = str(flask.request.args.get("id"))

    try:
        del db.data["services"][id]
        services = db.data["services"]

        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " deleted"])
    except KeyError:
        services = db.data["services"]
        return flask.render_template("services.html", services = services, messages = ["Service " + str(id) + " does not exist"])



# Thread functions