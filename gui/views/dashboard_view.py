import customtkinter as ctk
from database import get_connection
from gui.theme import Theme
from gui.components.stat_card import StatCard

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, navigate_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_callback = navigate_callback
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_kpi_grid()
        self._build_action_and_occupancy_strip()
        self._build_alerts_section()
        self.refresh()

    def _build_header(self):
        header_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        header_card.pack(fill="x", padx=12, pady=(10, 6))
        header_card.grid_columnconfigure(0, weight=1)

        left_box = ctk.CTkFrame(header_card, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="w", padx=14, pady=8)

        title = ctk.CTkLabel(
            left_box,
            text="Executive Disaster Response Telemetry",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            left_box,
            text="Real-time situational awareness, emergency triage prioritization and resource telemetry",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(1, 0))

        right_box = ctk.CTkFrame(header_card, fg_color="transparent")
        right_box.grid(row=0, column=1, sticky="e", padx=14, pady=8)

        status_pill = ctk.CTkLabel(
            right_box,
            text=" ● LIVE MONITORING ",
            fg_color=Theme.SUCCESS_BG,
            text_color=Theme.SUCCESS,
            corner_radius=10,
            font=Theme.font_badge()
        )
        status_pill.pack(side="left", padx=8)

        refresh_btn = ctk.CTkButton(
            right_box,
            text="🔄 Refresh",
            width=85,
            height=28,
            corner_radius=6,
            fg_color=Theme.PRIMARY_LIGHT,
            text_color=Theme.PRIMARY,
            hover_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=self.refresh
        )
        refresh_btn.pack(side="left")

    def _build_kpi_grid(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=8, pady=2)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_active = StatCard(cards_frame, title="Active Disasters", value="0", icon="🌪️", accent_color=Theme.DANGER)
        self.card_active.grid(row=0, column=0, sticky="ew", padx=4, pady=3)

        self.card_affected = StatCard(cards_frame, title="People Affected", value="0", icon="👥", accent_color=Theme.WARNING)
        self.card_affected.grid(row=0, column=1, sticky="ew", padx=4, pady=3)

        self.card_critical = StatCard(cards_frame, title="Critical Requests", value="0", icon="🚨", accent_color=Theme.DANGER)
        self.card_critical.grid(row=0, column=2, sticky="ew", padx=4, pady=3)

        self.card_pending = StatCard(cards_frame, title="Pending Triage", value="0", icon="⏳", accent_color=Theme.PURPLE)
        self.card_pending.grid(row=0, column=3, sticky="ew", padx=4, pady=3)

        self.card_shelters = StatCard(cards_frame, title="Shelter Capacity", value="0 / 0", icon="🏕️", accent_color=Theme.SUCCESS)
        self.card_shelters.grid(row=1, column=0, sticky="ew", padx=4, pady=3)

        self.card_rescue = StatCard(cards_frame, title="Available Squads", value="0", icon="🚑", accent_color=Theme.INFO)
        self.card_rescue.grid(row=1, column=1, sticky="ew", padx=4, pady=3)

        self.card_volunteers = StatCard(cards_frame, title="Ready Volunteers", value="0", icon="🤝", accent_color=Theme.TEAL)
        self.card_volunteers.grid(row=1, column=2, sticky="ew", padx=4, pady=3)

        self.card_resolved = StatCard(cards_frame, title="Resolved Incidents", value="0", icon="✅", accent_color=Theme.SUCCESS)
        self.card_resolved.grid(row=1, column=3, sticky="ew", padx=4, pady=3)

    def _build_action_and_occupancy_strip(self):
        strip = ctk.CTkFrame(self, fg_color="transparent")
        strip.pack(fill="x", padx=8, pady=3)
        strip.grid_columnconfigure((0, 1), weight=1)

        # Shelter Visual Occupancy Card
        self.shelter_card = ctk.CTkFrame(
            strip,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        self.shelter_card.grid(row=0, column=0, sticky="nsew", padx=4, pady=3)
        self.shelter_card.grid_columnconfigure(0, weight=1)

        sh_head = ctk.CTkFrame(self.shelter_card, fg_color="transparent")
        sh_head.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            sh_head,
            text="🏕️ Shelter Utilization Overview",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).pack(side="left")

        self.lbl_shelter_pct = ctk.CTkLabel(
            sh_head,
            text="0%",
            font=Theme.font_body_bold(),
            text_color=Theme.PRIMARY
        )
        self.lbl_shelter_pct.pack(side="right")

        self.shelter_pbar = ctk.CTkProgressBar(self.shelter_card, height=10, corner_radius=5)
        self.shelter_pbar.pack(fill="x", padx=12, pady=(0, 4))
        self.shelter_pbar.set(0)

        self.lbl_shelter_sub = ctk.CTkLabel(
            self.shelter_card,
            text="0 total evacuees currently sheltered",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_shelter_sub.pack(anchor="w", padx=12, pady=(0, 8))

        # Quick Actions Card
        actions_card = ctk.CTkFrame(
            strip,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        actions_card.grid(row=0, column=1, sticky="nsew", padx=4, pady=3)
        actions_card.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            actions_card,
            text="⚡ Emergency Response Quick Actions",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(8, 6))

        btn_new_em = ctk.CTkButton(
            actions_card,
            text="🚨 Log Emergency",
            height=30,
            corner_radius=6,
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            font=Theme.font_small(),
            command=lambda: self.navigate_callback("emergencies") if self.navigate_callback else None
        )
        btn_new_em.grid(row=1, column=0, padx=4, pady=(0, 8), sticky="ew")

        btn_new_dis = ctk.CTkButton(
            actions_card,
            text="🌪️ Add Disaster",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_small(),
            command=lambda: self.navigate_callback("disasters") if self.navigate_callback else None
        )
        btn_new_dis.grid(row=1, column=1, padx=4, pady=(0, 8), sticky="ew")

        btn_route = ctk.CTkButton(
            actions_card,
            text="🧭 Dijkstra Route",
            height=30,
            corner_radius=6,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_small(),
            command=lambda: self.navigate_callback("routes") if self.navigate_callback else None
        )
        btn_route.grid(row=1, column=2, padx=4, pady=(0, 8), sticky="ew")

    def _build_alerts_section(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        container.pack(fill="x", padx=12, pady=(4, 12))
        container.grid_columnconfigure(0, weight=1)

        sec_head = ctk.CTkFrame(container, fg_color="transparent")
        sec_head.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            sec_head,
            text="🚨 Critical & High Priority Emergency Queue",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).pack(side="left")

        ctk.CTkLabel(
            sec_head,
            text="Ranked by Automated Multi-Criteria Risk Formula",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        ).pack(side="right")

        self.alerts_list = ctk.CTkFrame(container, fg_color="transparent")
        self.alerts_list.pack(fill="x", padx=8, pady=(0, 8))

    def refresh(self):
        conn = get_connection()
        try:
            active_d = conn.execute("SELECT COUNT(*) c FROM disasters WHERE status='ACTIVE'").fetchone()["c"]
            affected_p = conn.execute("SELECT COALESCE(SUM(affected_people), 0) s FROM disasters WHERE status='ACTIVE'").fetchone()["s"]
            critical_r = conn.execute("SELECT COUNT(*) c FROM emergency_requests WHERE priority_level='CRITICAL' AND status!='RESOLVED'").fetchone()["c"]
            pending_r = conn.execute("SELECT COUNT(*) c FROM emergency_requests WHERE status='PENDING'").fetchone()["c"]
            resolved_r = conn.execute("SELECT COUNT(*) c FROM emergency_requests WHERE status='RESOLVED'").fetchone()["c"]

            total_cap = conn.execute("SELECT COALESCE(SUM(capacity), 0) s FROM shelters").fetchone()["s"]
            total_occ = conn.execute("SELECT COALESCE(SUM(occupied), 0) s FROM shelters").fetchone()["s"]
            avail_teams = conn.execute("SELECT COUNT(*) c FROM rescue_teams WHERE status='AVAILABLE'").fetchone()["c"]
            avail_vol = conn.execute("SELECT COUNT(*) c FROM volunteers WHERE availability='YES'").fetchone()["c"]

            self.card_active.update_value(active_d)
            self.card_affected.update_value(f"{affected_p:,}")
            self.card_critical.update_value(critical_r)
            self.card_pending.update_value(pending_r)
            self.card_shelters.update_value(f"{total_occ:,} / {total_cap:,}")
            self.card_rescue.update_value(avail_teams)
            self.card_volunteers.update_value(avail_vol)
            self.card_resolved.update_value(resolved_r)

            # Shelter progress
            ratio = (total_occ / total_cap) if total_cap > 0 else 0
            ratio = min(1.0, max(0.0, ratio))
            self.shelter_pbar.set(ratio)
            self.lbl_shelter_pct.configure(text=f"{ratio*100:.1f}%")
            if ratio >= 0.9:
                self.shelter_pbar.configure(progress_color=Theme.DANGER)
            elif ratio >= 0.7:
                self.shelter_pbar.configure(progress_color=Theme.WARNING)
            else:
                self.shelter_pbar.configure(progress_color=Theme.SUCCESS)

            self.lbl_shelter_sub.configure(text=f"{total_occ:,} accommodated ({max(0, total_cap-total_occ):,} beds free)")

            # Alerts
            for w in self.alerts_list.winfo_children():
                w.destroy()

            high_requests = conn.execute("""
                SELECT id, requester_name, location, emergency_type, priority_score, priority_level, status
                FROM emergency_requests
                WHERE status != 'RESOLVED'
                ORDER BY priority_score DESC, id ASC
                LIMIT 5
            """).fetchall()

            if not high_requests:
                lbl = ctk.CTkLabel(
                    self.alerts_list,
                    text="🎉 No active high-priority emergencies reported in the field.",
                    font=Theme.font_body(),
                    text_color=Theme.TEXT_MUTED
                )
                lbl.pack(pady=12)
            else:
                for idx, req in enumerate(high_requests):
                    row_box = ctk.CTkFrame(
                        self.alerts_list,
                        fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                        corner_radius=6,
                        border_width=1,
                        border_color=Theme.BORDER_COLOR_LIGHT
                    )
                    row_box.pack(fill="x", padx=2, pady=2)
                    row_box.grid_columnconfigure(2, weight=1)

                    badge_bg = Theme.DANGER if req["priority_level"] == "CRITICAL" else Theme.WARNING
                    ctk.CTkLabel(
                        row_box,
                        text=f" {req['priority_level']} ",
                        fg_color=badge_bg,
                        text_color="white",
                        corner_radius=6,
                        font=Theme.font_badge()
                    ).grid(row=0, column=0, padx=8, pady=6)

                    ctk.CTkLabel(
                        row_box,
                        text=f"ER-{req['id']:04d}",
                        font=Theme.font_body_bold(),
                        text_color=Theme.TEXT_MAIN
                    ).grid(row=0, column=1, padx=(0, 10), pady=6)

                    ctk.CTkLabel(
                        row_box,
                        text=f"{req['emergency_type']}  •  📍 {req['location']} ({req['requester_name'] or 'N/A'})",
                        font=Theme.font_small(),
                        text_color=Theme.TEXT_MAIN,
                        anchor="w"
                    ).grid(row=0, column=2, sticky="w", padx=4, pady=6)

                    ctk.CTkLabel(
                        row_box,
                        text=f"Risk: {req['priority_score']}/100",
                        font=Theme.font_body_bold(),
                        text_color=Theme.PRIMARY
                    ).grid(row=0, column=3, padx=(8, 10), pady=6)

        finally:
            conn.close()
