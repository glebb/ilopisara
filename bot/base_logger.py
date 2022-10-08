import logging

from helpers import DEBUG

logging.basicConfig(level=logging.INFO if DEBUG else logging.WARNING)
logger = logging
