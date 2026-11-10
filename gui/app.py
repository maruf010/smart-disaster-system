import customtkinter as ctk
from gui.theme import Theme
from gui.icons import get_icon
from gui.views.dashboard_view import DashboardView
from gui.views.disaster_view import DisasterView
from gui.views.emergency_view import EmergencyView
from gui.views.shelter_view import ShelterView
from gui.views.resource_view import ResourceView
from gui.views.rescue_view import RescueView
from gui.views.volunteer_view import VolunteerView
from gui.views.routes_view import RoutesView
from gui.views.reports_view import ReportsView

class App(ctk.CTk):
    def __init__(self, user, on_logout=None):
        super().__init__()
        self.user = user
        self.on_logout = on_logout

        self.title("SDERMS - Smart Disaster & Emergency Resource System")
        self.geometry("1260x780")
        self.minsize(1100, 700)

        # Set default appearance
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=Theme.BG_ROOT)

        self._center_window(1220, 760)

        # Layout: Sidebar (fixed width), Main Area (expands)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_sidebar()
        self._build_content_area()

        # Select default view
        self._select_tab("dashboard")

    def _on_close(self):
        self.destroy()

    def _center_window(self, width, height):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(14, weight=1)  # Spacer pushing profile to bottom

        # Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 14))

        brand_top = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_top.pack(fill="x")

        brand_icon = get_icon("shield", color=Theme.PRIMARY, size=24)
        logo_lbl = ctk.CTkLabel(
            brand_top,
            text="  SDERMS",
            image=brand_icon,
            compound="left",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        logo_lbl.pack(side="left")

        ver_badge = ctk.CTkLabel(
            brand_top,
            text=" PRO ",
            fg_color=Theme.PRIMARY,
            text_color="white",
            corner_radius=6,
            font=Theme.font_badge()
        )
        ver_badge.pack(side="left", padx=8)

        sub_lbl = ctk.CTkLabel(
            brand_frame,
            text="Smart Disaster Response System",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Divider
        div1 = ctk.CTkFrame(self.sidebar, height=1, fg_color=Theme.BORDER_COLOR_LIGHT)
        div1.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

        # Nav items grouped
        self.nav_buttons = {}
        row_idx = 2

        # Group 1: Operations
        self._add_nav_heading(row_idx, "OPERATIONS & TRIAGE")
        row_idx += 1

        nav_ops = [
            ("dashboard", "Executive Dashboard", "dashboard"),
            ("disasters", "Disaster Monitoring", "disaster"),
            ("emergencies", "Emergency Queue", "emergency"),
        ]
        for key, label, icon_name in nav_ops:
            self._add_nav_btn(row_idx, key, label, icon_name)
            row_idx += 1

        # Group 2: Logistics & Dispatch
        self._add_nav_heading(row_idx, "LOGISTICS & FLEET")
        row_idx += 1

        nav_logistics = [
            ("shelters", "Shelter Centers", "shelter"),
            ("resources", "Supply Inventories", "resource"),
            ("rescue", "Rescue Squads", "rescue"),
            ("volunteers", "Volunteers Roster", "volunteer"),
            ("routes", "Route Navigation", "routes"),
        ]
        for key, label, icon_name in nav_logistics:
            self._add_nav_btn(row_idx, key, label, icon_name)
            row_idx += 1

        # Group 3: Analytics
        self._add_nav_heading(row_idx, "AUDIT & INTELLIGENCE")
        row_idx += 1

        self._add_nav_btn(row_idx, "reports", "Reports & Analytics", "reports")
        row_idx += 1

        # Bottom Profile Card
        bottom_frame = ctk.CTkFrame(
            self.sidebar,
            corner_radius=12,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        bottom_frame.grid(row=15, column=0, sticky="ew", padx=12, pady=(0, 14))
        bottom_frame.grid_columnconfigure(0, weight=1)

        # User row
        user_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        user_row.pack(fill="x", padx=10, pady=(10, 6))

        user_avatar_icon = get_icon("user", color=Theme.TEXT_MUTED, size=22)
        user_avatar = ctk.CTkLabel(
            user_row,
            image=user_avatar_icon,
            text="",
            width=28
        )
        user_avatar.pack(side="left", padx=(0, 6))

        user_info = ctk.CTkFrame(user_row, fg_color="transparent")
        user_info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            user_info,
            text=self.user['username'],
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            user_info,
            text=f"Role: {self.user['role']}",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w")

        # Theme Switch
        self.theme_switch = ctk.CTkSwitch(
            bottom_frame,
            text="Dark Mode",
            command=self._toggle_theme,
            font=Theme.font_small(),
            progress_color=Theme.PRIMARY
        )
        self.theme_switch.select()
        self.theme_switch.pack(padx=12, pady=(4, 6), anchor="w")

        # Sign out button
        btn_logout = ctk.CTkButton(
            bottom_frame,
            text="Sign Out",
            height=30,
            corner_radius=8,
            fg_color=Theme.DANGER_BG,
            text_color=Theme.DANGER,
            hover_color=Theme.BORDER_COLOR,
            font=Theme.font_body_bold(),
            command=self._handle_logout
        )
        btn_logout.pack(fill="x", padx=10, pady=(4, 10))

    def _add_nav_heading(self, row, text):
        lbl = ctk.CTkLabel(
            self.sidebar,
            text=text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_SUBTLE,
            anchor="w"
        )
        lbl.grid(row=row, column=0, sticky="w", padx=18, pady=(8, 2))

    def _add_nav_btn(self, row, key, label, icon_name):
        inactive_icon = get_icon(icon_name, color=("#475569", "#94A3B8"), size=17)
        active_icon = get_icon(icon_name, color="#FFFFFF", size=17)

        btn = ctk.CTkButton(
            self.sidebar,
            text=f"  {label}",
            image=inactive_icon,
            compound="left",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            text_color=Theme.TEXT_MUTED,
            hover_color=Theme.PRIMARY_LIGHT,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="normal"),
            command=lambda k=key: self._select_tab(k)
        )
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=1)
        self.nav_buttons[key] = (btn, active_icon, inactive_icon)

    def _build_content_area(self):
        # Container
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Lazy views dictionary
        self.views = {
            "dashboard": DashboardView(self.content_container, navigate_callback=self._select_tab),
            "disasters": DisasterView(self.content_container),
            "emergencies": EmergencyView(self.content_container),
            "shelters": ShelterView(self.content_container),
            "resources": ResourceView(self.content_container),
            "rescue": RescueView(self.content_container),
            "volunteers": VolunteerView(self.content_container),
            "routes": RoutesView(self.content_container),
            "reports": ReportsView(self.content_container),
        }

    def _select_tab(self, key):
        # Update navigation highlights
        for k, (btn, active_icon, inactive_icon) in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=Theme.PRIMARY,
                    text_color="white",
                    hover_color=Theme.PRIMARY_HOVER,
                    image=active_icon,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_MUTED,
                    hover_color=Theme.PRIMARY_LIGHT,
                    image=inactive_icon,
                    font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="normal")
                )

        # Switch view
        for k, view in self.views.items():
            if k == key:
                view.grid(row=0, column=0, sticky="nsew")
                if hasattr(view, "refresh"):
                    view.refresh()
            else:
                view.grid_forget()

    def _toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="Light Mode")

    def _handle_logout(self):
        self.destroy()
        if self.on_logout:
            self.on_logout()
