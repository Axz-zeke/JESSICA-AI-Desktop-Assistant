"""
Jessica Desktop App - Native Desktop Window Launcher (v0.2)
Starts Jessica's sovereign FastAPI Mission Control server and opens a standalone native desktop window.
"""

import sys
import os
import time
import socket
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(r"E:\Documents\GitHub\JESSICA")
if not WORKSPACE_ROOT.exists():
    WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def is_port_open(port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def launch():
    print("=" * 60)
    print("      LAUNCHING JESSICA SOVEREIGN MISSION CONTROL")
    print("=" * 60)

    # 1. Ensure backend server is running
    if not is_port_open(8000):
        print("[*] Starting Jessica Server backend daemon on port 8000...")
        venv_py = WORKSPACE_ROOT / "venv" / "Scripts" / "python.exe"
        python_bin = str(venv_py) if venv_py.exists() else sys.executable

        server_proc = subprocess.Popen(
            [python_bin, "jessica_server.py"],
            cwd=str(WORKSPACE_ROOT),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        )

        # Wait for server to start
        for _ in range(15):
            time.sleep(0.5)
            if is_port_open(8000):
                print("[+] Jessica Mission Control Server is ONLINE.")
                break
    else:
        print("[+] Backend server already active on port 8000.")

    app_url = "http://127.0.0.1:8000"

    # 2. Launch native standalone application window with redirected E: drive cache
    cache_dir = r"E:\GitHub\JESSICA_STORAGE\cache\browser_cache"
    profile_dir = r"E:\GitHub\JESSICA_STORAGE\cache\browser_profile"
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(profile_dir, exist_ok=True)

    edge_paths = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]

    launched = False
    for p in edge_paths:
        if p.exists():
            print(f"[+] Launching native desktop window via {p.name} (Standalone App Mode with E: cache lock)...")
            subprocess.Popen([
                str(p),
                f"--app={app_url}",
                f"--disk-cache-dir={cache_dir}",
                f"--user-data-dir={profile_dir}",
                "--window-size=1440,900",
                "--window-position=50,50"
            ])
            launched = True
            break

    if not launched:
        print("[*] Launching via Windows shell application mode with E: cache lock...")
        subprocess.Popen(f'start msedge --app={app_url} --disk-cache-dir="{cache_dir}" --user-data-dir="{profile_dir}" --window-size=1440,900', shell=True)

    print("[+] Jessica Native Desktop Mission Control window launched successfully.")


if __name__ == "__main__":
    launch()
