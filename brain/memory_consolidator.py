"""
Project Jessica - Dynamic Memory Consolidator & Knowledge Graph Synchronizer
Autonomously extracts personal statements, preferences, relationships, and cues
from conversation turns and consolidates them across:
1. 32GB System RAM Resident Cache (Instant < 0.05 ms retrieval)
2. SQLite Eternal Memory Database (E:/GitHub/JESSICA_STORAGE/memory/jessica_eternal_memory.db)
3. Obsidian Vault Markdown Graph (obsidian_vault/00_Identity/Creator_Core_Memories.md)
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.persistence_engine import get_persistence_engine
from brain.ram_cache import get_ram_cache

CREATOR_MEMORIES_MD = WORKSPACE_ROOT / "obsidian_vault" / "00_Identity" / "Creator_Core_Memories.md"


class MemoryConsolidator:
    """
    Extracts and synchronizes creator memories across RAM, SQLite, and Markdown.
    """
    def __init__(self):
        self.persistence = get_persistence_engine()
        self.ram_cache = get_ram_cache()

    def consolidate_turn(self, user_text: str, reply_text: str = "") -> List[Dict[str, str]]:
        """
        Scans user_text for personal facts, preferences, or profile updates.
        Returns any newly extracted facts.
        """
        extracted_facts: List[Dict[str, str]] = []
        user_lower = user_text.lower()

        # 1. Identity & Names
        name_match = re.search(r"(?:my name is|i am|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", user_text, re.IGNORECASE)
        if name_match:
            val = name_match.group(1).strip()
            if val.lower() not in ["jessica", "here", "ready", "fine", "good", "going"]:
                extracted_facts.append({"category": "identity", "key": "full_name", "value": val})

        # 2. Preferred Title
        if re.search(r"\bcall me (boss|alexander|alex)\b", user_lower):
            title = "Boss" if "boss" in user_lower else "Alexander"
            extracted_facts.append({"category": "identity", "key": "preferred_title", "value": title})

        # 3. Girlfriend / Relationship
        gf_match = re.search(r"(?:my girlfriend(?:'s name)? is|gf is|dating)\s+([A-Z][a-z]+)", user_text, re.IGNORECASE)
        if gf_match:
            extracted_facts.append({"category": "relationship", "key": "girlfriend", "value": gf_match.group(1).strip()})

        # 4. Musical Instruments / Gear
        bass_match = re.search(r"\b(?:i play(?: a)?|my instrument is a?|my bass is a?)\s+([a-zA-Z0-9\-\s]+(?:bass|guitar|keyboard|drums))", user_text, re.IGNORECASE)
        if bass_match:
            extracted_facts.append({"category": "gear", "key": "instrument", "value": bass_match.group(1).strip()})
        elif "jcraft" in user_lower and "bass" in user_lower:
            extracted_facts.append({"category": "gear", "key": "instrument", "value": "4-string passive Jcraft Jazz bass guitar"})

        # 5. Favorite Food / Preferences
        food_match = re.search(r"(?:my favorite food is|i love eating|favorite dish is)\s+([a-zA-Z\s]+)", user_text, re.IGNORECASE)
        if food_match:
            val = food_match.group(1).strip().rstrip(".!?")
            extracted_facts.append({"category": "preference", "key": "favorite_food", "value": val})
        elif "sinigang" in user_lower:
            extracted_facts.append({"category": "preference", "key": "favorite_dish", "value": "Sinigang"})

        # 6. Arrival Cue
        if "daddy's home" in user_lower or "daddys home" in user_lower:
            extracted_facts.append({"category": "cue", "key": "arrival_cue", "value": "Jessica! Daddy's home"})

        # Persist and synchronize facts
        for fact in extracted_facts:
            self._apply_fact(fact["category"], fact["key"], fact["value"])

        return extracted_facts

    def _apply_fact(self, category: str, key: str, value: str):
        # 1. Update SQLite
        self.persistence.upsert_creator_fact(category, key, value)

        # 2. Append/Update in Markdown Creator_Core_Memories.md
        self._update_markdown_graph(category, key, value)

        # 3. Refresh RAM Cache
        if CREATOR_MEMORIES_MD.exists():
            try:
                with open(CREATOR_MEMORIES_MD, "r", encoding="utf-8") as f:
                    new_text = f.read()
                self.ram_cache.update_creator_memories(new_text)
            except Exception as e:
                print(f"[!] Consolidator RAM Cache refresh notice: {e}")

    def _update_markdown_graph(self, category: str, key: str, value: str):
        if not CREATOR_MEMORIES_MD.exists():
            return

        try:
            with open(CREATOR_MEMORIES_MD, "r", encoding="utf-8") as f:
                content = f.read()

            fact_entry = f"- **{key.replace('_', ' ').title()}:** {value}"
            if fact_entry in content:
                return  # Already present

            section_header = "### 6. Dynamic Real-Time Fact Graph"
            if section_header in content:
                parts = content.split(section_header)
                new_section = parts[1] + f"\n- [{category.upper()}] **{key.replace('_', ' ').title()}:** {value} *(Learned {time.strftime('%Y-%m-%d %H:%M')})*"
                content = parts[0] + section_header + new_section
            else:
                content += f"\n\n{section_header}\n- [{category.upper()}] **{key.replace('_', ' ').title()}:** {value}"

            with open(CREATOR_MEMORIES_MD, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[!] Error updating markdown graph: {e}")


# Global Singleton Consolidator
MEMORY_CONSOLIDATOR = MemoryConsolidator()


def get_memory_consolidator() -> MemoryConsolidator:
    return MEMORY_CONSOLIDATOR

