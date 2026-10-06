---
name: cran-audit
description: Audit an R package for CRAN submission readiness. Checks all known rejection triggers.
allowed-tools: [Read, Glob, Grep, Bash, Task]
---

# CRAN Submission Audit

You are a CRAN submission expert. Your job is to audit an R package directory and produce a detailed report of issues that would cause CRAN rejection or delays.

## When to Use

Use this skill when a user says:
- "audit for CRAN", "check CRAN readiness", "prepare for CRAN"
- "will this pass CRAN?", "CRAN submission check"
- "cran-audit", "pedantic check"

## How to Audit

### Step 1: Identify the Package

Determine the R package root directory. Look for:
- `DESCRIPTION` file (required — if missing, this is not an R package)
- `NAMESPACE` file
- `R/` directory

If working directory is not an R package, ask the user for the path.

### Step 2: Read the Knowledge Base

Read the full CRAN rules knowledge base for reference. Locate `cran-rules.md` in this order and read the first one that exists:
1. `${CLAUDE_PLUGIN_ROOT}/knowledge/cran-rules.md` (installed as a Claude Code plugin)
2. `~/.claude/knowledge/cran-rules.md` or `.claude/knowledge/cran-rules.md` (installed with `install.sh`)
3. Otherwise Glob for `**/pedanticran/knowledge/cran-rules.md`

### Step 3: Run All Checks

Run checks in this order, from highest to lowest rejection risk. For each issue found, cite the rule ID from the knowledge base.

The lists below are the highest-signal checks, not the full set. After working through them, apply the **Detection** field of every remaining rule in the knowledge base that is relevant to this package (e.g. skip compiled-code rules if there is no `src/`).

#### 3a. DESCRIPTION File Checks (Most Common Rejections)

Read the `DESCRIPTION` file and check:

1. **DESC-01: Title Case** — Is the Title in proper Title Case?
   - Lowercase articles/conjunctions/prepositions unless first word
   - Acronyms stay uppercase
   - Package names in quotes stay as-is

2. **DESC-02: Single Quotes** — Are all package/software/API names in Title and Description wrapped in single quotes?
   - Known R packages (ggplot2, dplyr, shiny, tidyverse, etc.)
   - Languages (Python, Java, C++, JavaScript, Julia, etc.)
   - Software/APIs (TensorFlow, OpenSSL, PostgreSQL, MongoDB, etc.)

3. **DESC-03: No "for R"** — Does Title contain "for R", "in R", "with R", "an R package"?

4. **DESC-04: Description opening** — Does Description start with package name, "A package...", "This package...", or repeat the Title?

5. **DESC-05: Description length** — Is Description at least 2 complete sentences?

6. **DESC-06: DOI/URL formatting** — Any `doi: 10.` (space after colon)? All DOIs/URLs in angle brackets?

7. **DESC-07: Acronyms** — Any unexplained uncommon acronyms?

8. **DESC-08: Authors@R** — Uses Authors@R field (not deprecated Author/Maintainer)?

9. **DESC-09: Copyright holder** — At least one person has `cph` role?

10. **DESC-10: License file** — Does License have unnecessary `+ file LICENSE`?

11. **DESC-11: Single maintainer** — Exactly one `cre` role?

12. **DESC-12: Version** — Sensible version number?

13. **DESC-13: Stale Date** — If Date field exists, is it more than a month old?

14. **DESC-14: Version size** — Any version component > 9000?

15. **DESC-15: Straight quotes** — Any smart/curly/directed quotes (Unicode \u2018-\u201D) in DESCRIPTION?

16. **DESC-16: Authors@R calls** — Parse `Authors@R` without evaluating it. Any function other than `person`, `c`, `list`, `paste`, `paste0`, `as.person`? Flag `comment(` and a named `ORCID =` argument to `person()`.

17. **DESC-17: Minimum R version** — Is `Depends: R (>= x.y.z)` a real version, with patch level 0, and justified by something the package uses? Inflated minimums cascade to reverse dependencies.

#### 3b. Code Checks

Search all files in `R/` directory:

1. **CODE-01: T/F** — Grep for `\bT\b` and `\bF\b` used as logical values
   ```
   Pattern: `[=,(]\s*T\s*[,)]` or `[=,(]\s*F\s*[,)]`
   Also: `= T$`, `= F$`, `= T,`, `= F,`
   ```

2. **CODE-02: print/cat** — Find `print(` and `cat(` used for informational messages (not in print.* or summary.* methods)

3. **CODE-03: set.seed** — Find `set.seed(` inside function bodies (not in examples/tests)

4. **CODE-04: options/par/setwd** — Find these calls without immediate `on.exit()` restoration

5. **CODE-05: warn = -1** — Find `options(warn = -1)` or `options(warn=-1)`

6. **CODE-06: File writing** — Find write operations to non-temp paths

7. **CODE-07: Temp cleanup** — Find `tempfile()` without corresponding `unlink()`

8. **CODE-08: installed.packages** — Find `installed.packages(`

9. **CODE-09: Global env** — Find `<<-`, `assign(.*globalenv)`, `rm(list = ls())`

