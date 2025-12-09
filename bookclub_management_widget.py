# bookclub_management_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog
)
from PySide6.QtGui import QFont

from bookclub_dao import BookClubDAO
from add_club_dialog import AddClubDialog  # Import the dialog


class BookClubManagementWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.club_dao = BookClubDAO()
        self.setup_ui()
        self.load_club_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("👥 Book Club Management")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title_label)

        # Table
        self.club_table = QTableWidget()
        self.club_table.setColumnCount(4)
        self.club_table.setHorizontalHeaderLabels([
            "ID", "Club Name", "Members (Current/Max)", "Description"
        ])
        self.club_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.club_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.club_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.club_table.verticalHeader().setVisible(False)
        self.club_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.club_table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.club_table)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_club_button = QPushButton("➕ Create New Club")
        self.delete_club_button = QPushButton("🗑️ Delete Selected Club")

        self.add_club_button.clicked.connect(self.add_club)
        self.delete_club_button.clicked.connect(self.delete_club)

        button_layout.addWidget(self.add_club_button)
        button_layout.addWidget(self.delete_club_button)
        button_layout.addStretch(1)

        main_layout.addLayout(button_layout)

    def load_club_data(self):
        """Fetches and displays all book clubs."""
        try:
            clubs = self.club_dao.get_all_clubs()
            self.club_table.setRowCount(len(clubs))

            for row_index, club in enumerate(clubs):
                members_text = f"{club['current_members']}/{club['max_members']}"

                self.club_table.setItem(row_index, 0, QTableWidgetItem(str(club['club_id'])))
                self.club_table.setItem(row_index, 1, QTableWidgetItem(club['name']))
                self.club_table.setItem(row_index, 2, QTableWidgetItem(members_text))
                self.club_table.setItem(row_index, 3, QTableWidgetItem(club['description']))

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load club data: {e}")
            self.club_table.setRowCount(0)

    def get_selected_club_id(self):
        """Helper function to get the ID of the currently selected club."""
        selected_rows = self.club_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a club from the table first.")
            return None
        row = selected_rows[0].row()
        item = self.club_table.item(row, 0)
        return int(item.text())

    def add_club(self):
        """Opens dialog and calls DAO to create a new club."""
        dialog = AddClubDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data: return

            try:
                self.club_dao.create_club(data['name'], data['description'], data['max_members'])
                QMessageBox.information(self, "Success", f"Book Club '{data['name']}' created successfully.")
                self.load_club_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to create club. Error: {e}")

    def delete_club(self):
        """Deletes the selected club using the DAO method."""
        club_id = self.get_selected_club_id()
        if club_id is None: return

        reply = QMessageBox.question(self, 'Confirm Delete',
                                     f"Are you sure you want to permanently delete Club ID {club_id}? (This will remove all members)",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.club_dao.delete_club(club_id)
                QMessageBox.information(self, "Success", f"Club ID {club_id} deleted successfully.")
                self.load_club_data()
            except Exception as e:
                QMessageBox.critical(self, "Deletion Error", str(e))