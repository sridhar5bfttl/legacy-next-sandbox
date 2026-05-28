#!/usr/bin/env python3
import re

def get_subroutine_prototypes(lines, declared_arrays):
    # Helper to split on comma not inside parentheses
    def split_by_comma(s):
        return re.split(r',(?![^(]*\))', s)

    prototypes = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue
        if line[0] in ('C', 'c', '*', '!'):
            i += 1
            continue
        
        stripped = line.strip()
        if not stripped or stripped.startswith('!'):
            i += 1
            continue

        sub_match = re.match(r'^\s*SUBROUTINE\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)', stripped, re.IGNORECASE)
        if sub_match:
            sub_name = sub_match.group(1).upper()
            args = [a.strip().upper() for a in sub_match.group(2).split(',') if a.strip()]
            
            # Look ahead to find types of arguments
            sub_vars_types = {}
            j = i + 1
            while j < len(lines):
                if j >= len(lines):
                    break
                next_line = lines[j]
                if not next_line:
                    j += 1
                    continue
                if next_line[0] in ('C', 'c', '*', '!'):
                    j += 1
                    continue
                next_stripped = next_line.strip()
                if next_stripped.startswith('!'):
                    j += 1
                    continue
                if next_stripped.upper().startswith('SUBROUTINE') or next_stripped.upper().startswith('PROGRAM') or next_stripped.upper().startswith('END'):
                    break
                
                type_match = re.match(r'^\s*(REAL|INTEGER)\s+(.*)', next_stripped, re.IGNORECASE)
                if type_match:
                    var_type = "double" if type_match.group(1).upper() == "REAL" else "int"
                    declarations = split_by_comma(type_match.group(2))
                    for decl in declarations:
                        decl = decl.strip()
                        arr_decl = re.match(r'([a-zA-Z0-9_]+)\s*\(([^)]+)\)', decl)
                        if arr_decl:
                            sub_vars_types[arr_decl.group(1).upper()] = "Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor>&"
                        else:
                            sub_vars_types[decl.upper()] = var_type
                j += 1
            
            params_decl = []
            for arg in args:
                arg_type = sub_vars_types.get(arg, "double")
                params_decl.append(f"{arg_type} {arg}")
            
            prototypes.append(f"void {sub_name}({', '.join(params_decl)});")
        i += 1
    return prototypes

