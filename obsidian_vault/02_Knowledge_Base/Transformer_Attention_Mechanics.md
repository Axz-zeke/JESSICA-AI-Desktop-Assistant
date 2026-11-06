---
title: Transformer Attention Mechanics & FlashAttention
category: Full-Stack & Systems Engineering
tags: [ai, transformers, nlp, attention, flashattention]
created: 2026-11-01
status: ACTIVE
related: "[[PyTorch_Tensor_Cores_and_CUDA]], [[LLM_Quantization_NF4_and_AWQ]], [[PEFT_and_LoRA_Architectures]]"
---

# Transformer Attention Mechanics & FlashAttention

The **Transformer** architecture replaces recurrence with the **Self-Attention** mechanism, allowing models to process all tokens in a sequence concurrently and model long-range context dependencies.

## Scaled Dot-Product Attention
Given Query ($Q$), Key ($K$), and Value ($V$) projections of dimension $d_k$:
$$	ext{Attention}(Q, K, V) = 	ext{softmax}\left(rac{Q K^T}{\sqrt{d_k}}ight) V$$
- **Quadratic Complexity:** Calculating $Q K^T$ requires $O(N^2)$ memory and compute for sequence length $N$.
- **Rotary Position Embeddings (RoPE):** Encodes relative token positions by rotating query and key vectors in complex 2D planes, preserving distance information across long sequences.

## FlashAttention-2 Optimization
Standard PyTorch attention materializes the huge $N 	imes N$ attention matrix in GPU High-Bandwidth Memory (HBM). **FlashAttention** tiles inputs, calculates partial softmax statistics incrementally in fast on-chip SRAM, and writes back only the final output, reducing memory reads/writes by up to 10x.

See also: [[PyTorch_Tensor_Cores_and_CUDA]], [[LLM_Quantization_NF4_and_AWQ]], [[PEFT_and_LoRA_Architectures]].
