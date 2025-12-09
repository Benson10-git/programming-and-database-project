# member_management_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from member_management_dao import MemberManagementDAO
from add_member_dialog import AddMemberDialog


class MemberManagementWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.member_dao = MemberManagementDAO()
        self.setup_ui()
        self.load_member_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("👤 Member Management Hub")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title_label)

        # Action Button Layout
        button_layout = QHBoxLayout()
        self.add_member_button = QPushButton("➕ Register New Member")
        self.add_member_button.clicked.connect(self.add_member)
        self.refresh_button = QPushButton("🔄 Refresh List")
        self.refresh_button.clicked.connect(self.load_member_data)

        button_layout.addWidget(self.add_member_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        main_layout.addSpacing(10)

        # Member Table
        self.member_table = QTableWidget()
        self.member_table.setColumnCount(5)
        self.member_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Username", "Active Loans"
        ])
        self.member_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.member_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.member_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.member_table.verticalHeader().setVisible(False)
        self.member_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.member_table)

    def load_member_data(self):
        """Fetches and displays all members."""
        try:
            members = self.member_dao.get_all_members()
            self.member_table.setRowCount(len(members))

            for row_index, member in enumerate(members):
                self.member_table.setItem(row_index, 0, QTableWidgetItem(str(member['id'])))
                self.member_table.setItem(row_index, 1, QTableWidgetItem(member['first_name']))
                self.member_table.setItem(row_index, 2, QTableWidgetItem(member['last_name']))
                self.member_table.setItem(row_index, 3, QTableWidgetItem(member['username']))
                self.member_table.setItem(row_index, 4, QTableWidgetItem(str(member['current_loans'])))

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load member list: {e}")
            self.member_table.setRowCount(0)

    def add_member(self):
        """Opens dialog and calls DAO to create a new member."""
        dialog = AddMemberDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data: return

            try:
                new_id = self.member_dao.create_new_member(
                    data['first_name'],
                    data['last_name'],
                    data['username'],
                    data['password']
                )
                QMessageBox.information(self, "Success",
                                        f"New Member Account created!\nID: {new_id}\nUsername: {data['username']}")
                self.load_member_data()  # Refresh the table
            except Exception as e:
                QMessageBox.critical(self, "Registration Failed", str(e))