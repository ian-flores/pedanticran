# CRAN Package Rejection Patterns: January -- June 2024

Generated: 2026-02-08
Sources: R-package-devel mailing list (stat.ethz.ch/pipermail), mail-archive.com, CRAN Cookbook, R-bloggers, CRANhaven, individual blog posts

---

## Executive Summary

The first half of 2024 saw a continuation and intensification of several CRAN enforcement trends. Key findings:

1. **~35% of new submissions are rejected on first try** (down from previous estimates), with 14.5% of all submission attempts rejected overall.
2. **Cascading archival** emerged as a major pain point -- packages archived because their dependencies were archived (dotwhisker, survivalSL).
3. **Rust/compiled code** requirements became stricter -- Rust compiler version reporting was newly enforced, and library size from debug symbols caused removals.
4. **"Lost braces"** warnings in Rd documentation became newly flagged across thousands of packages.
5. **R 4.4.0** (April 2024) changed NULL semantics, which will break packages relying on old behavior.
6. **gcc14** on Fedora introduced new compiler warnings that surfaced as CRAN check failures.
7. **CRAN process frustrations** dominated the mailing list -- packages removed without notification, no confirmation emails on resubmission, inability to reproduce Debian-only failures.

---

## Individual Rejection Cases

### Case 1: SuperCell -- License + Size + Dependencies (July 2024, reported Jan-Jun thread)

**Package**: SuperCell
**Category**: LICENSE, SIZE, DEPENDENCIES
**First submission**: Yes

**Verbatim CRAN feedback**:
- "Non-FOSS package license (file LICENSE)"
- "Suggests or Enhances not in mainstream repositories: velocyto.R"
- Invalid URL format (non-canonical CRAN link)
- Tarball size: 9,076,436 bytes

**Details**: Used CC BY-NC-ND 4.0 license. While technically on CRAN's accepted list, no other CRAN package combines NonCommercial + NoDerivatives clauses. Package had 21 non-default imports (NOTE threshold is ~20). Data exceeded 5MB limit.

**Novel aspect**: The CC BY-NC-ND license edge case -- technically listed but practically unprecedented on CRAN.

---

### Case 2: iopspackage -- Example Runtime Exceeded (Q1 2024)

**Package**: iopspackage (R-IO-PS)
**Category**: EXAMPLES, RUNTIME
**Submission type**: New

**Verbatim CRAN feedback**:
- "Examples with CPU (user + system) or elapsed time > 5s"
- Timing: user 10.06s, system 3.35s, elapsed 35.04s
- Detritus: `lastMiKTeXException` left in temp directory

**Details**: The 35s elapsed vs 13s CPU time indicated either internet access or heavily loaded machines. Uwe Ligges noted the disparity suggested "something waiting like internet access."

**Fix recommended**: Replace large datasets with toy examples, wrap longer examples in `\donttest{}`, implement timeout mechanisms.

---

### Case 3: rar -- Shared Library Too Large from Debug Symbols (January 2024)

**Package**: rar
**Category**: COMPILED CODE, SIZE
**Submission type**: Existing package, correction deadline

**Verbatim CRAN feedback**:
- "installed size is 8.9Mb; sub-directories of 1Mb or more: libs 8.7Mb"
- "Please correct before 2024-02-02 to safely retain your package on CRAN."

**Details**: Debug symbols in shared libraries inflated sizes. Varied across platforms:
- Ubuntu Linux (RHub): 18.2Mb
- Fedora Linux (RHub): 6.8Mb
- macOS arm64: 8.5Mb

**Fix**: Modify Makevars to strip debugging symbols.

---

### Case 4: prqlr -- Tarball Size for Rust Package (Q2 2024)

**Package**: prqlr
**Category**: SIZE, RUST
**Submission type**: Resubmission

**Verbatim CRAN feedback**:
- "Size of tarball: 18099770 bytes. Please reduce to less than 5 MB for a CRAN package."

**Details**: Uwe Ligges clarified the CRAN maintainer didn't recognize this involved Rust code. Many existing packages exceed 5MB (rcdklibs 19MB, fastrmodels 15MB, prqlr itself 15MB). The 5MB limit is more of a guideline for Rust packages, but proper documentation is required.

**Resolution**: Resubmit with proper documentation of Rust-based nature.

