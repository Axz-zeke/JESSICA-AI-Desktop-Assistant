# Modern PC Hardware: PCIe Gen 4/5 & NVMe Storage

## PCIe Bus Architecture
- **Point-to-Point Topology**: Unlike legacy shared PCI buses, PCIe connects each device directly to the CPU or PCH (Platform Controller Hub) via dedicated serial differential lanes (x1, x4, x8, x16).
- **Throughput by Generation**:
  * **PCIe 3.0**: ~1 GB/s per lane (x4 NVMe SSD = ~3,500 MB/s).
  * **PCIe 4.0 (RTX 4060, Modern M.2)**: ~2 GB/s per lane (x4 NVMe SSD = ~7,500 MB/s; x8 GPU = ~16 GB/s).
  * **PCIe 5.0**: ~4 GB/s per lane (x4 NVMe SSD = ~14,000 MB/s).

## NVMe Protocol Advantages over Legacy AHCI/SATA
- **Command Queues**: Legacy SATA AHCI supported a single queue with 32 commands max. NVMe supports up to **64,000 queues with 64,000 commands each**, taking full advantage of modern multi-core CPUs and flash parallelism.
- **Direct PCIe Access**: Eliminates intermediate SATA host controller bottlenecks and minimizes CPU driver overhead.
