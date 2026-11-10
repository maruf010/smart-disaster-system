import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from gui.theme import Theme
from utils.helper import format_datetime

class DisasterView(ctk.CTkFrame):
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
            text="Disaster Incident Command & Tracking",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Register active cyclones, floods, earthquakes and monitor casualty mitigation status with live filters and timestamp tracking",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_form(self):
        form_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        form_card.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        form_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            form_card,
            text="Register New Disaster / Incident",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(8, 4))

        # Row 1
        self.ent_name = ctk.CTkEntry(
            form_card,
            placeholder_text="Disaster Name (e.g. Cyclone Remal)",
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_name.grid(row=1, column=0, padx=6, pady=4, sticky="ew")

        self.cmb_type = ctk.CTkComboBox(
            form_card,
            values=["Flood", "Cyclone", "Earthquake", "Fire", "Landslide", "Other"],
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_type.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        self.cmb_type.set("Flood")

        self.ent_area = ctk.CTkEntry(
            form_card,
            placeholder_text="Affected Region / District (e.g. Sylhet Sadar)",
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_area.grid(row=1, column=2, padx=6, pady=4, sticky="ew")

        self.cmb_sev = ctk.CTkComboBox(
            form_card,
            values=["LOW", "MODERATE", "HIGH", "CRITICAL"],
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_sev.grid(row=1, column=3, padx=6, pady=4, sticky="ew")
        self.cmb_sev.set("HIGH")

        # Row 2
        self.ent_affected = ctk.CTkEntry(
            form_card,
            placeholder_text="Estimated Affected Population (e.g. 5000)",
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_affected.grid(row=2, column=0, columnspan=2, padx=6, pady=(2, 10), sticky="ew")

        btn_add = ctk.CTkButton(
            form_card,
            text="Enlist Disaster Event",
            height=32,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold(),
            command=self._add_disaster
        )
        btn_add.grid(row=2, column=2, columnspan=2, padx=6, pady=(2, 10), sticky="ew")

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

        # Search and Filters Bar
        filter_bar = ctk.CTkFrame(container, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Search disaster by name or affected area...",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self.f_type = ctk.CTkComboBox(
            filter_bar,
            values=["All Types", "Flood", "Cyclone", "Earthquake", "Fire", "Landslide", "Other"],
            width=120,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_type.grid(row=0, column=1, padx=4)
        self.f_type.set("All Types")

        self.f_sev = ctk.CTkComboBox(
            filter_bar,
            values=["All Severities", "CRITICAL", "HIGH", "MODERATE", "LOW"],
            width=130,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_sev.grid(row=0, column=2, padx=4)
        self.f_sev.set("All Severities")

        self.f_status = ctk.CTkComboBox(
            filter_bar,
            values=["All Status", "ACTIVE", "RESOLVED"],
            width=120,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_status.grid(row=0, column=3, padx=4)
        self.f_status.set("All Status")

        # Table Header
        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 2))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = ["INCIDENT & TYPE", "AFFECTED AREA", "SEVERITY", "POPULATION", "REPORTED TIME", "STATUS & ACTION"]
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

    def _add_disaster(self):
        name = self.ent_name.get().strip()
        dtype = self.cmb_type.get().strip()
        area = self.ent_area.get().strip()
        sev = self.cmb_sev.get().strip()
        affected_str = self.ent_affected.get().strip() or "0"

        if not name or not area:
            messagebox.showwarning("Validation Error", "Please provide disaster name and affected area.")
            return

        try:
            affected = int(affected_str)
        except ValueError:
            messagebox.showerror("Validation Error", "Affected people must be an integer.")
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO disasters(name, type, area, severity, affected_people) VALUES (?, ?, ?, ?, ?)",
                (name, dtype, area, sev, affected)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Disaster event '{name}' logged successfully.")
            self.ent_name.delete(0, "end")
            self.ent_area.delete(0, "end")
            self.ent_affected.delete(0, "end")
            self.refresh()
        finally:
            conn.close()

    def _toggle_resolve(self, did, current_status):
        new_status = "RESOLVED" if current_status == "ACTIVE" else "ACTIVE"
        conn = get_connection()
        try:
            conn.execute("UPDATE disasters SET status=? WHERE id=?", (new_status, did))
            conn.commit()
            self.refresh()
        finally:
            conn.close()

    def refresh(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM disasters ORDER BY id DESC").fetchall()
        finally:
            conn.close()

        # Filtering
        q = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ""
        type_f = self.f_type.get() if hasattr(self, 'f_type') else "All Types"
        sev_f = self.f_sev.get() if hasattr(self, 'f_sev') else "All Severities"
        status_f = self.f_status.get() if hasattr(self, 'f_status') else "All Status"

        filtered = []
        for r in rows:
            if type_f != "All Types" and r["type"].upper() != type_f.upper():
                continue
            if sev_f != "All Severities" and r["severity"].upper() != sev_f.upper():
                continue
            if status_f != "All Status" and r["status"].upper() != status_f.upper():
                continue
            if q:
                n = str(r["name"] or "").lower()
                a = str(r["area"] or "").lower()
                if q not in n and q not in a:
                    continue
            filtered.append(r)

        if not filtered:
            msg = "No disaster records match your filter criteria." if rows else "No disaster records found in database."
            lbl = ctk.CTkLabel(
                self.scroll_list,
                text=msg,
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        sev_colors = {
            "CRITICAL": Theme.DANGER,
            "HIGH": Theme.WARNING,
            "MODERATE": Theme.INFO,
            "LOW": Theme.SUCCESS
        }

        for idx, r in enumerate(filtered):
            is_active = (r["status"] == "ACTIVE")
            row_frame = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # Col 0: ID & Name & Type
            box0 = ctk.CTkFrame(row_frame, fg_color="transparent")
            box0.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
            ctk.CTkLabel(box0, text=f"DIS-{r['id']:03d} • {r['name']}", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").pack(anchor="w")
            ctk.CTkLabel(box0, text=f"Type: {r['type']}", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").pack(anchor="w")

            # Col 1: Area
            ctk.CTkLabel(
                row_frame,
                text=str(r['area']),
                font=Theme.font_small(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=1, sticky="ew", padx=6, pady=6)

            # Col 2: Severity badge
            bg = sev_colors.get(r["severity"], Theme.BORDER_COLOR)
            ctk.CTkLabel(
                row_frame,
                text=f" {r['severity']} ",
                fg_color=bg,
                text_color="white",
                corner_radius=6,
                font=Theme.font_badge()
            ).grid(row=0, column=2, padx=6, pady=6)

            # Col 3: Affected Population
            ctk.CTkLabel(
                row_frame,
                text=f"{r['affected_people']:,}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=3, sticky="ew", padx=6, pady=6)

            # Col 4: Reported Time
            time_str = format_datetime(r["created_at"]) if "created_at" in r.keys() else "N/A"
            ctk.CTkLabel(
                row_frame,
                text=str(time_str),
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=4, sticky="ew", padx=6, pady=6)

            # Col 5: Action button & status
            action_box = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_box.grid(row=0, column=5, padx=8, pady=6)

            status_pill = ctk.CTkLabel(
                action_box,
                text=" ACTIVE " if is_active else " RESOLVED ",
                fg_color=Theme.DANGER_BG if is_active else Theme.SUCCESS_BG,
                text_color=Theme.DANGER if is_active else Theme.SUCCESS,
                corner_radius=6,
                font=Theme.font_badge()
            )
            status_pill.pack(side="left", padx=(0, 4))

            btn_action = ctk.CTkButton(
                action_box,
                text="Resolve" if is_active else "Reopen",
                width=68,
                height=24,
                corner_radius=5,
                fg_color=Theme.SUCCESS if is_active else Theme.BORDER_COLOR,
                hover_color=Theme.SUCCESS_HOVER if is_active else Theme.BORDER_COLOR_LIGHT,
                font=Theme.font_small(),
                command=lambda did=r["id"], st=r["status"]: self._toggle_resolve(did, st)
            )
            btn_action.pack(side="left")
