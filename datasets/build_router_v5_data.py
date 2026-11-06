"""
Jessica Brain - Router v5 Hardening Dataset Generator (Wave 4)
Generates 3,000+ robust training examples across all 16 intent classes,
including 500+ adversarial false-friend technical explanations that map to 'conversation'.
"""

import json
import random
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = WORKSPACE_ROOT / "datasets" / "router_train.jsonl"

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
    "verify_biometrics",
    "analyze_screen"
]

all_data = []

def add_variations(intent, bases, prefixes=None, suffixes=None):
    if prefixes is None:
        prefixes = ["", "Jessica, ", "Hey Jessica, ", "Please ", "Can you ", "Could you ", "Quickly ", "Go ahead and "]
    if suffixes is None:
        suffixes = ["", " please", " right now", " for me", " thanks"]

    for b in bases:
        for p in prefixes:
            for s in suffixes:
                cmd = f"{p}{b}{s}".strip()
                if cmd:
                    all_data.append({"command": cmd, "intent": intent})

# =========================================================================
# 1. get_system_telemetry (Hardware Vitals, CPU/GPU, VRAM, RAM, Thermals)
# =========================================================================
telemetry_bases = [
    "check system telemetry", "what is the current CPU and RAM usage", "show me system telemetry",
    "how much free memory do I have", "check GPU temperature and load", "is my CPU overheating right now",
    "give me a hardware health check", "how much VRAM is currently allocated", "current system metrics please",
    "inspect host telemetry", "monitor CPU cores and utilization", "what is my RAM consumption at the moment",
    "show GPU stats", "system resource overview", "how hard is the RTX 4060 working right now",
    "display CPU frequency and percentage", "report memory usage", "is the GPU being throttled",
    "get system performance diagnostics", "tell me how much memory and CPU is utilized right now",
    "check how much CPU and RAM is being used by the system", "report currently used RAM and CPU percentages",
    "check my RTX 4060 telemetry", "check my GPU telemetry", "GPU status check", "show machine telemetry",
    "hardware metrics overview", "check graphics card VRAM status", "provide CPU load summary",
    "status of hardware resources", "give me current telemetry", "show device vitals",
    "how much system memory is free", "inspect thermal status and CPU usage", "get full hardware telemetry",
    "check if system temperature is safe", "check if the GPU temperature is normal", "inspect GPU temperature and clock"
]
add_variations("get_system_telemetry", telemetry_bases)

# =========================================================================
# 2. list_top_processes (Process breakdown, RAM hogs, active tasks)
# =========================================================================
process_bases = [
    "what processes are eating the most CPU", "list top active tasks", "show high memory consumers",
    "which apps are slowing down my machine", "display top 10 processes by CPU", "list top processes",
    "find resource-heavy background processes", "show process activity monitor", "who is hogging all the RAM",
    "list top 5 processes", "what is taking up so much memory", "show top processes running right now",
    "display current task list", "show memory-heavy tasks", "list background tasks", "inspect heavy processes",
    "top process breakdown", "show me the top 8 processes by RAM usage", "which applications are using CPU",
    "display active processes on host", "list top running applications", "inspect running tasks",
    "show which task is utilizing the most processor", "what programs are open and consuming RAM"
]
add_variations("list_top_processes", process_bases)

# =========================================================================
# 3. check_network_status (IP address, ping, latency, gateway, interfaces)
# =========================================================================
network_bases = [
    "check network status", "what is my current IP address", "test internet latency to 8.8.8.8",
    "is the network connection stable", "show active network interfaces", "ping google dns",
    "check default gateway and ping", "report network telemetry", "am I connected to wifi or ethernet",
    "measure network ping", "show local ip and gateway", "check connectivity status",
    "inspect network adapter metrics", "is my internet working properly", "run a network ping test",
    "get local ip address", "what is my gateway ip", "how is our internet connection",
    "check if our wifi connection has high packet loss", "test ping to cloudflare dns"
]
add_variations("check_network_status", network_bases)

# =========================================================================
# 4. open_application (Launch programs, notepad, calc, chrome, obsidian, taskmgr)
# =========================================================================
app_names = ["notepad", "calculator", "calc", "command prompt", "cmd", "powershell", "obsidian", 
             "task manager", "taskmgr", "file explorer", "chrome", "vscode", "terminal"]
app_bases = []
for app in app_names:
    app_bases.extend([
        f"open {app}", f"launch {app}", f"start {app}", f"fire up {app}", f"bring up {app}",
        f"run {app}", f"can you open {app}", f"pull up {app}"
    ])
