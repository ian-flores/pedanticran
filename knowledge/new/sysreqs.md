## Category: System Requirements

### SYS-01: Undeclared System Library in Compiled Code

- **Severity**: WARNING
- **Rule**: Packages that link against system libraries (libcurl, libxml2, OpenSSL, zlib, etc.) via compiled code in `src/` must declare those libraries in the `SystemRequirements` field. Without the declaration, the package fails to install on CRAN check machines when the configure script or linker cannot find the library.
- **CRAN says**: "configuration failed because libxml-2.0 was not found" / "cannot find -lcurl" (installation failure is the rejection mechanism)
- **Detection**: Scan `src/*.c`, `src/*.cpp`, `src/*.h` for `#include` of known system library headers (e.g., `<curl/curl.h>`, `<zlib.h>`, `<png.h>`). Also parse `src/Makevars` for `-l<library>` flags in `PKG_LIBS`. Cross-reference against `SystemRequirements` field in DESCRIPTION.
- **Fix**: Add the library name to SystemRequirements with platform install hints: `SystemRequirements: libcurl: libcurl-devel (rpm) or libcurl4-openssl-dev (deb)`
- **Files**: `DESCRIPTION`, `src/*.c`, `src/*.cpp`, `src/*.h`, `src/Makevars`

### SYS-02: Undeclared External Program or Interpreter

- **Severity**: WARNING
- **Rule**: Packages that invoke external programs via `system()`, `system2()`, or `processx::run()` — or depend on interpreters like Python, Java, or pandoc — must declare them in `SystemRequirements`. Writing R Extensions explicitly lists Perl, Python, Tcl, BUGS, JavaScript, Matlab, PHP, and shell scripts as needing declaration.
- **CRAN says**: "If your package requires one of these interpreters or an extension then this should be declared in the SystemRequirements field."
- **Detection**: Grep R source files for `system()`, `system2()`, `processx::run()` calls that invoke known external programs. Check for `reticulate::` usage (Python), `rJava::` or `.jcall()` (Java), `rmarkdown::render()` (pandoc). Cross-reference against SystemRequirements.
- **Fix**: Add the program to SystemRequirements with version if applicable: `SystemRequirements: Python (>= 3.6), pandoc (>= 2.0)`
- **Files**: `DESCRIPTION`, `R/*.R`

### SYS-03: C++20 Default Standard Transition

- **Severity**: NOTE
- **Rule**: R 4.6.0 makes C++20 the default C++ standard where available. Packages that explicitly set `CXX_STD = CXX17` in Makevars should verify compatibility with C++20 compilation. Packages still specifying `CXX_STD = CXX11` or `CXX_STD = CXX14` get a WARNING (already covered by COMP-06). Packages needing exactly C++17 should keep the explicit declaration; packages compatible with C++20 can remove `CXX_STD` entirely.
- **CRAN says**: R 4.6.0 NEWS: "C++20 is now the default C++ standard where available."
- **Detection**: Check if package has `src/` with C++ files. Check if `CXX_STD` is set in Makevars. If `CXX_STD = CXX17` is explicitly set, flag as informational for C++20 compatibility review.
- **Fix**: For new packages: remove CXX_STD entirely (C++20 default is backward-compatible for most code). For packages needing exactly C++17: keep `CXX_STD = CXX17`. For packages needing C++20 features: set `CXX_STD = CXX20`.
- **Files**: `src/Makevars`, `src/Makevars.win`

### SYS-04: Configure Script Missing for System Libraries

