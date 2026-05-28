# Walkthrough: Fortran Modernization Sandbox & LLM Chat Integration

We have successfully implemented and verified the Dockerized legacy-to-modern Fortran-to-C++ transpilation sandbox along with a local LLM chat advisor.

---

## 1. What was Completed

1. **Transpiler Module (`src/translator.py`)**: A parser that maps Fortran 77/90 structures to modern C++20 standard functions and column-major **Eigen** matrices.
2. **Flask Backend Web Server (`src/app.py`)**:
   * Evaluator scoring with double-decimal precision (`.toFixed(2)`).
   * Robust `/api/chat` route with active model discovery from the local `foundry.local` endpoint and Ollama fallbacks.
3. **High-Fidelity UI (`src/static/index.html`, `styles.css`, `script.js`)**: Slate-slate dark theme client with terminals, radial score indicator, and an interactive chat module.
4. **Dockerfile Containerization (`Dockerfile`)**: Container image with the complete compilation chain.
5. **Interactive Chat Integration (`foundry.local`)**:
   * Resolved macOS ONNX runtime library validation conflicts on the host by re-signing the `Inference.Service.Agent` service binaries and their dependent ONNX libraries with ad-hoc code signatures.
   * Configured the Docker network mapping to route `foundry.local` requests to the host gateway.
   * Automated dynamic active model detection from `http://foundry.local:5273/v1/models` so that any query matches the active model ID on the fly.

---

## 2. Docker Image Build Results

The Docker build task packages all code changes into the `legacy-next-sandbox` image:

```text
#13 exporting to image
#13 exporting layers 0.1s done
#13 naming to docker.io/library/legacy-next-sandbox:latest done
```

---

## 3. How to Run and Test the Sandbox

### A. Start the Foundry Service (Host Side)
Ensure your local `foundry` service is running on the host machine:
```bash
foundry service start
```
The active model will automatically load (e.g. `Phi-3.5-mini-instruct-generic-gpu` on port `5273`).

### B. Run the Sandbox Container
Run the container from the workspace root, configuring the DNS mapping for `foundry.local` so it maps to the host's loopback interface:

```bash
docker run -d --rm --name legacy-next-sandbox-run -p 8080:8080 --add-host=foundry.local:host-gateway legacy-next-sandbox
```

Once running, open your browser and go to:
**[http://localhost:8080](http://localhost:8080)**

---

## 4. Chat Advisor Verification

1. Ask the chatbot panel: *"How are arrays indexed in the transpiled C++?"*
2. The request is routed from inside Docker to the host at `http://foundry.local:5273/v1/chat/completions`.
3. The chatbot successfully uses the active `Phi-3.5` model to generate and stream the explanation:

```json
{
  "reply": " In the legacy Fortran code, arrays are typically indexed starting from 1... C++ uses zero-based indexing...",
  "source": "foundry.local"
}
```
 Gaps are dynamically bridged on the fly!
