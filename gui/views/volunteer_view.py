import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from gui.theme import Theme
from utils.helper import format_datetime

class VolunteerView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=8)

        ctk.CTkLabel(
            left,
            text="Civilian Volunteers Network & Skill Directory",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Mobilize community volunteers, track special skillsets, locations, timestamps, and readiness availability",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_form(self):
        card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        card.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            card,
            text="Register Civilian Volunteer",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(8, 4))

        self.ent_name = ctk.CTkEntry(
            card,
            placeholder_text="Full Name",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_name.grid(row=1, column=0, padx=6, pady=4, sticky="ew")

        self.cmb_skill = ctk.CTkComboBox(
            card,
            values=["First Aid / CPR", "Boat Operator", "Relief Packaging", "Crowd Control", "Driver", "Tech & Comms"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_skill.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        self.cmb_skill.set("First Aid / CPR")

        self.ent_loc = ctk.CTkEntry(
            card,
            placeholder_text="Current Location / Ward (e.g. Mirpur-2)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_loc.grid(row=1, column=2, padx=6, pady=4, sticky="ew")

        self.ent_contact = ctk.CTkEntry(
            card,
            placeholder_text="Phone / Contact Info",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_contact.grid(row=1, column=3, padx=6, pady=4, sticky="ew")

        btn_add = ctk.CTkButton(
            card,
            text="Enlist Volunteer",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold(),
            command=self._add_volunteer
        )
        btn_add.grid(row=2, column=0, columnspan=4, padx=6, pady=(4, 10), sticky="ew")

    def _build_table(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        container.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Search and Filter bar
        filter_bar = ctk.CTkFrame(container, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.vol_search = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Search volunteer by name, location or phone...",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.vol_search.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.vol_search.bind("<KeyRelease>", lambda e: self.refresh())

        self.f_vol_skill = ctk.CTkComboBox(
            filter_bar,
            values=["All Skills", "First Aid / CPR", "Boat Operator", "Relief Packaging", "Crowd Control", "Driver", "Tech & Comms"],
            width=140,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_vol_skill.grid(row=0, column=1, padx=4)
        self.f_vol_skill.set("All Skills")

        self.f_vol_avail = ctk.CTkComboBox(
            filter_bar,
            values=["All Availability", "Ready (YES)", "On Break (NO)"],
            width=130,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_vol_avail.grid(row=0, column=2, padx=4)
        self.f_vol_avail.set("All Availability")

        # Table Header
        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 2))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = ["VOLUNTEER NAME", "SKILLSET", "LOCATION", "CONTACT PHONE", "JOINED TIME", "READINESS & ACTION"]
        for idx, col in enumerate(cols):
            ctk.CTkLabel(
                th,
                text=col,
                font=Theme.font_badge(),
                text_color=Theme.TEXT_MUTED,
                anchor="w" if idx < 5 else "center"
            ).grid(row=0, column=idx, sticky="ew", padx=8, pady=4)

        self.scroll_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_list.grid(row=2, column=0, sticky="nsew", padx=4, pady=2)
        self.scroll_list.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    def _add_volunteer(self):
        name = self.ent_name.get().strip()
        skill = self.cmb_skill.get().strip()
        loc = self.ent_loc.get().strip()
        contact = self.ent_contact.get().strip()

        if not name or not loc:
            messagebox.showwarning("Validation Error", "Please provide volunteer name and location.")
            return

        conn = get_connection()
        try:
            conn.execute("INSERT INTO volunteers(name, skill, location, contact) VALUES (?, ?, ?, ?)", (name, skill, loc, contact))
            conn.commit()
            messagebox.showinfo("Success", f"Volunteer '{name}' registered.")
            self.ent_name.delete(0, "end")
            self.ent_loc.delete(0, "end")
            self.ent_contact.delete(0, "end")
            self.refresh()
        finally:
            conn.close()

    def _toggle_avail(self, vid, current_avail):
        new_avail = "NO" if current_avail == "YES" else "YES"
        conn = get_connection()
        try:
            conn.execute("UPDATE volunteers SET availability=? WHERE id=?", (new_avail, vid))
            conn.commit()
            self.refresh()
        finally:
            conn.close()

    def refresh(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM volunteers ORDER BY id DESC").fetchall()
        finally:
            conn.close()

        # Filtering
        q = self.vol_search.get().strip().lower() if hasattr(self, 'vol_search') else ""
        skill_f = self.f_vol_skill.get() if hasattr(self, 'f_vol_skill') else "All Skills"
        avail_f = self.f_vol_avail.get() if hasattr(self, 'f_vol_avail') else "All Availability"

        filtered = []
        for r in rows:
            if skill_f != "All Skills" and r["skill"].upper() != skill_f.upper():
                continue
            if avail_f == "Ready (YES)" and r["availability"] != "YES":
                continue
            if avail_f == "On Break (NO)" and r["availability"] != "NO":
                continue

            if q:
                n = str(r["name"] or "").lower()
                l = str(r["location"] or "").lower()
                c = str(r["contact"] or "").lower()
                if q not in n and q not in l and q not in c:
                    continue
            filtered.append(r)

        if not filtered:
            msg = "No volunteers match your search/filter criteria." if rows else "No volunteers currently registered."
            lbl = ctk.CTkLabel(
                self.scroll_list,
                text=msg,
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        for idx, r in enumerate(filtered):
            is_avail = (r["availability"] == "YES")
            row_frame = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # Name
            ctk.CTkLabel(row_frame, text=r["name"], font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=0, sticky="ew", padx=8, pady=6)
            
            # Skill
            ctk.CTkLabel(row_frame, text=r["skill"], font=Theme.font_small(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=1, sticky="ew", padx=6, pady=6)
            
            # Location
            ctk.CTkLabel(row_frame, text=str(r['location']), font=Theme.font_small(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=2, sticky="ew", padx=6, pady=6)
            
            # Contact
            ctk.CTkLabel(row_frame, text=r["contact"] or "N/A", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=3, sticky="ew", padx=6, pady=6)

            # Joined Time
            time_str = format_datetime(r["created_at"]) if "created_at" in r.keys() else "N/A"
            ctk.CTkLabel(row_frame, text=str(time_str), font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=4, sticky="ew", padx=6, pady=6)

            # Action Box
            action_box = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_box.grid(row=0, column=5, padx=6, pady=6)

            badge_bg = Theme.SUCCESS if is_avail else Theme.BORDER_COLOR
            badge_txt = " READY " if is_avail else " BUSY "
            ctk.CTkLabel(action_box, text=badge_txt, fg_color=badge_bg, text_color="white", corner_radius=6, font=Theme.font_badge()).pack(side="left", padx=(0, 4))

            btn = ctk.CTkButton(
                action_box,
                text="Set Busy" if is_avail else "Set Ready",
                width=72,
                height=24,
                corner_radius=5,
                fg_color=Theme.WARNING if is_avail else Theme.SUCCESS,
                hover_color=Theme.WARNING_HOVER if is_avail else Theme.SUCCESS_HOVER,
                font=Theme.font_small(),
                command=lambda vid=r["id"], av=r["availability"]: self._toggle_avail(vid, av)
            )
            btn.pack(side="left")
