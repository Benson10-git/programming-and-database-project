# test_loan_workflow.py

from datetime import date
from loan_dao import LoanDAO
from db_connector import get_db_connector


def run_loan_tests():
    """Tests the full borrowing and returning workflow."""

    # NOTE: These IDs rely on the sample data you inserted into the database.
    # Member ID 4 (Alice) has 1 existing loan.
    # Book ID 7 ('The Shining') has available copies.
    TEST_MEMBER_ID = 4
    TEST_BOOK_ID = 7

    loan_dao = LoanDAO()

    print("--- 📚 SmartLibrary Loan Workflow Test Script ---")

    # --- Test 1: Successful First Loan (Loan count 1 -> 2) ---
    print("\n--- 1. Attempting Loan 1 (Book ID 7) ---")

    success, result = loan_dao.create_loan(TEST_BOOK_ID, TEST_MEMBER_ID)

    if success:
        print(f"✅ SUCCESS: Loan created with ID: {result}")
        print(f"   Member {TEST_MEMBER_ID}'s loan count should now be 2.")
        loan_id_1 = result
    else:
        print(f"❌ FAILURE: Loan rejected. Reason: {result}")
        loan_id_1 = None

        # --- Test 2: Successful Second Loan (Loan count 2 -> 3) ---
    TEST_BOOK_ID_2 = 8
    print("\n--- 2. Attempting Loan 2 (Book ID 8) ---")

    success, result = loan_dao.create_loan(TEST_BOOK_ID_2, TEST_MEMBER_ID)

    if success:
        print(f"✅ SUCCESS: Loan created with ID: {result}")
        print(f"   Member {TEST_MEMBER_ID}'s loan count should now be 3 (MAX).")
    else:
        print(f"❌ FAILURE: Loan rejected. Reason: {result}")

    # --- Test 3: Loan Rejection (Business Rule: Max 3 Loans) ---
    # This should fail and confirm the business rule is enforced.
    print("\n--- 3. Attempting Loan 3 (Should Fail: Max 3 Loans) ---")

    success, result = loan_dao.create_loan(TEST_BOOK_ID, TEST_MEMBER_ID)

    if not success and "Max 3 loans reached" in str(result):
        print(f"✅ SUCCESS: Loan correctly rejected. Reason: {result}")
    else:
        print("❌ FAILURE: Loan incorrectly allowed or failed for wrong reason.")

    # --- Test 4: Check Overdue Loans ---
    # This checks for Diana's overdue loan inserted in the SQL script.
    print("\n--- 4. Checking Overdue Loans (Should show Diana Prince) ---")
    overdue_loans = loan_dao.get_overdue_loans()
    if overdue_loans:
        print(f"⚠️ Found {len(overdue_loans)} Overdue Loan(s).")
        print(
            f"   Example: {overdue_loans[0]['title']} (Due: {overdue_loans[0]['due_date']}) by {overdue_loans[0]['first_name']}")
    else:
        print("✅ No loans currently overdue.")

    # --- Test 5: Successful Return (Loan count 3 -> 2) ---
    if loan_id_1:
        print(f"\n--- 5. Returning Loan {loan_id_1} (No Fine Expected) ---")
        success, fine = loan_dao.return_loan(loan_id_1)

        if success:
            print(f"✅ SUCCESS: Book returned. Fine calculated: ${fine}")
            print(f"   Member {TEST_MEMBER_ID}'s loan count should now be 2.")
        else:
            print(f"❌ FAILURE: Return failed. Reason: {fine}")

    print("\n--- Testing Complete ---")
    get_db_connector().close_connection()


if __name__ == '__main__':
    run_loan_tests()