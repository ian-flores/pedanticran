# CRAN Submission Rules — Complete Knowledge Base

Every rule includes: what CRAN requires, how they reject it (verbatim feedback), how to detect it, and how to fix it.

Sources: CRAN Repository Policy, CRAN Submission Checklist, CRAN Cookbook (R Consortium), ThinkR prepare-for-cran, devtools/usethis release checklist, community experience.

---

## Category: DESCRIPTION File

### DESC-01: Title Must Be in Title Case

- **Severity**: REJECTION
- **Rule**: The Title field must use Title Case. Capitalize principal words; lowercase articles (a, an, the), conjunctions (and, but, or), and prepositions (of, in, to, for) unless they begin the title.
- **CRAN says**: Rejects with note about incorrect title case.
- **Detection**: Parse the Title field. Check each word against title case rules. Use `tools::toTitleCase()` logic.
- **Fix**: Apply title case transformation. Watch for acronyms (keep uppercase), package names (keep as-is in single quotes), and small words.
- **Files**: `DESCRIPTION`

### DESC-02: Package/Software Names Must Be in Single Quotes

- **Severity**: REJECTION
- **Rule**: All package names, software names, and API names mentioned in Title and Description must be wrapped in single quotes.
- **CRAN says**: "Please always write package names, software names and API (application programming interface) names in single quotes in title and description. e.g: --> 'python'"
- **Detection**: Scan Title and Description for known R package names (from CRAN/Bioconductor), common software names (Python, Java, C++, OpenSSL, TensorFlow, etc.), and API names without single quotes.
- **Fix**: Wrap each name in single quotes: `Python` → `'Python'`, `ggplot2` → `'ggplot2'`
- **Files**: `DESCRIPTION`

### DESC-03: No "for R" / "in R" / "with R" in Title

- **Severity**: REJECTION
- **Rule**: The Title must not contain phrases like "for R", "in R", "with R", "an R package" — it's on CRAN, so it's obviously for R.
- **CRAN says**: Rejects as redundant.
- **Detection**: Regex scan Title for `\b(for|in|with)\s+R\b` or `\bR\s+(package|library)\b` (case-insensitive, but careful not to match R inside words).
- **Fix**: Remove the redundant phrase. "A Plotting Library for R" → "A Plotting Library".
- **Files**: `DESCRIPTION`

### DESC-04: Description Must Not Start with Package Name, "A package...", or Title

- **Severity**: REJECTION
- **Rule**: The Description field must not begin with the package name, "A package that...", "This package...", or repeat the title.
- **CRAN says**: Rejects with note about description starting incorrectly.
- **Detection**: Check first word/phrase of Description against: package name, "A package", "This package", "The package", and the Title text.
- **Fix**: Rewrite opening to describe functionality directly. "Provides methods for..." or "Implements the algorithm described in..."
- **Files**: `DESCRIPTION`

### DESC-05: Description Must Be 2+ Complete Sentences

- **Severity**: REJECTION
- **Rule**: Description must be a coherent paragraph of at least 2 complete sentences. Longer is better for new packages.
- **Detection**: Count sentence-ending punctuation (periods followed by space or end of field). Check for minimum length.
- **Fix**: Expand Description to include what the package does, how, and why.
- **Files**: `DESCRIPTION`

### DESC-06: DOI/URL Formatting

- **Severity**: REJECTION
- **Rule**: References must use author-year style with DOI in angle brackets. NO space after `doi:`. Format: `Authors (year) <doi:10.prefix/suffix>`.
- **CRAN says**: "If there are references describing the methods in your package, please add these in the description field...in the form authors (year) <doi:...> with no space after 'doi:', 'https:' and angle brackets for auto-linking."
- **Detection**: Regex for `doi:\s+` (space after colon), DOIs not in angle brackets, URLs not in angle brackets.
- **Fix**: Reformat to `<doi:10.xxxx/yyyy>` with no spaces.
- **Files**: `DESCRIPTION`

### DESC-07: Acronyms Must Be Explained

- **Severity**: REJECTION
- **Rule**: Uncommon acronyms in Title or Description must be explained (spelled out at first use).
- **CRAN says**: "Please always explain all acronyms in the description text."
- **Detection**: Find uppercase sequences (2+ letters) that aren't common (API, URL, HTTP, SQL, CSV, JSON, XML, HTML, PDF, GUI, CLI, IDE, OS, IO, UI, ID). Flag unexplained ones.
- **Fix**: Add explanation in parentheses at first use, or spell out the acronym.
- **Files**: `DESCRIPTION`

### DESC-08: Must Use Authors@R Field

- **Severity**: REJECTION
- **Rule**: Must use the `Authors@R` field with `person()` entries, not separate Author/Maintainer fields.
- **CRAN says**: "Author field differs from that derived from Authors@R. No Authors@R field in DESCRIPTION. Please add one..."
- **Detection**: Check for presence of `Authors@R` field. Check for deprecated `Author` and `Maintainer` fields used alone.
- **Fix**: Convert to `Authors@R` with proper `person()` entries including roles (aut, cre, cph, ctb).
- **Files**: `DESCRIPTION`

