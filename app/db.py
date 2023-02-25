import json
import time
import itertools
import threading

import settings


def init():
    global data, id_iter
    data = {
        "exploits": {},
        "flags": {},
        "teams": {},
        "services": {},
        "submissions" : {},
        "settings": {
            "targetformat": settings.TARGET_DEFAULT_FORMAT,
            "flagformat": settings.FLAGFORMAT_DEFAULT_REGEX,
            "submitrate": settings.SUBMITTER_DEFAULT_RATE,
            "correctregex": settings.SUBMITTER_DEFAULT_CORRECT_REGEX,
            "incorrectregex": settings.SUBMITTER_DEFAULT_INCORRECT_REGEX
        }
    }

    id_iter = itertools.count()


def save():
    global data

    # Write to file
    with open(settings.DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load():
    global data
    try:
        with open(settings.DB_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        pass

# Set up a backup thread that saves the database every 5 seconds
def backup_loop():
    while True:
        save()
        time.sleep(settings.BACKUP_FREQUENCY)


# Backup thread
backup_thread = threading.Thread(target=backup_loop)