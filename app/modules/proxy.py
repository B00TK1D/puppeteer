import flask
import subprocess

proxy_process = None
status = "Inactive"

# Helper functions
def start_proxy():
    global proxy_process, status
    proxy_process = subprocess.Popen(['sudo', 'docker', 'run', '-e', 'TZ=UTC', '-p', '3128:3128', 'ubuntu/squid'])
    status = "Active"

def stop_proxy():
    global proxy_process, status
    if proxy_process != None:
        proxy_process.terminate()
        proxy_process = None
        status = "Inactive"


# Backend functions
def start():
    start_proxy()
    return flask.redirect("/vpn?message=Proxy started")

def stop():
    stop_proxy()
    return flask.redirect("/vpn?message=Proxy stopped")