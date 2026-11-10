import math
from PIL import Image, ImageDraw
import customtkinter as ctk

# In-memory cache for rendered CTkImage objects: (name, color, size, dark_color) -> CTkImage
_ICON_CACHE = {}

def _hex_to_rgba(hex_code, alpha=255):
    """Convert hex string (e.g. #4F46E5 or #FFF) to RGBA tuple."""
    if not isinstance(hex_code, str) or not hex_code.startswith("#"):
        # Handle named or fallback
        if hex_code == "white":
            return (255, 255, 255, alpha)
        return (100, 116, 139, alpha)
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join(2 * c for c in hex_code)
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    return (r, g, b, alpha)


def _draw_vector_icon(name, color_hex, size=24):
    """
    Renders a crisp, anti-aliased single-color vector icon as a PIL Image.
    Uses 4x supersampling and downsampling with LANCZOS filter.
    """
    scale = 4
    dim = size * scale
    im = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = _hex_to_rgba(color_hex)
    s = scale
    lw = max(1, int(1.8 * s))

    # Normalize name
    n = name.lower().strip()

    if n in ("shield", "logo", "brand"):
        # Elegant security crest
        pts = [
            (12 * s, 2.5 * s),
            (20.5 * s, 5.5 * s),
            (20.5 * s, 12.5 * s),
            (12 * s, 21.5 * s),
            (3.5 * s, 12.5 * s),
            (3.5 * s, 5.5 * s)
        ]
        d.polygon(pts, fill=c)

    elif n in ("dashboard", "grid", "layout"):
        # 4 rounded modern tiles
        bs = 6.5 * s
        r = 1.8 * s
        d.rounded_rectangle([3.5 * s, 3.5 * s, 3.5 * s + bs, 3.5 * s + bs], radius=r, fill=c)
        d.rounded_rectangle([14 * s, 3.5 * s, 14 * s + bs, 3.5 * s + bs], radius=r, fill=c)
        d.rounded_rectangle([3.5 * s, 14 * s, 3.5 * s + bs, 14 * s + bs], radius=r, fill=c)
        d.rounded_rectangle([14 * s, 14 * s, 14 * s + bs, 14 * s + bs], radius=r, fill=c)

    elif n in ("disaster", "alert", "warning"):
        # Alert triangle outline with exclamation mark
        pts = [(12 * s, 3 * s), (21.5 * s, 20 * s), (2.5 * s, 20 * s)]
        d.polygon(pts, fill=c)
        # Transparent cutout stencil mask
        mask = Image.new("L", (dim, dim), 255)
        dm = ImageDraw.Draw(mask)
        dm.line([(12 * s, 8 * s), (12 * s, 14 * s)], fill=0, width=int(2.2 * s))
        dm.ellipse([10.8 * s, 16 * s, 13.2 * s, 18.4 * s], fill=0)
        im.putalpha(Image.composite(im.split()[3], Image.new("L", (dim, dim), 0), mask))

    elif n in ("emergency", "siren", "bell"):
        # Bell / Emergency alarm beacon
        d.chord([6.5 * s, 7 * s, 17.5 * s, 18 * s], start=180, end=0, fill=c)
        d.rectangle([6.5 * s, 12.5 * s, 17.5 * s, 16.5 * s], fill=c)
        d.rounded_rectangle([4.5 * s, 16.5 * s, 19.5 * s, 18.5 * s], radius=1 * s, fill=c)
        d.ellipse([10.5 * s, 19 * s, 13.5 * s, 21 * s], fill=c)
        d.ellipse([11 * s, 4 * s, 13 * s, 7 * s], fill=c)

    elif n in ("shelter", "home", "house"):
        # Modern geometric house/shelter
        roof = [(12 * s, 2.5 * s), (21.5 * s, 10.5 * s), (2.5 * s, 10.5 * s)]
        d.polygon(roof, fill=c)
        d.rounded_rectangle([5 * s, 10 * s, 19 * s, 21 * s], radius=1.5 * s, fill=c)

    elif n in ("resource", "package", "box", "inventory"):
        # Supply package box
        d.rounded_rectangle([3.5 * s, 6 * s, 20.5 * s, 20.5 * s], radius=2 * s, fill=c)
        # Clean subtle seam cutout
        mask = Image.new("L", (dim, dim), 255)
        dm = ImageDraw.Draw(mask)
        dm.line([(3.5 * s, 11 * s), (20.5 * s, 11 * s)], fill=0, width=int(1.8 * s))
        dm.line([(12 * s, 11 * s), (12 * s, 20.5 * s)], fill=0, width=int(1.8 * s))
        im.putalpha(Image.composite(im.split()[3], Image.new("L", (dim, dim), 0), mask))

    elif n in ("rescue", "squad", "ambulance"):
        # Medical rescue cross badge
        d.rounded_rectangle([3.5 * s, 3.5 * s, 20.5 * s, 20.5 * s], radius=4.5 * s, fill=c)
        mask = Image.new("L", (dim, dim), 255)
        dm = ImageDraw.Draw(mask)
        dm.rectangle([10 * s, 6.5 * s, 14 * s, 17.5 * s], fill=0)
        dm.rectangle([6.5 * s, 10 * s, 17.5 * s, 14 * s], fill=0)
        im.putalpha(Image.composite(im.split()[3], Image.new("L", (dim, dim), 0), mask))

    elif n in ("volunteer", "users", "people", "team"):
        # Two stylized people profiles
        d.ellipse([6 * s, 4 * s, 12 * s, 10 * s], fill=c)
        d.chord([3 * s, 11.5 * s, 15 * s, 22.5 * s], start=180, end=0, fill=c)
        d.ellipse([13 * s, 6 * s, 18 * s, 11 * s], fill=c)
        d.chord([11 * s, 12.5 * s, 20.5 * s, 22.5 * s], start=180, end=0, fill=c)

    elif n in ("routes", "navigation", "compass", "direction"):
        # Modern navigation arrow tilted 45 degrees
        pts = [(12 * s, 3 * s), (20 * s, 20.5 * s), (12 * s, 16.5 * s), (4 * s, 20.5 * s)]
        d.polygon(pts, fill=c)

    elif n in ("reports", "chart", "analytics", "stats"):
        # Clean 3-bar analytical chart
        d.rounded_rectangle([4 * s, 13 * s, 8 * s, 20.5 * s], radius=1 * s, fill=c)
        d.rounded_rectangle([10 * s, 8 * s, 14 * s, 20.5 * s], radius=1 * s, fill=c)
        d.rounded_rectangle([16 * s, 3.5 * s, 20 * s, 20.5 * s], radius=1 * s, fill=c)

    elif n in ("user", "avatar", "person", "profile"):
        # Circle avatar with head and shoulders
        d.ellipse([3 * s, 3 * s, 21 * s, 21 * s], outline=c, width=lw)
        d.ellipse([9 * s, 6 * s, 15 * s, 12 * s], fill=c)
        d.chord([6 * s, 13.5 * s, 18 * s, 24 * s], start=180, end=0, fill=c)

    elif n in ("check", "resolved", "success", "done"):
        # Crisp checkmark
        pts = [(4.5 * s, 12 * s), (9.5 * s, 17 * s), (19.5 * s, 6.5 * s)]
        d.line(pts, fill=c, width=int(2.4 * s), joint="round")

    elif n in ("clock", "time", "pending", "history"):
        # Clock face with hands at 3:00
        d.ellipse([3.5 * s, 3.5 * s, 20.5 * s, 20.5 * s], outline=c, width=lw)
        d.line([(12 * s, 12 * s), (12 * s, 6.5 * s)], fill=c, width=lw)
        d.line([(12 * s, 12 * s), (16.5 * s, 12 * s)], fill=c, width=lw)

    elif n in ("lock", "admin", "secure"):
        # Padlock
        d.rounded_rectangle([5 * s, 10 * s, 19 * s, 20.5 * s], radius=2 * s, fill=c)
        d.arc([8 * s, 3.5 * s, 16 * s, 13.5 * s], start=180, end=0, fill=c, width=lw)
        mask = Image.new("L", (dim, dim), 255)
        dm = ImageDraw.Draw(mask)
        dm.ellipse([10.8 * s, 13.5 * s, 13.2 * s, 16.5 * s], fill=0)
        im.putalpha(Image.composite(im.split()[3], Image.new("L", (dim, dim), 0), mask))

    elif n in ("pin", "location", "marker"):
        # Map location pin
        d.ellipse([7 * s, 3 * s, 17 * s, 13 * s], fill=c)
        pts = [(7.2 * s, 10.5 * s), (16.8 * s, 10.5 * s), (12 * s, 21.5 * s)]
        d.polygon(pts, fill=c)
        mask = Image.new("L", (dim, dim), 255)
        dm = ImageDraw.Draw(mask)
        dm.ellipse([10 * s, 6 * s, 14 * s, 10 * s], fill=0)
        im.putalpha(Image.composite(im.split()[3], Image.new("L", (dim, dim), 0), mask))

    elif n in ("search", "find"):
        # Magnifying glass
        d.ellipse([4 * s, 4 * s, 15 * s, 15 * s], outline=c, width=lw)
        d.line([(13 * s, 13 * s), (20 * s, 20 * s)], fill=c, width=int(2.4 * s))

    elif n in ("refresh", "reload", "sync"):
        # Circular refresh arc
        d.arc([4 * s, 4 * s, 20 * s, 20 * s], start=45, end=315, fill=c, width=lw)
        arrow = [(19 * s, 6 * s), (21.5 * s, 11 * s), (15.5 * s, 10 * s)]
        d.polygon(arrow, fill=c)

    elif n in ("plus", "add", "create"):
        # Plus symbol
        d.line([(12 * s, 5 * s), (12 * s, 19 * s)], fill=c, width=int(2.4 * s))
        d.line([(5 * s, 12 * s), (19 * s, 12 * s)], fill=c, width=int(2.4 * s))

    elif n in ("phone", "call", "contact"):
        # Phone receiver
        d.rounded_rectangle([7 * s, 4 * s, 17 * s, 20 * s], radius=2.5 * s, outline=c, width=lw)
        d.ellipse([11 * s, 16.5 * s, 13 * s, 18.5 * s], fill=c)
        d.line([(10 * s, 6.5 * s), (14 * s, 6.5 * s)], fill=c, width=int(1.5 * s))

    elif n in ("download", "export"):
        # Download tray & arrow
        d.line([(12 * s, 4 * s), (12 * s, 15 * s)], fill=c, width=lw)
        d.polygon([(9 * s, 13 * s), (12 * s, 17 * s), (15 * s, 13 * s)], fill=c)
        d.line([(5 * s, 15 * s), (5 * s, 20 * s), (19 * s, 20 * s), (19 * s, 15 * s)], fill=c, width=lw)

    elif n in ("logout", "exit"):
        # Door with exit arrow
        d.rounded_rectangle([4 * s, 4 * s, 13 * s, 20 * s], radius=1 * s, outline=c, width=lw)
        d.line([(10 * s, 12 * s), (20 * s, 12 * s)], fill=c, width=lw)
        d.polygon([(17 * s, 9 * s), (21 * s, 12 * s), (17 * s, 15 * s)], fill=c)

    elif n in ("target", "crosshair"):
        # Target/crosshair for best-fit
        d.ellipse([4 * s, 4 * s, 20 * s, 20 * s], outline=c, width=lw)
        d.ellipse([9 * s, 9 * s, 15 * s, 15 * s], fill=c)
        d.line([(12 * s, 2 * s), (12 * s, 6 * s)], fill=c, width=lw)
        d.line([(12 * s, 18 * s), (12 * s, 22 * s)], fill=c, width=lw)
        d.line([(2 * s, 12 * s), (6 * s, 12 * s)], fill=c, width=lw)
        d.line([(18 * s, 12 * s), (22 * s, 12 * s)], fill=c, width=lw)

    else:
        # Default elegant circle dot
        d.ellipse([7 * s, 7 * s, 17 * s, 17 * s], fill=c)

    return im.resize((size, size), Image.Resampling.LANCZOS)


def get_icon(name, color="#4F46E5", size=20, dark_color=None):
    """
    Returns a cached CTkImage for the specified vector icon name and color.
    If dark_color is provided or if color is a tuple, CTkImage supports automatic
    appearance mode switching.
    """
    if isinstance(color, (tuple, list)):
        light_c = color[0]
        dark_c = color[1]
    else:
        light_c = color
        dark_c = dark_color if dark_color is not None else color

    cache_key = (name, light_c, dark_c, size)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    light_img = _draw_vector_icon(name, light_c, size)
    dark_img = _draw_vector_icon(name, dark_c, size)

    ctk_img = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=(size, size))
    _ICON_CACHE[cache_key] = ctk_img
    return ctk_img