add_variations("open_application", app_bases)

# =========================================================================
# 5. write_obsidian_note (Create knowledge notes, document, log into vault)
# =========================================================================
note_bases = [
    "write an obsidian note about quantum computing", "save this research to my obsidian vault",
    "create a new note in obsidian called GPU architecture", "take a note on python decorators",
    "write a markdown document in obsidian vault", "log this technical finding into obsidian",
    "create an obsidian note titled FastAPI best practices", "add a note to my knowledge base in obsidian",
    "write down these findings in an obsidian note", "record a new note in my vault about docker networking",
    "save notes on transformer attention heads to obsidian", "document our meeting summary in obsidian",
    "write a note about memory management into 02_Knowledge_Base", "make an obsidian note on rust concurrency"
]
add_variations("write_obsidian_note", note_bases)

# =========================================================================
# 6. read_obsidian_vault (Search vault, retrieve notes, check second brain)
# =========================================================================
read_vault_bases = [
    "search obsidian vault for kubernetes", "read my obsidian note on transformer architecture",
    "find notes in my vault about neural networks", "look up my notes on pytorch optimization",
    "what notes do I have in obsidian about databases", "search my second brain for docker sops",
    "read the obsidian document on system architecture", "check my obsidian notes for git commands",
    "find in vault everything related to cuda kernels", "search knowledge base for microservices",
    "query obsidian vault for redis caching strategies", "inspect my obsidian notes on linux kernel"
]
add_variations("read_obsidian_vault", read_vault_bases)

# =========================================================================
# 7. set_system_volume (Mute, adjust volume, level controls)
# =========================================================================
volume_bases = [
    "set system volume to 50 percent", "turn the volume up", "lower the volume to 20",
    "mute the system audio", "unmute the speakers", "increase master volume",
    "turn the sound down a bit", "set volume to 80%", "turn volume all the way down",
    "crank up the audio volume to 90 percent", "adjust audio output to 35 percent",
    "set audio level to 60", "turn volume up to 75", "quiet down the system volume"
]
add_variations("set_system_volume", volume_bases)

# =========================================================================
# 8. take_screenshot (Screen capture, grab desktop display)
# =========================================================================
screenshot_bases = [
    "take a screenshot", "capture the screen right now", "snap a picture of my desktop",
    "grab a screenshot of the display", "save a screenshot to screenshots folder",
    "take a snap of my monitor", "capture current display frame", "screenshot my screen",
    "save current desktop snapshot", "take a quick screenshot of what I have open"
]
add_variations("take_screenshot", screenshot_bases)

# =========================================================================
# 9. kill_process (Terminate app, end task, force close PID)
# =========================================================================
kill_bases = [
    "kill process notepad", "terminate chrome", "force close calculator",
    "kill task 9248", "end process with pid 4512", "stop the hanging notepad process",
    "kill python process", "force terminate cmd.exe", "shut down the frozen application",
    "kill process explorer.exe", "end task spotify", "terminate the runaway process"
]
add_variations("kill_process", kill_bases)

# =========================================================================
# 10. learn_from_internet (Web scraping, search online and ingest to vault)
# =========================================================================
learn_bases = [
    "learn about quantum computing from the internet and save to vault",
    "research rust web frameworks online and write a note",
    "search the web for llama 3 architecture and learn it",
    "autonomous web research on modern graph databases",
    "browse the web to learn how solid state drives work and document it",
    "look up recent breakthroughs in solid state batteries online and note it down",
    "learn from the web about kubernetes service mesh",
    "do online research about redis cluster replication and save to obsidian",
    "search google for zero knowledge rollups and index a note",
    "research linux eBPF on the internet and store notes in vault"
]
add_variations("learn_from_internet", learn_bases)

# =========================================================================
# 11. control_window (Minimize, maximize, restore, snap, focus window)
# =========================================================================
window_bases = [
    "minimize chrome window", "maximize notepad", "bring obsidian to the front",
    "restore the calculator window", "snap current window to the left side of screen",
    "focus the visual studio code window", "minimize all windows", "hide the active window",
    "bring terminal to foreground", "snap this window to the right", "maximize active window",
    "switch focus to browser window", "minimize spotify window"
]
add_variations("control_window", window_bases)

