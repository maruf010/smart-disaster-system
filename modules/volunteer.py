from database import get_connection

def add_volunteer():
    print("\n=== ADD VOLUNTEER ===")
    name = input("Name: ").strip()
    skill = input("Skill: ").strip()
    location = input("Location: ").strip()
    contact = input("Contact: ").strip()

    conn = get_connection()
    conn.execute(
        "INSERT INTO volunteers(name,skill,location,contact) VALUES (?,?,?,?)",
        (name, skill, location, contact)
    )
    conn.commit()
    conn.close()
    print("Volunteer added.")

def list_volunteers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM volunteers ORDER BY id").fetchall()
    conn.close()

    print("\n=== VOLUNTEERS ===")
    if not rows:
        print("No volunteers found.")
        return
    for r in rows:
        print(
            f"ID:{r['id']} | {r['name']} | Skill:{r['skill']} | "
            f"Location:{r['location']} | Available:{r['availability']}"
        )

def menu():
    while True:
        print("\n--- Volunteer Management ---")
        print("1. Add Volunteer")
        print("2. View Volunteers")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_volunteer()
        elif c == "2":
            list_volunteers()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
