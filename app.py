"""
SEABISCUIT - Root Streamlit Entry Point (for `streamlit run app.py` / Streamlit Cloud)
Delegates to the modular frontend application in frontend/app.py.
"""
import os
import sys

app_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import frontend.app

# frontend.app.main() only auto-runs under its own `if __name__ == "__main__"` guard,
# which does not fire when the module is imported (as opposed to run directly) — so it
# must be called explicitly here for `streamlit run app.py` to actually render the page.
frontend.app.main()