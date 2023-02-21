import time

import db
import settings

log = {}
exploit_log = {}
submit_log = {}


def log(message, type="info"):
    # Log a message to the log file
    with open(settings.LOG_FILE, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write("[{}]: {} - {}\n".format(timestamp, type, message))


def log_exploit(id, timestamp, team, service, target, status, info):
    global exploit_log
    if id not in exploit_log:
        exploit_log[id] = {}
    exploit_log[id][timestamp] = {
        "id": id,
        "timestamp": timestamp,
        "team": team,
        "service": service,
        "target": target,
        "status": status,
        "info": info
    }
    log("Exploit {} status {} for {} on {} ({})".format(id, status, team, service, target), "exploit")

def log_submit(timestamp, flag, team, service, result):
    global submit_log
    submit_log[timestamp] = {
        "timestamp": timestamp,
        "flag": flag,
        "team": team,
        "service": service,
        "result": result
    }
    log("Submitted {} for {} on {} ({})".format(flag, team, service, result), "submit")


def get_exploit_log(id, teamFilter=None, serviceFilter=None, statusFilter=None):
    global exploit_log
    if id not in exploit_log:
        raise KeyError
    log = exploit_log[id]
    if teamFilter:
        log = {k: v for k, v in log.items() if v["team"] == teamFilter}
    if serviceFilter:
        log = {k: v for k, v in log.items() if v["service"] == serviceFilter}
    if statusFilter:
        log = {k: v for k, v in log.items() if v["status"] == statusFilter}
    return log


def get_exploit_log_details(id, timestamp):
    global exploit_log
    if id not in exploit_log:
        raise KeyError
    if timestamp not in exploit_log[id]:
        raise KeyError
    return exploit_log[id][timestamp]


def get_submit_log(teamFilter=None, serviceFilter=None, statusFilter=None):
    global submit_log
    log = submit_log
    if teamFilter:
        log = {k: v for k, v in log.items() if v["team"] == teamFilter}
    if serviceFilter:
        log = {k: v for k, v in log.items() if v["service"] == serviceFilter}
    if statusFilter:
        log = {k: v for k, v in log.items() if v["result"] == statusFilter}
    return log