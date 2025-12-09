# add_book_dialog.py

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QPushButton, QVBoxLayout, QMessageBox, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt


class AddBookDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Add New Book")
        self.setFixedSize(400, 300)

        self.result_data = None

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Book Fields
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., The Midnight Library")

        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("e.g., 9780593086703")

        self.year_input = QSpinBox()
        self.year_input.setRange(1800, 2099)
        self.year_input.setValue(2025)

        self.copies_input = QSpinBox()
        self.copies_input.setRange(1, 100)
        self.copies_input.setValue(1)

        # Author Fields
        self.author_first_input = QLineEdit()
        self.author_first_input.setPlaceholderText("e.g., Matt")

        self.author_last_input = QLineEdit()
        self.author_last_input.setPlaceholderText("e.g., Haig")

        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("ISBN (13 digits):", self.isbn_input)
        form_layout.addRow("Year:", self.year_input)
        form_layout.addRow("Copies:", self.copies_input)
        form_layout.addRow("--- Author Details ---", QWidget())
        form_layout.addRow("Author First Name:", self.author_first_input)
        form_layout.addRow("Author Last Name:", self.author_last_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Save Book")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept_data)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def accept_data(self):
        """Validate and collect the data before closing the dialog."""
        title = self.title_input.text().strip()
        isbn = self.isbn_input.text().strip()
        year = self.year_input.value()
        copies = self.copies_input.value()
        author_first = self.author_first_input.text().strip()
        author_last = self.author_last_input.text().strip()

        if not title or not isbn or not author_first or not author_last:
            QMessageBox.warning(self, "Input Error", "Please fill in all book and author required fields.")
            return

        # Simple ISBN check (optional)
        if len(isbn) not in [10, 13] or not isbn.isdigit():
            QMessageBox.warning(self, "Input Error", "ISBN must be 10 or 13 digits and numeric.")
            return

        self.result_data = {
            'title': title,
            'isbn': isbn,
            'year': year,
            'copies': copies,
            'author_first': author_first,
            'author_last': author_last
        }

        self.accept()

    def get_data(self):
        return self.result_data