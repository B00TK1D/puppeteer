import os
import flask
import psutil
import subprocess

import utils
import settings

connect_p = None

# Helper functions
def get_status():
    # List interfaces
    addrs = psutil.net_if_addrs()
    # List processes
    procs = [p for p in psutil.process_iter()]
    # Filter processes for openvpn
    openvpn_procs = list(filter(lambda x: 'openvpn' in x.name(), procs))
    if "tun0" in addrs:
        if len(openvpn_procs) > 0:
            return "Connected"
        else:
            return "Stale connection"
    else:
        if len(openvpn_procs) > 0:
            return "Connecting..."
    return "Disconnected"

# Frontend views
def view_vpn():
    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))
    status = get_status()
    messages = [flask.request.args.get("message")]
    if messages[0] == None:
        messages = []
    return flask.render_template("vpn/index.html", code = code, status = status, messages = messages)

def view_modify_vpn():
    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))
    status = get_status()
    messages = [flask.request.args.get("message")]
    if messages[0] == None:
        messages = []
    return flask.render_template("vpn/modify.html", code = code, status = status, messages = messages)


# Backend functions
def connect_vpn():
    global connect_p
    os.system("chmod +x " + settings.VPN_CONNECT_FILE)
    connect_p = subprocess.Popen(['sudo', settings.VPN_CONNECT_FILE])

    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))

    return flask.redirect("/vpn?message=Connecting...")


def disconnect_vpn():
    global connect_p
    connect_p.kill()
    # Kill all openvpn processes
    os.system("sudo pkill openvpn")

    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))

    return flask.render_template("vpn/index.html", code = code, messages = ["VPN disconnected"])


def update_vpn():
    code = flask.request.form.get("code")

    if "file" in flask.request.files:
        file = flask.request.files["file"]
        file.save(settings.VPN_CONFIG_FILE)
    utils.write_file_contents(os.path.join(settings.VPN_CONNECT_FILE), code)

    return flask.redirect("/vpn/modify?message=VPN+updated")