import os
import sys
from pathlib import Path

# =====================================================================
# PERMANENT E-DRIVE STORAGE & CACHE ROUTING (EMERGENCY C-DRIVE LOCK)
# =====================================================================
CACHE_VAULT = Path(r"E:\GitHub\JESSICA_STORAGE\cache")
os.environ["HF_HOME"] = str(CACHE_VAULT / "huggingface")
os.environ["HUGGINGFACE_HUB_CACHE"] = str(CACHE_VAULT / "huggingface" / "hub")
os.environ["TORCH_HOME"] = str(CACHE_VAULT / "torch")
os.environ["PIP_CACHE_DIR"] = str(CACHE_VAULT / "pip")
os.environ["TEMP"] = str(CACHE_VAULT / "temp")
os.environ["TMP"] = str(CACHE_VAULT / "temp")
os.environ["ULTRALYTICS_CONFIG_DIR"] = str(CACHE_VAULT / "ultralytics")
os.makedirs(os.environ["TEMP"], exist_ok=True)
# =====================================================================

WORKSPACE_ROOT = Path(__file__).resolve().parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Redirect stdout and stderr to persistent log file so it never depends on terminal handles
log_path = WORKSPACE_ROOT / "jessica_server.log"
log_fp = open(log_path, "a", encoding="utf-8", buffering=1)
sys.stdout = log_fp
sys.stderr = log_fp

import uvicorn

if __name__ == "__main__":
    uvicorn.run("jessica_server:app", host="127.0.0.1", port=8000, access_log=False)
