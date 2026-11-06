"""
Test Server Multi-Turn Command Pipeline
"""
import os
import sys
from pathlib import Path

WORKSPACE_ROOT = Path("E:/Documents/GitHub/JESSICA").resolve()
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
os.chdir(str(WORKSPACE_ROOT))

from brain.media_disambiguator import clear_pending_media, get_pending_media
from hands.web_media_controller import can_handle_web_media, execute_web_media_command
from jessica_server import process_user_command

def test_multiturn_flow():
    clear_pending_media()
    print("[1] Turn 1: 'play IV of Spades on YouTube'")
    t1 = process_user_command("play IV of Spades on YouTube")
    print("Turn 1 Result:", t1.get("predicted_intent"), "| Reply:", t1.get("reply"))
    assert t1.get("predicted_intent") == "web_media_control"
    assert "Mundo" in t1.get("reply")
    assert get_pending_media() is not None

    print("\n[2] Checking if 'Mundo' is recognized as web media...")
    assert can_handle_web_media("Mundo") is True

    print("\n[3] Turn 2: 'Mundo'")
    t2 = process_user_command("Mundo")
    print("Turn 2 Result:", t2.get("predicted_intent"), "| Reply:", t2.get("reply"))
    assert t2.get("predicted_intent") == "web_media_control"
    assert "Mundo" in t2.get("reply")
    assert get_pending_media() is None
    print("\n[+] MULTI-TURN PIPELINE VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_multiturn_flow()
