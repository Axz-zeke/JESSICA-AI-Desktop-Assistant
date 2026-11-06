# Web Worker and Canvas Offscreen Frame Processing

## Offloading Main-Thread Rendering
Real-time webcam feeds at 1080p 60fps can cause UI stutter if frame analysis runs on the browser main UI thread.
`OffscreenCanvas` allows canvas rendering and pixel transformations to run inside an isolated Web Worker:
```javascript
// main.js
const offscreen = canvas.transferControlToOffscreen();
const worker = new Worker('vision-worker.js');
worker.postMessage({ canvas: offscreen }, [offscreen]);

// vision-worker.js
onmessage = function(e) {
  const canvas = e.data.canvas;
  const ctx = canvas.getContext('2d');
  // Process frames in background thread with zero UI lag
};
```
