---
title: PEFT & Low-Rank Adaptation (LoRA) Fine-Tuning
category: Full-Stack & Systems Engineering
tags: [ai, peft, lora, fine-tuning, training, rtx4060]
created: 2026-11-01
status: ACTIVE
related: "[[LLM_Quantization_NF4_and_AWQ]], [[PyTorch_Tensor_Cores_and_CUDA]], [[Transformer_Attention_Mechanics]]"
---

# PEFT & Low-Rank Adaptation (LoRA) Fine-Tuning

**Parameter-Efficient Fine-Tuning (PEFT)** adapts massive pre-trained foundation models to specialized tasks without updating all base model weights. **LoRA (Low-Rank Adaptation)** freezes base weights $W_0 \in \mathbb{R}^{d 	imes k}$ and injects trainable rank decomposition matrices:
$$W = W_0 + \Delta W = W_0 + rac{lpha}{r} (B 	imes A)$$
where $A \in \mathbb{R}^{r 	imes k}$ is initialized with Gaussian noise and $B \in \mathbb{R}^{d 	imes r}$ is initialized to zero.

## Key Hyperparameters
- **Rank ($r$):** The inner dimension (typically $r=8$ or $r=16$). Smaller rank reduces parameter count and VRAM; higher rank captures more complex behavior shifts.
- **Scaling Factor ($lpha$):** Scales the adapter's update magnitude relative to base weights ($\Delta W 	imes rac{lpha}{r}$). Often set to $2 	imes r$.
- **Target Modules:** Initially applied only to attention projections (`q_proj`, `v_proj`). Modern full-linear QLoRA adapts all linear layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`) for maximum expressiveness.

See also: [[LLM_Quantization_NF4_and_AWQ]], [[Transformer_Attention_Mechanics]], [[PyTorch_Tensor_Cores_and_CUDA]].
