from datetime import datetime

def pause():
    input("\nPress Enter to continue...")

def format_datetime(dt_str):
    """
    Format SQLite timestamp or ISO string into a clean, readable representation.
    E.g. '2026-10-07 01:15:30' -> '07 Oct 2026, 01:15 AM'
    """
    if not dt_str:
        return "N/A"
    
    dt_str = str(dt_str).strip()
    # Try different known SQLite datetime formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.strftime("%d %b %Y, %I:%M %p")
        except ValueError:
            continue
            
    return dt_str
