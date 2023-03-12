from modules import db
from modules import auth
from modules import router
from modules import update
from modules import traffic
from modules import exploits
from modules import submitter


def main():
    # Initialize the database
    db.init()

    db.load()

    # Initialize auth
    auth.init()

    # Load the exploits
    exploits.load_exploits()

    # Start backup thread
    db.start()

    # Start the submitter thread
    submitter.submit_thread.daemon = True
    submitter.submit_thread.start()

    # Start the exploit thread
    exploits.exploit_thread.daemon = True
    exploits.exploit_thread.start()

    # Start the traffic thread
    traffic.traffic_thread.daemon = True
    traffic.traffic_thread.start()

    # Start the update thread
    update.start()

    # Run the router
    router.run()


if __name__ == "__main__":
    main()

