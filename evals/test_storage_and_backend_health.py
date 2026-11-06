import os
import sys
import shutil
import subprocess
import json
import time
import urllib.request
import winreg
from pathlib import Path

def test_storage_and_backend():
    print("=" * 70)
    print("   STORAGE RECOVERY & SOVEREIGN BACKEND HEALTH AUDIT")
    print("=" * 70)

    # 1. Drive space audit
    c_usage = shutil.disk_usage("C:")
    e_usage = shutil.disk_usage("E:")
    c_free_gb = round(c_usage.free / (1024**3), 2)
    c_total_gb = round(c_usage.total / (1024**3), 2)
    e_free_gb = round(e_usage.free / (1024**3), 2)
    e_total_gb = round(e_usage.total / (1024**3), 2)

    print(f"[+] C: Drive: {c_free_gb} GB Free / {c_total_gb} GB Total")
    print(f"[+] E: Drive: {e_free_gb} GB Free / {e_total_gb} GB Total")

    # 2. Windows Environment Variables Verification
    env_keys = [
        "HF_HOME",
        "HUGGINGFACE_HUB_CACHE",
        "TORCH_HOME",
        "PIP_CACHE_DIR",
        "TEMP",
        "TMP",
        "ULTRALYTICS_CONFIG_DIR"
    ]
    
    print("\n[*] Auditing Windows User Environment Variables (HKCU\\Environment)...")
    reg_verified = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
        for k in env_keys:
            try:
                val, _ = winreg.QueryValueEx(key, k)
                reg_verified[k] = val
                assert val.startswith("E:\\GitHub\\JESSICA_STORAGE\\cache"), f"Invalid path for {k}: {val}"
                print(f"  [PASS] {k} -> {val}")
            except Exception as e:
                print(f"  [FAIL] {k}: {e}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[!] Registry open error: {e}")

    # 3. Cache directory verification
    print("\n[*] Auditing E: Drive Cache Vault Directories...")
    vault_dirs = [
        r"E:\GitHub\JESSICA_STORAGE\cache\huggingface",
        r"E:\GitHub\JESSICA_STORAGE\cache\huggingface\hub",
        r"E:\GitHub\JESSICA_STORAGE\cache\torch",
        r"E:\GitHub\JESSICA_STORAGE\cache\pip",
        r"E:\GitHub\JESSICA_STORAGE\cache\temp",
        r"E:\GitHub\JESSICA_STORAGE\cache\ultralytics"
    ]
    for vd in vault_dirs:
        exists = os.path.isdir(vd)
        print(f"  [{'PASS' if exists else 'FAIL'}] {vd} (exists: {exists})")

    # 4. Verify C:\.cache has no leftover HF or Torch bloat
    home = Path(os.path.expanduser("~"))
    c_hf_leftover = (home / ".cache" / "huggingface").exists()
    c_torch_leftover = (home / ".cache" / "torch").exists()
    print(f"\n[*] C: Drive Cache Cleanup Verification:")
    print(f"  [{'PASS' if not c_hf_leftover else 'FAIL'}] C:\\.cache\\huggingface removed: {not c_hf_leftover}")
    print(f"  [{'PASS' if not c_torch_leftover else 'FAIL'}] C:\\.cache\\torch removed: {not c_torch_leftover}")

    # 5. Launch detached backend and ping /api/status
    print("\n[*] Starting Jessica Sovereign Server with E: Drive Lock...")
    # Free port 8000 first if any
    try:
        subprocess.run(
            ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"],
            capture_output=True
        )
    except Exception:
        pass

    py_exe = sys.executable
    launch_cmd = f"powershell -Command \"Start-Process -FilePath '{py_exe}' -ArgumentList 'run_server.py' -WorkingDirectory 'E:\\Documents\\GitHub\\JESSICA' -WindowStyle Hidden\""
    subprocess.run(launch_cmd, shell=True)

    print("[*] Waiting for server startup on http://127.0.0.1:8000 (up to 15s)...")
    status_data = None
    for attempt in range(15):
        time.sleep(1.0)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/api/status", timeout=2) as resp:
                if resp.status == 200:
                    status_data = json.loads(resp.read().decode("utf-8"))
                    print(f"[+] Server responded HTTP 200 at attempt {attempt+1}!")
                    break
        except Exception:
            pass

    if status_data:
        print("\n=== Live Jessica Server Health ===")
        print(f"  Agent: {status_data.get('agent')} v{status_data.get('version')}")
        print(f"  Device: {status_data.get('device')}")
        print(f"  Cortex Checkpoint: {status_data.get('cortex_checkpoint')}")
        print(f"  VRAM Allocated: {status_data.get('vram_allocated_mb')} MB")
        print(f"  Vault Indexed: {status_data.get('vault_indexed')} notes")
        print(f"  Active Microphone: {status_data.get('wake_word', {}).get('active_microphone')}")
        backend_ok = True
    else:
        print("[!] Server did not respond within timeout.")
        backend_ok = False

    audit_summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "c_drive_free_gb": c_free_gb,
        "c_drive_total_gb": c_total_gb,
        "e_drive_free_gb": e_free_gb,
        "e_drive_total_gb": e_total_gb,
        "registry_environment_variables": reg_verified,
        "c_caches_purged": (not c_hf_leftover) and (not c_torch_leftover),
        "backend_ok": backend_ok,
        "server_status": status_data
    }

    out_file = Path("evals/final_storage_health_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)

    print(f"\n[+] Audit results persisted to: {out_file}")
    return audit_summary

if __name__ == "__main__":
    test_storage_and_backend()

