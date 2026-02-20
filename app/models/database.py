import sqlite3
from contextlib import contextmanager
from typing import Generator
import threading
import queue
import time
import logging
import os
from flask import current_app

logger = logging.getLogger(__name__)

# Default database path - absolute path using app directory
# This assumes database.py is in app/models/
# We want database in root, which is 2 levels up from app/models/
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'community_helper.db'))

def get_db_connection():
    """Create a connection to the SQLite database (Legacy support)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

class DatabaseConnectionPool:
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self._initialize_pool()
        self._setup_logging()

    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.max_connections):
            conn = self._create_new_connection()
            self.connections.put(conn)
        logger.info(f"Initialized connection pool with {self.max_connections} connections")

    def _setup_logging(self):
        """Setup logging configuration"""
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection from the pool with context management"""
        conn = None
        try:
            conn = self._get_connection()
            yield conn
            conn.commit()  # Auto-commit if no exception occurred
        except Exception as e:
            if conn:
                conn.rollback()  # Rollback on error
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                self._return_connection(conn)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection with timeout and retry"""
        start_time = time.time()
        while True:
            try:
                conn = self.connections.get(timeout=5)
                if not self._is_connection_valid(conn):
                    logger.warning("Found invalid connection, creating new one")
                    conn.close()
                    conn = self._create_new_connection()
                return conn
            except queue.Empty:
                if time.time() - start_time > 30:
                    logger.error("Connection pool timeout")
                    raise TimeoutError("Could not get database connection")
                time.sleep(0.1)

    def _return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool"""
        try:
            self.connections.put(conn, timeout=5)
        except queue.Full:
            logger.warning("Connection pool full, closing extra connection")
            conn.close()

    def _is_connection_valid(self, conn: sqlite3.Connection) -> bool:
        """Check if connection is still valid"""
        try:
            conn.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False

    def _create_new_connection(self) -> sqlite3.Connection:
        """Create a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Set journal mode to WAL for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def close_all(self):
        """Close all connections in the pool"""
        logger.info("Closing all database connections")
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                conn.close()
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")

# Global connection pool instance
db_pool = None

def init_db():
    """Initialize the database with required tables"""
    if os.path.exists(DATABASE_PATH):
        logger.info(f"Database {DATABASE_PATH} already exists.")
        return

    conn = get_db_connection()
    try:
        # Use absolute path for schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        logger.info(f"Database {DATABASE_PATH} initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

def init_db_pool(app):
    """Initialize the database pool with application context"""
    global db_pool
    if db_pool is None:
        db_path = app.config.get('DATABASE_PATH', DATABASE_PATH)
        max_connections = app.config.get('DB_MAX_CONNECTIONS', 10)
        db_pool = DatabaseConnectionPool(db_path, max_connections)
        logger.info("Database pool initialized")

def get_db():
    """Get a database connection from the pool"""
    global db_pool
    if db_pool is None:
        init_db_pool(current_app)
    return db_pool.get_connection()

# Run this file directly to initialize the database
if __name__ == "__main__":
    init_db()
