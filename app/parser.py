
import db
import submitter
import flagformat

flagdb = {}

def handle_data(exploit_id, team_id, service_id, data):
    # Handle output from exploits
    flags = flagformat.extract_flags(data)
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
            db.data["teams"][team_id]["flags_collected"] += 1
            db.data["services"][service_id]["flags_collected"] += 1
            db.data["exploits"][exploit_id]["flags_collected"] += 1


def submit_thread():
    # Submit flags to the submitter
    while True:
        for flag in flagdb:
            if flagdb[flag]["submitted"] == 0:
                result = submitter.submit_flag(flag)
                
