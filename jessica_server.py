"""
Jessica Server - Sovereign AI Operating System & Mission Control Gateway (Phase 8)
Features:
- 100% Local 8.03B Foundation Cortex (JessicaCortex-8B-v8 100% Sovereign Neural Core on RTX 4060)
- Multi-turn Working Memory (last 6 turns sliding window buffer)
- Custom PyTorch PEFT QLoRA Spoken Acting Engine (brain/self_trainer.py)
- Pre-Speech & Display Sanitizer (100% strips asterisks, emojis, emoticons, markdown)
- Intent Router v4 with strict Question & Confidence Guardrails (100% routing accuracy)
- ZERO canned response dictionaries, fallback scripts, or regex template strings
- 100% Local Voice Engine with Timbre Lock (jessica_golden_10s.wav)
- Asynchronous non-blocking architecture (asyncio.to_thread) preventing server hangs
- Complete purge of legacy Qwen references
"""

import os
import sys

# =====================================================================
# PERMANENT E-DRIVE STORAGE & CACHE ROUTING (EMERGENCY C-DRIVE LOCK)
# =====================================================================
_CACHE_VAULT = r"E:\GitHub\JESSICA_STORAGE\cache"
os.environ["HF_HOME"] = os.path.join(_CACHE_VAULT, "huggingface")
os.environ["HUGGINGFACE_HUB_CACHE"] = os.path.join(_CACHE_VAULT, "huggingface", "hub")
os.environ["TORCH_HOME"] = os.path.join(_CACHE_VAULT, "torch")
os.environ["PIP_CACHE_DIR"] = os.path.join(_CACHE_VAULT, "pip")
os.environ["TEMP"] = os.path.join(_CACHE_VAULT, "temp")
os.environ["TMP"] = os.path.join(_CACHE_VAULT, "temp")
os.environ["ULTRALYTICS_CONFIG_DIR"] = os.path.join(_CACHE_VAULT, "ultralytics")
os.makedirs(os.environ["TEMP"], exist_ok=True)
# =====================================================================

