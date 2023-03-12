import os
import flask

status = "Inactive"

# Helper functions
def start_proxy():
    global status
    try:
        os.system("sudo docker run --name squid-container -e TZ=UTC -p 3128:3128 -d ubuntu/squid")
        status = "Active"
    except:
        status = "Error"


def stop_proxy():
    global status
    if proxy_process != None:
        try:
            os.system("sudo docker stop squid-container")
            proxy_process = None
            status = "Inactive"
        except:
            status = "Error"


# Backend functions
def start():
    start_proxy()
    return flask.redirect("/vpn?message=Proxy started")

def stop():
    stop_proxy()
    return flask.redirect("/vpn?message=Proxy stopped")