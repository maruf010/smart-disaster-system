import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from algorithms.resource_allocation import proportional_allocation
from gui.theme import Theme
from utils.helper import format_datetime

class ResourceView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_inventory_table()
        self._build_allocation_panel()
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
            text="📦 Relief Supplies Inventory & Proportional Distribution",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Track warehouse stockpiles, minimum inventory alerts, timestamps, and perform demographic-proportional relief distribution",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(1, 0))

    def _build_inventory_table(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        container.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        container.grid_rowconfigure(4, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text="Warehouse Supply Stockpiles",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))

        # Add supply sub-card
        add_form = ctk.CTkFrame(
            container,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        add_form.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        add_form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.ent_res_name = ctk.CTkEntry(
            add_form,
            placeholder_text="Item (e.g. Rice)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_res_name.grid(row=0, column=0, padx=3, pady=4, sticky="ew")

        self.cmb_res_cat = ctk.CTkComboBox(
            add_form,
            values=["Food & Water", "Medical", "Shelter Kits", "Hygiene", "Rescue Gear"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_res_cat.grid(row=0, column=1, padx=3, pady=4, sticky="ew")
        self.cmb_res_cat.set("Food & Water")

        self.ent_res_qty = ctk.CTkEntry(
            add_form,
            placeholder_text="Qty (e.g. 5000)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_res_qty.grid(row=0, column=2, padx=3, pady=4, sticky="ew")

        self.ent_res_unit = ctk.CTkEntry(
            add_form,
            placeholder_text="Unit (kg/liter)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_res_unit.grid(row=0, column=3, padx=3, pady=4, sticky="ew")

        self.ent_res_min = ctk.CTkEntry(
            add_form,
            placeholder_text="Min Alert Qty (e.g. 500)",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_res_min.grid(row=1, column=0, columnspan=2, padx=3, pady=(0, 4), sticky="ew")

        btn_add = ctk.CTkButton(
            add_form,
            text="Add to Stockpile",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_small(),
            command=self._add_resource
        )
        btn_add.grid(row=1, column=2, columnspan=2, padx=3, pady=(0, 4), sticky="ew")

        # Filters Bar for Inventory
        inv_filter = ctk.CTkFrame(container, fg_color="transparent")
        inv_filter.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 4))
        inv_filter.grid_columnconfigure(0, weight=1)

        self.res_search = ctk.CTkEntry(
            inv_filter,
            placeholder_text="🔍 Search supply name...",
            height=28,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.res_search.grid(row=0, column=0, padx=(0, 3), sticky="ew")
        self.res_search.bind("<KeyRelease>", lambda e: self.refresh())

        self.f_res_cat = ctk.CTkComboBox(
            inv_filter,
            values=["All Categories", "Food & Water", "Medical", "Shelter Kits", "Hygiene", "Rescue Gear"],
            width=130,
            height=28,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_res_cat.grid(row=0, column=1, padx=3)
        self.f_res_cat.set("All Categories")

        self.f_res_status = ctk.CTkComboBox(
            inv_filter,
            values=["All Stock", "Critical Stock", "Sufficient"],
            width=120,
            height=28,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=lambda v: self.refresh()
        )
        self.f_res_status.grid(row=0, column=2, padx=3)
        self.f_res_status.set("All Stock")

        # Table Header
        th = ctk.CTkFrame(
            container,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HEADER
        )
        th.grid(row=3, column=0, sticky="ew", padx=8, pady=(2, 0))
        th.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(th, text="SUPPLY ITEM", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(th, text="CURRENT STOCK", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(th, text="ALERT MIN", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=2, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(th, text="🕒 ADDED TIME", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=3, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(th, text="STATUS", font=Theme.font_badge(), text_color=Theme.TEXT_MUTED, anchor="center").grid(row=0, column=4, padx=6, pady=4)

        self.inv_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.inv_list.grid(row=4, column=0, sticky="nsew", padx=4, pady=3)
        self.inv_list.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    def _build_allocation_panel(self):
        alloc_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        alloc_card.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
        alloc_card.grid_rowconfigure(3, weight=1)
        alloc_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            alloc_card,
            text="⚖️ Smart Proportional Allocation Solver",
            font=Theme.font_sub(),
            text_color=Theme.TEXT_MAIN
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            alloc_card,
            text="Proportional relief formula distributing supplies fairly across affected areas.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            wraplength=360,
            justify="left"
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 6))

        controls_box = ctk.CTkFrame(alloc_card, fg_color="transparent")
        controls_box.grid(row=2, column=0, sticky="ew", padx=8, pady=2)
        controls_box.grid_columnconfigure((0, 1), weight=1)

        self.cmb_alloc_res = ctk.CTkComboBox(
            controls_box,
            values=["Select Resource"],
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.cmb_alloc_res.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        self.ent_alloc_qty = ctk.CTkEntry(
            controls_box,
            placeholder_text="Quantity to Distribute",
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        self.ent_alloc_qty.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        # Dynamic area entries
        self.areas_frame = ctk.CTkScrollableFrame(
            alloc_card,
            label_text="Affected Areas & Target Populations",
            height=110,
            fg_color=Theme.BG_CARD_ALT
        )
        self.areas_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=4)
        self.areas_frame.grid_columnconfigure((0, 1), weight=1)

        self.area_rows = []
        for i in range(3):
            self._add_area_row()

        btn_row = ctk.CTkFrame(alloc_card, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="ew", padx=8, pady=4)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        btn_more = ctk.CTkButton(
            btn_row,
            text="➕ Add Area",
            height=30,
            corner_radius=6,
            fg_color=Theme.PRIMARY_LIGHT,
            text_color=Theme.PRIMARY,
            hover_color=Theme.BORDER_COLOR,
            font=Theme.font_small(),
            command=self._add_area_row
        )
        btn_more.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        btn_calc = ctk.CTkButton(
            btn_row,
            text="Calculate & Execute",
            height=30,
            corner_radius=6,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_small(),
            command=self._execute_allocation
        )
        btn_calc.grid(row=0, column=1, padx=(3, 0), sticky="ew")

        # Result box
        self.result_box = ctk.CTkFrame(
            alloc_card,
            corner_radius=8,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        self.result_box.grid(row=5, column=0, sticky="ew", padx=8, pady=(4, 10))

        self.lbl_alloc_summary = ctk.CTkLabel(
            self.result_box,
            text="Configure areas and click 'Calculate & Execute' to preview plan.",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_alloc_summary.pack(padx=8, pady=6)

    def _add_area_row(self):
        idx = len(self.area_rows) + 1
        row = ctk.CTkFrame(self.areas_frame, fg_color="transparent")
        row.pack(fill="x", pady=1)
        row.grid_columnconfigure((0, 1), weight=1)

        ent_a = ctk.CTkEntry(
            row,
            placeholder_text=f"Area {idx} (e.g. Region {chr(64+idx)})",
            height=28,
            corner_radius=5,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        ent_a.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        ent_p = ctk.CTkEntry(
            row,
            placeholder_text="Population (e.g. 5000)",
            height=28,
            corner_radius=5,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            font=Theme.font_small()
        )
        ent_p.grid(row=0, column=1, padx=(2, 0), sticky="ew")

        self.area_rows.append((ent_a, ent_p))

    def _add_resource(self):
        name = self.ent_res_name.get().strip()
        cat = self.cmb_res_cat.get().strip()
        qty_str = self.ent_res_qty.get().strip()
        unit = self.ent_res_unit.get().strip()
        min_str = self.ent_res_min.get().strip() or "0"

        if not name or not qty_str or not unit:
            messagebox.showwarning("Validation Error", "Please provide resource name, quantity, and unit.")
            return

        try:
            qty = float(qty_str)
            min_stock = float(min_str)
            if qty < 0 or min_stock < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity and Minimum Stock must be valid numbers.")
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO resources(name, category, quantity, unit, minimum_stock) VALUES (?, ?, ?, ?, ?)",
                (name, cat, qty, unit, min_stock)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Relief resource '{name}' added to inventory.")
            self.ent_res_name.delete(0, "end")
            self.ent_res_qty.delete(0, "end")
            self.ent_res_unit.delete(0, "end")
            self.ent_res_min.delete(0, "end")
            self.refresh()
        finally:
            conn.close()

    def _execute_allocation(self):
        sel = self.cmb_alloc_res.get()
        if not sel or sel.startswith("Select"):
            messagebox.showwarning("Input Needed", "Please select a supply resource.")
            return

        try:
            res_id = int(sel.split(":")[0].replace("#", "").strip())
        except Exception:
            messagebox.showerror("Error", "Could not parse selected resource ID.")
            return

        qty_str = self.ent_alloc_qty.get().strip()
        try:
            amount = float(qty_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive quantity.")
            return

        conn = get_connection()
        try:
            res = conn.execute("SELECT * FROM resources WHERE id=?", (res_id,)).fetchone()
            if not res:
                messagebox.showerror("Error", "Resource not found in database.")
                return

            if amount > res["quantity"]:
                messagebox.showerror("Insufficient Stock", f"Only {res['quantity']} {res['unit']} available. Cannot allocate {amount} {res['unit']}.")
                return

            area_populations = {}
            for ent_a, ent_p in self.area_rows:
                aname = ent_a.get().strip()
                pstr = ent_p.get().strip()
                if aname and pstr:
                    try:
                        pop = int(pstr)
                        if pop > 0:
                            area_populations[aname] = pop
                    except ValueError:
                        pass

            if not area_populations:
                messagebox.showwarning("Input Needed", "Please enter at least one area with valid population.")
                return

            allocations = proportional_allocation(amount, area_populations)

            for area, allocated_q in allocations.items():
                conn.execute(
                    "INSERT INTO resource_allocations(resource_id, area, population, allocated_quantity) VALUES (?, ?, ?, ?)",
                    (res_id, area, area_populations[area], allocated_q)
                )

            conn.execute("UPDATE resources SET quantity=quantity-? WHERE id=?", (amount, res_id))
            conn.commit()

            lines = [f"✅ Fair Allocation Plan for {amount} {res['unit']} of {res['name']}:"]
            for a, q in allocations.items():
                pct = (area_populations[a] / sum(area_populations.values())) * 100
                lines.append(f"• 📍 {a} (Pop: {area_populations[a]:,}, Share: {pct:.1f}%): {q} {res['unit']}")

            self.lbl_alloc_summary.configure(text="\n".join(lines), text_color=Theme.SUCCESS)
            messagebox.showinfo("Allocation Executed", "Supplies proportionally distributed and inventory balance updated!")
            self.refresh()
        finally:
            conn.close()

    def refresh(self):
        for w in self.inv_list.winfo_children():
            w.destroy()

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM resources ORDER BY id").fetchall()
        finally:
            conn.close()

        options = [f"#{r['id']}: {r['name']} ({r['quantity']} {r['unit']} avail)" for r in rows]
        if options:
            self.cmb_alloc_res.configure(values=options)
            if self.cmb_alloc_res.get() not in options:
                self.cmb_alloc_res.set(options[0])
        else:
            self.cmb_alloc_res.configure(values=["No resources available"])
            self.cmb_alloc_res.set("No resources available")

        # Filtering
        q = self.res_search.get().strip().lower() if hasattr(self, 'res_search') else ""
        cat_f = self.f_res_cat.get() if hasattr(self, 'f_res_cat') else "All Categories"
        status_f = self.f_res_status.get() if hasattr(self, 'f_res_status') else "All Stock"

        filtered = []
        for r in rows:
            is_critical = (r["quantity"] <= r["minimum_stock"])
            if cat_f != "All Categories" and r["category"].upper() != cat_f.upper():
                continue
            if status_f == "Critical Stock" and not is_critical:
                continue
            if status_f == "Sufficient" and is_critical:
                continue
            if q:
                n = str(r["name"] or "").lower()
                c = str(r["category"] or "").lower()
                if q not in n and q not in c:
                    continue
            filtered.append(r)

        if not filtered:
            msg = "No supplies match your filter criteria." if rows else "No supply items in inventory."
            lbl = ctk.CTkLabel(
                self.inv_list,
                text=msg,
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl.pack(pady=16)
            return

        for idx, r in enumerate(filtered):
            is_critical = (r["quantity"] <= r["minimum_stock"])
            row_frame = ctk.CTkFrame(
                self.inv_list,
                fg_color=Theme.BG_ROW_EVEN if idx % 2 == 0 else "transparent",
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_COLOR_LIGHT
            )
            row_frame.pack(fill="x", padx=2, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

            # Name & Category
            lbl_name = ctk.CTkLabel(
                row_frame,
                text=f"#{r['id']} {r['name']}\n({r['category']})",
                font=Theme.font_body_bold(),
                text_color=Theme.TEXT_MAIN,
                anchor="w",
                justify="left"
            )
            lbl_name.grid(row=0, column=0, sticky="ew", padx=6, pady=4)

            # Qty
            lbl_qty = ctk.CTkLabel(
                row_frame,
                text=f"{r['quantity']:g} {r['unit']}",
                font=Theme.font_body_bold(),
                text_color=Theme.PRIMARY,
                anchor="w"
            )
            lbl_qty.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

            # Min Stock
            lbl_min = ctk.CTkLabel(
                row_frame,
                text=f"{r['minimum_stock']:g} {r['unit']}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            )
            lbl_min.grid(row=0, column=2, sticky="ew", padx=6, pady=4)

            # Added Time
            time_str = format_datetime(r["created_at"]) if "created_at" in r.keys() else "N/A"
            lbl_time = ctk.CTkLabel(
                row_frame,
                text=f"🕒 {time_str}",
                font=Theme.font_small(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            )
            lbl_time.grid(row=0, column=3, sticky="ew", padx=6, pady=4)

            # Badge
            badge_bg = Theme.DANGER if is_critical else Theme.SUCCESS
            badge_txt = " CRITICAL " if is_critical else " SUFFICIENT "
            ctk.CTkLabel(
                row_frame,
                text=badge_txt,
                fg_color=badge_bg,
                text_color="white",
                corner_radius=6,
                font=Theme.font_badge()
            ).grid(row=0, column=4, padx=4, pady=4)
