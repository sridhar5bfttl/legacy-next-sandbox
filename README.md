# LEGACY-NEXT: Legacy-to-Modern Software Compatibility & Translation Framework

## 1. Executive Summary & Overview
Legacy systems represent years of business logic, optimization, and institutional knowledge. However, maintaining obsolete technologies introduces significant technical debt, security vulnerabilities, and a talent shortage. 

`LEGACY-NEXT` is a rigorous, quantitative framework designed to assess the feasibility, risks, and alignment of migrating legacy software components (e.g., COBOL, VB6, legacy Java) to modern platforms (e.g., Java 21/Spring Boot, C#/.NET 8, React). 

By analyzing code structures, architectural alignment, third-party dependencies, and runtime characteristics, `LEGACY-NEXT` generates a **Confidence Score** and categorizes each component's translation status into **Exact Matches**, **Relative Matches**, or **Unmet Gaps**.

---

## 2. The Five-Phase Modernization Lifecycle

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   1. INVENTORY  │ ──> │  2. ASSESSMENT  │ ──> │   3. PLANNING    │ ──> │  4. TRANSLATION  │ ──> │  5. AGENT ADVISOR│
│  Scan & Catalog │     │ Score & Categorize│   │ Design & Adapter │     │ Transpile/Refactor│    │  Q&A & Code Edit │
└─────────────────┘     └─────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
```

1. **Inventory Phase**: Codebases are scanned to index source lines, files, entry points, and dependencies.
2. **Assessment Phase**: Source code structures are evaluated using the compatibility metric to generate a numeric migration confidence score.
3. **Planning & Mapping Phase**: Match levels are mapped. Handlers, wrappers, or adapters are designed for "Relative" matches, and rewrite plans are defined for "Unmet" gaps.
4. **Translation & Verification Phase**: Automated translation prompts translate code, followed by compiling, unit testing, and integration verification.
5. **Interactive Agent Advisory Phase**: A built-in LLM chat advisor allows developers to query the legacy code, transpiled output, and execution results in natural language — and inject approved code changes directly into the editor.

---

## 3. Compatibility & Confidence Scoring Metric

To move away from subjective "gut-feel" estimates, `LEGACY-NEXT` defines the **Migration Confidence Score ($C$)** as a weighted linear combination of four core dimensions:

$$C = w_S \cdot S + w_A \cdot A + w_D \cdot D + w_R \cdot R$$

Where:
* **$S$ (Syntax & Semantics)**: Direct language syntax mapping compatibility (e.g., control flows, primitive data types, functions).
* **$A$ (Architecture & State)**: Structural pattern alignment (e.g., procedural blocks vs. OOP classes, stateful client forms vs. stateless REST APIs).
* **$D$ (Dependencies & Libraries)**: Third-party library and system API replacement coverage.
* **$R$ (Runtime & Integration)**: External interface bindings (e.g., file system I/O, database drivers, OS-specific sockets).

### Dimension Weightings ($w$)
Default weights are assigned based on empirical migration difficulty, but they can be customized per project:
* $w_S = 0.20$ (Syntax is easiest to transpile/refactor)
* $w_A = 0.30$ (Architectural misalignment introduces high rewrite risk)
* $w_D = 0.30$ (Missing dependency libraries block compilation)
* $w_R = 0.20$ (Runtime interfaces dictate system behavior and correctness)

---

## 4. Match Level Categorization

Within each dimension, each individual feature or capability is assessed and classified into one of three **Match Levels**:

### 🟢 Exact Match (E) — Weight: $1.0$
The legacy construct maps directly to a standard target construct with identical semantic behavior and no architectural distortion.
* *Example (COBOL)*: `MOVE A TO B` translates directly to Java's assignment `b = a;`.
* *Example (VB6)*: `If X = Y Then Z` maps to C# `if (x == y) { z; }`.

### 🟡 Relative Match (M) — Weight: $0.6$
The legacy construct has a functional equivalent in the target, but requires structured refactoring, helper classes, adapter patterns, or custom wrappers to maintain behavior.
* *Example (COBOL)*: Fixed-length record parsing (requires a helper class using byte-buffers or Spring Batch flat-file readers).
* *Example (VB6)*: `Recordset.MoveNext` (requires mapping to an Entity Framework enumerator or database cursor helper).

### 🔴 Unmet Gap (U) — Weight: $0.0$
The legacy construct relies on obsolete paradigms, hardware bindings, proprietary platforms, or OS-specific hooks that have no direct or safe equivalence in the target. These require a complete architectural rewrite.
* *Example (COBOL)*: Embedded CICS screen maps or direct mainframe system console interaction.
* *Example (VB6)*: Win32 API DLL injection hooks (`Declare Sub/Function ... Lib "user32"`).

---

## 5. Mathematical Scoring of Dimensions

For any given dimension (e.g., Syntax $S$), the dimension score is computed as:

$$Score = \frac{\sum E + 0.6 \cdot \sum M}{\sum E + \sum M + \sum U}$$

Where:
* $\sum E$ is the count (or structural weight) of elements classified as **Exact**.
* $\sum M$ is the count of elements classified as **Relative**.
* $\sum U$ is the count of elements classified as **Unmet**.

### Confidence Score Interpretation
* **$0.85 - 1.00$ (High Confidence)**: Safe for automated transpilation or direct syntactic migration with minimal manual refactoring.
* **$0.60 - 0.84$ (Moderate Confidence)**: Hybrid approach required. Core logic can be translated, but requires structured adapter layers, code refactoring, and integration testing.
* **$< 0.60$ (Low Confidence / High Risk)**: Rewrite recommended. The architecture and dependencies are too tightly bound to legacy abstractions to be migrated mechanically.

## 5. Interactive Agent Advisory

After translation and verification, developers often need to understand *why* specific transpilation decisions were made, or want to iterate on the output without manually editing files. The **LEGACY-NEXT Agent Advisor** addresses this directly.

### How It Works

The agent is embedded in the sandbox web UI as a persistent chat panel. When a user sends a message, the backend (`/api/chat` in `src/app.py`) enriches the query with live migration context — the current Fortran source, the transpiled C++ code, and both execution outputs — before routing it to the local LLM.

```
┌──────────────┐      POST /api/chat        ┌──────────────────────────────────────────┐
│  Chat Panel  │ ─────────────────────────> │  Flask Backend  (src/app.py)             │
│  (Browser)   │                            │  1. Inject context (Fortran + C++ + logs)│
└──────────────┘                            │  2. Discover active model via /v1/models  │
       ^                                    │  3. POST to LLM with 4096 token budget   │
       │                                    └──────────────┬───────────────────────────┘
       │                                                   │
       │              ┌────────────────────────────────────┼──────────────────────────┐
       │              │  LLM Fallback Chain                 │                          │
       │              │  ① foundry.local:5273 (primary)    │                          │
       │              │  ② foundry.local:11434 (Ollama)    │                          │
       │              │  ③ Rule-based expert fallback       │                          │
       │              └────────────────────────────────────┼──────────────────────────┘
       │                                                   ▼
       └─────────── JSON { reply, source } ────────── Markdown rendered in chat bubble
```

### Apply Code Suggestions Directly to the Editor

When the LLM returns a code block (fenced in triple backticks), the UI automatically detects the language and renders an **Apply** button alongside the code:

- **`Apply to C++ Editor`**: Injects the suggested C++20 code into the modern editor pane and enables the Run button.
- **`Apply to Fortran Editor`**: Injects the suggested Fortran code and auto-triggers a variable re-scan.

This closes the loop between the advisor's natural-language recommendations and the live execution sandbox.

### Agent Context Window

Every user query is automatically augmented with the full migration context. The system injects:

| Context Field | Source |
|:---|:---|
| Legacy Fortran source | Current Fortran editor content |
| Transpiled C++20 source | Current C++ editor content |
| Legacy stdout | Last Fortran binary execution output |
| Modern stdout | Last C++ binary execution output |

### LLM Configuration

| Setting | Value | Rationale |
|:---|:---|:---|
| `max_tokens` | `4096` | Allows complete formula derivations and multi-step explanations |
| `temperature` | `0.2` | Keeps answers deterministic and technically accurate |
| Primary endpoint | `foundry.local:5273` | Local Phi-3.5-mini-instruct (no data leaves the machine) |
| Timeout | `180s` | Accommodates full inference on CPU-constrained local hardware |

---

## 6. Technical & Architectural Challenges in Legacy Migration

Migrating legacy software is not simply a matter of syntax translation. Differences in compilers, runtimes, memory architectures, and concurrency models present severe roadblocks:

### A. Compiled vs. Interpreted Execution Models
*   **The Issue**: Legacy systems often run on highly optimized native compilers (e.g., Fortran, C/C++). Translating this logic directly to dynamic, interpreted languages like Python introduces extreme performance degradation (often 10x to 100x slower execution speeds).
*   **Impact**: Real-time components—such as pipeline SCADA flow calculations or seismic grid algorithms—cannot run in standard interpreted runtimes without compiled extension modules (e.g., Numba, Cython, C++ extensions). This restricts target stack choices to high-performance compiled runtimes like C++20, Rust, or optimized JVM engines.

### B. Deterministic Allocation vs. Automatic Garbage Collection (GC)
*   **The Issue**: Older systems (like Fortran or C) allocate memory deterministically on the stack or through manual heap pointers, ensuring predictable microsecond-level timing. Modern managed target stacks (like Java or C#) use automatic Garbage Collection.
*   **Impact**: Periodic "Stop-the-World" GC cycles introduce unpredictable latency spikes. In safety-critical processes (e.g., refinery DCS controllers or subsea valve loops), these latency spikes can cause safety threshold violations, requiring specialized real-time GC configurations or system rewrites.

### C. Floating-Point & Numeric Precision Discrepancies
*   **The Issue**: Legacy hardware platforms (such as IBM Mainframes) use unique floating-point formats and native Binary Coded Decimal (BCD) representations (e.g., COBOL `COMP-3`).
*   **Impact**: Translating these directly to standard IEEE 754 floating-point datatypes on modern x86 servers introduces rounding anomalies (where base-10 decimals cannot be represented exactly in binary). This creates discrepancy errors in financial accounting or high-precision spatial modeling.

### D. Concurrency Models & The Global Interpreter Lock (GIL)
*   **The Issue**: High-performance legacy modules use low-level compiler parallel directives (like Fortran OpenMP or C threads) to utilize all CPU cores. In contrast, languages like Python have a Global Interpreter Lock (GIL) that prevents concurrent execution of threads on multiple cores.
*   **Impact**: Translating a multi-threaded Fortran simulation directly to Python code blocks will bottleneck execution onto a single thread, rendering the target system unusable for heavy computing unless native multiprocessing or C-binding threads are configured.

### E. Operating System & Hardware Sandbox Lock-In
*   **The Issue**: Legacy programs are often tightly coupled with physical OS services (e.g., Win32 API handles, registry keys in VB6, local serial COM ports, or mainframe CICS terminal controllers).
*   **Impact**: Modern cloud environments mandate deployment within containerized, cross-platform sandboxes (Docker, Kubernetes). Access to local desktop APIs or physical hardware is blocked, requiring a complete rewrite of the system integration layer.

---

## 7. Rationale for Modern Target Technology Selection

Modern target technologies are selected not just based on syntax similarity, but to preserve critical runtime guarantees (concurrency, transactional stability, mathematical precision) while eliminating legacy environment lock-in:

| Legacy Source Stack | Modern Target Stack | Migration Rationale | Preserved Guarantees & Key Improvements |
| :--- | :--- | :--- | :--- |
| **Mainframe COBOL** | Java 21 / Spring Boot 3.x | Mainframe environments process massive volumes of structured batch jobs and concurrent transactions. Spring Boot (incorporating Spring Batch) provides a highly mature, declarative framework that mirrors JCL batch processing steps (readers, processors, and writers). | Java 21's **Virtual Threads (Project Loom)** enable high-throughput concurrency comparable to mainframe transaction processors, while the JVM platform provides the stability and memory safety required for core banking and enterprise records. |
| **VB6 Desktop Form Apps** | C# / .NET 8 + React SPA | VB6 is a Microsoft-proprietary event-driven desktop runtime. C#/.NET 8 is the direct evolutionary successor, retaining native support for legacy COM interoperability and Visual Studio tooling while upgrading the architecture to modern Object-Oriented principles. | React acts as the component-based UI layer, converting VB6 visual forms into browser-rendered stateful elements. C# .NET Web APIs handle backend business logic, decoupling the UI from local operating system event loops. |
| **Fortran 77 / 90 / 95** | Python + C++20 / Eigen | Fortran codebases are numerical processing powerhouses (fluid simulations, seismic modeling). Translating them to dynamic interpreted code (like raw Python) would degrade execution performance by orders of magnitude. | We pair C++20 with the **Eigen** matrix library to preserve Fortran's column-major indexing, memory layouts, and SIMD hardware optimizations. Python wraps this fast compiled core (using Pybind11) to provide scientific developers with an accessible, high-level scripting interface. |
| **ASP Classic** | ASP.NET Core / Blazor | ASP Classic pages combine server-side VBScript with raw HTML, running on IIS. ASP.NET Core is the cross-platform modern successor. | Blazor enables running C# directly in the browser via WebAssembly, preserving the unified single-file rendering model of ASP Classic while eliminating obsolete 32-bit ActiveX/COM+ component registration dependencies. |
| **Java 1.4 / Struts & EJB** | Spring Boot 3.x | Legacy enterprise systems run on early, heavily boilerplate-driven J2EE specifications. | Because Java remains fully backward-compatible, translating syntax from Java 1.4 to Java 21 is a 100% exact match. Spring Boot 3 replaces XML routing and EJB container-managed transactions with clean annotations (e.g., `@RestController`, `@Transactional`), dramatically reducing codebase maintenance overhead. |
| **SCADA/HMI Host Systems** | HTML5 SCADA (Ignition) | Legacy SCADA software relies on local hardware ports, Windows OS drawing threads, and obsolete OPC DA (DCOM) network architectures. | Ignition is built on platform-independent Java and communicates via TCP-based OPC UA and MQTT protocols. It renders operator displays in SVG/HTML5, ensuring high-frequency live status updates can run securely on web browsers without vendor or OS locking. |
| **FoxPro / MS Access** | C# / SQL Server | FoxPro and Access are file-share databases where data corruption occurs when multiple users write to files over network shares. | Migrating data to SQL Server provides transactional ACID compliance, centralized logging, and row-level locking. A C# middle-tier API layer wraps queries, extracting SQL operations out of UI events to prevent SQL injection and connection bottlenecks. |

---

## 9. Directory Layout

| Path | Purpose |
|:---|:---|
| `README.md` | Framework overview, methodology, and agent documentation (this file) |
| `architecture.md` | Pipeline flow and block diagrams including the agent advisory layer |
| `Dockerfile` | Container build: gfortran + g++ + Eigen + Flask |
| `fortran/` | Legacy Fortran source (`FLUIDSIM.f`), metadata JSON, and compatibility report |
| `src/app.py` | Flask backend — transpile, execute, compare, and `/api/chat` agent endpoint |
| `src/translator.py` | Fortran-to-C++20 transpiler (regex-driven pattern mapper) |
| `src/evaluator.py` | Scoring engine computing the Migration Confidence Score $C$ |
| `src/static/index.html` | Web UI shell — editors, terminals, score gauge, and chat panel |
| `src/static/script.js` | Client controller — API calls, markdown renderer, apply-code injection |
| `src/static/styles.css` | Dark-theme design system |
| `skills/` | Migration playbooks for target-specific technology stacks |
| `prompts/` | LLM prompt templates for metadata extraction and compatibility assessment |

---

## 9. Research References & Theoretical Foundations

The assessment dimensions and scoring models in `LEGACY-NEXT` are grounded in the following academic research and engineering publications:

*   **Syntax & Semantics ($S$)**: 
    *   *Unsupervised Translation of Programming Languages* (Lachaux et al., Meta AI) | [arXiv:2006.03511](https://arxiv.org/abs/2006.03511)
    *   Demonstrates the viability of neural machine translation (TransCoder) for mapping syntactic elements between different programming paradigms.
*   **Dependency & Library Coverage ($D$)**:
    *   *ClassEval: A Manually-Crafted Benchmark for Class-Level Code Generation* (Du et al.) | [arXiv:2308.01861](https://arxiv.org/abs/2308.01861)
    *   Highlights the necessity of evaluating class-level contexts and external dependency links (DEP metrics) rather than isolating translation to raw functions.
*   **Architecture & Design Pattern Alignment ($A$)**:
    *   *Code Reborn: Modernizing Legacy Codebases via Agentic Workflows* (General Industry Research) | [arXiv:2504.11335](https://arxiv.org/abs/2504.11335)
    *   Validates that migrating legacy procedural code (e.g., COBOL, VB6) line-for-line creates structural debt ("Jobol"). Proves that agentic workflows are required to refactor business logic into modern architectures.
*   **Runtime & Execution Verification ($R$)**:
    *   *Evaluating Large Language Models Trained on Code* (Chen et al., OpenAI) | [arXiv:2107.03374](https://arxiv.org/abs/2107.03374)
    *   Introduces standard execution-based evaluation benchmarks (HumanEval, pass@k) showing that execution accuracy and unit tests are the only true measures of semantic equivalence.
    *   *CodeBLEU: a Method for Automatic Evaluation of Code Synthesis* (Ren et al., Microsoft Research) | [arXiv:2009.10297](https://arxiv.org/abs/2009.10297)
    *   Establishes the industry standard for scoring code synthesis using Abstract Syntax Trees (AST) and Data-Flow analysis.
