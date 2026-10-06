import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from gui.theme import Theme
from utils.helper import format_datetime

class RescueView(ctk.CTkFrame):
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
            text="🚑 Specialized Rescue Teams & Deployment Dispatch",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Coordinate paramedic, boat evacuation, canine search squads, base node locations, timestamps, and dispatch readiness",
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
            text="➕ Enlist Rescue Squad",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(8, 4))

        self.ent_team = ctk.CTkEntry(
            card,
            placeholder_text="Team Name (e.g. Red Crescent Alpha)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_team.grid(row=1, column=0, padx=6, pady=4, sticky="ew")

        self.cmb_spec = ctk.CTkComboBox(
            card,
            values=["Flood Evacuation", "Medical / Paramedic", "Fire & Rescue", "Search & Canine", "Logistics"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_spec.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        self.cmb_spec.set("Flood Evacuation")

        self.ent_members = ctk.CTkEntry(
            card,
            placeholder_text="Personnel Count (e.g. 8)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_members.grid(row=1, column=2, padx=6, pady=4, sticky="ew")

        self.ent_loc = ctk.CTkEntry(
            card,
            placeholder_text="Base Node / Area (e.g. Node A)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_loc.grid(row=1, column=3, padx=6, pady=4, sticky="ew")

        btn_add = ctk.CTkButton(
            card,
            text="Enlist Response Squad  ➔",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold(),
            command=self._add_team
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

        # Search & Filter bar
        filter_bar = ctk.CTkFrame(container, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.rescue_search = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search squad by name or base location...",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.rescue_search.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.rescue_search.bind("<KeyRelease>", lambda e: self.refresh())

        self.f_spec = ctk.CTkComboBox(
            filter_bar,
            values=["All Specializations", "Flood Evacuation", "Medical / Paramedic", "Fire & Rescue", "Search & Canine", "Logistics"],
            width=150,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_spec.grid(row=0, column=1, padx=4)
        self.f_spec.set("All Specializations")

        self.f_status = ctk.CTkComboBox(
            filter_bar,
            values=["All Status", "AVAILABLE", "DEPLOYED"],
            width=130,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_status.grid(row=0, column=2, padx=4)
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

        cols = ["SQUAD NAME", "SPECIALIZATION", "PERSONNEL", "📍 BASE NODE", "🕒 REGISTERED TIME", "STATUS & ACTION"]
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

    def _add_team(self):
        name = self.ent_team.get().strip()
        spec = self.cmb_spec.get().strip()
        mem_str = self.ent_members.get().strip() or "0"
        loc = self.ent_loc.get().strip().upper()

        if not name or not loc:
            messagebox.showwarning("Validation Error", "Please provide squad name and base location node.")
            return

        try:
            mem = int(mem_str)
        except ValueError:
            messagebox.showerror("Validation Error", "Personnel count must be a valid integer.")
            return

        conn = get_connection()
        try:
            conn.execute("INSERT INTO rescue_teams(name, specialization, members, current_location) VALUES (?, ?, ?, ?)", (name, spec, mem, loc))
            conn.commit()
            messagebox.showinfo("Success", f"Rescue squad '{name}' registered.")
            self.ent_team.delete(0, "end")
            self.ent_members.delete(0, "end")
            self.ent_loc.delete(0, "end")
            self.refresh()
        finally:
            conn.close()

    def _toggle_status(self, tid, current_status):
        new_status = "DEPLOYED" if current_status == "AVAILABLE" else "AVAILABLE"
        conn = get_connection()
        try:
            conn.execute("UPDATE rescue_teams SET status=? WHERE id=?", (new_status, tid))
            conn.commit()
            self.refresh()
        finally:
            conn.close()

    def refresh(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM rescue_teams ORDER BY id").fetchall()
        finally:
            conn.close()

        # Filtering
        q = self.rescue_search.get().strip().lower() if hasattr(self, 'rescue_search') else ""
        spec_f = self.f_spec.get() if hasattr(self, 'f_spec') else "All Specializations"
        status_f = self.f_status.get() if hasattr(self, 'f_status') else "All Status"

        filtered = []
        for r in rows:
            if spec_f != "All Specializations" and r["specialization"].upper() != spec_f.upper():
                continue
            if status_f != "All Status" and r["status"].upper() != status_f.upper():
                continue
            if q:
                n = str(r["name"] or "").lower()
                l = str(r["current_location"] or "").lower()
                if q not in n and q not in l:
                    continue
            filtered.append(r)

        if not filtered:
            msg = "No rescue squads match your filter criteria." if rows else "No rescue squads currently registered."
            lbl = ctk.CTkLabel(
                self.scroll_list,
                text=msg,
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        for idx, r in enumerate(filtered):
            is_avail = (r["status"] == "AVAILABLE")
            row_frame = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # Squad Name
            ctk.CTkLabel(row_frame, text=r["name"], font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=0, sticky="ew", padx=8, pady=6)
            
            # Specialization
            ctk.CTkLabel(row_frame, text=r["specialization"], font=Theme.font_small(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=1, sticky="ew", padx=6, pady=6)
            
            # Personnel
            ctk.CTkLabel(row_frame, text=f"👥 {r['members']} staff", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=2, sticky="ew", padx=6, pady=6)
            
            # Base Node
            ctk.CTkLabel(row_frame, text=f"📍 Node {r['current_location']}", font=Theme.font_body_bold(), text_color=Theme.PRIMARY, anchor="w").grid(row=0, column=3, sticky="ew", padx=6, pady=6)

            # Registered Time
            time_str = format_datetime(r["created_at"]) if "created_at" in r.keys() else "N/A"
            ctk.CTkLabel(row_frame, text=f"🕒 {time_str}", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=4, sticky="ew", padx=6, pady=6)

            # Status & Action
            action_box = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_box.grid(row=0, column=5, padx=6, pady=6)

            badge_bg = Theme.SUCCESS if is_avail else Theme.WARNING
            ctk.CTkLabel(action_box, text=f" {r['status']} ", fg_color=badge_bg, text_color="white", corner_radius=6, font=Theme.font_badge()).pack(side="left", padx=(0, 4))

            btn = ctk.CTkButton(
                action_box,
                text="Deploy" if is_avail else "Set Ready",
                width=72,
                height=24,
                corner_radius=5,
                fg_color=Theme.DANGER if is_avail else Theme.SUCCESS,
                hover_color=Theme.DANGER_HOVER if is_avail else Theme.SUCCESS_HOVER,
                font=Theme.font_small(),
                command=lambda tid=r["id"], st=r["status"]: self._toggle_status(tid, st)
            )
            btn.pack(side="left")
