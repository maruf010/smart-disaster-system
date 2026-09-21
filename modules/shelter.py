from database import get_connection

def add_shelter():
    print("\n=== ADD SHELTER ===")
    name = input("Shelter name: ").strip()
    location = input("Location: ").strip()
    capacity = int(input("Capacity: "))
    occupied = int(input("Current occupied: ") or 0)

    conn = get_connection()
    conn.execute(
        "INSERT INTO shelters(name,location,capacity,occupied) VALUES (?,?,?,?)",
        (name, location, capacity, occupied)
    )
    conn.commit()
    conn.close()
    print("Shelter added.")

def list_shelters():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM shelters ORDER BY id").fetchall()
    conn.close()

    print("\n=== SHELTERS ===")
    for r in rows:
        available = r["capacity"] - r["occupied"]
        status = "FULL" if available <= 0 else ("ALMOST FULL" if available <= max(5, int(r["capacity"]*0.1)) else "AVAILABLE")
        print(
            f"ID:{r['id']} | {r['name']} | {r['location']} | "
            f"Capacity:{r['capacity']} | Occupied:{r['occupied']} | "
            f"Available:{available} | {status}"
        )
    if not rows:
        print("No shelters found.")

def recommend_shelter():
    required = int(input("Required seats: "))
    conn = get_connection()
    rows = conn.execute("SELECT * FROM shelters").fetchall()
    conn.close()

    suitable = []
    for r in rows:
        available = r["capacity"] - r["occupied"]
        if available >= required:
            suitable.append((available, r))

    if not suitable:
        print("No shelter has enough capacity.")
        return

    suitable.sort(key=lambda x: x[0])
    _, r = suitable[0]
    print("\nRecommended Shelter:")
    print(f"{r['name']} | Location: {r['location']} | Available Seats: {r['capacity']-r['occupied']}")

def menu():
    while True:
        print("\n--- Shelter Management ---")
        print("1. Add Shelter")
        print("2. View Shelters")
        print("3. Recommend Shelter")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_shelter()
        elif c == "2":
            list_shelters()
        elif c == "3":
            recommend_shelter()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
