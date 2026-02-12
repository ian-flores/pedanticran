# CRAN Policy Evolution 2015-2022

Generated: 2026-02-11

## Executive Summary

The period from 2015 to 2022 represents CRAN's transformation from a relatively informal package repository into a highly automated, strictly enforced quality gate for the R ecosystem. CRAN grew from roughly 6,200 packages (April 2015) to over 18,700 (end of 2022), forcing a shift from manual review to automated submission pipelines. Key milestones include: the introduction of native routine registration enforcement (R 3.4, 2017), staged installation (R 3.5-3.6, 2018-2019), the `stringsAsFactors = FALSE` breaking change (R 4.0, 2020), the native pipe and LazyData sanity checks (R 4.1, 2021), and HTML5 validation with implicit function declaration enforcement (R 4.2, 2022). Throughout this period, the CRAN Repository Policy document itself was revised approximately 30 times, progressively tightening requirements around secure downloads, API compliance, compilation standards, and package size. The automation of incoming checks (both Linux and Windows) starting in 2017-2018 was the single most consequential infrastructure change, enabling CRAN to scale while simultaneously raising the bar for acceptance.

---

## 1. CRAN Repository Policy Document Revisions

Source: [eddelbuettel/crp](https://github.com/eddelbuettel/crp) -- tracking CRAN Repository Policy SVN revisions.

The HTML archive of the crp repository contains 61 policy snapshots spanning SVN revisions r2908 (December 2011) through r6286 (August 2024). For the 2015-2022 period, the following revisions are documented:

### Timeline of Revisions (2015-2022)

| Approx. Date | SVN Revision | Key Content Changes |
|--------------|-------------|-------------------|
| 2014-2015 | r3231-r3415 | Multiple revisions through 2015. Policy established core requirements: 5MB data/documentation limit, `R CMD check --as-cran` requirement, 1-2 month update frequency, two-platform rule, secure download requirement (`https` or `ftps`). |
| ~2015 | r3553 | Strengthened language around `.Internal()` and undocumented entry point restrictions. Added explicit prohibition on disabling compiler diagnostics. |
| ~2015-2016 | r3577-r3715 | Tightened requirements on external software downloads at install time. Clarified that packages should first check for system libraries before bundling or downloading. Added language about fixed-version downloads. |
| ~2016-2017 | r3747-r3874 | Added requirements around `Authors@R` field with contributor (`ctb`) and copyright holder (`cph`) roles. Strengthened citation format requirements (author-year style with DOI/ISBN). Added CRAN submission checklist. |
| ~2017-2018 | r3923-r4050 | Policy updates reflecting the new automated submission system. Added language about packages not downloading/checking out sources at build time. Clarified that pre-compiled binary downloads require explicit CRAN team agreement. |
| ~2018-2019 | r4168-r4292 | Multiple rapid revisions. Strengthened secure download language. Added Additional_repositories field requirement for non-CRAN/Bioconductor suggested packages. Clarified SystemRequirements field usage. |
| Oct 27, 2020 | r4333 | Policy revision with updates to network connectivity and download requirements. |
| Oct 28, 2020 | r4334 | Follow-up revision, minor corrections. |
| Oct 29, 2020 | r4336 | Additional minor corrections/clarifications. |
| Apr 23, 2021 | r4540 | Policy updates. URL checking requirements strengthened. |
| Apr 25, 2021 | r4548 | Follow-up corrections. |
| Sep 25, 2021 | r4769 | Policy revision; further tightening of requirements. |
| Feb 8, 2022 | r5027 | Updated policy text. Likely includes language around HTML5 validation and stricter compilation requirements. |
| May 3, 2022 | r5236 | Further updates to policy text. |
| Jul 25, 2022 | r5316 | Policy revision. |
| Jul 26, 2022 | r5321 | Follow-up revision, minor updates. |

### Key Observation

Unlike the 2023-2025 period where the policy document changed relatively little in substance, the 2015-2022 period saw significant textual evolution of the policy itself. Many rules that CRAN enforces today were codified during this era. However, as with the later period, **the real enforcement tightening came through R CMD check changes in R releases**, with the policy document often lagging behind what was already being enforced through automated checks.

---

## 2. R Version Changes Affecting CRAN Checks

### R 3.2.0 (April 2015)

Major new checks introduced:
- **URL accessibility checking**: R CMD check now checks the existence and accessibility of URLs in DESCRIPTION, CITATION, NEWS.Rd, README.md, and help files (provided the build has libcurl support). This was the foundation for CRAN's later strict URL enforcement.
- **Title/Description termination**: R CMD check checks that the Title and Description fields are correctly terminated.
- **S3 method reporting**: Reports (apparent) S3 methods exported but not registered, and reports overwriting registered S3 methods from base/recommended packages.
- **Non-ASCII detection**: Reports non-ASCII characters in R source files when there is no package encoding declared in DESCRIPTION.
- **`library()`/`require()` detection**: R CMD check notes uses of `library()` and `require()` in package code (these should use namespace imports instead).
- **New options**: `--run-dontrun` and `--run-donttest` options for running examples that would normally be skipped.
- **`--test-dir` option**: Allows specifying an alternative set of tests to run.
- **NeedsCompilation field**: R CMD build now adds a `NeedsCompilation` field if not already present.
- **Reproducible builds**: R CMD INSTALL gains `--built-timestamp=STAMP` for 100% reproducible package building.

Source: [R Journal: Changes in R 3.2.x](https://journal.r-project.org/news/RJ-2015-1-r-changes/)

### R 3.3.0 (May 2016)

Major new checks introduced:
- **DOI checking**: R CMD check `--as-cran` now checks DOIs in package CITATION and Rd files. This was the first time DOIs were validated during checks.
- **Code usage checking by default**: R CMD check now by default checks code usage (via `codetools`) with only the base package attached.
- **Undefined globals reporting**: Functions from default packages other than base which are used in package code but not imported are reported as undefined globals, with a suggested addition to the NAMESPACE file.
- **`--ignore-vignettes` option**: New option for use with non-Sweave vignettes whose VignetteBuilder package is not available.
- **`--RdMacros` option**: R CMD Rdconv and R CMD Rd2pdf each gain a new option for specifying Rd macros before processing.
- **Makefile GNU extension detection**: R CMD check checks for undeclared use of GNU extensions in Makefiles, and for Makefiles with a missing final linefeed.
- **`\donttest` dependency checking**: R CMD check checks that packages used in `\donttest` sections are specified in the DESCRIPTION file.

Source: [R 3.3.0 release](https://www.r-bloggers.com/2016/05/r-3-3-0-is-released/)

### R 3.4.0 (April 2017)

Major new checks introduced:
- **Native routine registration enforcement**: R CMD check now reports a NOTE when packages with compiled code do not register native routines via `R_registerRoutines` and `R_useDynamicSymbols`. This NOTE was expected to become a WARNING. A new helper function `tools::package_native_routine_registration_skeleton()` was provided to auto-generate registration code. **This was one of the most impactful changes of the era, affecting thousands of packages with compiled code.**
- **`\Sexpr{}` evaluation**: R CMD check evaluates `\Sexpr{}` expressions in Rd files before checking contents, detecting issues in both evaluation and expanded output.
- **Vignette rebuilding**: R CMD check now tries re-building all vignettes rather than stopping at the first error, adding bookmarks to logs. Each vignette is rebuilt in a separate process by default.
- **Duplicated vignette titles**: Checks for duplicated vignette titles (used as hyperlinks on CRAN package pages).
- **Data directory checks**: More comprehensive checks on the `data` directory and the functioning of `data()` in a package.
- **Autoconf verification**: Checks that `autoconf`-generated `configure` files have their corresponding source files, with optional regeneration via `autoreconf`.
- **Line ending checks**: Verifies line endings for `.hpp` files and `inst/include` contents; non-empty files must terminate with newlines.
- **JIT compilation**: R 3.4.0 JIT-compiles all packages by default, which could surface previously hidden issues.

Source: [Dirk Eddelbuettel: Easy Package Registration](http://dirk.eddelbuettel.com/blog/2017/03/29/), [Registration of Entry Points](https://thecoatlessprofessor.com/programming/r/registration-of-entry-points-in-compiled-code-loaded-into-r/)

### R 3.5.0 (April 2018)

Major changes:
- **ALTREP framework**: New framework for alternate representations of basic R objects. Experimental, but would later have significant implications for packages using internal R structures.
- **Staged installation preparation**: Groundwork laid for staged installation (fully enabled in R 3.6.0).
- **Check timeouts**: It is now possible to set timeouts (elapsed-time limits) for most parts of R CMD check via environment variables.
- **OpenMP macro checks**: Optionally checks makefiles for correct and portable use of `SHLIB_OPENMP_*FLAGS` macros.
- **Byte-compilation universally**: All packages are now byte-compiled on installation.
- **Serialization format v3**: New serialization format supporting ALTREP objects. Packages needed to be re-installed under this version.
- **Fortran file handling**: `.f` extension now denotes fixed-form Fortran 90+ rather than FORTRAN 77. Files with `.f90`/`.f95` extensions are linked using C/C++ compiler rather than Fortran 9x compiler.

Source: [R 3.5.0 release](https://www.r-statistics.com/2018/04/r-3-5-0-is-released-major-release-with-many-new-features/), [R Blog: Staged Install](https://blog.r-project.org/2019/02/14/staged-install/)

### R 3.6.0 (April 2019)

Major new checks introduced:
- **Staged installation enabled by default**: Package installation is now "staged" -- installed to a temporary location and moved to the final location when successfully completed. R checks for hard-coded paths that include the temporary installation directory and fails the installation if found. Packages can opt out via `StagedInstall: no` in DESCRIPTION, but CRAN discourages this.
- **Temp directory cleanup check**: New option mitigates checks leaving files/directories in `/tmp`; included in `--as-cran`.
- **OpenMP macro enforcement**: Makefiles now checked for correct and portable `SHLIB_OPENMP_*FLAGS` macro usage.
- **CRLF line ending correction**: R CMD check checks for and R CMD build corrects CRLF line endings in shell scripts `configure` and `cleanup` (even on Windows).

Source: [R 3.6.0 release](https://stat.ethz.ch/pipermail/r-announce/2019/000641.html)

### R 4.0.0 (April 2020)

Major changes:
- **`stringsAsFactors = FALSE` default**: The single most breaking change of this era. `data.frame()` and `read.table()` no longer convert strings to factors by default. **This broke a large number of CRAN packages** that relied on the previous behavior, triggering widespread updates.
- **Matrix class inheritance**: Matrices now inherit from "array" class. Code incorrectly assuming `class(matrix_obj)` has length one would fail.
- **Bashism detection**: R CMD check optionally checks `configure` and `cleanup` scripts for non-Bourne-shell code ("bashisms").
- **`\donttest` examples run by default**: R CMD check `--as-cran` now runs `\donttest` examples instead of instructing the tester to do so. This was a significant enforcement tightening -- code previously hidden in `\donttest` blocks was now being exercised.
- **PCRE2 migration**: PCRE2 is now required (or PCRE1 >= 8.32). Hyphen characters in regex character classes must be escaped. This affected packages with regex patterns.
- **Raw string literals**: New syntax `r"(...)"` for strings containing backslashes and quotes.

Source: [R 4.0.0 release](https://stat.ethz.ch/pipermail/r-announce/2020/000653.html), [R Blog: stringsAsFactors](https://developer.r-project.org/Blog/public/2020/02/16/stringsasfactors/index.html)

### R 4.1.0 (May 2021)

Major new checks introduced:
- **LazyData sanity checks**: R CMD check performs sanity checks on LazyData usage, including reporting when `LazyData: true` is specified without a `data` directory, and checking compression specifications. R CMD build removes LazyData fields from packages lacking data directories.
- **Bogus return statement detection**: R CMD check scans for bogus return statements (activated via `_R_CHECK_BOGUS_RETURN_`, enabled for `--as-cran`).
- **Non-existing S4 export warnings**: Warns when packages export non-existing S4 classes or methods.
- **Tarball size threshold**: The checking of tarball sizes in R CMD check `--as-cran` can now be adjusted using `_R_CHECK_CRAN_INCOMING_TARBALL_THRESHOLD_`.
- **Native pipe operator**: The `|>` native pipe introduced (language feature, not check-related, but influenced package coding style).
- **C++ standard default**: Default C++ standard shifted to C++14 where available. Packages specifying C++11 continue using that version.
- **Link-Time Optimization (LTO)**: Expanded LTO support for recommended packages. New `--use-LTO` and `--no-use-LTO` flags. Packages can opt in/out via `UseLTO` field in DESCRIPTION.
- **Build artifact exclusion**: R CMD build now excludes tarballs and binaries from previous builds in the top-level directory.

Source: [R 4.1.0 release](https://stat.ethz.ch/pipermail/r-announce/2021/000670.html)

### R 4.2.0 (April 2022)

Major new checks introduced:
- **Implicit function declaration enforcement**: `_R_CHECK_SRC_MINUS_W_IMPLICIT_` now defaults to true, reflecting Apple clang's treatment of implicit function declarations as compilation errors. This was a significant change for packages with C code.
- **HTML5 Rd validation**: R CMD check can optionally (but included in `--as-cran`) validate the HTML produced from `.Rd` files using HTML Tidy.
- **`\Sexpr` error reporting**: Rd file name and line numbers now included in error messages for `\Sexpr` evaluation failures.
- **Vignette-only dependency checks**: R CMD check now selectively applies dependency checks to examples, tests, and vignettes via `_R_CHECK_DEPENDS_ONLY_`.
- **Valgrind for vignettes**: R CMD check `--use-valgrind` also uses valgrind when re-building vignettes.
- **Byte-compilation error reporting**: R CMD check now reports byte-compilation errors during installation.
- **32-bit Windows dropped**: Windows support is now 64-bit only. Rtools42 (64-bit gcc 10.3) required. UCRT (Universal C Runtime) mandatory.
- **USE_FC_LEN_T becoming default**: Fortran BLAS/LAPACK prototypes transitioning to new calling convention.
- **`\doi` Rd macro optimization**: Packages using only the `\doi` Rd macro (without other dynamic content) now produce smaller tarballs and build considerably faster.

Source: [R 4.2.0 release](https://stat.ethz.ch/pipermail/r-announce/2022/000683.html), [R NEWS](https://cran.r-project.org/bin/windows/base/old/4.2.0/NEWS.R-4.2.0.html)

---

## 3. CRAN Infrastructure Changes

### Automated Submission System (2017-2018)

The most consequential infrastructure change of this era was the introduction and expansion of the automated submission pipeline.

**Before automation (~2015-2016):**
- All submissions reviewed manually by CRAN volunteers (~3 people)
- Submission via the web form at `CRAN.R-project.org/submit.html` or FTP upload
- Limited scalability; growing backlog as package count increased
- At UseR! 2016 in Stanford, the CRAN team asked for help with processing submissions, and several community members volunteered

**Automation rollout (2017-2018):**
- The automated submission system ("auto-check") was introduced, performing incoming checks under both Linux and Windows
- Auto-check either accepts, rejects, or routes to manual inspection
- By June 2018, CRAN received 2,122 package submissions in one month, with 3,571 actions: 2,433 (68.1%) auto-processed and 1,138 (31.9%) manual
- The system initially had false positives leading to wrong rejections; these were progressively reduced
- First-time submissions always went to manual inspection
- The CRAN team announced they could "no longer respond to individual help requests or engage in lengthy discussions for exceptions" (November 2017, when ~70 submissions arrived per day)
- The r-package-devel mailing list became the designated channel for submission help

Source: [R Journal: Changes on CRAN (2018)](https://rjournal.github.io/news/RJ-2018-1-cran/), [R Journal: Changes on CRAN (2017)](https://rjournal.github.io/news/RJ-2017-2-cran/)

### CRAN Submission Checklist (2017-2019)

A formal [Checklist for CRAN submissions](https://cran.r-project.org/web/packages/submission_checklist.html) was published around 2017, providing structured guidance for package authors. It was updated in 2019 to emphasize:
- Making descriptions informative and avoiding redundancies
- Writing function names with parentheses as in `foo()` without quotes
- Running `R CMD check --as-cran` with current R-devel
- Ensuring clean check results before submission

### Check Flavors Growth

CRAN's check infrastructure expanded significantly during this period:

**2015-2016:** Primarily Linux and Windows flavors with r-devel and r-release.

**2017-2018:** Addition of corruption-of-constants checks (rcnst), expansion of sanitizer testing (ASAN/UBSAN), and PROTECT/UNPROTECT analysis (rchk). Brian Ripley contributed Fedora-based additional checks including ATLAS, MKL, OpenBLAS alternatives for linear algebra testing.

**2019-2022:** Further expansion to include:
- LTO (Link-Time Optimization) type mismatch detection
- noLD (no long double) testing
- noOMP (no OpenMP) testing
- M1mac (Apple Silicon ARM64) -- added as Apple transitioned to ARM
- musl (Alpine Linux) testing
- noSuggests (testing without suggested packages)
- rlibro (read-only library installation)
- donttest (running `\donttest` examples)

Source: [CRAN Package Check Issue Kinds](https://cran.r-project.org/web/checks/check_issue_kinds.html), [Debugging CRAN Additional Checks](https://reside-ic.github.io/blog/debugging-and-fixing-crans-additional-checks-errors/)

### CRAN Mirror Security (2019)

In 2019, there was significant attention to CRAN mirror security. As of December 2019, there were 97 official CRAN mirrors, with 67 (69%) providing both secure downloads via HTTPS and using secure mirroring from the CRAN master server. CRAN progressively encouraged and then required HTTPS for mirrors.

Source: [CRAN Mirror Security (R-bloggers)](https://www.r-bloggers.com/2019/03/cran-mirror-security/)

---

## 4. CRAN Package Ecosystem Growth

### Package Counts by Year

| Year | Approximate Active Packages | Notable Milestone |
|------|---------------------------|-------------------|
| 2015 | ~6,200 (Apr) to ~7,000 (Aug) | Milestone: 7,000 packages on CRAN (August 2015) |
| 2016 | ~8,000+ (Apr) to ~9,500 (Dec) | Rapid growth from Tidyverse ecosystem |
| 2017 | ~10,000 (Jan) to ~12,000 (Dec) | **Milestone: 10,000 packages** (January 2017) |
| 2018 | ~12,500 to ~13,500 | ~21 new/updated submissions per day average |
| 2019 | ~15,227 (Dec) | **Milestone: 15,000 packages** |
| 2020 | ~16,000+ (Nov) | Growth continued despite pandemic |
| 2021 | ~18,650 (Dec) | Approaching 20,000 |
| 2022 | ~18,785 (Dec) | Growth rate beginning to plateau |

Source: [CRAN 10,000 milestone](https://blog.revolutionanalytics.com/2017/01/cran-10000.html), [7,000 milestone](https://www.r-bloggers.com/2015/08/milestone-7000-packages-on-cran/), R Journal "Changes on CRAN" articles

### Submission Volume Growth

| Period | Submissions | Auto-Processed | Manual |
|--------|-----------|----------------|--------|
| Nov 2017 | ~2,087/month | N/A (system being introduced) | Mostly manual |
| Jun 2018 | 2,122/month | 2,433 actions (68.1%) | 1,138 actions (31.9%) |
| Jul-Dec 2021 | 12,256 (6 months) | 14,232 actions (66%) | 7,390 actions (34%) |

This tripling of package count (from ~6,200 in 2015 to ~18,785 in 2022) while maintaining quality standards explains why automated enforcement became essential.

---

## 5. Major Policy and Enforcement Themes

### Theme 1: Native Routine Registration (2017)

**The change**: R 3.4.0 introduced R CMD check NOTEs for packages with compiled code that did not register native routines via `R_registerRoutines()` and `R_useDynamicSymbols()`.

**Impact**: At the time, fewer than 10% of CRAN packages with compiled code registered their routines. The new check affected thousands of packages.

**Migration path**: `tools::package_native_routine_registration_skeleton()` was provided as an auto-generation tool. The community mobilized quickly -- Dirk Eddelbuettel published guides and Rcpp was updated to auto-generate registration.

**Enforcement trajectory**: NOTE in R 3.4.0 (2017) --> progressively stricter enforcement, eventually expected to become WARNING.

### Theme 2: Secure Downloads and URL Validation (2015-2020)

**2015**: R 3.2.0 introduced URL accessibility checking in DESCRIPTION, CITATION, NEWS.Rd, README.md, and help files.

**2016**: R 3.3.0 added DOI validation in CITATION and Rd files.

**~2017-2019**: CRAN policy required "secure download mechanisms (e.g., 'https' or 'ftps')" for package installation downloads.

**2020**: R-devel introduced stricter URL checks. CRAN does not tolerate permanent redirections for URLs (though DOI redirects are expected). The `urlchecker` package was created to help authors pre-validate URLs.

**2023**: Policy removed `ftps` as acceptable, leaving only `https`.

### Theme 3: stringsAsFactors Breaking Change (2020)

**The change**: R 4.0.0 made `stringsAsFactors = FALSE` the default in `data.frame()` and `read.table()`, reversing 20+ years of R behavior.

**Impact**: This was decided at R Core meetings in Toulouse in 2019. A large number of packages relied on the previous behavior and needed updating. It was arguably the single most disruptive language-level change in R history, but the community had long advocated for it.

**CRAN's role**: CRAN did not treat this as a special case -- packages that broke under the new default needed to be fixed or faced archival.

### Theme 4: Staged Installation (2018-2019)

**R 3.5.0 (2018)**: Groundwork laid. Source package installation could be staged (installed to a temporary location, then moved to final destination on success).

**R 3.6.0 (2019)**: Staged installation became the default. R checks for hard-coded paths referencing the temporary installation directory and fails if found. Packages could opt out via `StagedInstall: no` in DESCRIPTION, but this was discouraged.

**Impact**: Caught packages with install-time side effects, hard-coded paths, and other non-portable behaviors that had previously gone undetected.

### Theme 5: LazyData Enforcement (2021)

**The change**: R 4.1.0 introduced sanity checks for LazyData. Packages specifying `LazyData: true` without a `data/` directory received NOTEs. R CMD build began removing unnecessary LazyData fields.

**Impact**: Many package templates (including early `usethis` defaults) included `LazyData: true` regardless of whether the package had data. This was a moderate-impact cleanup affecting many packages.

### Theme 6: Compiled Code Standards (2017-2022)

A progressive tightening arc:

| Year | R Version | Change |
|------|----------|--------|
| 2017 | R 3.4.0 | Native routine registration NOTEs |
| 2018 | R 3.5.0 | Byte-compilation universal; ALTREP framework |
| 2019 | R 3.6.0 | OpenMP macro portability checks |
| 2020 | R 4.0.0 | Bashism detection in configure/cleanup scripts |
| 2021 | R 4.1.0 | LTO support expansion; C++14 default |
| 2022 | R 4.2.0 | Implicit function declarations enforced; 32-bit Windows dropped; USE_FC_LEN_T transition |

### Theme 7: API Compliance and .Internal Restrictions

The CRAN policy has long stated: "CRAN packages should use only the public API." This includes prohibitions on:
- `.Internal()` calls
- `.Call()` to base packages
- `:::` access to internal functions in base packages
- Using undocumented entry points

During 2015-2022, this was enforced primarily through policy review rather than automated checks. The automated non-API entry point checking that would become prominent in R 4.3+ (2023) was being developed during this period, with the `tools:::nonAPI` list growing from 259 entries (R 3.3.3) to progressively more entries through R 4.2.

### Theme 8: Compiler Diagnostics Policy

The CRAN policy states: "Packages should not attempt to disable compiler diagnostics, nor to remove other diagnostic information such as symbols in shared objects." This was codified during the 2015-2017 period and reflected CRAN's philosophy that compiler warnings should be addressed, not suppressed.

---

## 6. Year-by-Year Summary

### 2015

**R versions**: 3.2.0 (April), 3.2.1 (June), 3.2.2 (August), 3.2.3 (December)
**CRAN scale**: ~6,200 to ~7,000 packages
**Key developments**:
- URL accessibility checking introduced (R 3.2.0) -- foundation for later strict enforcement
- Title/Description validation added
- S3 method export/registration checking begun
- CRAN policy ~r3298-r3553: core rules well-established, beginning to tighten
- FTP upload still accepted as submission method alongside web form
- All submissions manually reviewed

### 2016

**R versions**: 3.3.0 (May), 3.3.1 (June), 3.3.2 (October), 3.3.3 (March 2017)
**CRAN scale**: ~8,000 to ~9,500 packages
**Key developments**:
- DOI checking in CITATION and Rd files (R 3.3.0) -- first automated reference validation
- Code usage checking strengthened with `codetools` integration
- Namespace import enforcement: functions from non-base packages must be properly imported
- GNU extension detection in Makefiles
- `\donttest` dependency checking added
- CRAN team at UseR! 2016 requested volunteer help with growing submission load
- CRAN policy ~r3670-r3760: Authors@R field preferred, citation format requirements added

### 2017

**R versions**: 3.4.0 (April), 3.4.1 (June), 3.4.2 (September), 3.4.3 (November)
**CRAN scale**: ~10,000 to ~12,000 packages (10,000 milestone in January)
**Key developments**:
- **Native routine registration enforcement** (R 3.4.0) -- the era's most impactful change for compiled packages
- Vignette rebuilding improvements (separate processes, continue after errors)
- Autoconf source verification
- Data directory comprehensive checks
- Automated submission system introduced; ~70 submissions/day by November
- CRAN team can no longer respond to individual help requests
- CRAN Submission Checklist published
- CRAN policy ~r3838-r3953: automated submission requirements formalized

### 2018

**R versions**: 3.5.0 (April), 3.5.1 (July), 3.5.2 (December)
**CRAN scale**: ~12,500 to ~13,500 packages
**Key developments**:
- ALTREP framework introduced (R 3.5.0) -- would later impact data.table and other performance packages
- Byte-compilation universal for all packages
- Check timeouts configurable
- OpenMP macro portability checks
- Serialization format v3
- Automated submission system fully operational: 68.1% auto-processed (June 2018)
- ORCID support added to DESCRIPTION files (person() comment field)
- CRAN policy ~r4040-r4168: pre-compiled binary download restrictions codified

### 2019

**R versions**: 3.6.0 (April), 3.6.1 (July), 3.6.2 (December)
**CRAN scale**: ~15,227 packages (December)
**Key developments**:
- **Staged installation** default (R 3.6.0) -- caught hard-coded paths and install-time side effects
- Temp directory cleanup checking (`--as-cran`)
- CRLF line ending detection and correction
- CRAN mirror security push: 67 of 97 mirrors using HTTPS
- R-hub blog published guide on keeping up with CRAN policies
- CRAN Submission Checklist updated with description quality guidance
- CRAN policy ~r4197-r4292: secure download language strengthened

### 2020

**R versions**: 4.0.0 (April), 4.0.1 (June), 4.0.2 (June), 4.0.3 (October), 4.0.4 (February 2021)
**CRAN scale**: ~16,000+ packages
**Key developments**:
- **`stringsAsFactors = FALSE` default** (R 4.0.0) -- the biggest breaking change, affecting many packages
- Matrix class now inherits from "array"
- Bashism detection in configure/cleanup scripts
- `\donttest` examples now run by `--as-cran` -- code previously hidden was now tested
- PCRE2 required, breaking some regex patterns
- URL checking significantly strengthened in R-devel (late 2020)
- CRAN policy r4333-r4336 (October): multiple rapid revisions updating network/download requirements

### 2021

**R versions**: 4.1.0 (May), 4.1.1 (August), 4.1.2 (November)
**CRAN scale**: ~18,650 packages (December)
**Key developments**:
- **LazyData sanity checks** (R 4.1.0) -- flagged unnecessary LazyData declarations
- Bogus return statement detection
- Non-existing S4 export warnings
- Tarball size threshold configurable
- Native pipe `|>` introduced
- C++14 default; LTO expansion
- Jul-Dec: 12,256 submissions, 66% auto-processed, 34% manual
- CRAN policy r4540-r4769: URL checking requirements strengthened

### 2022

**R versions**: 4.2.0 (April), 4.2.1 (June), 4.2.2 (October), 4.2.3 (March 2023)
**CRAN scale**: ~18,785 packages (December)
**Key developments**:
- **Implicit function declaration enforcement** (R 4.2.0) -- Apple clang made these errors, R CMD check followed
- HTML5 Rd validation in `--as-cran`
- 32-bit Windows support dropped entirely (Rtools42, 64-bit only)
- UTF-8 standard on Windows
- USE_FC_LEN_T Fortran calling convention transition
- Valgrind extended to vignette rebuilding
- CRAN policy r5027-r5321: four revisions, reflecting HTML5 and compilation requirements
- R Consortium Repositories Working Group established
- Community discussions about CRAN scalability and alternative repositories begin

---

## 7. Enforcement Trend Analysis

### Enforcement Trajectory: Warnings to Errors

A recurring pattern throughout 2015-2022 is the **gradual escalation** of enforcement:

1. **Feature introduced as optional check** (often controlled by environment variable)
2. **Enabled under `--as-cran`** (package authors who test with `--as-cran` see it)
3. **Reported as NOTE** (informational, doesn't block submission)
4. **Upgraded to WARNING** (blocks CRAN submission)
5. **Upgraded to ERROR** (blocks package building entirely)

Examples of this pattern:
- Native routine registration: NOTE (R 3.4, 2017) --> increasingly enforced
- URL checking: optional (R 3.2, 2015) --> DOI checking added (R 3.3, 2016) --> strict (R 4.0+, 2020)
- LazyData: unmentioned --> NOTE for unnecessary declaration (R 4.1, 2021)
- Implicit function declarations: warning (pre-2022) --> error via Apple clang (R 4.2, 2022)
- Non-API entry points: policy only (pre-2023) --> NOTE (R 4.3, 2023) --> WARNING (R 4.5, 2025)

### Categories That Got Stricter (2015-2022)

1. **Compiled Code Standards** (MOST SIGNIFICANT)
   - 2017: Native routine registration enforcement
   - 2018: Byte-compilation universal, ALTREP
   - 2019: OpenMP macro checks
   - 2020: Bashism detection
   - 2021: LTO expansion, C++14 default
   - 2022: Implicit function declarations, 32-bit dropped, USE_FC_LEN_T

2. **URL and Reference Validation**
   - 2015: Basic URL accessibility checking
   - 2016: DOI validation in CITATION/Rd
   - 2019-2020: Strict URL checking, no permanent redirections
   - Ongoing: HTTPS-only enforcement

3. **Package Installation Reliability**
   - 2018: Staged installation preparation
   - 2019: Staged installation default, temp directory cleanup
   - 2020: `\donttest` examples now tested by `--as-cran`

4. **Namespace and Import Hygiene**
   - 2016: Code usage checking with codetools by default
   - 2017: Undefined globals from non-base packages flagged
   - Ongoing: Progressively stricter import requirements

5. **Metadata Quality**
   - 2015: Title/Description termination
   - 2016-2017: Authors@R preferred with proper roles, DOI/ISBN citation format
   - 2018: ORCID support
   - 2021: LazyData sanity checks

### Categories That Remained Relatively Stable

- **Package naming**: No significant changes (name uniqueness long-established).
- **License requirements**: Fundamental requirement unchanged; license database maintained.
- **Size limits**: 5MB data/documentation limit stable throughout; 10MB tarball guideline formalized later.
- **Update frequency**: "No more than every 1-2 months" unchanged.
- **Two-platform rule**: Unchanged since pre-2015.

---

## 8. Implications for pedanticran

### Rules with Historical Roots in This Period

Many of the rules that pedanticran enforces have their origins in 2015-2022 policy changes:

1. **Native routine registration** (CODE rules): Introduced R 3.4.0 (2017). Any package with compiled code must register routines.

2. **URL validation** (DOC rules): Foundation laid R 3.2.0 (2015), DOI checking R 3.3.0 (2016). All URLs must be accessible, use HTTPS, and not have permanent redirections.

3. **Namespace imports** (CODE rules): Enforced from R 3.3.0 (2016). Functions from non-base packages must be imported via NAMESPACE, not accessed via `library()` or `require()`.

4. **LazyData without data directory** (DESC rules): Check introduced R 4.1.0 (2021). Simple but common issue.

5. **Authors@R field** (DESC rules): Preferred since ~2016-2017 policy revisions. Should include proper roles (aut, cre, ctb, cph).

6. **DOI/ISBN citation format** (DESC rules): Required since ~2016-2017. Must be in author-year style with proper markup.

7. **Staged installation compatibility** (CODE rules): Default since R 3.6.0 (2019). Packages must not hard-code installation paths.

8. **Compiler diagnostics** (CODE rules): Policy codified ~2015-2017. Packages must not suppress warnings with pragmas.

9. **`\donttest` must work** (DOC rules): Enforced by `--as-cran` since R 4.0.0 (2020).

10. **Implicit function declarations** (CODE rules): Enforced since R 4.2.0 (2022).

### Historical Context for Severity Levels

Understanding when rules were introduced helps calibrate pedanticran's severity:
- Rules from 2015-2017 (URL checking, namespace imports, routine registration) are **well-established** -- packages violating these have had 8+ years to comply. **Error severity**.
- Rules from 2018-2020 (staged install, `\donttest` enforcement, bashism detection) are **mature** -- 5+ years old. **Warning to Error severity**.
- Rules from 2021-2022 (LazyData, HTML5 validation, implicit declarations) are **recent but stable** -- 3+ years. **Warning severity**.

---

## Sources

- [CRAN Repository Policy](https://cran.r-project.org/web/packages/policies.html)
- [eddelbuettel/crp - Policy revision tracking](https://github.com/eddelbuettel/crp)
- [History for texi - eddelbuettel/crp](https://github.com/eddelbuettel/crp/commits/master/texi)
- [R 3.2.0 Changes in R](https://journal.r-project.org/news/RJ-2015-1-r-changes/)
- [R 3.3.0 release](https://www.r-bloggers.com/2016/05/r-3-3-0-is-released/)
- [R 3.4.0 release](https://www.r-statistics.com/2017/04/r-3-4-0-is-released-with-new-speed-upgrades-and-bug-fixes/)
- [R 3.5.0 release](https://www.r-statistics.com/2018/04/r-3-5-0-is-released-major-release-with-many-new-features/)
- [R 3.6.0 release](https://stat.ethz.ch/pipermail/r-announce/2019/000641.html)
- [R 4.0.0 release](https://stat.ethz.ch/pipermail/r-announce/2020/000653.html)
- [R 4.1.0 release](https://stat.ethz.ch/pipermail/r-announce/2021/000670.html)
- [R 4.2.0 release](https://stat.ethz.ch/pipermail/r-announce/2022/000683.html)
- [R NEWS (R 3.x)](https://cran.r-project.org/doc/manuals/r-release/NEWS.3.html)
- [R Journal: Changes on CRAN (2017)](https://rjournal.github.io/news/RJ-2017-2-cran/)
- [R Journal: Changes on CRAN (2018)](https://rjournal.github.io/news/RJ-2018-1-cran/)
- [R Journal: Changes on CRAN (2019)](https://journal.r-project.org/news/RJ-2019-2-cran/)
- [R Journal: Changes on CRAN (2021)](https://rjournal.github.io/news/RJ-2021-2-cran/)
- [Dirk Eddelbuettel: Easy Package Registration](http://dirk.eddelbuettel.com/blog/2017/03/29/)
- [Registration of Entry Points in Compiled Code](https://thecoatlessprofessor.com/programming/r/registration-of-entry-points-in-compiled-code-loaded-into-r/)
- [R Blog: stringsAsFactors](https://developer.r-project.org/Blog/public/2020/02/16/stringsasfactors/index.html)
- [R Blog: Staged Install](https://blog.r-project.org/2019/02/14/staged-install/)
- [R-hub: URL checks](https://blog.r-hub.io/2020/12/01/url-checks/)
- [R-hub: Keep up with CRAN policies](https://blog.r-hub.io/2019/05/29/keep-up-with-cran/)
- [CRAN 10,000 milestone](https://blog.revolutionanalytics.com/2017/01/cran-10000.html)
- [CRAN 7,000 milestone](https://www.r-bloggers.com/2015/08/milestone-7000-packages-on-cran/)
- [CRAN Mirror Security](https://www.r-bloggers.com/2019/03/cran-mirror-security/)
- [CRAN Package Check Issue Kinds](https://cran.r-project.org/web/checks/check_issue_kinds.html)
- [CRAN Submission Checklist](https://cran.r-project.org/web/packages/submission_checklist.html)
- [Debugging CRAN Additional Checks](https://reside-ic.github.io/blog/debugging-and-fixing-crans-additional-checks-errors/)
- [ORCID in R packages (rOpenSci)](https://ropensci.org/blog/2018/10/08/orcid/)
- [Size and Limitations of Packages on CRAN](https://thecoatlessprofessor.com/programming/r/size-and-limitations-of-packages-on-cran/)
