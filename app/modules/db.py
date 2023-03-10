import os
import json
import time
import flask
import shutil
import itertools
import threading

from modules import settings

paused = False

data = {}

# Helper functions
def init():
    global data, id_iter
    data = {
        "exploits": {},
        "flags": {},
        "teams": {},
        "services": {},
        "submissions" : {},
        "agents": {},
        "catches": {},
        "settings": {
            "targetformat": settings.TARGET_DEFAULT_FORMAT,
            "flagformat": settings.FLAGFORMAT_DEFAULT_REGEX,
            "submitrate": settings.SUBMITTER_DEFAULT_RATE,
            "correctregex": settings.SUBMITTER_DEFAULT_CORRECT_REGEX,
            "incorrectregex": settings.SUBMITTER_DEFAULT_INCORRECT_REGEX,
            "password": ""
        }
    }

    id_iter = itertools.count()

def save(file=settings.DB_FILE):
    global data

    # Delete the previous file
    if os.path.exists(file):
        os.remove(file)

    # Write to file
    with open(file, "x") as f:
        json.dump(data, f, indent=4)

def load():
    global data
    try:
        if os.path.exists(settings.DB_FILE + ".bak"):
            with open(settings.DB_FILE + ".bak", "r") as f:
                data = json.load(f)
            os.remove(settings.DB_FILE + ".bak")
        else:
            with open(settings.DB_FILE, "r") as f:
                data = json.load(f)
    except FileNotFoundError:
        pass

    if "settings" not in data:
        data["settings"] = {}
    
    if "targetformat" not in data["settings"]:
        data["settings"]["targetformat"] = settings.TARGET_DEFAULT_FORMAT

    if "flagformat" not in data["settings"]:
        data["settings"]["flagformat"] = settings.FLAGFORMAT_DEFAULT_REGEX

    if "submitrate" not in data["settings"]:
        data["settings"]["submitrate"] = settings.SUBMITTER_DEFAULT_RATE

    if "correctregex" not in data["settings"]:
        data["settings"]["correctregex"] = settings.SUBMITTER_DEFAULT_CORRECT_REGEX

    if "incorrectregex" not in data["settings"]:
        data["settings"]["incorrectregex"] = settings.SUBMITTER_DEFAULT_INCORRECT_REGEX

    if "password" not in data["settings"]:
        data["settings"]["password"] = ""

    if "exploits" not in data:
        data["exploits"] = {}

    if "flags" not in data:
        data["flags"] = {}

    if "teams" not in data:
        data["teams"] = {}

    if "services" not in data:
        data["services"] = {}

    if "submissions" not in data:
        data["submissions"] = {}

    if "agents" not in data:
        data["agents"] = {}

    if "catches" not in data:
        data["catches"] = {}

def pause():
    global backup_thread, paused
    paused = True
    backup_thread.join()

def start():
    global backup_thread
    backup_thread.daemon = True
    backup_thread.start()

