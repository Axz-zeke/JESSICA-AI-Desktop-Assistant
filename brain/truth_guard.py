"""
Jessica Brain - Truth Guard & Epistemic Honesty Engine
Prevents hallucinating or inventing plausible-sounding answers when facts are unknown.
Features:
1. Fast Factual Intent & Knowledge Domain Classifier (who, what, when, where, why, how, is it true).
2. Trick Question & False Premise Detector (Napoleon inventing iPhone, Einstein building GPUs, fictional protocols).
3. Live Web-Verification Fallback (DuckDuckGo / Wikipedia) when Obsidian similarity < 0.42.
4. Epistemic Honesty Injection: Forcibly mandates admitting lack of knowledge when facts are unverified.
5. Adaptive Sampling Temperature: 0.15 for pinpoint factual accuracy vs 0.45 for warm conversational banter.
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.web_learner import is_factual_query, extract_topic_from_query, fetch_wikipedia_knowledge


# Known False Premise & Historical Anachronism Patterns
FALSE_PREMISE_PATTERNS = [
    (r'\b(?:napoleon|caesar|cleopatra|lincoln|washington)\b.*\b(?:iphone|android|internet|gpu|computer|smartphone|wifi)\b',
     "Historical Anachronism: Ancient/historical figure paired with modern digital technology."),
    (r'\b(?:albert\s+einstein|isaac\s+newton|galileo)\b.*\b(?:nvidia|gpu|rtx|geforce|intel\s+core|microprocessor|playstation)\b',
     "Historical Anachronism: Historic physicist paired with modern semiconductor/GPU hardware."),
    (r'\b(?:hyperflux|qx-9900|quantum\s+vlan\s+protocol|fluxcapacitor\s+protocol|cyberquantum\s+router)\b',
     "Fictional / Non-Existent Technology: Name is a fabricated science fiction term."),
    (r'\b(?:what\s+color\s+socks?|what\s+did\s+i\s+eat\s+for\s+lunch\s+in\s+20\d\d|what\s+was\s+my\s+neighbor\s+wearing)\b',
     "Unknowable Personal / Real-World Micro-Fact: Private, unrecorded real-world physical event.")
]


class TruthGuard:
    """
    Epistemic Humility and Grounding Gate for Jessica.
    Ensures Jessica remains strictly truthful, catches trick questions,
    and candidly admits when she doesn't know rather than fabricating falsehoods.
    """
    def __init__(self):
        self.min_vault_confidence = 0.42
        self.verified_cache: Dict[str, Dict[str, Any]] = {}

    def is_knowledge_query(self, query: str) -> bool:
        """
        Detects if query is seeking factual, historical, scientific, or technical information.
        """
        q = query.lower().strip()
        # Direct dialogue / greeting exclusions
        casual_greetings = [
            "hi", "hello", "hey", "hey jessica", "hey jess", "how are you", "who are you",
            "where do you live", "look at my camera", "what is up", "what's up", "whats up",
            "what's new", "how is it going", "how's it going", "what are you doing"
        ]
        if any(q == g or q.startswith(g + " ") or q.endswith(" " + g) for g in casual_greetings):
            return False

        # OS Control exclusions
        if any(q.startswith(w) for w in ("open ", "launch ", "play ", "close ", "kill ", "set volume ", "restart ", "shutdown ")):
            return False

        if is_factual_query(q):
            return True

        question_markers = [
            "is it true", "is there", "are there", "did ", "when did", "who was", "who invented",
            "what year", "tell me about", "can you explain", "do you know about", "have you heard of",
            "how do i configure", "how does"
        ]
        return any(k in q for k in question_markers)

    def check_false_premises(self, query: str) -> Optional[str]:
        """
        Detects trick questions or impossible false premises.
        """
        q = query.lower().strip()
        for pattern, explanation in FALSE_PREMISE_PATTERNS:
            if re.search(pattern, q):
                return explanation
        return None

    def evaluate_grounding(
        self,
        query: str,
        vault_hits: List[Dict[str, Any]],
        web_learner_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluates knowledge query grounding and returns:
        - grounded_context: Context string to inject into LLM
        - recommended_temperature: 0.15 (factual) or 0.45 (banter)
        - honesty_directive_injected: bool
        - source: 'vault' | 'web' | 'epistemic_honesty' | 'banter'
        """
        query_clean = query.strip()
        q_lower = query_clean.lower()

        # 1. Check for False Premise / Trick Questions first
        false_premise_reason = self.check_false_premises(query_clean)
        if false_premise_reason:
            directive = (
                f"[EPISTEMIC HONESTY DIRECTIVE - TRICK QUESTION DETECTED]:\n"
                f"Boss is testing you with a trick question or false premise: '{false_premise_reason}'.\n"
                f"NEVER play along with the false premise or fabricate a timeline/steps!\n"
                f"Candidly, warmly, and playfully call out the false premise in natural conversational English. "
                f"Explain that this technology does not exist or that this historic figure never built/invented that item."
            )
            return {
                "grounded_context": directive,
                "recommended_temperature": 0.15,
                "honesty_directive_injected": True,
                "source": "epistemic_honesty",
                "reason": false_premise_reason
            }

        # 2. Check if this is a general conversational / roleplay query
        if not self.is_knowledge_query(query_clean):
            return {
                "grounded_context": "",
                "recommended_temperature": 0.45,
                "honesty_directive_injected": False,
                "source": "banter",
                "reason": "casual_dialogue"
            }

        # 3. Check Obsidian Vault grounding
        best_hit = vault_hits[0] if vault_hits else None
        vault_score = best_hit.get("score", 0.0) if best_hit else 0.0

        if best_hit and vault_score >= self.min_vault_confidence:
            # High-confidence Obsidian vault match
            vault_context = f"[Verified Obsidian Vault Knowledge Grounding]:\n{best_hit.get('snippet', '')}"
            return {
                "grounded_context": vault_context,
                "recommended_temperature": 0.15,
                "honesty_directive_injected": False,
                "source": "vault",
                "reason": f"vault_match_score_{vault_score:.2f}"
            }

        # 4. Vault similarity is low (< 0.42). Attempt fast web verification if enabled
        if web_learner_enabled:
            topic = extract_topic_from_query(query_clean)
            if topic in self.verified_cache:
                cached = self.verified_cache[topic]
                return {
                    "grounded_context": f"[Verified Live Knowledge Grounding]:\n{cached['summary']}",
                    "recommended_temperature": 0.15,
                    "honesty_directive_injected": False,
                    "source": "web_cache",
                    "reason": "cached_web_verification"
                }

            # Fast online lookup (Wikipedia REST)
            try:
                wiki_data = fetch_wikipedia_knowledge(topic)
                text_content = wiki_data.get("summary") or wiki_data.get("extract") or wiki_data.get("full_text") if wiki_data else None
                if text_content and len(text_content) > 40:
                    summary = text_content[:500]
                    self.verified_cache[topic] = {"summary": summary, "timestamp": time.time()}
                    return {
                        "grounded_context": f"[Verified Live Knowledge Grounding]:\n{summary}",
                        "recommended_temperature": 0.15,
                        "honesty_directive_injected": False,
                        "source": "web",
                        "reason": f"verified_topic_{topic}"
                    }
            except Exception as e:
                pass

        # 5. Unknown or Unverified Topic -> Mandate Epistemic Honesty!
        epistemic_directive = (
            f"[EPISTEMIC HONESTY DIRECTIVE - UNVERIFIED KNOWLEDGE]:\n"
            f"Confidence is low and no verified knowledge base source exists for this question: '{query_clean}'.\n"
            f"STRICT TRUTHFULNESS RULE: DO NOT GUESS OR FABRICATE FACTS! "
            f"Candidly and warmly tell Boss you don't know or don't have enough verified information on this right now, "
            f"and offer to research it deeper for him."
        )
        return {
            "grounded_context": epistemic_directive,
            "recommended_temperature": 0.15,
            "honesty_directive_injected": True,
            "source": "epistemic_honesty",
            "reason": "unverified_knowledge_low_confidence"
        }


# Global Singleton
TRUTH_GUARD = TruthGuard()
