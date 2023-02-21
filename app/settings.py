import os


BASE_DIR = os.path.realpath(__file__).rsplit("/", 1)[0]

# Database settings
DB_FILE = os.path.join(BASE_DIR, "db.json")

# Exploit settings
EXPLOITS_DIR = os.path.join(BASE_DIR, "exploits")
EXPLOITS_TEMPLATES_DIR = os.path.join(EXPLOITS_DIR, "templates")
EXPLOITS_ARCHIVE_DIR = os.path.join(EXPLOITS_DIR, "archive")

EXPLOIT_DEFAULT_FREQUENCY = 60


# Submitter settings
SUBMITTER_DIR = os.path.join(BASE_DIR, "submitter")
SUBMITTER_TEMPLATES_DIR = os.path.join(SUBMITTER_DIR, "templates")
SUBMITTER_FILE = os.path.join(SUBMITTER_DIR, "submitter")

SUBMITTER_DEFAULT_RATE = 1000
SUBMITTER_DEFAULT_CORRECT_REGEX = ".*success.*"
SUBMITTER_DEFAULT_INCORRECT_REGEX = ".*fail.*"

# Flag format settings
FLAGFORMAT_DEFAULT_REGEX = "flag{.*}"

# Target settings
TARGET_DEFAULT_FORMAT = "10.0.T.S"


# Logging settings
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "puppeteer.log")