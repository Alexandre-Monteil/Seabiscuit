"""
BALLERS Main Application Entry Point
Executes the modular Streamlit frontend application.
"""
import os
import sys

app_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import frontend.app