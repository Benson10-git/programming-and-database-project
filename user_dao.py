# user_dao.py

import psycopg2
from db_connector import get_db_connector


class UserDAO:
    """Data Access Object for User and Role entities, using plain text password for dev."""

    def __init__(self):
        self.db_connector = get_db_connector()

    def get_user_by_username(self, username):
        """Fetches a user and their role by username."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                # Query the 'password' column, NOT 'password_hash'
                query = """
                    SELECT 
                        u.user_id, u.username, u.password, 
                        u.first_name, u.last_name, r.role_name
                    FROM "User" u
                    JOIN Role r ON u.role_id = r.role_id
                    WHERE u.username = %s
                """
                cursor.execute(query, (username,))
                record = cursor.fetchone()

                if record:
                    return {
                        'user_id': record[0],
                        'username': record[1],
                        'password': record[2],
                        'first_name': record[3],
                        'last_name': record[4],
                        'role': record[5]
                    }
                return None
        except psycopg2.Error as e:
            conn.rollback()
            raise e

    def verify_login(self, username, password):
        """Authenticates a user using simple text comparison."""
        user_data = self.get_user_by_username(username)

        if user_data:
            # Simple text comparison for development purposes
            if password == user_data['password']:
                del user_data['password']  # Security best practice, remove password before returning
                return user_data

        return None