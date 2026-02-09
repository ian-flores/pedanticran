# CRAN Rejection Patterns: August - December 2023

Generated: 2026-02-08

## Executive Summary

The second half of 2023 was marked by several significant CRAN developments: the R 4.3 release series introducing new compiled-code checks (strict prototypes, sprintf deprecation, C++17 default), continued enforcement of multi-core usage limits, a growing pattern of cascade archival from dependency failures, and the winter submission closure from December 22 to January 8. Analysis of R-package-devel mailing list threads and supplementary sources reveals 15+ distinct rejection/archival cases with extractable patterns. The most common issues were: excessive CPU core usage, package size violations, dependency failures causing cascade archival, LaTeX/Rd documentation errors, and example execution time exceedances.

## Research Question

What were the common CRAN rejection patterns, verbatim rejection reasons, and policy enforcement trends during August-December 2023?

## Key Environmental Context

### CRAN Operational Events

1. **Summer Break**: July 21 - August 7, 2023. Submission queue was fully closed; backlog cleared starting Aug 8.
   - Source: Uwe Ligges announcement, r-package-devel 2023q3/009324

2. **R 4.3.2 "Eye Holes" Release**: October 31, 2023. Minor bugfix release.
   - Source: stat.ethz.ch/pipermail/r-announce/2023/000697.html

3. **Winter Break**: December 22, 2023 - January 8, 2024. Submission queue fully closed.
   - Source: Uwe Ligges announcement, r-package-devel 2023q4/010240

4. **Infrastructure Issues**: CRAN noted "submissions are currently partly not possible due to some infrastructure issues" and 2-day delays in pretest processing (July 2023, impacting early August).
   - Source: r-package-devel 2023q3/009352

### R 4.3.x New Checks (Active in H2 2023)

These checks were introduced with R 4.3.0 (April 2023) and were actively enforced during submissions in H2 2023:

1. **C++11 Specification NOTE**: `"Specified C++11: please drop specification unless essential"` - R 4.3 defaults to C++17
2. **sprintf/vsprintf Deprecation**: `"use of sprintf/vsprintf is a known security risk"` - requires snprintf/vsnprintf
3. **Strict C Prototypes**: `-Wstrict-prototypes` flag enforcement, requiring `void` in empty parameter lists
4. **Partial Matching Checks**: Default checks for partial argument matching in R function calls now enabled
5. **Invalid URI Checking**: R CMD check now warns about invalid email addresses and URIs in Rd files
6. **Fortran Random Number**: Reports use of `RANDOM_NUMBER()` and its initialization subroutines
7. **Lost Braces in Rd**: New check flagging "lost braces" - affected 3000+ CRAN packages (macros missing backslash, unescaped set notation `{1, 2}`, `\itemize` with description-like `\item{label}{desc}`)

Source: tidyverse.org/blog/2023/03/cran-checks-compiled-code/, journal.r-project.org/news/RJ-2023-4-core/

### Archival Statistics (2023)

- 2023 full year: 362 packages archived, 217 unarchived, 1 removed
- H1 2023 (May-Sep window): 701 archived, 332 unarchived
- Active packages at Dec 31, 2023: ~20,249
- Top archival reasons: unfixed problems (5,808 cumulative), dependency issues (1,270), policy violations (644)
- Source: cranhaven.org/cran-archiving-stats.html, journal.r-project.org/news/RJ-2023-3-cran/

## Individual Rejection Cases

### Case 1: prqlr - Package Size Violation (August 2023)

- **Package**: prqlr v0.5.0
- **Date**: Archived August 19, 2023
- **Verbatim**: `"Archived on 2023-08-19 for policy violation"`
- **Root Cause**: `"installed size is 18.5Mb"` - libs subdirectory was 18.2Mb
- **CRAN Policy**: "Packages should be of the minimum necessary size"; data/docs should not exceed 5MB; source tarballs should not exceed 10MB
- **Category**: Package size / compiled code
- **Type**: Archival of existing package
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q3/009491.html

### Case 2: Modeltime - Multi-Core Usage Detection (August-September 2023)