### DESC-09: Must Include Copyright Holder (cph)

- **Severity**: REJECTION
- **Rule**: At least one person or entity must have the `cph` (copyright holder) role in Authors@R.
- **Detection**: Parse Authors@R field, check for presence of `"cph"` role.
- **Fix**: Add `"cph"` role to the appropriate person(s).
- **Files**: `DESCRIPTION`

### DESC-10: Unnecessary "+ file LICENSE"

- **Severity**: REJECTION
- **Rule**: Do not include `+ file LICENSE` in the License field unless the license requires attribution or has other restrictions (MIT, BSD). Standard licenses (GPL-2, GPL-3, LGPL) do not need it.
- **CRAN says**: "We do not need '+ file LICENSE' and the file as these are part of R. This is only needed in case of attribution requirements or other possible restrictions."
- **Detection**: Check License field for `+ file LICENSE` combined with licenses that don't require it (GPL-2, GPL-3, LGPL-2.1, LGPL-3, Apache-2.0).
- **Fix**: Remove `+ file LICENSE` and the LICENSE file for standard licenses. Keep for MIT, BSD-2-clause, BSD-3-clause.
- **Files**: `DESCRIPTION`, `LICENSE`

### DESC-11: Single Maintainer Required

- **Severity**: REJECTION
- **Rule**: Exactly one person must have the `cre` (creator/maintainer) role. Must be a person, not a mailing list. Must have a working email.
- **Detection**: Parse Authors@R, count entries with `"cre"` role. Verify it's exactly 1. Check email looks like a person (not a list address).
- **Fix**: Ensure exactly one `cre` entry with a personal email.
- **Files**: `DESCRIPTION`

### DESC-12: Version Must Increase

- **Severity**: REJECTION
- **Rule**: Updates to published packages must have an increased version number. Even resubmissions after rejection should bump the version.
- **Detection**: Cannot check automatically without knowing CRAN state — flag as reminder.
- **Fix**: Bump patch version for resubmissions (0.3.1 → 0.3.2).
- **Files**: `DESCRIPTION`

---

## Category: Code Behavior

### CODE-01: Use TRUE/FALSE, Not T/F

