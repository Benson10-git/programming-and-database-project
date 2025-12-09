# bookclub_dao.py (FULL CODE with fixes)

import psycopg2
from db_connector import get_db_connector
from datetime import datetime


class BookClubDAO:
    """Data Access Object for managing BookClub and ClubMembership tables."""

    def __init__(self):
        self.db_connector = get_db_connector()

    def create_club(self, name, description, max_members):
        """Inserts a new Book Club. Assumes description and max_members exist."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO BookClub (club_name, description, max_members, current_members)
                    VALUES (%s, %s, %s, 0) RETURNING club_id;
                """
                cursor.execute(query, (name, description, max_members))
                club_id = cursor.fetchone()[0]
                conn.commit()
                return club_id
        except psycopg2.Error as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    def get_all_clubs(self):  # <-- Fixes club load errors
        """Fetches all book clubs."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                # Query uses description and max_members columns
                query = "SELECT club_id, club_name, description, max_members, current_members FROM BookClub ORDER BY club_name;"
                cursor.execute(query)
                records = cursor.fetchall()

                clubs = []
                for record in records:
                    clubs.append({
                        'club_id': record[0], 'name': record[1], 'description': record[2],
                        'max_members': record[3], 'current_members': record[4]
                    })
                return clubs
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    # NOTE: Ensure all other methods (delete_club, join_club, leave_club) are present.