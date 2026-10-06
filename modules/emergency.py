from database import get_connection
from algorithms.risk_score import calculate_risk

def add_request():
    print("\n=== CREATE EMERGENCY REQUEST ===")
    disaster_id = input("Disaster ID (optional): ").strip() or None
    requester = input("Requester name: ").strip()
    location = input("Location: ").strip()
    etype = input("Emergency type: ").strip()
    people = int(input("People affected: ") or 0)
    injured = int(input("Injured people: ") or 0)
    child = int(input("Children/Elderly count: ") or 0)
    life = input("Life threat? (y/n): ").strip().lower() == "y"
    shortage = input("Critical resource shortage? (y/n): ").strip().lower() == "y"

    score, level = calculate_risk(life, injured, child, people, shortage)

    conn = get_connection()
    conn.execute("""
        INSERT INTO emergency_requests(
            disaster_id, requester_name, location, emergency_type,
            people_affected, injured, children_elderly,
            life_threat, resource_shortage, priority_score, priority_level
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        disaster_id, requester, location, etype,
        people, injured, child,
        int(life), int(shortage), score, level
    ))
    conn.commit()
    conn.close()

    print(f"\nRequest submitted.")
    print(f"Risk Score: {score}/100")
    print(f"Priority: {level}")

def list_requests():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM emergency_requests
        ORDER BY priority_score DESC, id ASC
    """).fetchall()
    conn.close()

    print("\n=== EMERGENCY PRIORITY QUEUE ===")
    if not rows:
        print("No emergency requests.")
        return
    from utils.helper import format_datetime
    for r in rows:
        t_str = format_datetime(r['created_at']) if 'created_at' in r.keys() else 'N/A'
        print(
            f"ER-{r['id']:04d} | {r['emergency_type']} | "
            f"📍 {r['location']} | Score:{r['priority_score']} | "
            f"{r['priority_level']} | Status:{r['status']} | 🕒 {t_str}"
        )

def resolve_request():
    rid = input("Enter request ID: ").strip()
    conn = get_connection()
    conn.execute("UPDATE emergency_requests SET status='RESOLVED' WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    print("Request marked as resolved.")

def menu():
    while True:
        print("\n--- Emergency Requests ---")
        print("1. Create Request")
        print("2. View Priority Queue")
        print("3. Resolve Request")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_request()
        elif c == "2":
            list_requests()
        elif c == "3":
            resolve_request()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
