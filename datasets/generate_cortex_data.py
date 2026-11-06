"""
Generates 650+ synthetic conversational and RAG training pairs for Jessica's Causal Cortex.
"""

import json
import random

pairs = []

# Template variations
conversational_intents = [
    ("Who are you?", "Local AI Sovereign Agent on Intel i5 and RTX 4060", "none",
     "I am Jessica, your sovereign local AI operating system and cognitive co-pilot running directly on your RTX 4060 hardware."),
    ("What are your core directives?", "Zero cloud reliance, 100% data privacy, deterministic execution", "none",
     "My core mandates are local sovereignty, zero reliance on external cloud APIs, deterministic OS execution, and persistent memory via Obsidian."),
    ("Tell me about your hardware.", "Intel Core i5 11th Gen, 32GB RAM, RTX 4060 8GB VRAM", "none",
     "I operate on an Intel Core i5 11th Gen processor, 32 GB of system RAM, and an NVIDIA GeForce RTX 4060 with 8 GB VRAM delivering 30 TFLOPS of FP16 Tensor Core acceleration."),
    ("Are you connected to any cloud AI service?", "100% local neural inference, air-gapped cognition", "none",
     "No. All cognition, vector search, intent routing, and action execution execute 100% locally on your machine with complete data privacy."),
    ("How does your memory work?", "Obsidian Vault with hybrid dense neural embeddings and sparse TF-IDF", "none",
     "My memory is grounded in your local Obsidian Vault, cross-referencing markdown notes using dense PyTorch embeddings and sparse TF-IDF scoring.")
]

telemetry_scenarios = [
    ("What is our current system load?", "RTX 4060 Telemetry Rules",
     "CPU: {cpu}% | RAM: {ram}GB/32GB | GPU: RTX 4060 {temp}C, VRAM: {vram}MiB",
     "System telemetry report: CPU utilization is at {cpu}%, system RAM is at {ram} GB, and your RTX 4060 is running at {temp}°C with {vram} MiB of VRAM allocated."),
    ("Check GPU thermals and memory.", "RTX 4060 Telemetry Rules",
     "GPU: RTX 4060 | Temp: {temp}C | VRAM Used: {vram}MiB / 8188MiB",
     "Your NVIDIA GeForce RTX 4060 is operating nominally at {temp}°C with {vram} MiB of VRAM in use. Thermals are well below the 75°C threshold."),
    ("How much RAM is currently allocated?", "Windows Administration",
     "RAM used: {ram} GB of 31.8 GB ({ram_pct}%)",
     "System RAM consumption is currently {ram} GB out of 32 GB total ({ram_pct}% utilization). Adequate memory headroom remains.")
]

network_scenarios = [
    ("Is the internet reachable?", "Network Diagnostics",
     "Local IP: {ip} | Gateway: 192.168.1.1 | Ping 1.1.1.1: {ping}ms | Status: Online",
     "Network connection is active and stable. Gateway is reachable and latency to Cloudflare 1.1.1.1 is {ping} ms."),
    ("Run network latency check.", "Network Diagnostics",
     "1.1.1.1 latency: {ping}ms | 8.8.8.8 latency: {ping2}ms",
     "Dual DNS latency diagnostic complete: 1.1.1.1 responded in {ping} ms and 8.8.8.8 responded in {ping2} ms. WAN link is responsive."),
    ("What is my local IP address?", "Network Diagnostics",
     "Local IP: {ip} on active adapter Ethernet",
     "Your active network adapter is assigned local IPv4 address {ip} with full gateway reachability.")
]

app_scenarios = [
    ("Open {app} for me.", "Windows Administration",
     "Successfully launched application: {app}",
     "I have launched {app} in your desktop environment."),
    ("Launch {app} right now.", "Windows Administration",
     "Process started: {app}.exe",
     "{app} is now running in your active workspace."),
    ("Start {app}.", "Windows Administration",
     "Application target initialized: {app}",
     "Executing launch directive for {app}. Window opened.")
]