**Novel aspect**: Size limit enforcement is inconsistent -- depends on whether the reviewer recognizes compiled language requirements.

---

### Case 5: dotwhisker -- Cascading Archival (April 2024)

**Package**: dotwhisker
**Category**: DEPENDENCIES, ARCHIVAL
**Submission type**: Existing package removed

**Verbatim CRAN message**:
- "Archived on 2024-04-12 as requires archived package 'prediction'."

**Details**: Ben Bolker found this puzzling because dotwhisker's DESCRIPTION had no direct dependency on 'prediction'. The dependency was indirect/transitive (through 'margins' package which depends on 'prediction'). This cascading archival affected downstream packages.

**Novel aspect**: Transitive dependency archival -- your package gets archived for a dependency you don't directly import.

---

### Case 6: survivalSL -- Archived Dependency Cascade (March 2024)

**Package**: survivalSL
**Category**: DEPENDENCIES, ARCHIVAL
**Submission type**: Update after archival

**Details**: Moved archived 'survivalmodels' from Depends to Suggests, but CRAN archived the package anyway. Developer was working on replacement implementation but needed time.

**Novel aspect**: Even moving an archived dep to Suggests doesn't save you from archival.

---

### Case 7: refseqR -- Removal Without Notification (April-May 2024)

**Package**: refseqR
**Category**: PROCESS, ARCHIVAL
**Date**: Removed April 30, 2024

**Verbatim from maintainer**:
- "This news is extremely upsetting, especially because I did not receive any communication or warning regarding the issue."

**Novel aspect**: Package removed without prior warning email reaching the maintainer.

---

### Case 8: MetAlyzer -- Resubmission After Archival (March 2024)

**Package**: MetAlyzer
**Category**: ARCHIVAL, RESUBMISSION
**Version**: 1.0.0

**Details**: Previously archived November 2023 with "OK: 5, ERROR: 8" results. New version passed local R CMD check but failed CRAN automated pre-tests with 2 NOTEs (Windows) and 3 NOTEs (Debian). Maintainer asked about specific procedures for previously archived packages.

---

### Case 9: openaistream -- License DCF Format (January 2024)

**Package**: openaistream
**Category**: DESCRIPTION, LICENSE
**Version**: 0.2.0
**First submission**: No (update)

**CRAN feedback**: Invalid DCF in the license stub. Used "MIT + file LICENSE" format but CRAN flagged DCF formatting.

---

### Case 10: petersenlab -- Version + URIs + Temp Files (April 2024)

**Package**: petersenlab
**Category**: DESCRIPTION, DOCS, CODE
**Version**: 0.1.2-9033

**Verbatim CRAN NOTEs**:
1. "Version contains large components" -- flagged 9033 version component
2. "Found the following (possibly) invalid file URIs: URI: 10.1177/0146621613475471" -- DOIs in man pages treated as file URIs
3. "Found the following files/directories: 'encryptionKey.RData' 'encrypytedCredentials.txt'" -- files generated by example code left in check directory

**Novel aspect**: DOIs in Rd files being treated as file URIs rather than references. The version component 9000+ convention (used for dev versions) flagged as "large components."

---

### Case 11: NMRphasing -- Dependency Sanitizer Failure (Q1-Q2 2024)

**Package**: NMRphasing
**Category**: COMPILED CODE, DEPENDENCIES
**Version**: 1.0.6

**Verbatim CRAN pre-test result**: "gcc-san: Status: 1 ERROR"

**Details**: The error originated from MassSpecWavelet dependency, not NMRphasing itself:
> "MassSpecWavelet/src/find_local_maximum.c:492: writing outside the bounds of an allocated array"

Previous version had OK status on all 13 checks. The gcc-ASAN/UBSAN diagnostics caught memory issues in upstream code.

**Novel aspect**: Your package rejected because of sanitizer errors in your *dependency's* C code.

---

### Case 12: Clarabel -- Rust Vendor NOTEs (June 2024)

**Package**: Clarabel
**Category**: RUST, DOCUMENTATION
**Submission type**: Update

**Verbatim NOTEs**:
- "Found the following CITATION file in a non-standard place: src/rust/vendor/clarabel/CITATION.bib"
- "Found the following sources/headers not terminated with a newline: src/rust/vendor/lapack-sys/lapack/LAPACKE/src/lapacke_cgetsqrhrt_work.c"