- **Severity**: WARNING
- **Rule**: Packages that use system libraries (detected via SYS-01) should include a `configure` script that checks for required tools and provides informative error messages. The configure script must never attempt to install dependencies itself. The CRAN Repository Policy requires packages to check for the presence of required tools; for Rust packages specifically, "configure/configure.win script should check for the presence of commands cargo and rustc."
- **CRAN says**: "The package should not attempt to install these for itself." / Configure scripts must "check for the presence of commands."
- **Detection**: Check if `src/` exists with compiled code using system libraries (from SYS-01) but no `configure` script. If `configure` exists, grep for auto-install anti-patterns (`apt-get install`, `pip install`, `npm install` being executed rather than suggested in error messages).
- **Fix**: Add a configure script that checks for required tools/libraries and provides informative error messages. Never attempt to install tools automatically. Use `pkg-config` or `AC_CHECK_LIB` for detection.
- **Files**: `configure`, `configure.ac`, `src/Makevars`

### SYS-05: Java .class/.jar Files Require Source

- **Severity**: REJECTION
- **Rule**: Packages containing `.class` or `.jar` files must include Java source code in a top-level `java/` directory, or that directory must explain how the sources can be obtained. This is a FOSS license compliance requirement.
- **CRAN says**: "For Java .class and .jar files, the sources should be in a top-level java directory in the source package (or that directory should explain how they can be obtained)." / Real rejection (CirceR, April 2024): "Package has FOSS license, installs .class/.jar but has no 'java' directory."
- **Detection**: Search for `.class` and `.jar` files anywhere in the package (especially `inst/java/`, `java/`, `inst/`). If found, check for a `java/` top-level directory. Also verify SystemRequirements mentions Java/JDK.
- **Fix**: Create a `java/` directory containing Java source files, or include a README in `java/` explaining how to obtain the sources. Declare `SystemRequirements: Java (>= 8)` (or appropriate version).
- **Files**: `DESCRIPTION`, `java/`, `inst/java/`, any `.jar`/`.class` files

### SYS-06: Contradictory C++ Standard Between SystemRequirements and Makevars

- **Severity**: WARNING
- **Rule**: The C++ standard specified in `SystemRequirements` (e.g., "C++17") must be consistent with the `CXX_STD` setting in `src/Makevars*`. R CMD check validates this since R 4.5 and issues a warning for contradictory specifications.
- **CRAN says**: "C++ standard specifications (CXX_STD = in 'src/Makevars*' and in the SystemRequirements field of the 'DESCRIPTION' file) are now checked more thoroughly. Invalid values are still ignored but now give a warning, as do contradictory specifications."
- **Detection**: Parse SystemRequirements for C++ standard mentions (e.g., "C++17", "C++20", "C++11"). Parse `src/Makevars*` for `CXX_STD` setting. Flag if they contradict (e.g., SystemRequirements says C++17 but Makevars says CXX20). Also flag deprecated `SystemRequirements: C++11`.
- **Fix**: Ensure SystemRequirements and Makevars CXX_STD agree. Best practice: specify only in Makevars (`CXX_STD`), not in SystemRequirements, unless human-readable documentation is desired.
- **Files**: `DESCRIPTION`, `src/Makevars`, `src/Makevars.win`

### SYS-07: USE_C17 Opt-Out for C23 Keyword Conflicts

- **Severity**: NOTE
- **Rule**: Packages with C23 keyword conflicts (`bool`, `true`, `false`, `nullptr` used as variable/parameter names) can temporarily opt out of C23 compilation by adding `USE_C17` to SystemRequirements. This is a temporary escape hatch; the proper fix is to rename conflicting identifiers.
- **CRAN says**: "Packages can opt out via `SystemRequirements: USE_C17` or `R CMD INSTALL --use-C17`."
- **Detection**: Cross-reference with COMP-01 (C23 keyword conflicts). If COMP-01 detects conflicts AND `SystemRequirements: USE_C17` is present, suppress or downgrade the COMP-01 finding. If COMP-01 detects conflicts AND no USE_C17, suggest either fixing the code or adding USE_C17 as a temporary workaround.
- **Fix**: Best: Rename conflicting identifiers to avoid C23 keywords. Temporary: Add `USE_C17` to SystemRequirements in DESCRIPTION. Ensure configure script does not override the C standard selection.
- **Files**: `DESCRIPTION`, `src/*.c`, `src/*.h`
