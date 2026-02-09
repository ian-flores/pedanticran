# CRAN Submission Rules — NAMESPACE

---

## Category: NAMESPACE

### NS-01: Import Conflicts / Namespace Collisions

- **Severity**: WARNING
- **Rule**: When two imported packages export the same function name and both are imported via `import()` or `importFrom()`, R generates "Replacing previous import" warnings during namespace loading. This blocks CRAN submission.
- **CRAN says**: "Replacing previous import 'shinydashboard::taskItem' by 'shinydashboardPlus::taskItem'"
- **Detection**: Parse NAMESPACE for all `import()` and `importFrom()` directives. When two `importFrom()` directives import the same function name from different packages, flag it. When `import()` is used for multiple packages, flag as high-risk for collisions.
- **Fix**: Use `importFrom()` selectively. When conflict is unavoidable, use `import(pkg, except=c("conflicting_fun"))` (R >= 3.6.0) or only `importFrom()` the specific functions needed from each package.
- **Files**: `NAMESPACE`

### NS-02: Prefer importFrom over import

- **Severity**: NOTE
- **Rule**: Using `import(entire_package)` in NAMESPACE instead of selective `importFrom(pkg, fun1, fun2)` is discouraged by CRAN guidelines and Bioconductor policy. Human reviewers may request changes, especially for new packages.
- **CRAN says**: "Using importFrom selectively rather than import is good practice and recommended notably when importing from packages with more than a dozen exports." (Writing R Extensions)
- **Detection**: Parse NAMESPACE for `import()` directives (as opposed to `importFrom()`). Flag any `import(pkg)` usage. Particularly flag when multiple `import()` directives exist.
- **Fix**: Replace `import(pkg)` with specific `importFrom(pkg, fun1, fun2, ...)` for each function actually used. If using roxygen2, replace `@import pkg` with `@importFrom pkg fun1 fun2`.
- **Files**: `NAMESPACE`

### NS-03: S3 Method Exported but Not Registered via S3method()

- **Severity**: NOTE
- **Rule**: Functions that look like S3 methods (e.g., `print.myclass`, `summary.myclass`) that are `export()`-ed but not registered via `S3method()` trigger a NOTE that human reviewers consistently reject.
- **CRAN says**: "Found the following apparent S3 methods exported but not registered: [function names]. See section 'Registering S3 methods' in the 'Writing R Extensions' manual."
- **Detection**: Parse NAMESPACE for `export()` directives where the function name matches `generic.class` pattern (where generic is a known S3 generic like print, summary, format, plot, `[`, `[[`, `$`, as.data.frame, etc.) and is not also registered via `S3method()`.
- **Fix**: For roxygen2 users, use `@export` on S3 methods (roxygen2 >= 7.0 automatically generates `S3method()`). For manual NAMESPACE: replace `export(print.myclass)` with `S3method(print, myclass)`.
- **Files**: `NAMESPACE`

### NS-04: Broad exportPattern

- **Severity**: NOTE
- **Rule**: Using `exportPattern("^[[:alpha:]]")` or similar broad patterns exports all functions starting with a letter, including internal helpers. CRAN human reviewers flag this, especially for new packages.
- **CRAN says**: "Exporting all functions with exportPattern('^[[:alpha:]]+') is strongly discouraged and almost always not allowed." (Bioconductor, mirrored by CRAN)
- **Detection**: Parse NAMESPACE for `exportPattern()` directives. Flag any pattern that is broadly permissive (matches most function names), including `exportPattern(".")`, `exportPattern("^[[:alpha:]]")`, `exportPattern("^[^\\.]")`.
- **Fix**: Replace `exportPattern()` with explicit `export()` directives for each public function. If using roxygen2, tag each public function with `@export` and ensure internal helpers lack this tag.
- **Files**: `NAMESPACE`

### NS-05: Depends vs Imports Misuse

- **Severity**: NOTE
- **Rule**: Packages listed in `Depends:` are loaded onto the user's search path. CRAN prefers packages in `Imports:` unless they genuinely need to be on the search path (e.g., for user-facing data or extending another package's classes).
- **CRAN says**: "The 'Depends' field should nowadays be used rarely, only for packages which are intended to be put on the search path to make their facilities available to the end user (and not to the package itself)." (Writing R Extensions)
- **Detection**: Parse DESCRIPTION for `Depends:` field. Flag any package listed in `Depends` that is not `R` itself (version constraint) or `methods` (needed for S4). Cross-reference with NAMESPACE to check if the Depends package is also imported.
- **Fix**: Move packages from `Depends:` to `Imports:` in DESCRIPTION. Add corresponding `importFrom()` directives in NAMESPACE (or `@importFrom` in roxygen2).
- **Files**: `DESCRIPTION`, `NAMESPACE`

### NS-06: No Visible Binding / Missing importFrom

- **Severity**: NOTE
- **Rule**: When R code uses functions from other packages without proper `importFrom()` or `::` qualification, R CMD check generates "no visible global function definition" or "no visible binding for global variable" NOTEs. Human reviewers consistently reject packages with these, especially new submissions.
- **CRAN says**: "no visible global function definition for 'foo'"
- **Detection**: Requires R-level analysis. Partial detection: check that packages in DESCRIPTION `Imports:` have corresponding `importFrom()` or `import()` in NAMESPACE (if not, they may rely on `::` syntax, which is valid but worth verifying).
- **Fix**: For each function from another package, either use `pkg::fun()` syntax in code, or add `importFrom(pkg, fun)` to NAMESPACE / `@importFrom pkg fun` in roxygen2. For non-standard evaluation variables (e.g., dplyr column names), use `.data$col` or `utils::globalVariables()`.
- **Files**: `NAMESPACE`, `R/*.R`

### NS-07: Re-Export Documentation Requirements

- **Severity**: NOTE
- **Rule**: When re-exporting functions from other packages (e.g., the pipe `%>%` from magrittr), the re-exported function must have its own documentation page with `@return` tag. Missing documentation for re-exports triggers DOC-01 violations.
- **CRAN says**: "Please add \\value to .Rd files regarding exported methods."
- **Detection**: Parse NAMESPACE for patterns where a function is both `importFrom()`-ed and `export()`-ed (suggesting re-export). Check that corresponding .Rd documentation exists.
- **Fix**: Use roxygen2's `@importFrom pkg fun` + `@export` pattern, which generates proper re-export documentation. Or create a `R/reexports.R` file with roxygen2 blocks for re-exported objects.
- **Files**: `NAMESPACE`, `man/*.Rd`
