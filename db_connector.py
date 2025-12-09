# db_connector.py

import psycopg2
from psycopg2 import pool

# Database connection details (CONFIRMED CONFIGURATION)
DB_CONFIG = {
    "host": "localhost",
    "database": "SmartLibrary",
    "user": "postgres",
    "password": "799852",
    "port": "5432"
}

class DBConnector:
    """Manages the database connection pool."""
    _instance = None

    def __init__(self):
        if not hasattr(self, 'connection_pool'):
            self.connection_pool = self._setup_pool()

    def _setup_pool(self):
        """Creates and configures the connection pool."""
        try:
            return pool.ThreadedConnectionPool(
                1, 10,
                host=DB_CONFIG["host"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=DB_CONFIG["port"]
            )
        except psycopg2.OperationalError as e:
            print(f"Error connecting to the database pool: {e}")
            raise e

    def get_connection(self):
        """Retrieves a connection from the pool."""
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            print(f"Error getting connection: {e}")
            raise e

    def putconn(self, conn):
        """Returns a connection to the pool. FIXES 'putconn' ERROR."""
        if conn:
            self.connection_pool.putconn(conn)

def get_db_connector():
    """Singleton accessor function."""
    if DBConnector._instance is None:
        DBConnector._instance = DBConnector()
    return DBConnector._instance