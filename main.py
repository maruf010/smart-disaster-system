from database import init_db
from modules.auth import login
from modules import disaster, emergency, shelter, resource, rescue, volunteer, routes, reports

def main_menu(user):
    while True:
        print("\n" + "="*56)
        print(" SMART DISASTER & EMERGENCY RESOURCE MANAGEMENT SYSTEM")
        print("="*56)
        print(f"Logged in as: {user['username']} ({user['role']})")
        print("1. Disaster Management")
        print("2. Emergency Requests")
        print("3. Shelter Management")
        print("4. Resource Management")
        print("5. Rescue Team Management")
        print("6. Volunteer Management")
        print("7. Route Management")
        print("8. Analytics & Reports")
        print("9. Logout")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            disaster.menu()
        elif choice == "2":
            emergency.menu()
        elif choice == "3":
            shelter.menu()
        elif choice == "4":
            resource.menu()
        elif choice == "5":
            rescue.menu()
        elif choice == "6":
            volunteer.menu()
        elif choice == "7":
            routes.menu()
        elif choice == "8":
            reports.menu()
        elif choice == "9":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def main():
    init_db()

    while True:
        print("\n" + "="*56)
        print(" SMART DISASTER & EMERGENCY RESOURCE MANAGEMENT SYSTEM")
        print("="*56)
        print("1. Login")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            user = login()
            if user:
                main_menu(user)
        elif choice == "0":
            print("Thank you.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
