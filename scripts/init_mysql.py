"""
Standalone helper script to connect to MySQL, create the database if needed,
and initialize all tables from schema/models.
"""
import sys
import os
from pathlib import Path
from urllib.parse import urlparse
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import settings
from backend.core.logging import logger
from backend.database import connection

def create_mysql_database_if_not_exists(database_url: str):
    """Connects to MySQL server root without database name to ensure the target DB exists."""
    if "sqlite" in database_url.lower():
        return

    # Check if host:port is reachable first
    if not connection.is_mysql_reachable(database_url, timeout=0.5):
        return

    try:
        # Parse connection URL
        clean_url = database_url.split("://")[-1]
        auth_host = clean_url.split("/")[0]
        db_name = clean_url.split("/")[1].split("?")[0] if "/" in clean_url else "multimodal_chatbot"

        root_url = f"mysql+pymysql://{auth_host}/"
        logger.info(f"Connecting to MySQL server at {auth_host.split('@')[-1]} to verify database '{db_name}'...")
        
        server_engine = create_engine(root_url, connect_args={"connect_timeout": 5})
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            conn.commit()
        logger.info(f"Database '{db_name}' is verified / created.")
    except Exception as e:
        logger.warning(f"Could not automatically create database from root URL: {e}")

def main():
    logger.info("Initializing database...")
    db_url = settings.DATABASE_URL
    create_mysql_database_if_not_exists(db_url)
    try:
        connection.initialize_engine()
        connection.init_db()
        if connection.IS_USING_SQLITE:
            logger.warning(
                "Tables initialized in local SQLite fallback (chatbot.db) because MySQL server was unreachable. "
                "To use MySQL, verify your MySQL server is running and check DATABASE_URL in .env."
            )
        else:
            logger.info("Connected to MySQL and all tables were initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
