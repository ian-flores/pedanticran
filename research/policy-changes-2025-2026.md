# CRAN Policy Changes and Enforcement Patterns: August 2025 - February 2026

Generated: 2026-02-08

## Executive Summary

The CRAN Repository Policy document itself (Revision 6286) has not been formally updated since August 2024. However, the period from August 2025 to February 2026 has seen significant *de facto* enforcement changes driven by R 4.5.x release (April 2025), the upcoming R 4.6.0 (in development), and continued tightening of automated checks. The most impactful changes are: (1) C23 becoming the default compilation standard, (2) non-API entry point warnings being upgraded from NOTE to WARNING, (3) `-DR_NO_REMAP` becoming the default for C++ compilation, (4) new bashism checking for configure scripts, and (5) the upcoming deprecation of C++11/C++14 specifications.

## Research Question

What new rules has CRAN started enforcing, what existing rules have gotten stricter, and what patterns are CRAN reviewers focusing on in the August 2025 - February 2026 timeframe?

---

## Part 1: New Checks Introduced via R 4.5.x (April 2025 - October 2025)

R 4.5.0 (released April 2025) and R 4.5.2 (released October 31, 2025) introduced several new checks that directly affect CRAN submissions.

### Finding 1: C23 as Default Compilation Standard

R 4.5.0 defaults to the C23 standard when a C23 compiler is available. This is the single most impactful change for packages with compiled C code.

**What changed:**
- Packages are now installed using C23 where the OS and R build support it
- GCC 13-15, LLVM clang 18-20, Apple clang 15-17 all select C23
- Keywords like `bool`, `true`, `false`, `nullptr` are now reserved in C23

**Impact on packages:**
- Code using `bool`, `true`, `false` as variable names will break
- Implicit function declarations (removed in C23) will cause errors
- Packages can opt out via `SystemRequirements: USE_C17` or `R CMD INSTALL --use-C17`

**Detection:** R CMD check now reports clang warnings including `-Wkeyword-macro` for C23 keyword conflicts.

- Source: R 4.5.0 NEWS, https://cran.r-project.org/doc/manuals/r-release/NEWS.pdf

### Finding 2: `-DR_NO_REMAP` Default for C++ Compilation

R 4.5.0 changed `R CMD INSTALL` (and check) to compile C++ with `-DR_NO_REMAP` by default.

**What changed:**
- C++ code must now use the `Rf_` prefixed versions of R API functions (e.g., `Rf_error` instead of `error`, `Rf_length` instead of `length`)
- This was previously optional but recommended; now it's the default

**Impact on packages:**
- Any C++ code using bare names like `error()`, `length()`, `warning()`, `mkChar()` will fail to compile
- Packages must update to use `Rf_error()`, `Rf_length()`, `Rf_warning()`, `Rf_mkChar()`, etc.
- `COPY_TO_USER_STRING` must be replaced by `Rf_mkChar`

- Source: R 4.5.0 NEWS, spdep package changelog

### Finding 3: Non-API Entry Points Upgraded from NOTE to WARNING

R 4.5.0 upgraded some `R CMD check` NOTEs about non-API entry point usage to WARNINGs.

**What changed:**
- Additional non-API entry points added to the reported list: `IS_LONG_VEC`, `PRCODE`, `PRENV`, `PRVALUE`, `R_nchar`, `Rf_NonNullStringMatch`, `R_shallow_duplicate_attr`, `Rf_StringBlank`, `SET_TYPEOF`, `TRUELENGTH`, `XLENGTH_EX`, `XTRUELENGTH`
- Some of these are now WARNING-level, meaning they block CRAN submission (CRAN requires no warnings)

**Impact on packages:**
- Packages using internal R API functions must migrate to supported API equivalents
- `VECTOR_PTR`, `R_tryWrap`, and others will also become WARNINGs in R 4.6.0

- Source: R 4.5.0 NEWS, https://rstudio.github.io/r-manuals/r-exts/The-R-API.html

### Finding 4: New KaTeX HTML Math Rendering Check

R CMD check can now optionally (included in `--as-cran`) check whether HTML math rendering via KaTeX works for the package `.Rd` files.