def create_backup():
    global data
    backup = data.copy()
    
    
    # Delete old backups
    os.system("sudo rm -r {}".format(settings.BACKUP_DIR))
    os.system("sudo rm {}".format(settings.BACKUP_FILE))

    # Create backup folder
    if not os.path.exists(settings.BACKUP_DIR):
        os.makedirs(settings.BACKUP_DIR)


    # Write data to file
    with open(os.path.join(settings.BACKUP_DIR, "db.json"), "x") as f:
        json.dump(backup, f, indent=4)

    # Recursively copy exploits from exploits to backup/exploits
    if not os.path.exists(os.path.join(settings.BACKUP_DIR, "exploits")):
        os.makedirs(os.path.join(settings.BACKUP_DIR, "exploits"))

    for f in os.listdir(settings.EXPLOITS_DIR):
        if os.path.isfile(os.path.join(settings.EXPLOITS_DIR, f)):
            shutil.copyfile(os.path.join(settings.EXPLOITS_DIR, f), os.path.join(settings.BACKUP_DIR, "exploits", f))

    # Recursively copy submitter from exploits/archive to backup/exploits/archive
    if not os.path.exists(os.path.join(settings.BACKUP_DIR, "exploits", "archive")):
        os.makedirs(os.path.join(settings.BACKUP_DIR, "exploits", "archive"))

    for f in os.listdir(settings.EXPLOITS_ARCHIVE_DIR):
        if os.path.isfile(os.path.join(settings.EXPLOITS_ARCHIVE_DIR, f)):
            shutil.copyfile(os.path.join(settings.EXPLOITS_ARCHIVE_DIR, f), os.path.join(settings.BACKUP_DIR, "exploits", "archive", f))

    # Copy submitter from submitter/submitter to backup/submitter
    shutil.copyfile(settings.SUBMITTER_FILE, os.path.join(settings.BACKUP_DIR, "submitter"))

    # Copy vpn/connect.sh to backup/vpn/connect.sh
    if not os.path.exists(os.path.join(settings.BACKUP_DIR, "vpn")):
        os.makedirs(os.path.join(settings.BACKUP_DIR, "vpn"))

    shutil.copyfile(settings.VPN_CONNECT_FILE, os.path.join(settings.BACKUP_DIR, "vpn", "connect.sh"))

    # Copy agents/init to backup/agents/init
    if not os.path.exists(os.path.join(settings.BACKUP_DIR, "agents")):
        os.makedirs(os.path.join(settings.BACKUP_DIR, "agents"))

    for f in os.listdir(os.path.join(settings.AGENTS_DIR, "init")):
        if os.path.isfile(os.path.join(settings.AGENTS_DIR, "init", f)):
            shutil.copyfile(os.path.join(settings.AGENTS_DIR, "init", f), os.path.join(settings.BACKUP_DIR, "agents", f))

    # gzip backup directory
    os.system("tar -czf {} {}".format(settings.BACKUP_FILE, settings.BACKUP_DIR))

    # Delete backup directory
    os.system("rm -r {}".format(settings.BACKUP_DIR))

def restore_backup():
    global data
    # Unzip backup.tar.gz
    os.system("tar -xzf {}".format(settings.BACKUP_FILE))

    # Recursively copy exploits from backup/exploits to exploits
    for f in os.listdir(os.path.join(settings.BACKUP_DIR, "exploits")):
        if os.path.isfile(os.path.join(settings.BACKUP_DIR, "exploits", f)):
            shutil.copyfile(os.path.join(settings.BACKUP_DIR, "exploits", f), os.path.join(settings.EXPLOITS_DIR, f))

    # Recursively copy submitter from backup/exploits/archive to exploits/archive
    for f in os.listdir(os.path.join(settings.BACKUP_DIR, "exploits", "archive")):
        if os.path.isfile(os.path.join(settings.BACKUP_DIR, "exploits", "archive", f)):
            shutil.copyfile(os.path.join(settings.BACKUP_DIR, "exploits", "archive", f), os.path.join(settings.EXPLOITS_ARCHIVE_DIR, f))

    # Copy submitter from backup/submitter to submitter/submitter
    shutil.copyfile(os.path.join(settings.BACKUP_DIR, "submitter"), settings.SUBMITTER_FILE)

    # Copy vpn/connect.sh to backup/vpn/connect.sh
    shutil.copyfile(os.path.join(settings.BACKUP_DIR, "vpn", "connect.sh"), settings.VPN_CONNECT_FILE)

    # Copy agents/init to backup/agents/init
    for f in os.listdir(os.path.join(settings.BACKUP_DIR, "agents")):
        if os.path.isfile(os.path.join(settings.BACKUP_DIR, "agents", f)):
            shutil.copyfile(os.path.join(settings.BACKUP_DIR, "agents", f), os.path.join(settings.AGENTS_DIR, "init", f))

    # Copy db.json to db.json
    shutil.copyfile(os.path.join(settings.BACKUP_DIR, "db.json"), settings.DB_FILE)

    # Delete backup directory
    os.system("rm -rf {}".format(settings.BACKUP_DIR))

    # Reload the database
    load()


# Backend functions
def download_backup():
    create_backup()
    return flask.send_file(settings.BACKUP_FILE, as_attachment=True)

def upload_backup():
    if "backup" in flask.request.files:
        backup = flask.request.files["backup"]
        backup.save(settings.BACKUP_FILE)
        restore_backup()
    return flask.redirect("/login")


# Thread functions
def backup_loop():
    global paused
    while not paused:
        save()
        time.sleep(settings.BACKUP_FREQUENCY)


# Backup thread
backup_thread = threading.Thread(target=backup_loop)