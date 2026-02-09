# Research Report: CRAN Package Rejection Patterns — February through July 2023

Generated: 2026-02-08

## Executive Summary

The Feb-Jul 2023 period was dominated by R 4.3.0's release (April 21, 2023), which introduced several new checks that impacted thousands of existing CRAN packages. The most significant new checks were: (1) "lost braces" in Rd documentation (affecting 3000+ packages), (2) `sprintf`/`vsprintf` usage WARNING in compiled code, (3) `-Wstrict-prototypes` for C code, and (4) C++11/C++14 specification NOTEs. Traditional rejection reasons (DESCRIPTION formatting, `\dontrun` misuse, writing to user filespace, missing `\value` tags) continued to dominate first-time submissions. CRAN also published its first "Using Rust" policy document during this period.

## Research Question

What were the CRAN package rejection patterns from February through July 2023? What new checks or policy changes were introduced? What verbatim rejection text was used?

## R Version Context

- **R 4.2.3** was the current release at the start of the period (March 2023 patch)
- **R 4.3.0 "Already Tomorrow"** was released April 21, 2023 — a major release with many new checks
- **R 4.3.1** was released June 16, 2023 (patch)
- R-devel (pre-4.3) was already running new checks since early 2023, catching issues before the official release

## Key Findings

### Finding 1: R 4.3 "Lost Braces" Check — Massive Impact

R 4.3 introduced a new check in `R CMD check --as-cran` for "lost braces" in Rd documentation files. This was the single most impactful new check, affecting over 3,000 CRAN packages.

**What it detects:**
- Missing backslash before macro names: `code{...}` should be `\code{...}`
- Unescaped braces in mathematical/set notation: `{1, 2}` needs `\{1, 2\}` or `\eqn{}`
- Incorrect list structures: `\itemize{\item{label}{description}}` should use `\describe` instead

**R CMD check message:**
```
* checking Rd files ... NOTE
Lost braces in ...
```

This check was new and had no grace period — packages submitted during Feb-Jul 2023 that had these issues in Rd files would get NOTEs that could lead to rejection during manual review.

- Source: R Journal "Changes in R" (RJ-2023-4-core); R 4.3.0 NEWS

### Finding 2: sprintf/vsprintf WARNING in Compiled Code

R 4.3 elevated the `sprintf`/`vsprintf` check from a platform-specific issue (macOS 13 deprecation) to a cross-platform WARNING in R CMD check.

**Verbatim R CMD check message:**
```
checking compiled code ... WARNING
File '[package]/libs/[file].so':
  Found 'sprintf', possibly from 'sprintf' (C)
    Object: '[object file]'
Compiled code should not call entry points which might
terminate R nor write to stdout/stderr instead of to the
console, nor use Fortran I/O nor system RNGs nor [v]sprintf.
See 'Writing portable packages' in the 'Writing R Extensions' manual.
```

**Real example — clusterCrit v1.2.8 (archived March 2023):**
- Package had `sprintf` and `__sprintf_chk` in `criteria.o`
- Failed on all 4 r-devel Linux platforms (Debian clang, Debian gcc, Fedora clang, Fedora gcc)
- Passed on Windows and release/patched Linux
- Combined with `-Wstrict-prototypes` warnings in `criteria.h`

**Fix:** Replace `sprintf()` with `snprintf()`, `vsprintf()` with `vsnprintf()`.

- Source: Tidyverse blog (2023/03/cran-checks-compiled-code); CRAN archive check results for clusterCrit

### Finding 3: -Wstrict-prototypes C Code WARNING

R 4.3 (r-devel) began compiling with `-Wstrict-prototypes`, catching deprecated C function declarations.

**Verbatim compiler warning:**
```
warning: a function declaration without a prototype is deprecated in all
versions of C [-Wstrict-prototypes]
```

**Two sub-issues:**

Issue A — Empty argument lists:
```c
// WRONG: triggers warning
int myfun() { }
// RIGHT
int myfun(void) { }
```

Issue B — Unspecified argument types (K&R style):
```c
// WRONG
void myfun(x, y) { }
// RIGHT
void myfun(int x, char* y) { }
```

This affected packages with vendored C libraries particularly hard, as the upstream code often used old-style declarations.

- Source: Tidyverse blog (2023/03/cran-checks-compiled-code)

