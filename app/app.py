import db
import router
import traffic
import exploits
import submitter


def main():
    # Initialize the database
    db.init()

    db.load()

    # Load the exploits
    exploits.load_exploits()

    # Start backup thread
    db.backup_thread.daemon = True
    db.backup_thread.start()

    # Start the submitter thread
    submitter.submit_thread.daemon = True
    submitter.submit_thread.start()

    # Start the exploit thread
    exploits.exploit_thread.daemon = True
    exploits.exploit_thread.start()

    # Start the traffic thread
    traffic.traffic_thread.daemon = True
    traffic.traffic_thread.start()

    # Run the router
    router.run()


if __name__ == "__main__":
    main()