**Details**: Issues in vendored Rust dependencies. Can't modify vendored files without breaking checksums. Developer planned to submit upstream PRs.

---

### Case 13: CirceR -- Java + Vignette + URLs (April 2024)

**Package**: CirceR
**Category**: DOCS, COMPILED CODE, URLs

**Verbatim NOTEs**:
1. "Package has a VignetteBuilder field but no prebuilt vignette index."
2. "Package has FOSS license, installs .class/.jar but has no 'java' directory."
3. Three URLs returning 301 redirects (http->https, www->non-www)

**Details**: Java dependencies bundled without source. Developer asked whether CRAN requires bundling all Java dependency source code.

---

### Case 14: huxtable -- Reverse Dependency Failure (Q1 2024)

**Package**: huxtable
**Category**: DEPENDENCIES, REVERSE DEPS
**Version**: 5.5.4

**Details**: Update failed reverse dependency checks for homnormal and RSStest. Error: "there is no package called 'knitr'" -- knitr was Suggests, not Imports, but was required at runtime. Developer fixed and resubmitted with same version number, but CRAN may have tested the old tarball.

---

### Case 15: CRAN Rejection for Removing Failing Tests (Q2 2024)

**Package**: Not named (smallepsilon/Jesse)
**Category**: TESTS, POLICY

**Verbatim CRAN feedback**:
- "removed the failing tests which is not the idea of tests."

**Details**: Developer had tests using `identical()` that failed cross-platform due to parallel processing non-reproducibility. Replaced with platform-independent tests and moved platform-specific ones to local. CRAN rejected because tests were "removed."

**Novel aspect**: CRAN explicitly checks for test removal between versions and rejects it.

---

### Case 16: milorGWAS -- Resubmission After Compilation Archival (June 2024)

**Package**: milorGWAS
**Category**: COMPILED CODE, ARCHIVAL

**Verbatim NOTE**:
- "Archived on 2024-01-19 as issues were not corrected in time."
- Spelling false positives: "GWAS", "Milet", "et", "al" flagged as misspelled

---

### Case 17: quarto -- New Vignette Engine Check Failure (Q1 2024)

**Package**: quarto
**Category**: VIGNETTES

**Verbatim NOTE**:
- "Package has 'vignettes' subdirectory but apparently no vignettes. Perhaps the 'VignetteBuilder' information is missing from the DESCRIPTION file?"

**Details**: Custom vignette engine not recognized during check because the package wasn't yet installed on the test system. Passed on Windows but failed on Debian.

---

### Case 18: RITCH -- CPU Time Ratio (January 2024)

**Package**: RITCH
**Category**: EXAMPLES, PARALLELISM
**Version**: 0.1.23

**Verbatim NOTE**:
- "Examples with CPU time > 2.5 times elapsed time"
- User: 3.968s, System: 0.092s, Elapsed: 0.831s (ratio 4.886)

**Details**: Package imports data.table which uses multi-threading. NOTE appears only on Debian. Fix: `data.table::setDTthreads(2)` in examples.

---

### Case 19: Temp Directory Detritus from Downloads (May 2024)

**Package**: Not named
**Category**: CODE, TEMP FILES

**Verbatim NOTE**:
- "Found the following files/directories: 'RtmpRfd2nv\\02202307_MESA' 'RtmpRfd2nv\\02202307_MESA.zip'" (and 18+ additional files)

**Details**: Package downloads and caches ZIP files in temp directory. Developer wanted caching but CRAN requires cleanup.

---

### Case 20: CRAN External Libraries Policy Frustration (January 2024)

**Package**: Not named (Neal Richardson)
**Category**: POLICY, COMPILED CODE

**Details**: CRAN policy states downloading pre-compiled software should be "a last resort and with the agreement of the CRAN team." Richardson's project had been trying to get CRAN approval since October 2023 with no response to multiple emails.

**Novel aspect**: CRAN team non-responsive to policy clarification requests for 3+ months.

---

### Case 21: epiparameter -- Dual Licensing Rejected (2024)

**Package**: epiparameter
**Category**: LICENSE

**Verbatim CRAN feedback**:
- "A package can only be licensed as a whole. It can have a single license or a set of *alternative* licenses. If the data have to be licensed differently then the code, you have to provide the data in a separate data package with the other license."

