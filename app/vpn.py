import os
import flask
import subprocess
import threading

import db
import utils
import settings

connect_p = None

# Frontend views
def view_vpn():
    code = utils.read_file_contents(os.path.join(settings.VPN_CONNECT_FILE))
    return flask.render_template("vpn.html", code = code)


# Backend functions
def connect_vpn():
    global connect_p
    os.system("chmod +x " + settings.VPN_CONNECT_FILE)
    connect_p = subprocess.Popen([settings.VPN_CONNECT_FILE])

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