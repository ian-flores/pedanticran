# Research Report: CRAN Package Rejection Patterns — January through July 2025

Generated: 2026-02-08

## Executive Summary

The first half of 2025 was marked by three major disruptions to the CRAN ecosystem: (1) the `acs` package archival cascade in February that triggered widespread community debate about CRAN's governance model, (2) the R 4.5.0 release in April introducing C23 as the default compilation standard and `-DR_NO_REMAP` for C++ code, creating breaking changes for packages with compiled code, and (3) an escalating enforcement of non-API entry point restrictions that threatens major packages like `data.table`. Rejection patterns continued to center on DESCRIPTION formatting, file-writing policies, test/example timing, and URL validity, but new compiler-related failures became a significant category post-April.

## Research Question

What were the CRAN package rejection patterns from January through July 2025? What verbatim rejection reasons were sent by CRAN reviewers? What novel patterns emerged?

---

## 1. Major Events (January-July 2025)

### 1.1 The acs/choroplethr Archival Cascade (February 2025)

**What happened:** The `acs` package was archived because R CMD check produced a NOTE about two bash scripts (`cleanup` and `configure`) in its home directory not being portable. The maintainer chose not to fix the issues.

**Cascade impact:**
- `acs` archived -> triggered automatic archival of:
  - `choroplethr` (11 years on CRAN, 289K total downloads)
  - `noaastormevents`
  - `synthACS`
- Combined 2024 downloads of cascaded packages: 43,037

**Resolution:** Choroplethr v4.0.0 returned to CRAN in April 2025 after maintenance was transferred to Zhaochen He, who removed the `acs` dependency and migrated to `tidycensus`.

