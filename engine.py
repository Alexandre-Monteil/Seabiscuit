"""
SEABISCUIT - Core Engine Facade
Provides clean top-level imports for Equine Stock Engine, Time Series, 3D Visualizations, and The Racing API.
"""

from backend.theracingapi_client import TheRacingAPIClient
from backend.equine_stock_engine import EquineStockEngine
from backend.time_series_engine import EquineTimeSeriesEngine
from backend.visualization_3d import EquineVisualization3D
from backend.portfolio_engine import EquinePortfolioEngine
from backend.deepseek_intel_engine import DeepSeekIntelEngine

__all__ = [
    "TheRacingAPIClient",
    "EquineStockEngine",
    "EquineTimeSeriesEngine",
    "EquineVisualization3D",
    "EquinePortfolioEngine",
    "DeepSeekIntelEngine"
]