### Finding 4: C++11 Specification NOTE

R 4.3 changed the default C++ standard to C++17. Packages specifying `CXX_STD = CXX11` or `SystemRequirements: C++11` now get a NOTE.

**Verbatim R CMD check message:**
```
* checking C++ specification ...
  NOTE Specified C++11: please drop specification unless essential
```

**Real case — Riccardo Di Francesco (February 27, 2023):**
- Package had `CXX_STD = CXX11` in `src/Makevars`
- Got the NOTE during CRAN incoming checks
- Asked on r-package-devel how to resolve the conflict

**Fix:** Remove `SystemRequirements: C++11` from DESCRIPTION and `CXX_STD=CXX11` from `src/Makevars`, `src/Makevars.win`, `src/Makevars.ucrt`. The C++17 default is backward-compatible with C++11 code.

- Source: r-package-devel mailing list (2023q1/008938); Tidyverse blog

### Finding 5: Continued Traditional Rejection Patterns

The CRAN Cookbook (published by R Consortium) documents the most common rejection patterns with verbatim CRAN reviewer text. These remained the dominant reasons for rejection during 2023 H1:

#### DESCRIPTION Issues

**Software names not in single quotes:**
> "Please always write package names, software names and API (application programming interface) names in single quotes in title and description. e.g: --> 'python'"

**Unexplained acronyms:**
> "Please always explain all acronyms in the description text."

**Unnecessary LICENSE file:**
> "We do not need '+ file LICENSE' and the file as these are part of R. This is only needed in case of attribution requirements or other possible restrictions."

**Title case violation:**
> "The Title field should be in title case. Current version is: 'This is my title.' In title case that is: 'This is My Title.'"

**Missing Authors@R:**
> "Author field differs from that derived from Authors@R. No Authors@R field in DESCRIPTION. Please add one..."

**DOI/URL formatting:**
> "Please add these in the description field...in the form authors (year) <doi:...> with no space after 'doi:', 'https:' and angle brackets for auto-linking."

**Description too short:**
> "The Description field is intended to be a (one paragraph) description of what the package does and why it may be useful. Please add more details about the package functionality and implemented methods in your Description text."

#### Code Issues

**T/F instead of TRUE/FALSE:**
> "Please write TRUE and FALSE instead of T and F. Please don't use 'T' or 'F' as vector names."

**set.seed() in functions:**
> "Please do not set a seed to a specific number within a function."

**print()/cat() for messages:**
> "You write information messages to the console that cannot be easily suppressed. It is more R like to generate objects that can be used to extract the information a user is interested in, and then print() that object. Instead of print()/cat() rather use message()/warning() or if(verbose)cat(..) (or maybe stop()) if you really have to write text to the console. (except for print, summary, interactive functions)"

**options()/par()/setwd() not restored:**
> "Please make sure that you do not change the user's options, par or working directory. If you really have to do so within functions, please ensure with an immediate call of on.exit() that the settings are reset when the function is exited."

**Writing to user filespace:**
> "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies."

**Modifying .GlobalEnv:**
> "Please do not modify the global environment (e.g., by using <<-) in your functions. This is not allowed by the CRAN policies."

**installed.packages():**
> "You are using installed.packages() in your code. As mentioned in the notes of installed.packages() help page, this can be very slow. Therefore do not use installed.packages()."

**options(warn = -1):**
> "You are setting options(warn=-1) in your function. This is not allowed. Please rather use suppressWarnings() if really needed."

**Installing packages in functions:**
> "Please do not install packages in your functions, examples or vignettes. This can make the functions, examples and CRAN-check very slow."

**More than 2 cores:**
> "Please ensure that you do not use more than 2 cores in your examples, vignettes, etc."

#### Documentation Issues

**Missing \value tags:**
> "Please add \value to .Rd files regarding exported methods and explain the functions results in the documentation. Please write about the structure of the output (class) and also what the output means."
> "If a function does not return a value, please document that too, e.g., \value{No return value, called for side effects} or similar"

**Editing .Rd instead of .R (roxygen2):**
> "Since you are using 'roxygen2', please make sure to add a @return-tag in the corresponding .R-file and re-roxygenize() your .Rd-files."

