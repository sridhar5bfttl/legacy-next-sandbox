# Sample Legacy Code Snippets & Mock Reports for LEGACY-NEXT Demonstration

# ==============================================================================
# SAMPLE LEGACY CODE SNIPPETS (For reference and parsing documentation)
# ==============================================================================

COBOL_SAMPLE_CODE = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. FINPAYR.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT PAYROLL-FILE ASSIGN TO 'PAYROLL.DAT'
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  PAYROLL-FILE.
       01  PAYROLL-RECORD.
           05  EMP-ID        PIC 9(5).
           05  EMP-NAME      PIC X(20).
           05  EMP-SALARY    PIC S9(7)V99 COMP-3.
       WORKING-STORAGE SECTION.
       01  WS-TOTAL-SALARY  PIC S9(9)V99 VALUE ZERO COMP-3.
       01  WS-EOF           PIC X VALUE 'N'.
       
       PROCEDURE DIVISION.
       0000-MAIN.
           OPEN INPUT PAYROLL-FILE
           PERFORM UNTIL WS-EOF = 'Y'
               READ PAYROLL-FILE
                   AT END MOVE 'Y' TO WS-EOF
                   NOT AT END PERFORM 1000-PROCESS-PAYROLL
               END-READ
           END-PERFORM
           CLOSE PAYROLL-FILE
           
           EXEC SQL
               UPDATE SUMMARY_TABLE 
               SET TOTAL_EXPENSES = :WS-TOTAL-SALARY
               WHERE YEAR = 2026
           END-EXEC
           
           EXEC CICS SEND TEXT
               FROM("PAYROLL JOB SUCCESSFUL")
               LENGTH(23)
               FREEKB
           END-EXEC
           GOBACK.
           
       1000-PROCESS-PAYROLL.
           ADD EMP-SALARY TO WS-TOTAL-SALARY.
"""

VB6_SAMPLE_CODE = """
VERSION 5.00
Begin VB.Form CustomerForm 
   Caption         =   "Customer Details Entry"
   ClientHeight    =   4185
   ClientLeft      =   60
   ClientTop       =   345
   Begin VB.TextBox txtName 
      Height          =   285
      Left            =   1560
      TabIndex        =   0
      Top             =   360
   End
End
Attribute VB_Name = "CustomerForm"

Private Declare Function GetSystemMetrics Lib "user32" (ByVal nIndex As Long) As Long
Private Conn As ADODB.Connection
Private RS As ADODB.Recordset

Private Sub Form_Load()
    Dim systemWidth As Long
    systemWidth = GetSystemMetrics(0) ' Win32 API Call
    
    Set Conn = New ADODB.Connection
    Conn.Open "Provider=SQLOLEDB;Data Source=DB_SRV;Initial Catalog=Sales;Integrated Security=SSPI;"
    Set RS = Conn.Execute("SELECT * FROM Customers")
End Sub

Private Sub btnSave_Click()
    If txtName.Text = "" Then
        MsgBox "Name cannot be empty!", vbExclamation
        Exit Sub
    End If
    
    Conn.Execute "INSERT INTO Customers(Name) VALUES('" & txtName.Text & "')"
    MsgBox "Saved successfully!"
