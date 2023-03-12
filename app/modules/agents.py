import os
import re
import flask
import psutil
import paramiko
import traceback
import threading

from modules import db
from modules import log
from modules import utils
from modules import settings


package_managers = {
    "Linux": {
        "install": "apt-get install -y",
        "update": "apt-get update -y"
    },
    "CentOS": {
        "install": "yum install -y",
        "update": "yum update -y"
    }
}

# Helper functions
def connect(agent):
    # Connect to agent
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(agent["ip"], agent["port"], agent["user"], agent["password"])
        return ssh
    except:
        log.log("Error: " + traceback.format_exc())
        db["agents"][agent["ip"]]["status_code"] = -1
        return None

def run_cmd(agent, cmd, ssh=None, sudo=False, nohup=False):
    new = False
    if not ssh:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(agent["ip"], agent["port"], agent["user"], agent["password"])
        new = True
    if nohup:
        channel = ssh.get_transport().open_session()
        ssh = channel
    if sudo and agent["admin"]:
        stdin, stdout, stderr = ssh.exec_command("sudo -S " + cmd)
        stdin.write(agent["password"] + "\n")
        stdin.flush()
    else:
        stdin, stdout, stderr = ssh.exec_command(cmd)
    err = stderr.read().decode("utf-8").strip()
    if len(err) > 0:
        log.log("Error while executing " + cmd + " on " + agent["ip"] + ": " + err)
    if new:
        ssh.close()
    return stdout.read().decode("utf-8").strip()

def install_requirements(agent, requirements, ssh=None):
    if agent["os"] not in package_managers:
        return -1
    if agent["admin"] == 0:
        return -1
    package_manager = package_managers[agent["os"]]
    new = False
    if not ssh:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(agent["ip"], agent["port"], agent["user"], agent["password"])
        new = True
    # Check if requirements are installed
    unmet = []
    for requirement in requirements:
        if run_cmd(agent, "which " + requirement, ssh) == "":
            unmet.append(requirement)
    if unmet:
        # Get proxy IP
        proxy_ip = run_cmd(agent, "echo $SSH_CLIENT", ssh).split(" ")[0]
        # Set proxy
        run_cmd(agent, "set http_proxy=http://" + proxy_ip + ":3128", ssh)
        run_cmd(agent, "set https_proxy=http://" + proxy_ip + ":3128", ssh)
        # Update and install requirements
        run_cmd(agent, package_manager["update"], ssh, sudo=True)
        for u in unmet:
            run_cmd(agent, package_manager["install"] + " " + u, ssh, sudo=True)
        run_cmd(agent, "unset http_proxy", ssh)
        run_cmd(agent, "unset https_proxy", ssh)
    if new:
        ssh.close()

def upload(agent, local_path, remote_path, ssh=None):
    new = False
    if not ssh:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(agent["ip"], agent["port"], agent["user"], agent["password"])
        new = True
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    if new:
        ssh.close()

def download(agent, remote_path, local_path, ssh=None):
    new = False
    if not ssh:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(agent["ip"], agent["port"], agent["user"], agent["password"])
        new = True
    sftp = ssh.open_sftp()
    sftp.get(remote_path, local_path)
    sftp.close()
    if new:
        ssh.close()

