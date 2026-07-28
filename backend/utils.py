"""
SEABISCUIT - General Utilities & Comprehensive Distance & DateTime Parsers
"""

import re
import pandas as pd
from datetime import datetime
from typing import Any, Optional, List, Dict


def safe_float(val: Any, default: float = 0.0) -> float:
    """
    Safely converts value to float, handling currency symbols (€, £, $), percentages, fractions, and None.
    Example: '€10,500' -> 10500.0, '£50,000' -> 50000.0.
    """
    if val is None or pd.isna(val):
        return default
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    if not val_str or val_str in ["-", "SP", "N/A"]:
        return default
        
    if "/" in val_str:
        try:
            parts = val_str.split("/")
            return float(parts[0]) / float(parts[1])
        except (ValueError, ZeroDivisionError):
            return default
            
    cleaned = re.sub(r'[^\d.-]', '', val_str)
    try:
        return float(cleaned)
    except ValueError:
        return default


def safe_int(val: Any, default: int = 0) -> int:
    """Safely converts value to int."""
    if val is None or pd.isna(val):
        return default
    try:
        cleaned = re.sub(r'[^\d.-]', '', str(val).strip())
        return int(float(cleaned))
    except ValueError:
        return default


def normalize_array_input(val: Any) -> List[Any]:
    """Ensures input is returned as a list."""
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def parse_race_datetime(rc: Dict[str, Any]) -> datetime:
    """
    Parses race date and post time into a accurate 24-hour datetime object for chronological auto-sorting.
    Converts 12-hour afternoon post times (e.g. 2:45, 3:20, 7:35) into 24-hour format (14:45, 15:20, 19:35).
    """
    now = datetime.now()
    if not isinstance(rc, dict):
        return now
        
    raw_date = str(rc.get("race_date", now.strftime("%Y-%m-%d"))).strip()
    post_time = str(rc.get("post_time", "12:00")).strip()
    
    time_match = re.search(r'(\d{1,2}):(\d{2})', post_time)
    if time_match:
        hh = int(time_match.group(1))
        mm = int(time_match.group(2))
        # Convert afternoon times (1:00 to 11:59) to 24h format if post time is standard racing hours
        if "pm" in post_time.lower() or (hh < 11 and "am" not in post_time.lower()):
            hh += 12
    else:
        hh, mm = 12, 0
        
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        return dt.replace(hour=min(23, hh), minute=min(59, mm))
    except Exception:
        return now


def format_race_distance(dist_raw: Any, dist_furlongs: Optional[float] = None) -> str:
    """
    Formats raw distance strings into full, crystal-clear text with Furlongs, Meters, and Yards.
    Example: '6f211y' -> '7f (7 Furlongs — 1,400m / 1,540 yds)'.
    """
    total_f = safe_float(dist_furlongs, default=0.0)
    if total_f <= 0.0:
        s = str(dist_raw).strip().lower()
        m_match = re.search(r'(\d+)m', s)
        f_match = re.search(r'(\d+)f', s)
        y_match = re.search(r'(\d+)y', s)

        miles = int(m_match.group(1)) if m_match else 0
        furlongs = int(f_match.group(1)) if f_match else 0
        yards = int(y_match.group(1)) if y_match else 0

        total_yards = miles * 1760 + furlongs * 220 + yards
        total_f = round(total_yards / 220.0, 1) if total_yards > 0 else 7.0

    total_yards = int(round(total_f * 220.0))
    total_meters = int(round(total_yards * 0.9144))

    if total_f >= 8.0:
        miles = int(total_f // 8)
        rem_f = round(total_f % 8, 1)
        rem_str = f" {rem_f:g}f" if rem_f > 0 else ""
        dist_name = f"{miles}m{rem_str}"
    else:
        dist_name = f"{total_f:g}f"

    return f"{dist_name} ({total_f:g} Furlongs — {total_meters:,}m / {total_yards:,} yds)"
