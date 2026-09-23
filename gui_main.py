import sys
from database import init_db
from gui.login import LoginWindow
from gui.app import App
from gui.citizen_portal import CitizenPortal

def start_application():
    # Ensure database tables and initial seed data exist
    init_db()

    def launch_main_app(user_data):
        role = user_data.get("role", "CITIZEN").upper()
        if role == "ADMIN":
            app = App(user_data, on_logout=launch_login)
        else:
            app = CitizenPortal(user_data, on_logout=launch_login)
        app.mainloop()

    def launch_login():
        login_win = LoginWindow(on_login_success=launch_main_app)
        login_win.mainloop()

    launch_login()

if __name__ == "__main__":
    start_application()
