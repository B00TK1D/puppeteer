import flask
import logging
import datetime
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

from modules import db
from modules import log
from modules import services
from modules import settings
from modules import flagformat


ignore = []

# Helper functions
def full_duplex(p):
    sess = "Other"
    if 'Ether' in p:
        if 'IP' in p:
            if 'TCP' in p:
                sess = str(sorted(["TCP", p['IP'].src, p['TCP'].sport, p['IP'].dst, p['TCP'].dport],key=str))
            elif 'UDP' in p:
                sess = str(sorted(["UDP", p['IP'].src, p['UDP'].sport, p['IP'].dst, p['UDP'].dport] ,key=str))
            elif 'ICMP' in p:
                sess = str(sorted(["ICMP", p['IP'].src, p['IP'].dst, p['ICMP'].code, p['ICMP'].type, p['ICMP'].id] ,key=str)) 
            else:
                sess = str(sorted(["IP", p['IP'].src, p['IP'].dst, p['IP'].proto] ,key=str)) 
        elif 'ARP' in p:
            sess = str(sorted(["ARP", p['ARP'].psrc, p['ARP'].pdst],key=str)) 
        else:
            sess = p.sprintf("Ethernet type=%04xr,Ether.type%")
    return sess

def strip_ignores(catches):
    global ignore
    if not ignore:
        return catches
    new = {}
    for catch in catches.values():
        ignored = False
        for ig in ignore:
            local = True
            for packet in catch['packets']:
                if packet['dir'] == 'in':
                    if packet['bytes'] not in ig:
                        local = False
                        break
            if local:
                ignored = True
                break
        if not ignored:
            new[catch['id']] = catch
            break
    return new

def catch(pcap):
    log.log("Catching flags from " + pcap)
    packets = rdpcap(pcap)
    sessions = packets.sessions(full_duplex)
    catches = {}
    for session in sessions.values():
        # Search bytes of each packet for flag format
        catch = {}
        for packet in session:
            # Check if packet is outbound
            flags = flagformat.extract_flags_bytes(bytes(packet.payload))
            if flags:
                victim_ip = packet['IP'].src
                attacker_ip = packet['IP'].dst
                victim_port = 0
                attacker_port = 0
                if packet.haslayer('TCP'):
                    victim_port = packet['TCP'].sport
                    attacker_port = packet['TCP'].dport
                elif packet.haslayer('UDP'):
                    victim_port = packet['UDP'].sport
                    attacker_port = packet['UDP'].dport
                timestamp = datetime.fromtimestamp(int(packet.time)).strftime('%Y-%m-%d %H:%M:%S')
                id = int(packet.time)
                catch = {
                    "id": id,
                    "victim_ip": victim_ip,
                    "attacker_ip": attacker_ip,
                    "victim_port": victim_port,
                    "attacker_port": attacker_port,
                    "timestamp": timestamp,
                    "flags": flags,
                    "pcap": pcap,
                    "packets": []
                }
                break
        if catch:
            # Print packet bytes
            for packet in session:
                b = bytes(packet['TCP'].payload)
                if len(b) > 0:
                    # Convert each byte to ascii if possible
                    #ascii = "".join([chr(x) if x < 128 else "\\x" + hex(x)[2:] for x in b])
                    if packet['IP'].src == victim_ip:
                        catch['packets'].append({
                            "dir": "out",
                            "bytes": str(b)
                        })
                    else:
                        catch['packets'].append({
                            "dir": "in",
                            "bytes": str(b)
                        })
            catches[catch["id"]] = catch

    catches = strip_ignores(catches)

    for catch in catches.values():
        db.data["catches"][catch["id"]] = catch
    return catches


def generate_exploit(catch):
    exploit = "#!/usr/bin/env python3\n"
    exploit += "\n"
    exploit += "import sys\n"
    exploit += "import socket\n"
    exploit += "\n"

    exploit += "# Exploit - moodify this function\n"
    exploit += "def exploit(host):\n"
    exploit += "    port = " + str(catch["victim_port"]) + "\n"
    exploit += "\n"
    exploit += "    # Create socket\n"
    exploit += "    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
    exploit += "    s.connect((host, port))\n"
    exploit += "\n"
    for packet in catch["packets"]:
        if packet["dir"] == "in":
            exploit += "    s.sendall(" + packet["bytes"].replace("\\\\", "\\") + ")\n"
        else:
            exploit += "    print(s.recv(65536))\n"
    exploit += "\n"
    exploit += "    # Close socket\n"
    exploit += "    s.close()\n"
    exploit += "\n"
    exploit += "# Main - do not modify\n"
    exploit += "def main(argv):\n"
    exploit += "    if len(argv) != 2:\n"
    exploit += "        print(\"Usage: python3 exploit.py <host>\")\n"
    exploit += "        sys.exit(1)\n"
    exploit += "    \n"
    exploit += "    exploit(argv[1])\n"
    exploit += "    \n"
    exploit += "    host = argv[1]\n"
    exploit += "\n"
    exploit += "if __name__ == \"__main__\":\n"
    exploit += "    main(sys.argv)\n"

    service_id = services.service_from_ip(catch["victim_ip"])
    service_name = ""
    if service_id:
        service_name = db.data["services"][service_id]["name"] + "-"

    # Write exploit to file
    name = "catcher-" + service_name + str(catch["id"])
    filename = "exploits/" + name + ".py"
    with open(filename, "w") as f:
        f.write(exploit)

    # Add exploit to database
    id = str(next(db.id_iter))
    db.data["exploits"][id] = {
        "id": id,
        "name": name,
        "frequency": settings.EXPLOIT_DEFAULT_FREQUENCY,
        "path": name + ".py",
        "flags_captured": 0,
        "services_vulnerable": 0,
        "service_id": service_id,
        "log": {}
    }

    return id
    
def remove_similar(catch):
    req_stream = []
    for packet in catch["packets"]:
        if packet["dir"] == "in":
            req_stream.append(packet["bytes"])

    ignore.append(req_stream)

    db.data["catches"] = strip_ignores(db.data["catches"])

    db.data["catches"][catch["id"]] = catch


# Backend functions
def build_exploit():
    id = int(flask.request.args.get("id"))

    if id not in db.data["catches"]:
        return flask.render_template("catcher/index.html", catches=db.data["catches"], messages=["Invalid - catch not found"])
    
    catch = db.data["catches"][id]
    id = generate_exploit(catch)

    return flask.redirect("/exploits/modify?id=" + id)
    
def ignore_similar():
    id = int(flask.request.args.get("id"))

    if id not in db.data["catches"]:
        return flask.render_template("catcher/index.html", catches=db.data["catches"], messages=["Invalid - catch not found"])
    
    catch = db.data["catches"][id]

    remove_similar(catch)

    return flask.redirect("/catcher")    


# View functions
def view_catcher():
    return flask.render_template("catcher/index.html", catches=db.data["catches"])


def view_catch():
    id = int(flask.request.args.get("id"))

    if id not in db.data["catches"]:
        return flask.render_template("catcher/index.html", catches=db.data["catches"], messages=["Invalid - catch not found"])

    catch = db.data["catches"][id]

    return flask.render_template("catcher/view.html", catch=catch)