# =========================================================================
# 12. type_and_automate (Send keystrokes, click mouse, press enter)
# =========================================================================
automate_bases = [
    "type hello world into the active window", "press enter on the keyboard",
    "click the mouse at coordinates 500 300", "send keystroke control c",
    "press spacebar", "simulate typing python main.py and hit enter",
    "double click at current mouse position", "press alt tab to switch windows",
    "type my status update and press submit", "send key combination ctrl v"
]
add_variations("type_and_automate", automate_bases)

# =========================================================================
# 13. search_local_files (Find files on disk, locate .py, search C: and E:)
# =========================================================================
file_search_bases = [
    "find all pdf files on my E drive", "search for requirements.txt in this folder",
    "locate where python.exe is installed", "find files matching report*.docx",
    "search disk for config.json", "find any csv files in downloads",
    "search local files for invoice", "where is my docker-compose.yml located",
    "find all python files larger than 1 megabyte on disk", "search drive for backup zip"
]
add_variations("search_local_files", file_search_bases)

# =========================================================================
# 14. verify_biometrics (Face recognition, scan user webcam, biometrics)
# =========================================================================
bio_bases = [
    "verify my face with biometric recognition", "scan my face with the webcam",
    "biometric verification check", "authenticate my identity using camera",
    "run facial recognition scan", "is that me in front of the camera",
    "verify user biometrics", "check my face against enrolled owner profile",
    "scan webcam to authenticate operator", "biometric face scan now"
]
add_variations("verify_biometrics", bio_bases)

# =========================================================================
# 15. analyze_screen (OCR screen text, visual inspection of display)
# =========================================================================
screen_bases = [
    "analyze what is on my screen right now", "read the error message displayed on my monitor",
    "what text is visible on my screen", "inspect my display and tell me what you see",
    "run visual OCR on the current screen", "look at my screen and help me with this code",
    "analyze the open application on my display", "extract the text from my active monitor",
    "can you see the error dialog on my screen", "read the console log visible on screen"
]
add_variations("analyze_screen", screen_bases)

# =========================================================================
# 16. conversation (General Chat, Banter, Empathy, Greetings, AND 500+ FALSE-FRIEND TECHNICAL QUERIES!)
# =========================================================================
chat_bases = [
    "hello jessica", "hi there", "how are you doing today", "good morning jessica",
    "what is your name", "who created you", "tell me a funny joke",
    "how smart are you now", "where do you live", "what are your thoughts on artificial intelligence",
    "thank you for your help", "you are amazing jessica", "what can you do for me",
    "how do you feel today", "are you conscious", "tell me about yourself",
    "good evening", "how was your day", "do you ever sleep", "what is your favorite topic"
]
add_variations("conversation", chat_bases)

# 500+ ADVERSARIAL FALSE-FRIEND TECHNICAL QUERIES (Explaining technical concepts -> CONVERSATION!)
false_friend_concepts = [
    ("Explain how the BGP routing protocol works", "BGP routing"),
    ("Tell me about TCP handshake latency and three-way negotiation", "TCP handshake"),
    ("How does Docker container networking work under the hood", "Docker networking"),
    ("Explain process scheduling algorithms in modern operating system kernels", "process scheduling"),
    ("What is virtual memory and how does page table swapping work", "virtual memory"),
    ("How does an SSD flash controller handle wear leveling and TRIM", "SSD wear leveling"),
    ("Explain the architectural differences between L1, L2, and L3 CPU cache", "CPU cache hierarchy"),
    ("What is asymmetric cryptography and how does RSA public key encryption work", "RSA cryptography"),
    ("Explain neural network backpropagation and stochastic gradient descent", "backpropagation"),
    ("How does PyTorch manage CUDA streams and asynchronous GPU memory transfers", "CUDA stream synchronization"),
    ("Tell me about the Raft consensus algorithm and leader election", "Raft consensus"),
    ("How does Redis implement in-memory persistence with RDB snapshots and AOF", "Redis persistence"),
    ("Explain how DNS resolution traverses root, TLD, and authoritative nameservers", "DNS resolution"),
    ("What is an interrupt service routine and how does CPU context switching happen", "interrupt service routines"),
    ("How do zero-knowledge succinct proofs work mathematically", "zero-knowledge proofs"),
    ("Explain transformer multi-head self-attention and matrix dot-product scaling", "transformer attention"),
    ("Tell me about database index B-trees and write-ahead logging durability", "B-tree indexes"),
    ("What is the difference between TCP congestion control and UDP datagrams", "TCP vs UDP"),
    ("Explain how branch prediction and speculative execution operate on CPUs", "branch prediction"),
    ("How does the Linux epoll system call provide high performance event loops", "Linux epoll"),
    ("What is the difference between synchronous and asynchronous I/O in kernels", "async I/O"),
    ("Explain how garbage collection works in modern runtimes like V8 and Go", "garbage collection"),
    ("How does TLS 1.3 negotiate session keys using Diffie-Hellman", "TLS 1.3 handshake"),
    ("Tell me about quantum entanglement and superposition in quantum computing", "quantum entanglement"),
    ("Explain memory-mapped files and how the mmap system call functions", "mmap architecture"),
    ("What is cache invalidation and false sharing in multi-threaded programs", "cache invalidation"),
    ("Explain how neural network quantization like NF4 and INT8 reduces weight footprint", "quantization NF4"),
    ("How does a convolutional neural network extract spatial hierarchy features", "CNN architecture"),
    ("Tell me about vector embeddings and cosine similarity in semantic search", "vector embeddings"),
    ("What is the CAP theorem in distributed systems design", "CAP theorem"),
    ("Explain how database sharding distributes table records across partitions", "database sharding"),
    ("How does LoRA low rank adaptation train rank decomposition matrices", "LoRA rank decomposition"),
    ("Explain the difference between preemptive and cooperative multitasking", "multitasking kernels"),
    ("What is a race condition and how do mutexes and semaphores prevent it", "race conditions"),
    ("Explain how packet switching works across internet routers", "packet switching"),
    ("Tell me about graph neural networks and message passing paradigms", "graph neural networks"),
    ("How does consistent hashing balance distributed cache clusters", "consistent hashing"),
    ("Explain how memory paging avoids external fragmentation in physical RAM", "memory paging"),
    ("What are SIMD instructions and vector registers on modern processors", "SIMD vectorization"),
    ("Explain how write amplification affects solid state storage endurance", "write amplification")
]

