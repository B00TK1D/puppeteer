import os
import re
import time
import flask
import threading
import subprocess


import db
import log
import settings
import flagformat


flagdb = {}

total_found = 0
total_submitted = 0

status_msg = "Not yet run"
status_code = 0

# Helper functions
def get_submitter_templates():
    return os.listdir(settings.SUBMITTER_TEMPLATES_DIR)

def get_submitter_template_contents(template):
    with open(os.path.join(settings.SUBMITTER_TEMPLATES_DIR, template), "r") as f:
        return f.read()

def get_submitter_contents():
    with open(settings.SUBMITTER_FILE, "r") as f:
        return f.read()

def get_status(output):
    if re.search(db.data["settings"]["correctregex"], output):
        return "success"
    elif re.search(db.data["settings"]["incorrectregex"], output):
        return "incorrect"
    else:
        # HTML encode output
        #output = html.escape(output)
        return "failure: " + output

def submit_flag(flag):
    try:
        os.system("chmod +x " + settings.SUBMITTER_FILE)
        esc_flag = re.sub("(\{|\})", r"\\\1", flag)
        output = subprocess.check_output(settings.SUBMITTER_FILE + " \"" + esc_flag + "\"", shell=True, stderr=subprocess.STDOUT)
        status = get_status(output.decode("utf-8"))
        return status
    except Exception as e:
        return "Error: " + str(e)

def handle_data(exploit_id, team_id, service_id, data):
    global total_found
    # Handle output from exploits
    flags = flagformat.extract_flags(data)
    total_new = 0
    for flag in flags:
        if flag not in flagdb:
            flagdb[flag] = {
                "flag": flag,
                "exploit_id": exploit_id,
                "team_id": team_id,
                "service_id": service_id,
                "submitted": 0,
                "valid": 0,
            }
            db.data["teams"][team_id]["flags_captured"] += 1
            db.data["services"][service_id]["flags_captured"] += 1
            db.data["exploits"][exploit_id]["flags_captured"] += 1
            total_found += 1
            total_new += 1
    return len(flags),total_new



# Frontend views
def view_submitter():
    global status_msg, status_code
    template = flask.request.args.get("template")
    code = ""
    rate = db.data["settings"]["submitrate"]
    correctregex = db.data["settings"]["correctregex"]
    incorrectregex = db.data["settings"]["incorrectregex"]
    if template:
        code = get_submitter_template_contents(template)
    else:
        code = get_submitter_contents()
    templates = get_submitter_templates()
    return flask.render_template("submitter/index.html",
                templates = templates,
                code = code,
                rate = rate,
                correctregex = correctregex,
                incorrectregex = incorrectregex,
                status = status_msg,
                status_code = status_code
            )

def view_submit_log():
    return flask.render_template("submitter/log.html",
            log = log.get_submit_log()
        )


# Backend functions
def update_submitter():
    code = flask.request.form.get("code")
    db.data["settings"]["submitrate"] = int(flask.request.form.get("rate"))
    db.data["settings"]["correctregex"] = flask.request.form.get("correctregex")
    db.data["settings"]["incorrectregex"] = flask.request.form.get("incorrectregex")

    with open(settings.SUBMITTER_FILE, "w", newline='\n') as f:
        code = code.replace('\r', '')
        f.write(code)

    return flask.render_template("submitter/index.html",
            templates = get_submitter_templates(),
            code = code,
            rate = db.data["settings"]["submitrate"],
            correctregex = db.data["settings"]["correctregex"],
            incorrectregex = db.data["settings"]["incorrectregex"],
            status = status_msg
        )


# Thread functions

def submit_loop():
    global status_msg, status_code, total_submitted
    # Submit flags to the submitter
    last_anysuccess = False
    while True:
        time.sleep(int(db.data["settings"]["submitrate"])/1000)
        anysuccess = False
        submitted = 0
        holding = 0
        invalid = 0
        for flag in flagdb:
            if flagdb[flag]["submitted"] == 0:
                time.sleep(int(db.data["settings"]["submitrate"])/1000)
                result = submit_flag(flag)
                # Timestamp with milliseconds
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S") + "." + str(int(time.time()*1000))[-3:]
                log.log_submit(
                        timestamp,
                        flag,
                        flagdb[flag]["team_id"],
                        flagdb[flag]["service_id"],
                        result
                    )
                if result == "success":
                    flagdb[flag]["submitted"] = 1
                    flagdb[flag]["valid"] = 1
                    anysuccess = True
                    submitted += 1
                    total_submitted += 1
                elif result == "invalid":
                    flagdb[flag]["submitted"] = 1
                    flagdb[flag]["valid"] = 0
                    anysuccess = True
                    invalid += 1
                else:
                    holding += 1
                if not last_anysuccess and not anysuccess and holding > 0:
                    status_msg = "Error: All flag submissions failing, check your submitter (holding " + str(holding) + " flags until it is fixed)"
                    status_code = 3
                elif not last_anysuccess and not anysuccess:
                    status_msg = "No flags to submit"
                    status_code = 1
                else:
                    status_msg = "Last run: " + time.strftime("%H:%M:%S") + " - " + str(submitted) + " flags submitted (" + str(invalid) + " attempted but invalid)"
                    if (invalid > 0):
                        status_code = 1
                    else:
                        status_code = 0
        last_anysuccess = anysuccess
        if not anysuccess and holding > 0:
            status_msg = "Error: All flag submissions failing, check your submitter (holding " + str(holding) + " flags until it is fixed)"
            status_code = 3
        elif not anysuccess:
            status_msg = "No flags to submit"
            status_code = 1
        else:
            status_msg = "Last run: " + time.strftime("%H:%M:%S") + " - " + str(submitted) + " flags submitted (" + str(invalid) + " attempted but invalid)"
            if (invalid > 0):
                status_code = 1
            else:
                status_code = 0
    

submit_thread = threading.Thread(target=submit_loop)