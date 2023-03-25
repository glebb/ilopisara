import logging
import os

from dotenv import load_dotenv

load_dotenv("../.env")
DEBUG = int(os.getenv("DEBUG"))

logging.basicConfig(level=logging.INFO if DEBUG else logging.WARNING)
logger = logging
