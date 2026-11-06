"""
Jessica Evals - Neural Router v0.2 Generalization Test
Evaluates Jessica's v0.2 router on unseen test commands across all 10 intent categories.
"""

import sys
import torch
import torch.nn.functional as F
from pathlib import Path
from typing import List, Dict

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.tokenizer import JessicaTokenizer
from brain.router_net import JessicaRouterNet, ID_TO_INTENT, INTENT_CLASSES


def run_evals():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("=" * 75)
    print("      JESSICA BRAIN ROUTER v0.2 EVALUATION (UNSEEN TEST SUITE)")
    print("=" * 75)
    print(f"Inference Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    vocab_path = WORKSPACE_ROOT / "brain" / "tokenizer_vocab.json"
    weights_path = WORKSPACE_ROOT / "brain" / "router_v2.pt"

    if not weights_path.exists():
        weights_path = WORKSPACE_ROOT / "brain" / "router_v1.pt"

    tokenizer = JessicaTokenizer(vocab_path)
    checkpoint = torch.load(weights_path, map_location=device)
    max_len = checkpoint.get("max_seq_len", 48)
    classes = checkpoint.get("classes", INTENT_CLASSES)

    model = JessicaRouterNet(
        vocab_size=checkpoint["vocab_size"],
        d_model=128,
        n_heads=4,
        num_layers=3,
        d_ff=256,
        num_classes=len(classes),
        max_seq_len=max_len,
        dropout=0.0
    ).to(device)

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    test_suite: List[Dict[str, str]] = [
        {"command": "Could you tell me how much RAM and CPU is currently being used?", "expected": "get_system_telemetry"},
        {"command": "Which background processes are consuming the most memory right now?", "expected": "list_top_processes"},
        {"command": "Is our internet connection reachable and responsive to 1.1.1.1?", "expected": "check_network_status"},
        {"command": "Please start the calculator utility", "expected": "open_application"},
        {"command": "Create a note in 03_Daily_Logs summarizing today's sprint", "expected": "write_obsidian_note"},
        {"command": "Search the obsidian vault for our GPU telemetry rules", "expected": "read_obsidian_vault"},
        {"command": "Set the master audio volume to 65%", "expected": "set_system_volume"},
        {"command": "Capture a screenshot of my desktop right now", "expected": "take_screenshot"},
        {"command": "Kill process spotify.exe immediately", "expected": "kill_process"},
        {"command": "Good morning Jessica, what is your operational status?", "expected": "conversation"}
    ]

    correct = 0
    total = len(test_suite)

    print(f"\n{'#':<2} | {'Command':<46} | {'Predicted Intent':<22} | {'Conf':<6} | {'Status'}")
    print("-" * 92)

    with torch.no_grad():
        for idx, item in enumerate(test_suite, 1):
            cmd = item["command"]
            expected = item["expected"]

            ids = tokenizer.encode(cmd, max_len=max_len)
            x = torch.tensor([ids], dtype=torch.long, device=device)

            logits = model(x)
            probs = F.softmax(logits, dim=-1)
            conf, pred_id = torch.max(probs, dim=-1)
            predicted = classes[pred_id.item()]
            confidence = conf.item() * 100.0

            is_match = (predicted == expected)
            if is_match:
                correct += 1
                status = "[PASS]"
            else:
                status = f"[FAIL (Exp: {expected})]"

            short_cmd = (cmd[:43] + "...") if len(cmd) > 46 else cmd
            print(f"{idx:<2} | {short_cmd:<46} | {predicted:<22} | {confidence:5.1f}% | {status}")

    accuracy = (correct / total) * 100.0
    print("=" * 92)
    print(f"Overall Brain v0.2 Routing Accuracy: {accuracy:.1f}% ({correct}/{total} Passed)")
    print("=" * 92)

    return accuracy


if __name__ == "__main__":
    run_evals()
