# member_loan_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QPushButton  # <-- QPushButton must be imported
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from book_dao import BookDAO
from loan_dao import LoanDAO
from member_dao import MemberDAO


class MemberLoanWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.book_dao = BookDAO()
        self.member_dao = MemberDAO()
        # LoanDAO needs access to both book and member DAOs
        self.loan_dao = LoanDAO(self.book_dao, self.member_dao)

        self.target_book_id = None
        self.target_member_id = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Confirm Checkout")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Details about the book to be loaned
        self.book_details_label = QLabel("Please select a book to view details.")
        self.book_details_label.setAlignment(Qt.AlignCenter)
        self.book_details_label.setFont(QFont("Arial", 12))
        self.book_details_label.setWordWrap(True)
        main_layout.addWidget(self.book_details_label, alignment=Qt.AlignCenter)

        # Spacer
        main_layout.addSpacing(40)

        # Action Buttons
        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton("✅ CONFIRM LOAN")
        self.confirm_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.confirm_button.setStyleSheet("background-color: green; color: white;")
        self.confirm_button.clicked.connect(self.confirm_checkout)
        self.confirm_button.setEnabled(False)  # Disabled until data is loaded

        self.cancel_button = QPushButton("❌ CANCEL / Back to Catalog")
        self.cancel_button.clicked.connect(self.parent.show_member_dashboard)

        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def prepare_for_loan(self, book_id, member_id):
        """Called by main.py to load data for the selected book."""
        self.target_book_id = book_id
        self.target_member_id = member_id

        try:
            # Fetch book details to display confirmation text
            book = self.book_dao.get_book_details(book_id)
            if book:
                loan_text = (
                    f"You are attempting to loan:\n\n"
                    f"Title: **{book['title']}**\n"
                    f"Author(s): {book['authors']}\n"
                    f"Available Copies: {book['available_copies']}\n\n"
                    f"A standard loan period is 7 days. Click CONFIRM to proceed."
                )
                self.book_details_label.setText(loan_text)
                self.confirm_button.setEnabled(True)
            else:
                self.book_details_label.setText("Error: Book not found.")
                self.confirm_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load book details: {e}")
            self.book_details_label.setText("Error loading details.")
            self.confirm_button.setEnabled(False)

    def confirm_checkout(self):
        """Final call to the DAO to execute the loan transaction."""
        if self.target_book_id is None or self.target_member_id is None:
            QMessageBox.critical(self, "Error", "Loan details are missing.")
            return

        try:
            self.loan_dao.process_checkout(self.target_book_id, self.target_member_id)

            QMessageBox.information(self, "Success", "Book successfully checked out! Returning to the catalog.")

            # Navigate back to the member dashboard and refresh
            self.parent.show_member_dashboard()

        except Exception as e:
            QMessageBox.critical(self, "Checkout Failed", str(e))