def transpile_fortran_to_cpp(fortran_code):
    # Normalize line endings
    fortran_code = fortran_code.replace('\r\n', '\n').replace('\r', '\n')
    lines = fortran_code.split('\n')
    cpp_lines = []
    
    # Header inclusions
    cpp_lines.append("#include <iostream>")
    cpp_lines.append("#include <cstdio>")
    cpp_lines.append("#include <Eigen/Dense>")
    cpp_lines.append("")
    
    # State tracking
    declared_arrays = set()
    parameter_vars = set()
    common_blocks = {}
    current_routine = None  # 'main' or subroutine name
    in_subroutine = False
    
    # Helper to split on comma not inside parentheses
    def split_by_comma(s):
        return re.split(r',(?![^(]*\))', s)

    # First pass: Build symbol tables for arrays, common blocks, and parameters
    for line in lines:
        if not line:
            continue
        if line[0] in ('C', 'c', '*', '!'):
            continue
        
        cleaned_line = line.strip()
        if not cleaned_line or cleaned_line.startswith('!'):
            continue
            
        # Detect common blocks
        common_match = re.search(r'COMMON\s*/([^/]+)/\s*(.*)', cleaned_line, re.IGNORECASE)
        if common_match:
            block_name = common_match.group(1).upper().strip()
            vars_list = [v.strip().upper() for v in common_match.group(2).split(',') if v.strip()]
            common_blocks[block_name] = vars_list
            
        # Detect array declarations
        type_match = re.match(r'^\s*(REAL|INTEGER|DIMENSION)\s+(.*)', cleaned_line, re.IGNORECASE)
        if type_match:
            vars_part = type_match.group(2)
            parts = split_by_comma(vars_part)
            for part in parts:
                part = part.strip()
                arr_decl = re.match(r'([a-zA-Z0-9_]+)\s*\(([^)]+)\)', part)
                if arr_decl:
                    declared_arrays.add(arr_decl.group(1).upper())

        # Detect parameters to avoid double declarations
        param_match = re.search(r'PARAMETER\s*\(([^)]+)\)', cleaned_line, re.IGNORECASE)
        if param_match:
            params = split_by_comma(param_match.group(1))
            for p in params:
                if '=' in p:
                    name, _ = p.split('=')
                    parameter_vars.add(name.strip().upper())

    # Write out the Common Blocks as global structs
    for block_name, vars_list in common_blocks.items():
        cpp_lines.append(f"// Encapsulated COMMON block /{block_name}/")
        cpp_lines.append("struct {")
        for var in vars_list:
            cpp_lines.append(f"    double {var} = 0.0;")
        cpp_lines.append(f"}} {block_name};")
        cpp_lines.append("")

    # Write subroutine prototype forward declarations
    prototypes = get_subroutine_prototypes(lines, declared_arrays)
    if prototypes:
        cpp_lines.append("// Subroutine Forward Declarations")
        for proto in prototypes:
            cpp_lines.append(proto)
        cpp_lines.append("")

    # Map FORMAT descriptors to print statements
    format_map = {}
    for line in lines:
        if not line:
            continue
        if line[0] in ('C', 'c', '*', '!'):
            continue
        format_match = re.match(r'^\s*(\d+)\s+FORMAT\s*\((.*)\)', line, re.IGNORECASE)
        if format_match:
            lbl = format_match.group(1)
            fmt_str = format_match.group(2)
            
            # Convert Fortran scientific floats to C++ format specifiers
            parts = split_by_comma(fmt_str)
            cpp_fmt = ""
            for p in parts:
                p = p.strip()
                if p.startswith("'") or p.startswith('"'):
                    cpp_fmt += p[1:-1]
                elif re.match(r'[FEfe]\d+\.\d+', p):
                    match = re.search(r'(\d+)\.(\d+)', p)
                    if match:
                        width = match.group(1)
                        precision = match.group(2)
                        cpp_fmt += f"%{width}.{precision}f"
                    else:
                        cpp_fmt += "%f"
                elif p.upper() == 'X' or re.match(r'\d+X', p, re.IGNORECASE):
                    spaces = int(p[:-1]) if p[:-1].isdigit() else 1
                    cpp_fmt += " " * spaces
            format_map[lbl] = cpp_fmt

    # Second pass: code translation
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            cpp_lines.append("")
            i += 1
            continue
            
        stripped = line.strip()
        
        # 1. Handle Comments
        if line[0] in ('C', 'c', '*', '!'):
            comment_content = line[1:].rstrip()
            cpp_lines.append(f"//{comment_content}")
            i += 1
            continue
            
        if not stripped:
            cpp_lines.append("")
            i += 1
            continue
        if stripped.startswith('!'):
            cpp_lines.append(f"//{stripped[1:]}")
            i += 1
            continue

        # 2. Check for Program Start
        prog_match = re.match(r'^\s*PROGRAM\s+([a-zA-Z0-9_]+)', stripped, re.IGNORECASE)
        if prog_match:
            current_routine = 'main'
            cpp_lines.append("int main() {")
            i += 1
            continue

        # 3. Check for Subroutine Start
        sub_match = re.match(r'^\s*SUBROUTINE\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)', stripped, re.IGNORECASE)
        if sub_match:
            sub_name = sub_match.group(1).upper()
            args = [a.strip().upper() for a in sub_match.group(2).split(',') if a.strip()]
            current_routine = sub_name
            in_subroutine = True
            
            # Look ahead to see variable type declarations inside this subroutine
            sub_vars_types = {}
            j = i + 1
            while j < len(lines):
                if j >= len(lines):
                    break
                next_line = lines[j]
                if not next_line:
                    j += 1
                    continue
                if next_line[0] in ('C', 'c', '*', '!'):
                    j += 1
                    continue
                next_stripped = next_line.strip()
                if next_stripped.startswith('!'):
                    j += 1
                    continue
                if next_stripped.upper().startswith('SUBROUTINE') or next_stripped.upper().startswith('PROGRAM') or next_stripped.upper().startswith('END'):
                    break
                
                type_match = re.match(r'^\s*(REAL|INTEGER)\s+(.*)', next_stripped, re.IGNORECASE)
                if type_match:
                    var_type = "double" if type_match.group(1).upper() == "REAL" else "int"
                    declarations = split_by_comma(type_match.group(2))
                    for decl in declarations:
                        decl = decl.strip()
                        arr_decl = re.match(r'([a-zA-Z0-9_]+)\s*\(([^)]+)\)', decl)
                        if arr_decl:
                            sub_vars_types[arr_decl.group(1).upper()] = "Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor>&"
                        else:
                            sub_vars_types[decl.upper()] = var_type
                j += 1
            
            # Construct subroutine parameters list
            params_decl = []
            for arg in args:
                arg_type = sub_vars_types.get(arg, "double")
                params_decl.append(f"{arg_type} {arg}")
            
            cpp_lines.append(f"void {sub_name}({', '.join(params_decl)}) {{")
            i += 1
            continue

        # Skip variable declarations line inside subroutine if we mapped them to argument signatures
        if in_subroutine and re.match(r'^\s*(REAL|INTEGER)\s+.*', stripped, re.IGNORECASE):
            i += 1
            continue

        # 4. Handle Program/Subroutine End
        if stripped.upper() == 'END' or stripped.upper() == 'END PROGRAM' or stripped.upper() == 'END SUBROUTINE':
            if current_routine == 'main':
                cpp_lines.append("    return 0;")
            cpp_lines.append("}")
            current_routine = None
            in_subroutine = False
            i += 1
            continue

        # 5. Skip COMMON lines (handled globally) and RETURN lines
        if re.match(r'^\s*COMMON\s*/', stripped, re.IGNORECASE):
            i += 1
            continue
        if stripped.upper() == 'RETURN':
            i += 1
            continue

        # 6. PARAMETER Declaration
        param_match = re.match(r'^\s*PARAMETER\s*\(([^)]+)\)', stripped, re.IGNORECASE)
        if param_match:
            params = split_by_comma(param_match.group(1))
            for p in params:
                name, val = p.split('=')
                cpp_lines.append(f"    const int {name.strip().upper()} = {val.strip()};")
            i += 1
            continue

        # 7. Local Variable Declarations (main program)
        var_match = re.match(r'^\s*(REAL|INTEGER)\s+(.*)', stripped, re.IGNORECASE)
        if var_match and current_routine == 'main':
            var_type = "double" if var_match.group(1).upper() == "REAL" else "int"
            declarations = split_by_comma(var_match.group(2))
            for decl in declarations:
                decl = decl.strip()
                arr_match = re.match(r'([a-zA-Z0-9_]+)\s*\(([^)]+)\)', decl)
                if arr_match:
                    arr_name = arr_match.group(1).upper()
                    if arr_name in parameter_vars:
                        continue
                    dims = arr_match.group(2).split(',')
                    cpp_lines.append(f"    Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> {arr_name}({', '.join([d.strip().upper() for d in dims])});")
                else:
                    var_name = decl.upper()
                    if var_name in parameter_vars:
                        continue
                    cpp_lines.append(f"    {var_type} {var_name};")
            i += 1
            continue

        # 8. DO Loops
        do_match = re.match(r'^\s*DO\s+(\d+)?\s*([a-zA-Z0-9_]+)\s*=\s*([^,]+)\s*,\s*(.*)', stripped, re.IGNORECASE)
        if do_match:
            lbl = do_match.group(1)
            loop_var = do_match.group(2).upper()
            start_val = do_match.group(3).strip().upper()
            end_val = do_match.group(4).strip().upper()
            
            cpp_lines.append(f"    for (int {loop_var} = {start_val}; {loop_var} <= {end_val}; ++{loop_var}) {{")
            i += 1
            continue

        # Loop ends (e.g. 10 CONTINUE or 20 CONTINUE)
        cont_match = re.match(r'^\s*(\d+)\s+CONTINUE', stripped, re.IGNORECASE)
        if cont_match:
            cpp_lines.append("    }")
            i += 1
            continue

        # 9. WRITE statement
        write_match = re.match(r'^\s*WRITE\s*\(\s*[^,]+\s*,\s*(\d+)\s*\)\s*(.*)', stripped, re.IGNORECASE)
        if write_match:
            fmt_lbl = write_match.group(1)
            args_str = write_match.group(2)
            
            print_args = [a.strip().upper() for a in split_by_comma(args_str) if a.strip()]
            
            # Apply array index offset to args
            offset_args = []
            for arg in print_args:
                processed_arg = arg
                for arr in declared_arrays:
                    processed_arg = re.sub(
                        r'\b' + arr + r'\s*\(\s*([^,)]+)\s*,\s*([^)]+)\s*\)',
                        rf'{arr}(\1 - 1, \2 - 1)',
                        processed_arg
                    )
                offset_args.append(processed_arg)
                
            fmt_str = format_map.get(fmt_lbl, "")
            cpp_lines.append(f'    std::printf("{fmt_str}\\n", {", ".join(offset_args)});')
            i += 1
            continue
            
        # Skip format lines
        if re.match(r'^\s*\d+\s+FORMAT', stripped, re.IGNORECASE):
            i += 1
            continue

        # 10. Call Subroutine
        call_match = re.match(r'^\s*CALL\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)', stripped, re.IGNORECASE)
        if call_match:
            sub_name = call_match.group(1).upper()
            sub_args = call_match.group(2).upper()
            cpp_lines.append(f"    {sub_name}({sub_args});")
            i += 1
            continue

        # 11. Assignment & General code lines (e.g., calculations)
        processed_line = stripped.upper()
        
        # Apply array index offset shifting U(I, J) -> U(I-1, J-1)
        for arr in declared_arrays:
            processed_line = re.sub(
                r'\b' + arr + r'\s*\(\s*([^,)]+)\s*,\s*([^)]+)\s*\)',
                rf'{arr}(\1 - 1, \2 - 1)',
                processed_line
            )
            
        # COMMON variables mapping (DX -> SIMPARAM.DX)
        for block_name, vars_list in common_blocks.items():
            for var in vars_list:
                processed_line = re.sub(r'\b' + var + r'\b', f"{block_name}.{var}", processed_line)
                
        # Append semi-colon to statements in C++
        if processed_line and not processed_line.endswith(';'):
            processed_line += ';'
            
        cpp_lines.append(f"    {processed_line}")
        i += 1

    return '\n'.join(cpp_lines)

