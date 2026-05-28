// LEGACY-NEXT Client controller
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const btnLoadSample = document.getElementById('btn-load-sample');
    const btnScan = document.getElementById('btn-scan');
    const btnTranspile = document.getElementById('btn-transpile');
    const btnRunAll = document.getElementById('btn-run-all');
    const fortranEditor = document.getElementById('fortran-editor');
    const cppEditor = document.getElementById('cpp-editor');
    const dynamicInputs = document.getElementById('dynamic-inputs');
    const legacyStdout = document.getElementById('legacy-stdout');
    const modernStdout = document.getElementById('modern-stdout');
    const matchStatus = document.getElementById('match-status');
    const matchStatusCard = document.getElementById('match-status-card');
    const riskProfile = document.getElementById('risk-profile');
    const scoreText = document.getElementById('score-text');
    const scoreGauge = document.getElementById('score-gauge');
    const findingsContainer = document.getElementById('findings-container');
    const sandboxStatus = document.getElementById('sandbox-status');
    const btnExpandOutput = document.getElementById('btn-expand-output');

    // ── Drag-to-Resize: Dashboard ↕ Agent panels ─────────────────────────
    (function initResizablePanels() {
        const handle       = document.getElementById('resize-handle');
        const dashPanel    = document.getElementById('dashboard-panel');
        const agentPanel   = document.getElementById('agent-panel');
        const container    = document.getElementById('resizable-panels');

        if (!handle || !dashPanel || !agentPanel || !container) return;

        const MIN_DASH  = 120;  // px minimum for dashboard
        const MIN_AGENT = 120;  // px minimum for agent

        // Restore saved heights from last session
        const savedDash = localStorage.getItem('ln-dash-height');
        if (savedDash) {
            dashPanel.style.height  = savedDash + 'px';
            dashPanel.style.flex    = '0 0 auto';
        } else {
            // Set sensible default split: 40% dashboard / 60% agent
            const totalH = container.clientHeight - 10; // minus handle
            dashPanel.style.height = Math.round(totalH * 0.40) + 'px';
            dashPanel.style.flex   = '0 0 auto';
        }

        let dragging    = false;
        let startY      = 0;
        let startDashH  = 0;

        function onDragStart(e) {
            dragging   = true;
            startY     = (e.touches ? e.touches[0].clientY : e.clientY);
            startDashH = dashPanel.getBoundingClientRect().height;
            handle.classList.add('dragging');
            document.body.style.cursor    = 'ns-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        }

        function onDragMove(e) {
            if (!dragging) return;
            const clientY  = e.touches ? e.touches[0].clientY : e.clientY;
            const delta    = clientY - startY;
            const containerH = container.clientHeight - 10;
            const maxDash  = containerH - MIN_AGENT;
            const newDash  = Math.min(maxDash, Math.max(MIN_DASH, startDashH + delta));
            dashPanel.style.height = newDash + 'px';
            e.preventDefault();
        }

        function onDragEnd() {
            if (!dragging) return;
            dragging = false;
            handle.classList.remove('dragging');
            document.body.style.cursor     = '';
            document.body.style.userSelect = '';
            // Persist for next session
            localStorage.setItem('ln-dash-height', Math.round(dashPanel.getBoundingClientRect().height));
        }

        handle.addEventListener('mousedown',  onDragStart, { passive: false });
        handle.addEventListener('touchstart', onDragStart, { passive: false });
        document.addEventListener('mousemove',  onDragMove,  { passive: false });
        document.addEventListener('touchmove',  onDragMove,  { passive: false });
        document.addEventListener('mouseup',    onDragEnd);
        document.addEventListener('touchend',   onDragEnd);

        // Double-click to reset to default 40/60 split
        handle.addEventListener('dblclick', () => {
            const totalH = container.clientHeight - 10;
            dashPanel.style.height = Math.round(totalH * 0.40) + 'px';
            localStorage.removeItem('ln-dash-height');
        });
    })();

    // ── Expand/Collapse Output Section ──────────────────────────────────────
    if (btnExpandOutput) {
        btnExpandOutput.addEventListener('click', () => {
            const grid = document.querySelector('.workspace-grid');
            const icon = document.getElementById('expand-icon');
            const text = document.getElementById('expand-text');
            
            grid.classList.toggle('output-expanded');
            
            if (grid.classList.contains('output-expanded')) {
                icon.innerText = '⤡';
                text.innerText = 'Collapse View';
                btnExpandOutput.title = 'Restore standard layout';
            } else {
                icon.innerText = '⤢';
                text.innerText = 'Expand View';
                btnExpandOutput.title = 'Toggle full-width view';
            }
        });
    }

    // Sample code content
    const sampleFortranCode = `C     ==================================================================
C     FLUIDSIM.F - TWO-DIMENSIONAL SIMULATION OF FLUID FLOW VELOCITY
C     ==================================================================
      PROGRAM FLUIDSIM
      INTEGER NX, NY, I, J, STEPS
      PARAMETER (NX=10, NY=10)
      REAL U(NX, NY), V(NX, NY), P(NX, NY)
      
C     COMMON BLOCK FOR GLOBAL SYSTEM PARAMETERS
      COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS
      
C     INITIALIZE PHYSICAL PARAMETERS
      DX = 0.1
      DY = 0.1
      DT = 0.01
      REYNOLDS = 100.0
      STEPS = 5
      
C     INITIALIZE GRID VALUES
      DO 20 J = 1, NY
        DO 10 I = 1, NX
          U(I, J) = 1.0
          V(I, J) = 0.0
          P(I, J) = 101.3
10      CONTINUE
20    CONTINUE
      
C     RUN INTERATIVE SOLVER LOOP
      DO 100 I = 1, STEPS
        CALL SOLVER(U, V, P, NX, NY)
100   CONTINUE
      
C     PRINT FINAL RESULTS
      WRITE(*, 9000) U(NX/2, NY/2), V(NX/2, NY/2), P(NX/2, NY/2)
9000  FORMAT('MIDPOINT U:', F8.4, ' V:', F8.4, ' P:', F8.4)
      
      END
      
C     ==================================================================
C     SOLVER SUBROUTINE - UPDATES GRID VALUES BASED ON FINITE DIFFERENCE
C     ==================================================================
      SUBROUTINE SOLVER(U, V, P, NX, NY)
      INTEGER NX, NY, I, J
      REAL U(NX, NY), V(NX, NY), P(NX, NY)
      COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS
      
C     COMPUTE NEXT STEP (SIMPLIFIED PRESSURE CORRECTION)
      DO 200 J = 2, NY - 1
        DO 190 I = 2, NX - 1
          U(I, J) = U(I, J) - DT * (P(I+1, J) - P(I-1, J)) / (2.0 * DX)
          V(I, J) = V(I, J) - DT * (P(I, J+1) - P(I, J-1)) / (2.0 * DY)
190     CONTINUE
200   CONTINUE
      
      RETURN
      END`;

    // Global state
    let detectedVariables = {};

    // 1. Initialize
    fortranEditor.addEventListener('input', toggleButtons);

    // Load sample program
    btnLoadSample.addEventListener('click', () => {
        fortranEditor.value = sampleFortranCode;
        toggleButtons();
        scanVariables();
    });

    // Scan Variables Button
    btnScan.addEventListener('click', scanVariables);

    // Transpile Button
    btnTranspile.addEventListener('click', transpileCode);

    // Run All Button
    btnRunAll.addEventListener('click', executeCompare);

    function toggleButtons() {
        const hasCode = fortranEditor.value.trim().length > 0;
        btnScan.disabled = !hasCode;
        btnTranspile.disabled = !hasCode;
    }

    // Call API to analyze variables
    async function scanVariables() {
        const code = fortranEditor.value;
        if (!code) return;

        showStatus("Scanning variables...", "yellow");
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            const data = await response.json();
            
            if (data.variables) {
                detectedVariables = data.variables;
                renderInputs(data.variables);
                showStatus("Scan complete. Parameters loaded.", "green");
            }
        } catch (error) {
            console.error("Analysis failed:", error);
            showStatus("Scan failed.", "red");
        }
    }

    // Render configuration inputs on the UI
    function renderInputs(variables) {
        dynamicInputs.innerHTML = '';
        const keys = Object.keys(variables);
        
        if (keys.length === 0) {
            dynamicInputs.innerHTML = '<p class="empty-inputs-msg">No customizable variables detected in code.</p>';
            return;
        }

        keys.forEach(key => {
            const item = variables[key];
            const div = document.createElement('div');
            div.className = 'input-item';
            div.innerHTML = `
                <label for="input-${key}" title="${item.description}">${key}</label>
                <input type="text" id="input-${key}" value="${item.value}" data-key="${key}">
            `;
            dynamicInputs.appendChild(div);
        });
    }

    // Call API to transpile code
    async function transpileCode() {
        const code = fortranEditor.value;
        if (!code) return;

        showStatus("Transpiling code...", "yellow");
        cppEditor.value = "Translating Fortran patterns...";
        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    code,
                    inputs: {} // Dry run, only mapping code structure
                })
            });
            const data = await response.json();
            
            if (data.cpp_code) {
                cppEditor.value = data.cpp_code;
                btnRunAll.disabled = false;
                showStatus("Transpilation successful.", "green");
            } else {
                cppEditor.value = `Translation Error:\n${data.modern.compile_err || 'Unknown error'}`;
                showStatus("Transpilation failed.", "red");
            }
        } catch (error) {
            console.error("Transpilation failed:", error);
            cppEditor.value = "Error during transpilation api call.";
            showStatus("Transpilation call error.", "red");
        }
    }

    // Call API to execute code and run comparisons
    async function executeCompare() {
        const code = fortranEditor.value;
        if (!code) return;

        // Gather user override values
        const inputs = {};
        const inputElements = dynamicInputs.querySelectorAll('input');
        inputElements.forEach(el => {
            inputs[el.dataset.key] = el.value.trim();
        });

        // Set UI execution status
        showStatus("Executing simulation run...", "yellow");
        legacyStdout.innerHTML = '<pre class="stdout-text">Compiling and running legacy binary...</pre>';
        modernStdout.innerHTML = '<pre class="stdout-text">Compiling and running C++ binary...</pre>';
        
        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, inputs })
            });
            const data = await response.json();
            
            // Render outputs
            renderLegacyOutput(data.legacy);
            renderModernOutput(data.modern);
            
            if (data.cpp_code) {
                cppEditor.value = data.cpp_code;
            }

            // Render dashboard metrics
            if (data.comparison) {
                updateDashboard(data.comparison, data.legacy, data.modern);
                showStatus("Execution and audit complete.", "green");
            }
        } catch (error) {
            console.error("Execution call failed:", error);
            showStatus("Sandbox execution error.", "red");
        }
    }

    function renderLegacyOutput(legacy) {
        if (legacy.compile_err) {
            legacyStdout.innerHTML = `<pre class="compile-err-text">Compilation Error:\n${legacy.compile_err}</pre>`;
        } else if (legacy.stderr) {
            legacyStdout.innerHTML = `<pre class="stderr-text">Runtime Error:\n${legacy.stderr}</pre>`;
        } else {
            legacyStdout.innerHTML = `<pre class="stdout-text">${legacy.stdout || '[No terminal output]'}</pre>`;
        }
    }

    function renderModernOutput(modern) {
        if (modern.compile_err) {
            modernStdout.innerHTML = `<pre class="compile-err-text">Compilation Error:\n${modern.compile_err}</pre>`;
        } else if (modern.stderr) {
            modernStdout.innerHTML = `<pre class="stderr-text">Runtime Error:\n${modern.stderr}</pre>`;
        } else {
            modernStdout.innerHTML = `<pre class="stdout-text">${modern.stdout || '[No terminal output]'}</pre>`;
        }
    }

    function updateDashboard(comparison, legacy, modern) {
        // 1. Update match gauge
        const rawScore = comparison.score;
        const scoreDisp = rawScore.toFixed(2);
        scoreText.innerText = `${scoreDisp}%`;
        
        // Progress ring: radius=50, circumference = 2 * PI * 50 = 314.15
        const offset = 314.15 - (rawScore / 100) * 314.15;
        scoreGauge.style.strokeDashoffset = offset;

        // Color coding progress bar
        if (rawScore >= 85) {
            scoreGauge.style.stroke = "#10b981"; // success green
        } else if (rawScore >= 60) {
            scoreGauge.style.stroke = "#f59e0b"; // warning yellow
        } else {
            scoreGauge.style.stroke = "#ef4444"; // error red
        }

        // 2. Execution Match Badge
        matchStatusCard.className = 'status-card';
        if (legacy.compile_err || modern.compile_err) {
            matchStatus.innerText = "Compile Error";
            matchStatusCard.classList.add('mismatched');
        } else if (comparison.match) {
            matchStatus.innerText = "Success (Matched)";
            matchStatusCard.classList.add('matched');
        } else {
            matchStatus.innerText = "Mismatch Detected";
            matchStatusCard.classList.add('mismatched');
        }

        // 3. Risk Profile
        if (rawScore >= 85) {
            riskProfile.innerText = "Low Risk (Safe)";
            riskProfile.style.color = "var(--success)";
        } else if (rawScore >= 60) {
            riskProfile.innerText = "Medium Risk";
            riskProfile.style.color = "var(--warning)";
        } else {
            riskProfile.innerText = "High Risk (Rewrite)";
            riskProfile.style.color = "var(--error)";
        }

        // 4. Detailed findings log
        findingsContainer.innerHTML = '';
        
        // Compile status finding
        addFinding(
            legacy.compile_err ? "red" : "green",
            legacy.compile_err ? "Legacy Fortran compiler failed to build binary." : "Legacy Fortran compilation succeeded."
        );
        addFinding(
            modern.compile_err ? "red" : "green",
            modern.compile_err ? "Modern C++20 compiler failed to build." : "Modern C++20 + Eigen compilation succeeded."
        );

        // Verification comparison finding
        if (!legacy.compile_err && !modern.compile_err) {
            if (comparison.match) {
                addFinding(
                    "green",
                    "Success: Output matrices match exactly down to 4 decimal precision."
                );
            } else {
                addFinding(
                    "red",
                    `Numerical divergence detected. ${comparison.diffs.length} discrepancy values identified.`
                );
                // Detail diffs
                comparison.diffs.forEach(diff => {
                    addFinding(
                        "yellow",
                        `Line ${diff.line} - Legacy: "${diff.legacy.trim()}" | C++20: "${diff.modern.trim()}"`
                    );
                });
            }
        }

        // Leftover Gaps Section (The remaining 10%)
        const gapsHeader = document.createElement('h4');
        gapsHeader.innerText = `The Leftover Gaps (Representing the remaining ${(100 - rawScore).toFixed(2)}%)`;
        gapsHeader.style.marginTop = "14px";
        gapsHeader.style.marginBottom = "8px";
        gapsHeader.style.color = "var(--accent)";
        gapsHeader.style.fontSize = "0.75rem";
        gapsHeader.style.fontWeight = "600";
        gapsHeader.style.textTransform = "uppercase";
        gapsHeader.style.letterSpacing = "0.5px";
        findingsContainer.appendChild(gapsHeader);

        let gapCount = 0;
        const assessments = comparison.assessments || {};
        for (const dim in assessments) {
            const items = assessments[dim];
            const dimName = dim.replace(/_/g, ' ').toUpperCase();
            items.forEach(item => {
                if (item.match_level === 'M' || item.match_level === 'U') {
                    gapCount++;
                    const bulletColor = item.match_level === 'U' ? 'red' : 'yellow';
                    const gapDiv = document.createElement('div');
                    gapDiv.className = 'gap-detail-item';
                    gapDiv.style.marginBottom = "10px";
                    gapDiv.style.paddingLeft = "8px";
                    gapDiv.style.borderLeft = `2px solid var(--${bulletColor === 'red' ? 'error' : 'warning'})`;
                    gapDiv.innerHTML = `
                        <div style="font-weight: 600; color: #f8fafc; font-size: 0.8rem; line-height: 1.3;">
                            ${gapCount}. ${item.element} (${dimName})
                        </div>
                        <div style="color: var(--color-text-muted); font-size: 0.75rem; margin-top: 2px; line-height: 1.35;">
                            <strong>The Gap:</strong> ${item.rationale}
                        </div>
                        <div style="color: var(--success); font-size: 0.75rem; margin-top: 2px; line-height: 1.35;">
                            <strong>How we bridged it:</strong> ${item.target_equivalent}
                        </div>
                    `;
                    findingsContainer.appendChild(gapDiv);
                }
            });
        }

        if (gapCount === 0) {
            const noGaps = document.createElement('p');
            noGaps.innerText = "No outstanding migration gaps detected.";
            noGaps.style.color = "var(--success)";
            noGaps.style.fontSize = "0.75rem";
            findingsContainer.appendChild(noGaps);
        }

        // Mathematical Proof Section
        const mathHeader = document.createElement('h4');
        mathHeader.innerText = "Mathematical Proof of the Score";
        mathHeader.style.marginTop = "14px";
        mathHeader.style.marginBottom = "8px";
        mathHeader.style.color = "var(--accent)";
        mathHeader.style.fontSize = "0.75rem";
        mathHeader.style.fontWeight = "600";
        mathHeader.style.textTransform = "uppercase";
        mathHeader.style.letterSpacing = "0.5px";
        findingsContainer.appendChild(mathHeader);

        const dimScores = comparison.dimension_scores || {};
        const s_syntax = (dimScores.syntax_and_semantics || 1.0).toFixed(2);
        const s_arch = (dimScores.architecture_and_state || 1.0).toFixed(2);
        const s_dep = (dimScores.dependencies_and_libraries || 1.0).toFixed(2);
        const s_run = (dimScores.runtime_and_integration || 1.0).toFixed(2);

        const mathDiv = document.createElement('div');
        mathDiv.className = 'math-proof-item';
        mathDiv.style.fontFamily = "var(--font-mono)";
        mathDiv.style.fontSize = "0.7rem";
        mathDiv.style.color = "var(--color-text-muted)";
        mathDiv.style.background = "rgba(0, 0, 0, 0.3)";
        mathDiv.style.padding = "8px";
        mathDiv.style.borderRadius = "var(--radius-sm)";
        mathDiv.style.border = "1px solid var(--border-color)";
        mathDiv.style.lineHeight = "1.4";
        mathDiv.innerHTML = `
            <div>C = 0.20*S_Syntax + 0.30*S_Arch + 0.30*S_Deps + 0.20*S_Run</div>
            <div style="margin-top: 4px; color: #e2e8f0;">
                S_Syntax: ${s_syntax} | S_Arch: ${s_arch} | S_Deps: ${s_dep} | S_Run: ${s_run}
            </div>
            <div style="margin-top: 4px; color: var(--success); font-weight: 500;">
                C = (0.20*${s_syntax}) + (0.30*${s_arch}) + (0.30*${s_dep}) + (0.20*${s_run}) = ${(rawScore/100).toFixed(4)} (${scoreDisp}%)
            </div>
        `;
        findingsContainer.appendChild(mathDiv);
    }

    function addFinding(color, text) {
        const item = document.createElement('div');
        item.className = 'finding-item';
        item.innerHTML = `
            <span class="finding-bullet ${color}"></span>
            <span class="finding-text">${text}</span>
        `;
        findingsContainer.appendChild(item);
    }

    function showStatus(text, color) {
        sandboxStatus.innerText = text;
        const dot = sandboxStatus.previousElementSibling;
        dot.className = `status-dot ${color}`;
    }


    // Add user message to UI
        appendMessage('user', text);
        messageHistory.push({ role: 'user', content: text });

        // Add loading typing indicator
        const typingIndicator = appendTypingIndicator();
        chatHistory.scrollTop = chatHistory.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: messageHistory,
                    fortran_code: fortranEditor.value,
                    cpp_code: cppEditor.value,
                    legacy_stdout: legacyStdout.innerText,
                    modern_stdout: modernStdout.innerText
                })
            });
            const data = await response.json();
            
            // Remove indicator
            typingIndicator.remove();

            if (data.reply) {
                appendMessage('assistant', data.reply);
                messageHistory.push({ role: 'assistant', content: data.reply });

                // Sync health indicator with what the backend actually used
                const src = data.source || 'offline';
                if (src === 'foundry.local') {
                    setLlmState(true, 'foundry.local', null);
                } else if (src === 'local-ollama') {
                    setLlmState(true, 'local-ollama', null);
                } else {
                    // rule-based-fallback means LLM was unreachable
                    setLlmState(false, 'offline', null);
                }
            } else {
                appendMessage('assistant', 'Error: Received empty response from translation advisor.');
            }
        } catch (error) {
            console.error("Chat call failed:", error);
            typingIndicator.remove();
            appendMessage('assistant', 'Error: Unable to connect to LLM translation advisor.');
            setLlmState(false, 'offline', null);
        }

        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function appendMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${role}`;

        // Use a placeholder token to protect code block HTML from the newline-to-br pass
        const CODE_PLACEHOLDER_PREFIX = '\x00CODE_BLOCK_';
        const codeBlocks = [];

        // Step 1: Escape HTML in the raw content first
        let htmlContent = content
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Step 2: Extract code blocks (```lang\ncode```) into placeholders
        htmlContent = htmlContent.replace(/```(\w*)\n?([\s\S]*?)```/g, (match, lang, code) => {
            const trimmedCode = code.trim();
            const cleanLang = lang ? lang.toLowerCase() : '';

            let buttonHtml = '';
            let buttonClass = 'btn-accent';
            let buttonText = 'Apply to C++ Editor';
            let editorType = 'cpp';

            if (cleanLang === 'fortran' || cleanLang === 'f' || cleanLang === 'f77' || cleanLang === 'f90') {
                buttonText = 'Apply to Fortran Editor';
                editorType = 'fortran';
                buttonClass = 'btn-secondary';
            }

            const encodedCode = btoa(unescape(encodeURIComponent(trimmedCode)));

            let applyBtn = '';
            if (role === 'assistant') {
                applyBtn = `<button class="btn btn-sm ${buttonClass} apply-code-btn"
                    data-editor="${editorType}"
                    data-code="${encodedCode}"
                    onclick="applyCodeFromChat(this)"
                    style="margin-top:6px;display:block;font-size:0.7rem;padding:4px 8px;">
                    ${buttonText}
                </button>`;
            }

            const blockHtml = `<div class="chat-code-container" style="position:relative;margin:8px 0;">
                <pre style="background:rgba(0,0,0,0.4);padding:8px;border-radius:4px;font-family:var(--font-mono);font-size:0.75rem;overflow-x:auto;white-space:pre;border:1px solid var(--border-color);">${trimmedCode}</pre>
                ${applyBtn}
            </div>`;

            codeBlocks.push(blockHtml);
            return `${CODE_PLACEHOLDER_PREFIX}${codeBlocks.length - 1}\x00`;
        });

        // Step 3: Process inline Markdown on the text portions only
        htmlContent = htmlContent
            .replace(/`([^`\n]+)`/g, "<code style='background:rgba(0,0,0,0.4);padding:2px 4px;border-radius:3px;font-family:var(--font-mono);font-size:0.75rem;'>$1</code>")
            .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
            .replace(/^###\s+(.+)$/gm, "<h5 style='color:var(--accent);margin-top:10px;margin-bottom:4px;font-weight:600;'>$1</h5>")
            .replace(/^##\s+(.+)$/gm, "<h4 style='color:var(--accent);margin-top:12px;margin-bottom:4px;font-weight:700;'>$1</h4>")
            .replace(/^#\s+(.+)$/gm, "<h3 style='color:var(--accent);margin-top:14px;margin-bottom:6px;font-weight:700;'>$1</h3>")
            .replace(/^\s*[-*]\s+(.+)$/gm, "<li style='margin-left:16px;margin-bottom:2px;'>$1</li>")
            .replace(/(<li[^>]*>.*<\/li>\n?)+/g, m => `<ul style='margin:4px 0;padding-left:8px;'>${m}</ul>`)
            .replace(/\n/g, "<br>");

        // Step 4: Restore code blocks from placeholders
        htmlContent = htmlContent.replace(new RegExp(`${CODE_PLACEHOLDER_PREFIX}(\\d+)\x00`, 'g'), (_, idx) => codeBlocks[parseInt(idx)]);

        msgDiv.innerHTML = `<div class="msg-bubble" style="overflow-wrap:break-word;word-break:break-word;">${htmlContent}</div>`;
        chatHistory.appendChild(msgDiv);
    }

    function appendTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        chatHistory.appendChild(div);
        return div;
    }

    // Auto-load sample program on startup so the UI isn't empty
    setTimeout(() => {
        if (btnLoadSample && fortranEditor.value.trim() === '') {
            btnLoadSample.click();
        }
    }, 100);
});

