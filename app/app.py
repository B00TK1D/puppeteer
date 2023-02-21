import db
import router
import exploits
import submitter


def main():
    # Initialize the database
    db.init()

    db.load()

    # Start backup thread
    db.backup_thread.daemon = True
    db.backup_thread.start()

    # Load the exploits
    exploits.load_exploits()

    # Start the submitter thread
    submitter.submit_thread.daemon = True
    submitter.submit_thread.start()

    # Run the router
    router.run()


if __name__ == "__main__":
    main()