def init_agent(agent):
    print("Initializing agent on " + agent["ip"] + "...")
    # SSH into agent and run init script
    # Launch SSH connection
    try:
        ssh = connect(agent)
        agent["hostname"] = run_cmd(agent, "hostname", ssh)
        # Get OS
        os_name = run_cmd(agent, "uname", ssh)
        if (len(os_name) == 0):
            agent["os"] = "Windows"
        else:
            agent["os"] = os_name
        # Run init script
        if agent["os"] == "Windows":
            # SCP init script to agent
            sftp = ssh.open_sftp()
            sftp.put(os.path.join(settings.AGENTS_DIR, "init", "windows.ps1"), "C:\\Users\\" + agent["user"] + "\\AppData\\Local\\Temp\\init.ps1")
            sftp.close()
            # Run init script
            run_cmd(agent, "powershell -ExecutionPolicy Bypass -File C:\\Users\\" + agent["user"] + "\\AppData\\Local\\Temp\\init.ps1 && del C:\\Users\\" + agent["user"] + "\\AppData\\Local\\Temp\\init.ps1", ssh)
            # Close SSH connection
            ssh.close()
        else:
            # SCP init script to agent
            sftp = ssh.open_sftp()
            sftp.put(os.path.join(settings.AGENTS_DIR, "init", "unix.sh"), "/tmp/init.sh")
            sftp.close()
            # Check for sudo access
            groups = run_cmd(agent, "groups", ssh)
            if "sudo" in groups:
                db.data["agents"][agent["ip"]]["admin"] = 1
                # Run init script with sudo
                run_cmd(agent, "chmod +x /tmp/init.sh", ssh)
                run_cmd(agent, "/tmp/init.sh && rm /tmp/init.sh", ssh, sudo=True)
            else:
                db.data["agents"][agent["ip"]]["admin"] = 0
                run_cmd(agent, "chmod +x /tmp/init.sh && sudo /tmp/init.sh && rm /tmp/init.sh", ssh)
            # Close SSH connection
            ssh.close()
        db.data["agents"][agent["ip"]]["status"] = "Initialized"
        db.data["agents"][agent["ip"]]["status_code"] = 1
    except Exception as e:
        db.data["agents"][agent["ip"]]["status"] = "Failed to initialize: " + traceback.format_exc()

def get_status():
    addrs = psutil.net_if_addrs()
    if "tun0" in addrs:
        return "Connected"
    return "Disconnected"

# Frontend views
def view_agents():
    messages = [flask.request.args.get("message")]
    if messages[0] == None:
        messages = []
    agents = db.data["agents"]
    return flask.render_template("agents/index.html", agents = agents, messages = messages)

def view_agent_init():
    unix = utils.read_file_contents(os.path.join(settings.AGENTS_DIR, "init", "unix.sh"))
    windows = utils.read_file_contents(os.path.join(settings.AGENTS_DIR, "init", "windows.ps1"))
    return flask.render_template("agents/init.html", unix = unix, windows = windows)

def view_new_agent():
    return flask.render_template("agents/new.html")

# Backend functions
def create_agent():
    ip = flask.request.form.get("ip")
    port = int(flask.request.form.get("port"))
    user = flask.request.form.get("thing1")
    password = flask.request.form.get("thing2")

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
        "status": "Pending initialization...",
        "status_code": 0,
        "admin": 0,
        "capture": 0
    }

    db.data["agents"][ip] = agent

    # Start thread to initialize agent seperate from current thread
    init_thread = threading.Thread(target = init_agent, args = (agent,))
    init_thread.start()


    agents = db.data["agents"]

    return flask.redirect("/agents?message=" + "Agent on " + str(ip) + " added")

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

    return flask.redirect("/agents?message=" + "Agent on " + str(ip) + " updated")

def delete_agent():
    ip = flask.request.args.get("ip")

    try:
        del db.data["agents"][ip]
    except:
        return flask.render_template("agents/index.html", agents = db.data["agents"], messages = ["Agent on " + str(ip) + " does not exist"])

    agents = db.data["agents"]

    return flask.redirect("/agents?message=" + "Agent on " + str(ip) + " deleted")

def update_agent_init():
    unix = flask.request.form.get("unix")
    windows = flask.request.form.get("windows")
    utils.write_file_contents(os.path.join(settings.AGENTS_DIR, "init", "unix.sh"), unix)
    utils.write_file_contents(os.path.join(settings.AGENTS_DIR, "init", "windows.ps1"), windows)
    

    return flask.render_template("agents/init.html", unix = unix, windows = windows, messages = ["Agent init scripts saved"])


# Thread functions
