import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import csv
from database import get_connection
from gui.theme import Theme
from utils.helper import format_datetime

class ReportsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_export_card()
        self._build_telemetry_table()
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
            text="📈 Audit Intelligence & Emergency CSV Reports",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Review incident resolution records, posted locations, timestamps, and export compliance triage reports for authorities",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_export_card(self):
        card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        card.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        card.grid_columnconfigure((0, 1), weight=1)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=12, pady=10)

        ctk.CTkLabel(
            left,
            text="📥 Comprehensive Emergency Triage Spreadsheet (.CSV)",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Includes ID, Caller, Location, Casualty Counts, Calculated Risk Scores, and Audit Timestamps.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

        btn_export = ctk.CTkButton(
            card,
            text="Export CSV Spreadsheet  ➔",
            height=32,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_body_bold(),
            command=self._export_csv
        )
        btn_export.grid(row=0, column=1, sticky="e", padx=12, pady=10)

    def _build_telemetry_table(self):
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

        self.rep_search = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search audit log by caller, location or emergency type...",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.rep_search.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.rep_search.bind("<KeyRelease>", lambda e: self.refresh())

        self.f_rep_prio = ctk.CTkComboBox(
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
        self.f_rep_prio.grid(row=0, column=1, padx=4)
        self.f_rep_prio.set("All Priorities")

        self.f_rep_status = ctk.CTkComboBox(
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
        self.f_rep_status.grid(row=0, column=2, padx=4)
        self.f_rep_status.set("All Status")

        # Table Header
        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 2))
        th.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        cols = ["INCIDENT ID", "CALLER / CONTACT", "📍 LOCATION", "EMERGENCY TYPE", "PRIORITY RATING", "🕒 LOGGED TIME", "AUDIT STATUS"]
        for idx, col in enumerate(cols):
            ctk.CTkLabel(
                th,
                text=col,
                font=Theme.font_badge(),
                text_color=Theme.TEXT_MUTED,
                anchor="w" if idx < 6 else "center"
            ).grid(row=0, column=idx, sticky="ew", padx=8, pady=4)

        self.scroll_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_list.grid(row=2, column=0, sticky="nsew", padx=4, pady=2)
        self.scroll_list.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

    def _export_csv(self):
        os.makedirs("reports", exist_ok=True)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
            initialdir=os.path.abspath("reports"),
            initialfile="emergency_triage_report.csv",
            title="Export Emergency Audit Report"
        )

        if not file_path:
            return

        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT id, requester_name, location, emergency_type,
                       people_affected, injured, priority_score,
                       priority_level, status, created_at
                FROM emergency_requests
                ORDER BY priority_score DESC
            """).fetchall()
        finally:
            conn.close()

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Request ID", "Requester", "Location", "Emergency Type",
                "People Affected", "Injured", "Risk Score (0-100)", "Priority Level", "Status", "Timestamp"
            ])
            for r in rows:
                writer.writerow(list(r))

        messagebox.showinfo("Export Successful", f"Audit report successfully exported to:\n{file_path}")

    def refresh(self):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT * FROM emergency_requests
                ORDER BY priority_score DESC, id ASC
            """).fetchall()
        finally:
            conn.close()

        # Filtering
        q = self.rep_search.get().strip().lower() if hasattr(self, 'rep_search') else ""
        prio_f = self.f_rep_prio.get() if hasattr(self, 'f_rep_prio') else "All Priorities"
        status_f = self.f_rep_status.get() if hasattr(self, 'f_rep_status') else "All Status"

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
            msg = "No triage records match your filter criteria." if rows else "No triage records available for reporting."
            lbl = ctk.CTkLabel(
                self.scroll_list,
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
            row_frame = ctk.CTkFrame(
                self.scroll_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

            # ID
            ctk.CTkLabel(row_frame, text=f"ER-{r['id']:04d}", font=Theme.font_body_bold(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=0, sticky="ew", padx=8, pady=6)
            
            # Requester
            ctk.CTkLabel(row_frame, text=r["requester_name"] or "Anonymous", font=Theme.font_small(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=1, sticky="ew", padx=6, pady=6)
            
            # Location
            ctk.CTkLabel(row_frame, text=f"📍 {r['location']}", font=Theme.font_small(), text_color=Theme.TEXT_MAIN, anchor="w").grid(row=0, column=2, sticky="ew", padx=6, pady=6)
            
            # Type
            ctk.CTkLabel(row_frame, text=r["emergency_type"], font=Theme.font_small(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=3, sticky="ew", padx=6, pady=6)

            # Priority
            bg = color_map.get(r["priority_level"], Theme.BORDER_COLOR)
            ctk.CTkLabel(
                row_frame,
                text=f" {r['priority_level']} ({r['priority_score']}) ",
                fg_color=bg,
                text_color="white",
                corner_radius=6,
                font=Theme.font_badge()
            ).grid(row=0, column=4, padx=6, pady=6)

            # Logged Time
            time_str = format_datetime(r["created_at"]) if "created_at" in r.keys() else "N/A"
            ctk.CTkLabel(
                row_frame,
                text=f"🕒 {time_str}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=5, sticky="ew", padx=6, pady=6)

            # Status
            is_res = (r["status"] == "RESOLVED")
            st_color = Theme.SUCCESS if is_res else Theme.WARNING
            st_icon = "✅ Resolved" if is_res else "⏳ Pending"
            ctk.CTkLabel(
                row_frame,
                text=st_icon,
                font=Theme.font_small(),
                text_color=st_color,
                anchor="center"
            ).grid(row=0, column=6, sticky="ew", padx=6, pady=6)
