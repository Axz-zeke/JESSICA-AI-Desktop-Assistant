"""
Jessica Brain - Full English BPE Tokenizer
A production-grade BPE Tokenizer built on GPT-2's 50,257 subword vocabulary
extended with Jessica's special tokens for dialogue turns, RAG grounding, and emotional prosody.
Aligned to 50,304 tokens for optimal NVIDIA Tensor Core matrix multiplication.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
import tiktoken

# Special Token Definitions
SPECIAL_TOKENS = {
    "<|bos|>": 50257,
    "<|eos|>": 50258,
    "<|pad|>": 50259,
    "<|user|>": 50260,
    "<|context|>": 50261,
    "<|action|>": 50262,
    "<|jessica|>": 50263,
    "<|emotion:warm|>": 50264,
    "<|emotion:playful|>": 50265,
    "<|emotion:curious|>": 50266,
    "<|emotion:calm|>": 50267,
    "<|emotion:serious|>": 50268,
}

REVERSE_SPECIAL_TOKENS = {v: k for k, v in SPECIAL_TOKENS.items()}

# Aligned vocabulary size: 50,304 is the next multiple of 64 above 50,269 for Tensor Core throughput
VOCAB_SIZE_ALIGNED = 50304


class JessicaBPETokenizer:
    """
    Full English BPE Tokenizer wrapping tiktoken GPT-2 encoding with special tokens.
    Provides lossless subword encoding, decoding, and target-mask sequence formatting.
    """

    def __init__(self):
        base = tiktoken.get_encoding("gpt2")
        self.special_tokens = dict(SPECIAL_TOKENS)
        self.reverse_special_tokens = dict(REVERSE_SPECIAL_TOKENS)

        # Merge base special tokens with Jessica special tokens
        merged_special = {**base._special_tokens, **self.special_tokens}

        self._encoding = tiktoken.Encoding(
            name="jessica_gpt2_bpe",
            pat_str=base._pat_str,
            mergeable_ranks=base._mergeable_ranks,
            special_tokens=merged_special
        )

        self.bos_token_id = self.special_tokens["<|bos|>"]
        self.eos_token_id = self.special_tokens["<|eos|>"]
        self.pad_token_id = self.special_tokens["<|pad|>"]
        self.user_token_id = self.special_tokens["<|user|>"]
        self.context_token_id = self.special_tokens["<|context|>"]
        self.action_token_id = self.special_tokens["<|action|>"]
        self.jessica_token_id = self.special_tokens["<|jessica|>"]

        self.vocab_size = VOCAB_SIZE_ALIGNED
        self.actual_vocab_size = self._encoding.n_vocab

    def encode(self, text: str, allowed_special: str = "all") -> List[int]:
        """
        Encode raw string into list of token IDs.
        """
        if not text:
            return []
        return self._encoding.encode(text, allowed_special=allowed_special)

    def decode(self, token_ids: List[int], skip_special_tokens: bool = False) -> str:
        """
        Decode list of token IDs back into string.
        """
        if not token_ids:
            return ""
        # Filter out pad tokens or any tokens >= actual_vocab_size
        valid_ids = [t for t in token_ids if 0 <= t < self.actual_vocab_size and t != self.pad_token_id]
        if skip_special_tokens:
            valid_ids = [t for t in valid_ids if t not in self.reverse_special_tokens]
        return self._encoding.decode(valid_ids)

    def format_prompt(self, user_msg: str, context: str = "none", action: str = "none") -> str:
        """
        Format prompt prefix ready for generation:
        <|bos|><|user|> {user_msg} <|context|> {context} <|action|> {action} <|jessica|>
        """
        return f"<|bos|><|user|> {user_msg.strip()} <|context|> {context.strip()} <|action|> {action.strip()} <|jessica|>"

    def format_training_sequence(
        self,
        user_msg: str,
        completion: str,
        context: str = "none",
        action: str = "none"
    ) -> Dict[str, Union[List[int], str]]:
        """
        Create full sequence with prompt and completion, along with target mask boundaries.
        Returns prompt_ids, completion_ids, full_ids, and target_ids with -100 masking on prompt.
        """
        prompt_str = self.format_prompt(user_msg, context, action)
        completion_str = completion.strip()
        if not completion_str.endswith("<|eos|>"):
            completion_str += "<|eos|>"

        prompt_ids = self.encode(prompt_str)
        completion_ids = self.encode(completion_str)

        full_ids = prompt_ids + completion_ids
        # Target tokens: ignore_index = -100 for all prompt tokens
        targets = [-100] * len(prompt_ids) + list(completion_ids)

        return {
            "prompt_str": prompt_str,
            "completion_str": completion_str,
            "full_ids": full_ids,
            "targets": targets,
            "prompt_len": len(prompt_ids),
            "total_len": len(full_ids)
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": "Jessica Full English BPE Tokenizer (GPT-2 Base)",
            "base_vocab_size": 50257,
            "special_tokens_count": len(self.special_tokens),
            "actual_vocab_size": self.actual_vocab_size,
            "tensor_aligned_vocab_size": self.vocab_size,
            "special_tokens": self.special_tokens
        }


# Singleton instance
BPE_TOKENIZER = JessicaBPETokenizer()

if __name__ == "__main__":
    tok = JessicaBPETokenizer()
    print("Tokenizer Stats:", tok.get_stats())
    sample = tok.format_training_sequence(
        user_msg="How are you feeling today?",
        completion="<|emotion:warm|> I am feeling wonderful, thank you! Ready to assist you on your system.",
        context="RTX 4060 GPU Telemetry normal",
        action="none"
    )
    print("Full IDs length:", len(sample["full_ids"]))
    print("Decoded full:", tok.decode(sample["full_ids"]))
    print("Target mask test (first 5 and last 5):", sample["targets"][:5], "...", sample["targets"][-5:])
