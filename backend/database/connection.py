import os
import socket
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.core.config import settings
from backend.core.logging import logger
from backend.models.orm_models import Base

engine = None
SessionLocal = None
IS_USING_SQLITE = False

def is_mysql_reachable(url: str, timeout: float = 0.5) -> bool:
    try:
        # Extract host and port
        clean_url = url.split("://")[-1]
        host_port = clean_url.split("@")[-1].split("/")[0]
        if ":" in host_port:
            host, port_str = host_port.split(":")
            port = int(port_str)
        else:
            host = host_port
            port = 3306
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def initialize_engine():
    global engine, SessionLocal, IS_USING_SQLITE
    if engine is not None:
        return engine

    database_url = settings.DATABASE_URL

    if "sqlite" in database_url.lower():
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
        IS_USING_SQLITE = True
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine

    # Check if MySQL port is actively listening
    if is_mysql_reachable(database_url, timeout=0.5):
        try:
            test_engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Successfully connected to MySQL database: {database_url.split('@')[-1]}")
            engine = test_engine
            IS_USING_SQLITE = False
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return engine
        except Exception as e:
            logger.warning(f"MySQL handshake failed ({e}).")

    # Fallback to SQLite
    logger.warning(
        f"MySQL server is unreachable at {database_url.split('@')[-1]}. Using SQLite dev fallback at {settings.SQLITE_FALLBACK_URL}."
    )
    fallback_engine = create_engine(
        settings.SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False}
    )
    engine = fallback_engine
    IS_USING_SQLITE = True
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

def init_db():
    global engine
    if engine is None:
        initialize_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

def get_db():
    if SessionLocal is None:
        initialize_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
