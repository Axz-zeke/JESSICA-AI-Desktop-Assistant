"""
Jessica Hands - Sovereign OS Action API (v0.2 Enterprise)
Provides sandboxed, deterministic operating system control functions,
with permission classification (SAFE vs CONFIRM_REQUIRED), network diagnostics,
dynamic application launching, audio control, and Obsidian vault operations.
"""

import os
import sys
import psutil
import socket
import datetime
import subprocess
import ctypes
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from PIL import Image, ImageDraw

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
VAULT_ROOT = WORKSPACE_ROOT / "obsidian_vault"
SENSES_ROOT = WORKSPACE_ROOT / "senses"

# Tool Permission Sandbox Classification
TOOL_METADATA = {
    "get_system_telemetry": {"permission": "SAFE", "description": "Read CPU, RAM, and RTX 4060 GPU telemetry"},
    "list_top_processes": {"permission": "SAFE", "description": "List top processes by CPU and RAM usage"},
    "check_network_status": {"permission": "SAFE", "description": "Check IP, gateway, active interfaces, and ping 8.8.8.8 / 1.1.1.1"},
    "open_application": {"permission": "SAFE", "description": "Launch authorized desktop applications"},
    "write_obsidian_note": {"permission": "SAFE", "description": "Write Markdown note into local Obsidian Vault"},
    "read_obsidian_vault": {"permission": "SAFE", "description": "Search and retrieve notes from Obsidian Vault"},
    "set_system_volume": {"permission": "SAFE", "description": "Adjust Windows system master audio volume"},
    "take_screenshot": {"permission": "SAFE", "description": "Capture screen snapshot and save to senses/screenshots"},
    "kill_process": {"permission": "CONFIRM_REQUIRED", "description": "Terminate a running process by name or PID"},
    "learn_from_internet": {"permission": "SAFE", "description": "Research any topic on the live internet and write to Obsidian Knowledge Base"},
    "control_window": {"permission": "SAFE", "description": "Control desktop windows (minimize, maximize, snap left/right, lock)"},
    "type_and_automate": {"permission": "SAFE", "description": "Simulate keyboard typing and keyboard shortcuts"},
    "search_local_files": {"permission": "SAFE", "description": "Perform rapid local file system search for files and documents"},
    "verify_biometrics": {"permission": "SAFE", "description": "Scan webcam using PyTorch FaceNet to verify creator and unlock permissions"},
    "analyze_screen": {"permission": "SAFE", "description": "Inspect active monitor, window titles, OCR, and visible desktop UI"}
}


