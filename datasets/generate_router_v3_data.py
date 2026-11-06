"""
Jessica Brain - Expanded Intent Routing Dataset Generator (v0.3 - Phase 4)
Generates 1,500+ diverse training examples across all 15 intent classes.
"""

import json
import random
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# 15 Intent Classes
INTENT_CLASSES = [
    "get_system_telemetry",
    "list_top_processes",
    "check_network_status",
    "open_application",
    "write_obsidian_note",
    "read_obsidian_vault",
    "set_system_volume",
    "take_screenshot",
    "kill_process",
    "conversation",
    "learn_from_internet",
    "control_window",
    "type_and_automate",
    "search_local_files",
    "verify_biometrics"
]

data = []

def add_samples(intent: str, patterns: list, variations: list = None):
    for p in patterns:
        data.append({"command": p, "intent": intent})
        if variations:
            for v in variations:
                data.append({"command": v.format(p=p), "intent": intent})

# 1. get_system_telemetry (~105 samples)
telemetry_bases = [
    "What is the current CPU and RAM usage?", "Show me system telemetry", "How much free memory do I have?",
    "Check GPU temperature and load", "Is my CPU overheating right now?", "Give me a hardware health check",
    "How much VRAM is currently allocated?", "Current system metrics please", "Inspect host telemetry",
    "Monitor CPU cores and utilization", "What is my RAM consumption at the moment?", "Show GPU stats",
    "System resource overview", "How hard is the RTX 4060 working right now?", "Display CPU frequency and percentage",
    "Report memory usage", "Is the GPU being throttled?", "Get system performance diagnostics",
    "Can you check how much RAM is being used?", "Could you report how much RAM and CPU is currently being used?",
    "Tell me how much memory and CPU is utilized right now", "How much RAM and processor capacity is in use?",
    "Check how much CPU and RAM is being used by the system", "Report currently used RAM and CPU percentages",
    "Check my RTX 4060 telemetry", "Check my GPU telemetry", "GPU status check", "Show machine telemetry",
    "Hardware metrics overview", "Check graphics card VRAM status", "Provide CPU load summary",
    "Status of hardware resources", "Give me current telemetry", "Show device vitals", "How much system memory is free?",
    "Inspect thermal status and CPU usage", "Get full hardware telemetry", "Check if system temperature is safe",
    "Check if the GPU temperature is normal", "Inspect GPU temperature and clock", "Check GPU thermals and load"
]
prefixes = ["Jessica, {p}", "Hey Jessica, {p}", "Please {p}", "Could you {p}?", "Quickly {p}"]
for b in telemetry_bases:
    data.append({"command": b, "intent": "get_system_telemetry"})
    data.append({"command": f"Jessica, {b.lower()}", "intent": "get_system_telemetry"})
    data.append({"command": f"Hey Jessica, {b.lower()}", "intent": "get_system_telemetry"})

# 2. list_top_processes (~105 samples)
proc_bases = [
    "What processes are eating the most CPU?", "List top active tasks", "Show high memory consumers",
    "Which apps are slowing down my machine?", "Display top 10 processes by CPU", "List top processes",
    "Find resource-heavy background processes", "Show process activity monitor", "Who is hogging all the RAM?",
    "List top 5 processes", "What is taking up so much memory?", "Show top processes running right now",
    "Display current task list", "Show memory-heavy tasks", "List background tasks", "Inspect heavy processes",
    "Top process breakdown", "Show me the top 8 processes by RAM usage", "Which applications are using CPU?",
    "Display active processes on host", "List top running applications", "Inspect running tasks"
]
for b in proc_bases:
    data.append({"command": b, "intent": "list_top_processes"})
    data.append({"command": f"Jessica, {b.lower()}", "intent": "list_top_processes"})
    data.append({"command": f"Hey, {b.lower()}", "intent": "list_top_processes"})
    data.append({"command": f"Can you {b.lower()}", "intent": "list_top_processes"})
    data.append({"command": f"Please {b.lower()}", "intent": "list_top_processes"})