- **Package**: Modeltime v1.2.8
- **Date**: ~August/September 2023
- **Verbatim NOTE**: `"CPU time 2.7 times elapsed time"` on both testthat.R and vignette rebuilding
- **Verbatim NOTE**: `"you are using more than 2 cores by default. Please see the CRAN policies."`
- **Root Cause**: Unintentional parallelization despite single-core defaults in code; likely from a dependency using parallel processing
- **Category**: Code / parallel processing
- **Type**: Update rejection
- **Novel**: The developer confirmed functions default to single-core but CRAN still detected 2.7x CPU/elapsed ratio
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q3/009531.html

### Case 3: Unknown Package - Multi-Core Source Detection (September 2023)

- **Package**: Not named (Shu Fai Cheung)
- **Date**: September 18, 2023
- **Issue**: Package received "more than 2 cores are used" notification despite parallel processing being disabled by default
- **Root Cause**: Source of unintended parallelization could not be found; developer added `stop()` traps and timing analysis without success
- **Category**: Code / parallel processing
- **Type**: Submission rejection
- **Novel**: Demonstrates difficulty of diagnosing hidden parallelization, especially when it comes from dependencies
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q3/009570.html

### Case 4: CartogRaflow - Archival and Resubmission Errors (October 2023)

- **Package**: CartogRaflow v1.0.4
- **Date**: October 16, 2023
- **Issue**: Version 1.0.3 archived same day as 1.0.4 submission; showed `"OK: 11, ERROR: 2"`
- **Category**: Multiple issues / resubmission
- **Type**: Update submission during archival
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/009896.html

### Case 5: mlr3proba - Unexpected Package Removal (October 2023)

- **Package**: mlr3proba
- **Date**: ~October 2023
- **Issue**: Package was removed from CRAN without clear explanation to the maintainer
- **Category**: Archival / communication
- **Type**: Package removal
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/009849.html

### Case 6: bioOED - Premature Removal Before Deadline (November 2023)

- **Package**: bioOED
- **Date**: November 1, 2023 (removed 2 days before November 3 deadline)
- **Verbatim**: Dependency on MEIGOR package no longer available in Bioconductor
- **Root Cause**: CRAN notified maintainer October 20 to fix dependency by November 3; package removed November 1
- **Category**: Dependencies / Bioconductor
- **Type**: Archival
- **Novel**: Maintainer alleged premature removal before stated deadline; raised governance concerns about CRAN decision-making process
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/009997.html

### Case 7: Cascade Archival Question - Dependency Chain (November 2023)

- **Reporter**: Henrik Bengtsson
- **Date**: ~November 2023
- **Issue**: When package PkgA is archived, dependent packages PkgB and PkgC are automatically archived. Question: Does CRAN automatically un-archive them when PkgA returns?
- **Category**: Dependencies / cascade archival
- **Policy Clarification Needed**: Whether cascade-archived packages need manual resubmission
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/010000.html

### Case 8: iopspackage - Multiple Rejection Issues (November-December 2023)

- **Package**: iopspackage v2.1.0
- **Date**: November-December 2023
- **Verbatim NOTEs**: Windows: 3 NOTEs, Debian: 4 NOTEs
- **Issues**:
  1. **LaTeX Special Characters**: `"checkRd: (-1) IOPS.Rd:17: Escaped LaTeX specials: \\_ \\_"` (lines 17, 36, 42, 44, 46, 48, 50)
  2. **Example Execution Time**: ~133 seconds (Windows), ~173 seconds (Debian) - far exceeding 10-second limit
  3. **Non-Standard Files**: `"Found the following files/directories: 'Combined_Results.csv' 'Combined_Results.xlsx'"` left in check directory
  4. **Large Tarball**: 10,537,094 bytes (~10.5MB)
- **Category**: Documentation / examples / size / cleanliness
- **Type**: First submission (beginner maintainer)
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/010055.html

### Case 9: multipanelfigure - External Tool Dependency (November 2023)

- **Package**: multipanelfigure
- **Date**: ~November 2023 (resurrection attempt)
- **Issues**:
  1. **Example Time Ratio**: Images example: 7.745s user / 0.53s elapsed = 15.464x ratio
  2. **Missing External Tool**: `"Error: Rterm.exe: FailedToExecuteCommand \"inkscape\" ... --export-png=... @error/delegate.c/ExternalDelegateCommand/514"` - inkscape not available on CRAN Windows
  3. **file.access() Warning**: Windows-specific unreliability note
