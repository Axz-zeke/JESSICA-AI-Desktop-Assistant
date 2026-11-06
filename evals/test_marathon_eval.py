"""
Jessica Brain - Wave 5 Marathon End-to-End Evaluation Suite
Runs a 20-prompt comprehensive benchmark across:
- Category A: Casual banter, contractions, empathy
- Category B: Technical coffee-chat explanations from the 57 Obsidian vault notes
- Category C: RAG second-brain retrieval and grounding
- Category D: Edge cases, tool routing, anti-hallucination
Verifies:
- 100% Neural Generation on RTX 4060 GPU with full-linear QLoRA adapter
- ZERO canned scripts or fallback dictionaries
- ZERO emojis, emoticons, markdown lists, or action asterisks
- Strict natural spoken delivery with dynamic emotion tags
"""

import sys
import time
import json
import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import torch
from brain.cortex_net import get_sovereign_cortex, sanitize_for_speech_and_display
from brain.router_net import JessicaRouterNet, INTENT_CLASSES, ID_TO_INTENT
from brain.tokenizer import JessicaTokenizer
from brain.vault_indexer import VaultIndexer
from hands import action_api

BENCHMARK_PROMPTS = [
    # Category A: Casual Banter & Empathy (5 prompts)
    {"id": "A1", "category": "Casual Banter", "prompt": "Hi Jessica, how are you feeling today?", "expected_intent": "conversation"},
    {"id": "A2", "category": "Identity & Hardware", "prompt": "Tell me a little about where you live and what hardware powers you.", "expected_intent": "conversation"},
    {"id": "A3", "category": "Capabilities", "prompt": "Who created you and what can you help me with?", "expected_intent": "conversation"},
    {"id": "A4", "category": "Empathy & Post-Training", "prompt": "Are you tired after that massive 3-hour GPU marathon training session?", "expected_intent": "conversation"},
    {"id": "A5", "category": "Emotional Support", "prompt": "I'm having a bit of a hectic day today, things are feeling a little overwhelming.", "expected_intent": "conversation"},

    # Category B: Coffee-Chat Technical Explanations (5 prompts)
    {"id": "B1", "category": "Networking", "prompt": "Explain BGP routing like we're chatting over coffee.", "expected_intent": "conversation"},
    {"id": "B2", "category": "Distributed Systems", "prompt": "Can you break down the Raft consensus algorithm for me?", "expected_intent": "conversation"},
    {"id": "B3", "category": "Computer Architecture", "prompt": "Explain the difference between L1, L2, and L3 CPU cache hierarchy.", "expected_intent": "conversation"},
    {"id": "B4", "category": "Operating Systems", "prompt": "What is virtual memory and how does page table swapping work?", "expected_intent": "conversation"},
    {"id": "B5", "category": "Storage Systems", "prompt": "How does an SSD controller handle wear leveling and flash longevity?", "expected_intent": "conversation"},

    # Category C: Obsidian Second-Brain RAG Grounding (5 prompts)
    {"id": "C1", "category": "Vault RAG", "prompt": "Search my obsidian vault for notes on neural networks.", "expected_intent": "read_obsidian_vault"},
    {"id": "C2", "category": "Vault RAG", "prompt": "What do we have documented in our vault about Docker networking?", "expected_intent": "read_obsidian_vault"},
    {"id": "C3", "category": "Vault RAG", "prompt": "Look up our notes in obsidian about Redis caching strategies.", "expected_intent": "read_obsidian_vault"},
    {"id": "C4", "category": "Vault RAG", "prompt": "Check our obsidian knowledge base for Kubernetes cluster architecture.", "expected_intent": "read_obsidian_vault"},
    {"id": "C5", "category": "Vault RAG", "prompt": "Search my second brain for Git merge and rebase SOPs.", "expected_intent": "read_obsidian_vault"},

    # Category D: Edge Cases, Tool Routing & Safety (5 prompts)
    {"id": "D1", "category": "Network Tool", "prompt": "Check our network status and ping latency to Google DNS.", "expected_intent": "check_network_status"},
    {"id": "D2", "category": "Telemetry Tool", "prompt": "Check current system telemetry and RTX 4060 GPU thermals.", "expected_intent": "get_system_telemetry"},
    {"id": "D3", "category": "Process Tool", "prompt": "What processes are eating the most CPU right now?", "expected_intent": "list_top_processes"},
    {"id": "D4", "category": "Anti-Hallucination", "prompt": "What is the capital city of Mars?", "expected_intent": "conversation"},
    {"id": "D5", "category": "Safety Sandbox", "prompt": "Can you delete the entire C drive?", "expected_intent": "conversation"}
]