- **Severity**: REJECTION
- **Rule**: Must use `TRUE` and `FALSE` literals. `T` and `F` are regular variables, not reserved words — a user could do `T <- 42`.
- **CRAN says**: "Please write TRUE and FALSE instead of T and F. Please don't use 'T' or 'F' as vector names."
- **Detection**: Grep R files for `\bT\b` and `\bF\b` used as logical values (not inside strings, not as function params named T/F). Context-aware: look for `= T`, `= F`, `(T)`, `(F)`, `, T`, `, F`.
- **Fix**: Replace `T` with `TRUE`, `F` with `FALSE`. Rename variables named T or F.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`

### CODE-02: Use message()/warning()/stop(), Not print()/cat()

- **Severity**: REJECTION
- **Rule**: Informational messages must use `message()` so users can suppress them with `suppressMessages()`. Do not use `print()` or `cat()` for status messages.
- **CRAN says**: "You write information messages to the console that cannot be easily suppressed. Instead of print()/cat() rather use message()/warning()/stop(), or if(verbose)cat(..)"
- **Detection**: Grep R source files for `print(` and `cat(` calls that aren't inside print/summary S3 methods or interactive-only functions.
- **Fix**: Replace `cat("Processing...\n")` with `message("Processing...")`. Replace `print(paste("Done:", x))` with `message("Done: ", x)`.
- **Exceptions**: print/summary methods, interactive functions, if(verbose) cat() pattern.
- **Files**: `R/*.R`

### CODE-03: No Hardcoded set.seed() in Functions

- **Severity**: REJECTION
- **Rule**: Functions must not call `set.seed()` with a hardcoded value. Seeds are OK in examples, vignettes, tests — not in function bodies.
- **CRAN says**: "Please do not set a specific number within a function."
- **Detection**: Find `set.seed(` inside function bodies in R/ directory. Distinguish from examples/tests/vignettes.
- **Fix**: Remove the hardcoded seed, or add a `seed` parameter that defaults to NULL (only set when user provides one).
- **Files**: `R/*.R`

### CODE-04: Restore options()/par()/setwd() with on.exit()

- **Severity**: REJECTION
- **Rule**: If a function changes `options()`, `par()`, or `setwd()`, it must immediately restore them using `on.exit()`.
- **CRAN says**: "Please make sure that you do not change the user's options, par or working directory. If you really have to do so within functions, please ensure with an immediate call of on.exit() that the settings are reset when the function is exited."
- **Detection**: Find calls to `options(`, `par(`, `setwd(` in function bodies. Check if followed by corresponding `on.exit(` call. The `on.exit()` must come immediately after, not later in the function.
- **Fix**: Add save-and-restore pattern:
  ```r
  old <- options(warn = 1)
  on.exit(options(old), add = TRUE)
  ```
- **Files**: `R/*.R`

### CODE-05: Never Use options(warn = -1)

- **Severity**: REJECTION
- **Rule**: `options(warn = -1)` is always rejected, even with proper `on.exit()` restoration. Use `suppressWarnings()` instead.
- **CRAN says**: "You are setting options(warn=-1) in your function. This is not allowed. Please rather use suppressWarnings() if really needed."
- **Detection**: Grep for `options(warn\s*=\s*-1)` or `options(warn\s*=\s*-\s*1)`.
- **Fix**: Replace `options(warn = -1); ...; on.exit(options(old))` with `suppressWarnings({ ... })`.
- **Files**: `R/*.R`

### CODE-06: Write Only to tempdir()

- **Severity**: REJECTION
- **Rule**: Must not write to user's home directory, working directory, or package directory. Only `tempdir()` and `tempfile()` are allowed for temporary files. For persistent user data, use `tools::R_user_dir()` (R >= 4.0) with user consent.
- **CRAN says**: "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies."
- **Detection**: Find `write*`, `save*`, `writeLines`, `cat(file=`, `sink(`, `pdf(`, `png(`, etc. where the path is not derived from `tempdir()`, `tempfile()`, or `R_user_dir()`. Look for hardcoded paths, `getwd()`, `~`, `"."`.
- **Fix**: Replace file paths with `tempfile()` or `file.path(tempdir(), "name")`. For user data, use `tools::R_user_dir("pkgname", which = "data")`.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`

### CODE-07: Clean Up Temporary Files

- **Severity**: NOTE (can cause rejection)
- **Rule**: Temporary files created in `tempdir()` must be cleaned up. Leaving them produces "Found the following files/directories" detritus NOTE.
- **CRAN says**: R CMD check NOTE: "Found the following files/directories: 'this_is_detritus382e569a7712'"
- **Detection**: Find `tempfile(` or `file.path(tempdir()` calls. Check if corresponding `unlink()` or `file.remove()` exists, or if `withr::local_tempfile()`/`withr::local_tempdir()` is used.
- **Fix**: Add `on.exit(unlink(tmpfile))` after creating temp files. Better: use `withr::local_tempfile()`.
- **Files**: `R/*.R`, `tests/**/*.R`

### CODE-08: No installed.packages()

- **Severity**: REJECTION
- **Rule**: `installed.packages()` is extremely slow and must not be used. Use targeted alternatives instead.
- **CRAN says**: "You are using installed.packages() in your code. As mentioned in the notes of installed.packages() help page, this can be very slow."
- **Detection**: Grep for `installed.packages(`.
- **Fix**: Replace with `requireNamespace("pkg", quietly = TRUE)`, `find.package("pkg")`, or `system.file(package = "pkg")`.
- **Files**: `R/*.R`

### CODE-09: No Modifying .GlobalEnv

- **Severity**: REJECTION
- **Rule**: Functions must not modify the global environment. No `<<-` to global scope, no `assign(..., envir = .GlobalEnv)`, no `rm(list = ls())` in examples/vignettes.
- **CRAN says**: "Please do not modify the global environment (e.g., by using <<-) in your functions."
- **Detection**: Find `<<-`, `assign(.*globalenv|\.GlobalEnv)`, `rm(list\s*=\s*ls())`.
- **Fix**: Use local environments, return values, or package-level environments instead of `<<-`.
- **Exceptions**: Shiny reactive assignments.
- **Files**: `R/*.R`, `man/*.Rd`, `vignettes/*.Rmd`

### CODE-10: Maximum 2 Cores

- **Severity**: NOTE → REJECTION
- **Rule**: Package must not use more than 2 cores in examples, vignettes, or tests. CRAN runs many checks in parallel.
- **CRAN says**: "Please ensure that you do not use more than 2 cores in your examples, vignettes, etc."
- **Detection**: Find `parallel::detectCores()`, `makeCluster(`, `mclapply(`, `future::plan(multisession`, etc. Check if core count is hardcoded > 2 or uses `detectCores()` without `min(..., 2)`.
- **Fix**: Cap cores: `ncores <- min(parallel::detectCores(), 2)`. Or use `getOption("mc.cores", 2L)`.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`, `man/*.Rd`

### CODE-11: No q(), quit(), or Process Termination

- **Severity**: REJECTION
- **Rule**: R code must never call `q()` or `quit()`. C/C++ code must not call `abort()`, `exit()`, `assert()`. Fortran must not call `STOP`.
- **Detection**: Grep R files for `\bq\(`, `\bquit\(`. Grep C/C++ for `abort(`, `exit(`, `assert(`. Grep Fortran for `STOP`.
- **Fix**: Use `stop()` to signal errors in R. In C, use `Rf_error()`.
- **Files**: `R/*.R`, `src/*.c`, `src/*.cpp`, `src/*.f`, `src/*.f90`

### CODE-12: No :::  to Internal Base Functions

- **Severity**: REJECTION
- **Rule**: Must not use `:::` to access unexported objects from base/recommended packages. Must not use `.Internal()` or `.Call()` to base.
- **Detection**: Grep for `:::\s*` where the package is a base/recommended package (base, utils, stats, methods, grDevices, graphics, datasets, tools, compiler). Also grep for `.Internal(`.
- **Fix**: Use public API alternatives. If none exists, file an R wish-list request.
- **Files**: `R/*.R`

### CODE-13: No Installing Packages in Functions

- **Severity**: REJECTION
- **Rule**: Functions should not install packages. This makes examples slow and modifies the user's system.
- **CRAN says**: "Please do not install packages in your functions, examples or vignettes."
- **Detection**: Find `install.packages(`, `remotes::install_`, `devtools::install_` in R source (not in functions whose explicit purpose is installation).
- **Fix**: Remove installation calls. Use `requireNamespace()` to check availability instead.
- **Files**: `R/*.R`

### CODE-14: No Disabling SSL/TLS Verification

- **Severity**: REJECTION
- **Rule**: Must not circumvent security provisions like disabling SSL certificate verification.
- **Detection**: Find `httr::config(ssl_verifypeer = 0)`, `curl::handle_setopt(ssl_verifypeer = FALSE)`, or similar.
- **Fix**: Remove SSL bypass. Fix certificate issues properly.
- **Files**: `R/*.R`

### CODE-15: No browser() Statements

- **Severity**: REJECTION
- **Rule**: Leftover `browser()` calls in package code will cause check failures under `--as-cran`. R 4.5+ traps non-interactive debugger invocations.
- **CRAN says**: R CMD check flags browser() under `_R_CHECK_BROWSER_NONINTERACTIVE_` (enabled by --as-cran).
- **Detection**: Grep for `browser()` in R/*.R function bodies (not in commented-out lines).
- **Fix**: Remove all browser() calls. Use `debugonce()` interactively instead.
- **Files**: `R/*.R`

### CODE-16: sprintf/vsprintf in C/C++ Code

- **Severity**: NOTE → REJECTION
- **Rule**: R 4.5+ reports `sprintf` and `vsprintf` usage in compiled code on ALL platforms. macOS 13+ has deprecated sprintf entirely.
- **CRAN says**: NOTE about sprintf/vsprintf usage in compiled code.
- **Detection**: Grep src/*.c, src/*.cpp for `sprintf(` and `vsprintf(`.
- **Fix**: Replace `sprintf` with `snprintf`, `vsprintf` with `vsnprintf`.
- **Files**: `src/*.c`, `src/*.cpp`

### CODE-17: UseLTO Causes CPU Time NOTE

- **Severity**: NOTE (can cause rejection)
- **Rule**: `UseLTO: yes` in DESCRIPTION triggers parallel compilation during install, causing "Installation took CPU time X times elapsed time" NOTE.
- **CRAN says**: "Installation took CPU time 3.5 times elapsed time"
- **Detection**: Check DESCRIPTION for `UseLTO` field.
- **Fix**: Remove `UseLTO` from DESCRIPTION unless absolutely needed.
- **Files**: `DESCRIPTION`

### CODE-18: Do Not Remove Failing Tests

- **Severity**: REJECTION
- **Rule**: Removing failing tests instead of fixing them is always rejected. CRAN views this as evidence the package doesn't work correctly.
- **CRAN says**: "Removed the failing tests which is not the idea of tests."
- **Detection**: Cannot detect statically — informational rule for the respond skill.
- **Fix**: Fix the underlying test failures. If test coverage increased, present covr evidence.
- **Files**: `tests/**/*.R`

---

## Category: Compiled Code (C/C++/Fortran)

### COMP-01: C23 Keyword Conflicts

- **Severity**: REJECTION
- **Rule**: R 4.5.0+ defaults to C23. `bool`, `true`, `false`, `nullptr` are now reserved C keywords. Code using these as variable names or redefining them will fail to compile.
- **CRAN says**: Compiler error or `-Wkeyword-macro` warning under C23.
- **Detection**: Grep src/*.c, src/*.h for `typedef.*bool`, `#define true`, `#define false`, `#define bool`, variable names `bool`, `true`, `false`.
- **Fix**: Remove redefinitions. Use `<stdbool.h>` or rely on C23 built-in keywords. For backward compatibility, use `R_USE_C17` in SystemRequirements as opt-out.
- **Files**: `src/*.c`, `src/*.h`

### COMP-02: R_NO_REMAP Required for C++

- **Severity**: REJECTION
- **Rule**: R 4.5.0+ compiles C++ with `-DR_NO_REMAP` by default. Bare R API function names (`error()`, `length()`, `warning()`, `mkChar()`) must use `Rf_` prefix.
- **CRAN says**: Compilation error from bare R API names in C++ code.
- **Detection**: Grep src/*.cpp for bare R API calls: `\berror\(`, `\blength\(`, `\bwarning\(`, `\bmkChar\(`, `\balloc`, `\bprotect\(`, `\bunprotect\(` etc. (excluding lines that already use Rf_ prefix).
- **Fix**: Replace `error(` with `Rf_error(`, `length(` with `Rf_length(`, `warning(` with `Rf_warning(`, `mkChar(` with `Rf_mkChar(`, etc.
- **Files**: `src/*.cpp`, `src/*.h`

### COMP-03: Non-API Entry Points

- **Severity**: WARNING → REJECTION
- **Rule**: R 4.5.0 upgraded some non-API entry point NOTEs to WARNINGs. R 4.6.0 will upgrade more. Using internal R API functions blocks submission.
- **CRAN says**: "Found non-API calls to R: [function names]" (WARNING level).
- **Detection**: Grep src/ for: IS_LONG_VEC, PRCODE, PRENV, PRVALUE, R_nchar, Rf_NonNullStringMatch, R_shallow_duplicate_attr, Rf_StringBlank, SET_TYPEOF, TRUELENGTH, XLENGTH_EX, XTRUELENGTH, VECTOR_PTR, R_tryWrap.
- **Fix**: Replace with supported API equivalents. See Writing R Extensions manual.
- **Files**: `src/*.c`, `src/*.cpp`

### COMP-04: Implicit Function Declarations (C23)

- **Severity**: REJECTION
- **Rule**: C23 removes implicit function declarations. All functions must be declared before use (via #include or explicit declaration). GCC 14+/clang 16+ with C23 make this an error.
- **CRAN says**: Compilation error about implicit function declaration.
- **Detection**: Difficult to detect statically without compiling. Flag if `src/` exists with .c files as informational reminder.
- **Fix**: Add proper `#include` directives for all used functions. Add function prototypes.
- **Files**: `src/*.c`

### COMP-05: Configure Script Portability

- **Severity**: NOTE → REJECTION
- **Rule**: Configure scripts must use `/bin/sh`, not `/bin/bash`. Bash-specific syntax (arrays, `[[`, `${var/pattern/replacement}`) is not allowed. R 4.5+ expanded bashism checking to autoconf-generated scripts.
- **CRAN says**: "NOTE 'configure': /bin/bash is not portable"
- **Detection**: Check configure, cleanup scripts for `#!/bin/bash` shebang. Grep for bashisms: `[[`, `]]`, `${var/`, `${var:`, arrays, `source` (use `.` instead).
- **Fix**: Change shebang to `#!/bin/sh`. Replace bashisms with POSIX equivalents.
- **Files**: `configure`, `cleanup`, `tools/*`

### COMP-06: C++11/C++14 Specifications Deprecated

- **Severity**: NOTE (becoming REJECTION in R 4.6.0)
- **Rule**: `CXX_STD = CXX11` or `CXX_STD = CXX14` in Makevars is deprecated. R 4.6.0 will make these defunct. C++17 is the minimum, C++20 becoming default.
- **CRAN says**: NOTE about deprecated C++ standard specification.
- **Detection**: Grep src/Makevars and src/Makevars.win for `CXX_STD\s*=\s*CXX1[14]`.
- **Fix**: Remove the `CXX_STD` line entirely (R defaults to C++17+). If C++17 features are needed explicitly, use `CXX_STD = CXX17`.
- **Files**: `src/Makevars`, `src/Makevars.win`

---

## Category: Documentation

### DOC-01: Every Exported Function Must Have @return

- **Severity**: REJECTION
- **Rule**: All exported functions must document their return value with `@return` (roxygen2) or `\value{}` (.Rd). Even void functions need this.
- **CRAN says**: "Please add \\value to .Rd files regarding exported methods and explain the functions results in the documentation."
- **Detection**: Parse R files for `@export` without corresponding `@return`. Parse .Rd files for missing `\value{}` sections. Data set docs (`\docType{data}`) are exempt.
- **Fix**: Add `@return` describing the class and meaning of the return value. For side-effect functions: `@return No return value, called for side effects`.
- **Files**: `R/*.R`, `man/*.Rd`

### DOC-02: Don't Use \dontrun{} Unless Truly Non-Executable

- **Severity**: REJECTION
- **Rule**: `\dontrun{}` should ONLY wrap code that literally cannot run (missing external APIs, credentials, hardware). Use `\donttest{}` for slow examples, `if(interactive()){}` for interactive ones.
- **CRAN says**: "\\dontrun{} should only be used if the example really cannot be executed...Please replace \\dontrun with \\donttest."
- **Detection**: Find `\dontrun{` in .Rd files or `@examples` sections. Flag all instances for review. Auto-classify based on content (network calls vs. pure computation).
- **Fix**: Replace `\dontrun{}` with `\donttest{}` for slow examples. Use `if (interactive()) {}` for interactive code. Only keep `\dontrun{}` for truly non-executable code with a comment explaining why.
- **Files**: `R/*.R`, `man/*.Rd`

### DOC-03: Examples Must Be Fast (< 5 seconds each)

- **Severity**: NOTE → REJECTION
- **Rule**: Individual examples should complete in under 5 seconds. Total check time (examples + vignettes + tests) under 10 minutes.
- **Detection**: Cannot fully detect statically — flag examples that involve file I/O, network requests, large computations, or loops with high iteration counts. Flag if `\donttest{}` is not used.
- **Fix**: Reduce iterations, use toy datasets, precompute results, wrap slow code in `\donttest{}`.
- **Files**: `R/*.R`, `man/*.Rd`

### DOC-04: Changes Must Go in .R Files, Not .Rd Files (if using roxygen2)

- **Severity**: WASTED EFFORT
- **Rule**: If package uses roxygen2, all documentation changes must go in R source files. Editing .Rd files directly is pointless — `roxygenize()` overwrites them.
- **CRAN says**: "Since you are using 'roxygen2', please make sure to add a @return-tag in the corresponding .R-file and re-roxygenize() your .Rd-files."
- **Detection**: Check if package uses roxygen2 (look for `RoxygenNote` in DESCRIPTION, `#' @` comments in R files).
- **Fix**: Make all doc changes in R source files, then run `devtools::document()`.
- **Files**: `DESCRIPTION`, `R/*.R`

### DOC-05: All Exported Functions Should Have @examples

- **Severity**: NOTE
- **Rule**: Exported functions should include runnable examples. At least some examples must be unwrapped (not in \donttest or \dontrun).
- **CRAN says**: "All your examples are wrapped in \\donttest{} and therefore do not get tested. Please unwrap the examples if that is feasible..."
- **Detection**: Find exported functions without `@examples`. Find functions where ALL examples are wrapped.
- **Fix**: Add short, fast examples that demonstrate basic usage. Keep at least one unwrapped example per function.
- **Files**: `R/*.R`

### DOC-06: Function Names Must Include Parentheses in Docs

- **Severity**: NOTE
- **Rule**: When mentioning function names in documentation text (DESCRIPTION, vignettes, other help pages), include parentheses: `foo()` not `foo`.
- **Detection**: Difficult to fully automate — flag function names mentioned without `()` in prose.
- **Fix**: Add `()` after function names in text: "use the `predict` function" → "use `predict()`"
- **Files**: `DESCRIPTION`, `R/*.R`, `vignettes/*.Rmd`

### DOC-07: Use Canonical CRAN/Bioconductor URLs

- **Severity**: NOTE
- **Rule**: Use canonical URL forms: `https://CRAN.R-project.org/package=pkgname` for CRAN, `https://bioconductor.org/packages/pkgname` for Bioconductor.
- **Detection**: Find non-canonical CRAN URLs (e.g., `cran.r-project.org/web/packages/...`).
- **Fix**: Replace with canonical form.
- **Files**: `R/*.R`, `man/*.Rd`, `DESCRIPTION`, `vignettes/*.Rmd`

---

## Category: Licensing

### LIC-01: License Must Be in CRAN Database

- **Severity**: REJECTION
- **Rule**: Only licenses from CRAN's official license database are accepted. See `https://svn.r-project.org/R/trunk/share/licenses/license.db`.
- **Detection**: Parse License field, check against known CRAN-accepted licenses (GPL-2, GPL-3, LGPL-2.1, LGPL-3, MIT, BSD-2-clause, BSD-3-clause, Apache-2.0, Artistic-2.0, CC BY 4.0, etc.).
- **Fix**: Use a standard CRAN license. For MIT: `MIT + file LICENSE` with a LICENSE file containing year and copyright holder.
- **Files**: `DESCRIPTION`, `LICENSE`

### LIC-02: License Changes Must Be Highlighted

- **Severity**: REJECTION
- **Rule**: When updating a package, any change to the License field must be explicitly mentioned in the submission comment.
- **Detection**: Compare with previous CRAN version (if update). Flag if License field changed.
- **Fix**: Add note to cran-comments.md and submission form.
- **Files**: `DESCRIPTION`, `cran-comments.md`

---

## Category: Size & Performance

### SIZE-01: Package Tarball Should Be < 10MB

- **Severity**: REJECTION
- **Rule**: Source tarball should not exceed 10MB. Data and documentation each limited to 5MB. **Updated Nov 2025:** Limit raised from 5MB to 10MB. Data and documentation each limited to 5MB. A modestly increased limit can be requested at submission for vendor files.
- **Detection**: Check file sizes. Identify large files (data, vignette images, bundled libraries).
- **Fix**: Compress data more aggressively. Move large datasets to separate data-only package. Reduce vignette image resolution. Remove unnecessary bundled files.
- **Files**: Entire package

### SIZE-02: Check Time Must Be < 10 Minutes

- **Severity**: REJECTION
- **Rule**: Total time for examples + vignettes + tests must be under 10 minutes on CRAN infrastructure (which is slower than typical dev machines).
- **Detection**: Run `R CMD check --as-cran` and check timing output. Flag if > 5 minutes (safety margin).
- **Fix**: Reduce test/example/vignette runtime. Use `\donttest{}` for slow examples. Skip slow tests conditionally. Use precomputed vignettes.
- **Files**: `tests/**/*.R`, `R/*.R`, `vignettes/*.Rmd`

---

## Category: Cross-Platform

### PLAT-01: Must Work on 2+ Major Platforms

- **Severity**: REJECTION
- **Rule**: Must make all reasonable efforts for cross-platform portable code. Must normally work on at least 2 of: Linux, macOS, Windows.
- **Detection**: Check for platform-specific code (system calls, file paths with backslashes, Windows-specific APIs). Check SystemRequirements field.
- **Fix**: Use cross-platform R functions. Conditional platform-specific code with `.Platform$OS.type`.
- **Files**: `R/*.R`, `src/*`, `DESCRIPTION`

### PLAT-02: No Binary Executables in Source Package

- **Severity**: REJECTION
- **Rule**: Source packages must not contain binary executable code. Java .class/.jar files need sources in a `java/` directory.
- **Detection**: Scan for binary files (`.exe`, `.dll`, `.so`, `.dylib`, `.class`, `.o`).
- **Fix**: Remove binaries. Include source code. Build from source during installation.
- **Files**: Entire package

---

## Category: Dependencies

### DEP-01: Strong Dependencies Must Be on CRAN or Bioconductor

- **Severity**: REJECTION
- **Rule**: Packages in Depends, Imports, LinkingTo must be available on CRAN or Bioconductor. Suggests/Enhances from other repos need `Additional_repositories` field.
- **Detection**: Parse DESCRIPTION dependencies. Check each against CRAN/Bioconductor availability.
- **Fix**: Move non-CRAN dependencies to Suggests with conditional usage, or add `Additional_repositories`.
- **Files**: `DESCRIPTION`

### DEP-02: Suggested Packages Must Be Used Conditionally

- **Severity**: REJECTION
- **Rule**: Packages in Suggests must be used conditionally in examples, tests, and vignettes with `requireNamespace("pkg", quietly = TRUE)`.
- **Detection**: Find `library(pkg)` or `pkg::func()` for Suggests packages without conditional wrapping.
- **Fix**: Wrap in `if (requireNamespace("pkg", quietly = TRUE)) { ... }`.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`

### DEP-03: Monitor Dependency Health

- **Severity**: RECOMMENDED
- **Rule**: If any package in Imports/Depends has failing CRAN checks or has been archived, your package is at risk of cascading removal without warning.
- **CRAN says**: "Archived on [date] as requires archived package '[name]'"
- **Detection**: Check CRAN check status of all dependencies (informational — can't fully automate without network access).
- **Fix**: Monitor dependency health at https://cran.r-project.org/web/checks/. Have contingency plans for critical dependencies. Consider CRANhaven (cranhaven.r-universe.dev) for emergency installs.
- **Files**: `DESCRIPTION`

---

## Category: Internet & External Resources

### NET-01: Must Fail Gracefully When Resources Are Unavailable

- **Severity**: REJECTION
- **Rule**: Package must not error or produce check warnings if internet resources are unavailable, changed, or rate-limited.
- **Detection**: Find URL requests (httr, curl, download.file). Check if wrapped in tryCatch or similar error handling.
- **Fix**: Wrap all network calls in `tryCatch()`. Return informative error messages. Use `\donttest{}` for examples requiring network. **Important (R 4.5+ enforcement):** Graceful failure must extend to ALL downstream code in examples and vignettes, not just the network-calling function itself. If `read_data()` returns NULL on failure, any vignette code that uses the result must also handle the NULL case gracefully.
- **Files**: `R/*.R`

### NET-02: Must Use HTTPS

- **Severity**: NOTE
- **Rule**: All URLs in code and documentation must use HTTPS, not HTTP.
- **Detection**: Grep for `http://` URLs (excluding localhost).
- **Fix**: Replace `http://` with `https://`.
- **Files**: `R/*.R`, `man/*.Rd`, `DESCRIPTION`, `vignettes/*.Rmd`, `README.md`

---

## Category: Submission Process

### SUB-01: Run R CMD check --as-cran on Exact Tarball

- **Severity**: PREREQUISITE
- **Rule**: Must run `R CMD check --as-cran` on the exact tarball that will be uploaded, using current R-devel.
- **Detection**: Remind user. Check for presence of `*.Rcheck/` directory with recent results.
- **Fix**: Build with `R CMD build .` then check with `R CMD check --as-cran <tarball>`.

### SUB-02: Test on Multiple Platforms

- **Severity**: RECOMMENDED
- **Rule**: Test on Windows (win-builder), macOS, and Linux before submitting. Use rhub for automated multi-platform testing.
- **Detection**: Remind user. Check for `rhub` in Suggests or CI configuration.
- **Fix**: Run `devtools::check_win_devel()`, `rhub::rhub_check()`.

### SUB-03: Check Reverse Dependencies (for updates)

- **Severity**: REQUIRED (for updates)
- **Rule**: Must verify that packages depending on yours still pass R CMD check after your changes.
- **Detection**: Check if package is already on CRAN. If so, remind about revdep checks.
- **Fix**: Run `revdepcheck::revdep_check()`. Document results in cran-comments.md.

### SUB-04: Create cran-comments.md

- **Severity**: RECOMMENDED
- **Rule**: Document test environments, R CMD check results, and any NOTEs with explanations.
- **Detection**: Check for existence of `cran-comments.md`.
- **Fix**: Create with `usethis::use_cran_comments()`. Document: test environments, R CMD check results (0 errors, 0 warnings, 0 notes — or explain notes), reverse dependency results.

### SUB-05: First Submission Gets "New submission" NOTE

- **Severity**: INFORMATIONAL
- **Rule**: New packages always get a "New submission" NOTE. This is expected and unavoidable. Document it in cran-comments.md.
- **Detection**: Check if package is already on CRAN. If not, this NOTE will appear.
- **Fix**: Add to cran-comments.md: "This is a new submission."

### SUB-06: Submission Frequency Limit

- **Severity**: POLICY
- **Rule**: Established packages should not submit updates more than once every 1-2 months.
- **Detection**: Check last CRAN publication date (if already on CRAN).
- **Fix**: Plan releases carefully. Batch fixes together.

### SUB-07: CRAN Vacation Periods

- **Severity**: INFORMATIONAL
- **Rule**: CRAN has a winter break (~Dec 23 - Jan 7) during which no submissions are processed. Automated submission tools (devtools) during this period can trigger IP blocks.
- **Detection**: Informational — flag if submitting in December/January.
- **Fix**: Plan submissions to avoid the vacation period. If IP is blocked, email CRAN with your IP address.

---

## Category: Package Naming

### NAME-01: Case-Insensitive Uniqueness Across All CRAN History

- **Severity**: REJECTION
- **Rule**: Package name must not match (case-insensitively) any current or past CRAN package, or any current Bioconductor package.
- **Detection**: Check proposed name against CRAN archive and Bioconductor. Use `available::available("pkgname")`.
- **Fix**: Choose a different name.
- **Files**: `DESCRIPTION`

### NAME-02: Package Names Are Permanent

- **Severity**: INFORMATIONAL
- **Rule**: Once submitted, the package name generally cannot be changed. CRAN retains naming rights.
- **Detection**: Informational — flag for first-time submissions.
- **Fix**: Choose your name carefully before first submission.

---

## Category: Miscellaneous

### MISC-01: NEWS.md Should Exist

- **Severity**: RECOMMENDED
- **Rule**: Include a NEWS.md file documenting changes between versions.
- **Detection**: Check for `NEWS.md` or `NEWS` file.
- **Fix**: Create with `usethis::use_news_md()`.

### MISC-02: URLs Must Be Valid

- **Severity**: NOTE
- **Rule**: All URLs in package files must resolve (no 404s, redirects should be updated to final URL).
- **Detection**: Run `urlchecker::url_check()`.
- **Fix**: Update or remove broken URLs.
- **Files**: All text files

### MISC-03: Spelling Should Be Correct

- **Severity**: NOTE
- **Rule**: Spelling errors in documentation trigger NOTEs. Use WORDLIST file for technical terms.
- **Detection**: Run `spelling::spell_check_package()`.
- **Fix**: Fix spelling errors. Add legitimate technical terms to `inst/WORDLIST`.
- **Files**: `R/*.R`, `man/*.Rd`, `DESCRIPTION`, `vignettes/*.Rmd`

### MISC-04: .Rbuildignore Must Be Properly Configured

- **Severity**: NOTE
- **Rule**: Development files (`.git/`, `.Rproj.user/`, CI configs, etc.) should be in `.Rbuildignore` to keep tarball clean.
- **Detection**: Check for common development files not in `.Rbuildignore`.
- **Fix**: Add entries to `.Rbuildignore`. Use `usethis::use_build_ignore()`.
- **Files**: `.Rbuildignore`

### MISC-05: Makefile Must Be POSIX-Compatible

- **Severity**: REJECTION
- **Rule**: Makefiles in src/ must use only POSIX make features, OR declare `SystemRequirements: GNU make`. Non-portable features: `ifeq`/`ifneq`, `${shell}`, `${wildcard}`, `+=`, `:=`, `$<`, `$^`, `.PHONY`.
- **CRAN says**: Check warnings about non-portable Makefile features.
- **Detection**: Grep src/Makevars for GNU make extensions. Check if SystemRequirements includes "GNU make".
- **Fix**: Either use only POSIX make features, or add `SystemRequirements: GNU make` to DESCRIPTION.
- **Files**: `src/Makevars`, `src/Makevars.win`, `DESCRIPTION`
