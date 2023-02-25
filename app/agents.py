import re
import flask
import paramiko
import threading

import db

# Helper functions
def init_agent(agent):
    print("Initializing agent on " + agent["ip"] + "...")
    # SSH into agent and run init script
    # Launch SSH connection
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(agent["ip"], agent["port"], agent["user"], agent["password"])
        # Run init script
        stdin, stdout, stderr = ssh.exec_command("hostname")
        # Get hostname
        agent["hostname"] = stdout.read().decode("utf-8").strip()
        # Get OS
        stdin, stdout, stderr = ssh.exec_command("uname")
        if (len(stderr.read().decode("utf-8").strip()) > 0):
            agent["os"] = "Unknown"
        else:
            agent["os"] = stdout.read().decode("utf-8").strip()
        # Close SSH connection
        ssh.close()
        db.data["agents"][agent["ip"]]["status"] = "Initialized"
    except:
        db.data["agents"][agent["ip"]]["status"] = "Failed to initialize"



# Frontend views
def view_agents():
    agents = db.data["agents"]
    return flask.render_template("agents/index.html", agents = agents)


# Backend functions
def create_agent():
    ip = flask.request.form.get("ip")
    port = int(flask.request.form.get("port"))
    user = flask.request.form.get("user")
    password = flask.request.form.get("password")

    # Extract IP address regex from ip field
    ip_regex = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    ips = re.findall(ip_regex, ip)

    if len(ips) == 0:
        agents = db.data["agents"]
        return flask.render_template("agents/index.html", agents = agents, messages = ["Invalid IP address"])
    
    ip = ips[0]


    if ip in db.data["agents"]:
        agents = db.data["agents"]
        return flask.render_template("agents/index.html", agents = agents, messages = ["Agent " + str(ip) + " already exists"])
    
    agent = {
        "ip": ip,
        "port": port,
        "user": user,
        "password": password,
        "hostname": "",
        "os": "",
        "status": "Pending initialization..."
    }

    db.data["agents"][ip] = agent

    # Start thread to initialize agent seperate from current thread
    init_thread = threading.Thread(target = init_agent, args = (agent,))
    init_thread.start()


    agents = db.data["agents"]

    return flask.render_template("agents/index.html", agents = agents, messages = ["Agent on " + str(ip) + " added"])


def update_agent():
    ip = flask.request.form.get("ip")
    newip = flask.request.form.get("newip")
    port = int(flask.request.form.get("port"))
    user = flask.request.form.get("user")
    password = flask.request.form.get("password")
    
    if newip != ip and newip in db.data["agents"]:
        agents = db.data["agents"]
        return flask.render_template("agents/index.html", agents = agents, messages = ["Agent on " + str(newip) + " already exists"])

    try:
        agent = db.data["agents"][ip]

        agent["ip"] = newip
        agent["port"] = port
        agent["user"] = user
        agent["password"] = password

        del db.data["agents"][ip]
        db.data["agents"][newip] = agent
    except:
        return flask.render_template("agents/index.html", agents = db.data["agents"], messages = ["Agent on " + str(ip) + " does not exist"])

    agents = db.data["agents"]

    return flask.render_template("agents/index.html", agents = agents, messages = ["Agent on " + str(ip) + " updated"])



def delete_agent():
    ip = flask.request.args.get("ip")

    try:
        del db.data["agents"][ip]
    except:
        return flask.render_template("agents/index.html", agents = db.data["agents"], messages = ["Agent on " + str(ip) + " does not exist"])

    agents = db.data["agents"]

    return flask.render_template("agents/index.html", agents = agents, messages = ["Agent on " + str(ip) + " deleted"])



# Thread functions