**Resolution**: Split into epiparameter (MIT, code only) and epiparameterDB (CC0, data only).

---

### Case 22: sundialr -- Upstream C Library Warnings (Q1 2024)

**Package**: sundialr
**Category**: COMPILED CODE
**Submission type**: Resubmission after archival

**Warnings**:
- "conversion from 'long long unsigned int' to 'long unsigned int' changes value"
- "a function declaration without a prototype is deprecated in all versions of C"

**Details**: Warnings from upstream SUNDIALS C library. Developer reluctant to modify upstream code.

---

### Case 23: gesca -- HTML Trimming Empty Paragraphs (Q1 2024)

**Package**: gesca
**Category**: DOCUMENTATION

**Verbatim NOTE**:
- "gesca.run.Rd:127:1: Warning: trimming empty `<p>`"

**Details**: Empty paragraph tags in Rd documentation flagged during HTML conversion.

---

### Case 24: arcgisutils -- Debian-Only Check Failure (May 2024)

**Package**: arcgisutils
**Category**: COMPILED CODE, PLATFORM
**Version**: 0.3.0

**Details**: Package failing checks only on Debian while passing Ubuntu, Mac, and Windows. Developer unable to reproduce locally. Modified Makevars to remove problematic directory but issue persisted.

---

### Case 25: epanet2toolkit -- gcc14 Fedora Warnings (Q2 2024)

**Package**: epanet2toolkit
**Category**: COMPILED CODE

**Details**: New warnings from gcc14 on CRAN's Fedora check infrastructure. Developer sought to reproduce using Docker.

---

### Case 26: Submission Process -- No Confirmation Email (June 2024)

**Package**: Not named (Paul Kabaila)
**Category**: PROCESS

**Details**: After initial submission and CRAN response with NOTEs, developer fixed and resubmitted. No confirmation email received on resubmission. Process ambiguity about whether resubmission was received.

---

### Case 27: callr and Core Usage Policy (Q2 2024)

**Package**: Not named
**Category**: CODE, PARALLELISM

**Policy question**: Does each `callr` background R session count toward the 2-core CRAN check limit?

---

### Case 28: S3 Generic/Method Consistency Warning (Q1 2024)

**Category**: CODE

**Verbatim WARNING**:
```
checking S3 generic/method consistency ... WARNING
myscale:
  function(x, y)
myscale.default:
  function(x)
```

**Details**: Parameter mismatch between generic and method signature now triggers WARNING (previously might have been NOTE).

---

## Recurring Patterns

### Pattern 1: Cascading Dependency Archival
Multiple packages (dotwhisker, survivalSL, NMRphasing) were affected by dependencies being archived or having issues. This is a systemic risk where your package's fate depends on your dependency graph.
- **Frequency**: 3+ cases in H1 2024
- **Existing in KB**: Partially (no specific rule about cascading archival defense)

### Pattern 2: Compiled Code Size and Sanitizers
Packages with C/C++/Rust code faced multiple issue types:
- Debug symbols inflating library size
- gcc-ASAN/UBSAN catching memory issues in dependencies
- gcc14 introducing new warnings
- Rust vendoring creating documentation/format NOTEs
- **Frequency**: 5+ cases
- **Existing in KB**: Partially

### Pattern 3: Example Runtime and Parallelism
The 2-core limit and 5-second example runtime remain constant pain points. data.table multi-threading triggers false positives.
- **Frequency**: 3+ cases
- **Existing in KB**: Yes (CODE-09, CODE-10)

### Pattern 4: Temporary File Cleanup
Multiple packages flagged for leaving files in temp directories, either from downloads, caching, or example code.
- **Frequency**: 3+ cases
- **Existing in KB**: Yes (CODE-06)

### Pattern 5: URL/DOI Formatting
URLs returning 301 redirects, DOIs being treated as file URIs, non-canonical CRAN URLs.
- **Frequency**: 3+ cases
- **Existing in KB**: Partially (DESC-06 covers formatting but not redirect/URI issues)

### Pattern 6: Process Frustrations
Packages removed without notification, no confirmation emails on resubmission, CRAN team non-responsive to policy questions.
- **Frequency**: 3+ cases
- **Existing in KB**: No

