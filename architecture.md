# LEGACY-NEXT: Architecture Diagrams

This document contains visual diagrams mapping out the migration assessment pipeline and the internal architecture of the evaluation agent.

## 1. Migration Assessment Pipeline

This flowchart outlines the progression of source code from ingestion, syntax parsing, and AI-driven capability mapping to score calculation, target code generation, and interactive agent review.

```mermaid
graph TD
    subgraph Input Phase
        A[Legacy Source Code] --> B[Static Analyzer / Parser]
        B --> C[Extract Syntax, Dependencies & System Calls]
    end

    subgraph Evaluation Phase
        C --> D[LLM Metadata Extractor]
        D --> E[Structured Module Metadata JSON]
        E --> F[LLM Compatibility Assessor]
        G[(Target Tech Capability Matrix)] --> F
        F --> H[Classified Mappings JSON]
    end

    subgraph Scoring Phase
        H --> I[LEGACY-NEXT Scoring Engine]
        I --> J{Confidence Score C}
        J -->|C >= 0.85| K[High: Transpiler / Direct Rewrite]
        J -->|0.60 <= C < 0.85| L[Medium: Hybrid Adapter Refactoring]
        J -->|C < 0.60| M[Low: Complete System Redesign]
    end

    subgraph Translation Phase
        K --> N[Translation Engine & Unit Test Generator]
        L --> N
        M --> O[Manual Target Architecture Blueprints]
    end

    subgraph Agent Advisory Phase
        N --> P[Interactive Chat Advisor]
        O --> P
        P --> Q{Developer Action}
        Q -->|Apply suggestion| R[Code Injected into Editor]
        Q -->|Ask follow-up| P
        R --> S[Re-run Sandbox & Verify]
        S --> P
    end
```

---

## 2. Assessment Agent Architecture

This block diagram represents the logical components of the assessment tool, showing how it orchestrates files, external knowledge systems, prompts, and the scoring system.

```mermaid
graph LR
    subgraph Local Workspace
        Code[Legacy Codebases]
        Config[Target Rules Config]
    end

    subgraph Orchestrator [LEGACY-NEXT Flask Backend]
        Parser[Code Scanner]
        PromptEng[Prompt Compiler]
        Engine[Score Evaluator]
        ChatRouter["/api/chat Router"]
    end

    subgraph LLM Services
        Foundry["foundry.local:5273 (Phi-3.5)"]
        Ollama["foundry.local:11434 (Ollama)"]
        RuleFB["Rule-Based Fallback"]
    end

    subgraph Knowledge Base
        Rules[Compatibility Rules Database]
    end

    subgraph Web UI [Browser Client]
        EditorPanel[Fortran & C++ Editors]
        ChatPanel[Chat Advisor Panel]
        ApplyBtn[Apply Code to Editor]
    end

    Code --> Parser
    Parser --> PromptEng
    Config --> Rules
    Rules --> PromptEng
    PromptEng --> Engine
    Engine --> Report[Migration Compatibility Report]

    EditorPanel --> ChatRouter
    ChatPanel --> ChatRouter
    ChatRouter --> Foundry
    Foundry -->|fallback| Ollama
    Ollama -->|fallback| RuleFB
    Foundry --> ChatPanel
    Ollama --> ChatPanel
    RuleFB --> ChatPanel
    ChatPanel --> ApplyBtn
    ApplyBtn --> EditorPanel
```

---

## 3. Interactive Agent Advisory — Request & Response Flow

This sequence diagram shows the exact flow of a single chat message from the browser to the local LLM and back, including context injection and code-apply confirmation.

```mermaid
sequenceDiagram
    actor Developer
    participant Browser as Browser (Chat Panel)
    participant Flask as Flask Backend<br/>/api/chat
    participant Foundry as foundry.local:5273<br/>(Phi-3.5-mini)
    participant Ollama as foundry.local:11434<br/>(Ollama fallback)

    Developer->>Browser: Type question & press Send
    Browser->>Flask: POST /api/chat<br/>{ messages, fortran_code, cpp_code,<br/>  legacy_stdout, modern_stdout }

    Flask->>Foundry: GET /v1/models (discover active model)
    Foundry-->>Flask: { "id": "Phi-3.5-mini-instruct-generic-gpu" }

    Flask->>Foundry: POST /v1/chat/completions<br/>{ model, messages+context, max_tokens: 4096 }

    alt Foundry responds within 180s
        Foundry-->>Flask: { choices[0].message.content }
        Flask-->>Browser: { "reply": "...", "source": "foundry.local" }
    else Foundry timeout or error
        Flask->>Ollama: POST /v1/chat/completions (fallback)
        alt Ollama responds
            Ollama-->>Flask: { choices[0].message.content }
            Flask-->>Browser: { "reply": "...", "source": "local-ollama" }
        else Ollama also unavailable
            Flask-->>Browser: { "reply": "<rule-based answer>", "source": "rule-based-fallback" }
        end
    end

    Browser->>Browser: Render Markdown reply<br/>(headings, code blocks, lists)
    opt Reply contains a code block
        Browser->>Developer: Show "Apply to C++/Fortran Editor" button
        Developer->>Browser: Click Apply
        Browser->>Browser: Inject code into editor pane
        Browser->>Browser: Enable Run / Re-scan button
    end
```
