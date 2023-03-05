import os
import flask

import db

# Helper functions
def ensure_dependencies():
    os.system("sudo pip3 install -r ../deploy/docker/requirements.txt")

def run_update():
    # Save current state
    db.save()
    # Stop backup thread
    db.pause()
    # Update the system
    os.system("sudo git pull")
    print("done")


# Backend functions
def update():
    run_update()
    return flask.redirect("/login")