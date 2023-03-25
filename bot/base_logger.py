import logging
import os

from dotenv import load_dotenv

load_dotenv("../.env")
DEBUG = int(os.getenv("DEBUG"))

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging
