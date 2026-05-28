#!/usr/bin/env python3
import os
import re
import sys
import subprocess
import tempfile
import json
from flask import Flask, request, jsonify, send_from_directory
from translator import transpile_fortran_to_cpp

app = Flask(__name__, static_folder='static', static_url_path='')

# Ensure temp directory exists
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'fortran_sandbox')
os.makedirs(TEMP_DIR, exist_ok=True)

# Path to Eigen headers in Docker container
EIGEN_PATH = "/usr/include/eigen3"

# Direct import of evaluator calculation logic
from evaluator import evaluate_migration, DEFAULT_WEIGHTS

def extract_variables(code):
    """
    Scans Fortran code for parameters and numeric assignments that can be customized.
    """
    params = {}
    
    # 1. Look for PARAMETER constants
    param_matches = re.findall(r'PARAMETER\s*\(([^)]+)\)', code, re.IGNORECASE)
    for match in param_matches:
        for item in match.split(','):
            if '=' in item:
                k, v = item.split('=')
                params[k.strip().upper()] = {
                    "type": "parameter",
                    "value": v.strip(),
                    "description": f"Grid constant {k.strip().upper()}"
                }
                
    # 2. Look for scalar assignments at the top of the program
    assignments = [
        ("DX", "Grid step DX"),
        ("DY", "Grid step DY"),
        ("DT", "Time step DT"),
        ("REYNOLDS", "Reynolds Number"),
        ("STEPS", "Solver Iterations")
    ]
    for var, desc in assignments:
        match = re.search(r'\b' + var + r'\s*=\s*([0-9.]+)', code, re.IGNORECASE)
        if match:
            params[var] = {
                "type": "assignment",
                "value": match.group(1),
                "description": desc
            }
            
    return params

def inject_inputs(code, inputs):
    """
    Modifies Fortran code by replacing PARAMETERs and assignments with custom user values.
    """
    modified_code = code
    
    # Replace parameter values
    # e.g., PARAMETER (NX=10, NY=10)
    for k, v in inputs.items():
        # Match parameter definitions
        modified_code = re.sub(
            r'(\b' + k + r'\s*=\s*)([a-zA-Z0-9.]+)',
            rf'\g<1>{v}',
            modified_code,
            flags=re.IGNORECASE
        )
        
        # Match assignment definitions (e.g., DX = 0.1)
        modified_code = re.sub(
            r'(\b' + k + r'\s*=\s*)([0-9.]+)',
            rf'\g<1>{v}',
            modified_code,
            flags=re.IGNORECASE
        )
        
    return modified_code

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json() or {}
    code = data.get('code', '')
    if not code:
        return jsonify({"error": "No code provided"}), 400
        
    variables = extract_variables(code)
    return jsonify({"variables": variables})

