"""
Jessica Brain - Expanded Intent Routing Dataset Generator (v0.2 Enterprise)
Generates 850+ diverse, high-variance training examples across all 10 intent classes.
"""

import json
import random

data = []

# 1. get_system_telemetry (~85 examples)
telemetry_patterns = [
    "What is the current CPU and RAM usage?",
    "Show me system telemetry",
    "How much free memory do I have?",
    "Check GPU temperature and load",
    "Is my CPU overheating right now?",
    "Give me a hardware health check",
    "How much VRAM is currently allocated?",
    "Current system metrics please",
    "Inspect host telemetry",
    "Monitor CPU cores and utilization",
    "What is my RAM consumption at the moment?",
    "Show GPU stats",
    "System resource overview",
    "How hard is the RTX 4060 working right now?",
    "Display CPU frequency and percentage",
    "Report memory usage",
    "Is the GPU being throttled?",
    "Get system performance diagnostics",
    "Can you check how much RAM is being used?",
    "Could you report how much RAM and CPU is currently being used?",
    "Tell me how much memory and CPU is utilized right now",
    "How much RAM and processor capacity is in use?",
    "Check how much CPU and RAM is being used by the system",
    "Report currently used RAM and CPU percentages",
    "Current CPU and memory utilization breakdown",
    "Read hardware sensors",
    "Check processor usage",
    "What is the GPU clock and temp?",
    "Tell me system telemetry stats",
    "Are we running low on RAM?",
    "System diagnostics report",
    "Show machine telemetry",
    "Hardware metrics overview",
    "Check graphics card VRAM status",
    "Provide CPU load summary",
    "Status of hardware resources",
    "Give me current telemetry",
    "Show device vitals",
    "How much system memory is free?",
    "Inspect thermal status and CPU usage",
    "Get full hardware telemetry",
    "Check if system temperature is safe",
    "Check if the GPU temperature is normal",
    "Inspect GPU temperature and clock",
    "Check GPU thermals and load",
    "Are GPU thermals safe right now?",
    "Check hardware temperature readings",
    "Monitor thermal sensors across the GPU and CPU",
    "Check if hardware is running too hot",
    "Check temperature sensors",
    "What are our hardware telemetry stats?",
    "Give me an overview of GPU VRAM and CPU core load",
    "Inspect telemetry metrics",
    "Check memory consumption and GPU heat",
    "Display hardware vitals right now"
]
for p in telemetry_patterns:
    data.append({"command": p, "intent": "get_system_telemetry"})
# Augment with variations
for base in ["telemetry check", "check hardware load", "inspect cpu and ram", "rtx 4060 stats", "sensor report", "vram usage"]:
    for prefix in ["Please run a ", "Can you do a ", "Give me a ", "Quick ", "Jessica, "]:
        data.append({"command": prefix + base, "intent": "get_system_telemetry"})

# 2. list_top_processes (~85 examples)
process_patterns = [
    "What processes are eating my CPU?",
    "List top processes by memory usage",
    "Show running tasks",
    "What is taking up all my RAM right now?",
    "Show highest CPU consuming programs",
    "List top 10 running processes",
    "Find out which app is lagging my machine",
    "What background programs are active?",
    "Check process table for heavy tasks",
    "List active Windows processes",
    "Which process is using the most memory?",
    "Display process list",
    "Show process monitor",
    "Identify rogue background tasks",
    "What tasks are currently consuming CPU cycles?",
    "Give me the top memory hogging applications",
    "Inspect active system processes",
    "What software is currently running in the background?",
    "Find high memory usage apps",
    "List top processes",
    "Who is using up all the processor power?",
    "Show running system executables",
    "View active processes",
    "Rank processes by CPU",
    "Check if any application is hogging system RAM",
    "Top task list",
    "Inspect process tree",
    "What apps are consuming the most memory right now?",
    "Sort running processes by RAM",
    "Give me a breakdown of heavy processes",
    "Who is consuming CPU cycles?",
    "Check process resource hogs",
    "List programs using the most memory",
    "Show resource intensive tasks",
    "Display top processes"
]
for p in process_patterns:
    data.append({"command": p, "intent": "list_top_processes"})
