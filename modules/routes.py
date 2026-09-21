from database import get_connection
from algorithms.dijkstra import build_graph, shortest_path

def view_roads():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM roads ORDER BY id").fetchall()
    conn.close()

    print("\n=== ROAD NETWORK ===")
    for r in rows:
        print(
            f"ID:{r['id']} | {r['from_location']} <-> {r['to_location']} | "
            f"{r['distance']} KM | {r['status']}"
        )

def calculate_route():
    start = input("Start location node: ").strip().upper()
    end = input("Destination node: ").strip().upper()

    conn = get_connection()
    roads = conn.execute("SELECT * FROM roads").fetchall()
    conn.close()

    graph = build_graph(roads)
    distance, path = shortest_path(graph, start, end)

    if distance is None:
        print("No available route found.")
        return

    print("\n=== SHORTEST ROUTE ===")
    print(" -> ".join(path))
    print(f"Total Distance: {distance} KM")

def update_road_status():
    view_roads()
    rid = input("Road ID: ").strip()
    status = input("New status (OPEN/BLOCKED): ").strip().upper()
    if status not in ("OPEN", "BLOCKED"):
        print("Invalid status.")
        return

    conn = get_connection()
    conn.execute("UPDATE roads SET status=? WHERE id=?", (status, rid))
    conn.commit()
    conn.close()
    print("Road status updated.")

def add_road():
    a = input("From location: ").strip().upper()
    b = input("To location: ").strip().upper()
    d = float(input("Distance KM: "))
    conn = get_connection()
    conn.execute(
        "INSERT INTO roads(from_location,to_location,distance,status) VALUES (?,?,?,'OPEN')",
        (a, b, d)
    )
    conn.commit()
    conn.close()
    print("Road added.")

def menu():
    while True:
        print("\n--- Route Management ---")
        print("1. View Roads")
        print("2. Find Shortest Route")
        print("3. Block/Open Road")
        print("4. Add Road")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            view_roads()
        elif c == "2":
            calculate_route()
        elif c == "3":
            update_road_status()
        elif c == "4":
            add_road()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
