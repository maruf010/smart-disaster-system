import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from algorithms.risk_score import calculate_risk
from gui.theme import Theme
from utils.helper import format_datetime

class EmergencyView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_form()
        self._build_queue()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 6))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=8)

        ctk.CTkLabel(
            left,
            text="🚨 Emergency Incident Triage & Automated Prioritization",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Automated multi-criteria triage formula ranking SOS alerts by urgency, location, casualties, and time tracking",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_form(self):
        card = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        card.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Intake Incoming Emergency Call",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w", padx=10, pady=(8, 6))

        # Inputs
        self.ent_req = ctk.CTkEntry(
            card,
            placeholder_text="Caller / Requester Name",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_req.pack(fill="x", padx=10, pady=3)

        self.ent_loc = ctk.CTkEntry(
            card,
            placeholder_text="Incident Landmark / Location (e.g. Ward 4, Building 3)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_loc.pack(fill="x", padx=10, pady=3)

        self.cmb_etype = ctk.CTkComboBox(
            card,
            values=["Medical Emergency", "Trapped in Floodwaters", "Building Collapse", "Fire Outbreak", "Supply Shortage", "Other"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_etype.pack(fill="x", padx=10, pady=3)
        self.cmb_etype.set("Medical Emergency")

        # Counts
        cnt_frame = ctk.CTkFrame(card, fg_color="transparent")
        cnt_frame.pack(fill="x", padx=10, pady=4)
        cnt_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.ent_affected = ctk.CTkEntry(
            cnt_frame,
            placeholder_text="Affected",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_affected.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        self.ent_affected.bind("<KeyRelease>", lambda e: self._update_live_score())

        self.ent_injured = ctk.CTkEntry(
            cnt_frame,
            placeholder_text="Injured",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_injured.grid(row=0, column=1, padx=3, sticky="ew")
        self.ent_injured.bind("<KeyRelease>", lambda e: self._update_live_score())

        self.ent_child = ctk.CTkEntry(
            cnt_frame,
            placeholder_text="Child/Elder",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_child.grid(row=0, column=2, padx=(3, 0), sticky="ew")
        self.ent_child.bind("<KeyRelease>", lambda e: self._update_live_score())

        # Switches
        sw_frame = ctk.CTkFrame(card, fg_color="transparent")
        sw_frame.pack(fill="x", padx=10, pady=4)

        self.sw_life = ctk.CTkSwitch(
            sw_frame,
            text="Life in Immediate Threat?",
            command=self._update_live_score,
            font=Theme.font_small(),
            progress_color=Theme.DANGER
        )
        self.sw_life.pack(anchor="w", pady=2)

        self.sw_shortage = ctk.CTkSwitch(
            sw_frame,
            text="Severe Food / Water / Med Shortage?",
            command=self._update_live_score,
            font=Theme.font_small(),
            progress_color=Theme.WARNING
        )
        self.sw_shortage.pack(anchor="w", pady=2)

        # Realtime Triage Preview Card
        prev_card = ctk.CTkFrame(
            card,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        prev_card.pack(fill="x", padx=10, pady=(6, 8))

        phead = ctk.CTkFrame(prev_card, fg_color="transparent")
        phead.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            phead,
            text="CALCULATED RISK SCORE",
            font=Theme.font_badge(),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left")

        self.badge_preview = ctk.CTkLabel(
            phead,
            text=" LOW ",
            fg_color=Theme.SUCCESS,
            text_color="white",
            corner_radius=6,
            font=Theme.font_badge()
        )
        self.badge_preview.pack(side="right")

        self.lbl_score_val = ctk.CTkLabel(
            prev_card,
            text="0 / 100",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        self.lbl_score_val.pack(anchor="w", padx=10, pady=(0, 2))

        self.score_pbar = ctk.CTkProgressBar(prev_card, height=6, corner_radius=3)
        self.score_pbar.pack(fill="x", padx=10, pady=(0, 6))
        self.score_pbar.set(0)

        # Dispatch Button
        btn_submit = ctk.CTkButton(
            card,
            text="🚨 Dispatch SOS Emergency Request",
            height=34,
            corner_radius=6,
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            font=Theme.font_body_bold(),
            command=self._submit_request
        )
        btn_submit.pack(fill="x", padx=10, pady=(4, 10))

    def _build_queue(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        container.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Filter & Search Bar
        filter_bar = ctk.CTkFrame(container, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.queue_search = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search caller, location or emergency type...",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.queue_search.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.queue_search.bind("<KeyRelease>", lambda e: self.refresh())

        self.f_prio = ctk.CTkComboBox(
            filter_bar,
            values=["All Priorities", "CRITICAL", "HIGH", "MODERATE", "LOW"],
            width=130,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_prio.grid(row=0, column=1, padx=4)
        self.f_prio.set("All Priorities")

        self.f_req_status = ctk.CTkComboBox(
            filter_bar,
            values=["All Status", "PENDING", "RESOLVED"],
            width=120,
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_req_status.grid(row=0, column=2, padx=4)
        self.f_req_status.set("All Status")

        # Table Header
        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 2))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = ["INCIDENT & TYPE", "📍 LOCATION & CALLER", "👥 CASUALTIES", "🕒 LOGGED TIME", "RISK & PRIO", "ACTION"]
        for i, title in enumerate(cols):
            ctk.CTkLabel(
                th,
                text=title,
                font=Theme.font_badge(),
                text_color=Theme.TEXT_MUTED,
                anchor="w" if i < 5 else "center"
            ).grid(row=0, column=i, sticky="ew", padx=6, pady=4)

        self.queue_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.queue_list.grid(row=2, column=0, sticky="nsew", padx=4, pady=2)
        self.queue_list.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    def _get_form_values(self):
        try:
            affected = int(self.ent_affected.get().strip() or 0)
        except ValueError:
            affected = 0

        try:
            injured = int(self.ent_injured.get().strip() or 0)
        except ValueError:
            injured = 0

        try:
            child = int(self.ent_child.get().strip() or 0)
        except ValueError:
            child = 0

        life = bool(self.sw_life.get())
        shortage = bool(self.sw_shortage.get())
        return life, injured, child, affected, shortage

    def _update_live_score(self):
        life, injured, child, affected, shortage = self._get_form_values()
        score, level = calculate_risk(life, injured, child, affected, shortage)

        self.lbl_score_val.configure(text=f"{score} / 100")
        self.badge_preview.configure(text=f" {level} ")
        self.score_pbar.set(score / 100.0)

        color_map = {
            "CRITICAL": Theme.DANGER,
            "HIGH": Theme.WARNING,
            "MODERATE": Theme.INFO,
            "LOW": Theme.SUCCESS
        }
        color = color_map.get(level, Theme.SUCCESS)
        self.badge_preview.configure(fg_color=color)
        self.score_pbar.configure(progress_color=color)

    def _submit_request(self):
        requester = self.ent_req.get().strip()
        loc = self.ent_loc.get().strip()
        etype = self.cmb_etype.get().strip()

        if not loc:
            messagebox.showwarning("Validation Error", "Please provide the incident location.")
            return

        life, injured, child, affected, shortage = self._get_form_values()
        score, level = calculate_risk(life, injured, child, affected, shortage)

        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO emergency_requests(
                    requester_name, location, emergency_type,
                    people_affected, injured, children_elderly,
                    life_threat, resource_shortage, priority_score, priority_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                requester, loc, etype,
                affected, injured, child,
                int(life), int(shortage), score, level
            ))
            conn.commit()
            messagebox.showinfo("SOS Logged", f"Emergency logged successfully!\nCalculated Risk Score: {score}/100 ({level})")
            self.ent_req.delete(0, "end")
            self.ent_loc.delete(0, "end")
            self.ent_affected.delete(0, "end")
            self.ent_injured.delete(0, "end")
            self.ent_child.delete(0, "end")
            self.sw_life.deselect()
            self.sw_shortage.deselect()
            self._update_live_score()
            self.refresh()
        finally:
            conn.close()

    def _resolve_request(self, rid):
        conn = get_connection()
        try:
            conn.execute("UPDATE emergency_requests SET status='RESOLVED' WHERE id=?", (rid,))
            conn.commit()
            self.refresh()
        finally:
            conn.close()

    def refresh(self):
        for w in self.queue_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT * FROM emergency_requests
                ORDER BY CASE WHEN status='PENDING' THEN 0 ELSE 1 END,
                         priority_score DESC, id ASC
            """).fetchall()
        finally:
            conn.close()

        # Filtering
        q = self.queue_search.get().strip().lower() if hasattr(self, 'queue_search') else ""
        prio_f = self.f_prio.get() if hasattr(self, 'f_prio') else "All Priorities"
        status_f = self.f_req_status.get() if hasattr(self, 'f_req_status') else "All Status"

        filtered = []
        for r in rows:
            if prio_f != "All Priorities" and r["priority_level"].upper() != prio_f.upper():
                continue
            if status_f != "All Status" and r["status"].upper() != status_f.upper():
                continue
            if q:
                req_txt = str(r["requester_name"] or "").lower()
                loc_txt = str(r["location"] or "").lower()
                etype_txt = str(r["emergency_type"] or "").lower()
                if q not in req_txt and q not in loc_txt and q not in etype_txt:
                    continue
            filtered.append(r)

        if not filtered:
            msg = "No emergency records match your filter criteria." if rows else "No emergency records in triage queue."
            lbl = ctk.CTkLabel(
                self.queue_list,
                text=msg,
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        color_map = {
            "CRITICAL": Theme.DANGER,
            "HIGH": Theme.WARNING,
            "MODERATE": Theme.INFO,
            "LOW": Theme.SUCCESS
        }

        for idx, r in enumerate(filtered):
            is_pending = (r["status"] == "PENDING")
            row_frame = ctk.CTkFrame(
                self.queue_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # Col 0: ID & Type
            box0 = ctk.CTkFrame(row_frame, fg_color="transparent")
            box0.grid(row=0, column=0, sticky="ew", padx=6, pady=4)
            ctk.CTkLabel(box0, text=f"ER-{r['id']:04d}", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").pack(anchor="w")
            ctk.CTkLabel(box0, text=r['emergency_type'], font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").pack(anchor="w")

            # Col 1: Location & Caller
            box1 = ctk.CTkFrame(row_frame, fg_color="transparent")
            box1.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
            ctk.CTkLabel(box1, text=f"📍 {r['location']}", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").pack(anchor="w")
            caller_name = r['requester_name'] if r['requester_name'] else "Anonymous Caller"
            ctk.CTkLabel(box1, text=f"Caller: {caller_name}", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").pack(anchor="w")

            # Col 2: Casualties
            ctk.CTkLabel(
                row_frame,
                text=f"👥 {r['people_affected']} (🩹 {r['injured']})",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=2, sticky="ew", padx=6, pady=4)

            # Col 3: Logged Time
            time_str = format_datetime(r["created_at"]) if "created_at" in r.keys() else "N/A"
            ctk.CTkLabel(
                row_frame,
                text=f"🕒 {time_str}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=3, sticky="ew", padx=6, pady=4)

            # Col 4: Score & Level Badge
            box4 = ctk.CTkFrame(row_frame, fg_color="transparent")
            box4.grid(row=0, column=4, sticky="ew", padx=6, pady=4)
            ctk.CTkLabel(box4, text=f"Score: {r['priority_score']}/100", font=Theme.font_small(), text_color=Theme.PRIMARY, anchor="w").pack(anchor="w")
            bg = color_map.get(r["priority_level"], Theme.BORDER_COLOR)
            ctk.CTkLabel(
                box4,
                text=f" {r['priority_level']} ",
                fg_color=bg,
                text_color="white",
                corner_radius=6,
                font=Theme.font_badge()
            ).pack(anchor="w", pady=(2, 0))

            # Col 5: Action
            if is_pending:
                btn = ctk.CTkButton(
                    row_frame,
                    text="Resolve",
                    width=65,
                    height=24,
                    corner_radius=5,
                    fg_color=Theme.SUCCESS,
                    hover_color=Theme.SUCCESS_HOVER,
                    font=Theme.font_small(),
                    command=lambda rid=r["id"]: self._resolve_request(rid)
                )
                btn.grid(row=0, column=5, padx=6, pady=4)
            else:
                ctk.CTkLabel(
                    row_frame,
                    text="✅ Resolved",
                    font=Theme.font_small(),
                    text_color=Theme.SUCCESS
                ).grid(row=0, column=5, padx=6, pady=4)