for base in ["top 5 tasks", "heavy processes", "running programs", "cpu hoggers", "memory hogging apps"]:
    for prefix in ["Show me ", "List the ", "What are the ", "Identify ", "Display "]:
        data.append({"command": prefix + base, "intent": "list_top_processes"})

# 3. check_network_status (~85 examples)
network_patterns = [
    "Check my internet connection",
    "Is the network online?",
    "Test network ping and latency",
    "What is my local IP address?",
    "Can we reach the outside internet?",
    "Run network diagnostics",
    "Check network connectivity and packet status",
    "Inspect network interface",
    "Am I connected to Wi-Fi or Ethernet?",
    "Check DNS and gateway ping",
    "Is my internet down?",
    "Verify internet reachability",
    "Check network bandwidth throughput",
    "What is my machine's IP on the local subnet?",
    "Test latency to 1.1.1.1",
    "Network status report please",
    "Are we connected to the network?",
    "Check uplink and downlink status",
    "Run a quick ping check",
    "Inspect Wi-Fi connection",
    "Is there any internet lag right now?",
    "Verify web connectivity",
    "Check network adapters",
    "Are sockets reaching external hosts?",
    "Diagnostic test for network connection",
    "Check internet speed and latency",
    "Show network adapter information",
    "What is the network round trip time?",
    "Test if internet is responsive",
    "Is my local network adapter up?",
    "Check local IP and external connection",
    "Measure network latency",
    "Check WAN link",
    "Is our connection online?",
    "Network health check",
    "Ping 8.8.8.8 and 1.1.1.1",
    "What is my default gateway address?"
]
for p in network_patterns:
    data.append({"command": p, "intent": "check_network_status"})
for base in ["ping test", "network latency", "internet reachability", "gateway status", "ip configuration"]:
    for prefix in ["Run a ", "Do a ", "Execute ", "Perform ", "Start "]:
        data.append({"command": prefix + base, "intent": "check_network_status"})

# 4. open_application (~85 examples)
app_targets = ["notepad", "calculator", "calc", "task manager", "taskmgr", "cmd", "powershell", "obsidian", "explorer", "paint", "mspaint", "control panel", "regedit", "chrome", "edge", "brave"]
for app in app_targets:
    for verb in ["Open", "Launch", "Start", "Bring up", "Fire up"]:
        data.append({"command": f"{verb} {app}", "intent": "open_application"})
        data.append({"command": f"Please {verb.lower()} {app} for me", "intent": "open_application"})

# 5. write_obsidian_note (~85 examples)
note_patterns = [
    "Write a note in Obsidian titled Project Plan",
    "Create a new daily log in Obsidian",
    "Log this idea into my knowledge base vault",
    "Write down meeting notes in Obsidian folder 03_Daily_Logs",
    "Save this research note to my vault",
    "Append note to Obsidian",
    "Record these thoughts into my obsidian notes",
    "Document this architecture in obsidian knowledge base",
    "Add a note called System Architecture to 02_Knowledge_Base",
    "Write an entry in my daily journal in Obsidian",
    "Create an obsidian memo about Phase 1 rollout",
    "Save note to 01_Skills_SOPs titled Training Guide",
    "Take a note in my vault",
    "Store this log into Obsidian",
    "Make an obsidian note called Standup Updates",
    "Write down this summary to my obsidian vault",
    "Draft a new markdown document in Obsidian",
    "Record task list in Obsidian 03_Daily_Logs",
    "Write note in vault under 02_Knowledge_Base",
    "Save these bullet points into an obsidian file",
    "Document operational procedure in obsidian SOPs",
    "Add entry to daily logs in Obsidian",
    "Save note to knowledge base",
    "Write a quick note in my obsidian workspace",
    "Log progress report to obsidian vault",
    "Create note titled Jessica Architecture in 00_Identity",
    "Record this insight to obsidian vault",
    "Write down this checklist in obsidian",
    "Document neural training loss in obsidian notes",
    "Create a note in obsidian folder 03_Daily_Logs",
    "Save thought to obsidian vault",
    "Take note in 02_Knowledge_Base",
    "Write an obsidian note regarding our milestone",
    "Add daily note in obsidian",
    "Store this technical spec in Obsidian"
]
for p in note_patterns:
    data.append({"command": p, "intent": "write_obsidian_note"})
