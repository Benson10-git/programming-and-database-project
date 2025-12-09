# member_dao.py (Updated with get_member_loan_count)

import psycopg2
from db_connector import get_db_connector


class MemberDAO:
    """Data Access Object for Member-specific operations (e.g., login, loan checks)."""

    def __init__(self):
        self.db_connector = get_db_connector()

    def get_member_details(self, member_id):
        """Fetches member details by ID."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT u.first_name, u.last_name, m.current_loans
                    FROM "User" u
                    JOIN Member m ON u.user_id = m.member_id
                    WHERE u.user_id = %s;
                """
                cursor.execute(query, (member_id,))
                record = cursor.fetchone()

                if record:
                    return {
                        'first_name': record[0],
                        'last_name': record[1],
                        'current_loans': record[2]
                    }
                return None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    def get_member_loan_count(self, member_id):  # <-- FIX FOR 'get_member_loan_count' ERROR
        """Fetches the current loan count for a member."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = "SELECT current_loans FROM Member WHERE member_id = %s;"
                cursor.execute(query, (member_id,))
                record = cursor.fetchone()
                return record[0] if record else 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    def update_loan_count(self, member_id, change):
        """Increments or decrements the current loan count."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    UPDATE Member SET current_loans = current_loans + %s 
                    WHERE member_id = %s;
                """
                cursor.execute(query, (change, member_id))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)