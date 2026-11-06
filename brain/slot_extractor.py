"""
Jessica Brain - Parameter & Slot Extractor
Extracts structured parameters from natural language user commands for Jessica's OS tools.
"""

import re
from typing import Dict, Any, Optional


def extract_parameters(intent: str, command: str) -> Dict[str, Any]:
    """
    Extracts structured slots/arguments given the predicted intent and raw command string.
    """
    cmd = command.strip()
    cmd_lower = cmd.lower()
    params: Dict[str, Any] = {}

    if intent == "open_application":
        # Known common applications
        apps = [
            "task manager", "taskmgr", "calculator", "calc", "notepad", "obsidian",
            "explorer", "file explorer", "command prompt", "terminal", "powershell",
            "cmd", "mspaint", "paint", "control panel", "control", "regedit",
            "brave", "chrome", "edge"
        ]
        target = "notepad"
        for app in apps:
            if app in cmd_lower:
                target = app
                break
        else:
            # Regex extraction: open/launch/start <app>
            m = re.search(r"(?:open|launch|start|run|bring up)\s+([a-zA-Z0-9_\-\.]+)", cmd_lower)
            if m:
                target = m.group(1).strip()
        params["app_name"] = target

    elif intent == "write_obsidian_note":
        # Determine folder
        folder = "03_Daily_Logs"
        if "01" in cmd or "sop" in cmd_lower or "procedure" in cmd_lower or "skill" in cmd_lower:
            folder = "01_Skills_SOPs"
        elif "02" in cmd or "knowledge" in cmd_lower or "kb" in cmd_lower or "concept" in cmd_lower:
            folder = "02_Knowledge_Base"
        elif "00" in cmd or "identity" in cmd_lower or "persona" in cmd_lower:
            folder = "00_Identity"

        # Determine title
        title = "Quick_Note"
        title_match = re.search(r"(?:titled|called|named)\s+['\"]?([^'\"\n]+)['\"]?", cmd, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            about_match = re.search(r"(?:about|regarding|on)\s+([^,\.\n]+)", cmd, re.IGNORECASE)
            if about_match:
                title = about_match.group(1).strip().replace(" ", "_")[:30]

        # Determine content
        content_match = re.search(r"(?:with content|saying|text:?)\s+['\"]?([^'\"\n]+)['\"]?", cmd, re.IGNORECASE)
        if content_match:
            content = content_match.group(1).strip()
        else:
            content = f"Logged from natural command: {cmd}\nRecorded by Jessica Brain v0.2."

        params["folder"] = folder
        params["title"] = title
        params["content"] = content

    elif intent == "read_obsidian_vault":
        query = ""
        # Remove trigger keywords
        m = re.search(r"(?:search|find|read|look up|query|check)\s+(?:in\s+obsidian|obsidian\s+vault|vault|notes\s+about|notes\s+on|about|for)?\s*(.+)", cmd_lower)
        if m:
            query = m.group(1).strip()
            # Clean filler phrases
        query = re.sub(r"(?:in\s+my\s+vault|in\s+obsidian|vault|notes?|please|for\s+me)", "", query).strip()
        if not query:
            query = "Jessica"
        params["query"] = query

    elif intent == "set_system_volume":
        vol = 50
        if "mute" in cmd_lower:
            vol = 0
        elif "max" in cmd_lower or "full" in cmd_lower:
            vol = 100
        else:
            nums = re.findall(r"\d+", cmd)
            if nums:
                vol = int(nums[0])
            elif "up" in cmd_lower:
                vol = 70
            elif "down" in cmd_lower:
                vol = 30
        params["level"] = max(0, min(100, vol))

    elif intent == "take_screenshot":
        filename_match = re.search(r"(?:as|named|filename)\s+['\"]?([a-zA-Z0-9_\-\.]+\.png)['\"]?", cmd, re.IGNORECASE)
        params["filename"] = filename_match.group(1).strip() if filename_match else None

    elif intent == "kill_process":
        target = ""
        # Match process name or PID
        pid_match = re.search(r"pid\s+(\d+)", cmd_lower)
        if pid_match:
            target = pid_match.group(1)
        else:
            m = re.search(r"(?:kill|terminate|stop|end task|close)\s+(?:process\s+|task\s+)?([a-zA-Z0-9_\-\.]+)", cmd_lower)
            if m:
                target = m.group(1).strip()
            else:
                target = "unknown"
        params["process_name_or_pid"] = target

    elif intent == "list_top_processes":
        params["limit"] = 10
        m = re.search(r"top\s+(\d+)", cmd_lower)
        if m:
            params["limit"] = int(m.group(1))

    elif intent == "learn_from_internet":
        # Extract topic from phrases like "research X from the internet", "learn about X", "study X on the web"
        m = re.search(r"(?:research|learn about|learn|study|look up|investigate|find out about)\s+(.+?)(?:\s+from\s+the\s+internet|\s+on\s+the\s+web|\s+online|\s+and\s+save|\s+to\s+obsidian|$)", cmd, re.IGNORECASE)
        if m:
            topic = m.group(1).strip()
        else:
            topic = cmd.replace("learn", "").replace("research", "").strip()
        topic = re.sub(r"(?:from the internet|on the web|and save to obsidian|to obsidian|in obsidian|online)", "", topic, flags=re.IGNORECASE).strip(" ,.!?")
        params["topic"] = topic if topic else "General Science"

    elif intent == "control_window":
        act = "minimize_all"
        if "minimize" in cmd_lower or "desktop" in cmd_lower:
            act = "minimize_all"
        elif "maximize" in cmd_lower:
            act = "maximize_active"
        elif "snap left" in cmd_lower or "left side" in cmd_lower:
            act = "snap_left"
        elif "snap right" in cmd_lower or "right side" in cmd_lower:
            act = "snap_right"
        elif "switch" in cmd_lower or "alt tab" in cmd_lower or "next window" in cmd_lower:
            act = "switch_window"
        elif "lock" in cmd_lower:
            act = "lock_workstation"
        params["action"] = act

    elif intent == "type_and_automate":
        # Check hotkey
        hotkey_match = re.search(r"(?:press|hit|hotkey|combo)\s+([a-zA-Z0-9_\+\-]+)", cmd_lower)
        if hotkey_match:
            params["text_or_hotkey"] = hotkey_match.group(1).strip()
        else:
            type_match = re.search(r"(?:type|write|input)\s+['\"]?(.+?)['\"]?$", cmd, re.IGNORECASE)
            if type_match:
                params["text_or_hotkey"] = type_match.group(1).strip()
            else:
                params["text_or_hotkey"] = "ctrl+c"

    elif intent == "search_local_files":
        # Match "search local files for X", "find file X", "locate X on disk", etc.
        m = re.search(r"(?:search|find|locate|look for)\s+(?:local\s+files\s+for|files\s+for|file\s+for|files?\s+|documents?\s+)?(?:named|called|matching|for)?\s*['\"]?([a-zA-Z0-9_\-\.\*]+)['\"]?", cmd, re.IGNORECASE)
        if m:
            extracted = m.group(1).strip()
            # If extracted ended up being "local" or "files", fall back to text after "for"
            if extracted in ["local", "files", "file"] and "for " in cmd_lower:
                extracted = cmd_lower.split("for ", 1)[1].strip(" '\"")
            query = extracted
        else:
            query = cmd.replace("search", "").replace("find", "").replace("local", "").replace("files", "").strip()
        params["filename_query"] = query if query else "log"

    elif intent == "verify_biometrics":
        params["action"] = "scan_face"

    elif intent == "analyze_screen":
        params["query"] = cmd

    return params


if __name__ == "__main__":
    test_cases = [
        ("open_application", "Launch task manager right now"),
        ("write_obsidian_note", "Write a note in 02_Knowledge_Base titled Memory Architecture with content Attention models in RAM"),
        ("read_obsidian_vault", "Search obsidian vault for telemetry rules"),
        ("set_system_volume", "Set master audio volume to 75%"),
        ("kill_process", "Kill process chrome.exe"),
        ("take_screenshot", "Take a screenshot named mission_control.png")
    ]
    for intent, cmd in test_cases:
        p = extract_parameters(intent, cmd)
        print(f"[{intent}] '{cmd}' -> {p}")