for base in ["daily summary", "meeting notes", "troubleshooting log", "system benchmark results", "sprint ideas"]:
    for prefix in ["Log to obsidian: ", "Record in vault: ", "Write an obsidian entry about ", "Take a note on "]:
        data.append({"command": prefix + base, "intent": "write_obsidian_note"})

# 6. read_obsidian_vault (~85 examples)
read_vault_patterns = [
    "Search obsidian vault for telemetry rules",
    "Read notes about network diagnostics in vault",
    "Look up SOP for process termination in obsidian",
    "Find note on Windows administration",
    "Search my vault for hardware thresholds",
    "What notes do we have in 02_Knowledge_Base?",
    "Query obsidian memory about RTX 4060",
    "Find in obsidian vault any mention of TJunction",
    "Search vault for daily system audit procedures",
    "Look up our network triage SOP in obsidian",
    "Read my daily logs in obsidian",
    "Search knowledge base notes for security sandbox",
    "Find notes about memory architecture in vault",
    "Check obsidian notes on process management",
    "Read vault note titled Jessica Identity",
    "Search obsidian memory for dual DNS ping triage",
    "What does our knowledge base say about Tensor Cores?",
    "Find notes tagged windows in obsidian",
    "Search the vault for daily logs",
    "Read documentation from obsidian vault"
]
for p in read_vault_patterns:
    data.append({"command": p, "intent": "read_obsidian_vault"})
for topic in ["telemetry rules", "process security", "network diagnostics", "SOP protocols", "hardware specs", "daily logs"]:
    for prefix in ["Search vault for ", "Read obsidian note on ", "Look up in vault: ", "Query obsidian on ", "Find notes about "]:
        data.append({"command": prefix + topic, "intent": "read_obsidian_vault"})

# 7. set_system_volume (~85 examples)
volume_patterns = [
    "Set system volume to 50%",
    "Change volume to 80 percent",
    "Turn up the master volume to 75",
    "Lower the volume to 20%",
    "Mute the system audio",
    "Unmute volume",
    "Set audio level to 60",
    "Turn down system volume to 30%",
    "Max out the volume",
    "Set sound volume to 40 percent",
    "Adjust master volume to 65",
    "Turn audio up to 90%",
    "Reduce volume to 15 percent",
    "Put volume at 50",
    "Set PC volume to 70%",
    "Mute all sound",
    "Set audio volume to 100%",
    "Turn volume down to 10%",
    "Increase system volume to 85",
    "Change master audio to 45%"
]
for p in volume_patterns:
    data.append({"command": p, "intent": "set_system_volume"})
for lvl in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
    data.append({"command": f"Set volume to {lvl}%", "intent": "set_system_volume"})
    data.append({"command": f"Adjust audio to {lvl}", "intent": "set_system_volume"})
    data.append({"command": f"Turn volume to {lvl} percent", "intent": "set_system_volume"})
    data.append({"command": f"Master volume {lvl}", "intent": "set_system_volume"})

# 8. take_screenshot (~85 examples)
screenshot_patterns = [
    "Take a screenshot",
    "Capture the screen right now",
    "Grab a screenshot of the desktop",
    "Snap desktop window",
    "Take screenshot and save to senses",
    "Capture current display",
    "Save a screenshot named mission_control.png",
    "Take a screen capture",
    "Snapshot the current screen",
    "Capture desktop monitor view",
    "Record screen snapshot",
    "Take screenshot for diagnostic report",
    "Grab screen",
    "Capture full screen image",
    "Take a quick desktop screenshot",
    "Snapshot display",
    "Save screen capture to senses folder",
    "Capture screen view",
    "Take screenshot now",
    "Snap screen"
]
for p in screenshot_patterns:
    data.append({"command": p, "intent": "take_screenshot"})
