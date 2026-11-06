# BitsAndBytes 4-Bit NF4 De-quantization Mechanics

## On-the-Fly Dynamic De-quantization
In `bitsandbytes` 4-bit Linear layers (`Linear4bit`), weights remain stored in compressed 4-bit memory format in VRAM.
During forward pass:
1. Active input activations (FP16/BF16) arrive at the CUDA core.
2. The custom `bitsandbytes` CUDA kernel de-quantizes the 4-bit weight slice into 16-bit registers on-the-fly.
3. High-speed FP16 Tensor Core matrix multiplication executes.
4. Intermediate de-quantized weights are immediately discarded from registers, never allocating FP16 footprint in global VRAM.