// Global callback for applying code snippets from chat to editor panels
window.applyCodeFromChat = function(btn) {
    const editorType = btn.dataset.editor;
    const encodedCode = btn.dataset.code;
    
    try {
        const decodedCode = decodeURIComponent(escape(atob(encodedCode)));
        
        if (editorType === 'fortran') {
            const fortranEditor = document.getElementById('fortran-editor');
            if (fortranEditor) {
                fortranEditor.value = decodedCode;
            }
            
            // Show status and trigger scan
            btn.innerText = 'Applied to Fortran!';
            btn.disabled = true;
            btn.style.background = 'var(--success)';
            
            // Auto click scan
            setTimeout(() => {
                const btnScan = document.getElementById('btn-scan');
                if (btnScan) btnScan.click();
            }, 300);
        } else {
            const cppEditor = document.getElementById('cpp-editor');
            if (cppEditor) {
                cppEditor.value = decodedCode;
            }
            
            btn.innerText = 'Applied to C++!';
            btn.disabled = true;
            btn.style.background = 'var(--success)';
            
            // Enable run button
            const btnRunAll = document.getElementById('btn-run-all');
            if (btnRunAll) btnRunAll.disabled = false;
            
            // Notify user
            const sandboxStatus = document.getElementById('sandbox-status');
            if (sandboxStatus) {
                sandboxStatus.innerText = 'C++ code updated. Ready to run.';
                const dot = sandboxStatus.previousElementSibling;
                if (dot) dot.className = 'status-dot green';
            }
        }
    } catch (error) {
        console.error("Failed to apply code:", error);
        btn.innerText = 'Failed to Apply';
        btn.style.background = 'var(--error)';
    }
};
