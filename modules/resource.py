from database import get_connection
from algorithms.resource_allocation import proportional_allocation

def add_resource():
    print("\n=== ADD RESOURCE ===")
    name = input("Resource name: ").strip()
    category = input("Category: ").strip()
    quantity = float(input("Quantity: "))
    unit = input("Unit (packet/liter/kg/kit/etc): ").strip()
    minimum = float(input("Minimum stock alert level: ") or 0)

    conn = get_connection()
    conn.execute(
        "INSERT INTO resources(name,category,quantity,unit,minimum_stock) VALUES (?,?,?,?,?)",
        (name, category, quantity, unit, minimum)
    )
    conn.commit()
    conn.close()
    print("Resource added.")

def list_resources():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM resources ORDER BY id").fetchall()
    conn.close()

    print("\n=== RESOURCE INVENTORY ===")
    if not rows:
        print("No resources found.")
        return
    for r in rows:
        status = "CRITICAL" if r["quantity"] <= r["minimum_stock"] else "GOOD"
        print(
            f"ID:{r['id']} | {r['name']} | {r['quantity']} {r['unit']} | "
            f"Minimum:{r['minimum_stock']} | Status:{status}"
        )

def allocate_resource():
    list_resources()
    rid = int(input("\nResource ID to allocate: "))
    conn = get_connection()
    res = conn.execute("SELECT * FROM resources WHERE id=?", (rid,)).fetchone()
    if not res:
        conn.close()
        print("Resource not found.")
        return

    print(f"Available: {res['quantity']} {res['unit']}")
    amount = float(input("Total quantity to distribute: "))
    if amount > res["quantity"]:
        conn.close()
        print("Not enough stock.")
        return

    area_count = int(input("How many affected areas? "))
    area_populations = {}
    for i in range(area_count):
        area = input(f"Area {i+1} name: ").strip()
        pop = int(input(f"{area} affected population: "))
        area_populations[area] = pop

    allocations = proportional_allocation(amount, area_populations)
    print("\n=== ALLOCATION PLAN ===")
    for area, qty in allocations.items():
        print(f"{area}: {qty} {res['unit']}")
        conn.execute(
            "INSERT INTO resource_allocations(resource_id,area,population,allocated_quantity) VALUES (?,?,?,?)",
            (rid, area, area_populations[area], qty)
        )

    conn.execute("UPDATE resources SET quantity=quantity-? WHERE id=?", (amount, rid))
    conn.commit()
    conn.close()
    print("Allocation saved and stock updated.")

def menu():
    while True:
        print("\n--- Resource Management ---")
        print("1. Add Resource")
        print("2. View Inventory")
        print("3. Smart Resource Allocation")
        print("0. Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_resource()
        elif c == "2":
            list_resources()
        elif c == "3":
            allocate_resource()
        elif c == "0":
            break
        else:
            print("Invalid choice.")