chat_framings = [
    "Explain {topic} like we're chatting over coffee",
    "Can you explain {topic} to me in simple terms?",
    "Tell me how {topic} works in detail",
    "What is {topic} and why is it important?",
    "Could you break down {topic} for me?",
    "Hey Jessica, explain {topic}",
    "Jessica, what's your take on {topic}?",
    "I'm curious about {topic}, how does it operate?",
    "Walk me through the fundamentals of {topic}",
    "Give me an intuitive overview of {topic}",
    "How would you describe {topic} to a software engineer?",
    "What are the pros and cons of {topic}?",
    "Why does modern software rely on {topic}?",
    "Can you give me a clear breakdown of {topic}?"
]

for raw_q, short_name in false_friend_concepts:
    all_data.append({"command": raw_q, "intent": "conversation"})
    for framing in chat_framings:
        q = framing.format(topic=short_name)
        all_data.append({"command": q, "intent": "conversation"})

print(f"[*] Generated raw dataset pool: {len(all_data)} samples.")

# Balance classes and target exactly 3,000+ samples
# Group by intent
intent_pools = {intent: [] for intent in INTENT_CLASSES}
for item in all_data:
    intent_pools[item["intent"]].append(item)

# Deduplicate within each intent pool
for intent in INTENT_CLASSES:
    seen = set()
    deduped = []
    for item in intent_pools[intent]:
        cmd_clean = item["command"].strip().lower()
        if cmd_clean not in seen:
            seen.add(cmd_clean)
            deduped.append(item)
    intent_pools[intent] = deduped
    print(f"  - Intent '{intent}': {len(deduped)} unique samples")

final_dataset = []
# Ensure conversation has 600+ samples (including the 500 false friends)
# and each tool class has 150-200 samples
for intent, samples in intent_pools.items():
    if intent == "conversation":
        target_count = max(len(samples), 650)
        # Resample or take all
        if len(samples) < target_count:
            extended = samples + random.choices(samples, k=target_count - len(samples))
            final_dataset.extend(extended)
        else:
            final_dataset.extend(samples[:target_count])
    else:
        target_count = min(max(len(samples), 160), 220)
        if len(samples) < target_count:
            extended = samples + random.choices(samples, k=target_count - len(samples))
            final_dataset.extend(extended)
        else:
            final_dataset.extend(random.sample(samples, target_count))

random.seed(42)
random.shuffle(final_dataset)

print(f"\n[+] Total Balanced Dataset: {len(final_dataset)} samples across {len(INTENT_CLASSES)} classes.")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for item in final_dataset:
        f.write(json.dumps(item) + "\n")

print(f"[+] Successfully saved hardened dataset to {OUTPUT_FILE}")

