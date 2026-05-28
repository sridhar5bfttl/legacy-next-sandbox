# LEGACY-NEXT: Migration Playbook & Skill Profiles

This playbook defines the skills, architectural patterns, and translation conventions required for engineering teams executing legacy-to-modern software migrations.

---

## 1. Skill Profile Matrix

A successful migration requires developers who can bridge both the old and new worlds. Below is the skill matrix outlining critical competencies.

| Dimension | Legacy Skills (COBOL / VB6) | Modern Target Skills (Java / C# / React) |
| :--- | :--- | :--- |
| **Logic & Structure** | • **COBOL**: DATA DIVISION, LINKAGE SECTION, PERFORM loops, COMP-3 packed decimals.<br>• **VB6**: Procedural Forms, BAS Modules, Class Modules, event-driven architecture. | • **Java/C#**: Object-Oriented Design, Domain-Driven Design (DDD), Generics, Streams/LINQ.<br>• **TypeScript**: Functional Components, React hooks. |
| **State & Memory** | • Static global storage, single-threaded execution, shared Common Communication Area (COMMAREA). | • Stateless microservices, thread-safety, dependency injection (Spring IoC / .NET DI), distributed caching (Redis). |
| **Data Access** | • Mainframe sequential files, VSAM files, DB2 EXEC SQL blocks, ADO Recordsets. | • Object-Relational Mapping (Hibernate/EF Core), Spring Data repositories, async connection pools. |
| **Integration & I/O** | • JCL (Job Control Language) file routing, batch job windows, Win32 API DLL bindings. | • RESTful Web Services, gRPC, Event-driven queues (Kafka/RabbitMQ), cloud-native object storage (S3). |

---

## 2. Industry-Wide Technology Compatibility & Migration Issues

Below is a compatibility mapping matrix showing standard legacy technology stacks, their modern equivalents (excluding enterprise ERP integrations), and the potential issues that may occur after migration:

| Legacy Software / Tech Stack | Modern Target Equivalent | Match Level & Mapping Strategy | Potential Post-Migration Issues & Risks |
| :--- | :--- | :--- | :--- |
| **Mainframe COBOL Batch & JCL** | Java 21 / Spring Boot 3.x or C# / .NET 8 (hosted on Linux/AWS) | **🟡 Relative (M)**<br>• JCL paths mapped to Spring Batch job flows.<br>• COBOL variables mapped to POJOs / Records. | • **Decimal Precision**: Minor floating-point discrepancies if `COMP-3` decimal fields are mapped to standard `double` instead of `BigDecimal`. <br>• **EBCDIC to ASCII**: Sorting orders (collating sequences) change between character sets, causing business logic loops to behave differently. |
| **Visual Basic 6 (VB6) Client-Server Desktop Apps** | C# / .NET 8 Web API + React SPA (Web App) | **🟡 Relative (M)** / **🔴 Unmet (U)**<br>• Event-driven form layouts refactored into React functional components.<br>• Backend logic refactored to C# Web APIs. | • **State Management**: VB6 maintains a permanent connection & state. HTTP APIs are stateless, requiring session tracking (JWT/Redis).<br>• **OS Dependencies**: Win32 user32/gdi32 calls for screen metrics or registry hooks are completely blocked by the web browser sandbox. |
| **Fortran Scientific/Reservoir Simulation Engines** | Python (orchestration) + C++20 / Eigen / CUDA (solver engine) | **🟡 Relative (M)**<br>• Iterative numerical solver loops translated to modern parallelized C++ templates or CUDA kernels. | • **Numerical Divergence**: Extremely slight rounding differences in multi-dimensional matrix operations can accumulate, causing simulation models to diverge from legacy baselines.<br>• **Performance Regressions**: Fortran's compiler array optimization is difficult to match in standard C++ without optimized libraries. |
| **ASP Classic & COM+ Components** | ASP.NET Core MVC or Blazor | **🟡 Relative (M)**<br>• VBScript code converted to C# controller actions.<br>• Direct database connections upgraded to EF Core. | • **ActiveX/COM+ Registration**: Obsolete DLLs must be re-registered or completely rewritten to run in 64-bit modern IIS or Linux container systems.<br>• **Null Handling**: Differences in how C# and VBScript handle empty strings or `Null` can trigger unhandled runtime errors. |
| **Java 1.4 / Struts 1.x & EJB 2.x Enterprise Backend** | Spring Boot 3.x + Spring Security + REST APIs | **🟢 Exact (E)** / **🟡 Relative (M)**<br>• XML-based Struts routing mapped to REST annotation routes (`@RestController`).<br>• Stateful session beans converted to stateless Spring Beans. | • **Class Loading Conflicts**: Older dependencies/libraries might have transitive vulnerabilities or depend on obsolete JVM internals.<br>• **Transaction Propagation**: Differences in EJB container-managed transactions (CMT) vs. Spring's declarative transaction management (`@Transactional`). |
| **Legacy SCADA/HMI Host Systems (e.g., GE iFIX 3.x, Intouch 7)** | Modern HMI/SCADA (Ignition SCADA, HTML5 Web HMI) | **🔴 Unmet (U)** / **🟡 Relative (M)**<br>• Re-implement graphic displays using vector-based SVG/HTML5.<br>• Migrate COM/DCOM OPC DA connections to TCP-based OPC UA. | • **Real-time Latency**: Web-based interfaces can suffer from render latency compared to local OS drawing threads, critical for emergency shutdowns.<br>• **Network Protocol Security**: Connecting legacy serial/unencrypted protocols (Modbus) to modern IP networks increases cyber vulnerability. |
| **FoxPro / MS Access Database Apps** | C# / .NET 8 + Microsoft SQL Server / PostgreSQL | **🔴 Unmet (U)** / **🟡 Relative (M)**<br>• Multi-user file-share DB files (.DBF, .MDB) replaced by centralized SQL servers. | • **Concurrency Deadlocks**: FoxPro/Access handle multi-user locks via OS file locking. Centralized SQL engines handle row-level locks, causing query bottlenecks if not re-indexed.<br>• **Hardcoded Queries**: Logic embedded directly in UI events must be extracted and rewritten as stored procedures or ORM queries. |

---

## 3. Modernization Architectural Patterns

When migrating systems, never translate code line-for-line without refactoring. The following patterns must be applied:

### A. The Strangler Fig Pattern
Do not attempt a "Big Bang" migration. Instead, incrementally replace legacy subsystems with modern microservices.
* **Mechanism**: Intercept requests to the legacy system via an API Gateway or Reverse Proxy. Direct new or migrated endpoints to the new microservices, while routing legacy calls to the old system.
* **Benefit**: Reduces release risk, provides early feedback, and maintains system availability.

### B. The Anti-Corruption Layer (ACL)
Legacy database formats or message schemas should not pollute the new domain design.
* **Mechanism**: Implement a translation layer between the legacy system and the modern system. 
* **Benefit**: Ensures the modern microservice is built using pure, clean domain models, while translating data schemas on the boundary.

### C. The Repository Pattern
Decouple business logic from database and file structures.
* **Mechanism**: Replace legacy direct-file access (like COBOL sequential file reading or VB6 raw files) with a standard repository interface (`IRepository<T>`).
* **Benefit**: Allows logic to remain identical while changing storage from raw files to SQL databases or cloud storage.

---

## 4. Technology Translation Guidelines

### COBOL (Mainframe Batch) ──> Java 21 / Spring Boot 3.x

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     COBOL (Procedural/Flat)     │ ───>  │    Java (OOP/Spring Boot 3)     │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| COBOL Construct | Target Java Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| `IDENTIFICATION / ENVIRONMENT DIVISION` | Application config files (`application.yml` or metadata annotations). | 🟢 Exact | Direct mapping to project structure. |
| `DATA DIVISION` / variables | POJO classes with appropriate Java data types (e.g., `BigDecimal` for currency, `String` for text). | 🟢 Exact | Direct conversion, ensuring correct scale for decimals. |
| `PIC S9(7)V99 COMP-3` (Packed decimal) | `BigDecimal` (Initialized with scale = 2). | 🟢 Exact | Mandatory to use `BigDecimal` to prevent float-point rounding errors. |
| `PERFORM UNTIL ...` loops | `while (...)` or `for (...)` loops. | 🟢 Exact | Simple syntax translation. |
| `EXEC CICS RECEIVE / SEND MAP` | REST API Controller (`@RestController`) returning JSON payloads. | 🟡 Relative | Map legacy CICS screens to REST JSON payloads; replace physical terminal IO with API responses. |
| `EXEC SQL SELECT ... INTO ...` | Spring Data JPA / Hibernate Query. | 🟢 Exact | Map to repository methods. |
| `JCL DD (Data Definition) Files` | Spring Batch Reader/Writer mapping input file paths to Java resource buffers. | 🟡 Relative | Adapt JCL file mappings to standard application properties or environment variables. |

---

### VB6 (Desktop) ──> C# / .NET 8 / React

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│    VB6 (Stateful Client App)    │ ───>  │  React SPA + C# Web API Backend │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| VB6 Construct | Target Modern Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| `Form1.frm` (User Interface layout) | React Component (TypeScript + CSS). | 🟡 Relative | Translate visual controls (buttons, textboxes) to HTML5 elements; state logic moved to React State. |
| `Form_Load` Event Handler | React `useEffect` or lifecycle hook triggering API calls. | 🟡 Relative | Convert desktop load actions to API fetches. |
| `.BAS` Module (Global Functions) | C# Static Utility classes or Service classes. | 🟢 Exact | Refactor global state into dependency-injected services. |
| `ADO Recordset` (Direct DB connection) | Entity Framework Core Context & DbSet. | 🟡 Relative | Replace stateful, forward-only cursor recordsets with asynchronous DTO lists fetched via EF Core. |
| `Win32 DLL Calls` (`Declare Lib ...`) | Replaced with native .NET runtime capabilities or platform-specific service adapters. | 🔴 Unmet | **Gap**: Must re-implement OS-specific features (e.g., registry access, registry hooks) using modern OS-agnostic .NET API calls. |

---

### Fortran 77 / 90 / 95 (Numerical Engines) ──> Python + C++20 / Eigen

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     Fortran (Column-Major)      │ ───>  │  C++20 Engine + Python Wrapper  │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| Fortran Construct | Target Modern Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| `PROGRAM / SUBROUTINE` | C++ classes / static functions or Python methods. | 🟢 Exact | Wrap functions with clear entry/exit signatures. |
| `COMMON /name/` blocks (Fortran 77) | Shared C++ namespace variables or Singleton state. | 🟡 Relative | Refactor global shared variables to prevent memory races in multi-threaded modern environments. |
| `MODULE` definitions (Fortran 90/95) | C++ namespaces or static classes. | 🟢 Exact | Map module constants, variables, and subprograms directly to modern namespace structures. |
| `DIMENSION` / Arrays (1-indexed) | Python NumPy or C++ Eigen matrices (0-indexed). | 🟡 Relative | **Index Shift**: Adjust all index parameters (`i - 1`) and map columns (Fortran is Column-Major, C++ is Row-Major). |
| `FORMAT` statements / `WRITE` | C++ `std::format` or Python print streams. | 🟢 Exact | Translate scientific print configurations to modern string interpolation. |

---

### ASP Classic (Web) ──> ASP.NET Core / Blazor

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     ASP Classic (VBScript)      │ ───>  │     ASP.NET Core / C# / Razor   │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| ASP Classic Construct | Target Modern Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| `<% ... %>` Inline Code blocks | C# Razor Code `@(...)` or MVC Controllers. | 🟡 Relative | Decouple VBScript code from markup and move it to clean controller classes. |
| `Server.CreateObject("ADODB")` | Entity Framework Core DbContext configurations. | 🟡 Relative | Replace raw connection strings and inline SQL queries with typed entity schemas. |
| COM/COM+ custom DLL calls | Modern .NET standard class libraries (NuGet). | 🟡 Relative / 🔴 Unmet | Re-implement COM DLL business rules in native C# libraries; registry-bound DLLs are retired. |
| Session & Application State | Redis Cache or Memory Cache. | 🟡 Relative | Migrate in-memory local IIS state to distributed caching to support load-balanced containers. |

---

### Java 1.4 / Struts 1.x & EJB 2.x ──> Spring Boot 3.x

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│   Java 1.4 (Struts/Stateful)    │ ───>  │   Java 21 / Spring Boot (REST)  │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| Legacy Java Construct | Target Modern Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| `ActionForm` beans | POJO Data Transfer Objects (DTOs) with validations. | 🟢 Exact | Map parameter binders to modern Spring controllers using `@Valid` annotations. |
| `Action` (Struts execute class) | REST Controller (`@RestController` methods). | 🟢 Exact | Replace XML mapping actions with direct route mapping annotations. |
| `struts-config.xml` | Spring RequestMappings. | 🟢 Exact | Move XML routing logic to class-level annotations. |
| EJB Entity Beans (CMP/BMP) | Spring Data JPA Entities & Interfaces. | 🟢 Exact | Replace CMP schemas with plain JPA annotations (`@Entity`, `@Table`). |

---

### Legacy SCADA/HMI ──> Modern HTML5 SCADA (e.g., Ignition)

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│    Legacy HMI (Windows / COM)   │ ───>  │  HTML5 HMI / Web Clients / OPC   │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| SCADA HMI Construct | Target Modern Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| Tag Database (OPC DA / DDE) | Ignition Tag Database (OPC UA / MQTT). | 🟢 Exact | Migrate old COM tag configurations directly into modern, cross-platform TCP endpoints. |
| Custom HMI VBA Scripting | Jython (Python) Scripts or Expression scripts. | 🟡 Relative | Rewrite OS-dependent VBA hooks into sandbox-compliant Python scripts. |
| Graphic Mimic Screens | HTML5 SVG Perspective View drawings. | 🟡 Relative | Rebuild static graphics to support responsive views on mobile, tablets, and web monitors. |

---

### FoxPro / MS Access Apps ──> C# / SQL Server

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│   FoxPro / MS Access (DBF/MDB)  │ ───>  │   C# Web API + SQL Server DB    │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

| FoxPro/Access Construct | Target Modern Equivalency | Match Level | Migration Strategy |
| :--- | :--- | :---: | :--- |
| `.DBF` / `.MDB` table files | Microsoft SQL Server or PostgreSQL Database. | 🟢 Exact | Extract, transform, and load (ETL) file-based table records to structured relational schemas. |
| FoxPro `.prg` / Access VBA | C# Service classes or SQL Stored Procedures. | 🟡 Relative | Move query logic out of scripts and encapsulate it in domain service layers. |
| File Locking (`RLOCK()`) | SQL transactions (Optimistic / Pessimistic locks).| 🟡 Relative | Replace file-system level database locks with SQL engine row-level transaction management. |

