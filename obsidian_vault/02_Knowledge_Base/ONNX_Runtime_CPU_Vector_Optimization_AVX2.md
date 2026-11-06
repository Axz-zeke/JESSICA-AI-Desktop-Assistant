# ONNX Runtime CPU Vector Optimization (AVX2 / AVX-512)

## Vector Instruction Acceleration
ONNX Runtime executes graph optimizations on CPUs by utilizing Intel AVX2 and AVX-512 vector units to execute SIMD (Single Instruction, Multiple Data) operations across 256-bit or 512-bit registers.

## Optimizing Session Options in Python
```python
import onnxruntime as ort

opts = ort.SessionOptions()
opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
opts.intra_op_num_threads = 8   # Match Intel Core i5 physical/logical cores
opts.inter_op_num_threads = 2
opts.execution_mode = ort.ExecutionMode.ORT_PARALLEL

session = ort.InferenceSession("kokoro-v1.0.onnx", sess_options=opts, providers=["CPUExecutionProvider"])
```
This configuration accelerates Kokoro-ONNX neural speech synthesis, generating spoken audio chunks in <120ms without taxing the GPU.
