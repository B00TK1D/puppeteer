import flask


import db

# Helper functions
def list_targets():
    format = db.data["settings"]["targetformat"]
    targets = {}
    for team in db.data["teams"].values():
        for service in db.data["services"].values():
            ip = format.replace("T", str(team["id"])).replace("S", str(service["id"]))
            target = {
                "team": team["name"],
                "teamid": str(team["id"]),
                "service": service["name"],
                "serviceid": str(service["id"]),
                "ip": ip
            }
            targets[ip] = target
    return targets

def list_service_targets(service_id):
    format = db.data["settings"]["targetformat"]
    targets = {}
    for team in db.data["teams"].values():
        try:
            service = db.data["services"][service_id]
        except KeyError:
            return {}
        ip = format.replace("T", str(team["id"])).replace("S", str(service["id"]))
        target = {
            "team": team["name"],
            "teamid": str(team["id"]),
            "service": service["name"],
            "serviceid": str(service["id"]),
            "ip": ip
        }
        targets[ip] = target
    return targets


# Frontend views
def view_targets():
    format = db.data["settings"]["targetformat"]
    return flask.render_template("targets.html", targets = list_targets(), format = format)


# Backend functions
def update_targets():
    db.data["settings"]["targetformat"] = flask.request.form.get("format")

    return flask.render_template("targets.html", targets = list_targets(), format = format, messages = ["Targets updated"])