# 3. check_network_status (~105 samples)
net_bases = [
    "Is my internet connection online?", "Check network status", "Test ping to 8.8.8.8", "What is my local IP address?",
    "Inspect active network adapters", "Verify connectivity to the default gateway", "Am I connected to the internet?",
    "Check network latency", "Ping test to Google DNS", "Report my network interfaces and IP", "Run a network health check",
    "Check if Wi-Fi or Ethernet is active", "What is my gateway IP?", "Measure network ping latency",
    "Check internet reachability", "Network diagnostic test", "Show network details", "Inspect network connectivity",
    "Is my connection active?", "Verify internet access", "Check network interfaces", "Network status report"
]
for b in net_bases:
    data.append({"command": b, "intent": "check_network_status"})
    data.append({"command": f"Jessica, {b.lower()}", "intent": "check_network_status"})
    data.append({"command": f"Hey Jessica, {b.lower()}", "intent": "check_network_status"})
    data.append({"command": f"Please {b.lower()}", "intent": "check_network_status"})
    data.append({"command": f"Could you {b.lower()}", "intent": "check_network_status"})

# 4. open_application (~105 samples)
apps = ["notepad", "task manager", "calculator", "obsidian", "cmd", "powershell", "paint", "explorer", "chrome", "edge", "terminal"]
for app in apps:
    data.append({"command": f"Open {app}", "intent": "open_application"})
    data.append({"command": f"Launch {app} for me", "intent": "open_application"})
    data.append({"command": f"Start {app} right now", "intent": "open_application"})
    data.append({"command": f"Bring up {app}", "intent": "open_application"})
    data.append({"command": f"Run {app}", "intent": "open_application"})
    data.append({"command": f"Jessica, open {app}", "intent": "open_application"})
    data.append({"command": f"Hey Jessica, launch {app}", "intent": "open_application"})
    data.append({"command": f"Can you start {app}?", "intent": "open_application"})
    data.append({"command": f"Please open {app}", "intent": "open_application"})
    data.append({"command": f"Open the {app} application", "intent": "open_application"})