### Pattern 7: Documentation HTML Validation
"Lost braces" in Rd files and "trimming empty `<p>`" NOTEs became newly enforced across thousands of packages.
- **Frequency**: Widespread (thousands of packages)
- **Existing in KB**: No

### Pattern 8: Test Removal Detection
CRAN explicitly checks for removed tests between versions and rejects submissions where failing tests were deleted rather than fixed.
- **Frequency**: At least 1 explicit case
- **Existing in KB**: No

---

## Novel Patterns (Not in Existing Knowledge Base)

### Novel 1: "Lost Braces" Rd Warning (NEW in 2024)
CRAN began newly flagging "lost braces" in `\itemize` and `\value` sections of Rd documentation. Thousands of packages affected. Two subtypes:
- In `\itemize`: suggests `\describe` was intended
- In `\value`: `\item` is implicitly in `\describe`, no need for explicit `\describe`

### Novel 2: Cascading Archival Defense
No current rule addresses how to protect against transitive dependency archival. Need rules about:
- Monitoring dependency health
- Using conditional imports
- Having fallback strategies for archived deps

### Novel 3: Rust-Specific Requirements (Formalized 2024)
CRAN published explicit "Using Rust in CRAN Packages" guidelines:
- Must report `rustc` version in install log BEFORE compilation
- Must test with 2+ year old cargo version
- Must use `cargo vendor` and compress with xz
- Must limit `cargo build -j` to 1 or 2
- Must include all copyright info for vendored crates in DESCRIPTION
- Avoid relying on github.com for downloads (CRAN considers it unreliable long-term)

### Novel 4: Test Removal Between Versions
CRAN tracks test files between versions and rejects if tests are removed instead of fixed.
Verbatim: "removed the failing tests which is not the idea of tests."

### Novel 5: Dual Licensing Prohibition
A package cannot have different licenses for code and data within a single package. Must split into separate packages.
Verbatim: "A package can only be licensed as a whole."

### Novel 6: DOIs Treated as File URIs
DOIs in Rd man pages (like 10.1177/0146621613475471) can be flagged as invalid file URIs rather than recognized as references.

### Novel 7: Version Component Size Warning
Using development version conventions like 0.0.0.9000 triggers "Version contains large components" NOTE on CRAN submission.

### Novel 8: R 4.4.0 NULL Semantics Change
NULL is no longer atomic. `NCOL(NULL)` returns 0 instead of 1. Packages relying on old behavior will break.

### Novel 9: Vignette Engine Bootstrap Problem
New vignette engines aren't recognized during check if the package isn't installed yet, causing false-positive NOTE on some platforms.

---

## R 4.4.0 Impact (Released April 2024)

Key changes affecting CRAN packages:
1. **NULL no longer atomic** -- `is.atomic(NULL)` returns FALSE; `NCOL(NULL)` returns 0
2. **New `%||%` operator** in base R -- packages can drop rlang dependency for this
3. **Complex number parsing improved** -- `as.complex("1i")` now works (was NA)
4. **New `check_package_urls()` and `check_package_dois()`** -- tools for validating URLs/DOIs in package sources
5. **Stricter memory access checking** -- found large number of memory bugs in CRAN packages

---

## Submission Statistics (from llrs.dev analysis, Jan 2024)

- **65% of new packages pass on first try**
- **14.5% of all submission attempts are rejected**
- After rejection: 21.9% need 1 resubmission, 8.2% need 2, 4.9% need 3+
- **65.4% of first-published packages are eventually archived**
- Only 6.8% of all new packages are fully archived by study end
- Experienced maintainers also face submission difficulties

---

## Archival Statistics (from CRANhaven)

- 39% of all packages ever on CRAN (9,089 of 23,058) have been archived at some point
- 36% of archived packages eventually return (median 33 days)
- Among resubmitted packages, 95% eventually accepted
- 48.7% of archived packages never attempt resubmission
- Primary archival causes:
  1. Issues not fixed in time
  2. Unclear/mixed circumstances
  3. Dependencies on other archived packages
  4. CRAN policy violations
  5. Maintainer email delivery failures

---

## Recommendations for Knowledge Base Updates

### New Rules to Add

1. **DEPS-NEW: Cascading Archival Risk**
   - Monitor dependency health; have fallback for archived deps
   - Moving archived dep to Suggests may not be sufficient
   - Detection: Check if any Imports/Depends/LinkingTo packages are archived

