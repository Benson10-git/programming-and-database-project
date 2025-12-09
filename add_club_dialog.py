# add_club_dialog.py

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)


class AddClubDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Create New Book Club")
        self.setFixedSize(400, 350)

        self.result_data = None

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Club Fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Fantasy Bookworms")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("A club for discussing classic and modern fantasy novels.")

        self.max_members_input = QSpinBox()
        self.max_members_input.setRange(5, 50)
        self.max_members_input.setValue(15)

        form_layout.addRow("Club Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Max Members:", self.max_members_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Create Club")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept_data)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def accept_data(self):
        """Validate and collect the data."""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        max_members = self.max_members_input.value()

        if not name or not description:
            QMessageBox.warning(self, "Input Error", "Club Name and Description are required.")
            return

        self.result_data = {
            'name': name,
            'description': description,
            'max_members': max_members,
        }

        self.accept()

    def get_data(self):
        return self.result_data