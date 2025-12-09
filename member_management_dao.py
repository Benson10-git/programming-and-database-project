# member_management_dao.py (FULL CODE with fixes)

import psycopg2
from db_connector import get_db_connector


class MemberManagementDAO:
    """DAO for managing new members and viewing all members."""

    def __init__(self):
        self.db_connector = get_db_connector()

    def create_new_member(self, first_name, last_name, username, password):
        """Creates a new User record (Role must be 'Member') and the corresponding Member record."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Create the new User record (Uses role, excludes email to satisfy NOT NULL constraint fix)
                user_query = """
                    INSERT INTO "User" (username, password, first_name, last_name, role)
                    VALUES (%s, %s, %s, %s, 'Member') RETURNING user_id;
                """
                cursor.execute(user_query, (username, password, first_name, last_name))
                new_user_id = cursor.fetchone()[0]

                # 2. Create the corresponding Member record
                member_query = """
                    INSERT INTO Member (member_id, current_loans)
                    VALUES (%s, 0);
                """
                cursor.execute(member_query, (new_user_id,))

                conn.commit()
                return new_user_id
        except psycopg2.IntegrityError as e:
            conn.rollback()
            if 'duplicate key value violates unique constraint "user_username_key"' in str(e):
                raise Exception("Username already exists. Please choose a different one.")
            raise Exception(f"Database Integrity Error: {e}")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    def get_all_members(self):
        """Fetches details for all members in the system."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT u.user_id, u.first_name, u.last_name, u.username, m.current_loans
                    FROM "User" u
                    JOIN Member m ON u.user_id = m.member_id
                    ORDER BY u.user_id;
                """
                cursor.execute(query)
                records = cursor.fetchall()

                members = []
                for record in records:
                    members.append({
                        'id': record[0], 'first_name': record[1], 'last_name': record[2],
                        'username': record[3], 'current_loans': record[4]
                    })
                return members
        finally:
            self.db_connector.putconn(conn)