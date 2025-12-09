# member_club_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTabWidget
)
from PySide6.QtGui import QFont

from bookclub_dao import BookClubDAO


class MemberClubWidget(QWidget):

    def __init__(self, parent, member_id):
        super().__init__(parent)
        self.parent = parent
        self.member_id = member_id
        self.club_dao = BookClubDAO()
        self.setup_ui()
        self.load_club_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins for the splitter

        title_label = QLabel("✨ Your Book Clubs")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title_label)

        self.tabs = QTabWidget()

        # 1. My Clubs Tab
        self.my_clubs_widget = self._create_my_clubs_tab()
        self.tabs.addTab(self.my_clubs_widget, "My Clubs")

        # 2. Browse Clubs Tab
        self.browse_clubs_widget = self._create_browse_clubs_tab()
        self.tabs.addTab(self.browse_clubs_widget, "Browse All")

        self.tabs.currentChanged.connect(self.handle_tab_change)

        main_layout.addWidget(self.tabs)

    def _create_my_clubs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.my_clubs_table = QTableWidget()
        self.my_clubs_table.setColumnCount(3)
        self.my_clubs_table.setHorizontalHeaderLabels(["ID", "Club Name", "Joined Date"])
        self.my_clubs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.my_clubs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        layout.addWidget(self.my_clubs_table)

        self.leave_button = QPushButton("❌ Leave Selected Club")
        self.leave_button.clicked.connect(self.leave_club)
        layout.addWidget(self.leave_button)
        return widget

    def _create_browse_clubs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.browse_clubs_table = QTableWidget()
        self.browse_clubs_table.setColumnCount(4)
        self.browse_clubs_table.setHorizontalHeaderLabels(["ID", "Club Name", "Members (C/M)", "Description"])
        self.browse_clubs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.browse_clubs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.browse_clubs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.browse_clubs_table)

        self.join_button = QPushButton("✅ Join Selected Club")
        self.join_button.clicked.connect(self.join_club)
        layout.addWidget(self.join_button)
        return widget

    def handle_tab_change(self, index):
        """Reloads data when tabs are switched."""
        self.load_club_data()

    # --- Data Loading ---

    def load_club_data(self):
        """Loads data for both 'My Clubs' and 'Browse All' tabs."""

        # 1. Load My Clubs
        try:
            my_clubs = self.club_dao.get_member_clubs(self.member_id)
            self.my_clubs_table.setRowCount(len(my_clubs))
            for row_index, club in enumerate(my_clubs):
                self.my_clubs_table.setItem(row_index, 0, QTableWidgetItem(str(club['club_id'])))
                self.my_clubs_table.setItem(row_index, 1, QTableWidgetItem(club['name']))
                self.my_clubs_table.setItem(row_index, 2, QTableWidgetItem(club['join_date']))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load your clubs: {e}")
            self.my_clubs_table.setRowCount(0)

        # 2. Load All Clubs (for browsing)
        try:
            all_clubs = self.club_dao.get_all_clubs()
            self.browse_clubs_table.setRowCount(len(all_clubs))
            for row_index, club in enumerate(all_clubs):
                members_text = f"{club['current_members']}/{club['max_members']}"
                self.browse_clubs_table.setItem(row_index, 0, QTableWidgetItem(str(club['club_id'])))
                self.browse_clubs_table.setItem(row_index, 1, QTableWidgetItem(club['name']))
                self.browse_clubs_table.setItem(row_index, 2, QTableWidgetItem(members_text))
                self.browse_clubs_table.setItem(row_index, 3, QTableWidgetItem(club['description']))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load all clubs: {e}")
            self.browse_clubs_table.setRowCount(0)

    # --- Membership Actions ---

    def get_selected_club_id(self, table):
        """Helper to get the ID from a given table."""
        selected_rows = table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a club first.")
            return None
        row = selected_rows[0].row()
        item = table.item(row, 0)
        return int(item.text())

    def join_club(self):
        """Handles joining a selected club."""
        club_id = self.get_selected_club_id(self.browse_clubs_table)
        if club_id is None: return

        try:
            self.club_dao.join_club(club_id, self.member_id)
            QMessageBox.information(self, "Success", "You have successfully joined the club!")
            self.load_club_data()
            self.tabs.setCurrentWidget(self.my_clubs_widget)  # Switch to 'My Clubs'
        except Exception as e:
            QMessageBox.critical(self, "Join Failed", str(e))

    def leave_club(self):
        """Handles leaving a selected club."""
        club_id = self.get_selected_club_id(self.my_clubs_table)
        if club_id is None: return

        reply = QMessageBox.question(self, 'Confirm Leave',
                                     "Are you sure you want to leave this book club?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.club_dao.leave_club(club_id, self.member_id)
                QMessageBox.information(self, "Success", "You have successfully left the club.")
                self.load_club_data()
            except Exception as e:
                QMessageBox.critical(self, "Leave Failed", str(e))