import flask
from flask_bootstrap import Bootstrap4

import db
import teams
import targets
import exploits
import services
import submitter
import flagformat

# Initialize flask
app = flask.Flask(__name__)
Bootstrap4(app)



def main():
    # Initialize the database
    db.init()

    db.load()

    # Start backup thread
    db.backup_thread.start()

    # Load the exploits
    exploits.load_exploits()

    # Run the app
    app.run(port=8088)


####################
# Frontend Routes
####################

### Exploit Routes ###
@app.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html")

@app.route("/exploits", methods=["GET"])
def route_exploits():
    return exploits.view_exploits()

@app.route("/exploits/archived", methods=["GET"])
def route_archived_exploits():
    return exploits.view_archived_exploits()

@app.route("/exploits/new", methods=["GET"])
def route_new_exploit():
    return exploits.view_new_exploit()

@app.route("/exploits/modify", methods=["GET"])
def route_modify_exploit():
    return exploits.view_modify_exploit()

@app.route("/exploits/log", methods=["GET"])
def route_exploit_log():
    return exploits.view_exploit_log()

@app.route("/exploits/details", methods=["GET"])
def route_exploit_log_details():
    return exploits.view_exploit_log_details()


### Submitter Routes ###
@app.route("/submitter", methods=["GET"])
def route_submitter():
    return submitter.view_submitter()


### Flag Format Routes ###
@app.route("/flagformat", methods=["GET"])
def route_flag_format():
    return flagformat.view_flag_format()

### Team Routes ###
@app.route("/teams", methods=["GET"])
def route_teams():
    return teams.view_teams()

### Service Routes ###
@app.route("/services", methods=["GET"])
def route_services():
    return services.view_services()

### Target Routes ###
@app.route("/targets", methods=["GET"])
def route_targets():
    return targets.view_targets()



####################
# API Routes
####################

### Exploit API ###
@app.route("/api/exploits/create", methods=["POST"])
def route_create_exploit():
    return exploits.create_exploit()

@app.route("/api/exploits/update", methods=["POST"])
def route_update_exploit():
    return exploits.update_exploit()

@app.route("/api/exploits/archive", methods=["GET"])
def route_archive_exploit():
    return exploits.archive_exploit()

@app.route("/api/exploits/unarchive", methods=["GET"])
def route_unarchive_exploit():
    return exploits.unarchive_exploit()

@app.route("/api/exploits/delete", methods=["GET"])
def route_delete_exploit():
    return exploits.delete_exploit()

@app.route("/api/exploits/run", methods=["GET"])
def route_run_exploit():
    return exploits.run_exploit()


### Submitter API ###
@app.route("/api/submitter/update", methods=["POST"])
def route_update_submitter():
    return submitter.update_submitter()


### Flag Format API ###
@app.route("/api/flagformat/update", methods=["POST"])
def route_update_flag_format():
    return flagformat.update_flag_format()

### Team API ###
@app.route("/api/teams/create", methods=["POST"])
def route_create_team():
    return teams.create_team()

@app.route("/api/teams/update", methods=["POST"])
def route_update_team():
    return teams.update_team()

@app.route("/api/teams/delete", methods=["GET"])
def route_delete_team():
    return teams.delete_team()

### Service API ###
@app.route("/api/services/create", methods=["POST"])
def route_create_service():
    return services.create_service()

@app.route("/api/services/update", methods=["POST"])
def route_update_service():
    return services.update_service()

@app.route("/api/services/delete", methods=["GET"])
def route_delete_service():
    return services.delete_service()

### Target API ###
@app.route("/api/targets/update", methods=["POST"])
def route_update_target():
    return targets.update_targets()


if __name__ == "__main__":
    main()