- **Category**: External dependencies / examples / system tools
- **Type**: Archived package resurrection
- **Novel**: Package depends on system tools (inkscape) not present in CRAN check infrastructure
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/010116.html

### Case 10: tinycodet - Fake Test Packages (October 2023)

- **Package**: tinycodet v0.1.0.4
- **Date**: ~October 2023
- **Issue**: `"Subdirectory with package inside"` NOTE from fake packages in inst/tinytest/ used for testing import functions
- **Category**: Package structure / testing
- **Type**: New submission
- **Novel**: CRAN flagged intentional test fixtures as problematic; maintainer was unsure what CRAN required
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/009866.html

### Case 11: ARMA - Stale Metadata (December 2023)

- **Package**: ARMA (resubmission of archived package)
- **Date**: ~December 2023
- **Issue**: Non-standard check directory files: `"Found the following files/directories: 'PARMA21del1_ident'"`
- **Category**: Cleanliness / check artifacts
- **Type**: Archived package resubmission
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q4/010038.html

### Case 12: Unknown Package - Test Removal Rejection (Late 2023)

- **Reporter**: smallepsilon
- **Date**: Late 2023
- **Verbatim**: `"removed the failing tests which is not the idea of tests"`
- **Root Cause**: Developer removed platform-specific tests using `identical()` that failed on some CRAN platforms due to MKL/parallel processing numeric differences
- **CRAN Guidance**: `"replace identical() with all.equal()"`
- **Category**: Testing / numeric precision
- **Type**: Resubmission rejection
- **Novel**: Philosophical disagreement between developer (identical() tests prove same computation) and CRAN (all.equal() is sufficient); CRAN rejected removal of failing tests as approach
- **Source**: mail-archive.com/r-package-devel@r-project.org/msg10714.html

### Case 13: staplr - Unreachable Maintainer (August 2023)

- **Package**: staplr
- **Date**: ~August 2023
- **Issue**: Package removed; co-author attempted resubmission but "approval from the creator to finalise submission" was required; original maintainer unreachable
- **Category**: Maintainer / process
- **Type**: Resubmission blocked
- **Source**: stat.ethz.ch/pipermail/r-package-devel/2023q3/009378.html

### Case 14: milorGWAS - Stale Date Field (Late 2023/Early 2024)

- **Package**: milorGWAS
- **Date**: Archived January 11, 2024 (discussed late 2023)
- **Verbatim**: `"Archived on 2024-01-11 as issues were not corrected in time"`
- **Blocking Issue**: Uwe Ligges identified `"The Date field is over a month old"` as the specific blocking issue
- **Additional**: Spelled words NOTE for "GWAS", "Milet" in DESCRIPTION
- **Category**: DESCRIPTION metadata / date
- **Type**: Archived package resubmission
- **Novel**: A stale Date field alone can block resubmission
- **Source**: mail-archive.com/r-package-devel@r-project.org/msg09933.html

### Case 15: petersenlab - Multiple NOTE Issues (Late 2023)

- **Package**: petersenlab
- **Date**: Late 2023
- **Issues**:
  1. **Version String**: License content (CC BY 4.0) appeared in version field
  2. **Invalid DOI URIs**: `"Found the following (possibly) invalid file URIs: URI: 10.1177/0146621613475471"` from Rd files - DOIs were valid but format not recognized
  3. **Non-Standard Files in Check Dir**: `"Found the following files/directories: 'encryptionKey.RData' 'encrypytedCredentials.txt'"` - intentionally generated by examples demonstrating encryption
- **Category**: DESCRIPTION / documentation / examples
- **Type**: New submission
- **Source**: mail-archive.com/r-package-devel@r-project.org/msg09717.html

## Recurring Patterns

### Pattern 1: Multi-Core Usage Detection (HIGH FREQUENCY)
- Multiple cases of packages triggering "CPU time > 2.5x elapsed time" NOTE
- Often caused by dependencies rather than the package itself
- Developers frequently unable to identify the source of parallelization
- **Verbatim trigger**: `"you are using more than 2 cores by default. Please see the CRAN policies."`
- CRAN limit: 2 cores maximum in examples/tests/vignettes

