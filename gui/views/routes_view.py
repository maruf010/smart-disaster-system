import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from algorithms.dijkstra import build_graph, shortest_path
from gui.theme import Theme

class RoutesView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_network_table()
        self._build_dijkstra_panel()
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
            text="Dijkstra Shortest Route Solver & Road Blockade Control",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Simulate road blockades and compute the optimal navigation path for ambulances and relief convoys",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_network_table(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        container.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        container.grid_rowconfigure(3, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text="Active Road Network & Hazard Controls",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        # Add Road Form
        add_box = ctk.CTkFrame(
            container,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        add_box.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        add_box.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.ent_from = ctk.CTkEntry(
            add_box,
            placeholder_text="From (e.g. A)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_from.grid(row=0, column=0, padx=3, pady=5, sticky="ew")

        self.ent_to = ctk.CTkEntry(
            add_box,
            placeholder_text="To (e.g. B)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_to.grid(row=0, column=1, padx=3, pady=5, sticky="ew")

        self.ent_dist = ctk.CTkEntry(
            add_box,
            placeholder_text="Distance (KM)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_dist.grid(row=0, column=2, padx=3, pady=5, sticky="ew")

        btn_add = ctk.CTkButton(
            add_box,
            text="Add Road Link",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_small(),
            command=self._add_road
        )
        btn_add.grid(row=0, column=3, padx=3, pady=5, sticky="ew")

        # Table Header
        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 0))
        th.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(th, text="ROAD SEGMENT", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="ew", padx=8, pady=4)
        ctk.CTkLabel(th, text="DISTANCE", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        ctk.CTkLabel(th, text="CONDITION", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="center").grid(row=0, column=2, padx=8, pady=4)
        ctk.CTkLabel(th, text="ACTION", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="center").grid(row=0, column=3, padx=8, pady=4)

        self.road_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.road_list.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        self.road_list.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def _build_dijkstra_panel(self):
        panel = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        panel.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Dijkstra Shortest Route Solver",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            panel,
            text="Select origin and destination nodes to calculate the lowest latency route.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            wraplength=360,
            justify="left"
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # Node Selectors
        input_card = ctk.CTkFrame(
            panel,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        input_card.pack(fill="x", padx=10, pady=2)
        input_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(input_card, text="START NODE", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(input_card, text="DESTINATION NODE", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED).grid(row=0, column=1, sticky="w", padx=10, pady=(6, 2))

        self.cmb_start = ctk.CTkComboBox(
            input_card,
            values=["A"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_start.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))

        self.cmb_end = ctk.CTkComboBox(
            input_card,
            values=["D"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_end.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 8))

        btn_solve = ctk.CTkButton(
            panel,
            text="Calculate Shortest Route",
            height=32,
            corner_radius=6,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_body_bold(),
            command=self._calculate_route
        )
        btn_solve.pack(fill="x", padx=10, pady=8)

        # GPS Path Result Container
        self.res_card = ctk.CTkFrame(
            panel,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_ACCENT
        )
        self.res_card.pack(fill="both", expand=True, padx=10, pady=(2, 10))
        self.res_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.res_card,
            text="OPTIMAL ROUTE SUMMARY",
            font=Theme.font_badge(),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.lbl_path_visual = ctk.CTkLabel(
            self.res_card,
            text="Select start and destination nodes above, then click 'Calculate Shortest Route'.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            wraplength=340,
            justify="center"
        )
        self.lbl_path_visual.pack(pady=12, padx=10)

        self.lbl_distance = ctk.CTkLabel(
            self.res_card,
            text="",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.PRIMARY
        )
        self.lbl_distance.pack(pady=(0, 8))

    def _add_road(self):
        a = self.ent_from.get().strip().upper()
        b = self.ent_to.get().strip().upper()
        d_str = self.ent_dist.get().strip()

        if not a or not b or not d_str:
            messagebox.showwarning("Validation Error", "Please provide From Node, To Node, and Distance.")
            return

        try:
            d = float(d_str)
            if d <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Distance must be a positive number.")
            return

        conn = get_connection()
        try:
            conn.execute("INSERT INTO roads(from_location, to_location, distance, status) VALUES (?, ?, ?, 'OPEN')", (a, b, d))
            conn.commit()
            messagebox.showinfo("Success", f"Road segment between Node {a} and Node {b} ({d} KM) added.")
            self.ent_from.delete(0, "end")
            self.ent_to.delete(0, "end")
            self.ent_dist.delete(0, "end")
            self.refresh()
        finally:
            conn.close()

    def _toggle_road_status(self, rid, current_status):
        new_status = "BLOCKED" if current_status == "OPEN" else "OPEN"
        conn = get_connection()
        try:
            conn.execute("UPDATE roads SET status=? WHERE id=?", (new_status, rid))
            conn.commit()
            self.refresh()
        finally:
            conn.close()

    def _calculate_route(self):
        start = self.cmb_start.get().strip().upper()
        end = self.cmb_end.get().strip().upper()

        if not start or not end:
            messagebox.showwarning("Input Needed", "Please specify both Start and Destination nodes.")
            return

        if start == end:
            self.lbl_path_visual.configure(text=f"Origin and Destination are identical (Node {start}).\nDistance is 0 KM.", text_color=Theme.SUCCESS)
            self.lbl_distance.configure(text="Total Distance: 0 KM")
            return

        conn = get_connection()
        try:
            roads = conn.execute("SELECT * FROM roads").fetchall()
        finally:
            conn.close()

        graph = build_graph(roads)
        cost, path = shortest_path(graph, start, end)

        if cost is None:
            self.lbl_path_visual.configure(
                text=f"No passable route exists between Node {start} and Node {end}!\n(Roads might be BLOCKED)",
                text_color=Theme.DANGER
            )
            self.lbl_distance.configure(text="Status: Unreachable")
        else:
            visual_chain = "  ->  ".join([f"[{n}]" for n in path])
            self.lbl_path_visual.configure(
                text=f"Optimal Navigation Chain:\n\n{visual_chain}",
                text_color=Theme.SUCCESS
            )
            self.lbl_distance.configure(text=f"Shortest Distance: {cost:g} KM")

    def refresh(self):
        for w in self.road_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM roads ORDER BY id").fetchall()
        finally:
            conn.close()

        nodes = set()
        for r in rows:
            nodes.add(r["from_location"].upper())
            nodes.add(r["to_location"].upper())
        node_list = sorted(list(nodes))
        if node_list:
            self.cmb_start.configure(values=node_list)
            self.cmb_end.configure(values=node_list)
            if self.cmb_start.get() not in node_list:
                self.cmb_start.set(node_list[0])
            if self.cmb_end.get() not in node_list:
                self.cmb_end.set(node_list[-1])

        if not rows:
            lbl = ctk.CTkLabel(
                self.road_list,
                text="No road network links registered.",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        for idx, r in enumerate(rows):
            is_open = (r["status"] == "OPEN")
            row_frame = ctk.CTkFrame(
                self.road_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

            # Segment
            ctk.CTkLabel(
                row_frame,
                text=f"Node {r['from_location']} ⇄ Node {r['to_location']}",
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=0, sticky="ew", padx=6, pady=5)

            # Distance
            ctk.CTkLabel(
                row_frame,
                text=f"{r['distance']:g} KM",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).grid(row=0, column=1, sticky="ew", padx=6, pady=5)

            # Condition Badge
            badge_bg = Theme.SUCCESS if is_open else Theme.DANGER
            ctk.CTkLabel(
                row_frame,
                text=f" {r['status']} ",
                fg_color=badge_bg,
                text_color="white",
                corner_radius=6,
                font=Theme.font_badge()
            ).grid(row=0, column=2, padx=4, pady=5)

            # Toggle Action
            btn = ctk.CTkButton(
                row_frame,
                text="Block" if is_open else "Open",
                width=65,
                height=24,
                corner_radius=5,
                fg_color=Theme.DANGER if is_open else Theme.SUCCESS,
                hover_color=Theme.DANGER_HOVER if is_open else Theme.SUCCESS_HOVER,
                font=Theme.font_small(),
                command=lambda rid=r["id"], st=r["status"]: self._toggle_road_status(rid, st)
            )
            btn.grid(row=0, column=3, padx=6, pady=5)
