"""
Jessica Brain - Neural Intent Router Transformer
A from-scratch PyTorch Transformer architecture classifying user intent into deterministic OS tool calls.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Dict

# Intent labels mapping
INTENT_CLASSES: List[str] = [
    "get_system_telemetry",
    "list_top_processes",
    "check_network_status",
    "open_application",
    "write_obsidian_note",
    "read_obsidian_vault",
    "set_system_volume",
    "take_screenshot",
    "kill_process",
    "conversation",
    "learn_from_internet",
    "control_window",
    "type_and_automate",
    "search_local_files",
    "verify_biometrics",
    "analyze_screen"
]

INTENT_TO_ID: Dict[str, int] = {name: idx for idx, name in enumerate(INTENT_CLASSES)}
ID_TO_INTENT: Dict[int, str] = {idx: name for idx, name in enumerate(INTENT_CLASSES)}


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape

        # Linear projections & split into heads: (B, H, S, d_k)
        q = self.q_proj(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)

        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            # mask shape: (B, 1, 1, S)
            scores = scores.masked_fill(mask == 0, -1e9)

        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        context = torch.matmul(attn_weights, v)  # (B, H, S, d_k)
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.out_proj(context)


class TransformerEncoderBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attn = MultiHeadSelfAttention(d_model, n_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Pre-LN Transformer block architecture
        attn_out = self.attn(self.norm1(x), mask=mask)
        x = x + attn_out
        ffn_out = self.ffn(self.norm2(x))
        x = x + ffn_out
        return x


class JessicaRouterNet(nn.Module):
    def __init__(
        self,
        vocab_size: int = 1024,
        d_model: int = 128,
        n_heads: int = 4,
        num_layers: int = 3,
        d_ff: int = 256,
        num_classes: int = len(INTENT_CLASSES),
        max_seq_len: int = 64,
        dropout: float = 0.1
    ):
        super().__init__()
        self.d_model = d_model
        self.token_embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        self.dropout = nn.Dropout(dropout)

        self.blocks = nn.ModuleList([
            TransformerEncoderBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        self.final_norm = nn.LayerNorm(d_model)
        
        # Intent classification head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, num_classes)
        )

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        input_ids: (batch_size, seq_len)
        Returns: logits (batch_size, num_classes)
        """
        batch_size, seq_len = input_ids.shape
        device = input_ids.device

        # Padding mask: 1 for valid tokens, 0 for PAD
        pad_mask = (input_ids != 0).unsqueeze(1).unsqueeze(2)  # (B, 1, 1, S)

        positions = torch.arange(seq_len, device=device).unsqueeze(0).expand(batch_size, seq_len)
        x = self.token_embedding(input_ids) + self.pos_embedding(positions)
        x = self.dropout(x)

        for block in self.blocks:
            x = block(x, mask=pad_mask)

        x = self.final_norm(x)

        # Masked mean pooling across non-pad sequence tokens
        mask_expanded = (input_ids != 0).unsqueeze(-1).float()  # (B, S, 1)
        sum_embeddings = torch.sum(x * mask_expanded, dim=1)
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        pooled = sum_embeddings / sum_mask

        logits = self.classifier(pooled)
        return logits


if __name__ == "__main__":
    dummy_input = torch.randint(0, 100, (4, 32))
    model = JessicaRouterNet(vocab_size=200)
    out = model(dummy_input)
    print("RouterNet output shape:", out.shape)

