from database import get_connection

def login():
    print("\n=== LOGIN ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()

    if user:
        print(f"\nLogin successful. Role: {user['role']}")
        return dict(user)

    print("\nInvalid username or password.")
    return None
