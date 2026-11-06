"""
Jessica Brain - Generative Cortex Tokenizer
A subword/word tokenizer tailored for Jessica's Causal Decoder Transformer,
supporting structured conversation, context injection, and response generation.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Union, Optional


class CortexTokenizer:
    PAD_TOKEN = "<pad>"
    UNK_TOKEN = "<unk>"
    BOS_TOKEN = "<bos>"
    EOS_TOKEN = "<eos>"
    USER_TOKEN = "<user>"
    JESSICA_TOKEN = "<jessica>"
    CONTEXT_TOKEN = "<context>"
    ACTION_TOKEN = "<action>"

    EMOTION_TOKENS = [
        "<emotion: warm>",
        "<emotion: playful>",
        "<emotion: excited>",
        "<emotion: calm>",
        "<emotion: serious>",
        "<emotion: curious>"
    ]

    SPECIAL_TOKENS = [
        PAD_TOKEN, UNK_TOKEN, BOS_TOKEN, EOS_TOKEN,
        USER_TOKEN, JESSICA_TOKEN, CONTEXT_TOKEN, ACTION_TOKEN
    ] + EMOTION_TOKENS

    def __init__(self, vocab_file: Optional[Union[str, Path]] = None):
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}

        if vocab_file and Path(vocab_file).exists():
            self.load(vocab_file)
        else:
            self._init_special_tokens()

    def _init_special_tokens(self):
        self.token_to_id = {tok: idx for idx, tok in enumerate(self.SPECIAL_TOKENS)}
        self.id_to_token = {idx: tok for idx, tok in enumerate(self.SPECIAL_TOKENS)}

    def tokenize(self, text: str) -> List[str]:
        # Keep special tokens (including emotions) intact during tokenization
        pattern = r"(<pad>|<unk>|<bos>|<eos>|<user>|<jessica>|<context>|<action>|<emotion:\s*\w+>|[a-zA-Z0-9_\-\.]+|[^\w\s])"
        tokens = re.findall(pattern, text)
        return tokens

    def build_vocab(self, texts: List[str], min_freq: int = 1, max_vocab_size: int = 3500, additional_vocab: Optional[List[str]] = None):
        self._init_special_tokens()
        freqs: Dict[str, int] = {}

        for text in texts:
            for tok in self.tokenize(text):
                norm_tok = tok if tok.startswith("<") else tok.lower()
                if norm_tok not in self.token_to_id:
                    freqs[norm_tok] = freqs.get(norm_tok, 0) + 1

        sorted_tokens = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        for tok, count in sorted_tokens:
            if count < min_freq or len(self.token_to_id) >= max_vocab_size:
                break
            if tok not in self.token_to_id:
                idx = len(self.token_to_id)
                self.token_to_id[tok] = idx
                self.id_to_token[idx] = tok

        # Include additional vocabulary words if space remains
        if additional_vocab:
            for word in additional_vocab:
                clean_word = word.lower().strip()
                if clean_word and clean_word not in self.token_to_id and len(self.token_to_id) < max_vocab_size:
                    idx = len(self.token_to_id)
                    self.token_to_id[clean_word] = idx
                    self.id_to_token[idx] = clean_word

    def encode(self, text: str, max_len: Optional[int] = None, add_bos_eos: bool = False) -> List[int]:
        raw_tokens = self.tokenize(text)
        token_ids = []
        if add_bos_eos:
            token_ids.append(self.token_to_id[self.BOS_TOKEN])

        for tok in raw_tokens:
            norm_tok = tok.lower() if not tok.startswith("<") else tok
            token_ids.append(self.token_to_id.get(norm_tok, self.token_to_id[self.UNK_TOKEN]))

        if add_bos_eos:
            token_ids.append(self.token_to_id[self.EOS_TOKEN])

        if max_len is not None:
            if len(token_ids) > max_len:
                token_ids = token_ids[:max_len]
            else:
                token_ids = token_ids + [self.token_to_id[self.PAD_TOKEN]] * (max_len - len(token_ids))

        return token_ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = False) -> str:
        tokens = []
        for tid in token_ids:
            tok = self.id_to_token.get(tid, self.UNK_TOKEN)
            if skip_special_tokens and tok in self.SPECIAL_TOKENS:
                continue
            tokens.append(tok)
        
        # Clean spacing around punctuation
        text = " ".join(tokens)
        text = re.sub(r"\s+([,\.\?!;:])", r"\1", text)
        return text

    def save(self, file_path: Union[str, Path]):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "token_to_id": self.token_to_id,
                "vocab_size": len(self.token_to_id)
            }, f, indent=2)

    def load(self, file_path: Union[str, Path]):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.token_to_id = data["token_to_id"]
            self.id_to_token = {int(v): k for k, v in self.token_to_id.items()}

    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id)