**\dontrun{} misuse:**
> "\dontrun{} should only be used if the example really cannot be executed (e.g., because of missing additional software, missing API keys, ...) by the user. That's why wrapping examples in \dontrun{} adds the comment ('# Not run:') as a warning for the user. Does not seem necessary. Please replace \dontrun with \donttest."
> "Please unwrap the examples if they are executable in < 5 sec, or replace \dontrun{} with \donttest{}."

**All examples wrapped in \donttest:**
> "All your examples are wrapped in \donttest{} and therefore do not get tested. Please unwrap the examples if that is feasible and if they can be executed in < 5 sec for each Rd file or create additionally small toy examples to allow automatic testing."

**Interactive examples:**
> "Functions which are supposed to only run interactively (e.g., shiny) should be wrapped in if(interactive()). Please replace \dontrun{} with if(interactive()){} if possible, then users can see that the functions are not intended for use in scripts."

**Check time exceeded:**
> (NOTE) "Check: Overall checktime, Result: NOTE. Overall checktime 20 min > 10 min"

- Source: CRAN Cookbook (contributor.r-project.org/cran-cookbook)

### Finding 6: Specific 2023 H1 Mailing List Cases

#### Case: Package failing on Debian only (March 2023)
- **Package:** Anonymous ("APACKAGE"), C++ package using Rcpp
- **Error:** `unable to load shared object '...APACKAGE.so': undefined symbol: _ZTIN6nnlib25layerE`
- **Category:** Compiled code / platform-specific linking
- **Context:** Passed on Windows, failed on Debian with undefined C++ symbol
- **Notes:** This was a first submission; previous version had shown intermittent errors on Debian that resolved without code changes, suggesting platform instability

#### Case: NEWS file format failure (April 2023)
- **Package:** smaa v0.3-2
- **Error:** `Problems with news in 'NEWS': Cannot process chunk/lines: smaa 0.3-0 ... etc ...`
- **Category:** NEWS file formatting
- **Context:** NOTE appeared during Debian check but not on Windows or r-hub. The NEWS file had not been modified for this release. R 4.3 introduced stricter NEWS file parsing (checking both NEWS.md and plain text NEWS formats).

#### Case: movecost v2.0 — HTML tidy and temp detritus (April 2023)
- **Package:** movecost v2.0
- **Notes:**
  1. HTML manual conversion error: `'CreateProcess' failed to run 'd:\rtools43\...\tidy.exe'`
  2. Temp directory detritus: `Found the following files/directories: 'lastMiKTeXException'`
- **Category:** Build environment / temporary files
- **Context:** Passed all local checks via devtools but failed CRAN incoming pre-test. The tidy.exe issue was a CRAN infrastructure problem; the `lastMiKTeXException` was detritus from LaTeX processing.

#### Case: growthPheno v2.1.17 — Upload form issue (January 2023)
- **Package:** growthPheno v2.1.17
- **Issue:** CRAN upload form showing "Detected package information [non-editable]" and file input resetting
- **Category:** Submission process / infrastructure
- **Context:** Not a content rejection but a submission interface confusion

#### Case: daewr v1.2-9 — Win-builder access error (April 2023)
- **Package:** daewr v1.2-9
- **Error:** `ERROR: Access to the path 'C:\Inetpub\ftproot\R-devel\daewr_1.2-9.tar.gz' is denied.`
- **Category:** Submission process / infrastructure
- **Context:** Upload to win-builder R-devel failed with access denied; likely a concurrent upload or unprocessed file issue

#### Case: gcplyr — Windows lazy loading error (early 2023)
- **Package:** gcplyr
- **Error:** `Error in if (file.size(codeFile) == file.size(loaderFile)) warning("package seems to be using lazy loading already") else { : missing value where TRUE/FALSE needed`; `ERROR: lazy loading failed for package 'gcplyr'`
- **Category:** Infrastructure / temporary Windows build issue
- **CRAN response (Uwe Ligges):** "This was a temporary hicc up on the Windows machine, all check should have been triggered again."

### Finding 7: noSuggests Additional Check

CRAN runs packages with `_R_CHECK_DEPENDS_ONLY_=true` (the "noSuggests" check) on Brian Ripley's infrastructure at Oxford. This tests that packages work when Suggests/Enhances are unavailable.

