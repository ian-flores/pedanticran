# Research Report: CRAN Package Rejection Patterns -- 2020 through 2022

Generated: 2026-02-11

## Executive Summary

The 2020-2022 period saw three major R releases -- R 4.0.0 (April 2020), R 4.1.0 (May 2021), and R 4.2.0 (April 2022) -- each introducing breaking changes that cascaded through the CRAN ecosystem. R 4.0 brought the `stringsAsFactors=FALSE` default (breaking thousands of packages), `class(matrix())` returning `c("matrix","array")`, and `\donttest` examples being run by `R CMD check --as-cran`. R 4.1 introduced the native pipe `|>` and locked the base environment. R 4.2 upgraded the `if()/while()` length>1 condition from WARNING to ERROR, switched help pages to HTML5, and began the UCRT Windows toolchain migration. CRAN also enforced new policies on `tools::R_user_dir()` (replacing rappdirs), internet resource graceful failure, and URL validity. The isoband near-archival incident in October 2022 nearly cascaded to 4,747 dependent packages, including ggplot2.

## Research Question

What were the CRAN package rejection and archival patterns from 2020 through 2022? What new checks or policy changes were introduced? What R version changes broke existing packages?

## R Version Context

- **R 4.0.0 "Arbor Day"** -- released April 24, 2020
- **R 4.0.1 - R 4.0.5** -- patch releases through 2021-03-31
- **R 4.1.0 "Camp Pontanezen"** -- released May 18, 2021
- **R 4.1.1 - R 4.1.3** -- patch releases through 2022-03-10
- **R 4.2.0 "Vigorous Calisthenics"** -- released April 22, 2022
- **R 4.2.1 - R 4.2.2** -- patch releases through 2022-10-31

## CRAN Statistics for the Period

### Package Counts (from R Journal "Changes on CRAN")

| Period | New Packages | Archived | Unarchived | Active Total |
|--------|-------------|----------|------------|-------------|
| 2020 H2 | 818 | 248 | 100 | ~16,851 |
| 2021 H2 | 1,077 | 331 | 113 | ~18,650 |
| 2022 H1 | 485 (3 mo) | 1,179 (3 mo) | 76 (3 mo) | ~18,260 |
| 2022 H2 | -- | -- | 219 | -- |

### Submission Volume (from R Journal)

- 2021 H2: CRAN received 12,256 package submissions, with 21,622 actions (66% auto-processed, 34% manual)
- 2022 H1 (May-Aug): CRAN received 9,860 package submissions, with 17,476 actions (65% auto-processed, 35% manual)

### CRAN Review Team

During this period, the CRAN review team consisted of approximately 5 people who also maintained and developed R itself. First-time submissions ("newbies") received manual human review.

- Source: llrs.dev CRAN review analysis; R Journal "Changes on CRAN" issues

## Key Findings

### Finding 1: stringsAsFactors=FALSE Default -- R 4.0.0 (April 2020)

The single most impactful change in R 4.0.0 was changing the default value of `stringsAsFactors` from `TRUE` to `FALSE` in `data.frame()` and `read.table()`. This default had been in place since R 0.62 (1998).

**What broke:** Any package code that called `data.frame()` or `read.table()` and relied on strings being automatically converted to factors. This affected test expectations, downstream computations on factor levels, and sort orders that depended on locale-dependent factor conversion.

**CRAN testing approach:** Before the R 4.0.0 release, CRAN checks on r-devel began using the environment variable `_R_OPTIONS_STRINGS_AS_FACTORS_=false` to test packages against the new default. Base and recommended packages were pre-modified to work correctly regardless of the setting.

**R CMD check behavior:** Packages on r-devel Debian checks began failing when CRAN switched to the new default during the pre-release testing period (early 2020).

