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
    os.system("git stash")
    os.system("git pull")
    os.system("sudo pip3 install -r ../deploy/docker/requirements.txt")
    os.system("echo -e \"#!/bin/sh\nsudo kill -9 " + str(pid) + "\nsudo python3 app.py\nrm update.sh\n\" > update.sh")
    os.system("sudo sh update.sh")


# Backend functions
def update():
    run_update()
    return flask.redirect("/login")