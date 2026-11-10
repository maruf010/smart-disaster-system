import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from gui.theme import Theme
from gui.icons import get_icon

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success

        self.title("SDERMS - Disaster Emergency Portal")
        self.geometry("480x640")
        self.resizable(False, False)

        # Apply root background
        self.configure(fg_color=Theme.BG_ROOT)

        self._center_window(480, 640)
        

        # Current modes:
        # role_mode: 'CITIZEN' or 'ADMIN' (Default: 'CITIZEN')
        # citizen_submode: 'LOGIN' or 'REGISTER'
        self.role_mode = "CITIZEN"
        self.citizen_submode = "LOGIN"

        self._build_ui()
        self._render_view()

    def _center_window(self, width, height):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        # Prepare single-color icons
        self.brand_icon = get_icon("shield", color=Theme.PRIMARY, size=28)
        self.cit_icon_active = get_icon("users", color="#FFFFFF", size=16)
        self.cit_icon_inactive = get_icon("users", color=("#475569", "#94A3B8"), size=16)
        self.adm_icon_active = get_icon("lock", color="#FFFFFF", size=16)
        self.adm_icon_inactive = get_icon("lock", color=("#475569", "#94A3B8"), size=16)

        # Outer Card with subtle elevated border
        self.card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        self.card.pack(fill="both", expand=True, padx=22, pady=18)
        self.card.grid_columnconfigure(0, weight=1)

        # Header Glow Icon
        icon_box = ctk.CTkFrame(
            self.card,
            width=50,
            height=50,
            corner_radius=13,
            fg_color=Theme.PRIMARY_LIGHT,
            border_width=1,
            border_color=Theme.BORDER_ACCENT
        )
        icon_box.pack(pady=(16, 4))
        icon_box.grid_propagate(False)

        icon_lbl = ctk.CTkLabel(icon_box, image=self.brand_icon, text="")
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            self.card,
            text="SDERMS DISASTER PORTAL",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=19, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            self.card,
            text="Smart Disaster & Emergency Resource System",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        )
        subtitle.pack(pady=(1, 10))

        # Top Role Switcher: Citizen vs Admin side-by-side
        self.switcher_frame = ctk.CTkFrame(
            self.card,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        self.switcher_frame.pack(fill="x", padx=24, pady=(0, 10))
        self.switcher_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_citizen_tab = ctk.CTkButton(
            self.switcher_frame,
            text="  Citizen Portal",
            image=self.cit_icon_active,
            compound="left",
            height=34,
            corner_radius=6,
            font=Theme.font_body_bold(),
            command=self._switch_to_citizen
        )
        self.btn_citizen_tab.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        self.btn_admin_tab = ctk.CTkButton(
            self.switcher_frame,
            text="  Admin Console",
            image=self.adm_icon_inactive,
            compound="left",
            height=34,
            corner_radius=6,
            font=Theme.font_body_bold(),
            command=self._switch_to_admin
        )
        self.btn_admin_tab.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        # Dynamic Content Container
        self.content_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        self.content_container.grid_columnconfigure(0, weight=1)

    def _render_view(self):
        # Clear previous dynamic content
        for w in self.content_container.winfo_children():
            w.destroy()

        if self.role_mode == "CITIZEN":
            self.btn_citizen_tab.configure(
                fg_color=Theme.PRIMARY,
                text_color="white",
                image=self.cit_icon_active,
                hover_color=Theme.PRIMARY_HOVER
            )
            self.btn_admin_tab.configure(
                fg_color="transparent",
                text_color=Theme.TEXT_MUTED,
                image=self.adm_icon_inactive,
                hover_color=Theme.PRIMARY_LIGHT
            )

            if self.citizen_submode == "LOGIN":
                self._render_citizen_login()
            else:
                self._render_citizen_register()

        else:  # ADMIN Mode
            self.btn_citizen_tab.configure(
                fg_color="transparent",
                text_color=Theme.TEXT_MUTED,
                image=self.cit_icon_inactive,
                hover_color=Theme.PRIMARY_LIGHT
            )
            self.btn_admin_tab.configure(
                fg_color=Theme.PRIMARY,
                text_color="white",
                image=self.adm_icon_active,
                hover_color=Theme.PRIMARY_HOVER
            )
            self._render_admin_login()

    # ==================== CITIZEN LOGIN VIEW ====================
    def _render_citizen_login(self):
        # Badge
        badge_row = ctk.CTkFrame(self.content_container, fg_color="transparent")
        badge_row.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(
            badge_row,
            text="PUBLIC CITIZEN ACCESS",
            font=Theme.font_badge(),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left")

        ctk.CTkLabel(
            badge_row,
            text=" ● CITIZEN ",
            fg_color=Theme.SUCCESS_BG,
            text_color=Theme.SUCCESS,
            corner_radius=6,
            font=Theme.font_badge()
        ).pack(side="right")

        # Username
        ctk.CTkLabel(self.content_container, text="USERNAME", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(4, 2))
        self.ent_cit_user = ctk.CTkEntry(
            self.content_container,
            placeholder_text="Enter your username",
            height=36,
            corner_radius=7,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_cit_user.pack(fill="x", pady=(0, 6))

        # Password
        ctk.CTkLabel(self.content_container, text="PASSWORD", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(4, 2))
        self.ent_cit_pass = ctk.CTkEntry(
            self.content_container,
            placeholder_text="Enter your password",
            show="*",
            height=36,
            corner_radius=7,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_cit_pass.pack(fill="x", pady=(0, 6))
        self.ent_cit_pass.bind("<Return>", lambda e: self._attempt_citizen_login())

        # Error notification label
        self.lbl_cit_error = ctk.CTkLabel(
            self.content_container,
            text="",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.DANGER
        )
        self.lbl_cit_error.pack(pady=(0, 4))

        # Sign In Button
        btn_cit_login = ctk.CTkButton(
            self.content_container,
            text="Sign In to Citizen Portal",
            height=38,
            corner_radius=8,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_body_bold(),
            command=self._attempt_citizen_login
        )
        btn_cit_login.pack(fill="x", pady=(0, 10))

        # Divider: New to SDERMS?
        div_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        div_frame.pack(fill="x", pady=(4, 6))
        div_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            div_frame,
            text="────────  Don't have an account?  ────────",
            font=Theme.font_small(),
            text_color=Theme.TEXT_SUBTLE
        ).pack()

        # Register Button
        btn_create = ctk.CTkButton(
            self.content_container,
            text="Create New Citizen Account",
            height=34,
            corner_radius=8,
            fg_color=Theme.PRIMARY_LIGHT,
            text_color=Theme.PRIMARY,
            hover_color=Theme.BORDER_COLOR,
            font=Theme.font_body_bold(),
            command=self._show_register
        )
        btn_create.pack(fill="x", pady=(4, 0))

    # ==================== CITIZEN REGISTER VIEW ====================
    def _render_citizen_register(self):
        head = ctk.CTkFrame(self.content_container, fg_color="transparent")
        head.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            head,
            text="REGISTER AS CITIZEN",
            font=Theme.font_badge(),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left")

        btn_back = ctk.CTkButton(
            head,
            text="Back to Sign In",
            width=90,
            height=22,
            corner_radius=5,
            fg_color="transparent",
            text_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_LIGHT,
            font=Theme.font_small(),
            command=self._show_citizen_login
        )
        btn_back.pack(side="right")

        # Full Name
        ctk.CTkLabel(self.content_container, text="FULL NAME", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_fullname = ctk.CTkEntry(self.content_container, placeholder_text="e.g. Tanvir Ahmed", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.reg_fullname.pack(fill="x", pady=(0, 4))

        # Phone Number
        ctk.CTkLabel(self.content_container, text="PHONE / EMERGENCY CONTACT", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_phone = ctk.CTkEntry(self.content_container, placeholder_text="e.g. 01712345678", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.reg_phone.pack(fill="x", pady=(0, 4))

        # Username
        ctk.CTkLabel(self.content_container, text="CHOOSE USERNAME", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_username = ctk.CTkEntry(self.content_container, placeholder_text="e.g. tanvir01", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.reg_username.pack(fill="x", pady=(0, 4))

        # Password
        ctk.CTkLabel(self.content_container, text="CREATE PASSWORD", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(2, 1))
        self.reg_pass = ctk.CTkEntry(self.content_container, placeholder_text="Enter password", show="*", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.reg_pass.pack(fill="x", pady=(0, 6))

        # Submit Registration
        btn_reg = ctk.CTkButton(
            self.content_container,
            text="Create Account & Enter Portal",
            height=36,
            corner_radius=8,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_body_bold(),
            command=self._attempt_register
        )
        btn_reg.pack(fill="x", pady=(4, 0))

    # ==================== ADMIN LOGIN VIEW ====================
    def _render_admin_login(self):
        badge_row = ctk.CTkFrame(self.content_container, fg_color="transparent")
        badge_row.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(
            badge_row,
            text="RESTRICTED CONTROL ROOM",
            font=Theme.font_badge(),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left")

        ctk.CTkLabel(
            badge_row,
            text=" ● RESTRICTED ACCESS ",
            fg_color=Theme.DANGER_BG,
            text_color=Theme.DANGER,
            corner_radius=6,
            font=Theme.font_badge()
        ).pack(side="right")

        # Admin Username
        ctk.CTkLabel(self.content_container, text="ADMIN USERNAME", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(4, 2))
        self.ent_adm_user = ctk.CTkEntry(
            self.content_container,
            placeholder_text="Enter admin username",
            height=36,
            corner_radius=7,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_adm_user.pack(fill="x", pady=(0, 6))
        self.ent_adm_user.insert(0, "admin")

        # Admin Password
        ctk.CTkLabel(self.content_container, text="ADMIN PASSWORD", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(4, 2))
        self.ent_adm_pass = ctk.CTkEntry(
            self.content_container,
            placeholder_text="Enter admin password",
            show="*",
            height=36,
            corner_radius=7,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_adm_pass.pack(fill="x", pady=(0, 6))
        self.ent_adm_pass.insert(0, "admin123")
        self.ent_adm_pass.bind("<Return>", lambda e: self._attempt_admin_login())

        # Error notification label
        self.lbl_adm_error = ctk.CTkLabel(
            self.content_container,
            text="",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.DANGER
        )
        self.lbl_adm_error.pack(pady=(0, 4))

        # Admin Sign In Button
        btn_adm_login = ctk.CTkButton(
            self.content_container,
            text="Access Command Center",
            height=38,
            corner_radius=8,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold(),
            command=self._attempt_admin_login
        )
        btn_adm_login.pack(fill="x", pady=(0, 10))

        # Credentials hint box
        hint_frame = ctk.CTkFrame(
            self.content_container,
            corner_radius=6,
            fg_color=(Theme.BG_ROOT[0], "#141D2D"),
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        hint_frame.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(
            hint_frame,
            text="Default Credentials:  admin  /  admin123\nDisaster Control Room Operations & Fleet Dispatch",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_MUTED,
            justify="center"
        ).pack(pady=6)

    # ==================== ACTIONS & EVENT HANDLERS ====================
    def _switch_to_citizen(self):
        self.role_mode = "CITIZEN"
        self.citizen_submode = "LOGIN"
        self._render_view()

    def _switch_to_admin(self):
        self.role_mode = "ADMIN"
        self._render_view()

    def _show_register(self):
        self.citizen_submode = "REGISTER"
        self._render_view()

    def _show_citizen_login(self):
        self.citizen_submode = "LOGIN"
        self._render_view()

    def _attempt_citizen_login(self):
        username = self.ent_cit_user.get().strip()
        password = self.ent_cit_pass.get().strip()

        if not username or not password:
            self.lbl_cit_error.configure(text="Please provide username and password.")
            return

        conn = get_connection()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
        finally:
            conn.close()

        if user:
            user_data = dict(user)
            self.destroy()
            self.on_login_success(user_data)
        else:
            self.lbl_cit_error.configure(text="Invalid citizen credentials. Please try again.")

    def _attempt_admin_login(self):
        username = self.ent_adm_user.get().strip()
        password = self.ent_adm_pass.get().strip()

        if not username or not password:
            self.lbl_adm_error.configure(text="Please provide admin username and password.")
            return

        conn = get_connection()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
        finally:
            conn.close()

        if user:
            user_data = dict(user)
            if user_data.get("role", "").upper() != "ADMIN":
                self.lbl_adm_error.configure(text="This account does not have Admin privileges. Use Citizen Login.")
                return

            self.destroy()
            self.on_login_success(user_data)
        else:
            self.lbl_adm_error.configure(text="Invalid admin credentials.")

    def _attempt_register(self):
        fname = self.reg_fullname.get().strip()
        phone = self.reg_phone.get().strip()
        uname = self.reg_username.get().strip().lower()
        pwd = self.reg_pass.get().strip()

        if not fname or not uname or not pwd:
            messagebox.showwarning("Validation Error", "Full Name, Username, and Password are required.")
            return

        conn = get_connection()
        try:
            existing = conn.execute("SELECT id FROM users WHERE username=?", (uname,)).fetchone()
            if existing:
                messagebox.showerror("Username Taken", f"The username '{uname}' is already registered. Please choose another.")
                return

            conn.execute(
                "INSERT INTO users (username, password, role, full_name, phone) VALUES (?, ?, 'CITIZEN', ?, ?)",
                (uname, pwd, fname, phone)
            )
            conn.commit()

            new_user = conn.execute("SELECT * FROM users WHERE username=?", (uname,)).fetchone()
            user_data = dict(new_user)

            messagebox.showinfo("Registration Successful", f"Welcome, {fname}!\nYour Citizen account has been created.")
            self.destroy()
            self.on_login_success(user_data)
        finally:
            conn.close()
