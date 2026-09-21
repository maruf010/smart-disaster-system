from database import get_connection
import csv
import os

def dashboard():
    conn = get_connection()
    stats = {}
    stats["active_disasters"] = conn.execute(
        "SELECT COUNT(*) c FROM disasters WHERE status='ACTIVE'"
    ).fetchone()["c"]
    stats["affected"] = conn.execute(
        "SELECT COALESCE(SUM(affected_people),0) s FROM disasters WHERE status='ACTIVE'"
    ).fetchone()["s"]
    stats["critical"] = conn.execute(
        "SELECT COUNT(*) c FROM emergency_requests WHERE priority_level='CRITICAL' AND status!='RESOLVED'"
    ).fetchone()["c"]
    stats["pending"] = conn.execute(
        "SELECT COUNT(*) c FROM emergency_requests WHERE status='PENDING'"
    ).fetchone()["c"]
    stats["resolved"] = conn.execute(
        "SELECT COUNT(*) c FROM emergency_requests WHERE status='RESOLVED'"
    ).fetchone()["c"]
    stats["shelters"] = conn.execute("SELECT COUNT(*) c FROM shelters").fetchone()["c"]
    stats["capacity"] = conn.execute("SELECT COALESCE(SUM(capacity),0) s FROM shelters").fetchone()["s"]
    stats["occupied"] = conn.execute("SELECT COALESCE(SUM(occupied),0) s FROM shelters").fetchone()["s"]
    stats["teams"] = conn.execute(
        "SELECT COUNT(*) c FROM rescue_teams WHERE status='AVAILABLE'"
    ).fetchone()["c"]
    conn.close()

    print("\n" + "="*48)
    print("       DISASTER MANAGEMENT DASHBOARD")
    print("="*48)
    print(f"Active Disasters        : {stats['active_disasters']}")
    print(f"Affected People         : {stats['affected']}")
    print(f"Critical Requests       : {stats['critical']}")
    print(f"Pending Requests        : {stats['pending']}")
    print(f"Resolved Requests       : {stats['resolved']}")
    print(f"Available Shelters      : {stats['shelters']}")
    print(f"Total Shelter Capacity  : {stats['capacity']}")
    print(f"Occupied                : {stats['occupied']}")
    print(f"Available Rescue Teams  : {stats['teams']}")
    print("="*48)

def export_report():
    os.makedirs("reports", exist_ok=True)
    path = "reports/emergency_report.csv"

    conn = get_connection()
    rows = conn.execute("""
        SELECT id, requester_name, location, emergency_type,
               people_affected, injured, priority_score,
               priority_level, status, created_at
        FROM emergency_requests
        ORDER BY priority_score DESC
    """).fetchall()
    conn.close()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Request ID", "Requester", "Location", "Type",
            "People", "Injured", "Risk Score", "Priority", "Status", "Created"
        ])
        for r in rows:
            writer.writerow(list(r))

    print(f"Report exported: {path}")

def menu():
    while True:
        print("\n--- Analytics & Reports ---")
        print("1. View Dashboard")
        print("2. Export Emergency CSV Report")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            dashboard()
        elif c == "2":
            export_report()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
