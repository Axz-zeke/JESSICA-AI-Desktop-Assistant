"""
Emergency Storage Recovery & E-Drive Migration Script
======================================================
Reclaims choked C: drive storage and permanently relocates all AI, Python,
and cache directories to high-capacity E: drive storage.

Features:
1. External E-Drive Cache Vault Creation:
   - E:\\GitHub\\JESSICA_STORAGE\\cache\\huggingface
   - E:\\GitHub\\JESSICA_STORAGE\\cache\\huggingface\\hub
   - E:\\GitHub\\JESSICA_STORAGE\\cache\\torch
   - E:\\GitHub\\JESSICA_STORAGE\\cache\\pip
   - E:\\GitHub\\JESSICA_STORAGE\\cache\\temp
   - E:\\GitHub\\JESSICA_STORAGE\\cache\\ultralytics
2. Safe Model Migration:
   - Moves existing Whisper & PyTorch models from C:\\Users\\<User>\\.cache to E:
3. Deep C-Drive Bloat Purge:
   - Deletes redundant .cache\\huggingface and .cache\\torch on C:
   - Executes pip cache purge (clearing multi-GB wheel cache on C:)
   - Cleans C:\\Users\\<User>\\AppData\\Local\\pip\\cache
   - Cleans temporary files in AppData\\Local\\Temp
   - Cleans abandoned installer updates in AppData\\Local\\SquirrelTemp
   - Cleans old crash dumps in AppData\\Local\\CrashDumps
4. Permanent Windows User Environment Variables:
   - Updates HKCU\\Environment via Windows Registry and PowerShell User scope
   - Broadcasts WM_SETTINGCHANGE to the OS subsystem
   - Hardens HF_HOME, HUGGINGFACE_HUB_CACHE, TORCH_HOME, PIP_CACHE_DIR, TEMP, TMP, ULTRALYTICS_CONFIG_DIR
"""

import os
import sys
import shutil
import subprocess
import json
import time
import winreg
import ctypes
from pathlib import Path

# Paths
HOME = Path(os.path.expanduser("~"))
E_VAULT = Path(r"E:\GitHub\JESSICA_STORAGE")
CACHE_VAULT = E_VAULT / "cache"

TARGET_DIRS = {
    "huggingface": CACHE_VAULT / "huggingface",
    "huggingface_hub": CACHE_VAULT / "huggingface" / "hub",
    "torch": CACHE_VAULT / "torch",
    "pip": CACHE_VAULT / "pip",
    "temp": CACHE_VAULT / "temp",
    "ultralytics": CACHE_VAULT / "ultralytics"
}

ENV_VARS = {
    "HF_HOME": str(TARGET_DIRS["huggingface"]),
    "HUGGINGFACE_HUB_CACHE": str(TARGET_DIRS["huggingface_hub"]),
    "TORCH_HOME": str(TARGET_DIRS["torch"]),
    "PIP_CACHE_DIR": str(TARGET_DIRS["pip"]),
    "TMP": str(TARGET_DIRS["temp"]),
    "TEMP": str(TARGET_DIRS["temp"]),
    "ULTRALYTICS_CONFIG_DIR": str(TARGET_DIRS["ultralytics"])
}

def get_disk_info(drive_letter="C:"):
    try:
        usage = shutil.disk_usage(drive_letter)
        return {
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "free_bytes": usage.free
        }
    except Exception as e:
        print(f"[!] Error reading disk {drive_letter}: {e}")
        return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "free_bytes": 0}

def get_dir_size_bytes(path):
    p = Path(path)
    if not p.exists():
        return 0
    total = 0
    try:
        if p.is_file():
            return p.stat().st_size
        for entry in p.rglob("*"):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
            except Exception:
                pass
    except Exception:
        pass
    return total

def safe_copy_tree(src: Path, dst: Path):
    """Recursively copy files from src to dst, skipping errors."""
    if not src.exists():
        return 0
    bytes_copied = 0
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_root = dst / rel
        target_root.mkdir(parents=True, exist_ok=True)
        for f in files:
            s_file = Path(root) / f
            d_file = target_root / f
            try:
                if not d_file.exists() or d_file.stat().st_size != s_file.stat().st_size:
                    shutil.copy2(s_file, d_file)
                    bytes_copied += s_file.stat().st_size
            except Exception as e:
                print(f"[!] Could not copy {s_file} -> {d_file}: {e}")
    return bytes_copied

def safe_remove_dir(path: Path):
    """Safely remove a directory tree, ignoring locked/in-use files."""
    if not path.exists():
        return 0
    reclaimed = 0
    for root, dirs, files in os.walk(str(path), topdown=False):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                os.chmod(fp, 0o777)
                os.remove(fp)
                reclaimed += sz
            except Exception:
                pass
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                os.rmdir(dp)
            except Exception:
                pass
    try:
        os.rmdir(str(path))
    except Exception:
        pass
    return reclaimed

