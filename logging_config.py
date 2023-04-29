"""
Sets the format of messages related to the script operation (status and errors),
which will be written to the log.log file, saved in the same directory as the script.
"""
import os
import logging
from utils import BASE_DIR

log_file_path = os.path.join(BASE_DIR, "log.log")
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