**Impact:** Packages with LaTeX math in documentation that doesn't render properly via KaTeX will get a NOTE under `--as-cran`.

- Source: R 4.5.0 NEWS

### Finding 5: Bashism Checking Enabled for Configure Scripts

The `_R_CHECK_BASHISMS_` environment variable now enables thorough checking of bash scripts and bashisms in autoconf-generated configure scripts, not just top-level scripts.

**What changed:**
- Previously checked only configure and cleanup scripts for non-Bourne-shell code
- Now checks more thoroughly, including autoconf-generated scripts
- True for CRAN submission checks (except on Windows)
- Non-portable `#!/bin/bash` shebangs are reported

**Impact:** Packages with configure scripts using bash-specific syntax (e.g., `[[ ]]` comparisons, `${var/pattern/replacement}`) will be flagged.

- Source: R 4.5.0 NEWS, R-package-devel mailing list

### Finding 6: sprintf/vsprintf Detection on All Platforms

R CMD check now reports on ALL platforms if `sprintf` and `vsprintf` from C/C++ are found in compiled code. Previously this was platform-dependent.

**What changed:**
- Universal detection across all OS platforms
- Must replace with `snprintf` or `vsnprintf`
- macOS 13+ has deprecated sprintf entirely

**Impact:** Packages with any `sprintf` usage in C/C++ code will get flagged regardless of platform.

- Source: R 4.5.0 NEWS, macOS deprecation notices

### Finding 7: `browser()` Detection in Non-Interactive Checks

Non-interactive debugger invocations are trapped by setting `_R_CHECK_BROWSER_NONINTERACTIVE_` to true, which is enabled by `R CMD check --as-cran`.

**Impact:** Leftover `browser()` statements in package code will cause check failures under `--as-cran`.

- Source: R 4.5.0 NEWS, testthat changelog

### Finding 8: DESCRIPTION URL Field Checking

`R CMD check --as-cran` now notes problematic URL fields in package DESCRIPTION files.

**What changed:**
- Stricter validation of URLs in DESCRIPTION
- Invalid, broken, or improperly formatted URLs are flagged

- Source: R 4.5.0 NEWS

### Finding 9: Archive Format Support

R CMD check now handles archives with `.tar` or `.tar.zstd` extensions. R CMD build supports `--compression=zstd`.

- Source: R 4.5.2 NEWS

---

## Part 2: Upcoming Changes in R 4.6.0 (In Development, Expected April 2026)

These changes are already in R-devel and will affect CRAN submissions when R 4.6.0 releases.

### Finding 10: C++11/C++14 Specifications Becoming Defunct

**What changed:**
- Specifications for C++11 or C++14 in `src/Makevars` now generate notes
- Associated variables (`CXX11`, `CXX14`, `CXXxxFLAGS`, etc.) are reported as "defunct"
- Default C++ standard will shift to C++20 where available (scheduled for 2026-02-08)
- C++17 remains available as fallback

**Impact:** Packages specifying `CXX_STD = CXX11` or `CXX_STD = CXX14` in Makevars must remove these (99% of CRAN packages specifying these were doing so unnecessarily).

- Source: R 4.6.0 development NEWS

### Finding 11: More Non-API Entry Points Upgraded to WARNING

In R 4.6.0, `R_nchar`, `VECTOR_PTR`, `R_tryWrap`, and others will generate WARNING-level R CMD check notes (upgraded from NOTE).

- Source: R 4.6.0 development NEWS

### Finding 12: Non-API Header Files Removed

`R_ext/Callbacks.h` and `R_ext/PrtUtil.h` are no longer copied to installations. Packages including these must switch to `R_ext/ObjectTable.h`.

- Source: R 4.6.0 development NEWS

---

## Part 3: CRAN Repository Policy Status

### Finding 13: Policy Document Unchanged Since August 2024

The CRAN Repository Policy (Revision 6286) has not been formally updated since August 27, 2024, based on the eddelbuettel/crp policy tracker. The last commit to the tracker was `new rev6286` on August 27, 2024.

This means the formal policy text is unchanged, but enforcement has evolved through:
1. R CMD check gaining new checks (described above)
2. Stricter human review patterns
3. CRAN team focusing on specific areas