def safe_clean_folder_contents(path: Path, max_age_seconds=0):
    """Clean contents of a folder without deleting the folder itself."""
    if not path.exists():
        return 0
    reclaimed = 0
    now = time.time()
    for root, dirs, files in os.walk(str(path), topdown=False):
        for f in files:
            fp = os.path.join(root, f)
            try:
                stat = os.stat(fp)
                if max_age_seconds > 0 and (now - stat.st_mtime) < max_age_seconds:
                    continue
                sz = stat.st_size
                os.chmod(fp, 0o777)
                os.remove(fp)
                reclaimed += sz
            except Exception:
                pass
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                os.rmdir(dp)
            except Exception:
                pass
    return reclaimed

def set_windows_user_env():
    """Permanently sets Windows User environment variables via Registry & PowerShell."""
    print("\n[*] Setting Permanent Windows User Environment Variables...")
    
    # 1. Update Registry (HKCU\Environment)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE)
        for var_name, var_value in ENV_VARS.items():
            winreg.SetValueEx(key, var_name, 0, winreg.REG_SZ, var_value)
            print(f"  [+] Registry HKCU\\Environment\\{var_name} = {var_value}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[!] Registry update failed: {e}")

    # 2. Update via PowerShell [Environment]::SetEnvironmentVariable (User scope)
    for var_name, var_value in ENV_VARS.items():
        try:
            ps_cmd = f"[System.Environment]::SetEnvironmentVariable('{var_name}', '{var_value}', [System.EnvironmentVariableTarget]::User)"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, check=True)
        except Exception as e:
            print(f"[!] PowerShell env set failed for {var_name}: {e}")

    # 3. Update current process environment
    for var_name, var_value in ENV_VARS.items():
        os.environ[var_name] = var_value

    # 4. Broadcast WM_SETTINGCHANGE to Windows shell
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result)
        )
        print("  [+] Broadcasted WM_SETTINGCHANGE to Windows shell successfully.")
    except Exception as e:
        print(f"[!] WM_SETTINGCHANGE broadcast notice: {e}")

