import os
import time
import flask
import threading
import traceback
import subprocess

import db
import log
import utils
import agents
import catcher
import settings

MERGE_ALL = False

# Helper functions
def start_traffic_collection(agent):
    if agent["os"] == "Windows":
        pass
    else:
        try:
            log.log("Starting traffic collection on agent " + agent["ip"])
            # Connect to agent over SSH
            ssh = agents.connect(agent)
            # Get proxy IP
            proxy_ip = agents.run_cmd(agent, "echo $SSH_CLIENT", ssh).split(" ")[0]

            # Install requirements
            requirements = utils.read_file_contents(os.path.join(settings.AGENTS_DIR, "init", "traffic", "unix", "requirements.txt")).split("\n")
            agents.install_requirements(agent, requirements, ssh)
            
            # Upload traffic collection script
            agents.upload(agent, os.path.join(settings.AGENTS_DIR, "init", "traffic", "unix", "start-traffic.sh"), "/tmp/start-traffic.sh", ssh)

            # Start traffic collection
            agents.run_cmd(agent, "chmod +x /tmp/start-traffic.sh", ssh)
            agents.run_cmd(agent, "/tmp/start-traffic.sh " + proxy_ip + " " + str(agent["port"]), ssh, sudo=True)

            ssh.close()
        except Exception as e:
            log.log("Error: " + traceback.format_exc())

def stop_traffic_collection(agent):
    if agent["os"] == "Windows":
        pass
    else:
        ssh = agents.connect(agent)
        agents.upload(agent, os.path.join(settings.AGENTS_DIR, "init", "traffic", "unix", "stop-traffic.sh"), "/tmp/stop-traffic.sh", ssh)
        agents.run_cmd(agent, "chmod +x /tmp/stop-traffic.sh", ssh)
        agents.run_cmd(agent, "/tmp/stop-traffic.sh", ssh, sudo=True)
        agents.run_cmd(agent, "rm -f /tmp/stop-traffic.sh", ssh, sudo=True)
        ssh.close()



# Frontend views


# Backend functions
def start_capture():
    ip = flask.request.args.get("ip")
    
    if ip not in db.data["agents"]:
        return flask.render_template("agents/index.html", messages = ["Erorr: Agent not found"])
    
    agent = db.data["agents"][ip]
    t = threading.Thread(target = start_traffic_collection, args = (agent,))
    t.start()

    db.data["agents"][ip]["capture"] = 1
    db.data["agents"][ip]["status"] = "Capturing traffic"

    agents = db.data["agents"]

    return flask.redirect("/agents?message=Traffic capture started")

def stop_capture():
    ip = flask.request.args.get("ip")
    
    if ip not in db.data["agents"]:
        return flask.render_template("agents/index.html", messages = ["Erorr: Agent not found"])
    
    agent = db.data["agents"][ip]
    t = threading.Thread(target = stop_traffic_collection, args = (agent,))
    t.start()

    db.data["agents"][ip]["capture"] = 0
    db.data["agents"][ip]["status"] = "Idle"

    agents = db.data["agents"]

    return flask.redirect("/agents?message=Traffic capture stopped")


# Thread functions
def traffic_loop():
    global MERGE_ALL
    # Start arkime capture if installed
    if os.path.exists("/opt/arkime/bin/capture"):
        subprocess.Popen(['sudo', '/opt/arkime/bin/capture', '-r', settings.TRAFFIC_DIR, '-m'])
    while True:
        # Pull traffic from all agents
        for agent in db.data["agents"].values():
            try:
                if agent["capture"] > 0:
                    if agent["os"] == "Windows":
                        pass
                    else:
                        # Connect to agent over SSH
                        ssh = agents.connect(agent)
                        # Get current timestamp in seconds
                        timestamp = int(time.time())
                        # Download traffic file
                        agents.download(agent, "/tmp/traffic.pcap.gz", os.path.join(settings.TRAFFIC_DIR, agent["ip"] + "_" + str(timestamp) + ".pcap.gz"), ssh)
                        # Close SSH connection
                        ssh.close()
                        # Unzip traffic file
                        os.system("gunzip -f " + os.path.join(settings.TRAFFIC_DIR, agent["ip"] + "_" + str(timestamp) + ".pcap.gz"))
                        # Catch flags in traffic file
                        catcher.catch(os.path.join(settings.TRAFFIC_DIR, agent["ip"] + "_" + str(timestamp) + ".pcap"))
                        # Merge traffic file with existing traffic file
                        if MERGE_ALL:
                            if not os.path.exists(os.path.join(settings.TRAFFIC_DIR, "traffic.pcap")):
                                # If the traffic file doesn't exist, just copy the new traffic file
                                os.system("mv " + os.path.join(settings.TRAFFIC_DIR, agent["ip"] + "_" + str(timestamp) + + ".pcap") + " " + os.path.join(settings.TRAFFIC_DIR, "traffic.pcap"))
                            else:
                                # If the traffic file exists, merge the new traffic file with the existing traffic file
                                # Copy the existing traffic file to the new traffic file
                                os.system("mergecap -w " + os.path.join(settings.TRAFFIC_DIR, "traffic.pcap.tmp") + " " + os.path.join(settings.TRAFFIC_DIR, "traffic.pcap") + " " + os.path.join(settings.TRAFFIC_DIR, agent["ip"] + "_" + str(timestamp) + ".pcap"))
                                # Overwrite the existing traffic file with the new traffic file
                                os.system("mv -f " + os.path.join(settings.TRAFFIC_DIR, "traffic.pcap.tmp") + " " + os.path.join(settings.TRAFFIC_DIR, "traffic.pcap"))
                                # Delete the old traffic file
                                os.system("rm -f " + os.path.join(settings.TRAFFIC_DIR, agent["ip"] + "_" + str(timestamp) + ".pcap"))
            except Exception as e:
                log.log("Error: " + traceback.format_exc())
        # Sleep for n seconds as defined in settings
        time.sleep(settings.TRAFFIC_FREQUENCY)


# Traffic thread
traffic_thread = threading.Thread(target=traffic_loop)