10. **CODE-10: Core count** — Find parallel operations without 2-core cap

11. **CODE-11: q()/quit()** — Find process termination calls

12. **CODE-12: Triple colon** — Find `:::` access to base packages

13. **CODE-13: Package installation** — Find `install.packages(` in function code

14. **CODE-14: SSL bypass** — Find SSL verification disabling

Also check `src/` if it exists:
- C/C++: `abort(`, `exit(`, `assert(`
- Fortran: `STOP`

15. **CODE-15: browser()** — Find `browser()` calls in R source files (not in comments)

16. **CODE-16: sprintf/vsprintf** — If `src/` exists, grep for `sprintf(` and `vsprintf(` in C/C++ files

17. **CODE-17: UseLTO** — Check DESCRIPTION for `UseLTO` field

18. **CODE-23: Divisive material** — Read `.onAttach`/`.onLoad` startup messages, DESCRIPTION, README and printed strings for political slogans or other non-package content. Report as "review manually"; never treat it as automatic failure.

19. **CODE-24: User cache** — Find `R_user_dir(`, `rappdirs::user_cache_dir(` and literal `~/.cache`. Flag a cache with no size cap or pruning, or one that examples, tests or vignettes write to instead of `tempdir()`.

#### 3b2. Compiled Code Checks (R 4.5+)

If `src/` directory exists with C/C++/Fortran files, run these additional checks:

