"""
Jessica Working Memory - Multi-Turn Conversational Context Buffer
Maintains sliding-window short-term conversational context (last 6 turns)
ensuring Jessica maintains full coherent multi-turn awareness across messages.
"""

from typing import List, Dict, Any, Optional
import time
import json
from pathlib import Path


class WorkingMemory:
    """
    Sliding window conversational memory storing user-assistant dialogue pairs.
    """
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []

    def add_user_message(self, content: str):
        if not content:
            return
        self.history.append({
            "role": "user",
            "content": content.strip()
        })
        self._trim()

    def add_assistant_message(self, content: str):
        if not content:
            return
        self.history.append({
            "role": "assistant",
            "content": content.strip()
        })
        self._trim()

    def _trim(self):
        # Keep at most max_turns * 2 individual messages (user + assistant turns)
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def get_messages(self, max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        limit = (max_turns or self.max_turns) * 2
        return list(self.history[-limit:])

    def get_turn_count(self) -> int:
        # Number of user turns stored
        return sum(1 for m in self.history if m["role"] == "user")

    def clear(self):
        self.history.clear()


# Global singleton instance
WORKING_MEMORY = WorkingMemory(max_turns=6)


def get_working_memory() -> WorkingMemory:
    return WORKING_MEMORY