def main():
    print("=" * 70)
    print("      JESSICA EMERGENCY C-DRIVE RECLAMATION & E-DRIVE VAULT LOCK")
    print("=" * 70)

    # Step 0: Record initial disk space
    c_before = get_disk_info("C:")
    e_before = get_disk_info("E:")
    print(f"[*] Initial C: Drive State -> Free: {c_before['free_gb']} GB / {c_before['total_gb']} GB")
    print(f"[*] Initial E: Drive State -> Free: {e_before['free_gb']} GB / {e_before['total_gb']} GB")

    # Step 1: Create External E-Drive Cache Vault
    print("\n[*] Step 1: Creating E-Drive Cache Vault Directories...")
    for name, p in TARGET_DIRS.items():
        p.mkdir(parents=True, exist_ok=True)
        print(f"  [+] Vault Directory Ready: {p}")

    # Step 2: Migrate Active Model Weights
    print("\n[*] Step 2: Migrating Active Model Weights & Checkpoints from C: to E:...")
    c_hf = HOME / ".cache" / "huggingface"
    c_torch = HOME / ".cache" / "torch"
    
    hf_size = get_dir_size_bytes(c_hf)
    torch_size = get_dir_size_bytes(c_torch)
    print(f"  [i] Found {hf_size / (1024**2):.1f} MB in C: Hugging Face cache.")
    print(f"  [i] Found {torch_size / (1024**2):.1f} MB in C: Torch cache.")

    if c_hf.exists():
        print(f"  [*] Copying Hugging Face cache to {TARGET_DIRS['huggingface']}...")
        copied = safe_copy_tree(c_hf, TARGET_DIRS["huggingface"])
        print(f"  [+] Copied {copied / (1024**2):.1f} MB to E: vault.")

    if c_torch.exists():
        print(f"  [*] Copying PyTorch cache to {TARGET_DIRS['torch']}...")
        copied = safe_copy_tree(c_torch, TARGET_DIRS["torch"])
        print(f"  [+] Copied {copied / (1024**2):.1f} MB to E: vault.")

    # Step 3: Purge C-Drive Bloat
    print("\n[*] Step 3: Purging Bloat from C: Drive...")
    reclaimed_details = {}

    # 3a. Delete .cache/huggingface on C:
    if c_hf.exists():
        rec = safe_remove_dir(c_hf)
        reclaimed_details["c_cache_huggingface"] = round(rec / (1024**3), 3)
        print(f"  [+] Deleted C:\\.cache\\huggingface -> Reclaimed {rec / (1024**2):.1f} MB")

    # 3b. Delete .cache/torch on C:
    if c_torch.exists():
        rec = safe_remove_dir(c_torch)
        reclaimed_details["c_cache_torch"] = round(rec / (1024**3), 3)
        print(f"  [+] Deleted C:\\.cache\\torch -> Reclaimed {rec / (1024**2):.1f} MB")

    # 3c. Delete .cache/ultralytics on C:
    c_ultralytics = HOME / ".cache" / "ultralytics"
    if c_ultralytics.exists():
        rec = safe_remove_dir(c_ultralytics)
        reclaimed_details["c_cache_ultralytics"] = round(rec / (1024**3), 3)
        print(f"  [+] Deleted C:\\.cache\\ultralytics -> Reclaimed {rec / (1024**2):.1f} MB")

    # 3d. Pip cache purge
    print("  [*] Running pip cache purge...")
    try:
        pip_exe = sys.executable.replace("python.exe", "pip.exe")
        res = subprocess.run([pip_exe, "cache", "purge"], capture_output=True, text=True)
        print(f"  [+] pip cache purge output: {res.stdout.strip()}")
    except Exception as e:
        print(f"[!] pip cache purge notice: {e}")

    # Also clean AppData/Local/pip/cache
    c_pip_cache = HOME / "AppData" / "Local" / "pip" / "cache"
    if c_pip_cache.exists():
        rec = safe_remove_dir(c_pip_cache)
        reclaimed_details["c_pip_cache_folder"] = round(rec / (1024**3), 3)
        print(f"  [+] Cleared C:\\AppData\\Local\\pip\\cache -> Reclaimed {rec / (1024**2):.1f} MB")

    # 3e. Purge AppData/Local/Temp
    c_temp = HOME / "AppData" / "Local" / "Temp"
    if c_temp.exists():
        print("  [*] Purging temporary files in C:\\AppData\\Local\\Temp...")
        rec = safe_clean_folder_contents(c_temp)
        reclaimed_details["c_temp"] = round(rec / (1024**3), 3)
        print(f"  [+] Purged C:\\AppData\\Local\\Temp -> Reclaimed {rec / (1024**2):.1f} MB")

    # 3f. Purge AppData/Local/SquirrelTemp (massive installer junk)
    c_squirrel = HOME / "AppData" / "Local" / "SquirrelTemp"
    if c_squirrel.exists():
        print("  [*] Purging abandoned installer updates in C:\\AppData\\Local\\SquirrelTemp...")
        rec = safe_remove_dir(c_squirrel)
        reclaimed_details["c_squirrel_temp"] = round(rec / (1024**3), 3)
        print(f"  [+] Purged C:\\AppData\\Local\\SquirrelTemp -> Reclaimed {rec / (1024**3):.2f} GB")

    # 3g. Purge AppData/Local/CrashDumps
    c_dumps = HOME / "AppData" / "Local" / "CrashDumps"
    if c_dumps.exists():
        print("  [*] Purging old crash dumps in C:\\AppData\\Local\\CrashDumps...")
        rec = safe_remove_dir(c_dumps)
        reclaimed_details["c_crash_dumps"] = round(rec / (1024**3), 3)
        print(f"  [+] Purged C:\\AppData\\Local\\CrashDumps -> Reclaimed {rec / (1024**2):.1f} MB")

    # Step 4: Set Permanent Windows User Environment Variables
    set_windows_user_env()

    # Step 5: Post-migration disk audit
    c_after = get_disk_info("C:")
    e_after = get_disk_info("E:")
    reclaimed_gb = round(c_after["free_gb"] - c_before["free_gb"], 2)
    print("\n" + "=" * 70)
    print(f"[*] RECLAMATION COMPLETE!")
    print(f"[*] C: Drive Before: {c_before['free_gb']} GB Free | After: {c_after['free_gb']} GB Free")
    print(f"[*] Net Reclaimed Space on C: Drive: +{reclaimed_gb} GB")
    print(f"[*] E: Drive State: {e_after['free_gb']} GB Free / {e_after['total_gb']} GB Total")
    print("=" * 70)

    # Save summary report to JSON
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "c_drive_before_gb": c_before,
        "c_drive_after_gb": c_after,
        "reclaimed_gb": reclaimed_gb,
        "e_drive_state": e_after,
        "reclaimed_details_gb": reclaimed_details,
        "environment_variables": ENV_VARS
    }

    report_path = Path("evals/emergency_storage_reclamation_results.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"[+] Reclaim results persisted to: {report_path}")

    return report_data

if __name__ == "__main__":
    main()