if __name__ == '__main__':
    # Test transpiler
    test_code = """
      PROGRAM FLUIDSIM
      INTEGER NX, NY, I, J, STEPS
      PARAMETER (NX=10, NY=10)
      REAL U(NX, NY), V(NX, NY), P(NX, NY)
      COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS
      DX = 0.1
      DY = 0.1
      DT = 0.01
      REYNOLDS = 100.0
      STEPS = 5
      DO 20 J = 1, NY
        DO 10 I = 1, NX
          U(I, J) = 1.0
          V(I, J) = 0.0
          P(I, J) = 101.3
10      CONTINUE
20    CONTINUE
      DO 100 I = 1, STEPS
        CALL SOLVER(U, V, P, NX, NY)
100   CONTINUE
      WRITE(*, 9000) U(NX/2, NY/2), V(NX/2, NY/2), P(NX/2, NY/2)
9000  FORMAT('MIDPOINT U:', F8.4, ' V:', F8.4, ' P:', F8.4)
      END
      
      SUBROUTINE SOLVER(U, V, P, NX, NY)
      INTEGER NX, NY, I, J
      REAL U(NX, NY), V(NX, NY), P(NX, NY)
      COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS
      DO 200 J = 2, NY - 1
        DO 190 I = 2, NX - 1
          U(I, J) = U(I, J) - DT * (P(I+1, J) - P(I-1, J)) / (2.0 * DX)
          V(I, J) = V(I, J) - DT * (P(I, J+1) - P(I, J-1)) / (2.0 * DY)
190     CONTINUE
200   CONTINUE
      RETURN
      END
    """
    cpp = transpile_fortran_to_cpp(test_code)
    print(cpp)