**Real examples:**
- RNeXML (GitHub issue #245): "breaking change introduced in R 4.0.0" -- tests failed because string columns were no longer factors
- fst (GitHub issue #234): needed explicit `stringsAsFactors=TRUE` in test expectations
- protViz (GitHub issue #11): similar breakage in test suite
- rcrunch (GitHub issue #402): described it as the "`stringsAsFactors` apocalypse"

**Fix:** Add explicit `stringsAsFactors=TRUE` where factor behavior was needed, or update code to work with character vectors instead of factors.

**Impact:** "A large number of packages relied on the previous behaviour and so have needed/will need updating." (R 4.0.0 NEWS)

- Source: R Blog (developer.r-project.org/Blog/public/2020/02/16/stringsasfactors); R 4.0.0 NEWS; GitHub issues for RNeXML, fst, protViz, rcrunch

### Finding 2: class(matrix()) Returns c("matrix","array") -- R 4.0.0

R 4.0.0 changed `class(matrix())` to return `c("matrix","array")` instead of just `"matrix"`. This broke code that assumed `class()` returns a length-1 vector.

**What broke:** Any code using patterns like:
```r
if (class(x) == "matrix")         # now FALSE for exact match
if (length(class(x)) == 1)        # no longer true for matrices
```

**R CMD check message (related):**
```
the condition has length > 1 and only the first element will be used
```

**Real examples:**
- BayesianTools (GitHub issue #191): "Issues with changes in new CRAN devel (class of matrix changed)"
- recipes (GitHub issue #422): "new matrix classes for R 4.0.0"

**Fix:** Use `is.matrix()` or `inherits(x, "matrix")` instead of `class(x) == "matrix"`. The R Blog published guidance at developer.r-project.org/Blog/public/2019/11/09/when-you-think-class.-think-again.

**Impact:** This also interacted with the `if()` condition length change (see Finding 3), creating a double-hit for packages using `if (class(x) == "matrix")` patterns.

- Source: R 4.0.0 NEWS; GitHub issues for BayesianTools, recipes; R Blog (2019/11/09)

### Finding 3: if()/while() Condition Length -- Progressive Tightening (R 4.0 through R 4.2)

R progressively tightened handling of conditions with length > 1 in `if()` and `while()` statements across three releases:

| Version | Behavior |
|---------|----------|
| Pre-R 4.0 | Warning (since 2002) |
| R 4.0.0 (2020) | Warning, but R CMD check for CRAN treats as ERROR on Bioconductor |
| R 4.2.0 (2022) | **Error** (upgraded from warning) |

**R runtime error (R 4.2+):**
```
Error in if (c(TRUE, FALSE)) { :
  the condition has length > 1
```

**Additionally in R 4.2:** `&&` and `||` with either argument of length greater than one now gives a warning (intended to become error later).

**CRAN enforcement:** Package maintainers were given a deadline of 2022-04-04 to correct this issue before R 4.2.0 release to safely retain their package on CRAN.

**Fix:** Use `any()`, `all()`, or ensure conditions are scalar. Replace `if (class(x) == "matrix")` with `if (inherits(x, "matrix"))`.

- Source: R 4.0.0 and R 4.2.0 NEWS; jumpingrivers.com/blog/new-features-r420

### Finding 4: \donttest Examples Now Run by R CMD check --as-cran -- R 4.0.0

R 4.0.0 changed `R CMD check --as-cran` to actually run `\donttest{}` examples, rather than merely instructing the tester to do so. This was a major shift in example testing behavior.

**What broke:** Packages that wrapped slow, credential-dependent, or interactive examples in `\donttest{}` (rather than `\dontrun{}`) now had those examples executed during CRAN checks. Examples that were fast locally could exceed CRAN's 10-second-per-example threshold on CRAN's hardware.

**Verbatim R CMD check message (when examples time out):**
```
* checking examples ... [30s] ERROR
Running examples in 'package-Ex.R' failed
```

**Environment variable to temporarily disable:**
```
_R_CHECK_DONTTEST_EXAMPLES_=false
```

**Real case -- Andrew Wheeler's ptools (2022):**
- Package initially auto-failed without notification because "examples took too long"
- Examples that ran instantly locally exceeded limits on CRAN Windows builds
- Plot functions like `spplot()` were particularly slow on CRAN hardware
- Required wrapping plot examples in `\donttest{}`
- Took 20+ submissions over six weeks before final acceptance

**Impact:** This forced many packages to restructure their examples, distinguishing between truly non-runnable examples (`\dontrun`), slow but valid examples (`\donttest`), and interactive examples (`if(interactive())`).

- Source: R 4.0.0 NEWS; forum.posit.co thread on donttest; andrewpwheeler.com/2022/07/22/my-journey-submitting-to-cran

### Finding 5: Bashisms Check for configure/cleanup Scripts -- R 4.0.0

R 4.0.0 added an optional check for non-Bourne-shell code ("bashisms") in `configure` and `cleanup` scripts.

**R CMD check message:**
```
* checking whether the package can be loaded with stated dependencies ... WARNING
A complete check needs the 'checkbashisms' script.
```

**Details:** The check uses the Perl script `checkbashisms` (from Debian's `devscripts` package) and is enabled by default for `R CMD check --as-cran` (except on Windows). It catches:
- `#!/bin/bash` shebangs (should be `#!/bin/sh`)
- Bash-specific syntax like `[[ ]]`, `(( ))`, arrays
- Process substitution `<()` and other non-POSIX constructs

**Fix:** Ensure `configure` and `cleanup` scripts use only POSIX-compliant shell syntax. Scripts generated by `autoconf` are exempt.

- Source: R 4.0.0 NEWS; r-lib/actions issue #111; Writing R Extensions manual

### Finding 6: URL Checking Enhancements -- R 4.0+ through R 4.2

URL checking was significantly enhanced during this period:

**R 4.0 (2020):** R-devel got "more URL checks" with parallel, faster implementations.

**R 4.2.0 (2022):** New functions `tools::check_package_urls()` and `tools::check_package_dois()` added for checking URLs and DOIs in package sources.

**R CMD check message:**
```
* checking URLs ... NOTE
Found the following (possibly) invalid URLs:
  URL: http://example.com
    From: DESCRIPTION
    Status: 301
    Message: Moved Permanently
```

**CRAN enforcement:** CRAN does not tolerate permanent redirections for URLs. Packages were rejected for:
- HTTP to HTTPS redirects (must use HTTPS directly)
- Redirects to www subdomains
- Broken or unreachable URLs in DESCRIPTION, vignettes, README
- DOIs are exempted from redirect requirements

**Common issues:**
- URLs that work in a browser but return non-200 status codes to `curl -I -L`
- URLs that block automated checking (returning 403)
- URLs to services that have moved or shut down

- Source: R-hub blog (2020/12/01/url-checks); CRAN URL checks page; R 4.2.0 NEWS

### Finding 7: tools::R_user_dir() and CRAN Policy on User Filespace -- R 4.0+ / 2021 Enforcement

R 4.0.0 introduced `tools::R_user_dir()` as the sanctioned way for packages to store persistent user data. In late 2021, CRAN began enforcing migration from `rappdirs` to `tools::R_user_dir()`.

**CRAN policy (verbatim):**
> "Packages should not write in the user's home filespace (including clipboards), nor anywhere else on the file system apart from the R session's temporary directory... For R version 4.0 or later, packages may store user-specific data, configuration and cache files in their respective user directories obtained from tools::R_user_dir(), provided that by default sizes are kept as small as possible and the contents are actively managed (including removing outdated material)."

**CRAN enforcement email (2021, paraphrased):**
Packages using `rappdirs::user_cache_dir()` or similar were given a deadline of **2021-11-23** to migrate to `tools::R_user_dir()` or face archival.

**Real cases:**
- rappdirs (GitHub issue #27): "CRAN complains about `user_cache_dir()`"
- rnoaa (GitHub issue #403): scheduled for archival on Nov 30, 2021 for non-compliance; archival would cascade to dependent packages
- sass: changed from `rappdirs::user_cache_dir()` to `tools::R_user_dir()`

**Fix:** Replace `rappdirs::user_cache_dir("pkg")` with `tools::R_user_dir("pkg", "cache")`.

- Source: CRAN Repository Policy; GitHub issues for rappdirs, rnoaa, sass; R 4.0.0 NEWS

### Finding 8: Internet Resource Graceful Failure -- Ongoing Enforcement (2020-2022)

CRAN actively enforced the requirement that packages using internet resources must fail gracefully when those resources are unavailable.

**CRAN policy (verbatim):**
> "Packages which use Internet resources should fail gracefully with an informative message if the resource is not available or has changed (and not give a check warning nor error)."

**Enforcement pattern:** CRAN sent emails to maintainers with tight deadlines (sometimes 1-2 days) to correct issues before archival. Package maintainers receiving these notices were told to correct the issue by a specific date "to safely retain [the] package on CRAN."

**Real case -- gggenomes (2022):** Archived on 2022-08-08 for "CRAN policy violation" regarding internet resources.

**What CRAN checks for:**
- Functions that error when API endpoints are down
- Vignettes that fail to build when external data is unavailable
- Tests that require network access without `skip_on_cran()`
- Examples that crash on network failure

**Fix:** Wrap API calls in `tryCatch()`, check `curl::has_internet()`, use `try()` around downloads, and provide informative messages on failure.

- Source: CRAN Repository Policy; ropensci/gggenomes issue #197; books.ropensci.org/http-testing/graceful

### Finding 9: HTML5 Help Page Validation -- R 4.2.0 (April 2022)

R 4.2.0 switched help page rendering from HTML4 to HTML5, and introduced a validation check for generated HTML.

**Environment variable to enable check:**
```
_R_CHECK_RD_VALIDATE_RD2HTML_=TRUE
```

This was enabled by default for CRAN incoming checks.

**Common validation errors (from roxygen2 issue #1648):**
- Obsolete `align` attributes (e.g., `align='right'`) -- must use CSS `style` instead
- Height/width specifications with `px` units -- HTML5 requires bare integers
- Invalid table markup generated by older roxygen2 versions

**CRAN enforcement deadline:** Packages were required to correct HTML validation problems before **2022-09-01** to safely retain their package on CRAN.

**Davis Vaughan's extrachecks-html5 repo** tracked which CRAN packages had HTML5 validation issues, providing a community resource for identifying affected packages.

**Fix:** Update roxygen2 to version 7.2.1 or later, then run `roxygen2::roxygenize()` to regenerate `.Rd` files. This fixed "99.9% of the issues" according to community reports.

- Source: R Blog (2022/04/08/enhancements-to-html-documentation); DavisVaughan/extrachecks-html5; roxygen2 issue #1648; osmextract issue #259

### Finding 10: UCRT Windows Toolchain Migration -- R 4.2.0

R 4.2.0 switched from MSVCRT to UCRT (Universal C Runtime) on Windows and introduced Rtools42, dropping 32-bit Windows support entirely.

**Timeline:**
- March 2021: CRAN began experimental UCRT package checks
- December 13, 2021: CRAN switched incoming Windows checks to UCRT
- April 2022: R 4.2.0 released with UCRT as the only Windows target

**Impact on CRAN packages:**
- "Nearly 98% of CRAN packages seem to be working (result in OK or NOTE)" with the UCRT toolchain
- Approximately 380 packages (~2%) had issues, though "most will be blocked by their dependencies"
- "Below 1%" of packages needed direct attention from maintainers
- Patches were created for over 100 CRAN packages and several Bioconductor packages

**Common issues:**
- Packages downloading pre-compiled libraries at install time (incompatible with UCRT)
- External DLLs built for MSVCRT
- Encoding problems with non-Latin scripts (discovered when running in UTF-8)
- Packages needing `Makevars.ucrt` files

**Fix:** Use libraries bundled with Rtools42 instead of downloading external pre-compiled binaries. Add `Makevars.ucrt` where necessary.

- Source: R Blog (2021/12/07/upcoming-changes-in-r-4.2-on-windows); R Blog (2021/03/12/windows/utf-8-toolchain-and-cran-package-checks)

### Finding 11: Vignette Rebuild Errors Upgraded to ERROR -- R 4.2.0

R 4.2.0 changed vignette rebuild failures from WARNING to ERROR when vignette running had been skipped (as it frequently is in CRAN checks and by `--as-cran`).

**R CMD check message (R 4.2+):**
```
* checking re-building of vignette outputs ... ERROR
Error(s) in re-building vignettes:
...
```

**Impact:** Packages with vignettes that failed to rebuild (due to missing dependencies, network issues, or LaTeX problems) now got an ERROR instead of a WARNING, making this a blocking issue for CRAN submission.

- Source: R 4.2.0 NEWS

### Finding 12: S3 Method Lookup Changes -- R 4.0.0

R 4.0.0 changed S3 method lookup to skip elements of the search path between the global and base environments by default. This broke packages that relied on S3 methods being found via the search path rather than proper namespace registration.

**What broke:** Packages that exported S3 methods without properly registering them (using `@export` instead of `@exportS3Method` in roxygen2) found that their methods were no longer discovered at runtime.

**Fix:** Use `S3method()` directives in NAMESPACE for delayed S3 method registration, or use `@exportS3Method pkg::generic` in roxygen2 documentation.

- Source: R 4.0.0 NEWS; tshafer.com/blog/2020/08/r-packages-s3-methods; roxygen2 issues

### Finding 13: The Isoband Near-Archival Cascade -- October 2022

In October 2022, the `isoband` package (a dependency of ggplot2) was scheduled for archival on 2022-10-19 due to C++ compilation issues (missing `std::` in testthat C++ headers used by the Catch unit testing framework).

**Potential impact:** The removal of isoband would have led to the removal of **4,747 packages** -- including all packages depending on ggplot2.

**Resolution:** The isoband maintainers fixed the issue before the archival deadline, and the package was retained on CRAN.

**Significance:** This incident highlighted the extreme fragility of CRAN's dependency chain, where a single package's archival could cascade to thousands of downstream packages. It became a major talking point about CRAN's archival policies and dependency management.

- Source: Appsilon blog (appsilon.com/post/cran-and-the-isoband-incident); ggplot2 issue #5006; isoband issue #34

### Finding 14: Implicit Function Declaration Errors -- R 4.2+ / macOS

R 4.2.0 set `_R_CHECK_SRC_MINUS_W_IMPLICIT_` to default to true, reflecting that recent versions of Apple clang on macOS turned implicit function declarations in C from a warning to a compilation error.

**Compiler error:**
```
error: implicit declaration of function 'foo' is invalid in C99
[-Werror,-Wimplicit-function-declaration]
```

**Impact:** Packages with C code that relied on implicit function declarations (common in older C code) would fail to compile on macOS with newer Xcode/clang versions.

**Fix:** Add proper `#include` directives for all functions used, or add explicit function declarations/prototypes.

- Source: R 4.2.0 NEWS; nistara.net/post/compile-issues-r

### Finding 15: Continued Traditional Rejection Patterns (2020-2022)

The traditional rejection patterns documented in the CRAN Cookbook remained the dominant reasons for first-time submission rejections throughout 2020-2022:

#### DESCRIPTION Issues

**Software names not in single quotes:**
> "Please always write package names, software names and API (application programming interface) names in single quotes in title and description."

**Unexplained acronyms:**
> "Please always explain all acronyms in the description text."

**Title case violation:**
> "The Title field should be in title case."

**Missing Authors@R:**
> "Author field differs from that derived from Authors@R. No Authors@R field in DESCRIPTION."

**DOI/URL formatting:**
> "Please add these in the description field...in the form authors (year) <doi:...> with no space after 'doi:'"

#### Code Issues

**Writing to user filespace:**
> "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies."

**print()/cat() for messages:**
> "You write information messages to the console that cannot be easily suppressed... Instead of print()/cat() rather use message()/warning()..."

**options()/par() not restored:**
> "Please make sure that you do not change the user's options, par or working directory. If you really have to do so within functions, please ensure with an immediate call of on.exit() that the settings are reset when the function is exited."

**T/F instead of TRUE/FALSE:**
> "Please write TRUE and FALSE instead of T and F."

#### Documentation Issues

**Missing \value tags:**
> "Please add \value to .Rd files regarding exported methods and explain the functions results in the documentation."

**\dontrun{} misuse:**
> "\dontrun{} should only be used if the example really cannot be executed... Please replace \dontrun with \donttest."

**Check time exceeded:**
> "Overall checktime 20 min > 10 min"

- Source: CRAN Cookbook (contributor.r-project.org/cran-cookbook); ThinkR-open/prepare-for-cran

## CRAN Archival Statistics (2020-2022)

### Overall Archival Patterns (from llrs.dev and CRANhaven analyses)

**Reasons for archival (ranked by frequency):**
1. Uncorrected errors despite reminders (4,366 cumulative events as of 2021)
2. Dependency on already-archived packages (767 events)
3. Policy violations (~500 events)
4. Maintainer requests / orphaned packages (341 events)
5. Invalid maintainer email addresses

**Recovery rates:**
- 39% of all packages ever on CRAN have been archived at least once (out of ~23,058 total)
- 36% of archived packages eventually return to CRAN
- Median return time: ~33 days
- 95% of packages that resubmit are eventually accepted
- 48.7% of archived packages never resubmit

### Notable Enforcement Waves

| Date | Enforcement Target | Deadline |
|------|-------------------|----------|
| Late 2021 | rappdirs -> R_user_dir migration | 2021-11-23 |
| Early 2022 | if()/while() condition length > 1 | 2022-04-04 |
| Mid 2022 | HTML5 Rd validation | 2022-09-01 |
| Oct 2022 | isoband C++ compilation | 2022-10-19 |

## Submission Process Observations (from llrs.dev analysis, Sep 2020-Jan 2021)

- Approximately **one new package submission per hour**
- Queue size ranged between 50-230 packages
- First submissions: median **36 hours** in queue
- Resubmissions: **12-18 hours** median time
- CRAN review folders: pretest -> inspect -> newbies -> recheck -> publish
- 92 packages simultaneously had multiple versions queued
- No published rejection rates or explicit rejection reasons visible in CRAN's queue data

## Recurring Patterns

Based on the research, these were the most impactful categories during 2020-2022, ordered by estimated scope of impact:

1. **stringsAsFactors=FALSE transition** -- thousands of packages needed updating (2020)
2. **class(matrix()) change** -- broke code assuming single-class return (2020)
3. **DESCRIPTION formatting** -- perennial first-submission issue
4. **Missing \value documentation** -- perennial first-submission issue
5. **\donttest examples now executed** -- massive shift in example testing (2020)
6. **if()/while() condition length** -- progressive tightening, ERROR in 4.2 (2022)
7. **HTML5 Rd validation** -- enforcement wave with deadline (2022)
8. **UCRT Windows toolchain** -- ~380 packages affected (2022)
9. **URL validation failures** -- enhanced checking throughout period
10. **tools::R_user_dir() migration** -- enforcement wave with deadline (2021)
11. **Internet resource graceful failure** -- ongoing enforcement
12. **Writing to user filespace** -- ongoing enforcement
13. **Implicit function declarations on macOS** -- error instead of warning (2022)

## Novel Patterns (New in 2020-2022)

| Pattern | Trigger | Version | Impact |
|---------|---------|---------|--------|
| stringsAsFactors=FALSE | Default change | R 4.0.0 | Thousands of packages |
| class(matrix()) = c("matrix","array") | Class change | R 4.0.0 | Many packages |
| \donttest examples run by --as-cran | Check change | R 4.0.0 | All packages with \donttest |
| Bashisms check for configure/cleanup | New check | R 4.0.0 | Packages with shell scripts |
| S3 method lookup skips search path | Lookup change | R 4.0.0 | Packages with exported S3 methods |
| C++20 initial support | New standard | R 4.0.0 | Future impact |
| Native pipe `\|>` syntax | New syntax | R 4.1.0 | Packages depending on R >= 4.1 |
| Base environment locked | Environment change | R 4.1.0 | Packages modifying base env |
| tools::R_user_dir() enforcement | Policy enforcement | R 4.0+ / late 2021 | Packages using rappdirs |
| if()/while() length>1 becomes ERROR | Severity upgrade | R 4.2.0 | ~200 packages |
| HTML5 help pages + validation | HTML standard switch | R 4.2.0 | Many packages with old roxygen2 |
| UCRT Windows toolchain | Toolchain migration | R 4.2.0 | ~380 packages |
| 32-bit Windows dropped | Platform removal | R 4.2.0 | Packages with 32-bit code |
| Vignette rebuild failure = ERROR | Severity upgrade | R 4.2.0 | Packages with fragile vignettes |
| Implicit function declaration = error | Compiler change | R 4.2.0 / macOS | Packages with C code |
| as.vector() S3 method for data frames | Behavior change | R 4.2.0 | Packages using as.vector on df |
| Enhanced URL/DOI checking | New tools functions | R 4.2.0 | All packages with URLs |

## COVID-19 Impact

No direct evidence was found of CRAN publishing COVID-specific policy changes or formally acknowledging pandemic-related review delays. However, indirect evidence suggests:
- The CRAN review team (5 people) continued operating throughout the pandemic
- Queue wait times during Sep 2020-Jan 2021 were 36 hours for new submissions (not dramatically different from other periods)
- A flood of COVID-19-related R packages were submitted in 2020-2021 (e.g., nCov2019, the covid19R project)
- No "summer break" or extended closure announcements were found for 2020 specifically

## Recommendations for Knowledge Base Updates

### New Rules to Consider

1. **COMPAT-01: stringsAsFactors=FALSE Default** (R 4.0+)
   - Severity: LOGIC BUG
   - Code relying on `data.frame()` converting strings to factors will silently produce wrong results
   - Detection: Search for `data.frame()` and `read.table()` without explicit `stringsAsFactors=` argument where downstream code expects factors

2. **COMPAT-02: class(matrix()) Returns Two-Element Vector** (R 4.0+)
   - Severity: ERROR
   - `class(matrix())` returns `c("matrix","array")` -- breaks `class(x) == "matrix"` patterns
   - Detection: Search for `class(x) == "matrix"` or `length(class(x)) == 1`
   - Fix: Use `is.matrix()` or `inherits(x, "matrix")`

3. **COMPAT-03: if()/while() Condition Length > 1 is ERROR** (R 4.2+)
   - Severity: ERROR
   - No longer a warning -- will crash at runtime
   - Detection: Static analysis of `if()` / `while()` with potentially multi-element conditions

4. **CODE-XX: Bashisms in configure/cleanup** (R 4.0+)
   - Severity: WARNING
   - Detection: Run `checkbashisms` on configure/cleanup scripts
   - Fix: Use POSIX-compliant shell syntax only

5. **DOC-XX: HTML5 Rd Validation** (R 4.2+)
   - Severity: NOTE (blocks submission)
   - Detection: Run with `_R_CHECK_RD_VALIDATE_RD2HTML_=TRUE`
   - Fix: Update roxygen2 and re-document

6. **COMP-XX: UCRT Windows Compatibility** (R 4.2+)
   - Severity: ERROR on Windows
   - Packages must not download pre-compiled MSVCRT libraries at install time
   - Fix: Use libraries bundled with Rtools42+

7. **COMP-XX: Implicit Function Declarations** (R 4.2+ / macOS)
   - Severity: ERROR on macOS
   - Detection: Compile with `-Werror=implicit-function-declaration`
   - Fix: Add proper `#include` directives and function prototypes

### Rules to Update

1. **Existing \donttest rules**: Note that R 4.0+ actually runs \donttest examples during CRAN checks
2. **Existing user filespace rules**: Add tools::R_user_dir() as the required replacement for rappdirs
3. **Existing URL rules**: Note enhanced checking in R 4.2 with tools::check_package_urls()

## Open Questions

1. **Exact package counts affected by stringsAsFactors:** The R Blog post says "a large number" but no specific count was published. CRAN may have tracked this internally during r-devel testing.

2. **COVID-19 review delays:** Whether CRAN review times increased during 2020 lockdowns is unclear from public data. The llrs.dev analysis began tracking in September 2020, after the first wave.

3. **CRAN policy diff for 2020-2022:** The eddelbuettel/crp GitHub repository tracks CRAN Repository Policy changes via git history. A detailed diff of policy changes during this period would require examining that repository's commit history directly.

4. **Exact archival counts per year:** The R Journal "Changes on CRAN" articles provide partial data (some covering 3-month periods, others 6-month), making precise yearly totals difficult to reconstruct.

## Sources

- R 4.0.0 NEWS: https://cran.r-project.org/bin/windows/base/old/4.0.0/NEWS.R-4.0.0.html
- R Blog -- stringsAsFactors: https://developer.r-project.org/Blog/public/2020/02/16/stringsasfactors/
- R Blog -- class(matrix()): https://developer.r-project.org/Blog/public/2019/11/09/when-you-think-class.-think-again/
- R Blog -- HTML5 documentation: https://blog.r-project.org/2022/04/08/enhancements-to-html-documentation/
- R Blog -- UCRT Windows changes: https://blog.r-project.org/2021/12/07/upcoming-changes-in-r-4.2-on-windows/
- R Blog -- UTF-8 toolchain and CRAN checks: https://blog.r-project.org/2021/03/12/windows/utf-8-toolchain-and-cran-package-checks/
- R Journal "Changes in R 4.0-4.1": https://journal.r-project.org/news/RJ-2021-1-rcore/
- R Journal "Changes on CRAN" (2020 H2): https://rjournal.github.io/news/RJ-2020-2-cran/
- R Journal "Changes on CRAN" (2021 H2): https://rjournal.github.io/news/RJ-2021-2-cran/
- R Journal "Changes on CRAN" (2022 H1): https://journal.r-project.org/news/RJ-2022-2-cran/
- R Journal "Changes on CRAN" (2022 H2): https://journal.r-project.org/news/RJ-2022-4-cran/
- R-hub blog -- URL checks: https://blog.r-hub.io/2020/12/01/url-checks/
- Jumping Rivers -- R 4.2.0 features: https://www.jumpingrivers.com/blog/new-features-r420/
- llrs.dev -- CRAN review: https://llrs.dev/post/2021/01/31/cran-review/
- llrs.dev -- CRAN archival reasons: https://llrs.dev/post/2021/12/07/reasons-cran-archivals/
- llrs.dev -- CRAN first-try acceptance: https://llrs.dev/post/2024/01/10/submission-cran-first-try/
- CRANhaven -- archival statistics: https://www.cranhaven.org/cran-archiving-stats.html
- Appsilon -- isoband incident: https://www.appsilon.com/post/cran-and-the-isoband-incident
- Andrew Wheeler -- CRAN submission journey: https://andrewpwheeler.com/2022/07/22/my-journey-submitting-to-cran/
- DavisVaughan/extrachecks-html5: https://github.com/DavisVaughan/extrachecks-html5
- CRAN Cookbook: https://contributor.r-project.org/cran-cookbook/
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
- CRAN Repository Policy tracker: https://github.com/eddelbuettel/crp
- CRAN submission checklist: https://cran.r-project.org/web/packages/submission_checklist.html
- CRAN URL checks: https://cran.r-project.org/web/packages/URL_checks.html
- ThinkR-open/prepare-for-cran: https://github.com/ThinkR-open/prepare-for-cran
- R-package-devel mailing list: https://stat.ethz.ch/pipermail/r-package-devel/
- Tom Shafer -- S3 methods: https://tshafer.com/blog/2020/08/r-packages-s3-methods
- roxygen2 HTML5 issue: https://github.com/r-lib/roxygen2/issues/1648
- rappdirs CRAN issue: https://github.com/r-lib/rappdirs/issues/27
- rnoaa archival issue: https://github.com/ropensci/rnoaa/issues/403
- ropensci HTTP testing guide: https://books.ropensci.org/http-testing/graceful.html
- GitHub issues: RNeXML #245, fst #234, protViz #11, BayesianTools #191, recipes #422, isoband #34, ggplot2 #5006
