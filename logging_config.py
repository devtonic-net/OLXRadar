import os
import logging
from utils import BASE_DIR

log_file_path = os.path.join(BASE_DIR, "log.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
