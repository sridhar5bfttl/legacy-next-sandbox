#!/usr/bin/env python3
import json
import sys
import argparse

# Default weights
DEFAULT_WEIGHTS = {
    "syntax_and_semantics": 0.20,
    "architecture_and_state": 0.30,
    "dependencies_and_libraries": 0.30,
    "runtime_and_integration": 0.20
}

# Match weights
MATCH_WEIGHTS = {
    "E": 1.0,  # Exact Match
    "M": 0.6,  # Relative Match
    "U": 0.0   # Unmet Gap
}

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BOLD = "\033[1m"
COLOR_CYAN = "\033[96m"

def get_match_tag(level):
    if level == "E":
        return f"{COLOR_GREEN}[Exact]{COLOR_RESET}"
    elif level == "M":
        return f"{COLOR_YELLOW}[Relative]{COLOR_RESET}"
    elif level == "U":
        return f"{COLOR_RED}[UNMET GAP]{COLOR_RESET}"
    return "[Unknown]"

def calculate_dimension_score(assessments):
    if not assessments:
        return 1.0  # If no assessments in this dimension, assume full compatibility
    
    total_elements = len(assessments)
    weighted_sum = sum(MATCH_WEIGHTS.get(item["match_level"], 0.0) for item in assessments)
    
    return weighted_sum / total_elements

def evaluate_migration(data, weights=None):
    if weights is None:
        weights = DEFAULT_WEIGHTS
        
    module_name = data.get("module_name", "Unknown Module")
    target_tech = data.get("target_technology", "Unknown Target")
    assessments = data.get("assessments", {})
    
    dimension_scores = {}
    total_elements_count = 0
    exact_count = 0
    relative_count = 0
    unmet_count = 0
    
    print("=" * 80)
    print(f"{COLOR_BOLD}LEGACY-NEXT COMPATIBILITY EVALUATION REPORT{COLOR_RESET}")
    print(f"Legacy Module:     {COLOR_CYAN}{module_name}{COLOR_RESET}")
    print(f"Target Technology: {COLOR_CYAN}{target_tech}{COLOR_RESET}")
    print("=" * 80)
    
    for dimension, items in assessments.items():
        dim_display = dimension.replace("_", " ").title()
        print(f"\n{COLOR_BOLD}--- {dim_display} ---{COLOR_RESET}")
        
        for item in items:
            elem = item.get("element", "Unknown element")
            lvl = item.get("match_level", "U")
            rationale = item.get("rationale", "No rationale provided")
            target = item.get("target_equivalent", "N/A")
            
            tag = get_match_tag(lvl)
            print(f"  • {COLOR_BOLD}{elem}{COLOR_RESET} -> {tag}")
            print(f"    Target Equivalent: {target}")
            print(f"    Rationale:         {rationale}")
            
            total_elements_count += 1
            if lvl == "E":
                exact_count += 1
            elif lvl == "M":
                relative_count += 1
            elif lvl == "U":
                unmet_count += 1
                
        dim_score = calculate_dimension_score(items)
        dimension_scores[dimension] = dim_score
        print(f"  {COLOR_BOLD}Dimension Score ({dim_display}): {dim_score:.2f}{COLOR_RESET}")
        
    # Calculate Overall Confidence Score
    confidence_score = 0.0
    for dim, weight in weights.items():
        dim_score = dimension_scores.get(dim, 1.0)
        confidence_score += weight * dim_score
        
    print("\n" + "=" * 80)
    print(f"{COLOR_BOLD}SUMMARY & RECOMMENDATION{COLOR_RESET}")
    print("=" * 80)
    print(f"Total Elements Scanned: {total_elements_count}")
    print(f"  • Exact Matches (E):   {COLOR_GREEN}{exact_count}{COLOR_RESET}")
    print(f"  • Relative Matches (M): {COLOR_YELLOW}{relative_count}{COLOR_RESET}")
    print(f"  • Unmet Gaps (U):      {COLOR_RED}{unmet_count}{COLOR_RESET}")
    print("-" * 80)
    
    # Color-coded final score
    if confidence_score >= 0.85:
        score_color = COLOR_GREEN
        risk_rating = f"{COLOR_GREEN}{COLOR_BOLD}HIGH CONFIDENCE (Low Risk - Safe for automated/direct migration){COLOR_RESET}"
    elif confidence_score >= 0.60:
        score_color = COLOR_YELLOW
        risk_rating = f"{COLOR_YELLOW}{COLOR_BOLD}MODERATE CONFIDENCE (Medium Risk - Refactoring & custom adapters required){COLOR_RESET}"
    else:
        score_color = COLOR_RED
        risk_rating = f"{COLOR_RED}{COLOR_BOLD}LOW CONFIDENCE (High Risk - Rewrite recommended; too many unmet gaps){COLOR_RESET}"
        
    print(f"{COLOR_BOLD}Final Compatibility & Confidence Score (C): {score_color}{confidence_score * 100:.1f}%{COLOR_RESET}")
    print(f"Risk Profile & Verdict: {risk_rating}")
    print("=" * 80)
    
    return confidence_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LEGACY-NEXT Migration Compatibility Evaluator")
    parser.add_argument("--file", help="Path to compatibility JSON assessment file")
    args = parser.parse_args()
    
    if args.file:
        try:
            with open(args.file, "r") as f:
                data = json.load(f)
            evaluate_migration(data)
        except Exception as e:
            print(f"Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No input file provided. Running with built-in simulation cases...\n")
        # Direct execution of mock evaluation data to demonstrate capabilities
        from sample_legacy_code import (
            get_cobol_mock_report,
            get_vb6_mock_report,
            get_fortran_mock_report,
            get_struts_mock_report
        )
        
        print("\n--- SIMULATION 1: COBOL to Java/Spring Boot ---")
        evaluate_migration(get_cobol_mock_report())
        
        print("\n--- SIMULATION 2: VB6 to C# / .NET Core / React ---")
        evaluate_migration(get_vb6_mock_report())

        print("\n--- SIMULATION 3: Fortran to Python + C++20 / Eigen ---")
        evaluate_migration(get_fortran_mock_report())

        print("\n--- SIMULATION 4: Java 1.4 / Struts to Spring Boot 3 ---")
        evaluate_migration(get_struts_mock_report())
