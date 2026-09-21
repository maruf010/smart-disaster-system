from database import get_connection

def add_team():
    print("\n=== ADD RESCUE TEAM ===")
    name = input("Team name: ").strip()
    specialization = input("Specialization: ").strip()
    members = int(input("Number of members: ") or 0)
    location = input("Current location node (A/B/C/D/etc): ").strip().upper()

    conn = get_connection()
    conn.execute(
        "INSERT INTO rescue_teams(name,specialization,members,current_location) VALUES (?,?,?,?)",
        (name, specialization, members, location)
    )
    conn.commit()
    conn.close()
    print("Rescue team added.")

def list_teams():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rescue_teams ORDER BY id").fetchall()
    conn.close()

    print("\n=== RESCUE TEAMS ===")
    if not rows:
        print("No rescue teams found.")
        return
    for r in rows:
        print(
            f"ID:{r['id']} | {r['name']} | Skill:{r['specialization']} | "
            f"Members:{r['members']} | Location:{r['current_location']} | Status:{r['status']}"
        )

def menu():
    while True:
        print("\n--- Rescue Team Management ---")
        print("1. Add Rescue Team")
        print("2. View Rescue Teams")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_team()
        elif c == "2":
            list_teams()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
