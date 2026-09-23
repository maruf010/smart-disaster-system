import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from gui.theme import Theme

class ShelterView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
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
            text="🏕️ Evacuation Shelters & Best-Fit Capacity Recommender",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Monitor shelter bed availability and utilize algorithmic best-fit matching to prevent shelter overcrowding",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_controls(self):
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        ctrl_frame.grid_columnconfigure((0, 1), weight=1)

        # Left Card: Add Shelter
        add_box = ctk.CTkFrame(
            ctrl_frame,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        add_box.grid(row=0, column=0, sticky="nsew", padx=4, pady=2)
        add_box.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            add_box,
            text="➕ Register Shelter Center",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 4))

        self.ent_name = ctk.CTkEntry(
            add_box,
            placeholder_text="Name (e.g. Model College)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_name.grid(row=1, column=0, padx=(10, 3), pady=3, sticky="ew")

        self.ent_loc = ctk.CTkEntry(
            add_box,
            placeholder_text="Location / Area",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_loc.grid(row=1, column=1, padx=(3, 10), pady=3, sticky="ew")

        self.ent_cap = ctk.CTkEntry(
            add_box,
            placeholder_text="Capacity (e.g. 500)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_cap.grid(row=2, column=0, padx=(10, 3), pady=3, sticky="ew")

        self.ent_occ = ctk.CTkEntry(
            add_box,
            placeholder_text="Occupied (e.g. 100)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_occ.grid(row=2, column=1, padx=(3, 10), pady=3, sticky="ew")

        btn_add = ctk.CTkButton(
            add_box,
            text="Enlist Shelter",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold(),
            command=self._add_shelter
        )
        btn_add.grid(row=3, column=0, columnspan=2, padx=10, pady=(6, 10), sticky="ew")

        # Right Card: Recommender
        rec_box = ctk.CTkFrame(
            ctrl_frame,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        rec_box.grid(row=0, column=1, sticky="nsew", padx=4, pady=2)
        rec_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            rec_box,
            text="🎯 Best-Fit Shelter Recommender",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            rec_box,
            text="Finds the tightest-fit shelter matching requested evacuees without wasting large capacity.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", padx=10, pady=(0, 6))

        rec_row = ctk.CTkFrame(rec_box, fg_color="transparent")
        rec_row.pack(fill="x", padx=10, pady=2)
        rec_row.grid_columnconfigure(0, weight=1)

        self.ent_req_seats = ctk.CTkEntry(
            rec_row,
            placeholder_text="Evacuees Needed (e.g. 150)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_req_seats.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        btn_rec = ctk.CTkButton(
            rec_row,
            text="Calculate Best Fit",
            height=30,
            width=120,
            corner_radius=6,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_body_bold(),
            command=self._recommend_shelter
        )
        btn_rec.grid(row=0, column=1, sticky="e")

        # Result badge
        self.res_badge_frame = ctk.CTkFrame(
            rec_box,
            corner_radius=6,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        self.res_badge_frame.pack(fill="x", padx=10, pady=(6, 10))

        self.lbl_rec_result = ctk.CTkLabel(
            self.res_badge_frame,
            text="Enter evacuee count and click 'Calculate Best Fit'",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_rec_result.pack(padx=8, pady=6)

    def _build_table(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        container.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = ["SHELTER NAME", "LOCATION", "MAX CAPACITY", "OCCUPIED BEDS", "OCCUPANCY LEVEL", "STATUS"]
        for idx, col in enumerate(cols):
            ctk.CTkLabel(
                th,
                text=col,
                font=Theme.font_badge(),
                text_color=Theme.TEXT_MUTED,
                anchor="w" if idx < 5 else "center"
            ).grid(row=0, column=idx, sticky="ew", padx=8, pady=4)

        self.scroll_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_list.grid(row=1, column=0, sticky="nsew", padx=4, pady=2)
        self.scroll_list.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    def _add_shelter(self):
        name = self.ent_name.get().strip()
        loc = self.ent_loc.get().strip()
        cap_str = self.ent_cap.get().strip()
        occ_str = self.ent_occ.get().strip() or "0"

        if not name or not loc or not cap_str:
            messagebox.showwarning("Validation Error", "Please provide name, location, and capacity.")
            return

        try:
            cap = int(cap_str)
            occ = int(occ_str)
            if cap <= 0 or occ < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Capacity and Occupied must be valid numbers.")
            return

        conn = get_connection()
        try:
            conn.execute("INSERT INTO shelters(name, location, capacity, occupied) VALUES (?, ?, ?, ?)", (name, loc, cap, occ))
            conn.commit()
            messagebox.showinfo("Success", f"Shelter '{name}' registered.")
            self.ent_name.delete(0, "end")
            self.ent_loc.delete(0, "end")
            self.ent_cap.delete(0, "end")
            self.ent_occ.delete(0, "end")
            self.refresh()
        finally:
            conn.close()

    def _recommend_shelter(self):
        seats_str = self.ent_req_seats.get().strip()
        if not seats_str:
            messagebox.showwarning("Input Needed", "Please enter the number of evacuees.")
            return

        try:
            required = int(seats_str)
            if required <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer.")
            return

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM shelters").fetchall()
        finally:
            conn.close()

        suitable = []
        for r in rows:
            available = r["capacity"] - r["occupied"]
            if available >= required:
                suitable.append((available, r))

        if not suitable:
            self.lbl_rec_result.configure(
                text=f"❌ No single shelter has {required} available beds.",
                text_color=Theme.DANGER
            )
            return

        suitable.sort(key=lambda x: x[0])
        avail, best = suitable[0]
        self.lbl_rec_result.configure(
            text=f"🎯 Optimal: {best['name']} ({best['location']}) | Free: {avail} beds (Surplus: {avail - required})",
            text_color=Theme.SUCCESS
        )

    def refresh(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM shelters ORDER BY id").fetchall()
        finally:
            conn.close()

        if not rows:
            lbl = ctk.CTkLabel(
                self.scroll_list,
                text="No shelter facilities registered yet.",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        for idx, r in enumerate(rows):
            row_frame = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            cap = r["capacity"]
            occ = r["occupied"]
            avail = max(0, cap - occ)
            ratio = (occ / cap) if cap > 0 else 1.0
            ratio = min(1.0, max(0.0, ratio))

            # ID & Name
            ctk.CTkLabel(
                row_frame,
                text=f"#{r['id']} {r['name']}",
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=5)

            # Location
            ctk.CTkLabel(
                row_frame,
                text=f"📍 {r['location']}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=1, sticky="ew", padx=6, pady=5)

            # Capacity
            ctk.CTkLabel(
                row_frame,
                text=f"{cap:,} beds",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=2, sticky="ew", padx=6, pady=5)

            # Occupied
            ctk.CTkLabel(
                row_frame,
                text=f"{occ:,} ({avail:,} free)",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=3, sticky="ew", padx=6, pady=5)

            # Progress Bar
            prog_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            prog_frame.grid(row=0, column=4, sticky="ew", padx=6, pady=5)
            prog_frame.grid_columnconfigure(0, weight=1)

            pbar = ctk.CTkProgressBar(prog_frame, height=8, corner_radius=4)
            pbar.set(ratio)
            if ratio >= 1.0:
                pbar.configure(progress_color=Theme.DANGER)
            elif ratio >= 0.8:
                pbar.configure(progress_color=Theme.WARNING)
            else:
                pbar.configure(progress_color=Theme.SUCCESS)
            pbar.grid(row=0, column=0, sticky="ew")

            pct_lbl = ctk.CTkLabel(prog_frame, text=f"{(ratio*100):.0f}%", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=9), text_color=Theme.TEXT_MUTED)
            pct_lbl.grid(row=0, column=1, padx=(4, 0))

            # Status Badge
            if avail <= 0:
                status_text = " FULL "
                status_bg = Theme.DANGER
            elif ratio >= 0.8:
                status_text = " ALMOST FULL "
                status_bg = Theme.WARNING
            else:
                status_text = " AVAILABLE "
                status_bg = Theme.SUCCESS

            ctk.CTkLabel(
                row_frame,
                text=status_text,
                fg_color=status_bg,
                text_color="white",
                corner_radius=6,
                font=Theme.font_badge()
            ).grid(row=0, column=5, padx=6, pady=5)
