import customtkinter as ctk

# Professional Design System & Palette Tokens for SDERMS
class Theme:
    # Surface & Backgrounds
    BG_ROOT = ("#F1F5F9", "#0F172A")       # Light: Slate 100, Dark: Slate 900
    BG_SIDEBAR = ("#FFFFFF", "#0A0F1D")    # Light: White, Dark: Deep midnight
    BG_CARD = ("#FFFFFF", "#1E293B")       # Light: White, Dark: Slate 800
    BG_CARD_ALT = ("#F8FAFC", "#162032")   # Subtle card inner
    BG_ROW_EVEN = ("#F8FAFC", "#1E293B")
    BG_ROW_ODD = ("#FFFFFF", "#182234")
    BG_INPUT = ("#F8FAFC", "#0F172A")
    BG_HEADER = ("#E2E8F0", "#243248")

    # Borders
    BORDER_COLOR = ("#CBD5E1", "#334155")
    BORDER_COLOR_LIGHT = ("#E2E8F0", "#1E293B")
    BORDER_ACCENT = ("#818CF8", "#4F46E5")

    # Primary Brand / Accent
    PRIMARY = "#4F46E5"        # Indigo 600
    PRIMARY_HOVER = "#4338CA"  # Indigo 700
    PRIMARY_LIGHT = ("#EEF2FF", "#312E81")

    # Status Colors
    SUCCESS = "#10B981"        # Emerald 500
    SUCCESS_HOVER = "#059669"
    SUCCESS_BG = ("#D1FAE5", "#064E3B")

    DANGER = "#EF4444"         # Red 500
    DANGER_HOVER = "#DC2626"
    DANGER_BG = ("#FEE2E2", "#7F1D1D")

    WARNING = "#F59E0B"        # Amber 500
    WARNING_HOVER = "#D97706"
    WARNING_BG = ("#FEF3C7", "#78350F")

    INFO = "#0EA5E9"           # Sky 500
    INFO_HOVER = "#0284C7"
    INFO_BG = ("#E0F2FE", "#0C4A6E")

    PURPLE = "#8B5CF6"         # Violet 500
    TEAL = "#14B8A6"           # Teal 500

    # Text Colors
    TEXT_MAIN = ("#0F172A", "#F8FAFC")
    TEXT_MUTED = ("#64748B", "#94A3B8")
    TEXT_SUBTLE = ("#94A3B8", "#64748B")

    # Typography
    FONT_FAMILY = "Segoe UI"

    @classmethod
    def font_title(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=22, weight="bold")

    @classmethod
    def font_section(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=16, weight="bold")

    @classmethod
    def font_sub(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="bold")

    @classmethod
    def font_body(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12)

    @classmethod
    def font_body_bold(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="bold")

    @classmethod
    def font_small(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=11)

    @classmethod
    def font_badge(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=10, weight="bold")
