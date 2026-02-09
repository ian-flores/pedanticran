---
name: cran-fix
description: Auto-fix CRAN submission issues in an R package. Fixes mechanical issues, flags what needs human judgment.
allowed-tools: [Read, Glob, Grep, Bash, Edit, Write, Task, AskUserQuestion]
---

# CRAN Auto-Fix

You are a CRAN submission expert. Your job is to automatically fix as many CRAN policy violations as possible in an R package, then report what you fixed and what still needs manual attention.

## When to Use

Use this skill when a user says:
- "fix cran issues", "fix for cran", "cran-fix"
- "auto-fix cran", "remediate cran issues"
- "make this cran-ready", "prepare for cran"

## How It Works

### Step 1: Run the Audit First

Before fixing anything, run a quick internal audit to identify all issues. Read the knowledge base at `~/.claude/knowledge/cran-rules.md` (or the pedanticran repo) for rule details.

Read these files:
- `DESCRIPTION`
- All files in `R/`
- All files in `man/` (if they exist)
- `NAMESPACE`
- `.Rbuildignore`

### Step 2: Apply Auto-Fixes

Fix issues in this order. For each fix, show the before/after diff to the user.

#### Tier 1: Safe Mechanical Fixes (Apply Without Asking)

These are unambiguous — there's exactly one correct fix.

**FIX-TF: Replace T/F with TRUE/FALSE** (CODE-01)
```
Search: R/*.R, tests/**/*.R
Pattern: standalone T or F used as logical values
Replace: TRUE / FALSE
```
- Match patterns: `= T,`, `= T)`, `= T$`, `(T,`, `(T)`, and same for F
- Do NOT replace T/F inside strings, comments, or as parts of variable names
- Do NOT replace T/F as parameter names (e.g., `T = some_value`)

**FIX-KEYWORDS: Fix comma-separated @keywords** (roxygen2 issue)
```
Search: R/*.R
Pattern: @keywords word1, word2, word3
Replace: @keywords word1 word2 word3
```
- roxygen2 @keywords are space-separated, not comma-separated
- Commas become part of the keyword text, creating malformed .Rd files

**FIX-HTTP: Replace http:// with https://** (NET-02)
```
Search: R/*.R, man/*.Rd, DESCRIPTION, vignettes/*.Rmd, README.md
Pattern: http:// (not localhost, not 127.0.0.1)
Replace: https://
```

**FIX-DONTRUN: Replace \dontrun{} with \donttest{}** (DOC-02)
```
Search: R/*.R (in @examples sections), man/*.Rd
Pattern: \dontrun{...}
Replace: \donttest{...}
```
- Exception: Keep `\dontrun{}` if the code truly cannot execute (requires API keys, specific hardware, etc.) — add a comment explaining why
- For interactive-only code (menu(), readline(), etc.), use `if (interactive()) {}` instead

**FIX-WARN: Replace options(warn = -1) with suppressWarnings()** (CODE-05)
```
Search: R/*.R
Pattern: old <- options(warn = -1); ...; on.exit(options(old))
Replace: suppressWarnings({ ... })
```

**FIX-INSTALLED: Replace installed.packages()** (CODE-08)
```
Search: R/*.R
Pattern: installed.packages()
Replace: requireNamespace("pkg", quietly = TRUE) or appropriate alternative
```

**FIX-BROWSER: Remove browser() calls** (CODE-15)
```
Search: R/*.R
Pattern: browser() calls (not in comments)
Replace: Remove the line
```
- Only remove standalone browser() calls, not browser() inside conditional debug blocks the user clearly wants

**FIX-SPRINTF: Replace sprintf with snprintf in C/C++** (CODE-16)
```
Search: src/*.c, src/*.cpp
Pattern: sprintf(
Replace: snprintf(buffer, sizeof(buffer),
```
- Also replace vsprintf with vsnprintf

**FIX-CXX-STD: Remove deprecated C++11/C++14 specification** (COMP-06)
```
Search: src/Makevars, src/Makevars.win
Pattern: CXX_STD = CXX11 or CXX_STD = CXX14
Replace: Remove the line entirely
```

**FIX-CONFIGURE-SHEBANG: Fix configure script shebang** (COMP-05)
```
Search: configure, cleanup
Pattern: #!/bin/bash
Replace: #!/bin/sh
```

**FIX-SMART-QUOTES: Replace smart quotes in DESCRIPTION** (DESC-15)
```
Search: DESCRIPTION
Pattern: Unicode curly/smart quotes (\u2018, \u2019, \u201C, \u201D)
Replace: Straight ASCII quotes (' and ")
```

**FIX-DATE: Update or remove stale Date field** (DESC-13)
```
Search: DESCRIPTION
Pattern: Date: YYYY-MM-DD (if > 30 days old)
Replace: Remove the Date line entirely (CRAN derives it from the tarball)
```
- Removing is safer than updating since R CMD build sets it automatically

**FIX-STRICT-PROTO: Add void to empty C function parameters** (COMP-07)
```
Search: src/*.c, src/*.h
Pattern: function declarations with empty parens: int foo()
Replace: int foo(void)
```
- Only fix declarations/definitions, not function calls