- Source: https://github.com/eddelbuettel/crp/commits/master

### Finding 14: CRAN Submission Checklist Additions

The official CRAN submission checklist now includes:
- ORCID identifiers for authors when available
- ROR (Research Organization Registry) IDs for organizations when available
- DOIs formatted as `<doi:10.prefix/suffix>`
- arXiv preprints referenced via `<doi:10.48550/arXiv.ID>`

These appear to be relatively recent additions emphasizing researcher identification standards.

- Source: https://cran.r-project.org/web/packages/submission_checklist.html

---

## Part 4: Enforcement Trends and Reviewer Focus Areas

### Finding 15: Compiled Code is the #1 Focus Area

Based on the R 4.5 and 4.6 changes, CRAN's primary enforcement focus is on compiled code quality:
- C API tightening (non-API entry points being removed/hidden)
- C23 compliance
- R_NO_REMAP enforcement
- sprintf deprecation
- This affects packages using C, C++, Fortran

### Finding 16: System Language Packages Under Scrutiny

Packages using non-R languages face additional challenges:
- **Go packages:** CRAN archived a Go-using package in October 2025. The `go` toolchain was not found on the CRAN Windows build machine, and loading multiple Go c-shared libraries can crash R. CRAN's position on Go packages remains unclear.
- **Rust packages:** Established policy requires bundling via `cargo vendor`, testing with 2+ year old cargo versions, limiting to 1-2 build cores, and declaring `SystemRequirements: Cargo (Rust's package manager), rustc`.
- **General compiled languages:** Must check for tools in configure scripts, report versions, never self-install toolchains.

- Source: R-package-devel mailing list (October 2025), https://cran.r-project.org/web/packages/using_rust.html

### Finding 17: Archival Rates Remain High

Based on CRANhaven dashboard data (January-February 2026):
- 183 packages archived or removed in the last 35 days alone
- Top archival reasons observed:
  1. "Issues were not corrected in time" (most common)
  2. "Email to the maintainer is undeliverable"
  3. Dependency on other archived packages (cascading)
- Historical stats: 39% of all CRAN packages have been archived at some point
- 36% of archived packages eventually return (median: 33 days)

- Source: https://www.cranhaven.org/dashboard-live.html, https://www.cranhaven.org/cran-archiving-stats.html

### Finding 18: File System Policy Enforcement Continues

CRAN continues strict enforcement of the `tools::R_user_dir()` requirement:
- Packages must not write to user's home directory
- Must use `tempdir()` in examples/vignettes/tests
- Persistent data must go through `tools::R_user_dir()` (R >= 4.0)
- Must actively manage stored data (remove outdated material)
- User confirmation required in interactive sessions

- Source: CRAN Repository Policy, https://cran.r-project.org/web/packages/policies.html

### Finding 19: Example Wrapping Under Scrutiny

CRAN continues to focus on proper use of `\dontrun{}` vs `\donttest{}`:
- `\dontrun{}` should ONLY be used when code genuinely cannot execute
- `\donttest{}` for long-running examples (>5 seconds)
- CRAN requests unwrapping examples if they execute in <5 seconds
- CRAN notes examples wrapped in `\donttest{}` are not tested

- Source: CRAN Cookbook, R-package-devel mailing list

---

## Part 5: CRAN Cookbook Reference (Current Best Practices)

