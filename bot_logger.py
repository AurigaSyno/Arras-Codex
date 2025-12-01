import logging

import constants
from bot_instance import bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(constants.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_logger(name=None):
    return logging.getLogger(name)