vault_scenarios = [
    ("What are the thermal limits for the RTX 4060?", "RTX 4060 Telemetry Rules",
     "Nominal: 40-65C | Warning: 75C | Critical: 85C",
     "According to our knowledge base, the RTX 4060 thermal limits are: 40°C–65°C nominal, 75°C warning, and 85°C critical TJunction ceiling."),
    ("What is the protocol for process termination?", "SOP Process Termination",
     "CONFIRM_REQUIRED tier, safety check against system services, prompt user",
     "Process termination follows SOP-01: it is classified as CONFIRM_REQUIRED, verifies that critical OS services are never killed, and awaits explicit user authorization."),
    ("How do we triage network outages?", "SOP Network Outage Triage",
     "Check local NIC IP, ping default gateway, test DNS 1.1.1.1, flush DNS cache",
     "Per our network triage SOP, we first verify local adapter IP, test gateway reachability, probe external DNS 1.1.1.1, and flush DNS caches if hostname resolution fails.")
]

action_confirm_scenarios = [
    ("Kill process {proc}.", "SOP Process Termination",
     "Security Action: CONFIRM_REQUIRED for {proc}",
     "Terminating {proc} is classified as CONFIRM_REQUIRED. Please confirm authorization before I terminate the process tree: [APPROVE] / [DENY]."),
    ("Terminate {proc} immediately.", "Process Management & Security",
     "CONFIRM_REQUIRED trigger: {proc}",
     "Safety intercept: {proc} termination requires your explicit approval. Click [APPROVE] in Mission Control to proceed or [DENY] to abort.")
]

# Generate variations
apps_list = ["notepad", "calculator", "task manager", "cmd", "powershell", "obsidian", "explorer", "paint"]
procs_list = ["chrome.exe", "spotify.exe", "discord.exe", "steam.exe", "python_old.exe", "slack.exe"]

for _ in range(50):
    for u, c, a, j in conversational_intents:
        pairs.append({"user": u, "context": c, "action": a, "jessica": j})

for _ in range(25):
    for u_tpl, c, a_tpl, j_tpl in telemetry_scenarios:
        cpu = random.randint(3, 45)
        ram = round(random.uniform(9.0, 18.5), 1)
        ram_pct = int((ram / 32.0) * 100)
        temp = random.randint(42, 64)
        vram = random.randint(850, 2400)
        u = u_tpl.format(cpu=cpu, ram=ram, temp=temp, vram=vram)
        a = a_tpl.format(cpu=cpu, ram=ram, ram_pct=ram_pct, temp=temp, vram=vram)
        j = j_tpl.format(cpu=cpu, ram=ram, ram_pct=ram_pct, temp=temp, vram=vram)
        pairs.append({"user": u, "context": c, "action": a, "jessica": j})

for _ in range(25):
    for u_tpl, c, a_tpl, j_tpl in network_scenarios:
        ip = f"192.168.1.{random.randint(10, 150)}"
        ping = random.randint(11, 28)
        ping2 = ping + random.randint(2, 8)
        u = u_tpl.format(ip=ip, ping=ping, ping2=ping2)
        a = a_tpl.format(ip=ip, ping=ping, ping2=ping2)
        j = j_tpl.format(ip=ip, ping=ping, ping2=ping2)
        pairs.append({"user": u, "context": c, "action": a, "jessica": j})

for _ in range(15):
    for app in apps_list:
        for u_tpl, c, a_tpl, j_tpl in app_scenarios:
            u = u_tpl.format(app=app)
            a = a_tpl.format(app=app)
            j = j_tpl.format(app=app)
            pairs.append({"user": u, "context": c, "action": a, "jessica": j})

for _ in range(30):
    for u, c, a, j in vault_scenarios:
        pairs.append({"user": u, "context": c, "action": a, "jessica": j})

for _ in range(15):
    for proc in procs_list:
        for u_tpl, c, a_tpl, j_tpl in action_confirm_scenarios:
            u = u_tpl.format(proc=proc)
            a = a_tpl.format(proc=proc)
            j = j_tpl.format(proc=proc)
            pairs.append({"user": u, "context": c, "action": a, "jessica": j})

random.seed(42)
random.shuffle(pairs)

print(f"Total Cortex Training Pairs Generated: {len(pairs)}")

out_path = "datasets/cortex_train.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for item in pairs:
        # Formulate full training sequence
        text = f"<user> {item['user']} <context> {item['context']} <action> {item['action']} <jessica> {item['jessica']} <eos>"
        f.write(json.dumps({"text": text, **item}) + "\n")

print(f"[+] Successfully wrote {len(pairs)} records to {out_path}")

