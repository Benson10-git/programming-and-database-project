# member_main_widget.py (Member Book Catalog View)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from book_dao import BookDAO
from member_dao import MemberDAO


class MemberMainWidget(QWidget):

    def __init__(self, parent, member_id):
        super().__init__(parent)
        self.parent = parent
        self.member_id = member_id
        self.book_dao = BookDAO()
        self.member_dao = MemberDAO()

        self.setup_ui()
        self.load_book_data()
        self.update_loan_info()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Top Section: Title and User Loan Info ---
        header_layout = QHBoxLayout()
        title_label = QLabel("📖 Member Dashboard: Book Catalog")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        self.loan_limit_label = QLabel("Loans: 0/3")  # Display member's loan count
        self.loan_limit_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(self.loan_limit_label)

        main_layout.addLayout(header_layout)

        # --- Search Section ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Title, Author, or ISBN...")
        self.search_input.returnPressed.connect(self.search_books)

        search_button = QPushButton("🔍 Search")
        search_button.clicked.connect(self.search_books)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # --- Middle Section: Data Table ---
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(5)
        self.book_table.setHorizontalHeaderLabels([
            "ID", "Title", "Author(s)", "ISBN", "Available Copies"
        ])

        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.book_table.verticalHeader().setVisible(False)
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setSelectionMode(QTableWidget.SingleSelection)

        main_layout.addWidget(self.book_table)

        # --- Bottom Section: Loan Button ---
        button_layout = QHBoxLayout()

        self.loan_button = QPushButton("📚 Loan Selected Book")
        self.loan_button.clicked.connect(self.initiate_loan)

        button_layout.addStretch(1)
        button_layout.addWidget(self.loan_button)

        main_layout.addLayout(button_layout)

    def update_loan_info(self):
        """Fetches and displays the member's current loan count."""
        try:
            current_loans = self.member_dao.get_member_loan_count(self.member_id)
            self.loan_limit_label.setText(f"Loans: {current_loans}/3")
        except Exception as e:
            self.loan_limit_label.setText("Loans: Error")
            QMessageBox.critical(self, "Error", f"Could not load member loan info: {e}")

    def get_selected_book_data(self):
        """Helper to get ID and availability of the selected book."""
        selected_rows = self.book_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a book from the table first.")
            return None

        row = selected_rows[0].row()
        book_id = int(self.book_table.item(row, 0).text())
        available = int(self.book_table.item(row, 4).text())

        return {'book_id': book_id, 'available': available}

    # --- Data Handling (Read & Search) ---

    def load_book_data(self, books=None):
        """Loads data from the DAO into the QTableWidget."""

        if books is None:
            try:
                # Use a specific DAO method that returns the right columns for members
                books = self.book_dao.get_all_books()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to load book data: {e}")
                self.book_table.setRowCount(0)
                return

        self.book_table.setRowCount(len(books))

        for row_index, book in enumerate(books):
            self.book_table.setItem(row_index, 0, QTableWidgetItem(str(book.get('book_id', ''))))
            self.book_table.setItem(row_index, 1, QTableWidgetItem(book.get('title', '')))
            self.book_table.setItem(row_index, 2, QTableWidgetItem(book.get('authors', '')))
            self.book_table.setItem(row_index, 3, QTableWidgetItem(book.get('isbn', '')))
            # Only showing Available Copies for members
            self.book_table.setItem(row_index, 4, QTableWidgetItem(str(book.get('available_copies', 0))))

    def search_books(self):
        """Calls the DAO search method and updates the table."""
        search_term = self.search_input.text().strip()

        if not search_term:
            self.load_book_data()
            return

        try:
            results = self.book_dao.search_books(search_term)
            if results:
                self.load_book_data(results)
            else:
                QMessageBox.information(self, "Search Result", f"No books found matching '{search_term}'.")
                self.book_table.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"An error occurred during search: {e}")

    # --- Loan Initiation ---

    def initiate_loan(self):
        """Validates selection and navigates to the loan confirmation screen."""
        book_data = self.get_selected_book_data()

        if book_data:
            if book_data['available'] <= 0:
                QMessageBox.warning(self, "Loan Failed", "This book has no available copies for loan.")
                return

            # Navigate to the loan confirmation screen
            self.parent.show_member_loan_view(book_data['book_id'])