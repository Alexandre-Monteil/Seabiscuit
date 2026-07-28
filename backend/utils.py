"""
SEABISCUIT - Utility Functions & Date/Distance Metric Parsers
Provides safe type conversions, datetime parsing for race post-times, metric distance formatters, and weather generators.
"""

from datetime import datetime
from typing import Any, Dict, Optional, List


def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely casts any value to float, handling None, string representations, or exceptions."""
    if val is None:
        return default
    try:
        if isinstance(val, str):
            val = val.replace("$", "").replace("%", "").replace(",", "").strip()
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val: Any, default: int = 0) -> int:
    """Safely casts any value to int."""
    if val is None:
        return default
    try:
        if isinstance(val, str):
            val = val.replace("$", "").replace("%", "").replace(",", "").strip()
        return int(float(val))
    except (ValueError, TypeError):
        return default


def normalize_array_input(val: Any) -> List[Any]:
    """Helper to ensure array/list inputs are normalized."""
    if isinstance(val, list):
        return val
    if isinstance(val, tuple):
        return list(val)
    return []


def format_race_distance(distance_raw: Any, furlongs: Optional[float] = None) -> str:
    """
    Formats distance into full metric notation with Furlongs, Meters, and Yards.
    1 Furlong = 201.168 meters = 220 yards.
    """
    if furlongs is None or furlongs <= 0.0:
        if isinstance(distance_raw, (int, float)):
            furlongs = float(distance_raw)
        elif isinstance(distance_raw, str):
            raw_lower = distance_raw.lower().strip()
            if "f" in raw_lower:
                try:
                    furlongs = float(raw_lower.replace("f", "").strip())
                except ValueError:
                    furlongs = 7.0
            elif "m" in raw_lower:
                try:
                    meters = float(raw_lower.replace("m", "").strip())
                    furlongs = meters / 201.168
                except ValueError:
                    furlongs = 7.0
            else:
                furlongs = safe_float(distance_raw, default=7.0)
        else:
            furlongs = 7.0

    meters = int(round(furlongs * 201.168))
    yards = int(round(furlongs * 220.0))

    if furlongs.is_integer():
        f_str = f"{int(furlongs)}f"
        lbl_str = f"{int(furlongs)} Furlongs"
    else:
        f_str = f"{furlongs:.1f}f"
        lbl_str = f"{furlongs:.1f} Furlongs"

    return f"{f_str} ({lbl_str} - {meters:,}m / {yards:,} yds)"


def get_race_weather_info(racecard: Dict[str, Any]) -> str:
    """Generates rich weather status string with temperature, rain status, wind speed, and moisture %."""
    going = str(racecard.get("going", "Good")).lower()
    moisture = safe_float(racecard.get("moisture_percent"), default=18.5)
    
    if "soft" in going or "heavy" in going or moisture > 30.0:
        weather_icon = "Rain"
        temp_c = 16
        wind_kmh = 18
    elif "firm" in going or moisture < 15.0:
        weather_icon = "Clear Sun"
        temp_c = 24
        wind_kmh = 9
    else:
        weather_icon = "Mild Clouds"
        temp_c = 21
        wind_kmh = 12

    return f"[{weather_icon}] | {temp_c}C | {wind_kmh} km/h Wind | Ground Moisture: {moisture:.1f}%"


def parse_race_datetime(racecard: Dict[str, Any]) -> datetime:
    """
    Parses exact race date & post-time into a Python datetime object for chronological auto-sorting.
    Defaults to today's date if date is unparseable.
    """
    if not isinstance(racecard, dict):
        return datetime.now()

    raw_date = str(racecard.get("race_date") or racecard.get("date") or datetime.now().strftime("%Y-%m-%d")).strip()
    raw_time = str(racecard.get("post_time") or racecard.get("off_time") or "15:00").strip()

    raw_time = raw_time.replace("GMT", "").replace("BST", "").replace("PM", "").replace("AM", "").strip()
    
    try:
        date_obj = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except Exception:
        date_obj = datetime.now().date()

    hh, mm = 15, 0
    if ":" in raw_time:
        parts = raw_time.split(":")
        try:
            hh = int(parts[0])
            mm = int(parts[1][:2])
        except Exception:
            pass

    return datetime.combine(date_obj, datetime.min.time()).replace(hour=hh, minute=mm)
