import flask
from flask_bootstrap import Bootstrap4

import home
import teams
import agents
import targets
import traffic
import exploits
import services
import submitter
import flagformat



# Initialize flask
app = flask.Flask(__name__)
Bootstrap4(app)


def run():
    global app
    # Run the app
    app.run(port=8088, host="0.0.0.0", debug=True, use_evalex=False)



####################
# Frontend Routes
####################

### Exploit Routes ###
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

@app.route("/submitter/log", methods=["GET"])
def route_submitter_log():
    return submitter.view_submit_log()


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

### Agent Routes ###
@app.route("/agents", methods=["GET"])
def route_agents():
    return agents.view_agents()

@app.route("/agents/init", methods=["GET"])
def route_init_agent():
    return agents.view_agent_init()

@app.route("/agents/new", methods=["GET"])
def route_new_agent():
    return agents.view_new_agent()

### Dashboard Routes ###
@app.route("/", methods=["GET"])
def route_home():
    return home.view_home()



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
    return exploits.trigger_run_exploit()


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

### Agent API ###
@app.route("/api/agents/create", methods=["POST"])
def route_create_agent():
    return agents.create_agent()

@app.route("/api/agents/update", methods=["POST"])
def route_update_agent():
    return agents.update_agent()

@app.route("/api/agents/delete", methods=["GET"])
def route_delete_agent():
    return agents.delete_agent()

@app.route("/api/agents/init/update", methods=["POST"])
def route_update_agent_init():
    return agents.update_agent_init()

### Traffic API ###
@app.route("/api/traffic/start", methods=["GET"])
def route_start_traffic():
    return traffic.start_capture()

@app.route("/api/traffic/stop", methods=["GET"])
def route_stop_traffic():
    return traffic.stop_capture()

### Dashboard API ###
@app.route("/api/counters/reset", methods=["GET"])
def route_reset_counters():
    return home.reset_counters()