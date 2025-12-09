# loan_dao.py

import psycopg2
from db_connector import get_db_connector
from datetime import datetime, timedelta  # <-- CRITICAL FIX: Add datetime import


class LoanDAO:
    """Data Access Object for managing book loans."""

    def __init__(self):
        self.db_connector = get_db_connector()

    # NOTE: All methods (create_loan, get_active_loans, etc.) must be implemented below
    # and use the try/finally/putconn structure.