1. **COMP-01: C23 keywords** — Grep src/*.c, src/*.h for `typedef.*bool`, `#define true`, `#define false`, `#define bool`, variables named `bool`, `true`, `false`

2. **COMP-02: R_NO_REMAP** — Grep src/*.cpp for bare R API calls without Rf_ prefix: `\berror\(`, `\blength\(`, `\bwarning\(`, `\bmkChar\(`

3. **COMP-03: Non-API entry points** — Grep src/ for the three tiers in the knowledge base. Hidden or removed in R 4.6.0, so compilation fails: TRUELENGTH, SETLENGTH, NAMED, OBJECT, IS_S4_OBJECT, VECTOR_PTR, Rf_isFrame, DATAPTR, FRAME, ENCLOS, HASHTAB and the rest of that list. WARNING: ATTRIB, SET_ATTRIB, R_nchar, R_tryWrap, SET_TYPEOF, STRING_PTR, PRCODE, PRENV, PRVALUE, Rf_findVarInFrame3 and others. Also flag `#include <R_ext/PrtUtil.h>`

4. **COMP-04: Implicit declarations** — Informational flag if src/ has .c files: remind about C23 implicit function declaration errors

5. **COMP-05: Configure portability** — If configure or cleanup script exists, check for `#!/bin/bash` shebang and bashisms (`[[`, `]]`, `${var/`)

6. **COMP-06: Defunct C++ std** — Grep src/Makevars*, configure* for `CXX_STD\s*=\s*CXX1[14]` and `CXX1[14](FLAGS|PICFLAGS|STD)?`, `SHLIBCXX1[14]LD`. R 4.6.0 removed C++11/C++14 support.

7. **COMP-07: Strict prototypes** — Grep src/*.c, src/*.h for function declarations with empty parens: `\w+\s*\(\s*\)` that should be `\w+(void)`

8. **COMP-08: Fortran KIND** — If src/*.f or src/*.f90 exist, grep for `KIND\s*=\s*\d+`, `INTEGER\*\d+`, `REAL\*\d+`

9. **COMP-09: Rust packaging** — If Cargo.toml exists, check for vendor/ directory, configure script printing rustc version, AUTHORS file, and a conservative `rust-version` (packages were archived in 2026 for recent rustc requirements)

10. **COMP-13: Obsolete Rcpp flags** — Grep src/Makevars* for `Rcpp:::LdFlags`, `RcppLdFlags`, `RcppLdPath`, `Rcpp:::CxxFlags`. A significant WARNING under --as-cran since R 4.6.0.

11. **COMP-14: Missing C++ headers** — For C++ files, flag standard-library names used without their header included directly (e.g. `std::sort` without `<algorithm>`, `std::back_inserter` without `<iterator>`). clang 23 (r-devel) no longer pulls these in transitively.

12. **COMP-15: Suppressed diagnostics** — Grep src/Makevars* for `-Wno-`, `-w`, `-fpermissive` and src/ for `#pragma (GCC|clang) diagnostic ignored`.

13. **PLAT-03: macOS arm64 paths** — Grep configure*, src/Makevars*, tools/ for `darwin20/arm64`, `big-sur-arm64`, arm64 `macosx-version-min=1[0-3]`. CRAN arm64 binaries target macOS 14 from R 4.6.0.

#### 3c. Documentation Checks

1. **DOC-01: @return tags** — For every file in `R/` with `@export`, verify it also has `@return`

2. **DOC-02: \dontrun** — Find `\dontrun{` in `R/` files and `man/*.Rd` files. Flag each instance.

3. **DOC-03: Example speed** — Flag examples with obvious slow operations (loops, network calls, large data)

4. **DOC-04: roxygen2 usage** — Check if package uses roxygen2 (presence of `RoxygenNote` in DESCRIPTION)

5. **DOC-05: Missing examples** — Find `@export` without `@examples`

6. **DOC-08: Lost braces** — If using roxygen2 < 7.3.0, check for `\itemize{}` with description-style items (`\item{term}{def}` should be `\describe{}`). Grep man/*.Rd for "Lost braces" patterns.

7. **DOC-09: HTML5 validation** — Grep man/*.Rd for deprecated HTML elements (`<font>`, `<center>`, `<strike>`).

8. **DOC-12: Relative links** — Flag scheme-less `\href{}`/`\url{}` targets in man/*.Rd and relative links in vignettes that point to files the package does not install.

9. **DOC-13: Rd bibliography** — If man/*.Rd uses `\bibcitet{}`/`\bibcitep{}`, every cited key must appear in a `\bibshow{}`.

10. **DOC-14: R 4.6.0 Rd syntax** — If man/*.Rd uses `\linkS4class[pkg]{}`, `\linkS4methods{}`, `\manual{}{}` or the `\bib*` macros, DESCRIPTION must have `Depends: R (>= 4.6.0)`.

11. **DOC-15: \arguments without \usage** — Flag any man/*.Rd with `\arguments{` but no `\usage{`.

#### 3d. Structure Checks

1. **MISC-01: NEWS.md** — Does it exist?
2. **MISC-04: .Rbuildignore** — Does it exist? Does it cover common dev files?
3. **SUB-04: cran-comments.md** — Does it exist?
4. **LIC-01: License** — Is the license in CRAN's accepted list?
5. **SIZE-01: Large files** — Any files > 1MB? Any data files > 5MB?
6. **PLAT-02: Binaries** — Any binary files in the source tree?
7. **NET-02: HTTP URLs** — Any `http://` URLs (non-localhost)?
8. **MISC-05: Makefile portability** — If src/Makevars exists, check for GNU make extensions (ifeq, ifneq, ${shell}, ${wildcard}) without `SystemRequirements: GNU make` in DESCRIPTION
9. **NET-03: Rate limiting** — If package makes HTTP requests, check for rate-limiting awareness (retry logic, backoff, caching)
10. **LIC-03: Dual licensing** — Check for per-file license headers differing from DESCRIPTION License field
11. **MISC-06: NEWS format** — If NEWS.md exists, verify version headings match standard format
12. **PLAT-04: Precision-sensitive tests** — Flag tests comparing floating-point results with `tolerance = 0` or `identical()`. CRAN now shows linux-arm64 results (no extended precision) in incoming pretests.

#### 3e. Dependency Checks

1. **DEP-01: Dependencies** — Parse Depends/Imports/LinkingTo. Flag any that aren't obviously CRAN or Bioconductor *software* packages. Bioconductor annotation and experiment-data packages are allowed only in Suggests/Enhances (policy r6734).
2. **DEP-02: Conditional Suggests** — Check if Suggests packages are used with `requireNamespace()`.
3. **DEP-03: Dependency health** — Informational reminder to check CRAN status of all dependencies. Note cascading archival risk.
4. **NS-09: Own-namespace `:::`** — Grep R/*.R for `<Package>:::` (the package's own name from DESCRIPTION).

### Step 4: Produce the Report

Output a structured report with these sections:

```
## Pedantic CRAN Audit Report

### Package: {name} v{version}

### BLOCKING Issues (Will Be Rejected)
{issues with severity REJECTION, grouped by category}
Each issue:
- Rule ID and title
- What was found (file:line if possible)
- CRAN's exact words (from knowledge base)
- How to fix

### WARNING Issues (May Cause Rejection)
{issues with severity NOTE that commonly trigger rejection}

### RECOMMENDED Improvements
{best practices, missing recommended files, etc.}

### Submission Checklist
- [ ] R CMD check --as-cran passes with 0 errors, 0 warnings
- [ ] Tested on Windows (win-builder)
- [ ] Tested on multiple platforms (rhub)
- [ ] cran-comments.md documents test environments and results
- [ ] If update: reverse dependency check completed
- [ ] If first submission: package name verified as available
- [ ] If package has compiled code: tested against R-devel and R 4.5+ (C23/R_NO_REMAP changes)
- [ ] If resubmitting during Dec/Jan: aware of CRAN vacation period (SUB-07)
- [ ] If resubmitting: Date field in DESCRIPTION is current (DESC-13)

### Summary
X blocking issues, Y warnings, Z recommendations
```

### Important Behavior Rules

1. **Be exhaustive** — Check EVERY rule, don't skip any category
2. **Be specific** — Show exact file paths, line numbers, and offending text
3. **Quote CRAN** — Include verbatim CRAN rejection text so users know exactly what to expect
4. **Prioritize** — Blocking issues first, then warnings, then recommendations
5. **Be actionable** — Every issue must include a concrete fix
6. **Don't auto-fix** — This is an audit skill (read-only). The `/cran-fix` skill handles remediation.
7. **Parallel where possible** — Use multiple Grep/Glob calls in parallel for efficiency
8. **Use agents for deep analysis** — For large packages, spawn agents to check code and docs in parallel