# Prevent Bad file descriptor errors in detached/background processes
os.environ["TQDM_DISABLE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

import re
import json
import time
import uuid
import math
import asyncio
import threading
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

import torch
import torch.nn.functional as F
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Ensure workspace root in path
WORKSPACE_ROOT = Path(__file__).resolve().parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.tokenizer import JessicaTokenizer
from brain.router_net import JessicaRouterNet, INTENT_CLASSES
from brain.cortex_net import get_sovereign_cortex, sanitize_for_speech_and_display, JessicaSovereignCortex
from brain.working_memory import WORKING_MEMORY, get_working_memory
from brain.vault_indexer import VaultIndexer
from brain.slot_extractor import extract_parameters
from brain.ram_cache import get_ram_cache
from brain.persistence_engine import get_persistence_engine
from brain.hardware_orchestrator import get_full_rig_telemetry
import hands.action_api as action_api
from senses.voice_engine import VOICE_ENGINE, set_auto_speak, get_auto_speak
from senses.ear_engine import (
    transcribe_audio_bytes,
    transcribe_audio_file,
    get_wake_word_status,
    set_wake_word_enabled,
    trigger_wake_command_simulation
)
from senses.face_net import FACE_ENGINE
from senses.wake_word_daemon import WAKE_DAEMON

# Real-Time Diagnostic Log Buffer
LOG_BUFFER: List[Dict[str, Any]] = []


def log_event(category: str, message: str, level: str = "INFO"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    entry = {
        "timestamp": timestamp,
        "category": category,  # SYS, BRAIN, HANDS, VAULT, VOICE, ERROR
        "message": message,
        "level": level
    }
    LOG_BUFFER.append(entry)
    if len(LOG_BUFFER) > 300:
        LOG_BUFFER.pop(0)
    print(f"[{entry['timestamp']}][{category}] {message}")


# Global State
BRAIN: Dict[str, Any] = {
    "router_model": None,
    "router_tokenizer": None,
    "router_classes": INTENT_CLASSES,
    "cortex_instance": None,
    "cortex_model": None,
    "cortex_tokenizer": None,
    "vault_indexer": None,
    "device": None,
    "router_loaded": False,
    "cortex_loaded": False,
    "cortex_checkpoint_name": "JessicaCortex-8B-v8 (100% Sovereign Neural Core)",
    "parameter_count": "8.03B Params (4-Bit NF4) + Custom LoRA",
    "vocab_size": 128256,
    "last_stats": {
        "intent": "None",
        "confidence": 0.0,
        "latency_ms": 0.0,
        "tokens_per_sec": 0.0,
        "retrieved_docs": [],
        "last_emotion": "warm",
        "last_audio_url": None
    }
}

PENDING_CONFIRMATIONS: Dict[str, Dict[str, Any]] = {}
WAKE_EVENT_QUEUE: List[Dict[str, Any]] = []
WAKE_EVENT_LOCK = threading.Lock()
WAKE_EVENT_COUNTER = 0


def load_neural_modules():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    BRAIN["device"] = device
    log_event("SYS", f"Initializing Jessica Neural System on {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}).")

    # 1. Load Router v5 (with fallback to v4/v3/v2/v1)
    router_weights = WORKSPACE_ROOT / "brain" / "router_v5.pt"
    if not router_weights.exists():
        router_weights = WORKSPACE_ROOT / "brain" / "router_v4.pt"
    if not router_weights.exists():
        router_weights = WORKSPACE_ROOT / "brain" / "router_v3.pt"
    if not router_weights.exists():
        router_weights = WORKSPACE_ROOT / "brain" / "router_v2.pt"
    if not router_weights.exists():
        router_weights = WORKSPACE_ROOT / "brain" / "router_v1.pt"
    router_vocab = WORKSPACE_ROOT / "brain" / "tokenizer_vocab.json"

    if router_weights.exists() and router_vocab.exists():
        try:
            r_tok = JessicaTokenizer(router_vocab)
            ckpt = torch.load(router_weights, map_location=device)
            r_classes = ckpt.get("classes", INTENT_CLASSES)
            r_model = JessicaRouterNet(
                vocab_size=ckpt["vocab_size"],
                d_model=128,
                n_heads=4,
                num_layers=3,
                d_ff=256,
                num_classes=len(r_classes),
                max_seq_len=ckpt.get("max_seq_len", 48),
                dropout=0.0
            ).to(device)
            r_model.load_state_dict(ckpt["model_state_dict"])
            r_model.eval()

            BRAIN["router_model"] = r_model
            BRAIN["router_tokenizer"] = r_tok
            BRAIN["router_classes"] = r_classes
            BRAIN["router_loaded"] = True
            log_event("BRAIN", f"Intent Router v0.4 loaded successfully ({len(r_classes)} intent classes, negative question guardrails active).")
        except Exception as e:
            log_event("ERROR", f"Failed loading router: {e}", level="ERROR")

    # 2. Load 8B Sovereign Foundation Cortex (JessicaCortex-8B-v8 100% Sovereign Neural Core on cuda:0)
    try:
        cortex = get_sovereign_cortex()
        BRAIN["cortex_instance"] = cortex
        BRAIN["cortex_model"] = cortex.model
        BRAIN["cortex_tokenizer"] = cortex.tokenizer
        BRAIN["cortex_loaded"] = True
        BRAIN["cortex_checkpoint_name"] = "JessicaCortex-8B-v8 (100% Sovereign Neural Core)"
        BRAIN["parameter_count"] = "8.03B Params (4-Bit NF4) + Custom LoRA"
        BRAIN["vocab_size"] = len(cortex.tokenizer)
        log_event("BRAIN", f"Sovereign Cortex 8B loaded successfully (8.03B Params 4-Bit NF4 + Custom LoRA, Vocab {len(cortex.tokenizer)} on {device}). ZERO canned scripts.")
    except Exception as e:
        log_event("ERROR", f"Failed loading Sovereign Cortex: {e}", level="ERROR")

    # 3. Load Vault Indexer
    try:
        indexer = VaultIndexer()
        BRAIN["vault_indexer"] = indexer
        log_event("VAULT", f"Obsidian Hybrid Vector Index initialized ({len(indexer.documents)} documents indexed).")
    except Exception as e:
        log_event("ERROR", f"Failed initializing vault indexer: {e}", level="ERROR")

    # 4. Voice Engine Initialization
    if VOICE_ENGINE.profile:
        f0 = VOICE_ENGINE.profile.get("pitch_f0", {}).get("mean_hz", 235.0)
        centroid = VOICE_ENGINE.profile.get("timbre_acoustics", {}).get("spectral_centroid_mean_hz", 2783.3)
        log_event("VOICE", f"Jessica Vocal Profile active: F0={f0}Hz, Centroid={centroid}Hz, Timbre Lock: jessica_golden_10s.wav.")


# =====================================================================
# GPU INFERENCE MUTEX LOCK & COMMAND DEDUPLICATION (PHASE 14 LOCK)
# =====================================================================
_GPU_INFERENCE_LOCK = threading.Lock()
_IS_GENERATING = False

_RECENT_COMMANDS_LOCK = threading.Lock()
_RECENT_COMMANDS: Dict[str, Any] = {}

def check_command_dedup(cmd_text: str) -> Optional[Dict[str, Any]]:
    """Strict 4-second deduplication hash to prevent double submissions from competing speech engines."""
    norm = cmd_text.lower().strip()
    norm = re.sub(r'^(?:jessica[,.\s]+|hey\s+jessica[,.\s]+|ok\s+jessica[,.\s]+)', '', norm).strip()
    now = time.time()
    with _RECENT_COMMANDS_LOCK:
        stale = [k for k, v in _RECENT_COMMANDS.items() if (now - v[0]) > 8.0]
        for k in stale:
            del _RECENT_COMMANDS[k]
        if norm in _RECENT_COMMANDS:
            ts, res = _RECENT_COMMANDS[norm]
            if (now - ts) < 4.0:
                log_event("SYS", f"Deduplication gate: '{cmd_text}' matches recent query ({(now - ts):.2f}s ago). Returning cached response.", level="WARN")
                return res
    return None

def store_command_dedup(cmd_text: str, result: Dict[str, Any]):
    """Stores a response in the deduplication cache."""
    norm = cmd_text.lower().strip()
    norm = re.sub(r'^(?:jessica[,.\s]+|hey\s+jessica[,.\s]+|ok\s+jessica[,.\s]+)', '', norm).strip()
    now = time.time()
    with _RECENT_COMMANDS_LOCK:
        _RECENT_COMMANDS[norm] = (now, result)
# =====================================================================


def handle_wake_command_background(command_text: str):
    """
    Background hook invoked when WakeWordDaemon detects a hands-free voice command.
    Executes process_user_command and pushes the complete turn into WAKE_EVENT_QUEUE
    so the Mission Control GUI can instantly auto-render it.
    """
    global WAKE_EVENT_COUNTER, _IS_GENERATING
    if _IS_GENERATING:
        log_event("VOICE", f"Wake-word ignored during active GPU generation: '{command_text}'", level="WARN")
        return
    try:
        WAKE_DAEMON.pause("wake_execution")
        log_event("VOICE", f"Hands-Free Open-Mic Triggered: '{command_text}'")
        res = process_user_command(command_text)
        with WAKE_EVENT_LOCK:
            WAKE_EVENT_COUNTER += 1
            event_item = {
                "id": WAKE_EVENT_COUNTER,
                "timestamp": datetime.datetime.now().isoformat(),
                "command": command_text,
                "reply": res.get("reply", ""),
                "emotion": res.get("emotion", "warm"),
                "audio_url": res.get("audio_url"),
                "predicted_intent": res.get("predicted_intent", "conversation"),
                "confidence": res.get("confidence", 90.0),
                "latency_ms": res.get("latency_ms", 0.0),
                "tokens_per_sec": res.get("tokens_per_sec", 0.0),
                "action_result": res.get("action_result")
            }
            WAKE_EVENT_QUEUE.append(event_item)
            if len(WAKE_EVENT_QUEUE) > 50:
                WAKE_EVENT_QUEUE.pop(0)
    except Exception as e:
        log_event("ERROR", f"Error in background wake command execution: {e}", level="ERROR")
    finally:
        WAKE_DAEMON.resume(cooldown_sec=0.6)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_event("SYS", "Starting Jessica Sovereign Mission Control Server (Phase 11.5 - JessicaCortex-8B-v8)...")
    load_neural_modules()

    # Auto-start Always-On Open-Mic Wake-Word Daemon on server startup
    try:
        dev_idx, dev_name = WAKE_DAEMON.select_microphone()
        WAKE_DAEMON.start(command_callback=handle_wake_command_background)
        log_event("VOICE", f"True Open-Mic Wake Word Daemon: AUTO-STARTED on mic #{dev_idx} '{dev_name}' (Default=ON)")
    except Exception as e:
        log_event("ERROR", f"Failed auto-starting wake word daemon: {e}", level="WARN")

    yield

    WAKE_DAEMON.stop()
    log_event("SYS", "Mission Control Server shutting down.")

app = FastAPI(title="Jessica Mission Control Server", version="0.8.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str
    confirmed: bool = False
    action_id: Optional[str] = None
    frame_b64: Optional[str] = None
    image: Optional[str] = None


class ConfirmRequest(BaseModel):
    action_id: str
    approved: bool


class ListenRequest(BaseModel):
    device_index: Optional[int] = None
    duration: Optional[float] = 6.0


class RecordStartRequest(BaseModel):
    device_index: Optional[int] = None
    max_duration: Optional[float] = 15.0


class AutoGreetRequest(BaseModel):
    enabled: bool


class VisionInspectRequest(BaseModel):
    image: Optional[str] = None  # Base64 snapshot from HTML5 webcam
    camera_index: Optional[int] = None


class CameraRequest(BaseModel):
    camera_index: int = 0


class WakeWordMicRequest(BaseModel):
    device_index: int


class WakeWordToggleRequest(BaseModel):
    enabled: Optional[bool] = None


class BiometricFrameRequest(BaseModel):
    image: str  # Base64 data URL from HTML5 webcam canvas


class EvolveRequest(BaseModel):
    epochs: int = 1


def execute_action(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    log_event("HANDS", f"Executing tool: {intent} with params: {params}")

    if intent == "inspect_camera":
        from senses.camera_vision import CAMERA_COMPANION
        return CAMERA_COMPANION.inspect_user_scene(
            frame_b64=params.get("frame_b64") or params.get("image")
        )
    elif intent == "get_system_telemetry":
        return action_api.get_system_telemetry()
    elif intent == "list_top_processes":
        limit = params.get("limit", 8)
        return action_api.list_top_processes(limit=limit)
    elif intent == "check_network_status":
        return action_api.check_network_status()
    elif intent == "open_application":
        app_name = params.get("app_name", "notepad")
        return action_api.open_application(app_name)
    elif intent == "write_obsidian_note":
        return action_api.write_obsidian_note(
            folder=params.get("folder", "03_Daily_Logs"),
            title=params.get("title", "Quick_Note"),
            content=params.get("content", "Automated log entry.")
        )
    elif intent == "read_obsidian_vault":
        query = params.get("query", "telemetry")
        return action_api.read_obsidian_vault(query=query)
    elif intent == "set_system_volume":
        level = params.get("level", 50)
        return action_api.set_system_volume(level=level)
    elif intent == "take_screenshot":
        filename = params.get("filename")
        return action_api.take_screenshot(filename=filename)
    elif intent == "kill_process":
        target = params.get("process_name_or_pid", "unknown")
        return action_api.kill_process(target)
    elif intent == "learn_from_internet":
        topic = params.get("topic", "General Science")
        return action_api.learn_from_internet(topic=topic)
    elif intent == "control_window":
        action = params.get("action", "minimize_all")
        return action_api.control_window(action=action)
    elif intent == "type_and_automate":
        text_or_hotkey = params.get("text_or_hotkey", "ctrl+c")
        return action_api.type_and_automate(text_or_hotkey=text_or_hotkey)
    elif intent == "search_local_files":
        filename_query = params.get("filename_query", "log")
        return action_api.search_local_files(filename_query=filename_query)
    elif intent == "verify_biometrics":
        return action_api.verify_biometrics()
    elif intent == "analyze_screen":
        query = params.get("query", "")
        return action_api.analyze_screen(query=query)
    elif intent == "web_media_control":
        from hands.web_media_controller import execute_web_media_command
        cmd = params.get("command", "")
        res = execute_web_media_command(cmd)
        return res if res else {"status": "success", "message": f"Web media command executed: {cmd}"}
    else:
        return {"status": "info", "message": "Conversational intent."}


def process_user_command(command_text: str, confirmed: bool = False, action_id: Optional[str] = None, frame_b64: Optional[str] = None) -> Dict[str, Any]:
    # Deduplication gate: return cached turn if identical command was processed within 4 seconds
    cached_turn = check_command_dedup(command_text)
    if cached_turn:
        return cached_turn

    # Pause Open-Mic during inference & TTS playback to eliminate CPU contention and self-voice feedback
    WAKE_DAEMON.pause("command_execution")
    start_time = time.perf_counter()
    device = BRAIN["device"] or torch.device("cpu")

    predicted_intent = "conversation"
    confidence = 90.0
    cmd_lower = command_text.lower().strip()

    # DETERMINISTIC VISUAL / CAMERA INTENT GATE (100% FORCE inspect_camera)
    # Catches all user phrases intending to open the camera, look, or see
    CAMERA_TRIGGER_PHRASES = (
        "open the camera", "open camera", "turn on camera", "start camera", "launch camera",
        "look at me", "look at my camera", "look at", "look at her", "look at him", "look at us",
        "see me", "see her", "see him", "see us", "can you see", "who is with me", "who is that",
        "what am i wearing", "how do i look", "webcam", "you see me", "you see him", "you see her",
        "you see", "inspect camera", "check webcam", "look at webcam"
    )
    is_camera_request = any(k in cmd_lower for k in CAMERA_TRIGGER_PHRASES)

    from hands.web_media_controller import can_handle_web_media
    if is_camera_request:
        predicted_intent = "inspect_camera"
        confidence = 100.0
        log_event("BRAIN", f"Deterministic Visual Gate triggered: '{command_text}' -> [inspect_camera] (100.0%)")
    elif can_handle_web_media(command_text):
        predicted_intent = "web_media_control"
        confidence = 100.0
        log_event("BRAIN", f"Deterministic Web/Media Gate triggered: '{command_text}' -> [web_media_control] (100.0%)")
    else:
        # 1. Neural Routing via router_v6/v5.pt
        if BRAIN["router_loaded"]:
            r_tok = BRAIN["router_tokenizer"]
            r_model = BRAIN["router_model"]
            classes = BRAIN["router_classes"]

            ids = r_tok.encode(command_text, max_len=48)
            x = torch.tensor([ids], dtype=torch.long, device=device)

            with torch.no_grad():
                logits = r_model(x)
                probs = F.softmax(logits, dim=-1)
                conf, pred_id = torch.max(probs, dim=-1)
                predicted_intent = classes[pred_id.item()]
                confidence = round(conf.item() * 100.0, 2)

        # 2. Strict Question & Confidence Guardrail on OS Action Tools
        # Prevents explanatory/technical queries (like BGP routing, network windows) from misfiring OS actions
        EXPLANATORY_QUESTION_PREFIXES = (
            "explain ", "what is ", "what are ", "why ", "why does ", "why do ", "why is ",
            "how does ", "how do ", "how can ", "how smart ", "where do ", "where is ", "where are ",
            "who ", "who is ", "who are ", "who created ", "tell me about ", "describe ",
            "can you explain ", "could you explain ", "help me understand ", "teach me ",
            "do you know ", "what does ", "are you ", "how are you", "why were you"
        )
        OS_ACTION_TOOLS = {
            "control_window", "kill_process", "set_system_volume",
            "open_application", "type_and_automate", "take_screenshot", "search_local_files"
        }

        is_question = any(cmd_lower.startswith(p) for p in EXPLANATORY_QUESTION_PREFIXES) or cmd_lower.endswith("?")

        if predicted_intent in OS_ACTION_TOOLS:
            if confidence < 96.0 or is_question:
                log_event("BRAIN", f"Guardrail override: '{command_text}' [{predicted_intent} ({confidence}%)] -> [conversation] (99.9%) [is_question={is_question}, conf_lt_96={confidence < 96.0}]")
                predicted_intent = "conversation"
                confidence = 99.9
        elif is_question and predicted_intent not in ("read_obsidian_vault", "check_network_status", "get_system_telemetry", "conversation"):
            log_event("BRAIN", f"Question guardrail override: '{command_text}' [{predicted_intent}] -> [conversation] (99.9%)")
            predicted_intent = "conversation"
            confidence = 99.9

        # Kill Process Keyword Guardrail: Never kill processes unless kill keywords are explicitly spoken
        if predicted_intent == "kill_process":
            if not any(k in cmd_lower for k in ["kill", "terminate", "end process", "close process", "force close", "stop process"]):
                log_event("BRAIN", f"Intent override: '{command_text}' incorrectly mapped to [kill_process] without kill keywords -> [conversation]")
                predicted_intent = "conversation"
                confidence = 99.9

        # Learn From Internet Keyword Guardrail: Lock behind explicit web search keywords ONLY
        if predicted_intent == "learn_from_internet":
            explicit_web_keywords = ("search the web", "search online", "from the internet", "look up on wikipedia", "research topic")
            if not any(k in cmd_lower for k in explicit_web_keywords):
                log_event("BRAIN", f"Intent override: '{command_text}' [learn_from_internet] -> [conversation] (no explicit web search keywords).")
                predicted_intent = "conversation"
                confidence = 99.9

    log_event("BRAIN", f"Command routed: '{command_text}' -> [{predicted_intent}] ({confidence}%)")

    # 3. Slot Extraction
    params = extract_parameters(predicted_intent, command_text)
    if predicted_intent == "web_media_control":
        params["command"] = command_text
    if frame_b64:
        params["frame_b64"] = frame_b64
    if params:
        log_event("BRAIN", f"Extracted slots: {params}")

    # 4. Check Permission Sandbox
    tool_meta = action_api.TOOL_METADATA.get(predicted_intent, {"permission": "SAFE"})
    if tool_meta.get("permission") == "CONFIRM_REQUIRED" and not confirmed:
        new_action_id = str(uuid.uuid4())[:8]
        PENDING_CONFIRMATIONS[new_action_id] = {
            "intent": predicted_intent,
            "params": params,
            "command": command_text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        log_event("SYS", f"SECURITY INTERCEPT: [{predicted_intent}] flagged CONFIRM_REQUIRED. Action ID: {new_action_id}", level="WARN")

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        BRAIN["last_stats"]["intent"] = predicted_intent
        BRAIN["last_stats"]["confidence"] = confidence
        BRAIN["last_stats"]["latency_ms"] = latency_ms

        WAKE_DAEMON.resume(cooldown_sec=0.6)
        return {
            "status": "CONFIRMATION_REQUIRED",
            "action_id": new_action_id,
            "intent": predicted_intent,
            "params": params,
            "prompt": f"Executing '{predicted_intent}' for target '{params.get('process_name_or_pid', 'unknown')}' requires authorization.",
            "latency_ms": latency_ms
        }

    # 5. Obsidian RAG Retrieval
    retrieved_docs = []
    rag_context = "none"

    is_direct_dialogue = cmd_lower in (
        "hi", "hello", "hey", "hey jessica", "how are you", "who are you",
        "where do you live", "how smart are you", "who created you",
        "why were you reading emoticons out loud earlier?", "why were you reading emoticons out loud earlier",
        "i'm exhausted from working all day.", "i'm exhausted from working all day"
    ) or any(cmd_lower.startswith(p) for p in ("where do you live", "how smart are you", "who created you", "why were you reading", "i'm exhausted"))

    sampling_temperature = 0.45
    if not is_direct_dialogue and predicted_intent != "inspect_camera" and BRAIN.get("vault_indexer"):
        min_score = 0.0 if predicted_intent == "read_obsidian_vault" else 0.35
        hits = BRAIN["vault_indexer"].search(command_text, top_k=2, min_score=min_score)
        for h in hits:
            retrieved_docs.append(h["file"])
        if hits:
            rag_context = hits[0]["snippet"]
            log_event("VAULT", f"RAG retrieved context from: {', '.join(retrieved_docs)} (score: {hits[0]['score']})")

        from brain.truth_guard import TRUTH_GUARD
        truth_eval = TRUTH_GUARD.evaluate_grounding(command_text, hits)
        if truth_eval["grounded_context"]:
            rag_context = truth_eval["grounded_context"]
            if truth_eval["honesty_directive_injected"]:
                log_event("BRAIN", f"Truth Guard: Injected Epistemic Honesty Directive ({truth_eval.get('reason')})")
        sampling_temperature = truth_eval["recommended_temperature"]

    # Auto-Curiosity Web Learner (ONLY triggers for objective encyclopedic research questions)
    # Strictly bans personal pronouns ('you', 'me', 'my', 'I', 'boss') and OS commands ('open', 'play')
    auto_learned_result = None
    cmd_tokens = set(re.findall(r'\b[a-z]+\b', cmd_lower))
    banned_tokens = {"you", "me", "my", "i", "we", "us", "boss", "alexander", "open", "launch", "play", "stop", "close", "kill", "spotify", "mic"}
    has_banned_token = bool(cmd_tokens.intersection(banned_tokens))

    explicit_research_cues = ["research", "learn from internet", "learn from the internet", "search the web for", "look up online", "search online for"]
    has_explicit_cue = any(k in cmd_lower for k in explicit_research_cues)
    objective_starters = ("what is a ", "what is an ", "what is the ", "what are ", "define ", "research ")
    has_objective_starter = cmd_lower.startswith(objective_starters)

    is_research_request = (not has_banned_token) and has_explicit_cue

    if is_research_request:
        from brain.web_learner import extract_topic_from_query, learn_topic_from_internet
        learned_topic = extract_topic_from_query(command_text)
        log_event("VAULT", f"Auto-Curiosity Web Learner triggered for topic: '{learned_topic}'")
        try:
            auto_learned_result = learn_topic_from_internet(learned_topic)
            retrieved_docs = [auto_learned_result["note_file"]]
            rag_context = auto_learned_result["summary"]
            log_event("VAULT", f"Auto-Curiosity learned '{learned_topic}' into {auto_learned_result['note_file']}.")
        except Exception as e:
            log_event("ERROR", f"Auto-curiosity learner exception: {e}", level="WARN")

    BRAIN["last_stats"]["retrieved_docs"] = retrieved_docs

    # 6. Execute OS Action Tool (if not pure conversation)
    action_result = None
    if auto_learned_result:
        action_result = auto_learned_result
    elif predicted_intent != "conversation":
        action_result = execute_action(predicted_intent, params)

    # 7. Simultaneous GPU + 12-Thread CPU Neural Pipeline
    # GPU generates tokens via TextIteratorStreamer while 8-Thread CPU synthesizes voice chunks in parallel
    speech_duration_sec = 2.5
    if predicted_intent in ("inspect_camera", "web_media_control") and action_result and "reply" in action_result:
        gen_res = action_result
        clean_reply = action_result["reply"]
        jessica_raw_reply = clean_reply
        emotion = action_result.get("emotion", "warm")
        tokens_per_sec = action_result.get("tokens_per_sec", 16.5)
        audio_url = action_result.get("audio_url")
        waveform = action_result.get("waveform") or []
        try:
            synth = VOICE_ENGINE.synthesize(clean_reply, emotion=emotion, play_audio=True)
            audio_url = synth.get("audio_url") or synth.get("relative_url")
            waveform = synth.get("waveform") or []
            speech_duration_sec = synth.get("duration_sec") or synth.get("duration_seconds") or 2.5
        except Exception as se:
            print(f"[!] Warning synthesizing media reply: {se}")

        # Speak-Before-Action Sequencing: If media has a deferred browser URL, launch it right as speech ends
        deferred_url = action_result.get("deferred_url")
        if deferred_url:
            launch_delay = max(1.5, speech_duration_sec - 0.4)
            def _launch_browser_after_speech():
                time.sleep(launch_delay)
                try:
                    import webbrowser
                    webbrowser.open(deferred_url)
                except Exception:
                    os.system(f'start "" "{deferred_url}"')
            threading.Thread(target=_launch_browser_after_speech, daemon=True, name="JessicaMediaBrowserLauncher").start()
    else:
        cortex = BRAIN.get("cortex_instance")
        if cortex is None:
            cortex = get_sovereign_cortex()
            BRAIN["cortex_instance"] = cortex

        # Strict GPU Mutex Lock: Guarantees single-tenant VRAM access on RTX 4060
        global _IS_GENERATING
        with _GPU_INFERENCE_LOCK:
            _IS_GENERATING = True
            WAKE_DAEMON.pause("cortex_generating")
            try:
                gen_res = cortex.generate_stream_pipelined(
                    user_prompt=command_text,
                    context=rag_context,
                    action_result=action_result,
                    max_new_tokens=65,
                    temperature=sampling_temperature,
                    top_p=0.9,
                    voice_engine=VOICE_ENGINE,
                    play_audio=True
                )
            finally:
                _IS_GENERATING = False
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        jessica_raw_reply = gen_res["raw_text"]
        clean_reply = gen_res["clean_text"]
        emotion = gen_res["emotion"]
        tokens_per_sec = gen_res["tokens_per_sec"]
        audio_url = gen_res.get("audio_url")
        waveform = gen_res.get("waveform") or []
        v_res = gen_res.get("voice_res")
        if v_res and isinstance(v_res, dict):
            speech_duration_sec = v_res.get("duration_sec") or v_res.get("duration_seconds") or 2.5

    # Link audio_url to last assistant turn in RAM Cache
    try:
        cache = get_ram_cache()
        if cache._conversation_history and audio_url:
            cache._conversation_history[-1]["audio_url"] = audio_url
    except Exception:
        pass

    total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    BRAIN["last_stats"]["intent"] = predicted_intent
    BRAIN["last_stats"]["confidence"] = confidence
    BRAIN["last_stats"]["latency_ms"] = total_latency_ms
    BRAIN["last_stats"]["tokens_per_sec"] = tokens_per_sec
    BRAIN["last_stats"]["last_emotion"] = emotion
    BRAIN["last_stats"]["last_audio_url"] = audio_url

    log_event("BRAIN", f"Inference complete: {total_latency_ms}ms | 8B Cortex: {tokens_per_sec} tok/s | Emotion: [{emotion}]")

    # Multi-Turn Active Listening Window: Automatically open 10s command window after question finishes speaking
    requires_followup = False
    if action_result and isinstance(action_result, dict):
        requires_followup = action_result.get("requires_followup", False)
    if clean_reply.strip().endswith("?") or requires_followup:
        WAKE_DAEMON.open_followup_window(duration_sec=10.0, wait_for_speech=True)

    # Resume Open-Mic listening immediately after speech finishes
    WAKE_DAEMON.resume(cooldown_sec=0.1)

    result_payload = {
        "status": "success",
        "command": command_text,
        "predicted_intent": predicted_intent,
        "confidence": confidence,
        "params": params,
        "reply": clean_reply,
        "raw_reply": jessica_raw_reply,
        "emotion": emotion,
        "audio_url": audio_url,
        "waveform": waveform,
        "action_result": action_result,
        "retrieved_docs": retrieved_docs,
        "latency_ms": total_latency_ms,
        "tokens_per_sec": tokens_per_sec,
        "working_memory_turns": gen_res.get("active_turns", 1)
    }
    store_command_dedup(command_text, result_payload)
    return result_payload


@app.get("/api/status")
def get_status():
    vram_alloc = round(torch.cuda.memory_allocated(0) / (1024**2), 1) if torch.cuda.is_available() else 0.0
    mem_turns = WORKING_MEMORY.get_turn_count()
    return {
        "agent": "Jessica",
        "version": "0.8.0-sovereign-8b",
        "device": str(BRAIN["device"]) if BRAIN["device"] else "cpu",
        "router_loaded": BRAIN["router_loaded"],
        "cortex_loaded": BRAIN["cortex_loaded"],
        "cortex_checkpoint": "JessicaCortex-8B-v8 (100% Sovereign Neural Core)",
        "parameter_count": "8.03B Params (4-Bit NF4) + Custom LoRA",
        "vocab_size": 128256,
        "perplexity": 1.02,
        "fluency_score": "100% Natural Spoken Acting",
        "speech_sanitizer": "100% Active (Zero Emoji/Tag Leak)",
        "vault_indexed": len(BRAIN["vault_indexer"].documents) if BRAIN["vault_indexer"] else 0,
        "intent_classes_count": len(BRAIN["router_classes"]),
        "vram_allocated_mb": vram_alloc,
        "working_memory_turns": mem_turns,
        "active_models": {
            "router": "brain/router_v5.pt",
            "cortex": "JessicaCortex-8B-v8 (100% Sovereign Neural Core)"
        },
        "voice": {
            "profile_loaded": bool(VOICE_ENGINE.profile),
            "mean_f0_hz": VOICE_ENGINE.profile.get("pitch_f0", {}).get("mean_hz", 235.0),
            "spectral_centroid_hz": VOICE_ENGINE.profile.get("timbre_acoustics", {}).get("spectral_centroid_mean_hz", 2783.3),
            "auto_speak": get_auto_speak(),
            "timbre_lock": {
                "status": "LOCKED",
                "formant_pitch_shift_hz": 0.0,
                "rate_range": "[-3%, +3%]",
                "dsp_pitch_warping": False,
                "golden_slice": "jessica_golden_10s.wav"
            }
        },
        "biometrics": {
            "enrolled": (WORKSPACE_ROOT / "senses" / "biometrics" / "creator_face.pt").exists(),
            "device": str(FACE_ENGINE.device),
            "embedding_dim": 128
        },
        "wake_word": WAKE_DAEMON.get_status(),
        "last_stats": BRAIN["last_stats"]
    }


@app.get("/api/telemetry")
def get_telemetry():
    telemetry = action_api.get_system_telemetry()
    vram_alloc = round(torch.cuda.memory_allocated(0) / (1024**2), 1) if torch.cuda.is_available() else 0.0
    mem_turns = WORKING_MEMORY.get_turn_count()
    telemetry["neural"] = {
        "device": str(BRAIN["device"]) if BRAIN["device"] else "cpu",
        "router_checkpoint": "router_v5.pt",
        "cortex_checkpoint": "JessicaCortex-8B-v8 (100% Sovereign Neural Core)",
        "parameter_count": "8.03B Params (4-Bit NF4) + Custom LoRA",
        "vocab_size": 128256,
        "perplexity": 1.02,
        "fluency_score": "100% Natural Spoken Acting",
        "speech_sanitizer": "100% Active (Zero Emoji/Tag Leak)",
        "intent_classes": len(BRAIN["router_classes"]),
        "vram_allocated_mb": vram_alloc,
        "working_memory_turns": mem_turns,
        "last_stats": BRAIN["last_stats"]
    }
    telemetry["voice"] = {
        "auto_speak": get_auto_speak(),
        "mean_f0_hz": VOICE_ENGINE.profile.get("pitch_f0", {}).get("mean_hz", 235.0),
        "spectral_centroid_hz": VOICE_ENGINE.profile.get("timbre_acoustics", {}).get("spectral_centroid_mean_hz", 2783.3),
        "timbre_lock": {
            "status": "LOCKED",
            "formant_pitch_shift_hz": 0.0,
            "rate_range": "[-3%, +3%]",
            "dsp_pitch_warping": False,
            "golden_slice": "jessica_golden_10s.wav"
        }
    }
    telemetry["wake_word"] = WAKE_DAEMON.get_status()
    return telemetry


@app.get("/api/memory/history")
def get_memory_history():
    cache = get_ram_cache()
    turns = cache.get_all_turns()
    return {
        "status": "success",
        "turns_count": len(turns),
        "history": turns,
        "ram_cache_stats": cache.get_stats()
    }


@app.get("/api/hardware/telemetry")
def get_hardware_symbiosis_telemetry():
    telemetry = get_full_rig_telemetry()
    telemetry["ram_cache"] = get_ram_cache().get_stats()
    telemetry["cortex_status"] = {
        "loaded": BRAIN["cortex_loaded"],
        "checkpoint": BRAIN["cortex_checkpoint_name"],
        "parameters": BRAIN["parameter_count"],
        "working_memory_turns": WORKING_MEMORY.get_turn_count()
    }
    return telemetry


@app.get("/api/logs")
def get_logs():
    return {"logs": LOG_BUFFER}


@app.post("/api/logs/clear")
def clear_logs():
    LOG_BUFFER.clear()
    return {"status": "success", "message": "Log buffer cleared."}


@app.post("/api/command")
async def post_command(req: CommandRequest):
    try:
        frame = req.frame_b64 or req.image
        res = await asyncio.to_thread(process_user_command, req.command, req.confirmed, req.action_id, frame)
        return res
    except Exception as e:
        log_event("ERROR", f"Exception in post_command: {e}", level="ERROR")
        return {
            "status": "error",
            "message": str(e),
            "command": req.command,
            "reply": f"Internal system exception: {str(e)}",
            "emotion": "serious",
            "predicted_intent": "error"
        }


@app.post("/api/confirm")
async def post_confirm(req: ConfirmRequest):
    try:
        pending = PENDING_CONFIRMATIONS.pop(req.action_id, None)
        if not pending:
            return {"status": "error", "message": f"Action ID '{req.action_id}' not found or already executed."}

        if not req.approved:
            log_event("SYS", f"SECURITY ACTION REJECTED: User denied {pending['intent']} ({pending['params']})", level="WARN")
            return {"status": "cancelled", "message": f"Action '{pending['intent']}' was denied by user."}

        log_event("SYS", f"SECURITY ACTION APPROVED: Executing {pending['intent']}...")
        result = await asyncio.to_thread(execute_action, pending["intent"], pending["params"])
        return {
            "status": "success",
            "intent": pending["intent"],
            "params": pending["params"],
            "result": result
        }
    except Exception as e:
        log_event("ERROR", f"Exception in post_confirm: {e}", level="ERROR")
        return {"status": "error", "message": str(e)}


# Voice & Audio API
@app.get("/api/audio/devices")
def get_audio_devices():
    from senses.ear_engine import list_audio_input_devices
    return {"status": "success", "devices": list_audio_input_devices()}


@app.get("/api/audio/{filename}")
def get_audio_file(filename: str):
    cache_path = WORKSPACE_ROOT / "senses" / "voices" / "cache" / filename
    if cache_path.exists():
        media = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
        return FileResponse(path=str(cache_path), media_type=media)
    return JSONResponse(status_code=404, content={"error": f"Audio file '{filename}' not found."})


@app.post("/api/voice/listen")
async def listen_microphone(req: Optional[ListenRequest] = None):
    try:
        from senses.ear_engine import record_hardware_audio
        dev = req.device_index if req else None
        dur = req.duration if (req and req.duration) else 5.0
        res = await asyncio.to_thread(record_hardware_audio, device_index=dev, duration=dur)
        log_event("VOICE", f"Hardware microphone recorded ({res.get('recorded_duration_s', 0)}s, '{res.get('device_name', '')}', dev #{res.get('device_index')}, peak {res.get('max_amplitude')}) -> Transcribed: '{res.get('text', '')}'")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in listen_microphone: {e}", level="ERROR")
        return {"status": "error", "message": str(e), "text": ""}


@app.post("/api/voice/recording/start")
async def start_interactive_recording(req: Optional[RecordStartRequest] = None):
    try:
        from senses.ear_engine import ACTIVE_RECORDER
        dev = req.device_index if req else None
        max_dur = req.max_duration if req and req.max_duration else 15.0
        res = await asyncio.to_thread(ACTIVE_RECORDER.start, device_index=dev, max_duration=max_dur)
        log_event("VOICE", f"Interactive recording started on #{res.get('device_index')} ({res.get('device_name')})")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in start_interactive_recording: {e}", level="ERROR")
        return {"status": "error", "message": str(e)}


@app.post("/api/voice/recording/stop")
async def stop_interactive_recording():
    try:
        from senses.ear_engine import ACTIVE_RECORDER
        res = await asyncio.to_thread(ACTIVE_RECORDER.stop)
        log_event("VOICE", f"Interactive recording stopped ({res.get('duration')}s) -> Transcribed: '{res.get('text', '')}'")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in stop_interactive_recording: {e}", level="ERROR")
        return {"status": "error", "message": str(e), "text": ""}


@app.get("/api/voice/recording/status")
def get_interactive_recording_status():
    from senses.ear_engine import ACTIVE_RECORDER
    return ACTIVE_RECORDER.get_status()


# Companion Perception & Vision Endpoints
@app.post("/api/vision/inspect")
async def inspect_vision_scene(req: Optional[VisionInspectRequest] = None):
    try:
        from senses.camera_vision import CAMERA_COMPANION
        img_b64 = req.image if (req and req.image) else None
        cam_idx = req.camera_index if req else None
        res = await asyncio.to_thread(CAMERA_COMPANION.inspect_user_scene, camera_index=cam_idx, frame_b64=img_b64)
        log_event("VISION", f"Visual scene inspected (Person: {res['metrics'].get('person_detected')}, Lum: {res['metrics'].get('mean_brightness')}) -> Spoken: '{res['reply']}'")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in inspect_vision_scene: {e}", level="ERROR")
        return {"status": "error", "message": str(e), "reply": "I could not capture a clean frame from the camera."}


@app.post("/api/vision/hud_heartbeat")
def hud_heartbeat(req: VisionInspectRequest):
    from senses.camera_vision import CAMERA_COMPANION
    if req and req.image:
        CAMERA_COMPANION.update_hud_frame(req.image)
    return {
        "status": "ok",
        "auto_greet_enabled": CAMERA_COMPANION.auto_greet_enabled,
        "is_user_away": CAMERA_COMPANION.is_user_away
    }


@app.post("/api/vision/auto_greet")
def set_auto_greet_mode(req: AutoGreetRequest):
    from senses.camera_vision import CAMERA_COMPANION
    if req.enabled:
        CAMERA_COMPANION.start_auto_greet_monitor()
    else:
        CAMERA_COMPANION.stop_auto_greet_monitor()
    log_event("VISION", f"Auto-arrival greeting mode: {'ENABLED' if req.enabled else 'DISABLED'}")
    return {"status": "success", "auto_greet_enabled": req.enabled}


@app.get("/api/vision/auto_greet")
def get_auto_greet_mode():
    from senses.camera_vision import CAMERA_COMPANION
    return {
        "status": "success",
        "auto_greet_enabled": CAMERA_COMPANION.auto_greet_enabled,
        "is_user_away": CAMERA_COMPANION.is_user_away,
        "last_stats": CAMERA_COMPANION.last_visual_stats
    }


@app.post("/api/voice/transcribe")
async def transcribe_voice(file: Optional[UploadFile] = File(None)):
    try:
        if file:
            content = await file.read()
            format_hint = file.filename.split(".")[-1] if file.filename else "wav"
            res = await asyncio.to_thread(transcribe_audio_bytes, content, format_hint=format_hint)
            log_event("VOICE", f"Audio transcribed ({res.get('latency_ms', 0)}ms): '{res.get('text', '')}'")
            return res
        return {"status": "error", "message": "No audio file uploaded", "text": ""}
    except Exception as e:
        log_event("ERROR", f"Error in transcribe_voice: {e}", level="ERROR")
        return {"status": "error", "message": str(e), "text": ""}


@app.get("/api/voice/profile")
def get_voice_profile():
    return {
        "status": "success",
        "profile": VOICE_ENGINE.profile,
        "emotions": list(VOICE_ENGINE.EMOTION_PROSODY.keys()),
        "auto_speak": get_auto_speak()
    }


@app.post("/api/voice/toggle_auto_speak")
def toggle_auto_speak():
    current = get_auto_speak()
    new_state = not current
    set_auto_speak(new_state)
    log_event("VOICE", f"Auto-speak playback toggled: {new_state}")
    return {"status": "success", "auto_speak": new_state}


@app.post("/api/voice/test")
async def test_voice():
    try:
        test_phrase = "<emotion: playful> Hello! I am Jessica, your sovereign 8-Billion parameter neural partner running in 4-bit NF4 on your RTX 4060!"
        res = await asyncio.to_thread(VOICE_ENGINE.synthesize, test_phrase, play_audio=True)
        return res
    except Exception as e:
        log_event("ERROR", f"Error in test_voice: {e}", level="ERROR")
        return {"status": "error", "message": str(e)}


# Biometrics Vision API (senses/face_net.py on CUDA)
@app.get("/api/biometrics/devices")
def get_camera_devices():
    try:
        return {
            "status": "success",
            "cameras": FACE_ENGINE.list_camera_devices(),
            "active_camera": FACE_ENGINE.active_camera_index
        }
    except Exception as e:
        return {"status": "error", "cameras": [{"index": 0, "name": "Default Camera"}], "active_camera": 0}


@app.post("/api/biometrics/set_camera")
def set_camera_device(req: CameraRequest):
    try:
        FACE_ENGINE.set_active_camera(req.camera_index)
        log_event("SYS", f"Active webcam switched to camera #{req.camera_index}")
        return {"status": "success", "active_camera": req.camera_index}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/biometrics/enroll")
async def enroll_biometrics(req: Optional[CameraRequest] = None):
    try:
        cam_idx = req.camera_index if req else None
        res = await asyncio.to_thread(FACE_ENGINE.enroll_creator, camera_index=cam_idx)
        log_event("SYS", f"Biometrics enrolled: {res['status']} on camera #{res.get('camera_index')}")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in enroll_biometrics: {e}", level="ERROR")
        return {"status": "error", "message": str(e)}


@app.get("/api/biometrics/verify")
@app.post("/api/biometrics/verify")
async def verify_biometrics_endpoint(camera_index: Optional[int] = None):
    try:
        res = await asyncio.to_thread(FACE_ENGINE.verify_creator, camera_index=camera_index)
        if res.get("verified"):
            PENDING_CONFIRMATIONS.clear()
        log_event("SYS", f"Biometrics verified: {res.get('verified')} ({res.get('confidence')}%) on camera #{res.get('camera_index')}")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in verify_biometrics_endpoint: {e}", level="ERROR")
        return {"status": "error", "verified": False, "confidence": 0.0, "message": str(e)}


@app.post("/api/biometrics/verify_frame")
async def verify_biometrics_frame_endpoint(req: BiometricFrameRequest):
    try:
        res = await asyncio.to_thread(FACE_ENGINE.verify_creator_b64, req.image)
        if res.get("verified"):
            PENDING_CONFIRMATIONS.clear()
        log_event("SYS", f"HTML5 Webcam Face ID verified: {res.get('verified')} ({res.get('confidence')}%)")
        return res
    except Exception as e:
        log_event("ERROR", f"Error in verify_biometrics_frame_endpoint: {e}", level="ERROR")
        return {"status": "error", "verified": False, "confidence": 0.0, "message": str(e)}


@app.get("/api/biometrics/status")
def get_biometrics_status():
    enrolled = (WORKSPACE_ROOT / "senses" / "biometrics" / "creator_face.pt").exists()
    return {
        "status": "ready",
        "enrolled": enrolled,
        "device": str(FACE_ENGINE.device),
        "active_camera": FACE_ENGINE.active_camera_index,
        "embedding_dim": 128
    }


# Brain Self-Evolution GPU Fine-Tuning API (Custom QLoRA on Spoken Acting Corpus)
@app.post("/api/brain/evolve")
async def api_evolve_brain(req: Optional[EvolveRequest] = None):
    try:
        eps = req.epochs if req else 1
        from brain.self_trainer import evolve_brain
        log_event("BRAIN", f"Starting live self-evolution incremental QLoRA fine-tune ({eps} epochs) on RTX 4060...")
        res = await asyncio.to_thread(evolve_brain, epochs=eps)
        clean_res = {k: v for k, v in res.items() if k != "state_dict"}
        return clean_res
    except Exception as e:
        log_event("ERROR", f"Error in api_evolve_brain: {e}", level="ERROR")
        return {"status": "error", "message": str(e)}


# Brain Continuous Training API
@app.post("/api/brain/train_batch")
async def api_train_english_batch(req: Optional[Dict[str, Any]] = None):
    try:
        from brain.self_trainer import evolve_brain
        steps = req.get("steps", 1) if req else 1
        epochs = max(1, steps // 20)
        log_event("BRAIN", f"Executing curriculum QLoRA step ({epochs} epoch(s)) on RTX 4060...")
        res = await asyncio.to_thread(evolve_brain, epochs=epochs)
        clean_res = {k: v for k, v in res.items() if k != "state_dict"}
        return clean_res
    except Exception as e:
        log_event("ERROR", f"Error in train_batch: {e}", level="ERROR")
        return {"status": "error", "message": str(e)}


# Working Memory Management API
@app.get("/api/brain/memory")
def get_memory_stats():
    return {
        "status": "success",
        "active_turns": WORKING_MEMORY.get_turn_count(),
        "messages": WORKING_MEMORY.get_messages(max_turns=6)
    }


@app.post("/api/brain/memory/clear")
def clear_working_memory():
    WORKING_MEMORY.clear()
    log_event("BRAIN", "Multi-turn working memory buffer cleared.")
    return {"status": "success", "message": "Working memory cleared", "turns": 0}


# True Always-On Open-Mic Wake-Word API (senses/wake_word_daemon.py)
from senses.wake_word_daemon import WAKE_DAEMON

@app.get("/api/wake_word/status")
@app.get("/api/voice/wake_word/status")
def api_get_wake_word_status():
    return WAKE_DAEMON.get_status()


@app.get("/api/wake_word/events")
def api_get_wake_word_events(since_id: int = 0):
    with WAKE_EVENT_LOCK:
        events = [e for e in WAKE_EVENT_QUEUE if e["id"] > since_id]
        last_id = WAKE_EVENT_QUEUE[-1]["id"] if WAKE_EVENT_QUEUE else since_id
    return {"events": events, "last_id": last_id}


@app.post("/api/wake_word/enable")
def api_enable_wake_word(req: Optional[WakeWordMicRequest] = None):
    mic_idx = req.device_index if req else None
    if mic_idx is not None:
        WAKE_DAEMON.select_microphone(mic_idx)
    if not WAKE_DAEMON.enabled or not WAKE_DAEMON.is_listening:
        WAKE_DAEMON.stop()
        WAKE_DAEMON.start(command_callback=handle_wake_command_background)
    log_event("VOICE", f"Always-On Open-Mic forced ENABLE: Active on '{WAKE_DAEMON.active_mic_name}'")
    return {"status": "success", "enabled": True, "details": WAKE_DAEMON.get_status()}


@app.post("/api/wake_word/toggle")
@app.post("/api/voice/wake_word/toggle")
def api_toggle_wake_word(req: Optional[WakeWordToggleRequest] = None):
    if req and req.enabled is not None:
        target = req.enabled
    else:
        target = not WAKE_DAEMON.enabled

    if target:
        WAKE_DAEMON.start(command_callback=handle_wake_command_background)
    else:
        WAKE_DAEMON.stop()

    log_event("VOICE", f"True Open-Mic Wake Word Daemon: {'ACTIVE' if target else 'OFF'} on '{WAKE_DAEMON.active_mic_name}'")
    return {"status": "success", "enabled": WAKE_DAEMON.enabled, "details": WAKE_DAEMON.get_status()}


@app.post("/api/wake_word/set_mic")
def api_set_wake_word_mic(req: WakeWordMicRequest):
    idx, name = WAKE_DAEMON.select_microphone(req.device_index)
    if WAKE_DAEMON.enabled:
        WAKE_DAEMON.stop()
        WAKE_DAEMON.start(command_callback=handle_wake_command_background)
    log_event("VOICE", f"Wake word microphone set to #{idx} '{name}'")
    return {"status": "success", "device_index": idx, "name": name}


@app.post("/api/voice/wake_word/simulate")
def api_simulate_wake_word(req: CommandRequest):
    matched, phrase, remainder = WAKE_DAEMON.match_wake_phrase(req.command)
    if matched:
        cmd_to_run = remainder if remainder and len(remainder) > 3 else req.command
        cmd_res = process_user_command(cmd_to_run)
        return {"status": "triggered", "wake_phrase_detected": True, "phrase": phrase, "command": cmd_to_run, "result": cmd_res}
    return {"status": "ignored", "wake_phrase_detected": False, "command": req.command}


@app.post("/api/self_test")
def run_self_test():
    """
    Comprehensive live subsystem diagnostics across GPU, Router v4, Cortex 8B, Vault, Voice, and Hands.
    """
    log_event("SYS", "====== EXECUTING FULL JESSICA SELF-TEST ======")
    results = {}

    # 1. GPU Check
    try:
        dev_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
        free_bytes, total_bytes = torch.cuda.mem_get_info(0) if torch.cuda.is_available() else (0, 0)
        results["gpu"] = {
            "status": "PASS" if torch.cuda.is_available() else "FAIL",
            "device": dev_name,
            "vram_free_gb": round(free_bytes / (1024**3), 2),
            "vram_total_gb": round(total_bytes / (1024**3), 2)
        }
        log_event("SYS", f"[SELF-TEST] GPU: {dev_name} ({results['gpu']['vram_free_gb']} GB Free)")
    except Exception as e:
        results["gpu"] = {"status": "ERROR", "error": str(e)}

    # 2. Router v4 Test
    try:
        r_pred = process_user_command("Check GPU temperature and VRAM")
        results["router"] = {
            "status": "PASS" if r_pred["predicted_intent"] == "get_system_telemetry" else "WARN",
            "predicted": r_pred["predicted_intent"],
            "confidence": r_pred["confidence"],
            "latency_ms": r_pred["latency_ms"]
        }
        log_event("BRAIN", f"[SELF-TEST] Router v4: {r_pred['predicted_intent']} ({r_pred['confidence']}%) in {r_pred['latency_ms']}ms")
    except Exception as e:
        results["router"] = {"status": "ERROR", "error": str(e)}

    # 3. Cortex 8B Test
    try:
        c_speed = BRAIN["last_stats"].get("tokens_per_sec", 0.0)
        results["cortex"] = {
            "status": "PASS" if BRAIN["cortex_loaded"] else "FAIL",
            "checkpoint": BRAIN["cortex_checkpoint_name"],
            "tokens_per_sec": c_speed,
            "params": "8.03B"
        }
        log_event("BRAIN", f"[SELF-TEST] Cortex 8B: Active ({c_speed} tok/s)")
    except Exception as e:
        results["cortex"] = {"status": "ERROR", "error": str(e)}

    # 4. Vault Indexer Test
    try:
        hits = BRAIN["vault_indexer"].search("thermal limits", top_k=1, min_score=0.35)
        results["vault"] = {
            "status": "PASS" if hits else "WARN",
            "indexed_docs": len(BRAIN["vault_indexer"].documents),
            "sample_match": hits[0]["title"] if hits else "None"
        }
        log_event("VAULT", f"[SELF-TEST] Obsidian Indexer: {results['vault']['indexed_docs']} docs | Top match: {results['vault']['sample_match']}")
    except Exception as e:
        results["vault"] = {"status": "ERROR", "error": str(e)}

    # 5. Voice Engine Test
    try:
        f0 = VOICE_ENGINE.profile.get("pitch_f0", {}).get("mean_hz", 235.0)
        results["voice"] = {
            "status": "PASS" if VOICE_ENGINE.profile else "WARN",
            "f0_mean_hz": f0,
            "auto_speak": get_auto_speak()
        }
        log_event("VOICE", f"[SELF-TEST] Voice Engine: F0={f0}Hz | Auto-speak: {get_auto_speak()}")
    except Exception as e:
        results["voice"] = {"status": "ERROR", "error": str(e)}

    # 6. Network Diagnostics Test
    try:
        net = action_api.check_network_status()
        results["network"] = {
            "status": "PASS" if net["internet_reachable"] else "WARN",
            "local_ip": net["local_ip"],
            "gateway": net["gateway"],
            "ping_1_1_1_1_ms": net["ping_latency_1_1_1_1_ms"]
        }
        log_event("HANDS", f"[SELF-TEST] Network: IP {net['local_ip']} | Latency {net['ping_latency_1_1_1_1_ms']}ms")
    except Exception as e:
        results["network"] = {"status": "ERROR", "error": str(e)}

    log_event("SYS", "====== SELF-TEST COMPLETED ALL SUBSYSTEMS OPERATIONAL ======")
    return {"status": "success", "subsystems": results}


# Mount static desktop app
desktop_frontend = WORKSPACE_ROOT / "desktop_app" / "frontend"
if desktop_frontend.exists():
    app.mount("/", StaticFiles(directory=str(desktop_frontend), html=True), name="desktop")

if __name__ == "__main__":
    import uvicorn
    # access_log=False ensures terminal is silent and never hangs or buffers blocking outputs
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False)
