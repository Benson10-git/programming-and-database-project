# librarian_main_widget.py (UPDATED)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTabWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import DAOs
from book_dao import BookDAO

# Import Widgets/Dialogs
from add_book_dialog import AddBookDialog
from bookclub_management_widget import BookClubManagementWidget
from member_management_widget import MemberManagementWidget  # <--- NEW IMPORT


class LibrarianMainWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.book_dao = BookDAO()

        self.tabs = QTabWidget()
        self.setup_tabs()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

        # Connect tab change to refresh club data
        self.tabs.currentChanged.connect(self.handle_tab_change)

    def handle_tab_change(self, index):
        """Refreshes the data when switching tabs."""
        widget = self.tabs.widget(index)
        if widget == self.club_widget:
            self.club_widget.load_club_data()
        elif widget == self.catalog_widget:
            self.load_book_data()
        # No refresh needed for Member Management tab

    def setup_tabs(self):
        # 1. Book Catalog Tab
        self.catalog_widget = self._create_catalog_widget()
        self.tabs.addTab(self.catalog_widget, "📖 Book Catalog")

        # 2. Book Club Management Tab
        self.club_widget = BookClubManagementWidget(self)
        self.tabs.addTab(self.club_widget, "👥 Book Clubs")

        # 3. Member Management Tab <--- NEW TAB
        self.member_widget = MemberManagementWidget(self)
        self.tabs.addTab(self.member_widget, "👤 Member Management")

    def _create_catalog_widget(self):
        """Creates the UI for the Book Catalog tab."""
        # ... (rest of the _create_catalog_widget method is unchanged) ...
        # (This remains exactly as provided in the previous full update)

        catalog_container = QWidget()
        main_layout = QVBoxLayout(catalog_container)

        # Title and Search
        title_label = QLabel("📚 Manage Library Inventory")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title_label)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Title, Author, or ISBN...")
        self.search_input.returnPressed.connect(self.search_books)
        search_button = QPushButton("🔍 Search")
        search_button.clicked.connect(self.search_books)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Data Table
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(6)
        self.book_table.setHorizontalHeaderLabels([
            "ID", "Title", "Author(s)", "ISBN", "Total Copies", "Available"
        ])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.book_table.verticalHeader().setVisible(False)
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.book_table)

        # CRUD and Workflow Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Add New Book")
        self.add_button.clicked.connect(self.add_book)
        self.edit_button = QPushButton("✏️ Edit Selected Book")
        self.edit_button.clicked.connect(self.edit_book)
        self.delete_button = QPushButton("🗑️ Delete Selected Book")
        self.delete_button.clicked.connect(self.delete_book)
        self.loan_button = QPushButton("➡️ Process Loan/Return")
        self.loan_button.clicked.connect(self.parent.show_loan_manager)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.loan_button)
        main_layout.addLayout(button_layout)

        return catalog_container

    # --- Data Handling Methods (Unchanged) ---
    # ... load_book_data, search_books, get_selected_book_id, add_book, edit_book, delete_book
    # (The methods below are unchanged from the previous version)

    def load_book_data(self, books=None):
        """Loads data from the DAO into the QTableWidget."""

        if books is None:
            try:
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
            self.book_table.setItem(row_index, 4, QTableWidgetItem(str(book.get('total_copies', 0))))
            self.book_table.setItem(row_index, 5, QTableWidgetItem(str(book.get('available_copies', 0))))

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

    # --- CRUD Implementation Methods ---

    def get_selected_book_id(self):
        """Helper function to get the ID of the currently selected book."""
        selected_rows = self.book_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a book from the table first.")
            return None
        row = selected_rows[0].row()
        item = self.book_table.item(row, 0)
        return int(item.text())

    def add_book(self):
        """Opens dialog, calls DAO to add book/author, and refreshes the table."""
        dialog = AddBookDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data: return

            title = data['title']
            isbn = data['isbn']
            year = data['year']
            copies = data['copies']
            author_first = data['author_first']
            author_last = data['author_last']

            try:
                author_id = self.book_dao.add_author(author_first, author_last)
                if author_id:
                    self.book_dao.add_book(title, isbn, year, copies, [author_id])
                    QMessageBox.information(self, "Success", f"Book '{title}' added successfully.")
                    self.load_book_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add book. Error: {e}")

    def edit_book(self):
        """Placeholder for editing a selected book."""
        book_id = self.get_selected_book_id()
        if book_id is None: return
        QMessageBox.information(self, "Feature Pending",
                                f"Editing book ID {book_id} functionality will be implemented next.")

    def delete_book(self):
        """Deletes the selected book using the DAO method."""
        book_id = self.get_selected_book_id()
        if book_id is None: return

        reply = QMessageBox.question(self, 'Confirm Delete',
                                     f"Are you sure you want to permanently delete Book ID {book_id}? (Must not have active loans)",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.book_dao.delete_book_by_id(book_id)
                QMessageBox.information(self, "Success", f"Book ID {book_id} deleted successfully.")
                self.load_book_data()
            except Exception as e:
                QMessageBox.critical(self, "Deletion Error", str(e))