**Source:** [Choroplethr is Scheduled to be Archived from CRAN](https://arilamstein.com/blog/2025/02/02/choroplethr-is-scheduled-to-be-archived-from-cran/)

### 1.2 "Is CRAN Holding R Back?" Controversy (February 12, 2025)

Ari Lamstein published a widely-discussed blog post identifying three CRAN restrictions he argued limit R's ecosystem:

1. **Release frequency constraints**: CRAN mandates "no more than every 1-2 months" for updates; Lamstein wanted weekly releases
2. **Forced package fragmentation**: CRAN required splitting `choroplethr` into separate packages (`choroplethrMaps`, `choroplethrAdmin1`, `zctaCrosswalk`), making cross-package updates difficult
3. **Vignette size limitations**: Restrictions on documentation size forced removal of long-form guides

**Source:** [Is CRAN Holding R Back?](https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/)

### 1.3 R 4.5.0 Release (April 11, 2025)

R 4.5.0 ("How About a Twenty-Six") introduced major breaking changes:

- **C23 as default compilation standard**: A C23 compiler is now selected by default. GCC 13-15, LLVM clang 18-20, Apple clang 15-17 all use C23.
- **C23 keywords**: `bool`, `true`, `false` are now keywords in C23, conflicting with packages using these as identifiers
- **USE_C17 escape hatch**: Packages can opt out by adding `USE_C17` to `SystemRequirements` or installing with `R CMD INSTALL --use-C17`
- **R_NO_REMAP for C++**: `R CMD INSTALL` (and hence `check`) now compiles C++ code with `-DR_NO_REMAP`
- **R_NO_REMAP_RMATH**: New ability to define `R_NO_REMAP_RMATH` and call `Rf_*()` functions
- **All packages must rebuild**: Every R package had to be rebuilt for 4.5.0

**Impact example:** The `spdep` package had to replace `COPY_TO_USER_STRING` with `Rf_mkChar` because `include/Rdefines.h` set `COPY_TO_USER_STRING` as `mkChar` which is not defined as `Rf_mkChar` when `R_NO_REMAP` is defined.

**Source:** [What's new in R 4.5.0?](https://www.r-bloggers.com/2025/04/whats-new-in-r-4-5-0/), [R 4.5.0 release announcement](https://stat.ethz.ch/pipermail/r-announce/2025/000710.html)

### 1.4 Non-API Entry Point Enforcement Escalation

R 4.5.2 (October 2025, but enforcement building throughout H1) escalated treatment of non-API calls:
- Some `R CMD check` NOTEs on non-API entry points **upgraded to WARNINGs**
- Declarations for flagged functions will be **removed from public header files** in near future
- Non-API entry point list grew from 259 (R-3.3.3) to 322 in development versions

**Affected functions include:** `SET_GROWABLE_BIT`, `SETLENGTH`, `SET_TRUELENGTH`, `LEVELS`, `STRING_PTR`, `IS_S4_OBJECT`, `SET_S4_OBJECT`, `UNSET_S4_OBJECT`, `SET_TYPEOF`, `NAMED`, `ATTRIB`, `SET_ATTRIB`, `findVar`

**Major packages affected:** `data.table`, `readr`, `vctrs` among others. 22% of CRAN packages use compiled code.

**Source:** [Use of non-API entry points in data.table](https://rdatatable-community.github.io/The-Raft/posts/2025-01-13-non-api-use/)

### 1.5 nprcgenekeepr: Archived 4 Days After Publication (July 2025)

**Package:** nprcgenekeepr v1.0.8
**Submitted:** July 25, 2025
**Published:** Shortly after submission
**Archived:** July 29, 2025 (4 days later)
**Reason given:** "Archived on 2025-07-29 as issues were not corrected in time"

The maintainer received publication confirmation but was then archived without additional notification. Ben Bolker identified a test failure in `print.summary.nprcgenekeeprErr.R`. Lluis Revilla noted this is a systemic issue: "~400 cases" of archival within 7 days of publication, with no follow-up communication to maintainers.

**Source:** [r-package-devel thread](https://www.mail-archive.com/r-package-devel@r-project.org/msg11263.html)

---

## 2. Individual Rejection Cases (with Verbatim Text)

### Case 1: Test Removal Rejection (May 2025)

**Package:** Not named
**Category:** Testing / Code quality
**Type:** Resubmission
**Verbatim CRAN message:**
> "removed the failing tests which is not the idea of tests."

**Context:** Developer used `identical()` to verify two code paths produced the same calculations, but multithreaded linear algebra (LAPACK/BLAS, MKL) produced non-deterministic results. Developer moved tests to local-only testing. CRAN rejected this approach.

**Advice from community:** Use `covr` to show test coverage increased despite removing specific tests. "Tests are code and thus may also contain bugs, and sometimes it's the right choice to remove the buggy code."

**Novel:** Yes - rejection with zero errors/warnings/notes reported. The human reviewer flagged a semantic concern about test philosophy.

**Source:** [r-package-devel msg10719](https://www.mail-archive.com/r-package-devel@r-project.org/msg10719.html)

### Case 2: Non-FOSS License + Missing Suggested Package (Early 2025)

**Package:** Not named (first submission)
**Category:** DESCRIPTION / Licensing / Dependencies
**Type:** First submission
**Verbatim CRAN messages:**
> "Non-FOSS package license (file LICENSE)"
> "Suggests or Enhances not in mainstream repositories: velocyto.R"
> "Found the following (possibly) invalid URLs"
> "Package suggested but not available for checking: 'velocyto.R'"

**Context:** Developer used CC BY-NC-ND 4.0 license (believed to be CRAN-approved). Tarball size: 9,076,436 bytes. URL issue was not using canonical CRAN form (`https://CRAN.R-project.org/package=pkgname`).

**Source:** [r-package-devel msg10005](https://www.mail-archive.com/r-package-devel@r-project.org/msg10005.html)

### Case 3: Mega2R False Positive Sanitizer Warning (July 2025)

**Package:** Mega2R v1.2.0
**Category:** Compiled code / Sanitizer checks
**Type:** Resubmission
**Verbatim CRAN message:**
> "package Mega2R_1.2.0.tar.gz does not pass the incoming checks automatically."

**Specific warning from gcc-san:**
> "runtime error: load of address 0x7faa31b1fa40 with insufficient space for an object of type 'struct MemPage *'"

**Context:** Warning originated in vendor SQLite code (sqlite3.c:80239), not the package's own code. An SQLite forum investigation concluded: "Because of the requirements to reproduce the issue, it looks like a compiler issue not a bug in SQLite." The warning appeared only on gcc-san and was not reproducible on clang-asan, clang-ubsan, or valgrind. No response to developer's rebuttal.

**Novel:** Yes - false positive from vendored dependency code in a specific compiler configuration.

**Source:** [r-package-devel msg10895](https://www.mail-archive.com/r-package-devel@r-project.org/msg10895.html)

### Case 4: HLSM Archived Package Resubmission (2025)

**Package:** HLSM
**Category:** Compiled code / UBSAN
**Type:** Resubmission (was archived 2024-01-19)
**Verbatim CRAN message:**
> "does not pass the incoming checks automatically"

**Specific error from clang-UBSAN:**
> "vendor/cigraph/src/constructors/adjacency.c:87:34: runtime error: nan is outside the range of representable values of type 'long'"

**Context:** Error in vendored igraph C code, plus 24 compilation warnings. Maintainer could not reproduce locally. The pattern of vendored dependency code causing sanitizer failures is recurring.

**Source:** [r-package-devel msg10698](https://www.mail-archive.com/r-package-devel@r-project.org/msg10698.html)

### Case 5: ironseed File-Writing False Positive (2025)

**Package:** ironseed
**Category:** Code / File system policy
**Type:** Submission
**Verbatim CRAN message:**
> "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies. Please omit any default path in writing functions. In your examples/vignettes/tests you can write to tempdir().
> -> tools/config.Rtools/config/configure.R"

**Context:** The referenced file `tools/config.Rtools/config/configure.R` didn't exist in the package. Developer suspected it was created during installation by the configure script. Uwe Ligges confirmed this was a **false positive** - the reviewer likely meant `tools/config/configure.R`, which was acceptable.

**Source:** [r-package-devel msg10861](https://www.mail-archive.com/r-package-devel@r-project.org/msg10861.html)

### Case 6: epiparameter Dual Licensing Rejection (January 2025)

**Package:** epiparameter
**Category:** Licensing
**Type:** Submission
**Verbatim CRAN message:**
> "A package can only be licensed as a whole. It can have a single license or a set of alternative licenes. If the data have to be licensed differently then the code, you have to provide the data in a separate data package with the other license."

**Context:** Developers attempted dual licensing: MIT for code and CC0 for data. LICENSE file stated: "All data included in the epiparameter R package is licensed under CC0...This includes the parameter database (extdata/parameters.json) and data in the data/ folder."

**Resolution:** Split into two packages: `epiparameter` (MIT, code) and `epiparameterDB` (CC0, data).

**Source:** [R-bloggers: Licensing R packages with code and data](https://www.r-bloggers.com/2025/01/licensing-r-packages-with-code-and-data-learnings-from-submitting-to-cran/)

### Case 7: Ecdat URL Redirect Chain (2025)

**Package:** Ecdat v0.4-6
**Category:** URLs / Documentation
**Type:** Update
**Verbatim CRAN message:**
> "Number of redirects hit maximum amount [www.cde.ca.gov]: Maximum (10) redirects followed"

**Context:** URL in Caschool.Rd documentation triggered excessive redirect chain on CRAN's URL checker. URL worked normally in browsers. Local `R CMD check --as-cran` did not reproduce the issue. Deadline: September 30, 2025.

**Source:** [r-package-devel msg10976](https://www.mail-archive.com/r-package-devel@r-project.org/msg10976.html)

### Case 8: geotopbricks Example Timing (2025)

**Package:** geotopbricks v1.5.9.1
**Category:** Examples / Performance
**Type:** Update
**Issue:** `get.geotop.inpts.keyword.value` example exceeded 5-second threshold on Debian Linux.
- Elapsed time: 5.326 seconds (user: 1.406s, system: 0.027s)
- Example loaded data from a URL outside `\donttest{}` blocks
- Windows checks passed; Debian flagged the NOTE

**Advice:** Wrap URL-based data loading in `\donttest{}` or include data within the package using `system.file()`.

**Source:** [r-package-devel msg10674](https://www.mail-archive.com/r-package-devel@r-project.org/msg10674.html)

### Case 9: geomander Premature Archival + Cascade (Late 2025)

**Package:** geomander
**Category:** Deadline enforcement / Dependency cascade
**Type:** Archived by Brian Ripley before self-imposed deadline

**Context:** Christopher Kenny's `geomander` was archived, triggering automatic archival of reverse dependencies. Uwe Ligges clarified the deadline had passed. Resubmission of archived packages now requires manual review, adding processing time.

**Debate:** Whether CRAN's "before [DATE]" means strictly before or on-or-before. Community leaned toward "strictly less than."

**Source:** [r-package-devel msg11188](https://www.mail-archive.com/r-package-devel@r-project.org/msg11188.html)

---

## 3. Recurring Patterns

### 3.1 DESCRIPTION Formatting (Perennial)
Verbatim messages CRAN sends:
- "Please always write package names, software names and API names in single quotes"
- "Please always explain all acronyms in the description text"
- "We do not need '+ file LICENSE' and the file as these are part of R"
- "The Title field should be in title case"
- "Author field differs from that derived from Authors@R"
- "Please add references with no space after 'doi:', 'https:' and angle brackets"

### 3.2 File-Writing Policy Violations (Perennial)
Verbatim:
> "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies."

Fix: Use `tempdir()` in examples/tests. Omit default paths in writing functions.

### 3.3 Code Quality Standards (Perennial)
Verbatim messages:
- "Please write TRUE and FALSE instead of T and F"
- "Please do not set a seed to a specific number within a function"
- "Write information messages suppressibly using message()/warning()/stop()"
- "Reset settings when exiting functions using on.exit()"
- "Don't modify global environment using <<- operator"
- "Limit parallel processing to 2 cores maximum in examples/tests/vignettes"

### 3.4 Documentation Requirements (Perennial)
Verbatim:
- "Please add \\value to .Rd files regarding exported methods"
- "\\dontrun{} should only be used if the example really cannot be executed"
- "Please replace \\dontrun with \\donttest"
- "Please unwrap the examples if they are executable in < 5 sec"
- "Overall checktime 20 min > 10 min"

### 3.5 Vendored Code Sanitizer Failures (Growing - 2025)
Multiple packages (Mega2R, HLSM) rejected for sanitizer warnings in **vendored dependency code** (SQLite, igraph), not their own code. Developers cannot reproduce locally. This is a growing friction point with no clear resolution path.

### 3.6 URL Validity Checks (Perennial but Intensifying)
Packages rejected for:
- URLs with excessive redirect chains
- URLs not in canonical CRAN form
- Non-functional URLs in documentation
- "301 Moved Permanently" requiring URL updates

---

## 4. Novel Patterns (2025-Specific)

### 4.1 C23 Compilation Breaking Changes
R 4.5.0 defaulting to C23 means:
- `bool`, `true`, `false` are now reserved keywords
- Packages using these as identifiers must add `USE_C17` to `SystemRequirements`
- Some packages ignore settings in configure scripts or sub-directory compilation

### 4.2 R_NO_REMAP Enforcement for C++
`R CMD INSTALL` now compiles C++ with `-DR_NO_REMAP`, requiring packages to use `Rf_*()` prefixed function names instead of unprefixed versions.

### 4.3 Non-API Entry Points Upgraded from NOTE to WARNING
Functions like `SET_GROWABLE_BIT`, `SETLENGTH`, `SET_TRUELENGTH` are now flagged more severely. Declarations will be removed from public headers. Major packages (`data.table`, `readr`, `vctrs`) affected.

### 4.4 Post-Publication Archival Without Notification
~400 packages archived within 7 days of publication, with no follow-up communication. Maintainers believe packages are published successfully, only to discover archival days later.

### 4.5 Dual Licensing Explicitly Forbidden
CRAN now explicitly states packages must have a single license. Code+data packages with different license needs must be split into separate packages.

### 4.6 100+ Newbie Submissions in 3 Days
Uwe Ligges reported receiving over 100 newbie submissions within three days, indicating growing demand for CRAN inclusion and increasing review burden.

---

## 5. Impact of R 4.5.0 Release on Submissions

### Immediate Impact (April 2025)
1. **All packages must rebuild** — Universal requirement, no exceptions
2. **C23 keyword conflicts** — Packages using `bool`, `true`, `false` as identifiers break immediately
3. **R_NO_REMAP breakage** — C++ packages using unprefixed R API functions (e.g., `mkChar` instead of `Rf_mkChar`) fail to compile
4. **Configure script portability** — Scripts ignoring `USE_C17` in their configure scripts don't get the opt-out

### CRAN Additional Checks Expanded to 28 Types
Post-R 4.5, CRAN runs these additional check categories:
- **Compiler variants:** ATLAS, BLAS, MKL, OpenBLAS, C23, Intel, LTO, gcc, gcc15
- **Sanitizers:** clang-ASAN, gcc-ASAN, clang-UBSAN, gcc-UBSAN, valgrind
- **Memory/safety:** 0len, rchk, rcnst
- **Configuration:** Strict, noLD, noOMP, noRemap, noSuggests, rlibro, donttest
- **Platform:** M1mac, musl

The `C23` and `noRemap` checks are particularly relevant to the R 4.5 transition.

---

## 6. CRAN Ecosystem Statistics

### Archival Statistics (All-Time)
- Total packages ever archived: 9,089 (39% of 23,058 total packages ever on CRAN)
- Packages that return: 36-38% of archived packages eventually return
- Median return time: ~33 days
- Mean return time: 128 days (for packages archived once)
- Packages archived 2+ times: 972
- Packages that never attempt to return: 48.7%
- Resubmission success rate: 95% of packages that resubmit are eventually accepted

### Rejection Statistics
- Overall rejection rate: 14.5% of attempts
- Average submissions per accepted version: ~2
- First-time submissions receive additional manual scrutiny in "newbies" queue
- CRAN team response time: within 10 working days (typical)

### New Packages (2025 H1, Partial Data)
- January 2025: 186 new packages
- June 2025: 123 new packages

---

## 7. Sources

### Mailing List Threads (R-package-devel)
- [Test removal rejection](https://www.mail-archive.com/r-package-devel@r-project.org/msg10719.html)
- [Non-FOSS license rejection](https://www.mail-archive.com/r-package-devel@r-project.org/msg10005.html)
- [Mega2R false positive](https://www.mail-archive.com/r-package-devel@r-project.org/msg10895.html)
- [HLSM UBSAN failure](https://www.mail-archive.com/r-package-devel@r-project.org/msg10698.html)
- [ironseed file-writing false positive](https://www.mail-archive.com/r-package-devel@r-project.org/msg10861.html)
- [Ecdat URL redirects](https://www.mail-archive.com/r-package-devel@r-project.org/msg10976.html)
- [geotopbricks example timing](https://www.mail-archive.com/r-package-devel@r-project.org/msg10674.html)
- [Resubmitting archived packages](https://www.mail-archive.com/r-package-devel@r-project.org/msg11188.html)
- [nprcgenekeepr post-publication archival](https://www.mail-archive.com/r-package-devel@r-project.org/msg11263.html)
- [CRAN submissions down / IP blocking](https://www.mail-archive.com/r-package-devel@r-project.org/msg11250.html)
- [Package title changes](https://www.mail-archive.com/r-package-devel@r-project.org/msg10796.html)

### Blog Posts and Articles
- [Is CRAN Holding R Back?](https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/) — Ari Lamstein, Feb 2025
- [Choroplethr is Scheduled to be Archived](https://arilamstein.com/blog/2025/02/02/choroplethr-is-scheduled-to-be-archived-from-cran/) — Ari Lamstein, Feb 2025
- [Choroplethr v4.0.0 is now on CRAN](https://arilamstein.com/blog/2025/04/14/choroplethr-v4-0-0-is-now-on-cran/) — Ari Lamstein, Apr 2025
- [Licensing R packages with code and data](https://www.r-bloggers.com/2025/01/licensing-r-packages-with-code-and-data-learnings-from-submitting-to-cran/) — epiparameter team, Jan 2025
- [Use of non-API entry points in data.table](https://rdatatable-community.github.io/The-Raft/posts/2025-01-13-non-api-use/) — Ivan Krylov, Jan 2025
- [What's new in R 4.5.0?](https://www.r-bloggers.com/2025/04/whats-new-in-r-4-5-0/) — Apr 2025

### Official Resources
- [CRAN Submission Checklist](https://cran.r-project.org/web/packages/submission_checklist.html)
- [CRAN Repository Policy](https://cran.r-project.org/web/packages/policies.html)
- [CRAN Package Check Issue Kinds](https://cran.r-project.org/web/checks/check_issue_kinds.html)
- [CRAN Cookbook](https://contributor.r-project.org/cran-cookbook/) — Community guide to common issues
- [CRANhaven Archiving Statistics](https://www.cranhaven.org/cran-archiving-stats.html)
- [eddelbuettel/crp](https://github.com/eddelbuettel/crp) — CRAN Repository Policy change tracker

---

## 8. Recommendations for Knowledge Base Updates

### New Rules to Add

1. **RULE: C23 keyword conflicts** (R 4.5+)
   - Severity: ERROR
   - Detection: Check for `bool`, `true`, `false` used as identifiers in C code
   - Fix: Add `USE_C17` to `SystemRequirements` or rename identifiers

2. **RULE: R_NO_REMAP compliance** (R 4.5+)
   - Severity: ERROR
   - Detection: Check C++ code for unprefixed R API calls (`mkChar`, `allocVector`, etc.)
   - Fix: Use `Rf_mkChar`, `Rf_allocVector`, etc.

3. **RULE: Non-API entry points** (escalating)
   - Severity: WARNING (was NOTE)
   - Detection: Check for `SET_GROWABLE_BIT`, `SETLENGTH`, `SET_TRUELENGTH`, `STRING_PTR`, `NAMED`, etc.
   - Fix: Use ALTREP framework or official API alternatives

4. **RULE: Dual licensing forbidden**
   - Severity: ERROR
   - Verbatim: "A package can only be licensed as a whole"
   - Fix: Split code and data into separate packages with different licenses

5. **RULE: Test removal philosophy**
   - Severity: ERROR (human review)
   - Verbatim: "removed the failing tests which is not the idea of tests"
   - Fix: Fix tests rather than remove them; if removing, show increased coverage via `covr`

6. **RULE: Post-publication check compliance**
   - Severity: WARNING
   - Note: Packages can be archived within days of publication if check failures exist
   - Fix: Verify ALL check flavors pass, not just local checks

### Existing Rules to Update

7. **UPDATE: URL validation** — Add "Number of redirects hit maximum amount" as verbatim text; note that browser-functional URLs may fail CRAN's checker

8. **UPDATE: Configure/cleanup portability** — The `acs` archival shows this NOTE can lead to cascading package losses; escalate severity

9. **UPDATE: Package size** — Still 5MB limit; recommend separate data packages for data-heavy submissions

10. **UPDATE: Submission frequency** — Add note about 100+ newbie submissions in 3-day bursts; expect 10+ working day review times

## 9. Open Questions

1. How many packages were specifically archived due to R 4.5.0 C23/R_NO_REMAP changes? The exact count is not available from public sources.
2. What is the complete list of CRAN Repository Policy changes in 2025? The `eddelbuettel/crp` tracker shows commits through August 2024 on the first page; 2025 changes may exist on later pages.
3. What is the full monthly breakdown of new packages accepted in 2025 H1? Only January (186) and June (123) figures were found.
4. How does CRAN plan to handle the non-API entry point transition for major packages like `data.table` that require API alternatives not yet available?