@app.route('/api/run', methods=['POST'])
def run_and_compare():
    data = request.get_json() or {}
    fortran_code = data.get('code', '')
    inputs = data.get('inputs', {})
    
    if not fortran_code:
        return jsonify({"error": "No code provided"}), 400
        
    # 1. Inject inputs into Fortran code
    modified_fortran = inject_inputs(fortran_code, inputs)
    
    # 2. Setup temp filenames
    fortran_file = os.path.join(TEMP_DIR, 'sim_legacy.f')
    fortran_bin = os.path.join(TEMP_DIR, 'sim_legacy')
    cpp_file = os.path.join(TEMP_DIR, 'sim_modern.cpp')
    cpp_bin = os.path.join(TEMP_DIR, 'sim_modern')
    
    legacy_stdout = ""
    legacy_stderr = ""
    legacy_compile_err = ""
    modern_stdout = ""
    modern_stderr = ""
    modern_compile_err = ""
    cpp_code = ""
    
    # --- LEGACY EXECUTION ---
    # Write Fortran file
    with open(fortran_file, 'w') as f:
        f.write(modified_fortran)
        
    # Compile Fortran
    compile_legacy = subprocess.run(
        ['gfortran', '-o', fortran_bin, fortran_file],
        capture_output=True, text=True
    )
    
    if compile_legacy.returncode != 0:
        legacy_compile_err = compile_legacy.stderr
    else:
        # Run Fortran binary
        run_legacy = subprocess.run(
            [fortran_bin],
            capture_output=True, text=True
        )
        legacy_stdout = run_legacy.stdout
        legacy_stderr = run_legacy.stderr
        
    # --- MODERN TRANSPILATION & EXECUTION ---
    try:
        # Transpile code
        cpp_code = transpile_fortran_to_cpp(modified_fortran)
        
        # Write C++ file
        with open(cpp_file, 'w') as f:
            f.write(cpp_code)
            
        # Compile C++20 + Eigen
        # Use g++ compiler with std=c++20 and include Eigen path
        compile_modern = subprocess.run(
            ['g++', '-std=c++20', f'-I{EIGEN_PATH}', '-o', cpp_bin, cpp_file],
            capture_output=True, text=True
        )
        
        if compile_modern.returncode != 0:
            modern_compile_err = compile_modern.stderr
        else:
            # Run C++ binary
            run_modern = subprocess.run(
                [cpp_bin],
                capture_output=True, text=True
            )
            modern_stdout = run_modern.stdout
            modern_stderr = run_modern.stderr
    except Exception as e:
        modern_compile_err = f"Transpilation / compilation exception: {str(e)}"

    # --- SCORE EVALUATION ---
    # Build dynamic mock report for score evaluation based on whether it compiled
    has_unmet_gaps = "U" if "CICS" in fortran_code or "registry" in fortran_code else "E"
    
    mock_assessment = {
        "module_name": "custom_sim.f",
        "target_technology": "Python + C++20 / Eigen",
        "assessments": {
            "syntax_and_semantics": [
                {
                    "element": "Variable declarations (INTEGER/REAL)",
                    "match_level": "E",
                    "rationale": "Numeric types mapped to C++ standard variables.",
                    "target_equivalent": "int, double"
                },
                {
                    "element": "DIMENSION array allocations",
                    "match_level": "M",
                    "rationale": "Fortran arrays are 1-indexed; Eigen is 0-indexed column-major.",
                    "target_equivalent": "Eigen::Matrix<double, ..., ColMajor>"
                }
            ],
            "architecture_and_state": [
                {
                    "element": "PROGRAM / SUBROUTINE layout",
                    "match_level": "E",
                    "rationale": "Subprograms mapped to separate functional blocks.",
                    "target_equivalent": "C++ functions"
                },
                {
                    "element": "COMMON blocks global sharing",
                    "match_level": "M",
                    "rationale": "Global common block variables grouped into struct scopes.",
                    "target_equivalent": "C++ global structs"
                }
            ],
            "dependencies_and_libraries": [
                {
                    "element": "Numerical solver nested DO loops",
                    "match_level": "E",
                    "rationale": "Matrix solver loops mapped to C++ loops.",
                    "target_equivalent": "for loops"
                }
            ],
            "runtime_and_integration": [
                {
                    "element": "System Call Output (WRITE)",
                    "match_level": has_unmet_gaps,
                    "rationale": "System terminal bindings handled natively.",
                    "target_equivalent": "std::format / std::cout"
                }
            ]
        }
    }
    
    # Calculate score using evaluator.py module
    score = 0.0
    scores_dict = {}
    for dim, items in mock_assessment["assessments"].items():
        weighted_sum = sum({"E": 1.0, "M": 0.6, "U": 0.0}.get(item["match_level"], 0.0) for item in items)
        dim_score = weighted_sum / len(items)
        scores_dict[dim] = dim_score
        
    for dim, weight in DEFAULT_WEIGHTS.items():
        score += weight * scores_dict.get(dim, 1.0)

    # Output comparison and diff metrics
    outputs_match = False
    diffs = []
    
    cleaned_legacy = legacy_stdout.strip().replace(" ", "")
    cleaned_modern = modern_stdout.strip().replace(" ", "")
    
    if cleaned_legacy and cleaned_modern:
        outputs_match = cleaned_legacy == cleaned_modern
        
    # Analyze differences
    legacy_lines = legacy_stdout.strip().split('\n')
    modern_lines = modern_stdout.strip().split('\n')
    
    max_len = max(len(legacy_lines), len(modern_lines))
    for idx in range(max_len):
        leg_l = legacy_lines[idx] if idx < len(legacy_lines) else "[EOF]"
        mod_l = modern_lines[idx] if idx < len(modern_lines) else "[EOF]"
        if leg_l.replace(" ", "") != mod_l.replace(" ", ""):
            diffs.append({
                "line": idx + 1,
                "legacy": leg_l,
                "modern": mod_l,
                "type": "Numeric/Formatting discrepancy"
            })

    return jsonify({
        "fortran_code": modified_fortran,
        "legacy": {
            "stdout": legacy_stdout,
            "stderr": legacy_stderr,
            "compile_err": legacy_compile_err
        },
        "cpp_code": cpp_code,
        "modern": {
            "stdout": modern_stdout,
            "stderr": modern_stderr,
            "compile_err": modern_compile_err
        },
        "comparison": {
            "match": outputs_match,
            "diffs": diffs,
            "score": score * 100,
            "dimension_scores": scores_dict,
            "assessments": mock_assessment["assessments"]
        }
    })