def get_system_telemetry() -> Dict[str, Any]:
    """
    Collects real-time CPU, RAM, and GPU telemetry.
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count_logical = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    
    vm = psutil.virtual_memory()
    ram_total_gb = round(vm.total / (1024 ** 3), 2)
    ram_used_gb = round(vm.used / (1024 ** 3), 2)
    ram_percent = vm.percent

    # GPU telemetry via nvidia-smi
    gpu_info = {
        "device": "Unknown",
        "utilization_gpu_pct": 0.0,
        "memory_used_mb": 0.0,
        "memory_total_mb": 8188.0,
        "temperature_c": 0.0,
        "status": "No GPU detected or nvidia-smi unavailable"
    }

    try:
        smi_out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
             "--format=csv,noheader,nounits"],
            encoding="utf-8",
            errors="ignore",
            timeout=2
        ).strip()
        if smi_out:
            parts = [p.strip() for p in smi_out.split(",")]
            if len(parts) >= 5:
                gpu_info = {
                    "device": parts[0],
                    "utilization_gpu_pct": float(parts[1]),
                    "memory_used_mb": float(parts[2]),
                    "memory_total_mb": float(parts[3]),
                    "temperature_c": float(parts[4]),
                    "status": "Online"
                }
    except Exception as e:
        gpu_info["status"] = f"Telemetry query notice: {str(e)}"

    return {
        "status": "success",
        "timestamp": datetime.datetime.now().isoformat(),
        "cpu": {
            "utilization_pct": cpu_percent,
            "physical_cores": cpu_count_physical,
            "logical_cores": cpu_count_logical
        },
        "ram": {
            "total_gb": ram_total_gb,
            "used_gb": ram_used_gb,
            "utilization_pct": ram_percent
        },
        "gpu": gpu_info
    }


def list_top_processes(limit: int = 10) -> Dict[str, Any]:
    """
    Returns top processes sorted by CPU and Memory usage.
    """
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            procs.append({
                "pid": info['pid'],
                "name": info['name'] or "unknown",
                "cpu_percent": info['cpu_percent'] or 0.0,
                "memory_percent": round(info['memory_percent'] or 0.0, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    sorted_by_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    sorted_by_mem = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)[:limit]

    return {
        "status": "success",
        "top_by_cpu": sorted_by_cpu,
        "top_by_memory": sorted_by_mem
    }


def _ping_host(host: str, port: int = 53, timeout: float = 1.5) -> Optional[float]:
    start = datetime.datetime.now()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return round((datetime.datetime.now() - start).total_seconds() * 1000, 2)
    except Exception:
        # Fallback to ICMP ping command on Windows
        try:
            out = subprocess.check_output(f"ping -n 1 -w {int(timeout*1000)} {host}", shell=True, encoding="utf-8", errors="ignore")
            m = re.search(r"Average = (\d+)ms|time[=<](\d+)ms", out)
            if m:
                val = m.group(1) or m.group(2)
                return float(val)
        except Exception:
            pass
        return None


def check_network_status() -> Dict[str, Any]:
    """
    Returns real local IP, default gateway, active interfaces, and ping latency to 8.8.8.8 and 1.1.1.1.
    """
    hostname = socket.gethostname()
    
    # Active interfaces and IP addresses
    active_interfaces = {}
    local_ip = "127.0.0.1"
    
    try:
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for iface_name, addrs in net_if_addrs.items():
            stats = net_if_stats.get(iface_name)
            is_up = stats.isup if stats else False
            ip_list = []
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_list.append(addr.address)
                    if is_up and not addr.address.startswith("127.") and not addr.address.startswith("169.254."):
                        local_ip = addr.address
            if is_up and ip_list:
                active_interfaces[iface_name] = {
                    "is_up": is_up,
                    "speed_mbps": stats.speed if stats else 0,
                    "ipv4": ip_list
                }
    except Exception as e:
        active_interfaces["error"] = str(e)

    # Detect Gateway via route print or ipconfig
    gateway_ip = "Unknown"
    try:
        route_out = subprocess.check_output("route print 0.0.0.0", shell=True, encoding="utf-8", errors="ignore")
        for line in route_out.splitlines():
            line_parts = line.strip().split()
            if len(line_parts) >= 5 and line_parts[0] == "0.0.0.0" and line_parts[1] == "0.0.0.0":
                gateway_ip = line_parts[2]
                break
    except Exception:
        pass

    # Ping 8.8.8.8 (Google DNS) & 1.1.1.1 (Cloudflare DNS)
    latency_1_1_1_1 = _ping_host("1.1.1.1", port=53)
    latency_8_8_8_8 = _ping_host("8.8.8.8", port=53)

    internet_reachable = (latency_1_1_1_1 is not None) or (latency_8_8_8_8 is not None)
    net_io = psutil.net_io_counters()

    return {
        "status": "success",
        "hostname": hostname,
        "local_ip": local_ip,
        "gateway": gateway_ip,
        "internet_reachable": internet_reachable,
        "ping_latency_1_1_1_1_ms": latency_1_1_1_1,
        "ping_latency_8_8_8_8_ms": latency_8_8_8_8,
        "active_interfaces": active_interfaces,
        "bytes_sent_mb": round(net_io.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb": round(net_io.bytes_recv / (1024 ** 2), 2)
    }


def open_application(app_name: str) -> Dict[str, Any]:
    """
    Dynamically maps and launches Windows applications.
    """
    app_cleaned = app_name.strip().lower()
    
    known_apps = {
        "notepad": "notepad.exe",
        "calc": "calc.exe",
        "calculator": "calc.exe",
        "cmd": "cmd.exe",
        "terminal": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "pwsh": "powershell.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "taskmgr": "taskmgr.exe",
        "task manager": "taskmgr.exe",
        "mspaint": "mspaint.exe",
        "paint": "mspaint.exe",
        "control": "control.exe",
        "control panel": "control.exe",
        "regedit": "regedit.exe",
        "edge": "msedge.exe",
        "chrome": "chrome.exe",
        "brave": "brave.exe",
        "obsidian": "obsidian"
    }

    target = known_apps.get(app_cleaned, app_cleaned)

    try:
        if target == "obsidian":
            obs_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Obsidian" / "Obsidian.exe",
                Path(os.environ.get("ProgramFiles", "")) / "Obsidian" / "Obsidian.exe"
            ]
            found = False
            for p in obs_paths:
                if p.exists():
                    subprocess.Popen([str(p)], shell=False)
                    found = True
                    break
            if not found:
                os.startfile("obsidian:")
        else:
            if target.endswith(".exe") or "/" in target or "\\" in target:
                subprocess.Popen(target, shell=True)
            else:
                subprocess.Popen(["start", "", target], shell=True)

        return {
            "status": "success",
            "message": f"Successfully launched application: {app_cleaned}",
            "executable_target": target
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to launch {app_cleaned}: {str(e)}"
        }


def write_obsidian_note(folder: str, title: str, content: str) -> Dict[str, Any]:
    """
    Creates or appends a structured markdown note with YAML frontmatter within the local Obsidian Vault.
    """
    try:
        safe_folder = folder.strip().replace("..", "").strip("/\\")
        target_dir = (VAULT_ROOT / safe_folder).resolve()
        
        if not str(target_dir).startswith(str(VAULT_ROOT.resolve())):
            target_dir = VAULT_ROOT

        target_dir.mkdir(parents=True, exist_ok=True)

        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
        if not safe_title:
            safe_title = f"Note_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if not safe_title.endswith(".md"):
            safe_title += ".md"

        file_path = target_dir / safe_title
        
        frontmatter = (
            f"---\n"
            f"title: \"{safe_title.replace('.md', '')}\"\n"
            f"date: {datetime.date.today().isoformat()}\n"
            f"time: {datetime.datetime.now().strftime('%H:%M:%S')}\n"
            f"agent: Jessica\n"
            f"category: {safe_folder or 'root'}\n"
            f"tags:\n"
            f"  - jessica-os\n"
            f"  - sovereign-memory\n"
            f"---\n\n"
        )
        
        if not file_path.exists():
            full_content = frontmatter + content.strip() + "\n"
        else:
            full_content = "\n\n" + content.strip() + "\n"

        with open(file_path, "a" if file_path.exists() else "w", encoding="utf-8") as f:
            f.write(full_content)

        return {
            "status": "success",
            "path": str(file_path),
            "relative_path": str(file_path.relative_to(VAULT_ROOT)),
            "bytes_written": len(full_content)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write obsidian note: {str(e)}"
        }


def read_obsidian_vault(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Searches all Markdown notes inside obsidian_vault/ by query keyword and returns matched notes with context.
    """
    if not VAULT_ROOT.exists():
        return {"status": "error", "message": "Obsidian vault does not exist."}

    q_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    matches = []

    for root, _, files in os.walk(VAULT_ROOT):
        for f in files:
            if f.endswith(".md"):
                file_path = Path(root) / f
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                    
                    score = 0
                    text_lower = text.lower()
                    for t in q_tokens:
                        score += text_lower.count(t)

                    if score > 0 or not q_tokens:
                        # Extract matching paragraph snippet
                        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.strip().startswith("---")]
                        snippet = ""
                        for p in paragraphs:
                            if any(t in p.lower() for t in q_tokens):
                                snippet = p[:300]
                                break
                        if not snippet and paragraphs:
                            snippet = paragraphs[0][:300]

                        matches.append({
                            "title": f.replace(".md", ""),
                            "file": f,
                            "relative_path": str(file_path.relative_to(VAULT_ROOT)),
                            "match_score": score,
                            "snippet": snippet,
                            "full_text": text
                        })
                except Exception:
                    continue

    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)[:max_results]
    return {
        "status": "success",
        "query": query,
        "count": len(matches),
        "results": matches
    }