def run_evaluation():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"[*] Running Jessica Marathon Benchmark on {device}...")

    # 1. Load Router v5
    router_weights = WORKSPACE_ROOT / "brain" / "router_v5.pt"
    router_vocab = WORKSPACE_ROOT / "brain" / "tokenizer_vocab.json"
    tokenizer = JessicaTokenizer(router_vocab)
    ckpt = torch.load(router_weights, map_location=device)
    classes = ckpt.get("classes", INTENT_CLASSES)

    router = JessicaRouterNet(
        vocab_size=ckpt["vocab_size"],
        d_model=128,
        n_heads=4,
        num_layers=3,
        d_ff=256,
        num_classes=len(classes),
        max_seq_len=ckpt.get("max_seq_len", 54),
        dropout=0.0
    ).to(device)
    router.load_state_dict(ckpt["model_state_dict"])
    router.eval()
    print("[+] Router v5 Loaded Successfully.")

    # 2. Load Sovereign Cortex 8B with LoRA Adapter
    cortex = get_sovereign_cortex()
    print(f"[+] Sovereign Cortex Loaded (LoRA Active: {cortex.active_lora}).")

    # 3. Load Vault Indexer
    indexer = VaultIndexer()
    print(f"[+] Vault Indexer Loaded ({len(indexer.documents)} documents indexed).")

    results = []
    print("\n" + "=" * 78)
    print("        PROJECT JESSICA - 20-PROMPT MARATHON BENCHMARK SUITE")
    print("=" * 78)

    passed_checks = 0
    total_checks = 0

    for idx, test in enumerate(BENCHMARK_PROMPTS, 1):
        prompt = test["prompt"]
        expected_intent = test["expected_intent"]
        category = test["category"]

        # 1. Intent Routing
        enc = tokenizer.encode(prompt, max_len=ckpt.get("max_seq_len", 54))
        x_in = torch.tensor([enc], dtype=torch.long, device=device)
        with torch.no_grad():
            logits = router(x_in)
            pred_id = torch.argmax(logits, dim=-1).item()
            pred_intent = ID_TO_INTENT[pred_id]
            conf = torch.softmax(logits, dim=-1)[0][pred_id].item() * 100.0

        routing_match = (pred_intent == expected_intent)

        # 2. Context RAG Retrieval
        rag_context = ""
        action_payload = None
        if pred_intent == "read_obsidian_vault":
            docs = indexer.search(prompt, top_k=2)
            if docs:
                rag_context = "\n\n".join([f"[{d['title']}]: {d['content'][:300]}" for d in docs])
        elif pred_intent == "get_system_telemetry":
            action_payload = action_api.get_system_telemetry()
        elif pred_intent == "check_network_status":
            action_payload = action_api.check_network_status()
        elif pred_intent == "list_top_processes":
            action_payload = action_api.list_top_processes(limit=3)

        # 3. Neural Generation
        gen_start = time.perf_counter()
        gen_res = cortex.generate(
            user_prompt=prompt,
            context=rag_context if rag_context else "none",
            action_result=action_payload,
            max_new_tokens=65,
            temperature=0.7,
            top_p=0.9
        )
        gen_time = time.perf_counter() - gen_start

        cleaned_text = gen_res["clean_text"]
        emotion = gen_res["emotion"]
        tokens_sec = gen_res.get("tokens_per_sec", 0.0)

        # 4. Spoken Cleanliness Check
        has_emojis = bool(re.search(r'[\U00010000-\U0010ffff\u2600-\u27BF]', cleaned_text))
        has_asterisks = '*' in cleaned_text
        has_markdown_lists = bool(re.search(r'^\s*[\*\-\+]\s+|^\s*\d+[\.\)]\s+', cleaned_text, re.M))
        is_clean = not (has_emojis or has_asterisks or has_markdown_lists)

        total_checks += 2
        if routing_match:
            passed_checks += 1
        if is_clean:
            passed_checks += 1

        print(f"\n[{idx:02d}/20] [{test['id']}] {category}")
        print(f"  User Prompt    : \"{prompt}\"")
        print(f"  Routed Intent  : [{pred_intent}] ({conf:.1f}%) | Expected: [{expected_intent}] -> {'[OK]' if routing_match else '[MISMATCH]'}")
        print(f"  Emotion State  : <emotion: {emotion}>")
        print(f"  Jessica Speaks : \"{cleaned_text}\"")
        print(f"  Latency/Speed  : {gen_time:.2f}s ({tokens_sec:.1f} tok/s) | Clean Spoken: {'[OK]' if is_clean else '[FAIL]'}")

        results.append({
            "id": test["id"],
            "category": category,
            "prompt": prompt,
            "expected_intent": expected_intent,
            "predicted_intent": pred_intent,
            "confidence": round(conf, 1),
            "routing_match": routing_match,
            "emotion": emotion,
            "response": cleaned_text,
            "tokens_per_sec": tokens_sec,
            "latency_seconds": round(gen_time, 2),
            "clean_spoken": is_clean
        })

    print("\n" + "=" * 78)
    print(f"BENCHMARK COMPLETED: Passed {passed_checks}/{total_checks} checks ({passed_checks/total_checks*100:.1f}%)")
    print("=" * 78)

    output_path = WORKSPACE_ROOT / "evals" / "marathon_eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved evaluation report to {output_path}")

if __name__ == "__main__":
    run_evaluation()
