# book_dao.py (FULL CODE with fixes)

import psycopg2
from db_connector import get_db_connector


class BookDAO:
    """Data Access Object for Book and Author management."""

    def __init__(self):
        self.db_connector = get_db_connector()

    def get_all_books(self):  # <-- FIX: Implements missing method
        """Fetches all books, their authors, and available copies."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        b.book_id, b.title, b.isbn, b.publication_year, 
                        b.total_copies, b.available_copies, 
                        STRING_AGG(CONCAT(a.first_name, ' ', a.last_name), ', ') AS authors
                    FROM Book b
                    LEFT JOIN BookAuthor ba ON b.book_id = ba.book_id
                    LEFT JOIN Author a ON ba.author_id = a.author_id
                    GROUP BY b.book_id
                    ORDER BY b.title;
                """
                cursor.execute(query)
                records = cursor.fetchall()

                books = []
                for record in records:
                    books.append({
                        'book_id': record[0], 'title': record[1], 'isbn': record[2],
                        'year': record[3], 'total_copies': record[4],
                        'available_copies': record[5], 'authors': record[6] if record[6] else "N/A"
                    })
                return books
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    def get_book_availability(self, book_id):  # <-- FIX: Implements missing method
        """Checks the available copies for a specific book."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = "SELECT available_copies FROM Book WHERE book_id = %s;"
                cursor.execute(query, (book_id,))
                record = cursor.fetchone()
                return record[0] if record else 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    def delete_book_by_id(self, book_id):
        """Deletes a book (and related entries in BookAuthor) by ID."""
        conn = self.db_connector.get_connection()
        try:
            with conn.cursor() as cursor:
                # Check for active loans
                check_query = "SELECT COUNT(*) FROM Loan WHERE book_id = %s AND return_date IS NULL;"
                cursor.execute(check_query, (book_id,))
                active_loans = cursor.fetchone()[0]

                if active_loans > 0:
                    raise Exception(f"Cannot delete Book ID {book_id}. It has {active_loans} active loan(s).")

                delete_query = "DELETE FROM Book WHERE book_id = %s;"
                cursor.execute(delete_query, (book_id,))

                if cursor.rowcount == 0:
                    raise Exception(f"Book ID {book_id} not found.")

                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db_connector.putconn(conn)

    # NOTE: You must include your other required methods (get_book_details, add_author, add_book, search_books)
    # in this file, ensuring they all use the try/finally/putconn structure.