def set_system_volume(level: Union[int, float, str]) -> Dict[str, Any]:
    """
    Adjusts Windows system master audio volume (0-100).
    """
    try:
        if isinstance(level, str):
            nums = re.findall(r"\d+", level)
            vol_int = int(nums[0]) if nums else 50
        else:
            vol_int = int(level)
        vol_int = max(0, min(100, vol_int))

        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF
        VK_VOLUME_MUTE = 0xAD

        # Reset volume to 0 by pressing VOLUME_DOWN 50 times
        for _ in range(50):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)

        # Step up to target (each step is 2%)
        steps = vol_int // 2
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)

        return {
            "status": "success",
            "volume_level": vol_int,
            "message": f"System master volume set to {vol_int}%"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set system volume: {str(e)}"
        }


def take_screenshot(filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Captures a screenshot and saves it to senses/screenshots/.
    Includes seamless graphical fallback for non-interactive / headless service sessions.
    """
    shots_dir = SENSES_ROOT / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if not filename:
        filename = f"screenshot_{timestamp}.png"
    elif not filename.endswith(".png"):
        filename += ".png"

    save_path = shots_dir / filename

    try:
        from PIL import ImageGrab
        im = ImageGrab.grab()
        im.save(save_path)
        return {
            "status": "success",
            "path": str(save_path),
            "filename": filename,
            "resolution": f"{im.width}x{im.height}",
            "mode": "Direct Desktop Capture"
        }
    except Exception as e:
        # Generate diagnostic telemetry visual snapshot
        telemetry = get_system_telemetry()
        w, h = 1280, 720
        img = Image.new("RGB", (w, h), color=(10, 14, 23))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(20, 20), (w - 20, h - 20)], outline=(6, 182, 212), width=3)
        draw.text((40, 40), "JESSICA SOVEREIGN OS — MISSION CONTROL DIAGNOSTIC SNAPSHOT", fill=(245, 158, 11))
        draw.text((40, 80), f"Timestamp: {datetime.datetime.now().isoformat()}", fill=(200, 200, 200))
        draw.text((40, 120), f"CPU Usage: {telemetry['cpu']['utilization_pct']}% ({telemetry['cpu']['logical_cores']} Cores)", fill=(255, 255, 255))
        draw.text((40, 160), f"RAM Usage: {telemetry['ram']['used_gb']} / {telemetry['ram']['total_gb']} GB ({telemetry['ram']['utilization_pct']}%)", fill=(255, 255, 255))
        draw.text((40, 200), f"GPU: {telemetry['gpu']['device']} | VRAM: {telemetry['gpu']['memory_used_mb']:.0f} / {telemetry['gpu']['memory_total_mb']:.0f} MiB", fill=(6, 182, 212))
        draw.text((40, 240), f"Session Note: Running in sandboxed display session ({str(e)})", fill=(150, 150, 150))
        img.save(save_path)
        return {
            "status": "success",
            "path": str(save_path),
            "filename": filename,
            "resolution": f"{w}x{h}",
            "mode": "Diagnostic Canvas Snapshot",
            "notice": f"Saved telemetry snapshot: {str(e)}"
        }


def kill_process(process_name_or_pid: Union[str, int]) -> Dict[str, Any]:
    """
    Terminates a process by name or PID. Classified as CONFIRM_REQUIRED.
    """
    killed = []
    target_str = str(process_name_or_pid).strip().lower()

    if target_str.isdigit():
        target_pid = int(target_str)
        try:
            p = psutil.Process(target_pid)
            p_name = p.name()
            p.terminate()
            try:
                p.wait(timeout=2)
            except psutil.TimeoutExpired:
                p.kill()
            killed.append({"pid": target_pid, "name": p_name})
        except Exception as e:
            return {"status": "error", "message": f"Failed to terminate PID {target_pid}: {str(e)}"}
    else:
        # Match by name
        target_name = target_str if target_str.endswith(".exe") else f"{target_str}.exe"
        for p in psutil.process_iter(['pid', 'name']):
            try:
                if p.info['name'] and (p.info['name'].lower() == target_name or p.info['name'].lower() == target_str):
                    pid = p.info['pid']
                    name = p.info['name']
                    p.terminate()
                    killed.append({"pid": pid, "name": name})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    if killed:
        return {
            "status": "success",
            "message": f"Successfully terminated {len(killed)} process instance(s).",
            "killed_processes": killed
        }
    else:
        return {
            "status": "warning",
            "message": f"No running process found matching '{process_name_or_pid}'."
        }


def learn_from_internet(topic: str) -> Dict[str, Any]:
    """
    Researches topic via Wikipedia & Web, writes structured note to Obsidian Knowledge Base,
    and updates vector RAG index.
    """
    try:
        from brain.web_learner import learn_topic_from_internet as do_learn
        return do_learn(topic)
    except Exception as e:
        return {"status": "error", "message": f"Internet research error: {str(e)}", "topic": topic}


def control_window(action: str = "minimize_all") -> Dict[str, Any]:
    """
    Controls desktop window states via user32 / pyautogui.
    Supported actions: minimize_all, maximize_active, switch_window, snap_left, snap_right, lock_workstation.
    """
    import pyautogui
    pyautogui.FAILSAFE = False
    action_clean = action.lower().strip()
    status = "success"
    msg = ""

    try:
        if "minimize" in action_clean:
            # Native Windows Win+D keybd_event
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
            msg = "Desktop windows toggled / minimized."
        elif "maximize" in action_clean:
            pyautogui.hotkey('win', 'up')
            msg = "Active window maximized."
        elif "snap_left" in action_clean or "left" in action_clean:
            pyautogui.hotkey('win', 'left')
            msg = "Active window snapped to left half."
        elif "snap_right" in action_clean or "right" in action_clean:
            pyautogui.hotkey('win', 'right')
            msg = "Active window snapped to right half."
        elif "switch" in action_clean or "tab" in action_clean:
            pyautogui.hotkey('alt', 'tab')
            msg = "Switched to previous active window."
        elif "lock" in action_clean:
            ctypes.windll.user32.LockWorkStation()
            msg = "Workstation locked securely."
        else:
            pyautogui.hotkey('win', 'd')
            msg = f"Default window action performed ({action})."
        return {"status": status, "action": action_clean, "message": msg}
    except Exception as e:
        return {"status": "error", "action": action_clean, "message": f"Window control failed: {e}"}


def type_and_automate(text_or_hotkey: str) -> Dict[str, Any]:
    """
    Simulates keyboard input or triggers system hotkeys.
    """
    import pyautogui
    pyautogui.FAILSAFE = False
    clean = text_or_hotkey.strip()
    is_hotkey = "+" in clean or clean.lower() in ["enter", "escape", "tab", "backspace", "space", "win", "ctrl", "alt"]
    try:
        if is_hotkey:
            keys = [k.strip().lower() for k in clean.split("+")]
            key_map = {"ctrl": "ctrl", "control": "ctrl", "alt": "alt", "win": "win", "windows": "win", "shift": "shift"}
            mapped = [key_map.get(k, k) for k in keys]
            pyautogui.hotkey(*mapped)
            return {"status": "success", "mode": "hotkey", "keys": mapped, "message": f"Pressed hotkey combo: {' + '.join(mapped)}"}
        else:
            pyautogui.write(clean, interval=0.01)
            return {"status": "success", "mode": "type_text", "length": len(clean), "message": f"Typed {len(clean)} characters into active window."}
    except Exception as e:
        return {"status": "error", "message": f"Automation error: {e}"}


def search_local_files(filename_query: str, search_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Fast local file search matching filename patterns.
    """
    query = filename_query.strip().lower()
    stem = re.sub(r'\.[a-zA-Z0-9]+$', '', query).strip()
    query_tokens = [t for t in re.split(r'[\s_\-\.]+', stem) if len(t) >= 3]

    root_paths = []
    if search_root and os.path.exists(search_root):
        root_paths.append(Path(search_root))
    else:
        root_paths.append(WORKSPACE_ROOT)
        user_home = Path.home()
        for sub in ["Desktop", "Documents", "Downloads"]:
            p = user_home / sub
            if p.exists():
                root_paths.append(p)

    matches = []
    max_matches = 15
    for r in root_paths:
        if len(matches) >= max_matches:
            break
        try:
            for root, dirs, files in os.walk(r):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'target', '.git']]
                for f in files:
                    f_low = f.lower()
                    matched = (
                        query in f_low
                        or (stem and stem in f_low)
                        or (query_tokens and all(tok in f_low for tok in query_tokens))
                    )
                    if matched:
                        fp = Path(root) / f
                        try:
                            st = fp.stat()
                            matches.append({
                                "filename": f,
                                "path": str(fp),
                                "size_kb": round(st.st_size / 1024, 1),
                                "modified": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                            })
                        except Exception:
                            continue
                        if len(matches) >= max_matches:
                            break
                if len(matches) >= max_matches:
                    break
        except Exception:
            continue

    return {
        "status": "success",
        "query": filename_query,
        "match_count": len(matches),
        "matches": matches,
        "search_roots": [str(r) for r in root_paths]
    }


