# loan_manager_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import DAOs
from loan_dao import LoanDAO
from book_dao import BookDAO
from member_dao import MemberDAO


class LoanManagerWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Instantiate DAOs needed for loan logic
        self.book_dao = BookDAO()
        self.member_dao = MemberDAO()
        self.loan_dao = LoanDAO(self.book_dao, self.member_dao)

        self.setup_ui()
        # Initial load is called when the widget is created, but main.py will call it again on navigation

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Header and Back Button ---
        header_layout = QHBoxLayout()
        title_label = QLabel("🔄 Loan Management: Checkout & Returns")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        self.back_button = QPushButton("⬅️ Back to Dashboard")
        self.back_button.clicked.connect(self.parent.show_librarian_dashboard)
        header_layout.addWidget(self.back_button)

        main_layout.addLayout(header_layout)

        # --- Top Section: Checkout Form ---
        checkout_group = QWidget()
        checkout_layout = QHBoxLayout(checkout_group)

        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Enter Book ID")
        self.member_id_input = QLineEdit()
        self.member_id_input.setPlaceholderText("Enter Member ID")

        checkout_button = QPushButton("✅ Checkout Book")
        checkout_button.clicked.connect(self.handle_checkout)

        checkout_layout.addWidget(QLabel("New Loan:"))
        checkout_layout.addWidget(self.book_id_input)
        checkout_layout.addWidget(self.member_id_input)
        checkout_layout.addWidget(checkout_button)

        main_layout.addWidget(checkout_group)

        # --- Middle Section: Active Loans Table ---
        main_layout.addWidget(QLabel("Active Loans (Books out):"))

        self.loan_table = QTableWidget()
        self.loan_table.setColumnCount(5)
        self.loan_table.setHorizontalHeaderLabels([
            "Loan ID", "Book Title", "Member Username", "Loan Date", "Due Date"
        ])
        self.loan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.loan_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.loan_table.verticalHeader().setVisible(False)
        self.loan_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.loan_table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.loan_table)

        # --- Bottom Section: Return Button ---
        return_layout = QHBoxLayout()
        self.return_button = QPushButton("⬅️ Process Selected Return")
        self.return_button.clicked.connect(self.handle_return)

        return_layout.addStretch(1)
        return_layout.addWidget(self.return_button)

        main_layout.addLayout(return_layout)

    # --- Data & Logic Methods ---

    def load_active_loans(self):
        """Fetches and displays all unreturned loans."""
        try:
            loans = self.loan_dao.get_active_loans()
            self.loan_table.setRowCount(len(loans))

            for row_index, loan in enumerate(loans):
                # Highlight overdue loans (Due date column is index 4)

                # We assume current date check is done in the DAO, here we just check for visualization
                due_date_str = loan.get('due_date', '')
                due_date_item = QTableWidgetItem(due_date_str)

                # Simple check: If due date is in the past, color it red
                if due_date_str < datetime.now().strftime("%Y-%m-%d"):
                    due_date_item.setForeground(Qt.red)

                self.loan_table.setItem(row_index, 0, QTableWidgetItem(str(loan.get('loan_id', ''))))
                self.loan_table.setItem(row_index, 1, QTableWidgetItem(loan.get('book_title', '')))
                self.loan_table.setItem(row_index, 2, QTableWidgetItem(loan.get('member_username', '')))
                self.loan_table.setItem(row_index, 3, QTableWidgetItem(loan.get('loan_date', '')))
                self.loan_table.setItem(row_index, 4, due_date_item)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load active loans: {e}")
            self.loan_table.setRowCount(0)

    def handle_checkout(self):
        """Processes a new book checkout."""
        try:
            # Input validation
            book_id_str = self.book_id_input.text()
            member_id_str = self.member_id_input.text()

            if not book_id_str.isdigit() or not member_id_str.isdigit():
                raise ValueError("IDs must be numeric.")

            book_id = int(book_id_str)
            member_id = int(member_id_str)

            self.loan_dao.process_checkout(book_id, member_id)
            QMessageBox.information(self, "Checkout Success",
                                    f"Book ID {book_id} successfully checked out to Member ID {member_id}.")

            self.book_id_input.clear()
            self.member_id_input.clear()
            self.load_active_loans()

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric IDs for Book and Member.")
        except Exception as e:
            QMessageBox.critical(self, "Checkout Failed", str(e))

    def handle_return(self):
        """Processes the return of a selected loan."""
        selected_rows = self.loan_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an active loan from the table first.")
            return

        loan_id = int(self.loan_table.item(selected_rows[0].row(), 0).text())

        reply = QMessageBox.question(self, 'Confirm Return',
                                     f"Are you sure you want to process the return for Loan ID {loan_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                fine = self.loan_dao.process_return(loan_id)

                if fine > 0:
                    QMessageBox.warning(self, "Return Processed - Fine Due",
                                        f"Loan ID {loan_id} returned successfully. Fine calculated: ${fine:.2f}")
                else:
                    QMessageBox.information(self, "Return Success",
                                            f"Loan ID {loan_id} returned successfully. No fine due.")

                self.load_active_loans()
            except Exception as e:
                QMessageBox.critical(self, "Return Failed", str(e))