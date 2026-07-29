"""
SEABISCUIT - Institutional Equine Stock Exchange FastAPI Router
Exposes high-frequency microservices for racecards, horse asset metrics, 3D visualizations, and The Racing API data.
"""

from fastapi import APIRouter, Query
from typing import Dict, Any
from .theracingapi_client import TheRacingAPIClient
from .equine_stock_engine import EquineStockEngine
from .time_series_engine import EquineTimeSeriesEngine
from .deepseek_intel_engine import DeepSeekIntelEngine

router = APIRouter(prefix="/api/v1/seabiscuit", tags=["SEABISCUIT Equine Exchange"])

client = TheRacingAPIClient()
intel_engine = DeepSeekIntelEngine()


@router.get("/racecards", summary="Fetch upcoming racecards with equity stock metrics")
def get_racecards():
    """Returns all featured racecards converted into Wall Street Equine Equity Assets."""
    raw_racecards = client.get_upcoming_racecards()
    processed = [EquineStockEngine.process_racecard(rc) for rc in raw_racecards]
    return {"status": "success", "count": len(processed), "racecards": processed}


@router.get("/jockey/{jockey_id}/owners", summary="Fetch jockey-owner synergy breakdown")
def get_jockey_owners(jockey_id: str = "jky_257379"):
    """Returns Jockey vs Owner win rate, A/E ratio, and 1-Unit P/L synergy."""
    data = client.get_jockey_owner_analysis(jockey_id)
    return {"status": "success", "data": data}


@router.get("/jockey/{jockey_id}/courses", summary="Fetch jockey course performance breakdown")
def get_jockey_courses(jockey_id: str = "jky_257379"):
    """Returns Jockey performance by course."""
    data = client.get_jockey_course_analysis(jockey_id)
    return {"status": "success", "data": data}


@router.get("/horse/{horse_id}/distance-times", summary="Fetch horse distance & time breakdowns")
def get_horse_distance_times(horse_id: str = "hrs_25481624"):
    """Returns Horse distance & time breakdowns."""
    data = client.get_horse_distance_times_analysis(horse_id)
    return {"status": "success", "data": data}


@router.get("/eex-index", summary="Fetch $EEX Composite Market Index")
def get_eex_index(days: int = Query(90, ge=7, le=365)):
    """Returns historical $EEX Composite Market Index time-series."""
    df_eex = EquineTimeSeriesEngine.compute_eex_composite_index(days=days)
    return {"status": "success", "days": days, "index_data": df_eex.to_dict(orient="records")}


@router.post("/intel-dossier", summary="Generate DeepSeek AI Executive Market Intelligence Dossier")
def generate_intel_dossier(racecard: Dict[str, Any]):
    """Generates an executive quantitative market dossier for a racecard."""
    dossier = intel_engine.generate_race_dossier(racecard)
    return dossier