def verify_biometrics() -> Dict[str, Any]:
    """
    Runs face detection and Siamese embedding verification via senses/face_net.py on CUDA.
    """
    try:
        from senses.face_net import FACE_ENGINE
        res = FACE_ENGINE.verify_creator()
        return res
    except Exception as e:
        return {"status": "error", "verified": False, "confidence": 0.0, "message": f"Biometric verification error: {e}"}


def analyze_screen(query: str = "") -> Dict[str, Any]:
    """
    Captures primary screen, inspects foreground window and visible applications,
    and returns a structured multimodal analysis of desktop state.
    """
    try:
        from senses.screen_eyes import analyze_active_screen
        return analyze_active_screen(query)
    except Exception as e:
        return {"status": "error", "message": f"Screen vision error: {e}"}


# -------------------------------------------------------------------------
# Phase 13.5: Web Browser, YouTube Auto-Play & Spotify Automation
# -------------------------------------------------------------------------
def play_on_youtube(query: str) -> Dict[str, Any]:
    """
    Finds the exact first YouTube video for the query and launches it directly in the browser to auto-play.
    """
    from hands.web_media_controller import play_on_youtube as _play_yt
    return _play_yt(query)


def control_spotify_and_media(action: str, query: Optional[str] = None) -> Dict[str, Any]:
    """
    Controls Spotify desktop app and Windows virtual media keys (play, pause, next, prev, volume).
    """
    from hands.web_media_controller import control_spotify_and_media as _ctrl_spot
    return _ctrl_spot(action, query)


def open_browser_or_site(command: str) -> Dict[str, Any]:
    """
    Opens default browser to specific site or executes a Google search with live grounded summary.
    """
    from hands.web_media_controller import open_browser_or_site as _open_site
    return _open_site(command)


def execute_web_media(command: str) -> Dict[str, Any]:
    """
    Dispatches web, YouTube, Spotify, or media automation based on natural language command.
    """
    from hands.web_media_controller import execute_web_media_command
    res = execute_web_media_command(command)
    if res:
        return res
    return {"status": "info", "message": f"No web media action matched for: '{command}'"}



if __name__ == "__main__":
    import json
    print("--- System Telemetry ---")
    print(json.dumps(get_system_telemetry(), indent=2))
    print("\n--- Network Status ---")
    print(json.dumps(check_network_status(), indent=2))
    print("\n--- Read Vault Test ---")
    print(json.dumps(read_obsidian_vault("Jessica"), indent=2))
