import customtkinter as ctk
from gui.theme import Theme

class StatCard(ctk.CTkFrame):
    """
    Standard Compact SaaS/Enterprise KPI Card.
    Layout:
    ┌──────────────────────────────────────────────┐
    │ LABEL / TITLE (muted uppercase)      [ ICON ]│
    │ 2,800                                        │
    │ ↳ subtitle/trend (optional)                  │
    └──────────────────────────────────────────────┘
    """
    def __init__(self, master, title, value, subtitle="", icon="📊", accent_color="#4F46E5", **kwargs):
        super().__init__(
            master,
            corner_radius=10,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT,
            height=90,
            **kwargs
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=0)

        # Top row: Title on left, compact Icon badge on right
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
        top_row.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            top_row,
            text=title.upper(),
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Compact icon pill
        self.icon_badge = ctk.CTkFrame(
            top_row,
            width=28,
            height=28,
            corner_radius=7,
            fg_color=(Theme.BG_ROOT[0], "#141D2C"),
            border_width=1,
            border_color=Theme.BORDER_COLOR_LIGHT
        )
        self.icon_badge.grid(row=0, column=1, sticky="e")
        self.icon_badge.grid_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_badge,
            text=icon,
            font=ctk.CTkFont(size=14)
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Value row
        val_row = ctk.CTkFrame(self, fg_color="transparent")
        val_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 2))
        val_row.grid_columnconfigure(1, weight=1)

        # Colored indicator dot
        self.dot = ctk.CTkFrame(
            val_row,
            width=6,
            height=6,
            corner_radius=3,
            fg_color=accent_color
        )
        self.dot.grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(4, 0))

        self.value_label = ctk.CTkLabel(
            val_row,
            text=str(value),
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        )
        self.value_label.grid(row=0, column=1, sticky="w")

        # Subtitle (optional)
        self.sub_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        if subtitle:
            self.sub_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 6))

    def update_value(self, new_val, new_subtitle=None):
        self.value_label.configure(text=str(new_val))
        if new_subtitle is not None:
            self.sub_label.configure(text=str(new_subtitle))
            if not self.sub_label.winfo_ismapped():
                self.sub_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 6))