# 5. write_obsidian_note (~105 samples)
write_notes = [
    "Write an Obsidian note in 03_Daily_Logs titled Daily Standup",
    "Create a new note titled Project Roadmap with content Phase 4 deployment",
    "Log a note titled System Diagnostics into 03_Daily_Logs",
    "Write a note in 01_Skills_SOPs titled Windows Tuning",
    "Record a note about Memory Optimizations into 02_Knowledge_Base",
    "Add a note called Neural Router Architecture to 02_Knowledge_Base",
    "Write a quick note in daily logs saying completed GPU training",
    "Save a note in Obsidian titled Evening Review",
    "Create an Obsidian log note titled Telemetry Audit",
    "Draft a new note in 01_Skills_SOPs titled Emergency Recovery SOP",
    "Write a note titled Benchmarks into 03_Daily_Logs"
]
for n in write_notes:
    data.append({"command": n, "intent": "write_obsidian_note"})
    data.append({"command": f"Jessica, {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Hey Jessica, {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Please {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Can you {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Quickly {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"In obsidian, {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Save note: {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Log to obsidian: {n.lower()}", "intent": "write_obsidian_note"})
    data.append({"command": f"Record to vault: {n.lower()}", "intent": "write_obsidian_note"})

# 6. read_obsidian_vault (~105 samples)
read_notes = [
    "Search Obsidian vault for telemetry rules", "Read the note about Jessica identity",
    "Find SOP Hardware Overheat Protocol in Obsidian", "Query my second brain for network diagnostics",
    "Search vault notes for GPU thermal thresholds", "What does Obsidian say about Windows administration?",
    "Retrieve notes on neural router architecture", "Look up identity guidelines in my vault",
    "Search Obsidian for daily logs", "Find notes regarding hardware maintenance", "Search vault for telemetry",
    "Look up thermal limits in Obsidian vault", "Read my obsidian notes on system performance",
    "Search my second brain for SOP", "Query obsidian notes about memory management"
]
for r in read_notes:
    data.append({"command": r, "intent": "read_obsidian_vault"})
    data.append({"command": f"Jessica, {r.lower()}", "intent": "read_obsidian_vault"})
    data.append({"command": f"Hey Jessica, {r.lower()}", "intent": "read_obsidian_vault"})
    data.append({"command": f"Please {r.lower()}", "intent": "read_obsidian_vault"})
    data.append({"command": f"Can you {r.lower()}", "intent": "read_obsidian_vault"})
    data.append({"command": f"Search vault: {r.lower()}", "intent": "read_obsidian_vault"})
    data.append({"command": f"Find in vault: {r.lower()}", "intent": "read_obsidian_vault"})

# 7. set_system_volume (~105 samples)
vol_bases = [
    "Set system volume to 50%", "Mute system audio", "Turn the volume up", "Set volume to 80 percent",
    "Lower the volume to 25%", "Max out the system volume", "Unmute audio", "Adjust volume to 40",
    "Change volume to 60%", "Turn sound down", "Set audio volume to 75%", "Volume up please", "Volume down please",
    "Make it quieter", "Set master volume to 30%", "Mute speaker", "Set sound to 100 percent"
]
for v in vol_bases:
    data.append({"command": v, "intent": "set_system_volume"})
    data.append({"command": f"Jessica, {v.lower()}", "intent": "set_system_volume"})
    data.append({"command": f"Hey Jessica, {v.lower()}", "intent": "set_system_volume"})
    data.append({"command": f"Please {v.lower()}", "intent": "set_system_volume"})
    data.append({"command": f"Can you {v.lower()}", "intent": "set_system_volume"})
    data.append({"command": f"Could you {v.lower()}", "intent": "set_system_volume"})
    data.append({"command": f"Quickly {v.lower()}", "intent": "set_system_volume"})

# 8. take_screenshot (~105 samples)
shot_bases = [
    "Take a screenshot", "Capture the screen right now", "Take a snapshot of my desktop",
    "Capture screenshot named mission_control.png", "Save a screen capture to senses",
    "Take screenshot of current window", "Snap the screen", "Grab a desktop screenshot",
    "Screen capture please", "Take a screenshot named display_test.png", "Record a screenshot of my desktop"
]
for s in shot_bases:
    data.append({"command": s, "intent": "take_screenshot"})
    data.append({"command": f"Jessica, {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Hey Jessica, {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Please {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Can you {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Could you {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Quickly {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Take screenshot: {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Capture display: {s.lower()}", "intent": "take_screenshot"})
    data.append({"command": f"Snap desktop: {s.lower()}", "intent": "take_screenshot"})

# 9. kill_process (~105 samples)
kill_targets = ["chrome.exe", "notepad.exe", "calc.exe", "discord.exe", "spotify.exe", "steam.exe", "python.exe", "PID 1234", "PID 9999", "edge.exe"]
for t in kill_targets:
    data.append({"command": f"Kill process {t}", "intent": "kill_process"})
    data.append({"command": f"Terminate {t} right now", "intent": "kill_process"})
    data.append({"command": f"End task {t}", "intent": "kill_process"})
    data.append({"command": f"Stop running process {t}", "intent": "kill_process"})
    data.append({"command": f"Close process {t}", "intent": "kill_process"})
    data.append({"command": f"Jessica, kill {t}", "intent": "kill_process"})
    data.append({"command": f"Hey Jessica, terminate {t}", "intent": "kill_process"})
    data.append({"command": f"Please end task {t}", "intent": "kill_process"})
    data.append({"command": f"Force kill {t}", "intent": "kill_process"})
    data.append({"command": f"Abort process {t}", "intent": "kill_process"})
    data.append({"command": f"Kill the task for {t}", "intent": "kill_process"})

# 10. conversation (~350 samples + Hard Negative Routing & Technical Explanations)
conv_bases = [
    "Hi", "Hello", "Hey there", "Good morning", "Good evening", "Who are you?", "Tell me who you are",
    "Who created you?", "Who are you and who created you?", "How can you help me?", "What can you do for me Jessica?",
    "How are you feeling today?", "How do you feel?", "Are you awake?", "What is your purpose?", "Tell me a joke",
    "What are your core capabilities?", "Nice to meet you", "Thank you Jessica", "Thanks for your help",
    "Are you sentient?", "Who made you?", "Identify yourself", "What can you do?", "What is your name?",
    "Tell me about yourself", "Are all systems nominal?", "Hello Jessica", "Hey Jessica how are you?", "Greetings",
    "Where do you live?", "How smart are you now?", "Can we just chat for a bit?", "Tell me something interesting",
    "I'm building you from scratch, what do you think?", "Good night Jessica", "How are you feeling right now?",
    "What should I do to relax tonight?", "My favorite instrument to play is a 4-string Jcraft Jazz bass guitar.",
    "What instrument did I just tell you I play, and why is it cool?", "Do you remember what we talked about?"
]

# Hard negative technical explanations that mention "routing", "window", "process", or "protocol"
# These MUST route to conversation/explanation, NOT to control_window or kill_process!
hard_negative_explanations = [
    "Explain how the BGP routing protocol works",
    "Explain how BGP routing functions on the internet",
    "What is the BGP routing protocol and how does it work?",
    "How does BGP routing exchange routes between autonomous systems?",
    "Can you explain the border gateway protocol routing algorithm?",
    "Tell me about BGP routing protocol attributes and path selection",
    "Why is BGP routing important for the global internet?",
    "How does packet routing work in computer networks?",
    "Explain OSPF versus BGP routing protocols",
    "What is dynamic routing in computer networking?",
    "How do routers build their routing tables?",
    "Explain how network packets are routed across the internet",
    "What is a network window size in TCP?",
    "Explain how the TCP sliding window protocol works",
    "What is a congestion window in transport layer protocols?",
    "How does the sliding window flow control mechanism operate?",
    "Explain window management algorithms in computer graphics and OS theory",
    "What is a time window in stream processing?",
    "How do Windows processes work under the hood?",
    "What is a process control block in operating system design?",
    "Explain how CPU scheduling coordinates concurrent processes",
    "What is the difference between a process and a thread in Windows?",
    "How does the OS scheduler allocate time slices to running processes?",
    "Why do operating systems isolate process memory spaces?",
    "Explain inter-process communication mechanisms in modern operating systems"
]

for c in conv_bases:
    data.append({"command": c, "intent": "conversation"})
    data.append({"command": f"Jessica, {c.lower()}", "intent": "conversation"})
    data.append({"command": f"Hey Jessica, {c.lower()}", "intent": "conversation"})
    data.append({"command": f"Well {c.lower()}", "intent": "conversation"})
    data.append({"command": f"So {c.lower()}", "intent": "conversation"})

for h in hard_negative_explanations:
    data.append({"command": h, "intent": "conversation"})
    data.append({"command": f"Jessica, {h.lower()}", "intent": "conversation"})
    data.append({"command": f"Hey Jessica, {h.lower()}", "intent": "conversation"})
    data.append({"command": f"Can you {h.lower()}", "intent": "conversation"})
    data.append({"command": f"Please {h.lower()}", "intent": "conversation"})

# 11. learn_from_internet (~110 samples)
learn_topics = [
    "Quantum Computing", "General Relativity", "CRISPR Gene Editing", "Neural Network Pruning",
    "Transformer Attention Mechanisms", "Nuclear Fusion Energy", "Superconductivity", "Distributed Consensus",
    "Black Holes", "Dark Matter", "Graphene Nanotechnology", "Epigenetics", "WebAssembly", "Rust Memory Safety"
]
for top in learn_topics:
    data.append({"command": f"Jessica, research {top} from the internet and save it to Obsidian", "intent": "learn_from_internet"})
    data.append({"command": f"Research {top} from the internet", "intent": "learn_from_internet"})
    data.append({"command": f"Learn about {top} on the web", "intent": "learn_from_internet"})
    data.append({"command": f"Study {top} and write to Obsidian", "intent": "learn_from_internet"})
    data.append({"command": f"Look up {top} online and store in knowledge base", "intent": "learn_from_internet"})
    data.append({"command": f"Search the internet for {top} and summarize into vault", "intent": "learn_from_internet"})
    data.append({"command": f"Investigate {top} online", "intent": "learn_from_internet"})
    data.append({"command": f"Find out about {top} from the web and save to my second brain", "intent": "learn_from_internet"})

# 12. control_window (~110 samples)
window_cmds = [
    "Minimize all windows", "Show desktop", "Minimize everything", "Maximize active window",
    "Maximize the current application", "Snap window to the left", "Snap window to the right",
    "Snap to left side", "Snap to right side", "Switch to the previous window", "Alt tab to next window",
    "Switch active window", "Lock my workstation right now", "Lock computer", "Lock the PC",
    "Minimize all open applications", "Toggle desktop view", "Expand window to full screen", "Snap active app left",
    "Snap current window right", "Cycle active application", "Lock the screen"
]
for w in window_cmds:
    data.append({"command": w, "intent": "control_window"})
    data.append({"command": f"Jessica, {w.lower()}", "intent": "control_window"})
    data.append({"command": f"Hey Jessica, {w.lower()}", "intent": "control_window"})
    data.append({"command": f"Please {w.lower()}", "intent": "control_window"})
    data.append({"command": f"Can you {w.lower()}", "intent": "control_window"})

# 13. type_and_automate (~110 samples)
type_cmds = [
    "Press ctrl+c", "Press ctrl+v", "Hit alt+tab", "Press win+d", "Hit enter key",
    "Simulate keyboard shortcut ctrl+s", "Type Hello World into the active window",
    "Type Jessica is online", "Press ctrl+z", "Hit spacebar", "Press escape key",
    "Automate keyboard press ctrl+a", "Type python script into editor", "Press hotkey ctrl+shift+esc",
    "Type sovereign intelligence", "Hit backspace", "Press hotkey win+r", "Type notepad into run prompt",
    "Input text System verified", "Simulate typing current status into window", "Press media play pause"
]
for t in type_cmds:
    data.append({"command": t, "intent": "type_and_automate"})
    data.append({"command": f"Jessica, {t.lower()}", "intent": "type_and_automate"})
    data.append({"command": f"Hey Jessica, {t.lower()}", "intent": "type_and_automate"})
    data.append({"command": f"Please {t.lower()}", "intent": "type_and_automate"})
    data.append({"command": f"Can you {t.lower()}", "intent": "type_and_automate"})

# 14. search_local_files (~110 samples)
file_cmds = [
    "Search local files for test_voice.py", "Find file matching jessica_golden", "Locate router_v2.pt on my drive",
    "Search for document named roadmap.md", "Find all files matching telemetry", "Look for file named vault_indexer",
    "Locate screenshot in my documents", "Search PC for file config.json", "Find file error.log on disk",
    "Where is the file jessica_server.py?", "Search my drive for model weights", "Locate python file main.py",
    "Find files containing dataset in filename", "Search local directories for audio files", "Locate text file readme.md",
    "Find document titled notes.txt", "Search files for backup", "Locate presentation slide.pptx", "Find spreadsheet data.xlsx"
]
for f in file_cmds:
    data.append({"command": f, "intent": "search_local_files"})
    data.append({"command": f"Jessica, {f.lower()}", "intent": "search_local_files"})
    data.append({"command": f"Hey Jessica, {f.lower()}", "intent": "search_local_files"})
    data.append({"command": f"Please {f.lower()}", "intent": "search_local_files"})
    data.append({"command": f"Can you {f.lower()}", "intent": "search_local_files"})
    data.append({"command": f"Search disk: {f.lower()}", "intent": "search_local_files"})

# 15. verify_biometrics (~110 samples)
bio_cmds = [
    "Scan my face with webcam", "Verify my biometrics", "Authenticate user via face ID",
    "Check facial recognition", "Look at the webcam and verify creator", "Run biometric scan",
    "Scan face to unlock authority", "Verify creator face ID", "Check if I am authorized using webcam",
    "Perform biometric verification", "Face ID scan please", "Recognize creator through camera",
    "Scan user face", "Authenticate using Siamese face net", "Verify biometric authority",
    "Check my face against enrolled embedding", "Scan webcam for creator", "Unlock permissions via face scan"
]
for b in bio_cmds:
    data.append({"command": b, "intent": "verify_biometrics"})
    data.append({"command": f"Jessica, {b.lower()}", "intent": "verify_biometrics"})
    data.append({"command": f"Hey Jessica, {b.lower()}", "intent": "verify_biometrics"})
    data.append({"command": f"Please {b.lower()}", "intent": "verify_biometrics"})
    data.append({"command": f"Can you {b.lower()}", "intent": "verify_biometrics"})

random.seed(42)
random.shuffle(data)

save_path = WORKSPACE_ROOT / "datasets" / "router_train.jsonl"
with open(save_path, "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item) + "\n")

print(f"[+] Successfully generated {len(data)} router training samples across all {len(INTENT_CLASSES)} intent classes!")
print(f"[+] Saved to: {save_path.resolve()}")

