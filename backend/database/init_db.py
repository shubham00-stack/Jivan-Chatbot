import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.database import connection
from backend.core.logging import logger

if __name__ == "__main__":
    logger.info("Starting database initialization...")
    connection.initialize_engine()
    connection.init_db()
    if connection.IS_USING_SQLITE:
        logger.info("Initialized local SQLite database (MySQL was offline or unconfigured).")
    else:
        logger.info("Initialized MySQL database successfully.")
