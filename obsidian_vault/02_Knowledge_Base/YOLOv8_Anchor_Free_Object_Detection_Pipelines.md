# YOLOv8 Anchor-Free Object Detection Pipelines

## Anchor-Free Architecture
Ultralytics YOLOv8 abandons legacy anchor boxes in favor of anchor-free split-head detection:
- **Task-Aligned Assignor:** Dynamically balances classification confidence and bounding-box Intersection-over-Union (IoU).
- **Decoupled Head:** Computes classification loss (Binary Cross-Entropy) and regression loss (Complete IoU + Distribution Focal Loss) independently.
- **Execution on CPU:** YOLOv8n (nano, ~3.2M parameters) runs inference in ~18ms on an Intel Core i5 CPU, allocating zero GPU VRAM.
