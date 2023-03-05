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
    os.system("git stash")
    os.system("git pull")
    os.system("sudo pip3 install -r ../deploy/docker/requirements.txt")
    os.system("echo -e \"#!/bin/sh\nsudo killall python3\nsudo python3 app.py\n\" > update.sh")
    os.system("sudo sh update.sh")


# Backend functions
def update():
    run_update()
    return flask.redirect("/login")