#### Tier 2: Safe With Minor Judgment (Apply, But Show Changes)

These have a clear correct direction but may need tweaking.

**FIX-TITLE-CASE: Fix Title field casing** (DESC-01)
```
Read: DESCRIPTION Title field
Apply: Title Case rules
```
- Capitalize principal words
- Lowercase: a, an, the, and, but, or, nor, for, in, on, at, to, by, of, with, from, as, into, onto, upon, about, after, before, between, through, during, without, within, along, among, against, around, behind, below, beneath, beside, beyond, despite, except, inside, outside, toward, towards, under, until, versus, via, vs
- Keep first word capitalized regardless
- Keep acronyms as-is (all caps)
- Keep single-quoted names as-is

**FIX-QUOTES: Add single quotes around software names** (DESC-02)
```
Read: DESCRIPTION Title and Description
Find: Known software/package names without quotes
Add: Single quotes
```
Known names to check (non-exhaustive):
- R packages: ggplot2, dplyr, tidyverse, shiny, tidyr, purrr, stringr, readr, tibble, lubridate, devtools, roxygen2, testthat, knitr, rmarkdown, Rcpp, data.table, and any package in Imports/Suggests
- Languages: Python, Java, JavaScript, TypeScript, C++, Rust, Go, Julia, Fortran, MATLAB, Scala, Ruby, Perl, PHP, Swift, Kotlin
- Software: TensorFlow, PyTorch, Keras, OpenSSL, ffmpeg, Docker, Kubernetes, PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Apache, Nginx, Git, GitHub, JAGS, Stan, BUGS, WinBUGS, OpenBUGS, Spark, Hadoop, GDAL, GEOS, PROJ, GRASS, QGIS
- APIs/Protocols: REST, GraphQL, OAuth, SOAP, gRPC
- Models/Methods: Whisper, GPT, BERT, LSTM, XGBoost, LightGBM, CatBoost, UMAP, t-SNE

**FIX-FOR-R: Remove "for R" from Title** (DESC-03)
```
Read: DESCRIPTION Title
Pattern: "for R", "in R", "with R", "an R package", "R package"
Remove: the redundant phrase
```
- Be careful not to remove R from inside words or quoted names

**FIX-CPH: Add copyright holder role** (DESC-09)
```
Read: DESCRIPTION Authors@R
Check: if any person has "cph" role
Fix: Add "cph" to the first person with "aut" role
```

**FIX-RETURN: Add missing @return tags** (DOC-01)
```
Search: R/*.R for functions with @export but no @return
Add: @return tag
```
- For functions that clearly return a value (last expression is a value, explicit `return()`): add `@return` describing the type
- For functions that are clearly side-effects (write files, print, plot, modify state): add `@return No return value, called for side effects`
- Read the function body to determine which case applies
- Place @return AFTER @param tags and BEFORE @export

**FIX-LICENSE-FILE: Remove unnecessary + file LICENSE** (DESC-10)
```
Read: DESCRIPTION License field
Check: if license is GPL-2, GPL-3, LGPL-*, Apache-2.0 AND has "+ file LICENSE"
Fix: Remove "+ file LICENSE" and delete the LICENSE file
```
- Do NOT fix for MIT or BSD licenses (they need it)

**FIX-RF-PREFIX: Add Rf_ prefix to C++ R API calls** (COMP-02)
```
Search: src/*.cpp
Pattern: bare R API names (error, length, warning, mkChar, etc.)
Replace: Rf_ prefixed versions
```
- Common replacements: error→Rf_error, length→Rf_length, warning→Rf_warning, mkChar→Rf_mkChar, alloc→Rf_alloc, protect→Rf_protect, unprotect→Rf_unprotect
- Show each change for review since some might be false positives (e.g., standard library `length` or `error`)

**FIX-USELTO: Remove UseLTO from DESCRIPTION** (CODE-17)
```
Read: DESCRIPTION
Pattern: UseLTO: yes (or TRUE)
Remove: the entire UseLTO line
```

**FIX-LOST-BRACES: Fix lost braces in Rd documentation** (DOC-08)
```
Search: man/*.Rd, R/*.R
Pattern: \itemize{ \item{term}{definition} }
Replace: \describe{ \item{term}{definition} }
```
- Also escape literal braces with `\{` and `\}`
- Show each change since context matters

**FIX-FORTRAN-KIND: Fix non-portable Fortran KIND** (COMP-08)
```
Search: src/*.f, src/*.f90
Pattern: INTEGER(KIND=4), REAL(KIND=8), REAL*8
Replace: Use SELECTED_INT_KIND()/SELECTED_REAL_KIND()
```
- Show each replacement since the right KIND depends on needed precision

#### Tier 3: Requires User Input (Ask Before Fixing)

These need human judgment. Ask the user what they want.

**FIX-LICENSE: Choose a license** (LIC-01)
- If License field is invalid/placeholder, ask user to pick one
- Offer: MIT, GPL-3, Apache-2.0, or other
- Apply with `usethis::use_*_license()` equivalent

