# test_user_login.py

from user_dao import UserDAO
from db_connector import get_db_connector
import bcrypt

# --- SET YOUR TEST CREDENTIALS HERE ---
# Use one of the usernames from your SQL table
TEST_USERNAME = "lib_admin"

# NOTE: Since the password_hash in your database is a placeholder,
# you need to know the actual password you expected to work with that hash,
# OR temporarily use a known hash for testing.

# If you used the dummy hash from the setup (e.g., $2b$12$LIBRARIAN1HASH.Example),
# you'll need to know the corresponding password or temporarily insert a known hash/password pair.
TEST_PASSWORD = "some_dummy_password"


def test_login():
    dao = UserDAO()

    print(f"Attempting to log in as: {TEST_USERNAME}")

    try:
        user_data = dao.verify_login(TEST_USERNAME, TEST_PASSWORD)

        if user_data:
            print(f"✅ SUCCESS! User found: {user_data['first_name']} {user_data['last_name']}")
            print(f"Role: {user_data['role']}")
        else:
            print("❌ FAILURE: DAO returned None (Username not found OR Password check failed).")

    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

    finally:
        get_db_connector().close_connection()


if __name__ == '__main__':
    test_login()