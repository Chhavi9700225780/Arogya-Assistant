import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)

handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=2)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger("HealthMesh")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
