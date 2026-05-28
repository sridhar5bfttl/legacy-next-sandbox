# Fortran-to-Modern Migration Guide & Runbook

This guide details the modernization framework for the 2D fluid flow velocity simulator, explaining input/output structures, build commands, customization configurations, and sandbox options.

---

## 1. Migration Architecture & Associated Files

The migration targets [FLUIDSIM.f](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/FLUIDSIM.f) (legacy Fortran 77) and converts it to [fluidsim_modern.cpp](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/fluidsim_modern.cpp) (modern C++20 + Eigen).

### The Migration Package
All code and configurations are isolated inside the [fortran/](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran) directory:

1. **Legacy Input**: [FLUIDSIM.f](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/FLUIDSIM.f)
   * *What it is*: A Fortran 77 finite-difference numerical simulation updating velocity values `U` and `V` in a 2D grid based on a pressure grid `P`.
2. **Modern Output**: [fluidsim_modern.cpp](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/fluidsim_modern.cpp)
   * *What it is*: A modern C++20 program using the **Eigen** header-only matrix library. It preserves Fortran's column-major ordering, eliminates global state, and wraps logic in modern classes and static structures.
3. **Pipeline Metadata**: [FLUIDSIM_metadata.json](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/FLUIDSIM_metadata.json)
   * *What it is*: The inventory representation of variables, modules, complexity, and dependencies extracted from the Fortran code.
4. **Compatibility Mapping**: [FLUIDSIM_compatibility_report.json](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/FLUIDSIM_compatibility_report.json)
   * *What it is*: The compatibility matrix mapping elements to C++20 equivalents, assigning match levels (`E`, `M`, `U`).

---

## 2. Compilation and Execution Walkthrough

Follow these steps to compile both implementations locally and verify that their outputs match exactly.

### A. Testing the Legacy Fortran Code
To compile and run Fortran code locally, you need a Fortran compiler (e.g., `gfortran` from the GNU Compiler Collection).

1. **Install Compiler**:
   * **macOS (Homebrew)**: `brew install gcc`
   * **Ubuntu/Linux**: `sudo apt install gfortran`
2. **Compile and Run**:
   ```bash
   gfortran -o fluidsim_legacy fortran/FLUIDSIM.f
   ./fluidsim_legacy
   ```
3. **Expected Console Output**:
   ```text
   MIDPOINT U:  1.0000 V:  0.0000 P: 101.3000
   ```

---

### B. Testing the Modernized C++ Code
The modernized C++ codebase utilizes the **Eigen** library for fast matrix calculations.

1. **Install Compiler & Libraries**:
   * **macOS (Homebrew)**: `brew install gcc eigen`
   * **Ubuntu/Linux**: `sudo apt install g++ libeigen-dev`
2. **Compile and Run**:
   Ensure you pass the path to the Eigen header directory using the `-I` flag. On macOS with Homebrew, this is typically `/opt/homebrew/include/eigen3`.
   ```bash
   g++ -std=c++20 -I/opt/homebrew/include/eigen3 -o fluidsim_modern fortran/fluidsim_modern.cpp
   ./fluidsim_modern
   ```
3. **Expected Console Output**:
   ```text
   MIDPOINT U: 1.0000 V: 0.0000 P: 101.3000
   ```

*Note: The output matches the Fortran implementation exactly, verifying that 0-indexed loop conversions, index shifts, and column-major matrix configurations were executed correctly.*

---

## 3. How to Test Custom Variables & Fields

You can customize the parameters of the simulation or the rules of the evaluation framework.

### A. Customizing Simulation Parameters
To test different behaviors, modify the variables within the source files:
* In Fortran ([FLUIDSIM.f](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/FLUIDSIM.f)), edit the parameters (line 6-12) like grid size `NX, NY` or the `DT` step.
* In C++ ([fluidsim_modern.cpp](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/fluidsim_modern.cpp)), modify the `NX` and `NY` constants and the `SimParams` initialization parameters.

### B. Customizing Scoring & Assessment Criteria
To add new features to your compatibility report:
1. Open [FLUIDSIM_compatibility_report.json](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/FLUIDSIM_compatibility_report.json).
2. Add a new element block under any category (e.g., `syntax_and_semantics`). For example:
   ```json
   {
     "element": "Custom File Parser",
     "match_level": "U",
     "rationale": "Uses legacy Fortran OPEN/READ structures which must be rewritten in C++.",
     "target_equivalent": "std::ifstream"
   }
   ```
3. Re-run the evaluation scoring tool from the workspace root:
   ```bash
   python3 src/evaluator.py --file fortran/FLUIDSIM_compatibility_report.json
   ```
4. To modify the scoring dimensions or weights (e.g. giving higher weight to runtime integration), adjust the `DEFAULT_WEIGHTS` dictionary at the top of [evaluator.py](file:///Volumes/superfast/LinkedIn/Classic_Code/src/evaluator.py).

---

## 4. Sandbox & Browser-Based Learning Platforms

If you want to practice legacy coding or compile/test conversions without installing any compilers locally, there are excellent online sandbox platforms available.

### Practicing Legacy Code (Fortran)
* **OnlineGDB compiler**: [onlinegdb.com/online_fortran_compiler](https://www.onlinegdb.com/online_fortran_compiler)
  * *Features*: Full support for Fortran 77, 90, and 95. Includes an online debugger, customizable console parameters, and is completely free. Excellent for testing `FLUIDSIM.f` first.
* **JDoodle Fortran Compiler**: [jdoodle.com/ia-online-compiler-for-fortran](https://www.jdoodle.com/ia-online-compiler-for-fortran)
  * *Features*: Allows you to write and run Fortran scripts on the fly, pass command-line arguments, and share code snippets.
* **Tutorialspoint Coding Ground**: [tutorialspoint.com/compile_fortran_online.php](https://www.tutorialspoint.com/compile_fortran_online.php)
  * *Features*: Quick compiler sandbox for executing legacy scripts in a simulated web shell.

### Practicing and Testing Modern C++ & Libraries
* **Compiler Explorer (Godbolt)**: [godbolt.org](https://godbolt.org)
  * *Features*: The industry-standard tool for testing C++ compilation on the fly. 
  * *How to use with Eigen*: Under **Libraries**, search for **Eigen** and select the latest version. Paste the code from [fluidsim_modern.cpp](file:///Volumes/superfast/LinkedIn/Classic_Code/fortran/fluidsim_modern.cpp) into the editor. You will be able to see the generated assembly instructions and run the program directly in the browser.
* **Replit**: [replit.com](https://replit.com)
  * *Features*: A complete cloud-based IDE. You can create a C++ project, install Eigen (using vcpkg or apt-get), and run/test the entire code suite with an interactive terminal.
* **Google Colab / Jupyter**: [colab.research.google.com](https://colab.research.google.com)
  * *Features*: You can create a notebook, write code blocks in Fortran (using `%%fortran` extension), write C++ blocks, compile them locally on Google's cloud server, and visualize the output grid using matplotlib in Python.