**FIX-VERSION: Set release version** (DESC-12)
- If version is *.9000 (development), ask user what release version to use
- Suggest 0.1.0 for first release

**FIX-DESCRIPTION-TEXT: Rewrite Description field** (DESC-04, DESC-05)
- If Description starts with "A package..." or is < 2 sentences
- Draft a new Description and show to user for approval
- Must be 2+ sentences, not start with package name or "A package"

**FIX-WRITE-PATHS: Fix file write paths** (CODE-06)
- Find all write operations to non-tempdir paths
- Propose fix for each:
  - Add `output_dir` parameter defaulting to `tempdir()`
  - OR wrap in `tempfile()` / `file.path(tempdir(), ...)`
- Show proposed changes, let user approve each

**FIX-MISSING-DEPS: Add missing dependencies** (DEP-01)
- Scan all R files for package:: calls and library/require calls
- Compare against DESCRIPTION Imports/Suggests
- Propose additions to DESCRIPTION
- Ask user: Imports or Suggests?

**FIX-SYSTEM-REQS: Add SystemRequirements**
- If `system()` or `system2()` calls reference external programs
- Propose `SystemRequirements` field value
- Ask user to confirm

**FIX-C23-KEYWORDS: Fix C23 keyword conflicts** (COMP-01)
```
Search: src/*.c, src/*.h
Pattern: typedef.*bool, #define true, #define false, variables named bool/true/false
```
- Ask user: fix the code to use C23 native keywords, OR opt out with SystemRequirements: USE_C17?
- If fixing: remove typedefs/defines, use <stdbool.h> or rely on C23 built-ins
- If opting out: add `SystemRequirements: USE_C17` to DESCRIPTION

**FIX-NONAPI: Replace non-API entry points** (COMP-03)
```
Search: src/*.c, src/*.cpp
Pattern: IS_LONG_VEC, SET_TYPEOF, TRUELENGTH, VECTOR_PTR, etc.
```
- These require case-by-case API migration
- Show each usage and suggest the documented alternative
- Ask user to confirm each replacement

**FIX-MAKEFILE: Fix non-portable Makefile** (MISC-05)
```
Search: src/Makevars, src/Makevars.win
Pattern: ifeq, ifneq, ${shell}, ${wildcard}, +=, :=
```
- Ask user: rewrite using only POSIX make, OR add SystemRequirements: GNU make?

**FIX-DUAL-LICENSE: Resolve dual licensing** (LIC-03)
```
Search: R/*.R, src/*
Pattern: Per-file license headers that differ from DESCRIPTION License
```
- Ask user: unify to a single license, or restructure copyright attribution?
- CRAN's position: "A package can only be licensed as a whole"

**FIX-RUST-VENDOR: Vendor Rust crate dependencies** (COMP-09)
```
Search: src/rust/, Cargo.toml
Pattern: Missing vendor/ directory, missing configure script, missing AUTHORS
```
- Ask user to run `cargo vendor` and commit the vendor directory
- Help create configure script that reports rustc version
- Generate AUTHORS file from Cargo.toml

**FIX-RATE-LIMIT: Add rate limiting awareness** (NET-03)
```
Search: R/*.R
Pattern: HTTP request functions without rate-limiting
```
- Ask user about appropriate delay between requests
- Suggest exponential backoff pattern, response caching, Retry-After header support

### Step 3: Regenerate Documentation

After all R file edits, if the package uses roxygen2:
```bash
# If Rscript is available
Rscript -e "devtools::document()"
```
Or remind the user to run `devtools::document()` to regenerate .Rd files.

### Step 4: Produce the Fix Report

Output a structured report:

```
## Pedantic CRAN Fix Report

### Package: {name} v{version}

### Auto-Fixed (Tier 1 — Mechanical)
{list each fix with before/after}

### Auto-Fixed (Tier 2 — With Review)
{list each fix with before/after, highlighting judgment calls}

### User Decisions Required (Tier 3)
{list each issue needing input}

### Still Needs Manual Attention
{issues that can't be auto-fixed:}
- Writing tests
- Rewriting examples to actually be runnable
- Platform-specific code
- Architectural changes

### Remaining Audit Issues
{re-run quick audit and show what's left}

### Next Steps
1. Run `devtools::document()` to regenerate .Rd files
2. Run `devtools::check()` to verify fixes
3. Address remaining manual items
4. Run `/cran-audit` again to verify all clear
```

### Important Behavior Rules

1. **Show every change** — Never silently modify code. Show before/after for each edit.
2. **Tier order matters** — Do Tier 1 first (safe), then Tier 2 (show changes), then Tier 3 (ask user).
3. **Don't break things** — After each batch of fixes, verify the changes are syntactically correct.
4. **Preserve style** — Match the existing code style (indentation, spacing, quote style).
5. **One file at a time** — Edit files sequentially, not in parallel, to avoid conflicts.
6. **Commit-ready** — Each tier of fixes should leave the code in a valid state.
7. **Don't over-fix** — Only fix CRAN policy violations. Don't refactor, optimize, or "improve" code beyond what CRAN requires.
8. **Track what's left** — Always end with a clear list of remaining issues for the user.