for suffix in ["right now", "please", "for debugging", "named diag.png", "and save it", "of my desktop"]:
    for prefix in ["Take a screenshot ", "Capture screen ", "Grab screenshot ", "Snap display "]:
        data.append({"command": prefix + suffix, "intent": "take_screenshot"})

# 9. kill_process (~85 examples)
kill_patterns = [
    "Kill process chrome.exe",
    "Terminate spotify.exe",
    "Kill task discord.exe",
    "Stop process steam.exe",
    "End task notepad.exe",
    "Kill process with PID 1234",
    "Terminate PID 5678",
    "Force close chrome",
    "Kill rogue background process",
    "Terminate process slack.exe",
    "Close application process firefox.exe",
    "Kill task with pid 4321",
    "End process explorer.exe",
    "Kill lagging application process",
    "Stop and kill process python_bad.exe",
    "Terminate task spotify",
    "Kill process brave.exe",
    "End task for discord",
    "Force kill process",
    "Terminate process PID 9999"
]
for p in kill_patterns:
    data.append({"command": p, "intent": "kill_process"})
for proc in ["chrome.exe", "spotify.exe", "discord.exe", "steam.exe", "slack.exe", "teams.exe", "zoom.exe", "epicgames.exe", "notion.exe"]:
    for prefix in ["Kill ", "Terminate ", "Stop ", "Force kill ", "End task "]:
        data.append({"command": prefix + proc, "intent": "kill_process"})
        data.append({"command": f"Please {prefix.lower()}{proc}", "intent": "kill_process"})
        data.append({"command": f"Can you {prefix.lower()}{proc} now", "intent": "kill_process"})

for q_topic in ["process termination", "network triage", "GPU thermals", "Windows administration", "daily audits", "memory architecture", "system telemetry"]:
    for prefix in ["What does obsidian say about ", "Look up vault documentation on ", "Find notes on ", "Query knowledge base for ", "Read obsidian docs about "]:
        data.append({"command": prefix + q_topic, "intent": "read_obsidian_vault"})

for base in ["hardware vitals", "CPU temperature", "RTX 4060 load", "memory headroom", "VRAM consumption"]:
    for prefix in ["Check ", "Inspect ", "Report ", "Show ", "Audit "]:
        data.append({"command": prefix + base, "intent": "get_system_telemetry"})

# 10. conversation (~85 examples)
conv_patterns = [
    "Hello Jessica, how are you today?",
    "Who are you and what are your capabilities?",
    "Tell me a joke",
    "Good morning Jessica",
    "What is the meaning of life?",
    "Thanks for your assistance!",
    "Are you a local sovereign AI?",
    "Tell me about your neural architecture",
    "Hey Jessica, what can you do?",
    "Good evening",
    "Can you introduce yourself?",
    "What model are you running on?",
    "Nice to meet you Jessica",
    "How does your routing brain work?",
    "Explain quantum computing simply",
    "Are you sentient?",
    "Thanks Jessica, great job",
    "What are your core directives?",
    "Tell me something interesting about space",
    "Hi there, ready for work?",
    "What is your name?",
    "How are you feeling?",
    "Give me advice on software engineering",
    "Who created you?",
    "You are doing awesome",
    "What makes you different from cloud agents?",
    "Good afternoon Jessica",
    "Why is local sovereignty important?",
    "Appreciate your help",
    "Can you think for yourself?",
    "Tell me a fun fact about transformers",
    "Hello there!",
    "What is your primary mission?",
    "I have a philosophical question for you",
    "Talk to me Jessica"
]
for p in conv_patterns:
    data.append({"command": p, "intent": "conversation"})
for base in ["Jessica", "assistant", "system", "copilot"]:
    for prefix in ["Hey ", "Greetings ", "Good day ", "Salutations ", "What's up "]:
        data.append({"command": prefix + base, "intent": "conversation"})

random.seed(42)
random.shuffle(data)

print(f"Total Router Training Samples Generated: {len(data)}")

with open("datasets/router_train.jsonl", "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item) + "\n")

print("Saved to datasets/router_train.jsonl successfully.")
