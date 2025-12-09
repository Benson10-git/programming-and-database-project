# main.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton,
    QMessageBox, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap  # QPixmap needed for potential future logo/icon use

# Import DAOs
from user_dao import UserDAO
from member_dao import MemberDAO

# Import Widgets
from librarian_main_widget import LibrarianMainWidget
from member_main_widget import MemberMainWidget
from loan_manager_widget import LoanManagerWidget
from member_loan_widget import MemberLoanWidget


# --------------------------------------------------------------------------
## I. Main Window & Application Structure
# --------------------------------------------------------------------------

class SmartLibraryApp(QMainWindow):
    """The main window containing all application views."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartLibrary Management System")

        # Increased size for better visual space
        self.setFixedSize(1000, 700)

        # --- APPLY NEW DESIGN STYLE ---
        self.setStyleSheet(self.get_dope_stylesheet())

        # Initialize DAOs
        self.user_dao = UserDAO()
        self.member_dao = MemberDAO()

        self.current_user = None

        # Central widget for managing different views (screens)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize and add views
        self.login_widget = LoginWidget(self)
        self.stack.addWidget(self.login_widget)

        # Connect signals for navigation
        self.login_widget.login_successful.connect(self.handle_login_success)

        # Initialize widget placeholders
        self.librarian_main_widget = None
        self.member_main_widget = None
        self.loan_manager_widget = None
        self.member_loan_widget = None

    def get_dope_stylesheet(self):
        """Returns the Minimalist Dark Theme stylesheet with Neon Blue accents."""
        return """
            /* GLOBAL STYLES: DARK BACKGROUND */
            QMainWindow {
                background-color: #282c34; /* Deep Anthracite Gray/Blue */
                color: #f0f0f0; /* Light text color for contrast */
                font-family: 'Segoe UI', 'Helvetica', sans-serif;
            }

            /* PUSH BUTTON: HIGH CONTRAST NEON BLUE */
            QPushButton {
                background-color: #00bfff; /* Electric Blue */
                color: #282c34; /* Dark text for contrast */
                border: none;
                border-radius: 8px; 
                padding: 12px 25px; 
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QPushButton:hover {
                background-color: #0099cc; /* Slightly darker on hover */
                box-shadow: 0 4px 10px rgba(0, 191, 255, 0.4); /* Glow effect */
            }

            QPushButton:pressed {
                background-color: #007399;
            }

            /* LINE EDIT DESIGN */
            QLineEdit {
                background-color: #3e4451; /* Slightly lighter input background */
                color: #f0f0f0;
                padding: 10px;
                border: 1px solid #5a606c;
                border-radius: 5px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #00bfff; /* Neon Blue focus highlight */
            }

            /* LABEL STYLING */
            QLabel {
                color: #f0f0f0;
                font-size: 14px;
            }

            /* Title Label Specific Styling */
            QLabel#title_label { 
                color: #00bfff; /* Neon Blue Title */
                font-size: 28px;
                font-weight: 800; /* Extra bold */
                padding-bottom: 10px;
            }

            /* Message Box Styling (Optional, might be overridden by OS) */
            QMessageBox {
                background-color: #282c34;
                color: #f0f0f0;
            }
        """

    def handle_login_success(self, user_data):
        """Called upon successful login to transition screens."""
        self.current_user = user_data
        role = user_data['role']

        QMessageBox.information(self, "Login Success",
                                f"Welcome, {user_data['first_name']}! You are logged in as a {role}.")

        self.login_widget.clear_fields()

        # --- CRITICAL NAVIGATION LOGIC ---
        if role == 'Librarian':
            if self.librarian_main_widget is None:
                # Pass the main app reference to the dashboard
                self.librarian_main_widget = LibrarianMainWidget(self)
                self.stack.addWidget(self.librarian_main_widget)

            self.stack.setCurrentWidget(self.librarian_main_widget)
            self.setWindowTitle("SmartLibrary - Librarian Dashboard")

        elif role == 'Member':
            if self.member_main_widget is None:
                # Pass member_id to the member widget for personalized actions
                self.member_main_widget = MemberMainWidget(self, user_data['user_id'])
                self.stack.addWidget(self.member_main_widget)

            self.stack.setCurrentWidget(self.member_main_widget)
            self.setWindowTitle("SmartLibrary - Member Dashboard")

    # --- Librarian Navigation Methods ---

    def show_loan_manager(self):
        """Switches to the Librarian Loan Manager screen."""
        if self.current_user is None or self.current_user.get('role') != 'Librarian':
            QMessageBox.warning(self, "Access Denied", "Librarian privileges required.")
            return

        if self.loan_manager_widget is None:
            self.loan_manager_widget = LoanManagerWidget(self)
            self.stack.addWidget(self.loan_manager_widget)

        self.loan_manager_widget.load_active_loans()
        self.stack.setCurrentWidget(self.loan_manager_widget)
        self.setWindowTitle("SmartLibrary - Loan Management")

    def show_librarian_dashboard(self):
        """Switches back to the Librarian Dashboard."""
        if self.librarian_main_widget:
            self.stack.setCurrentWidget(self.librarian_main_widget)
            self.setWindowTitle("SmartLibrary - Librarian Dashboard")

    # --- Member Navigation Methods ---

    def show_member_loan_view(self, book_id):
        """Switches to the Member Loan Confirmation screen."""
        if self.member_loan_widget is None:
            self.member_loan_widget = MemberLoanWidget(self)
            self.stack.addWidget(self.member_loan_widget)

        self.member_loan_widget.prepare_for_loan(book_id, self.current_user['user_id'])
        self.stack.setCurrentWidget(self.member_loan_widget)
        self.setWindowTitle("SmartLibrary - Checkout Confirmation")

    def show_member_dashboard(self):
        """Switches back to the Member Dashboard."""
        if self.member_main_widget:
            self.member_main_widget.load_book_data()
            self.member_main_widget.update_loan_info()
            self.stack.setCurrentWidget(self.member_main_widget)
            self.setWindowTitle("SmartLibrary - Member Dashboard")


# --------------------------------------------------------------------------
## II. Login Screen Widget
# --------------------------------------------------------------------------

class LoginWidget(QWidget):
    login_successful = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.user_dao = parent.user_dao
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Login Form Card - White Background for High Contrast
        form_widget = QWidget()
        form_widget.setObjectName("login_card")  # Needed for CSS targeting

        form_widget.setStyleSheet("""
            #login_card {
                background-color: #ffffff; /* White background */
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5); /* Strong shadow against dark background */
                padding: 40px; 
            }
            QLabel {
                color: #282c34; /* Dark text on white card */
                font-size: 14px;
            }
        """)

        # Use a stable Vertical Box Layout
        form_vbox = QVBoxLayout(form_widget)
        form_vbox.setSpacing(15)
        form_vbox.setAlignment(Qt.AlignCenter)

        # --- LOGO (Placeholder) ---
        logo_label = QLabel("📚")
        logo_label.setFont(QFont("Arial", 40))
        logo_label.setAlignment(Qt.AlignCenter)
        form_vbox.addWidget(logo_label)

        # --- LOGIN TITLE ---
        title_label = QLabel("SmartLibrary Login")
        title_label.setObjectName("title_label")  # CSS target
        title_label.setAlignment(Qt.AlignCenter)
        form_vbox.addWidget(title_label)

        # --- INPUTS (Grid for better alignment, placed inside the VBox) ---
        input_widget = QWidget()
        input_grid = QGridLayout(input_widget)
        input_grid.setSpacing(10)

        input_grid.addWidget(QLabel("Username:"), 0, 0, alignment=Qt.AlignRight)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        input_grid.addWidget(self.username_input, 0, 1)

        input_grid.addWidget(QLabel("Password:"), 1, 0, alignment=Qt.AlignRight)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        input_grid.addWidget(self.password_input, 1, 1)

        form_vbox.addWidget(input_widget)

        # --- LOGIN BUTTON (Fixed Blue Color & Stable Layout) ---
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        form_vbox.addWidget(self.login_button)

        main_layout.addWidget(form_widget, alignment=Qt.AlignCenter)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return

        try:
            user_data = self.user_dao.verify_login(username, password)

            if user_data:
                self.login_successful.emit(user_data)
            else:
                QMessageBox.critical(self, "Login Error", "Invalid username or password.")

        except Exception as e:
            QMessageBox.critical(self, "System Error", f"A system error occurred during login. Error: {e}")

    def clear_fields(self):
        self.password_input.clear()


# --------------------------------------------------------------------------
## III. Execution Block
# --------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartLibraryApp()
    window.show()
    sys.exit(app.exec())