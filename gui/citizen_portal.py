import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from algorithms.risk_score import calculate_risk
from gui.theme import Theme

class CitizenPortal(ctk.CTk):
    def __init__(self, user, on_logout=None):
        super().__init__()
        self.user = user
        self.on_logout = on_logout

        self.title("SDERMS - Citizen Disaster Relief & Emergency Portal")
        self.geometry("1100x720")
        self.minsize(980, 640)

        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=Theme.BG_ROOT)

        self._center_window(1100, 720)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_top_bar()
        self._build_active_disaster_banner()
        self._build_tabs()

    def _on_close(self):
        self.destroy()

    def _center_window(self, width, height):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_top_bar(self):
        top_bar = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        top_bar.pack(fill="x", padx=14, pady=(10, 6))
        top_bar.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(top_bar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=8)

        greeting_name = self.user.get("full_name") or self.user.get("username", "Citizen")
        ctk.CTkLabel(
            left,
            text=f"🛡️ SDERMS  •  Citizen Emergency Portal",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"Welcome, {greeting_name} (Username: @{self.user['username']})",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

        right = ctk.CTkFrame(top_bar, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=14, pady=8)

        ctk.CTkLabel(
            right,
            text=" 🟢 CITIZEN ACCOUNT ",
            fg_color=Theme.SUCCESS_BG,
            text_color=Theme.SUCCESS,
            corner_radius=8,
            font=Theme.font_badge()
        ).pack(side="left", padx=8)

        self.theme_switch = ctk.CTkSwitch(
            right,
            text="Dark",
            command=self._toggle_theme,
            font=Theme.font_small(),
            progress_color=Theme.PRIMARY
        )
        self.theme_switch.select()
        self.theme_switch.pack(side="left", padx=6)

        btn_signout = ctk.CTkButton(
            right,
            text="Sign Out",
            width=75,
            height=28,
            corner_radius=6,
            fg_color=Theme.DANGER_BG,
            text_color=Theme.DANGER,
            hover_color=Theme.BORDER_COLOR,
            font=Theme.font_body_bold(),
            command=self._handle_logout
        )
        btn_signout.pack(side="left", padx=4)

    def _build_active_disaster_banner(self):
        conn = get_connection()
        try:
            active = conn.execute("SELECT * FROM disasters WHERE status='ACTIVE' ORDER BY id DESC LIMIT 1").fetchone()
        finally:
            conn.close()

        banner = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=Theme.DANGER_BG if active else Theme.PRIMARY_LIGHT,
            border_width=1,
            border_color=Theme.DANGER if active else Theme.PRIMARY
        )
        banner.pack(fill="x", padx=14, pady=(0, 6))

        if active:
            txt = f"⚠️ ACTIVE FIELD ADVISORY: {active['name']} ({active['type']}) reported in {active['area']} with {active['severity']} severity! Stay in safe shelters."
            txt_color = Theme.DANGER
        else:
            txt = "ℹ️ No major active disaster alerts reported right now. System operational for emergency assistance."
            txt_color = Theme.PRIMARY

        ctk.CTkLabel(
            banner,
            text=txt,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=txt_color,
            anchor="w"
        ).pack(fill="x", padx=12, pady=6)

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            segmented_button_fg_color=Theme.BG_CARD_ALT,
            segmented_button_selected_color=Theme.PRIMARY,
            segmented_button_selected_hover_color=Theme.PRIMARY_HOVER
        )
        self.tabview.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        self.tab_sos = self.tabview.add("  🚨 Send Emergency SOS  ")
        self.tab_track = self.tabview.add("  📍 Track My Requests  ")
        self.tab_shelters = self.tabview.add("  🏕️ Find Safe Shelters  ")
        self.tab_volunteer = self.tabview.add("  🤝 Join as Volunteer  ")

        self._build_sos_tab()
        self._build_track_tab()
        self._build_shelters_tab()
        self._build_volunteer_tab()

    # ==================== TAB 1: SEND SOS ====================
    def _build_sos_tab(self):
        tab = self.tab_sos
        tab.grid_columnconfigure((0, 1), weight=1)

        # Form Column
        form = ctk.CTkFrame(tab, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=10, pady=6)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Request Immediate Emergency Assistance", font=Theme.font_sub(), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(form, text="Fill in the location details. Our dispatch center will triage your request immediately.", font=Theme.font_small(), text_color=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 8))

        # Requester info
        self.sos_name = ctk.CTkEntry(form, placeholder_text="Caller / Requester Name", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_name.pack(fill="x", pady=3)
        self.sos_name.insert(0, self.user.get("full_name") or self.user["username"])

        self.sos_phone = ctk.CTkEntry(form, placeholder_text="Contact Phone Number", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_phone.pack(fill="x", pady=3)
        if self.user.get("phone"):
            self.sos_phone.insert(0, self.user["phone"])

        self.sos_loc = ctk.CTkEntry(form, placeholder_text="Exact Location / Landmark / Ward (e.g. Roof of School, Ward 3)", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_loc.pack(fill="x", pady=3)

        self.sos_type = ctk.CTkComboBox(form, values=["Medical Assistance Needed", "Trapped in Rising Floodwaters", "Structural / Building Collapse", "Fire Hazard", "Food & Drinking Water Exhausted"], height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_type.pack(fill="x", pady=3)
        self.sos_type.set("Medical Assistance Needed")

        # Counts row
        cframe = ctk.CTkFrame(form, fg_color="transparent")
        cframe.pack(fill="x", pady=4)
        cframe.grid_columnconfigure((0, 1, 2), weight=1)

        self.sos_affected = ctk.CTkEntry(cframe, placeholder_text="People with You", height=30, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_affected.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        self.sos_affected.bind("<KeyRelease>", lambda e: self._update_sos_score())

        self.sos_injured = ctk.CTkEntry(cframe, placeholder_text="Injured Count", height=30, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_injured.grid(row=0, column=1, padx=3, sticky="ew")
        self.sos_injured.bind("<KeyRelease>", lambda e: self._update_sos_score())

        self.sos_child = ctk.CTkEntry(cframe, placeholder_text="Children / Elderly", height=30, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.sos_child.grid(row=0, column=2, padx=(3, 0), sticky="ew")
        self.sos_child.bind("<KeyRelease>", lambda e: self._update_sos_score())

        # Switches
        sw_f = ctk.CTkFrame(form, fg_color="transparent")
        sw_f.pack(fill="x", pady=2)
        sw_f.grid_columnconfigure((0, 1), weight=1)

        self.sos_life = ctk.CTkSwitch(sw_f, text="Life in Immediate Threat?", command=self._update_sos_score, font=Theme.font_small(), progress_color=Theme.DANGER)
        self.sos_life.grid(row=0, column=0, sticky="w", pady=2)

        self.sos_shortage = ctk.CTkSwitch(sw_f, text="Zero Food/Water Left?", command=self._update_sos_score, font=Theme.font_small(), progress_color=Theme.WARNING)
        self.sos_shortage.grid(row=0, column=1, sticky="w", pady=2)

        # Right Column: Visual Preview & Submit
        right_panel = ctk.CTkFrame(tab, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=6)
        right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_panel, text="Emergency Triage Preview", font=Theme.font_sub(), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(right_panel, text="Our automated triage system scores calls so rescue teams reach the highest risks first.", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, wraplength=400, justify="left").pack(anchor="w", pady=(0, 8))

        preview_card = ctk.CTkFrame(right_panel, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER_ACCENT)
        preview_card.pack(fill="x", pady=(0, 10))

        prev_head = ctk.CTkFrame(preview_card, fg_color="transparent")
        prev_head.pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(prev_head, text="PRIORITY RATING", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).pack(side="left")
        self.lbl_sos_badge = ctk.CTkLabel(prev_head, text=" LOW ", fg_color=Theme.SUCCESS, text_color="white", corner_radius=6, font=Theme.font_badge())
        self.lbl_sos_badge.pack(side="right")

        self.lbl_sos_score = ctk.CTkLabel(preview_card, text="0 / 100", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=26, weight="bold"), text_color=Theme.TEXT_MAIN)
        self.lbl_sos_score.pack(anchor="w", padx=12, pady=(0, 4))

        self.sos_pbar = ctk.CTkProgressBar(preview_card, height=8, corner_radius=4)
        self.sos_pbar.pack(fill="x", padx=12, pady=(0, 10))
        self.sos_pbar.set(0)

        # Instructions
        info_box = ctk.CTkFrame(right_panel, corner_radius=8, fg_color=(Theme.BG_ROOT[0], "#141D2D"), border_width=1, border_color=Theme.BORDER_COLOR_LIGHT)
        info_box.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            info_box,
            text="📞 If phone networks are down, your request remains queued locally.\n📍 Keep your mobile phone charged and remain in a high, visible spot.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            justify="left"
        ).pack(padx=10, pady=8)

        # Big Submit Button
        btn_sos = ctk.CTkButton(
            right_panel,
            text="🚨 SEND EMERGENCY SOS NOW",
            height=44,
            corner_radius=10,
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            command=self._submit_sos
        )
        btn_sos.pack(fill="x")

    def _get_sos_values(self):
        try:
            affected = int(self.sos_affected.get().strip() or 0)
        except ValueError:
            affected = 0
        try:
            injured = int(self.sos_injured.get().strip() or 0)
        except ValueError:
            injured = 0
        try:
            child = int(self.sos_child.get().strip() or 0)
        except ValueError:
            child = 0
        life = bool(self.sos_life.get())
        shortage = bool(self.sos_shortage.get())
        return life, injured, child, affected, shortage

    def _update_sos_score(self):
        life, injured, child, affected, shortage = self._get_sos_values()
        score, level = calculate_risk(life, injured, child, affected, shortage)

        self.lbl_sos_score.configure(text=f"{score} / 100")
        self.lbl_sos_badge.configure(text=f" {level} ")
        self.sos_pbar.set(score / 100.0)

        color_map = {"CRITICAL": Theme.DANGER, "HIGH": Theme.WARNING, "MODERATE": Theme.INFO, "LOW": Theme.SUCCESS}
        c = color_map.get(level, Theme.SUCCESS)
        self.lbl_sos_badge.configure(fg_color=c)
        self.sos_pbar.configure(progress_color=c)

    def _submit_sos(self):
        requester = self.sos_name.get().strip()
        phone = self.sos_phone.get().strip()
        loc = self.sos_loc.get().strip()
        etype = self.sos_type.get().strip()

        if not loc:
            messagebox.showwarning("Location Required", "Please provide your current location or landmark so rescue teams can find you.")
            return

        life, injured, child, affected, shortage = self._get_sos_values()
        score, level = calculate_risk(life, injured, child, affected, shortage)

        full_requester = f"{requester} ({phone})" if phone else requester

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO emergency_requests(
                    user_id, requester_name, location, emergency_type,
                    people_affected, injured, children_elderly,
                    life_threat, resource_shortage, priority_score, priority_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user["id"], full_requester, loc, etype,
                affected, injured, child,
                int(life), int(shortage), score, level
            ))
            req_id = cur.lastrowid
            conn.commit()

            messagebox.showinfo(
                "SOS Sent Successfully",
                f"🚨 Emergency Request Dispatched!\n\nYour Ticket ID: ER-{req_id:04d}\nAssigned Priority: {level} (Score: {score}/100)\n\nControl Room has received your alert. Check 'Track My Requests' tab for real-time updates."
            )
            self.sos_loc.delete(0, "end")
            self.sos_affected.delete(0, "end")
            self.sos_injured.delete(0, "end")
            self.sos_child.delete(0, "end")
            self.sos_life.deselect()
            self.sos_shortage.deselect()
            self._update_sos_score()
            self._refresh_track_list()
            self.tabview.set("  📍 Track My Requests  ")
        finally:
            conn.close()

    # ==================== TAB 2: TRACK REQUESTS ====================
    def _build_track_tab(self):
        tab = self.tab_track
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(tab, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(head, text="My Emergency Request Status & Resolution Tracker", font=Theme.font_sub(), text_color=Theme.TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(head, text="Monitor your dispatch tickets in real-time as rescue operations proceed", font=Theme.font_small(), text_color=Theme.TEXT_MUTED).grid(row=1, column=0, sticky="w")

        btn_ref = ctk.CTkButton(head, text="🔄 Refresh Status", width=100, height=28, corner_radius=6, fg_color=Theme.PRIMARY_LIGHT, text_color=Theme.PRIMARY, hover_color=Theme.BORDER_COLOR, font=Theme.font_small(), command=self._refresh_track_list)
        btn_ref.grid(row=0, column=1, rowspan=2, sticky="e")

        self.track_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.track_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self.track_scroll.grid_columnconfigure(0, weight=1)

        self._refresh_track_list()

    def _refresh_track_list(self):
        for w in self.track_scroll.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            # Query by user_id or matching username
            rows = conn.execute("""
                SELECT * FROM emergency_requests
                WHERE user_id=? OR requester_name LIKE ?
                ORDER BY id DESC
            """, (self.user["id"], f"%{self.user['username']}%")).fetchall()
        finally:
            conn.close()

        if not rows:
            box = ctk.CTkFrame(self.track_scroll, fg_color=Theme.BG_CARD_ALT, corner_radius=10)
            box.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(box, text="You have not logged any emergency requests yet.", font=Theme.font_body(), text_color=Theme.TEXT_MUTED).pack(pady=20)
            return

        color_map = {"CRITICAL": Theme.DANGER, "HIGH": Theme.WARNING, "MODERATE": Theme.INFO, "LOW": Theme.SUCCESS}

        for r in rows:
            card = ctk.CTkFrame(self.track_scroll, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER_COLOR_LIGHT)
            card.pack(fill="x", padx=4, pady=4)
            card.grid_columnconfigure(1, weight=1)

            # Left ticket badge
            badge_frame = ctk.CTkFrame(card, fg_color="transparent")
            badge_frame.grid(row=0, column=0, rowspan=2, padx=12, pady=10)

            ctk.CTkLabel(badge_frame, text=f"ER-{r['id']:04d}", font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"), text_color=Theme.PRIMARY).pack()
            bg = color_map.get(r["priority_level"], Theme.BORDER_COLOR)
            ctk.CTkLabel(badge_frame, text=f" {r['priority_level']} ", fg_color=bg, text_color="white", corner_radius=6, font=Theme.font_badge()).pack(pady=(2, 0))

            # Details
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", padx=4, pady=(8, 2))

            ctk.CTkLabel(info, text=f"{r['emergency_type']}  •  📍 {r['location']}", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"Affected: {r['people_affected']} | Injured: {r['injured']} | Risk Rating: {r['priority_score']}/100", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").pack(anchor="w")

            # Status pill on right
            is_res = (r["status"] == "RESOLVED")
            st_color = Theme.SUCCESS if is_res else Theme.WARNING
            st_text = "✅ RESCUE ASSISTED / SAFE" if is_res else "⏳ DISPATCH IN PROGRESS"

            st_lbl = ctk.CTkLabel(card, text=f" {st_text} ", fg_color=(Theme.SUCCESS_BG if is_res else Theme.WARNING_BG), text_color=st_color, corner_radius=8, font=Theme.font_badge())
            st_lbl.grid(row=0, column=2, padx=12, pady=10)

    # ==================== TAB 3: FIND SHELTERS ====================
    def _build_shelters_tab(self):
        tab = self.tab_shelters
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(tab, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(head, text="Nearby Safe Evacuation Shelters", font=Theme.font_sub(), text_color=Theme.TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(head, text="Public shelter facilities with verified bed capacity and safety status", font=Theme.font_small(), text_color=Theme.TEXT_MUTED).grid(row=1, column=0, sticky="w")

        btn_ref = ctk.CTkButton(head, text="🔄 Refresh Shelters", width=110, height=28, corner_radius=6, fg_color=Theme.PRIMARY_LIGHT, text_color=Theme.PRIMARY, hover_color=Theme.BORDER_COLOR, font=Theme.font_small(), command=self._refresh_shelters_list)
        btn_ref.grid(row=0, column=1, rowspan=2, sticky="e")

        self.sh_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.sh_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self.sh_scroll.grid_columnconfigure(0, weight=1)

        self._refresh_shelters_list()

    def _refresh_shelters_list(self):
        for w in self.sh_scroll.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM shelters ORDER BY id").fetchall()
        finally:
            conn.close()

        if not rows:
            ctk.CTkLabel(self.sh_scroll, text="No shelters registered in system.", font=Theme.font_small(), text_color=Theme.TEXT_MUTED).pack(pady=20)
            return

        for r in rows:
            cap = r["capacity"]
            occ = r["occupied"]
            avail = max(0, cap - occ)
            ratio = (occ / cap) if cap > 0 else 1.0

            card = ctk.CTkFrame(self.sh_scroll, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER_COLOR_LIGHT)
            card.pack(fill="x", padx=4, pady=4)
            card.grid_columnconfigure(1, weight=1)

            # Icon
            ctk.CTkLabel(card, text="🏕️", font=ctk.CTkFont(size=24)).grid(row=0, column=0, rowspan=2, padx=12, pady=10)

            # Info
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", padx=4, pady=8)

            ctk.CTkLabel(info, text=f"{r['name']}  •  📍 {r['location']}", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"Available Beds: {avail:,} of {cap:,} capacity", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").pack(anchor="w")

            # Progress bar
            pbar = ctk.CTkProgressBar(card, width=140, height=8, corner_radius=4)
            pbar.grid(row=0, column=2, padx=10, pady=10)
            pbar.set(ratio)
            pbar.configure(progress_color=Theme.DANGER if ratio >= 1.0 else (Theme.WARNING if ratio >= 0.8 else Theme.SUCCESS))

            # Status Badge
            status_txt = "FULL" if avail <= 0 else ("ALMOST FULL" if ratio >= 0.8 else "AVAILABLE")
            status_bg = Theme.DANGER if avail <= 0 else (Theme.WARNING if ratio >= 0.8 else Theme.SUCCESS)
            ctk.CTkLabel(card, text=f" {status_txt} ", fg_color=status_bg, text_color="white", corner_radius=6, font=Theme.font_badge()).grid(row=0, column=3, padx=12, pady=10)

    # ==================== TAB 4: VOLUNTEER REGISTRATION ====================
    def _build_volunteer_tab(self):
        tab = self.tab_volunteer
        tab.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(tab, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER_COLOR_LIGHT)
        card.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(card, text="Join the Community Emergency Volunteer Force", font=Theme.font_sub(), text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(card, text="If you are in a safe zone and possess helpful skills (medical, boating, packaging, rescue), enroll below to assist your community.", font=Theme.font_small(), text_color=Theme.TEXT_MUTED, wraplength=700, justify="left").pack(anchor="w", padx=14, pady=(0, 10))

        grid_f = ctk.CTkFrame(card, fg_color="transparent")
        grid_f.pack(fill="x", padx=14, pady=(0, 10))
        grid_f.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid_f, text="YOUR NAME", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=4, pady=(4, 2))
        ctk.CTkLabel(grid_f, text="CONTACT NUMBER", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).grid(row=0, column=1, sticky="w", padx=4, pady=(4, 2))

        self.vol_name = ctk.CTkEntry(grid_f, height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.vol_name.grid(row=1, column=0, padx=4, pady=(0, 6), sticky="ew")
        self.vol_name.insert(0, self.user.get("full_name") or self.user["username"])

        self.vol_phone = ctk.CTkEntry(grid_f, height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.vol_phone.grid(row=1, column=1, padx=4, pady=(0, 6), sticky="ew")
        if self.user.get("phone"):
            self.vol_phone.insert(0, self.user["phone"])

        ctk.CTkLabel(grid_f, text="SPECIAL SKILLSET", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).grid(row=2, column=0, sticky="w", padx=4, pady=(4, 2))
        ctk.CTkLabel(grid_f, text="YOUR LOCATION / AREA", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).grid(row=2, column=1, sticky="w", padx=4, pady=(4, 2))

        self.vol_skill = ctk.CTkComboBox(grid_f, values=["First Aid / CPR", "Boat Operator", "Relief Packaging", "Driver", "Tech & Comms", "Search Support"], height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.vol_skill.grid(row=3, column=0, padx=4, pady=(0, 6), sticky="ew")
        self.vol_skill.set("First Aid / CPR")

        self.vol_loc = ctk.CTkEntry(grid_f, placeholder_text="e.g. Mirpur, Dhaka", height=32, corner_radius=6, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER_COLOR, font=Theme.font_small())
        self.vol_loc.grid(row=3, column=1, padx=4, pady=(0, 6), sticky="ew")

        btn_vol = ctk.CTkButton(
            card,
            text="Enlist as Ready Volunteer  ➔",
            height=36,
            corner_radius=8,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_body_bold(),
            command=self._submit_volunteer
        )
        btn_vol.pack(fill="x", padx=14, pady=(6, 14))

    def _submit_volunteer(self):
        name = self.vol_name.get().strip()
        phone = self.vol_phone.get().strip()
        skill = self.vol_skill.get().strip()
        loc = self.vol_loc.get().strip()

        if not name or not loc:
            messagebox.showwarning("Validation Error", "Please provide your name and location.")
            return

        conn = get_connection()
        try:
            conn.execute("INSERT INTO volunteers(name, skill, location, contact, availability) VALUES (?, ?, ?, ?, 'YES')", (name, skill, loc, phone))
            conn.commit()
            messagebox.showinfo("Thank You!", f"You have been successfully enlisted in the SDERMS volunteer directory!\nThe Disaster Command Center can mobilize you when help is needed in {loc}.")
        finally:
            conn.close()

    def _toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="Dark")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="Light")

    def _handle_logout(self):
        self.destroy()
        if self.on_logout:
            self.on_logout()
