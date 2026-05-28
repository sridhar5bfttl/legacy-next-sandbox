# Fortran Modernization: Analysis & Lessons Learned

This document outlines the step-by-step process of analyzing legacy Fortran codebases using the `LEGACY-NEXT` framework and details critical engineering lessons learned during Fortran-to-Modern migrations.

---

## 1. The Migration Analysis Pipeline

To analyze a specific Fortran codebase, `LEGACY-NEXT` utilizes a structured three-step pipeline:

```mermaid
graph LR
    A[Raw Fortran Code] -->|1. Extract Metadata| B[Metadata JSON]
    B -->|2. Compatibility Assessor| C[Assessment JSON]
    C -->|3. Scoring Engine| D[Confidence Report]
    D -->|4. Transpile & Execute| E[Legacy + Modern Outputs]
    E -->|5. Agent Advisory| F[LLM Chat Q&A]
    F -->|Apply suggestion| E
```

### Step 1: Inventory & Metadata Extraction
First, raw Fortran source files are scanned using the static analyzer prompt ([metadata_extractor.txt](file:///Volumes/superfast/LinkedIn/Classic_Code/prompts/metadata_extractor.txt)). This extracts a syntax-free inventory of:
* Variable definitions and types (e.g., `REAL`, `INTEGER`).
* Array layouts and dimensionality (e.g., `DIMENSION(NX, NY)`).
* Procedural boundaries (`PROGRAM`, `SUBROUTINE`, `FUNCTION`).
* Global state shared via `COMMON` blocks.
* External interfaces (system outputs like `WRITE`, file I/O, library bindings).

### Step 2: Compatibility Assessment Mapping
Next, the metadata inventory is run through the compatibility rules compiler ([compatibility_assessor.txt](file:///Volumes/superfast/LinkedIn/Classic_Code/prompts/compatibility_assessor.txt)) with a chosen modern target stack (e.g., **Python + C++20 / Eigen**). Each construct is categorized by a **Match Level**:
* **🟢 Exact Match (E)**: Directly maps to modern equivalents without structural changes.
* **🟡 Relative Match (M)**: Modern equivalents exist but require code refactoring, adapters, or math library utilities.
* **🔴 Unmet Gap (U)**: Incompatible bindings that require complete architectural redesign.

### Step 3: Numerical Evaluation & Scoring
Finally, the resulting compatibility JSON is evaluated by the scoring engine ([evaluator.py](file:///Volumes/superfast/LinkedIn/Classic_Code/src/evaluator.py)) to compute the overall **Migration Confidence Score ($C$)**:
$$C = 0.20 \cdot S_{Syntax} + 0.30 \cdot S_{Architecture} + 0.30 \cdot S_{Dependencies} + 0.20 \cdot S_{Runtime}$$

---

## 2. Concrete Example: `FLUIDSIM.f` Analysis

We created a sample Fortran 77 fluid simulation program ([FLUIDSIM.f](file:///Volumes/superfast/LinkedIn/Classic_Code/src/FLUIDSIM.f)) and evaluated its modernization profile.

### Scoring Run Results
Running the analyzer engine on `FLUIDSIM.f` yields a **90.0% Confidence Score (High Confidence)**:

* **Syntax & Semantics (Score: 0.80)**:
  * Variable declarations map exactly to C++ standard types (`int`, `double`).
  * Matrix arrays (`U`, `V`, `P`) are relative matches due to indexing and storage order differences.
* **Architecture & State (Score: 0.80)**:
  * Main program flow maps exactly to a C++ `main()` loop calling helper subroutines.
  * Shared state via `COMMON /SIMPARAM/` is a relative match requiring OOP encapsulation.
* **Dependencies & Libraries (Score: 1.00)**:
  * Numerical finite difference loops map exactly to loops or vectorized vector operations.
* **Runtime & Integration (Score: 1.00)**:
  * Scientific print formats map exactly to modern C++ string formatting.

---

## 3. Critical Technical Lessons Learned

When migrating Fortran (particularly Fortran 77/90/95) to modern C++20/Eigen and Python, several key engineering hazards must be handled:

### 1. The Column-Major vs. Row-Major Dilemma
* **The Hazard**: Fortran stores multi-dimensional arrays in **column-major** order (consecutive memory addresses store elements down a column). Modern C++ and standard memory layouts default to **row-major** order (consecutive addresses store elements across a row).
* **The Migration Impact**: Translating loops line-for-line without matching memory layout destroys CPU cache locality, leading to severe memory access performance regressions. It can also cause math bugs if matrix index order is swapped.
* **Lesson & Solution**: When mapping Fortran matrices to the C++ **Eigen** library, explicitly declare the matrix as Column-Major:
  ```cpp
  Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> U(NX, NY);
  ```
  This preserves the layout in memory and allows safe vectorized memory operations.

### 2. The 1-Based to 0-Based Index Shift
* **The Hazard**: Fortran loops and arrays are 1-indexed (`1` to `N`). C++ and Python are 0-indexed (`0` to `N-1`).
* **The Migration Impact**: A simple off-by-one error will result in segfaults, buffer overflows, or silent grid alignment errors.
* **Lesson & Solution**: Loop bounds must be shifted down:
  ```fortran
  DO 100 I = 2, NX - 1
  ```
  Maps in C++ to:
  ```cpp
  for (int i = 1; i < NX - 1; ++i) { // 0-indexed offset applied
  ```
  Ensure all index accesses read `U(i, j)` where `i` and `j` have been decremented by `1` from their Fortran counterparts.

### 3. Encapsulating Shared Globals (`COMMON` Blocks)
* **The Hazard**: Fortran uses `COMMON` blocks to share mutable variables globally. In modern multi-threaded software, this creates race conditions and prevents thread scaling.
* **The Migration Impact**: Migrating simulation logic to run in parallel threads (e.g., executing multiple simulation steps concurrently) will cause corruption if global parameters are modified.
* **Lesson & Solution**: Refactor `COMMON` blocks into configuration structs passed by reference:
  ```cpp
  struct SimParams {
      double dx;
      double dy;
      double dt;
      double reynolds;
  };
  
  void solver(Eigen::MatrixXd& U, Eigen::MatrixXd& V, const SimParams& params);
  ```

### 4. Floating-Point Precision & Accumulative Divergence
* **The Hazard**: Fortran compilers are highly optimized for mathematical expressions, sometimes performing optimizations (like fused multiply-add or register-level precision changes) that differ from modern GCC/Clang compilers.
* **The Migration Impact**: Extremely tiny floating-point rounding discrepancies (e.g., $10^{-16}$) will accumulate over thousands of timesteps in chaotic fluid models, leading to numeric divergence.
* **Lesson & Solution**: Use double-precision floating-points throughout. Write automated integration tests that run the legacy Fortran binary and the new C++ binary on the same initial states, asserting that intermediate outputs match within a tolerance threshold (e.g., `abs(f_val - cpp_val) < 1e-7`).

---

## 4. The Interactive Agent Advisory Step

Once the transpiled code is executing and producing output, the migration is not finished — the developer still needs to understand the *why* behind every transpilation decision, validate edge cases, and iterate on the output. The **LEGACY-NEXT Agent Advisor** formalises this step as a first-class phase in the pipeline.

### When to Use the Agent

| Situation | Example Question |
|:---|:---|
| Understanding a formula | *"Simplify the main solver loop formula for me"* |
| Debugging output divergence | *"Why does the C++ output differ from Fortran at line 3?"* |
| Exploring migration gaps | *"How are COMMON blocks mapped in the C++ code?"* |
| Requesting code improvements | *"Add OpenMP parallelisation to the inner loop"* |
| Verifying numeric precision | *"Is the floating-point precision guaranteed to match Fortran?"* |

### Agent Question Taxonomy

The advisor categorises incoming questions into three tiers automatically:

1. **Explanation queries** — *"What does X do?"* → The LLM answers from the injected migration context (no code change).
2. **Comparison queries** — *"Why does legacy differ from modern here?"* → The LLM cross-references `legacy_stdout` vs `modern_stdout` and points to the diverging line.
3. **Modification queries** — *"Change the solver to use central differences"* → The LLM returns a fenced code block with an **Apply to C++ Editor** button. One click injects it.

### Apply-Code Loop

```
Ask question
    └── LLM returns answer + code block
            └── Click "Apply to C++ Editor"
                    └── Code injected into editor
                            └── Click "Run All"
                                    └── Re-executes both binaries
                                            └── New diff appears in Findings
                                                    └── Ask follow-up
```

This loop replaces manual file editing, reducing the cognitive overhead of context switching between the chat panel and the code editor.

### Lesson Learned: Context Is Everything

The quality of the LLM's answers depends directly on how much migration context is injected per request. In our testing, sending only the user message (without the Fortran source, C++ code, and stdout) produced generic textbook answers. Sending the full context produced accurate, line-specific explanations referencing the actual variable names and loop bounds in `FLUIDSIM.f`.

> **Best Practice**: Always run the sandbox at least once before using the advisor. The agent's answers improve significantly when it has real execution output (`legacy_stdout`, `modern_stdout`) to reason from.

---

## 5. Summary Matrix of Fortran Mappings

| Fortran Feature | Modern C++ / Eigen Equivalent | Difficulty / Match | Key Practice |
| :--- | :--- | :---: | :--- |
| `PARAMETER` | `const` or `constexpr` | 🟢 Exact | Define variables at compile-time to allow optimization. |
| `DIMENSION` / Arrays | `Eigen::Matrix<..., Eigen::ColMajor>` | 🟡 Relative | Enforce column-major ordering to match memory layouts. |
| `COMMON` block | Configuration `struct` / Dependency injection | 🟡 Relative | Eliminate global scopes to allow multi-threaded parallel execution. |
| `DO` loops | `for` loops or parallelized `std::for_each` | 🟢 Exact | Utilize OpenMP (`#pragma omp parallel for`) for rapid CPU scaling. |
| Scientific Print | C++20 `std::format` / `std::print` | 🟢 Exact | Simple formatting string replacements. |