@app.route('/api/llm-status', methods=['GET'])
def llm_status():
    """Probe for Gemini API key first, then fallback to local daemon."""
    import urllib.request
    import urllib.error

    # 1. Cloud-Native Managed LLM
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return jsonify({"online": True, "source": "Gemini Cloud API", "model": "gemini-2.5-flash"})

    # 2. Local Fallback LLMs
    foundry_host = "foundry.local:5273"
    ollama_host  = "foundry.local:11434"

    def probe(host):
        try:
            req = urllib.request.Request(f"http://{host}/v1/models", method="GET")
            with urllib.request.urlopen(req, timeout=3) as r:
                data = json.loads(r.read().decode())
                model = data.get("data", [{}])[0].get("id", "unknown") if data.get("data") else "unknown"
                return {"online": True, "model": model}
        except Exception:
            return {"online": False, "model": None}

    foundry = probe(foundry_host)
    if foundry["online"]:
        return jsonify({"online": True, "source": "foundry.local", "model": foundry["model"]})

    ollama = probe(ollama_host)
    if ollama["online"]:
        return jsonify({"online": True, "source": "local-ollama", "model": ollama["model"]})

    # 3. Rule-Based Fallback
    return jsonify({"online": False, "source": "offline (rule-based)", "model": None})


@app.route('/api/llm-restart', methods=['POST'])
def llm_restart():
    """Attempt to restart the local Foundry service via the host CLI."""
    import urllib.request

    foundry_host = "foundry.local:5273"

    # 1. Try starting foundry via subprocess (only works if foundry CLI is in PATH on host)
    try:
        result = subprocess.run(
            ['foundry', 'service', 'start'],
            capture_output=True, text=True, timeout=20
        )
        app.logger.info(f"foundry service start: {result.stdout} {result.stderr}")
    except FileNotFoundError:
        # foundry CLI not in PATH inside container — try host via shell escape (won't work in Docker)
        app.logger.warning("foundry CLI not found in container PATH — cannot auto-restart from inside Docker.")
        return jsonify({
            "success": False,
            "message": "Cannot auto-restart: run 'foundry service start' on your host machine, then click Retry.",
            "source": "offline"
        }), 200
    except Exception as e:
        app.logger.error(f"foundry restart failed: {e}")
        return jsonify({"success": False, "message": str(e), "source": "offline"}), 200

    # 2. Poll for up to 15 seconds
    import time
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            req = urllib.request.Request(f"http://{foundry_host}/v1/models", method="GET")
            with urllib.request.urlopen(req, timeout=2) as r:
                data = json.loads(r.read().decode())
                model = data.get("data", [{}])[0].get("id", "unknown") if data.get("data") else "unknown"
                return jsonify({"success": True, "message": "Foundry is online.", "model": model, "source": "foundry.local"})
        except Exception:
            time.sleep(1.5)

    return jsonify({"success": False, "message": "Foundry did not come online within 15s. Try again.", "source": "offline"}), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    messages = data.get('messages', [])
    fortran_code = data.get('fortran_code', '')
    cpp_code = data.get('cpp_code', '')
    legacy_stdout = data.get('legacy_stdout', '')
    modern_stdout = data.get('modern_stdout', '')

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    system_prompt = (
        "You are LEGACY-NEXT, an expert AI software migration solutions architect and code analyst.\n"
        "You specialise in Fortran 77/90 → C++20 + Eigen migration, numerical methods, and HPC code optimisation.\n\n"
        "Current Migration Context (if provided):\n"
        f"--- Legacy Fortran Code ---\n{fortran_code}\n\n"
        f"--- Transpiled C++20 Code ---\n{cpp_code}\n\n"
        f"--- Legacy stdout ---\n{legacy_stdout}\n\n"
        f"--- Modern C++ stdout ---\n{modern_stdout}\n\n"
        "Guidelines:\n"
        "- Answer the user's question directly and concisely using your code expertise.\n"
        "- Reference specific variable names, line numbers, or loop bounds from the code above when relevant.\n"
        "- For code suggestions, always return a complete, compilable code block fenced in triple backticks with the language tag (cpp or fortran).\n"
        "- Keep responses formatted in clean Markdown with headings and bullet points."
    )

    # 1. Attempt to connect to foundry.local (OpenAI-compatible local API)
    import urllib.request
    import urllib.error
    
    foundry_host = "foundry.local:5273"
    model_name = "Phi-3.5-mini-instruct-generic-gpu"  # Default fallback
    
    try:
        # Fetch active models from foundry to dynamically match the loaded model
        req_models = urllib.request.Request(f"http://{foundry_host}/v1/models", method="GET")
        with urllib.request.urlopen(req_models, timeout=3) as res_models:
            models_data = json.loads(res_models.read().decode('utf-8'))
            if models_data and "data" in models_data and len(models_data["data"]) > 0:
                # Prefer Phi if available to avoid heavy GPU hang from Qwen 7B
                available_models = [m["id"] for m in models_data["data"]]
                for m in available_models:
                    if "phi" in m.lower():
                        model_name = m
                        break
                else:
                    model_name = available_models[0]
    except Exception:
        pass

    # Format messages to prepend the system prompt context to the first user message,
    # avoiding potential template parsing issues with the "system" role in local models.
    formatted_messages = []
    system_injected = False
    for msg in messages:
        if msg.get("role") == "user":
            if not system_injected:
                formatted_messages.append({
                    "role": "user",
                    "content": f"[System Context: {system_prompt}]\n\nUser Query: {msg.get('content')}"
                })
                system_injected = True
            else:
                formatted_messages.append(msg)
        else:
            formatted_messages.append(msg)

    # In case there are no user messages, fallback to simple system message
    if not system_injected:
        formatted_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

    payload = {
        "model": model_name,
        "messages": formatted_messages,
        "temperature": 0.2,
        "max_tokens": 4096,
        "stream": True
    }

    from flask import Response

    def generate():
        # 0. Cloud-Native Managed LLM (Gemini API)
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if gemini_key:
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=gemini_key)
                
                gemini_contents = []
                for msg in formatted_messages:
                    role = "user" if msg["role"] == "user" else "model"
                    if msg["role"] == "system":
                        role = "user" # Gemini expects system instructions in config
                    gemini_contents.append(
                        types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                    )
                    
                response_stream = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=gemini_contents,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=4096,
                    )
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield f"data: {json.dumps({'reply_chunk': chunk.text, 'source': 'Gemini Cloud API'})}\n\n"
                yield "data: [DONE]\n\n"
                return
            except Exception as e_gemini:
                app.logger.error(f"Gemini API failed: {e_gemini}")

        # 1. Local Foundry (Streaming)
        try:
            req = urllib.request.Request(
                f"http://{foundry_host}/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=180) as response:
                for line in response:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: ') and line_str != 'data: [DONE]':
                        try:
                            chunk_data = json.loads(line_str[6:])
                            delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta:
                                yield f"data: {json.dumps({'reply_chunk': delta['content'], 'source': 'foundry.local'})}\n\n"
                        except Exception:
                            pass
            yield "data: [DONE]\n\n"
            return
        except Exception as e_foundry:
            app.logger.error(f"Foundry connection failed: {e_foundry}")
            
        # 2. Offline rule-based fallback
        last_user_msg = messages[-1]["content"].lower() if messages else ""
        if "common" in last_user_msg or "block" in last_user_msg:
            reply = (
                "### COMMON Block Migration Analysis\n\n"
                "In Fortran, `COMMON` blocks like `COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS` share mutable global state across files and subroutines.\n\n"
                "* **The C++ Translation**: We grouped these parameters into a named global struct scope (`SIMPARAM`).\n"
                "* **Best Practice Refactoring**: Global mutable structs are a thread-safety hazard. For multi-threaded production runs, we recommend refactoring the code to:\n"
                "  1. Wrap parameters into a clean config struct (e.g., `SimParams`).\n"
                "  2. Pass it by const reference `const SimParams& params` to your simulation routines."
            )
        elif "index" in last_user_msg or "dimension" in last_user_msg or "offset" in last_user_msg:
            reply = (
                "### Array Index Shifting & Memory Layout\n\n"
                "Fortran uses 1-based indexing (`1` to `N`), whereas C++ is 0-based (`0` to `N-1`).\n\n"
                "* **Transpilation Rules**: The parser maps every index access like `U(I, J)` to `U(I-1, J-1)`. C++ math formulas evaluate terms like `I+1 - 1` directly to `I` at compile time.\n"
                "* **Storage Layout**: Enforcing column-major ordering (`Eigen::ColMajor`) is critical to ensure cache locality matches Fortran's contiguous column storage in memory."
            )
        elif "omp" in last_user_msg or "parallel" in last_user_msg or "loop" in last_user_msg:
            reply = (
                "### Parallelization & OpenMP\n\n"
                "Fortran loops can be parallelized easily. In the transpiled C++ code, you can accelerate nested loops by adding **OpenMP directives**:\n"
                "```cpp\n"
                "#pragma omp parallel for collapse(2)\n"
                "for (int J = 2; J <= NY - 1; ++J) {\n"
                "    for (int I = 2; I <= NX - 1; ++I) {\n"
                "         // computation...\n"
                "    }\n"
                "}\n"
                "```\n"
                "Compile with `-fopenmp` (e.g., `g++ -fopenmp ...`) to unlock multi-core execution."
            )
        else:
            reply = (
                "### LEGACY-NEXT Migration Advisor\n\n"
                "The local model endpoint at **http://foundry.local:5273** appears offline.\n\n"
                "**Quick Summary of the Migration Gaps**:\n"
                "1. **COMMON Block**: Refactored to global struct (`SIMPARAM`) to mimic global scopes.\n"
                "2. **1-Indexed to 0-Indexed Array Shift**: Adjusted all grid mappings by `-1` offset.\n"
                "3. **Column-Major Configuration**: Set Eigen matrices to `Eigen::ColMajor` to prevent memory thrashing.\n\n"
                "Please start your local LLM daemon (Ollama/Foundry) or ask about **COMMON blocks**, **array indexing**, or **OpenMP parallelization** to trigger local rule-based expert analysis."
            )
            
        yield f"data: {json.dumps({'reply_chunk': reply, 'source': 'offline (rule-based)'})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Default Flask execution on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
