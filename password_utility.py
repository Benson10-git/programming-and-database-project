# password_utility.py
import bcrypt
import sys


def generate_hash(password):
    """Generates a bcrypt hash for a given plaintext password."""
    # Encode the password to bytes
    encoded_password = password.encode('utf-8')

    # Generate the salt and hash the password
    # The 'gensalt()' function handles generating a secure, random salt.
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt()).decode('utf-8')

    return hashed_password


if __name__ == '__main__':
    # Usage: python password_utility.py <username> <base_password>
    if len(sys.argv) != 3:
        print("Usage: python password_utility.py <username> <base_password>")
        print("Example: python password_utility.py lib_admin 123")
        print("         (This creates the hash for the password 'lib_admin123')")
        sys.exit(1)

    username = sys.argv[1]
    base_password = sys.argv[2]

    # The actual password is: username + base_password, e.g., benson123
    full_password = username + base_password

    hash_output = generate_hash(full_password)

    print("\n--- PASSWORD HASH GENERATOR ---")
    print(f"Target Username: {username}")
    print(f"Full Password:   {full_password}")
    print(f"Bcrypt Hash:     {hash_output}")
    print("\n>>> COPY THIS HASH STRING AND PASTE IT INTO THE SQL SCRIPT. <<<")