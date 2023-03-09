import os
import flask
import psutil
import subprocess

import utils
import settings

connect_p = None

list(filter(lambda x: 'Chrome' in x.name, [p for p in psutil.process_iter()]))

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
    return flask.render_template("vpn.html", code = code, status = status)


# Backend functions
def connect_vpn():
    global connect_p
    os.system("chmod +x " + settings.VPN_CONNECT_FILE)
    connect_p = subprocess.Popen(['sudo', settings.VPN_CONNECT_FILE])

    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))

    return flask.render_template("vpn.html", code = code, messages = ["VPN connected"])


def disconnect_vpn():
    global connect_p
    connect_p.kill()

    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))

    return flask.render_template("vpn.html", code = code, messages = ["VPN disconnected"])


def update_vpn():
    code = flask.request.form.get("code")

    if "file" in flask.request.files:
        file = flask.request.files["file"]

        file.save(settings.VPN_CONFIG_FILE)

        print("Saved vpn file")

    utils.write_file_contents(os.path.join(settings.VPN_CONNECT_FILE), code)

    return flask.render_template("vpn.html", code = code, messages = ["VPN updated"])