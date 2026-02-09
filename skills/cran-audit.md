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

Read the full CRAN rules knowledge base for reference. Its location depends on where pedanticran is installed:
- Check `~/.claude/knowledge/cran-rules.md`
- Or check the pedanticran repo at the path the user has configured

### Step 3: Run All Checks

Run checks in this order, from highest to lowest rejection risk. For each issue found, cite the rule ID from the knowledge base.

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

#### 3b2. Compiled Code Checks (R 4.5+)

If `src/` directory exists with C/C++/Fortran files, run these additional checks:

1. **COMP-01: C23 keywords** — Grep src/*.c, src/*.h for `typedef.*bool`, `#define true`, `#define false`, `#define bool`, variables named `bool`, `true`, `false`

2. **COMP-02: R_NO_REMAP** — Grep src/*.cpp for bare R API calls without Rf_ prefix: `\berror\(`, `\blength\(`, `\bwarning\(`, `\bmkChar\(`

3. **COMP-03: Non-API entry points** — Grep src/ for: IS_LONG_VEC, PRCODE, PRENV, PRVALUE, R_nchar, SET_TYPEOF, TRUELENGTH, VECTOR_PTR

4. **COMP-04: Implicit declarations** — Informational flag if src/ has .c files: remind about C23 implicit function declaration errors

5. **COMP-05: Configure portability** — If configure or cleanup script exists, check for `#!/bin/bash` shebang and bashisms (`[[`, `]]`, `${var/`)

6. **COMP-06: Deprecated C++ std** — Grep src/Makevars and src/Makevars.win for `CXX_STD\s*=\s*CXX1[14]`

7. **COMP-07: Strict prototypes** — Grep src/*.c, src/*.h for function declarations with empty parens: `\w+\s*\(\s*\)` that should be `\w+(void)`

8. **COMP-08: Fortran KIND** — If src/*.f or src/*.f90 exist, grep for `KIND\s*=\s*\d+`, `INTEGER\*\d+`, `REAL\*\d+`

9. **COMP-09: Rust packaging** — If Cargo.toml exists, check for vendor/ directory, configure script printing rustc version, AUTHORS file

#### 3c. Documentation Checks

1. **DOC-01: @return tags** — For every file in `R/` with `@export`, verify it also has `@return`

2. **DOC-02: \dontrun** — Find `\dontrun{` in `R/` files and `man/*.Rd` files. Flag each instance.

3. **DOC-03: Example speed** — Flag examples with obvious slow operations (loops, network calls, large data)

4. **DOC-04: roxygen2 usage** — Check if package uses roxygen2 (presence of `RoxygenNote` in DESCRIPTION)

5. **DOC-05: Missing examples** — Find `@export` without `@examples`

6. **DOC-08: Lost braces** — If using roxygen2 < 7.3.0, check for `\itemize{}` with description-style items (`\item{term}{def}` should be `\describe{}`). Grep man/*.Rd for "Lost braces" patterns.

7. **DOC-09: HTML5 validation** — Grep man/*.Rd for deprecated HTML elements (`<font>`, `<center>`, `<strike>`).

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

#### 3e. Dependency Checks

1. **DEP-01: Dependencies** — Parse Depends/Imports/LinkingTo. Flag any that aren't obviously CRAN/Bioconductor packages.
2. **DEP-02: Conditional Suggests** — Check if Suggests packages are used with `requireNamespace()`.
3. **DEP-03: Dependency health** — Informational reminder to check CRAN status of all dependencies. Note cascading archival risk.

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