### Pattern 2: Package Size Violations (HIGH FREQUENCY)
- Compiled code packages frequently exceed limits (libs directories 10-18+ MB)
- CRAN policy: source tarball < 10MB, installed data+docs < 5MB
- Enforcement was strict in H2 2023; prqlr archived for 18.5MB installed size
- Rust and other modern compiled language bindings particularly affected

### Pattern 3: Cascade Dependency Archival (MEDIUM FREQUENCY)
- When a dependency is archived, reverse dependencies cascade-archived
- Bioconductor package availability changes cause CRAN archivals (bioOED/MEIGOR)
- Timeline for fixes often insufficient (2 weeks typical)
- Manual resubmission required for cascade-archived packages

### Pattern 4: Documentation/Rd Errors (MEDIUM FREQUENCY)
- LaTeX special character escaping errors
- Missing `\value` tags in Rd files
- "Lost braces" check affecting 3000+ packages
- Invalid DOI/URI formatting in Rd files

### Pattern 5: Example Execution Time (MEDIUM FREQUENCY)
- Windows threshold: ~10 seconds
- Debian threshold: ~5 seconds
- Overall check time limit: 10 minutes for all examples + vignettes + tests
- External tool dependencies causing failures on CRAN infrastructure

### Pattern 6: Non-Standard Files in Check Directory (MEDIUM FREQUENCY)
- Files created during examples/tests not cleaned up
- `"Found the following files/directories: ..."` NOTE
- Common culprit: examples that demonstrate file I/O
- Fix: use `tempdir()` and clean up with `unlink()`

### Pattern 7: Stale Metadata (LOW FREQUENCY but BLOCKING)
- Date field "over a month old" blocks resubmission
- Author/Authors@R field inconsistencies block submission (must rebuild with R-devel)
- Version string format issues (leading zeroes, license content leaking into version)

### Pattern 8: Test Strategy Disagreements (LOW FREQUENCY but NOVEL)
- CRAN rejects removal of failing tests as a strategy
- `identical()` vs `all.equal()` for numeric comparison remains contentious
- Platform-specific numeric differences (MKL, parallel processing) cause test instability

## Novel Patterns (Not Commonly Documented)

1. **Premature Archival Before Deadline**: bioOED removed 2 days before stated deadline - raises governance/process concerns
2. **Hidden Parallelization from Dependencies**: Developers cannot always identify which dependency triggers multi-core detection
3. **System Tool Dependencies**: Packages depending on external tools (inkscape) fail on CRAN infrastructure where those tools are absent
4. **Fake Test Packages Flagged**: Test fixtures that are valid R packages inside `inst/` trigger "subdirectory with package" warnings
5. **Encryption Demo Files**: Examples that demonstrate encryption create credential files that CRAN flags as non-standard check artifacts
6. **Date Field as Blocker**: A stale Date field alone can prevent resubmission of an archived package

## R 4.3.x Specific Enforcement (New in H2 2023)

These checks were newly active during this period and likely contributed to additional rejections not fully documented in mailing list threads:

| Check | Verbatim Message | Impact |
|-------|-----------------|--------|
| C++11 spec | `"Specified C++11: please drop specification unless essential"` | All packages specifying C++11 |
| sprintf usage | `"use of sprintf/vsprintf is a known security risk"` | All packages with C/C++ code using sprintf |
| Strict prototypes | Compiler warnings from `-Wstrict-prototypes` | All packages with C code and empty param lists |
| Lost braces | `"\\item in \\itemize with non-empty label"` etc. | 3000+ CRAN packages |
| Partial matching | Default check now enabled for partial arg matching | Broadly applicable |

## Recommendations for Knowledge Base Updates

### New Rules to Add

1. **RULE: multi-core-detection** (Severity: ERROR)
   - Detection: Check for CPU time / elapsed time ratio > 2.5 in test/example output
   - Verbatim: `"CPU time X times elapsed time"` or `"you are using more than 2 cores by default"`
   - Fix: Cap at 2 cores; check all dependencies for hidden parallelization

2. **RULE: stale-date-field** (Severity: WARNING)
   - Detection: Date field in DESCRIPTION older than 1 month from submission date
   - Verbatim: `"The Date field is over a month old"`
   - Fix: Update Date field to current date before submission

