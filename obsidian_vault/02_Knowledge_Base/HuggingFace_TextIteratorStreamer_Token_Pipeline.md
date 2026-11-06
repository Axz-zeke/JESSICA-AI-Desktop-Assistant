# HuggingFace TextIteratorStreamer Token Pipeline

## Pipelined Streaming Architecture
To deliver natural human conversational pacing, text generation must stream tokens to speech vocoders sentence-by-sentence rather than buffering entire paragraphs.

```text
[PyTorch GPU Worker] ----(tokens via Streamer)----> [Thread Queue]
                                                           |
[8-Thread CPU Worker] <==== Sentence Chunks (". ! ?") =====+
         |
[Kokoro-ONNX Speech Engine] ====> Audio Output Stream
```

`TextIteratorStreamer` operates in a background thread, pushing decoded subwords into an internal queue while the main thread consumes clauses immediately.
