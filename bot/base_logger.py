import logging
import os

from dotenv import load_dotenv

load_dotenv("../.env")
DEBUG = int(os.getenv("DEBUG"))
rootLogger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

fileHandler = logging.FileHandler("{0}/{1}.log".format("./", "log"))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

logger = logging
