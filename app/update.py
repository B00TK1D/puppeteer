import os
import flask

import db

# Helper functions
def run_update():
    # Save current state
    db.save()
    # Stop backup thread
    db.pause()
    # Update the system
    pid = os.getpid()
    os.system("git pull")
    os.system("sudo pip3 install -r ../deploy/docker/requirements.txt")
    os.system("echo \"#!/bin/sh\nsudo kill -9 " + str(pid) + "\nsleep 20\nsudo python3 app.py\n\" > update.sh")
    os.system("sudo nohup sh update.sh &")
    exit(0)


# Backend functions
def update():
    run_update()
    return flask.redirect("/login")