End Sub
"""

# ==============================================================================
# MOCK LLM COMPATIBILITY REPORTS (Target structures computed by Extractor & Assessor)
# ==============================================================================

def get_cobol_mock_report():
    return {
        "module_name": "FINPAYR.cbl",
        "target_technology": "Java 21 / Spring Boot 3.x",
        "assessments": {
            "syntax_and_semantics": [
                {
                    "element": "Variable declarations (DATA DIVISION)",
                    "match_level": "E",
                    "rationale": "COBOL variables map directly to Java object fields.",
                    "target_equivalent": "Java class fields (String, int)"
                },
                {
                    "element": "COMP-3 Packed Decimal Math (EMP-SALARY)",
                    "match_level": "E",
                    "rationale": "High-precision calculations translate perfectly to BigDecimal.",
                    "target_equivalent": "java.math.BigDecimal"
                },
                {
                    "element": "PERFORM UNTIL loops",
                    "match_level": "E",
                    "rationale": "Procedural loops translate directly to while/for loops.",
                    "target_equivalent": "while (...) loop"
                }
            ],
            "architecture_and_state": [
                {
                    "element": "Procedural batch processing",
                    "match_level": "M",
                    "rationale": "Monolithic batch loop can be restructured into a modern Spring Batch job.",
                    "target_equivalent": "Spring Batch Step (Reader, Processor, Writer)"
                },
                {
                    "element": "Working-Storage Section State",
                    "match_level": "M",
                    "rationale": "Global variables must be scope-constrained within service beans or request DTOs.",
                    "target_equivalent": "Spring Service Instance Variables / Batch Context"
                }
            ],
            "dependencies_and_libraries": [
                {
                    "element": "EXEC SQL Database operations",
                    "match_level": "E",
                    "rationale": "Standard SQL query syntax works natively with Hibernate or Spring JDBC.",
                    "target_equivalent": "Spring Data JPA Repository Interface"
                },
                {
                    "element": "LINE SEQUENTIAL File IO",
                    "match_level": "M",
                    "rationale": "File routing and buffering requires replacement with Spring File Reader classes.",
                    "target_equivalent": "FlatFileItemReader / Files.newBufferedReader"
                }
            ],
            "runtime_and_integration": [
                {
                    "element": "EXEC CICS Online Terminal Screens",
                    "match_level": "U",
                    "rationale": "CICS terminal output streams cannot exist in modern web services. This requires a full redesign.",
                    "target_equivalent": "REST Controller returning JSON + React UI"
                }
            ]
        }
    }

def get_vb6_mock_report():
    return {
        "module_name": "CustomerForm.frm",
        "target_technology": "C# / .NET 8 Web API + React SPA",
        "assessments": {
            "syntax_and_semantics": [
                {
                    "element": "Basic Control Loops & Conditionals",
                    "match_level": "E",
                    "rationale": "If/Then and variable declarations translate directly to C# syntax.",
                    "target_equivalent": "C# if statements and local variables"
                },
                {
                    "element": "Event Handler Declarations (btnSave_Click)",
                    "match_level": "M",
                    "rationale": "Visual event loops must be split into a frontend React onClick event and a backend API Controller endpoint.",
                    "target_equivalent": "React event handler calling C# controller API"
                }
            ],
            "architecture_and_state": [
                {
                    "element": "Event-driven Desktop Form Layout",
                    "match_level": "M",
                    "rationale": "VB6 form components map structurally to React state-driven components.",
                    "target_equivalent": "React Functional Component with CSS Grid"
                },
                {
                    "element": "Form Load Lifecycle State",
                    "match_level": "M",
                    "rationale": "Form loading state transitions to React useEffect hooks initiating API fetches.",
                    "target_equivalent": "React.useEffect() and C# controller constructor"
                }
            ],
            "dependencies_and_libraries": [
                {
                    "element": "ADODB Connection & Recordset",
                    "match_level": "M",
                    "rationale": "Direct SQL access inside UI classes is a pattern violation. Needs mapping to EF Core contexts.",
                    "target_equivalent": "Entity Framework Core (EF Core) DbContext"
                }
            ],
            "runtime_and_integration": [
                {
                    "element": "Win32 DLL Calls (Declare Lib user32)",
                    "match_level": "U",
                    "rationale": "Web applications run in a sandbox browser/server environment and cannot hook into local client Win32 DLLs.",
                    "target_equivalent": "OS-independent CSS responsive layouts / window dimensions APIs"
                }
            ]
        }
    }

def get_fortran_mock_report():
    return {
        "module_name": "FLUIDSIM.f",
        "target_technology": "Python + C++20 / Eigen",
        "assessments": {
            "syntax_and_semantics": [
                {
                    "element": "PROGRAM / SUBROUTINE logic",
                    "match_level": "E",
                    "rationale": "Fortran procedural structure maps directly to C++ static methods/functions.",
                    "target_equivalent": "C++ functions/methods"
                },
                {
                    "element": "DIMENSION 1-indexed matrices",
                    "match_level": "M",
                    "rationale": "Fortran is 1-indexed and column-major, requiring index shifts and column-to-row major checks in Eigen.",
                    "target_equivalent": "Eigen::MatrixXd (0-indexed, row-major)"
                }
            ],
            "architecture_and_state": [
                {
                    "element": "COMMON blocks global state",
                    "match_level": "M",
                    "rationale": "Fortran COMMON blocks map to C++ namespace variables or configuration Singletons.",
                    "target_equivalent": "C++ Configuration Singleton class"
                }
            ],
            "dependencies_and_libraries": [
                {
                    "element": "Numerical solver DO loops",
                    "match_level": "E",
                    "rationale": "Numerical computations map directly to standard C++ parallelized loops or BLAS/Eigen calls.",
                    "target_equivalent": "Eigen vector calculations / OpenMP loops"
                }
            ],
            "runtime_and_integration": [
                {
                    "element": "FORMAT scientific console output",
                    "match_level": "E",
                    "rationale": "Formatted print lines translate cleanly to modern C++ format streams.",
                    "target_equivalent": "std::format / std::cout"
                }
            ]
        }
    }

def get_struts_mock_report():
    return {
        "module_name": "UserLoginAction.java",
        "target_technology": "Java 21 / Spring Boot 3.x",
        "assessments": {
            "syntax_and_semantics": [
                {
                    "element": "Java 1.4 syntax and loops",
                    "match_level": "E",
                    "rationale": "Syntax maps natively to Java 21 since Java maintains full backward compatibility.",
                    "target_equivalent": "Java 21 Syntax"
                }
            ],
            "architecture_and_state": [
                {
                    "element": "ActionForm backing beans",
                    "match_level": "E",
                    "rationale": "Struts parameter beans map directly to plain POJO data structures with validation annotations.",
                    "target_equivalent": "POJO / Record DTO with @Valid"
                },
                {
                    "element": "Action execute controllers",
                    "match_level": "E",
                    "rationale": "Struts routing and business controllers map to stateless Spring MVC RestControllers.",
                    "target_equivalent": "@RestController mapping methods"
                }
            ],
            "dependencies_and_libraries": [
                {
                    "element": "struts-config.xml routing mapping",
                    "match_level": "E",
                    "rationale": "Struts routing is replaced by standard Spring annotations.",
                    "target_equivalent": "@RequestMapping / @PostMapping annotations"
                }
            ],
            "runtime_and_integration": [
                {
                    "element": "EJB 2.x Entity beans DB accesses",
                    "match_level": "E",
                    "rationale": "EJB persistence translates directly to JPA Repository interfaces.",
                    "target_equivalent": "Spring Data JPA Repository interfaces"
                }
            ]
        }
    }
