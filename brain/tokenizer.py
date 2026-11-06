"""
Jessica Brain - Custom Tokenizer From Scratch
A zero-dependency, subword/character-aware tokenizer designed for local neural intent routing.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Union, Optional


class JessicaTokenizer:
    PAD_TOKEN = "<pad>"
    UNK_TOKEN = "<unk>"
    BOS_TOKEN = "<bos>"
    EOS_TOKEN = "<eos>"

    PAD_ID = 0
    UNK_ID = 1
    BOS_ID = 2
    EOS_ID = 3

    def __init__(self, vocab_file: Optional[Union[str, Path]] = None):
        self.special_tokens = [self.PAD_TOKEN, self.UNK_TOKEN, self.BOS_TOKEN, self.EOS_TOKEN]
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}

        if vocab_file and Path(vocab_file).exists():
            self.load(vocab_file)
        else:
            self._init_base_vocab()

    def _init_base_vocab(self):
        self.token_to_id = {tok: idx for idx, tok in enumerate(self.special_tokens)}
        self.id_to_token = {idx: tok for idx, tok in enumerate(self.special_tokens)}

    def tokenize(self, text: str) -> List[str]:
        """
        Regex-based tokenization splitting words, numbers, and punctuation.
        """
        cleaned = text.strip().lower()
        tokens = re.findall(r"\w+|[^\w\s]", cleaned)
        return tokens

    def build_vocab(self, texts: List[str], min_freq: int = 1, max_vocab_size: int = 2048):
        """
        Builds vocabulary from a corpus of texts.
        """
        self._init_base_vocab()
        freqs: Dict[str, int] = {}

        for text in texts:
            for tok in self.tokenize(text):
                freqs[tok] = freqs.get(tok, 0) + 1

        sorted_tokens = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        
        for tok, count in sorted_tokens:
            if count < min_freq or len(self.token_to_id) >= max_vocab_size:
                break
            if tok not in self.token_to_id:
                idx = len(self.token_to_id)
                self.token_to_id[tok] = idx
                self.id_to_token[idx] = tok

    def encode(self, text: str, max_len: int = 64, add_special_tokens: bool = True) -> List[int]:
        """
        Encodes string to a fixed-length list of token IDs with padding / truncation.
        """
        raw_tokens = self.tokenize(text)
        token_ids = [self.token_to_id.get(tok, self.UNK_ID) for tok in raw_tokens]

        if add_special_tokens:
            token_ids = [self.BOS_ID] + token_ids[:max_len - 2] + [self.EOS_ID]
        else:
            token_ids = token_ids[:max_len]

        # Padding
        if len(token_ids) < max_len:
            token_ids += [self.PAD_ID] * (max_len - len(token_ids))

        return token_ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Converts list of token IDs back into string.
        """
        tokens = []
        for tid in token_ids:
            if skip_special_tokens and tid in (self.PAD_ID, self.UNK_ID, self.BOS_ID, self.EOS_ID):
                continue
            tokens.append(self.id_to_token.get(tid, self.UNK_TOKEN))
        return " ".join(tokens)

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


if __name__ == "__main__":
    sample = ["What is the current CPU usage?", "Launch notepad please.", "Hello Jessica!"]
    tok = JessicaTokenizer()
    tok.build_vocab(sample)
    print("Vocab size:", tok.vocab_size)
    encoded = tok.encode("What is CPU usage?", max_len=12)
    print("Encoded:", encoded)
    print("Decoded:", tok.decode(encoded))