2. **DOCS-NEW: Lost Braces in Rd Files**
   - `\itemize` with `{item}{description}` should be `\describe`
   - `\value` section doesn't need explicit `\describe` around `\item`
   - Detection: Parse Rd files for brace patterns in itemize/value

3. **CODE-NEW: Test Removal Detection**
   - Never remove failing tests; fix or skip with explanation
   - CRAN compares test files between versions
   - Detection: Compare test file list with previous version

4. **LIC-NEW: No Dual Licensing Within Package**
   - Cannot license code and data separately in one package
   - Must split into code package + data package
   - Detection: Check LICENSE file for multiple license sections

5. **RUST-01 through RUST-06: Rust-Specific Rules**
   - Report rustc version before compilation
   - Test with old cargo (2+ years)
   - Use cargo vendor + xz compression
   - Limit cargo build -j to 1-2
   - Include vendored crate copyright in DESCRIPTION
   - Don't rely on github.com for downloads

6. **DESC-NEW: Version Component Size**
   - Avoid large version components (9000+) in CRAN submissions
   - Use proper release version numbering
   - Detection: Check if any version component > 999

7. **DESC-NEW: DOIs as File URIs**
   - DOIs in Rd files can be misinterpreted as file URIs
   - Use proper `\doi{}` markup in Rd files
   - Detection: Scan Rd files for bare DOI strings

8. **CODE-NEW: R 4.4.0 NULL Changes**
   - Check for `is.atomic(NULL)`, `NCOL(NULL)` assumptions
   - Detection: Grep for these patterns in package code

### Rules to Update

1. **SIZE rules**: Note that Rust packages may get 5MB exception with proper documentation
2. **URL rules**: Add 301 redirect detection (CRAN flags redirects as issues)
3. **COMPILED rules**: Add gcc14 awareness, ASAN/UBSAN dependency failures
4. **EXAMPLE rules**: Note data.table threading can trigger CPU time ratio NOTE

---

## Sources

- R-package-devel mailing list Q1 2024: https://stat.ethz.ch/pipermail/r-package-devel/2024q1/
- R-package-devel mailing list Q2 2024: https://stat.ethz.ch/pipermail/r-package-devel/2024q2/
- mail-archive.com R-package-devel: https://www.mail-archive.com/r-package-devel@r-project.org/
- CRAN Cookbook - Code Issues: https://contributor.r-project.org/cran-cookbook/code_issues.html
- CRAN Cookbook - DESCRIPTION Issues: https://contributor.r-project.org/cran-cookbook/description_issues.html
- CRAN Cookbook - General Issues: https://contributor.r-project.org/cran-cookbook/general_issues.html
- CRAN Submission Checklist: https://cran.r-project.org/web/packages/submission_checklist.html
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
- Using Rust in CRAN Packages: https://cran.r-project.org/web/packages/using_rust.html
- llrs.dev CRAN first-try analysis (Jan 2024): https://llrs.dev/post/2024/01/10/submission-cran-first-try/
- Epiverse-TRACE licensing blog: https://epiverse-trace.github.io/posts/data-licensing-cran.html
- R 4.4.0 changes: https://www.r-bloggers.com/2024/04/whats-new-in-r-4-4-0/
- CRANhaven archival stats: https://www.cranhaven.org/cran-archiving-stats.html
- R-bloggers archival tale: https://www.r-bloggers.com/2024/09/tales-from-open-source-development-i-your-package-is-archived/
- dotwhisker archival: https://github.com/fsolt/dotwhisker/issues/115
- Is CRAN Holding R Back?: https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/

---

## Open Questions

1. **How does CRAN handle gcc14 transition?** Will there be a grace period for packages with new warnings?
2. **What is CRAN's exact policy on Suggests dependencies that are archived?** Moving to Suggests didn't save survivalSL.
3. **Is there a formal list of "acceptable large packages"?** The 5MB limit seems to have exceptions for Rust/C++ packages but this isn't documented clearly.
4. **How does CRAN track test removal?** The mechanism for detecting removed tests between versions isn't publicly documented.
5. **What is the notification policy for archival?** Some maintainers report receiving no warning, while the process supposedly includes a deadline email.
