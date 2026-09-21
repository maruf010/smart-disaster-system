from database import get_connection

def add_disaster():
    print("\n=== ADD DISASTER ===")
    name = input("Disaster name: ").strip()
    dtype = input("Type (Flood/Fire/Cyclone/Earthquake/etc): ").strip()
    area = input("Affected area: ").strip()
    severity = input("Severity (LOW/MODERATE/HIGH/CRITICAL): ").strip().upper()
    affected = int(input("Affected people: ") or 0)

    conn = get_connection()
    conn.execute(
        "INSERT INTO disasters(name,type,area,severity,affected_people) VALUES (?,?,?,?,?)",
        (name, dtype, area, severity, affected)
    )
    conn.commit()
    conn.close()
    print("Disaster added successfully.")

def list_disasters():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM disasters ORDER BY id DESC").fetchall()
    conn.close()

    print("\n=== DISASTERS ===")
    if not rows:
        print("No disasters found.")
        return
    for r in rows:
        print(
            f"ID:{r['id']} | {r['name']} | Type:{r['type']} | "
            f"Area:{r['area']} | Severity:{r['severity']} | "
            f"Affected:{r['affected_people']} | Status:{r['status']}"
        )

def close_disaster():
    did = input("Enter disaster ID to close: ").strip()
    conn = get_connection()
    conn.execute("UPDATE disasters SET status='RESOLVED' WHERE id=?", (did,))
    conn.commit()
    conn.close()
    print("Disaster status updated.")

def menu():
    while True:
        print("\n--- Disaster Management ---")
        print("1. Add Disaster")
        print("2. View Disasters")
        print("3. Close Disaster")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_disaster()
        elif c == "2":
            list_disasters()
        elif c == "3":
            close_disaster()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