**Impact:** Packages that unconditionally use Suggested packages in vignettes, tests, or examples fail this check. Common issues:
- Vignettes using `library(suggested_pkg)` without conditional checks
- Tests not using `if (requireNamespace("pkg", quietly = TRUE))`
- Style packages in vignettes (e.g., BiocStyle) not declared in VignetteDepends

**URL:** https://www.stats.ox.ac.uk/pub/bdr/noSuggests/

### Finding 8: HTML5 Validation Enforcement

R 4.2 switched to HTML5 for help page rendering. During 2023 H1, CRAN actively enforced HTML5 compliance:

- **Environment variable:** `_R_CHECK_RD_VALIDATE_RD2HTML_=TRUE`
- **Common issues:** Elements removed from HTML5 (e.g., `align='right'`), `px` units in length specifications
- **Fix:** Update roxygen2 to latest version and re-document

Packages using older roxygen2 versions generated invalid HTML5 from Rd files and were flagged.

### Finding 9: Internet Resource Graceful Failure (Ongoing Enforcement)

CRAN continued enforcing the graceful failure policy for packages using internet resources:

> "Packages which use Internet resources should fail gracefully with an informative message if the resource is not available or has changed (and not give a check warning nor error)."

This was actively enforced during 2023 H1 with tight deadlines (sometimes 1 day) for correction before archival.

### Finding 10: Package Size Limit (5MB at the time)

During this period, the CRAN package size limit was still 5MB:

> "A CRAN package should not be larger than 5 MB. Please reduce the size."

(Note: This was later raised to 10MB in November 2025.)

## Recurring Patterns

Based on the research, these were the most frequent rejection/issue categories during Feb-Jul 2023, ordered by estimated frequency:

1. **DESCRIPTION formatting** — Title case, single quotes, acronyms, DOI formatting, Authors@R
2. **Missing \value documentation** — Nearly universal for first-time submissions
3. **\dontrun{} misuse** — Should be \donttest{} or if(interactive())
4. **Writing to user filespace** — Must use tempdir()
5. **Compiled code warnings** — sprintf, strict-prototypes (NEW in this period)
6. **C++ standard specification** — C++11 NOTE (NEW in this period)
7. **Lost braces in Rd** — (NEW in this period, massive impact)
8. **print()/cat() for messages** — Must use message()/warning()
9. **options()/par() not restored** — Must use on.exit()
10. **Examples too slow / all wrapped** — Must have unwrapped executable examples

## Novel Patterns (New in 2023 H1)

These were new or newly enforced during the Feb-Jul 2023 period:

| Pattern | Trigger | Impact |
|---------|---------|--------|
| Lost braces in Rd | R 4.3 new check | 3000+ packages |
| sprintf WARNING | R 4.3 cross-platform | All packages with C code using sprintf |
| -Wstrict-prototypes | R 4.3 compiler flag | Many packages with C code |
| C++11/14 specification NOTE | R 4.3 default C++17 | All packages specifying old C++ standards |
| NEWS file stricter parsing | R 4.3 | Packages with non-standard NEWS files |
| HTML5 Rd validation | R 4.2 enforcement wave | Packages with old roxygen2 |
| is.atomic(NULL) returns FALSE | R 4.3 | Packages testing NULL with is.atomic() |
| NCOL(NULL) returns 0 not 1 | R 4.3 | Packages relying on NCOL(NULL) == 1 |
| Using Rust policy | New CRAN document (mid-2023) | Packages with Rust code |

## Submission Statistics (from llrs.dev analysis, Sep 2020 - Jan 2024)

- **35% of first-time submissions rejected** (65% accepted first try)
- **14.5% of all submission attempts rejected overall**
- Among rejected first submissions:
  - 1 rejection: 21.9% of new packages
  - 2 rejections: 8.2% of new packages
  - 3+ rejections: 4.3% of new packages
- Experienced maintainers struggle similarly to newcomers (suggesting environmental/platform issues rather than knowledge gaps)

## CRAN Infrastructure Notes

During Feb-Jul 2023, several mailing list threads reported infrastructure issues:
- Windows build machine "hiccups" causing spurious failures (gcplyr case)
- Win-builder access denied errors for R-devel uploads
- HTML tidy tool failures on CRAN Windows (movecost case)
- Dependency compilation failures when CRAN machines had infrastructure problems (Rcpp unavailable)

