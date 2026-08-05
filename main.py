# main.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import threading
from storage.database import init_db
from capture.sniffer import start_sniffer
from dashboard.app import start_flask
from logger_setup import logger

if __name__ == "__main__":
    logger.info("Starting NetSentinel...")
    init_db()

    t = threading.Thread(target=start_sniffer, daemon=True)
    t.start()

    start_flask()
