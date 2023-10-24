import logging

from ilobot.helpers import DEBUG

rootLogger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

fileHandler = logging.FileHandler("./log.txt")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

logger = logging