The CRAN Cookbook (https://contributor.r-project.org/cran-cookbook/) documents the most common submission issues. Key categories:

### Code Issues (11 documented)
1. T/F instead of TRUE/FALSE
2. Setting specific seeds in functions
3. Using print()/cat() instead of message()/warning()
4. Changing options/par/wd without restoration via on.exit()
5. Writing files to home directory instead of tempdir()
6. Leaving detritus in temp directory
7. Writing to .GlobalEnv
8. Calling installed.packages() instead of requireNamespace()
9. Setting options(warn = -1) instead of suppressWarnings()
10. Installing software in functions/examples/tests
11. Using more than 2 cores

### DESCRIPTION Issues (6 documented)
1. Software names not in single quotes
2. Unexplained acronyms
3. Unnecessary LICENSE files
4. Title not in Title Case
5. Not using Authors@R format
6. Improperly formatted references/DOIs

### General Issues (4 documented)
1. Description field too short
2. Improper example structuring (dontrun/donttest)
3. Package size exceeding 5MB
4. Improper communication with CRAN

- Source: https://contributor.r-project.org/cran-cookbook/

---

## Sources

1. CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
2. CRAN Submission Checklist: https://cran.r-project.org/web/packages/submission_checklist.html
3. CRAN Repository Policy Tracker (eddelbuettel/crp): https://github.com/eddelbuettel/crp/commits/master
4. R 4.5.2 Release NEWS: https://cran.r-project.org/bin/windows/base/NEWS.R-4.5.2.html
5. R 4.6.0 Development NEWS: https://cran.r-project.org/doc/manuals/r-devel/NEWS.html
6. CRAN Cookbook: https://contributor.r-project.org/cran-cookbook/
7. CRAN Cookbook - Code Issues: https://contributor.r-project.org/cran-cookbook/code_issues.html
8. CRAN Cookbook - DESCRIPTION Issues: https://contributor.r-project.org/cran-cookbook/description_issues.html
9. CRAN Cookbook - General Issues: https://contributor.r-project.org/cran-cookbook/general_issues.html
10. Using Rust in CRAN Packages: https://cran.r-project.org/web/packages/using_rust.html
11. CRANhaven Dashboard: https://www.cranhaven.org/dashboard-live.html
12. CRANhaven Archiving Stats: https://www.cranhaven.org/cran-archiving-stats.html
13. R-package-devel mailing list (Go packages): http://www.mail-archive.com/r-package-devel@r-project.org/msg11103.html
14. CRAN Extra Checks (coolbutuseless): https://github.com/coolbutuseless/CRAN-checks
15. R Package Quality: Maintainer Criteria: https://www.r-bloggers.com/2025/07/r-package-quality-maintainer-criteria/
16. R 4.5.0 blog post: https://www.r-bloggers.com/2025/04/whats-new-in-r-4-5-0/
17. Writing R Extensions (R API): https://rstudio.github.io/r-manuals/r-exts/The-R-API.html

---

## Recommendations

For the pedanticran knowledge base and tooling, the following areas should be updated or added:

### High Priority (New Rules)
1. **C23 compilation default** - Add checks for C23 keyword conflicts (`bool`, `true`, `false`, `nullptr` as variable names)
2. **R_NO_REMAP for C++** - Add checks for bare R API function names in C++ code (must use `Rf_` prefix)
3. **Non-API entry points** - Add checks for the expanded list of non-API functions, especially those upgraded to WARNING level
4. **sprintf/vsprintf** - Add checks for sprintf usage in compiled code (must use snprintf/vsnprintf)
5. **browser() statements** - Add checks for leftover browser() calls in package code
6. **Bashisms in configure** - Add checks for non-Bourne-shell syntax in configure scripts

### Medium Priority (Enforcement Tightening)
7. **C++11/C++14 deprecation** - Warn about `CXX_STD = CXX11` or `CXX_STD = CXX14` in Makevars
8. **URL validation in DESCRIPTION** - Add stricter URL checking
9. **KaTeX math rendering** - Check that Rd math notation is KaTeX-compatible
10. **dontrun/donttest** - Enforce proper usage patterns
11. **ORCID/ROR identifiers** - Suggest including these in Authors@R

### Lower Priority (Existing but Worth Tracking)
12. **Go package policy** - Monitor CRAN's evolving position
13. **Package size** - 5MB soft limit, 10MB hard limit
14. **Maintainer email** - Ensure deliverable email addresses
15. **Archival patterns** - 183 packages in 35 days suggests active enforcement

## Open Questions

1. Will CRAN formalize its position on Go-using packages?
2. When exactly will the C++20 default take effect? (Scheduled for 2026-02-08 per R-devel NEWS)
3. Will CRAN update the policy document to reflect the R 4.5/4.6 changes, or continue relying on R CMD check as the enforcement mechanism?
4. Are there additional automated pre-screening checks being added to the CRAN submission pipeline beyond R CMD check?
5. How will cascading archival (due to dependency failures) be handled as more packages with compiled code fail under stricter checks?