These were temporary but caused confusion for maintainers who couldn't distinguish infrastructure failures from genuine package problems.

## Recommendations for Knowledge Base Updates

Based on this research, the following should be added or updated in `/Users/borikropotkin/pedanticran/knowledge/cran-rules.md`:

### New Rules to Add

1. **RD-01: Lost Braces in Rd Documentation** (R 4.3+)
   - Severity: NOTE (can block submission)
   - Verbatim check: `Lost braces in ...`
   - Detection: Parse Rd files for unescaped `{`/`}` in text, missing `\` before macros, `\itemize` with `\item{label}{desc}` pattern
   - Fix: Escape braces as `\{`/`\}`, use `\eqn{}` for math, use `\describe` for labeled lists

2. **NEWS-01: NEWS File Format** (R 4.3+)
   - Severity: NOTE
   - Detection: Validate NEWS and NEWS.md parsing with `tools::news()`
   - Fix: Ensure NEWS file follows R-parseable format

3. **COMP-07: is.atomic(NULL) Changed** (R 4.3+)
   - Severity: LOGIC BUG
   - `is.atomic(NULL)` now returns `FALSE` (was `TRUE`)
   - `NCOL(NULL)` now returns `0` (was `1`)

4. **COMP-08: Rust Package Requirements** (mid-2023+)
   - Severity: REJECTION
   - Must vendor cargo crates for offline installation
   - Must include `inst/AUTHORS` for Rust dependencies
   - Must include authorship/copyright info in DESCRIPTION

### Rules to Update

1. **COMP-06** (C++ Standard): Add verbatim NOTE text: `Specified C++11: please drop specification unless essential`
2. **CODE-16** (sprintf): Upgrade from NOTE to WARNING for R 4.3+; add full verbatim text
3. **SIZE-01**: Note that 5MB was the limit during this period (later raised to 10MB in Nov 2025)

### Rules Already Well-Covered

The existing knowledge base already covers the most common traditional rejection reasons well. The CRAN Cookbook verbatim texts align with what's already documented in the knowledge base for DESCRIPTION, code, and documentation issues.

## Open Questions

1. **Exact archival counts for H1 2023:** The R Journal article covering this period is rendered as JavaScript and the actual text couldn't be extracted. The H2 2023 period had 701 archivals and 332 unarchivals; H1 numbers are not available from this research.

2. **HTML5 enforcement timeline:** The exact dates when CRAN began sending HTML5 compliance emails in bulk during 2023 H1 are unclear. The check was introduced in R 4.2 but enforcement waves happened later.

3. **Specific first-submission rejection rate for this period:** The 35% first-time rejection rate covers Sep 2020 - Jan 2024 broadly. It's unknown if this rate changed specifically during the R 4.3 transition.

4. **KaTeX math rendering check:** R 4.3 added optional checking of HTML math rendering via KaTeX for Rd files. The extent to which this caused rejections in 2023 H1 is unclear.

## Sources

- R-package-devel mailing list archives: https://stat.ethz.ch/pipermail/r-package-devel/ (2023q1, 2023q2)
- Mail Archive mirror: https://www.mail-archive.com/r-package-devel@r-project.org/
- Tidyverse blog — New CRAN requirements for C/C++: https://tidyverse.org/blog/2023/03/cran-checks-compiled-code/
- CRAN Cookbook: https://contributor.r-project.org/cran-cookbook/
- R Journal "Changes in R": https://journal.r-project.org/news/RJ-2023-4-core/
- R Journal "Changes on CRAN": https://journal.r-project.org/news/RJ-2023-1-cran/ and https://journal.r-project.org/news/RJ-2023-3-cran/
- llrs.dev CRAN submission statistics: https://llrs.dev/post/2024/01/10/submission-cran-first-try/
- CRAN archived check results (clusterCrit): https://cran-archive.r-project.org/web/checks/2023/2023-03-11_check_results_clusterCrit.html
- noSuggests check: https://www.stats.ox.ac.uk/pub/bdr/noSuggests/README.txt
- HTML5 compliance: https://github.com/DavisVaughan/extrachecks-html5
- CRAN "Using Rust": https://cran.r-project.org/web/packages/using_rust.html
- R 4.3.0 announcement: https://stat.ethz.ch/pipermail/r-announce/2023/000691.html
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