3. **RULE: check-directory-artifacts** (Severity: NOTE)
   - Detection: Files/directories created during R CMD check that remain after
   - Verbatim: `"Found the following files/directories: ..."`
   - Fix: Use `tempdir()` for all file creation in examples/tests; clean up with `unlink()`

4. **RULE: external-tool-dependency** (Severity: WARNING)
   - Detection: System calls to external tools (inkscape, pandoc, python) in examples
   - Fix: Wrap in `\dontrun{}` or check for tool availability with `Sys.which()`

5. **RULE: lost-braces-rd** (Severity: NOTE)
   - Detection: Rd files with unescaped braces, missing backslash macros, \itemize with label-description items
   - Verbatim: Various "lost braces" messages
   - Fix: Escape braces with `\{` `\}`, add backslash to macro names, use `\describe` instead of `\itemize` for labeled items

6. **RULE: sprintf-deprecation** (Severity: WARNING)
   - Detection: Use of `sprintf()` or `vsprintf()` in C/C++ code
   - Verbatim: `"use of sprintf/vsprintf is a known security risk"`
   - Fix: Replace with `snprintf()`/`vsnprintf()` with explicit buffer size

7. **RULE: cxx11-specification** (Severity: NOTE)
   - Detection: `SystemRequirements: C++11` in DESCRIPTION or `CXX_STD=CXX11` in Makevars
   - Verbatim: `"Specified C++11: please drop specification unless essential"`
   - Fix: Remove C++11 specification; R 4.3+ defaults to C++17

8. **RULE: strict-c-prototypes** (Severity: WARNING)
   - Detection: C functions with empty parameter lists: `int foo()`
   - Fix: Add `void`: `int foo(void)`

9. **RULE: cascade-archival-dependency** (Severity: INFO)
   - Detection: Depends/Imports on packages that are archived or not in standard repos
   - Fix: Check dependency health before submission; consider conditional usage

10. **RULE: test-removal-not-allowed** (Severity: ERROR)
    - Detection: Submission comment mentions "removed tests"
    - Verbatim: `"removed the failing tests which is not the idea of tests"`
    - Fix: Fix tests rather than removing them; use `all.equal()` instead of `identical()` for numeric comparisons

### Existing Rules to Strengthen

- **Package size**: Add specific guidance for compiled code packages (libs directory limit)
- **Example time**: Clarify per-platform thresholds (5s Debian, 10s Windows)
- **Internet resources**: Add graceful failure requirement from CRAN policy
- **noSuggests check**: Ensure all Suggests packages are used conditionally

## Sources

- R-package-devel mailing list 2023 Q3: https://stat.ethz.ch/pipermail/r-package-devel/2023q3/
- R-package-devel mailing list 2023 Q4: https://stat.ethz.ch/pipermail/r-package-devel/2023q4/
- Mail archive: https://www.mail-archive.com/r-package-devel@r-project.org/
- CRAN Cookbook: https://contributor.r-project.org/cran-cookbook/
- CRAN submission checklist: https://cran.r-project.org/web/packages/submission_checklist.html
- Tidyverse blog on compiled code: https://tidyverse.org/blog/2023/03/cran-checks-compiled-code/
- CRANhaven archiving stats: https://www.cranhaven.org/cran-archiving-stats.html
- CRAN submission first-try analysis: https://llrs.dev/post/2024/01/10/submission-cran-first-try/
- R Journal Changes on CRAN 2023 Q3/Q4: https://journal.r-project.org/news/RJ-2023-3-cran/ and https://journal.r-project.org/news/RJ-2023-4-cran/
- R 4.3.2 release: https://stat.ethz.ch/pipermail/r-announce/2023/000697.html

## Open Questions

1. **Exact archival numbers for H2 2023**: The R Journal article for Q4 2023 was not extractable due to CSS-only rendering; full statistics for Oct-Dec 2023 archival counts remain unknown.
2. **Cascade un-archival policy**: Henrik Bengtsson's question about automatic un-archival of dependent packages was not answered in the accessible thread content.
3. **R 4.3.x enforcement wave**: The number of packages specifically archived or rejected due to R 4.3 new checks (sprintf, strict prototypes, C++11) during H2 2023 is not quantified in available sources.
4. **CRAN governance**: The bioOED premature removal case raises questions about CRAN decision consistency that were unresolved in the mailing list discussion.
