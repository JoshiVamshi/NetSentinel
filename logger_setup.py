# logger_setup.py
import os
import logging

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/netsentinel.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("NetSentinel")
