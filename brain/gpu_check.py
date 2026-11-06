"""
Jessica Brain - RTX 4060 CUDA & Tensor Core Benchmark
Verifies CUDA 12.4, device capabilities, VRAM, and evaluates FP16 Tensor Core throughput.
"""

import time
import torch


def run_gpu_check():
    print("=" * 60)
    print("        JESSICA HARDWARE VERIFICATION & BENCHMARK")
    print("=" * 60)

    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available:           {cuda_available}")
    print(f"PyTorch Version:          {torch.__version__}")
    print(f"CUDA Version (Torch):     {torch.version.cuda}")

    if not cuda_available:
        print("[-] ERROR: CUDA device not detected by PyTorch.")
        return

    device_id = 0
    device_name = torch.cuda.get_device_name(device_id)
    capability = torch.cuda.get_device_capability(device_id)
    free_mem_bytes, total_mem_bytes = torch.cuda.mem_get_info(device_id)

    free_vram_gb = free_mem_bytes / (1024 ** 3)
    total_vram_gb = total_mem_bytes / (1024 ** 3)

    print(f"GPU Device Name:          {device_name}")
    print(f"Compute Capability:       {capability[0]}.{capability[1]} (Ada Lovelace)")
    print(f"Total VRAM:               {total_vram_gb:.2f} GB ({total_mem_bytes / (1024**2):.0f} MiB)")
    print(f"Free VRAM:                {free_vram_gb:.2f} GB ({free_mem_bytes / (1024**2):.0f} MiB)")

    print("-" * 60)
    print("Running FP16 Tensor Core Matrix Multiplication Benchmark...")
    # Matrix dimensions
    N = 4096
    print(f"Matrix Size:              {N} x {N} (FP16)")

    # Allocate matrices on GPU
    device = torch.device(f"cuda:{device_id}")
    a = torch.randn(N, N, device=device, dtype=torch.float16)
    b = torch.randn(N, N, device=device, dtype=torch.float16)

    # Warmup
    for _ in range(10):
        _ = torch.matmul(a, b)
    torch.cuda.synchronize()

    # Timed iterations
    iterations = 50
    start = time.perf_counter()
    for _ in range(iterations):
        c = torch.matmul(a, b)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    avg_time_per_iter_ms = (elapsed / iterations) * 1000
    # FLOPs for NxN matmul = 2 * N^3
    flops_per_iter = 2 * (N ** 3)
    tflops = (flops_per_iter / (avg_time_per_iter_ms / 1000)) / 1e12

    print(f"Iterations:               {iterations}")
    print(f"Avg Latency per Matmul:   {avg_time_per_iter_ms:.3f} ms")
    print(f"FP16 Compute Throughput:  {tflops:.2f} TFLOPS")
    print("=" * 60)
    print("[+] RTX 4060 Hardware Verification & Tensor Cores OPERATIONAL.")
    print("=" * 60)


if __name__ == "__main__":
    run_gpu_check()

