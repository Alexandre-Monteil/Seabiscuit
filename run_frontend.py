"""
SEABISCUIT - Streamlit Frontend Runner (Production & Tunnel Compatible Edition)
Automatically detects virtual environment (venv) and launches Streamlit with external tunnel support.
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    root_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Auto-detect venv python executable
    venv_python = os.path.join(root_dir, "venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable

    env = os.environ.copy()
    env["PYTHONPATH"] = root_dir + os.pathsep + env.get("PYTHONPATH", "")

    print(f"Starting SEABISCUIT Streamlit Quant Terminal using [{python_exe}]...")
    subprocess.run([
        python_exe, "-m", "streamlit", "run", "frontend/app.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ], env=env, cwd=root_dir)
