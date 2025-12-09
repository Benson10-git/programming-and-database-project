# add_member_dialog.py

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)


class AddMemberDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Add New Member")
        self.setFixedSize(400, 250)

        self.result_data = None

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Member Fields
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Alice")

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Smith")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("asmith")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("temp_password")

        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Create Member")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept_data)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def accept_data(self):
        """Validate and collect the data."""
        data = {
            'first_name': self.first_name_input.text().strip(),
            'last_name': self.last_name_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
        }

        if not all(data.values()):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        self.result_data = data
        self.accept()

    def get_data(self):
        return self.result_data