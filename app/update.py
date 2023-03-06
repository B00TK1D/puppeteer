import os
import time
import flask
import threading

import db

update_status = "No updates available"

paused = False

# Helper functions
def ensure_dependencies():
    os.system("sudo pip3 install -r ../deploy/docker/requirements.txt")

def run_update():
    global update_status
    # Save current state
    db.save()
    # Stop backup thread
    db.pause()
    # Update the system
    os.system("sudo git pull")
    update_status = "Updated successfully"

def check_update():
    # Check if there is an update
    os.system("sudo git fetch")
    status = os.popen("sudo git status").read()
    if "up to date" in status:
        return 0
    else:
        try:
            count = int(status.split("\n")[1].split(" ")[6])
            return count
        except:
            return 0

# Backend functions
def update():
    run_update()
    return flask.redirect("/login")


# Thread functions
def check_loop():
    global update_status, paused
    while not paused:
        count = check_update()
        if count > 0:
            update_status = str(count) + " updates available"
        else:
            update_status = "No updates available"
        time.sleep(20)

def start():
    # Start update thread
    update_thread = threading.Thread(target = check_loop)
    update_thread.daemon = True
    update_thread.start()

def pause():
    global paused
    paused = True