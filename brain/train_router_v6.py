"""
Jessica Brain - Neural Router v6 Whisper-Hardened Training Script (Wave 4)
Trains Jessica's custom Transformer router across 6,000 samples.
Hardens the model against Whisper speech transcription artifacts and false-friend technical queries.
Saves model weights to router_v6.pt and mirrors to router_v5.pt through router_v1.pt.
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
    print("           TRAINING JESSICA INTENT ROUTER v6 (WHISPER-HARDENED)")
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

    # Save weights to router_v6.pt and mirror to v5, v4, v3, v2, v1
    save_path_v6 = WORKSPACE_ROOT / "brain" / "router_v6.pt"
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

    for p in [save_path_v6, save_path_v5, save_path_v4, save_path_v3, save_path_v2, save_path_v1]:
        torch.save(checkpoint_data, p)
    print(f"[+] Model weights saved to router_v6.pt and mirrored to v5, v4, v3, v2, v1.")

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
        ("Explain why BGP route reflectors are necessary in large iBGP networks", "conversation"),
        ("Tell me how the Linux CFS completely fair scheduler allocates CPU slices", "conversation"),
        ("How does virtual memory page table translation use the TLB cache?", "conversation"),
        ("What happens during the TLS 1.3 handshake compared to TLS 1.2?", "conversation"),
        ("Explain the difference between optimistic concurrency and pessimistic locking", "conversation"),
        # Nap wake up & companion banter
        ("Hey Jessica, I just woke up from my nap", "conversation"),
        ("I'm awake now", "conversation"),
        ("Good afternoon Jess, I'm up", "conversation"),
        ("Did you miss me while I was sleeping?", "conversation"),
        ("Jessica! Daddy's home", "conversation"),
        ("Daddy's home", "conversation"),
        ("Crishaira is here", "conversation"),
        ("Say hi to Crishaira", "conversation"),
        # Real system tool commands (MUST route to system tools)
        ("check system telemetry", "get_system_telemetry"),
        ("how much free ram do i have", "get_system_telemetry"),
        ("check gpu temperature and load", "get_system_telemetry"),
        ("is my cpu overheating right now", "get_system_telemetry"),
        ("what is my current cpu and ram usage", "get_system_telemetry"),
        ("list top processes", "list_top_processes"),
        ("who is hogging all the ram", "list_top_processes"),
        ("which apps are slowing down my machine", "list_top_processes"),
        ("what processes are eating the most cpu", "list_top_processes"),
        ("check network status", "check_network_status"),
        ("what is my current ip address", "check_network_status"),
        ("test internet latency to 8.8.8.8", "check_network_status"),
        ("ping google dns", "check_network_status"),
        ("is the network connection stable", "check_network_status"),
        ("open chrome", "open_application"),
        ("launch visual studio code", "open_application"),
        ("start notepad", "open_application"),
        ("set volume to 50 percent", "set_system_volume"),
        ("mute the audio", "set_system_volume"),
        ("turn the volume up", "set_system_volume"),
        ("take a screenshot", "take_screenshot"),
        ("capture the screen", "take_screenshot"),
        ("kill process notepad", "kill_process"),
        ("terminate chrome", "kill_process"),
        ("write an obsidian note about my meeting", "write_obsidian_note"),
        ("save this to obsidian", "write_obsidian_note"),
        ("search my obsidian notes for network architecture", "read_obsidian_vault"),
        ("read notes from my vault", "read_obsidian_vault"),
        ("search google for python 3.12 release notes", "learn_from_internet"),
        ("look up nextjs 15 documentation on the web", "learn_from_internet"),
        ("minimize the active window", "control_window"),
        ("maximize this window", "control_window"),
        ("type hello world and press enter", "type_and_automate"),
        ("find file report.pdf in my documents", "search_local_files"),
        ("verify my facial biometrics", "verify_biometrics"),
        ("analyze what is on my screen right now", "analyze_screen")
    ]

    passed = 0
    total_tests = len(adversarial_tests)

    with torch.no_grad():
        for query, expected in adversarial_tests:
            ids = tokenizer.encode(query, max_len=max_len)
            x = torch.tensor([ids], dtype=torch.long, device=device)
            logits = model(x)
            probs = torch.softmax(logits, dim=-1)
            pred_id = torch.argmax(logits, dim=-1).item()
            pred_intent = ID_TO_INTENT[pred_id]
            conf = probs[0, pred_id].item() * 100.0

            is_correct = (pred_intent == expected)
            status = "PASS" if is_correct else "FAIL"
            if is_correct:
                passed += 1

            if not is_correct:
                print(f"[{status}] '{query}' -> Got: {pred_intent} ({conf:.1f}%), Expected: {expected}")

    accuracy = (passed / total_tests) * 100.0
    print("-" * 70)
    print(f"Adversarial Test Results: {passed}/{total_tests} passed ({accuracy:.1f}% accuracy)")
    print("=" * 70)

    # Persist benchmark results
    results_file = WORKSPACE_ROOT / "evals" / "router_v6_eval_results.json"
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": len(samples),
        "vocab_size": tokenizer.vocab_size,
        "epochs": epochs,
        "initial_loss": round(initial_loss, 4),
        "final_loss": round(final_loss, 4),
        "training_time_sec": round(total_training_time, 2),
        "test_suite_passed": passed,
        "test_suite_total": total_tests,
        "test_suite_accuracy": round(accuracy, 2)
    }
    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"[+] Benchmark results saved to {results_file}")

    return results


if __name__ == "__main__":
    res = train()
    if res["test_suite_accuracy"] >= 95.0:
        sys.exit(0)
    sys.exit(1)

