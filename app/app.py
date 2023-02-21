import db
import router
import exploits


def main():
    # Initialize the database
    db.init()

    db.load()

    # Start backup thread
    db.backup_thread.start()

    # Load the exploits
    exploits.load_exploits()

    # Run the router
    router.run()


if __name__ == "__main__":
    main()

