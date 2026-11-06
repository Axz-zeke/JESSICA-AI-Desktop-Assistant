# Local LLM Quantization: NF4, GGUF, and AWQ Comparison

## Quantization Formats & Trade-offs
Quantization maps 16-bit floating point weights (FP16/BF16) to low-bit integers (4-bit / 8-bit), allowing 8B parameter models to run within 8GB VRAM (e.g. RTX 4060):

| Format | Execution Engine | Best Use Case | VRAM for 8B Model | Perplexity Loss |
| :--- | :--- | :--- | :--- | :--- |
| **NF4 (bitsandbytes)** | PyTorch / CUDA | LoRA Training & Fine-Tuning | ~5.4 GB | Extremely Low |
| **GGUF (llama.cpp)** | CPU + GPU Hybrid Offload | Cross-platform desktop apps | ~4.8 GB (Q4_K_M) | Low |
| **AWQ (Activation-aware)** | vLLM / TensorRT-LLM | High-throughput server serving | ~5.0 GB | Very Low |

## NF4 (NormalFloat4) Mathematical Principle
Unlike uniform integer quantization (INT4), NF4 represents normally distributed transformer weights with information-theoretically optimal quantiles, maintaining near-FP16 fidelity without outlier clipping.
