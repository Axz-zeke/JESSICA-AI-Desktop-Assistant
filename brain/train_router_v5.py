"""
Jessica Brain - Neural Router v5 Hardening & Training Script (Wave 4)
Trains Jessica's custom Transformer router on the RTX 4060 across 4,700 samples.
Hardens the model against false-friend technical queries (e.g. BGP routing -> conversation).
Saves model weights to router_v5.pt and mirrors to router_v4.pt through router_v1.pt.
"""

import json
import time
import sys
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.tokenizer import JessicaTokenizer
from brain.router_net import JessicaRouterNet, INTENT_TO_ID, ID_TO_INTENT, INTENT_CLASSES


def train():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    dataset_path = WORKSPACE_ROOT / "datasets" / "router_train.jsonl"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    # Load dataset
    samples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    print(f"[*] Loaded {len(samples)} training samples across {len(INTENT_CLASSES)} classes.")

    # Build tokenizer vocabulary
    corpus = [s["command"] for s in samples]
    tokenizer = JessicaTokenizer()
    tokenizer.build_vocab(corpus, min_freq=1, max_vocab_size=4096)
    vocab_path = WORKSPACE_ROOT / "brain" / "tokenizer_vocab.json"
    tokenizer.save(str(vocab_path))
    print(f"[*] Vocabulary built and saved to {vocab_path}. Vocab size: {tokenizer.vocab_size}")

    # Prepare tensors
    max_len = 54
    input_ids = [tokenizer.encode(s["command"], max_len=max_len) for s in samples]
    target_ids = [INTENT_TO_ID[s["intent"]] for s in samples]

    x_tensor = torch.tensor(input_ids, dtype=torch.long)
    y_tensor = torch.tensor(target_ids, dtype=torch.long)

    dataset = TensorDataset(x_tensor, y_tensor)
    batch_size = 32
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = JessicaRouterNet(
        vocab_size=tokenizer.vocab_size,
        d_model=128,
        n_heads=4,
        num_layers=3,
        d_ff=256,
        num_classes=len(INTENT_CLASSES),
        max_seq_len=max_len,
        dropout=0.1
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=1e-4)
    epochs = 25
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    print("\n" + "=" * 70)
    print("           TRAINING JESSICA INTENT ROUTER v5 (HARDENED)")
    print("=" * 70)

    initial_loss = None
    final_loss = None
    start_time = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_x.size(0)
            preds = torch.argmax(logits, dim=-1)
            correct += (preds == batch_y).sum().item()
            total += batch_x.size(0)

        scheduler.step()
        epoch_loss = total_loss / total
        epoch_acc = (correct / total) * 100.0

        if epoch == 1:
            initial_loss = epoch_loss
        if epoch == epochs:
            final_loss = epoch_loss

        print(f"Epoch [{epoch:02d}/{epochs:02d}] | Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:6.2f}% | LR: {scheduler.get_last_lr()[0]:.6f}")

    total_training_time = time.perf_counter() - start_time
    print("-" * 70)
    print(f"Training Complete in {total_training_time:.2f} seconds.")
    print(f"Initial Loss (Epoch 1):  {initial_loss:.4f}")
    print(f"Final Loss (Epoch {epochs}):   {final_loss:.4f}")
    print("=" * 70)

    # Save weights to router_v5.pt and mirror to v4, v3, v2, v1
    save_path_v5 = WORKSPACE_ROOT / "brain" / "router_v5.pt"
    save_path_v4 = WORKSPACE_ROOT / "brain" / "router_v4.pt"
    save_path_v3 = WORKSPACE_ROOT / "brain" / "router_v3.pt"
    save_path_v2 = WORKSPACE_ROOT / "brain" / "router_v2.pt"
    save_path_v1 = WORKSPACE_ROOT / "brain" / "router_v1.pt"

    checkpoint_data = {
        "model_state_dict": model.state_dict(),
        "vocab_size": tokenizer.vocab_size,
        "max_seq_len": max_len,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "classes": INTENT_CLASSES
    }

    for p in [save_path_v5, save_path_v4, save_path_v3, save_path_v2, save_path_v1]:
        torch.save(checkpoint_data, p)
    print(f"[+] Model weights saved to router_v5.pt and mirrored to v4, v3, v2, v1.")

    # =========================================================================
    # Run 100-Prompt Adversarial Test Suite
    # =========================================================================
    print("\n" + "=" * 70)
    print("       RUNNING 100-PROMPT ADVERSARIAL ROUTING BENCHMARK")
    print("=" * 70)

    model.eval()

    adversarial_tests = [
        # False friends (technical explanations that MUST route to conversation)
        ("Explain how the BGP routing protocol works", "conversation"),
        ("Explain BGP routing like we're chatting over coffee", "conversation"),
        ("Tell me about TCP handshake latency and three-way negotiation", "conversation"),
        ("How does Docker container networking work under the hood", "conversation"),
        ("Explain process scheduling algorithms in modern operating system kernels", "conversation"),
        ("What is virtual memory and how does page table swapping work", "conversation"),
        ("How does an SSD flash controller handle wear leveling and TRIM", "conversation"),
        ("Explain the architectural differences between L1, L2, and L3 CPU cache", "conversation"),
        ("What is asymmetric cryptography and how does RSA public key encryption work", "conversation"),
        ("Explain neural network backpropagation and stochastic gradient descent", "conversation"),
        ("How does PyTorch manage CUDA streams and asynchronous GPU memory transfers", "conversation"),
        ("Tell me about the Raft consensus algorithm and leader election", "conversation"),
        ("How does Redis implement in-memory persistence with RDB snapshots and AOF", "conversation"),
        ("Explain how DNS resolution traverses root, TLD, and authoritative nameservers", "conversation"),
        ("What is an interrupt service routine and how does CPU context switching happen", "conversation"),
        ("How do zero-knowledge succinct proofs work mathematically", "conversation"),
        ("Explain transformer multi-head self-attention and matrix dot-product scaling", "conversation"),
        ("Tell me about database index B-trees and write-ahead logging durability", "conversation"),
        ("What is the difference between TCP congestion control and UDP datagrams", "conversation"),
        ("Explain how branch prediction and speculative execution operate on CPUs", "conversation"),
        ("How does the Linux epoll system call provide high performance event loops", "conversation"),
        ("Can you explain BGP routing to me in simple terms?", "conversation"),
        ("Could you break down process scheduling for me?", "conversation"),
        ("I'm curious about virtual memory, how does it operate?", "conversation"),
        ("Walk me through the fundamentals of CPU cache hierarchy", "conversation"),
        ("Give me an intuitive overview of neural backpropagation", "conversation"),
        ("How would you describe CUDA stream synchronization to a software engineer?", "conversation"),
        ("What are the pros and cons of Redis persistence?", "conversation"),
        ("Why does modern software rely on DNS resolution?", "conversation"),
        ("Can you give me a clear breakdown of Raft consensus?", "conversation"),
        ("Hey Jessica, explain BGP routing", "conversation"),
        ("Jessica, what's your take on zero-knowledge proofs?", "conversation"),
        ("Explain memory paging like we're having coffee", "conversation"),
        ("Tell me about SIMD vector registers", "conversation"),
        ("Explain write amplification on SSD storage", "conversation"),
        ("How does quantum superposition work in quantum algorithms?", "conversation"),
        ("Explain consistent hashing across distributed nodes", "conversation"),
        ("What is the CAP theorem in distributed computing?", "conversation"),
        ("Explain database sharding strategies", "conversation"),
        ("Tell me how LoRA low-rank adaptation reduces trainable parameters", "conversation"),

        # Real OS Tool Commands
        ("Check system telemetry", "get_system_telemetry"),
        ("What is the current CPU and RAM usage?", "get_system_telemetry"),
        ("Show me system telemetry", "get_system_telemetry"),
        ("Check GPU temperature and load", "get_system_telemetry"),
        ("How much VRAM is currently allocated?", "get_system_telemetry"),
        ("What processes are eating the most CPU?", "list_top_processes"),
        ("List top active tasks", "list_top_processes"),
        ("Show high memory consumers", "list_top_processes"),
        ("Which apps are slowing down my machine?", "list_top_processes"),
        ("Display top 10 processes by CPU", "list_top_processes"),
        ("Check network status", "check_network_status"),
        ("What is my current IP address?", "check_network_status"),
        ("Test internet latency to 8.8.8.8", "check_network_status"),
        ("Show active network interfaces", "check_network_status"),
        ("Ping google dns", "check_network_status"),
        ("Open notepad", "open_application"),
        ("Launch calculator", "open_application"),
        ("Start command prompt", "open_application"),
        ("Fire up obsidian", "open_application"),
        ("Launch task manager", "open_application"),
        ("Write an obsidian note about quantum computing", "write_obsidian_note"),
        ("Save this research to my obsidian vault", "write_obsidian_note"),
        ("Create a new note in obsidian called GPU architecture", "write_obsidian_note"),
        ("Take a note on python decorators", "write_obsidian_note"),
        ("Log this technical finding into obsidian", "write_obsidian_note"),
        ("Search obsidian vault for kubernetes", "read_obsidian_vault"),
        ("Read my obsidian note on transformer architecture", "read_obsidian_vault"),
        ("Find notes in my vault about neural networks", "read_obsidian_vault"),
        ("Look up my notes on pytorch optimization", "read_obsidian_vault"),
        ("Query obsidian vault for redis caching strategies", "read_obsidian_vault"),
        ("Set system volume to 50 percent", "set_system_volume"),
        ("Turn the volume up", "set_system_volume"),
        ("Mute the system audio", "set_system_volume"),
        ("Lower the volume to 20", "set_system_volume"),
        ("Set volume to 80%", "set_system_volume"),
        ("Take a screenshot", "take_screenshot"),
        ("Capture the screen right now", "take_screenshot"),
        ("Snap a picture of my desktop", "take_screenshot"),
        ("Grab a screenshot of the display", "take_screenshot"),
        ("Take a quick screenshot of what I have open", "take_screenshot"),
        ("Kill process notepad", "kill_process"),
        ("Terminate chrome", "kill_process"),
        ("Force close calculator", "kill_process"),
        ("Stop the hanging notepad process", "kill_process"),
        ("Kill python process", "kill_process"),
        ("Learn about quantum computing from the internet and save to vault", "learn_from_internet"),
        ("Research rust web frameworks online and write a note", "learn_from_internet"),
        ("Search the web for llama 3 architecture and learn it", "learn_from_internet"),
        ("Autonomous web research on modern graph databases", "learn_from_internet"),
        ("Browse the web to learn how solid state drives work and document it", "learn_from_internet"),
        ("Minimize chrome window", "control_window"),
        ("Maximize notepad", "control_window"),
        ("Bring obsidian to the front", "control_window"),
        ("Snap current window to the left side of screen", "control_window"),
        ("Focus the visual studio code window", "control_window"),
        ("Type hello world into the active window", "type_and_automate"),
        ("Press enter on the keyboard", "type_and_automate"),
        ("Click the mouse at coordinates 500 300", "type_and_automate"),
        ("Send keystroke control c", "type_and_automate"),
        ("Press alt tab to switch windows", "type_and_automate"),
        ("Find all pdf files on my E drive", "search_local_files"),
        ("Search for requirements.txt in this folder", "search_local_files"),
        ("Locate where python.exe is installed", "search_local_files"),
        ("Find files matching report*.docx", "search_local_files"),
        ("Search disk for config.json", "search_local_files"),
        ("Verify my face with biometric recognition", "verify_biometrics"),
        ("Scan my face with the webcam", "verify_biometrics"),
        ("Biometric verification check", "verify_biometrics"),
        ("Authenticate my identity using camera", "verify_biometrics"),
        ("Run facial recognition scan", "verify_biometrics"),
        ("Analyze what is on my screen right now", "analyze_screen"),
        ("Read the error message displayed on my monitor", "analyze_screen"),
        ("What text is visible on my screen", "analyze_screen"),
        ("Inspect my display and tell me what you see", "analyze_screen"),
        ("Run visual OCR on the current screen", "analyze_screen")
    ]

    correct_adversarial = 0
    total_adversarial = len(adversarial_tests)

    print(f"[*] Testing {total_adversarial} adversarial & OS prompts...")

    for cmd, expected in adversarial_tests:
        enc = tokenizer.encode(cmd, max_len=max_len)
        x = torch.tensor([enc], dtype=torch.long, device=device)
        with torch.no_grad():
            logits = model(x)
            pred_id = torch.argmax(logits, dim=-1).item()
            pred_intent = ID_TO_INTENT[pred_id]
            probs = torch.softmax(logits, dim=-1)[0]
            conf = probs[pred_id].item() * 100.0

        if pred_intent == expected:
            correct_adversarial += 1
        else:
            print(f"  [X] MISMATCH: '{cmd}'")
            print(f"      Expected: [{expected}], Got: [{pred_intent}] ({conf:.1f}%)")

    acc_adv = (correct_adversarial / total_adversarial) * 100.0
    print(f"\n[+] Adversarial Test Suite Accuracy: {correct_adversarial}/{total_adversarial} ({acc_adv:.1f}%)")
    assert acc_adv >= 98.0, f"Router v5 accuracy below requirement: {acc_adv:.1f}%"
    print("[+] Router v5 is fully verified and rock-solid!")


if __name__ == "__main__":
    train()

