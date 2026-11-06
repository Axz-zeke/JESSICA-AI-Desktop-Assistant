# PyTorch FlashAttention and SDPA Inference Kernels

## Scaled Dot-Product Attention (SDPA)
Standard attention computes $O(N^2)$ memory bandwidth by writing full intermediate attention matrices ($Q K^T / \sqrt{d}$) to High Bandwidth Memory (HBM).
FlashAttention tiles attention computation into GPU SRAM blocks, fusing softmax and matrix multiplication, cutting memory bandwidth consumption by up to 80%.

## Enabling SDPA Kernels in PyTorch
```python
import torch

with torch.inference_mode():
    with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=True):
        output = model(input_ids)
```
Enabling SDPA alongside TensorFloat-32 (`allow_tf32 = True`) accelerates generation throughput on Ada Lovelace RTX 4060 GPUs.
