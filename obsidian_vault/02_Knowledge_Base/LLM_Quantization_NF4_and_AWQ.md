---
title: LLM Quantization: 4-Bit NormalFloat (NF4), AWQ & GPTQ
category: Full-Stack & Systems Engineering
tags: [ai, quantization, nf4, awq, bitsandbytes, rtx4060]
created: 2026-11-01
status: ACTIVE
related: "[[PyTorch_Tensor_Cores_and_CUDA]], [[PEFT_and_LoRA_Architectures]], [[RTX_4060_Ada_Lovelace_Architecture]]"
---

# LLM Quantization: 4-Bit NormalFloat (NF4), AWQ & GPTQ

**Model Quantization** compresses large language model weights from 16-bit floating point down to 4-bit integers or normal floats, enabling 8-billion parameter models (which typically require 16GB+ VRAM) to execute within 5.5GB VRAM on consumer GPUs like the RTX 4060.

## 4-Bit NormalFloat (NF4) & Double Quantization
Developed for QLoRA by Tim Dettmers et al. (bitsandbytes):
- **Normal Distribution Mapping:** Neural network weights naturally follow a normal distribution centered at zero. NF4 constructs optimal information-theoretic quantiles such that each bin holds an equal probability mass.
- **Double Quantization:** Quantizes the quantization constants themselves, saving an additional 0.37 bits per parameter (~3GB saved on 65B models; ~400MB saved on 8B models).
- **Compute Precision:** Weights are stored in 4-bit, but dynamically dequantized into FP16 or BF16 registers during matrix multiplication, preserving high numerical precision during inference and backprop.

See also: [[PEFT_and_LoRA_Architectures]], [[PyTorch_Tensor_Cores_and_CUDA]], [[RTX_4060_Ada_Lovelace_Architecture]].
