# CRAN Rejection Patterns: July-December 2024

Research Report
Generated: 2026-02-08

---

## Executive Summary

The second half of 2024 saw two significant CRAN Repository Policy revisions (rev6277 in August, rev6286 in August), continued enforcement of internet access policies leading to package archivals, and an increase in Rust/compiled code requirements causing friction. The mailing list showed recurring themes around: internet resource handling, temporary file management, clang sanitizer failures, Windows build infrastructure issues, timing constraints, and DESCRIPTION formatting. The period also saw the emergence of CRANhaven as a community response to archival waves, and the "CRAN doomsday clock" illustrating cascading dependency archival risks.

---

## 1. CRAN Policy Revisions (August 2024)

### Rev 6277 (August 20, 2024) -- NEW: Rate Limiting for External Resources

**Added text (verbatim):**
> "Use of external resources such as websites must be kept to a minimum. In particular, 'rate limit' errors for websites (such as HTTP codes 429 and 403) must be avoided (and do bear in mind that other packages may be using the same resource)."

- **Source**: https://github.com/eddelbuettel/crp (commit d064f66)
- **Category**: Internet Access / External Resources
- **Impact**: Novel policy. Packages that heavily query external APIs now have an explicit rate-limit avoidance obligation. Notably, CRAN warns that *other packages* may share the same resource, raising the bar for shared API endpoints.
- **Recommendation**: Add as new knowledge base rule. Packages must implement rate limiting and respect HTTP 429/403 responses.

### Rev 6286 (August 27, 2024) -- NEW: Package Names Are Persistent

**Added text (verbatim):**
> "Package names on CRAN are persistent and in general it is not permitted to change a package's name."

- **Source**: https://github.com/eddelbuettel/crp (commit 0c151d6)
- **Category**: DESCRIPTION / Package Identity
- **Impact**: Codifies existing practice. Package renaming was already rare, but this makes it explicit policy.
- **Recommendation**: Add as informational note to knowledge base.

---

## 2. Individual Rejection/Archival Cases

### Case 1: CopernicusMarine -- Archived for Internet Access

- **Package**: CopernicusMarine
- **Date**: Archived December 16, 2024
- **Reason (verbatim)**: "Archived on 2024-12-16 from policy violation. On Internet Access."
- **Category**: Internet Access
- **Details**: Maintainer discovered archival "by accident" -- was not aware the package had been archived. Posted to R-package-devel on December 21, 2024 asking how to identify the specific policy violation.
- **Resolution**: Archival notice found in CRAN PACKAGES.in file; detailed failure logs at Oxford statistics server.
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10380.html
- **Novel**: Illustrates that maintainers may not receive or notice archival notifications.

### Case 2: timeless -- Archived for Rust Compiler Reporting

- **Package**: timeless
- **Date**: Archived September 11, 2024 (deadline was September 6, 2024)
- **Reason (verbatim)**: "Please report the version of rustc used (as R does for C, C++ and Fortran compilers) in the installation log especially if compilation fails, so best reported before starting compilation (as R does)."
- **Category**: Compiled Code / Rust
- **Details**: CRAN required Rust compiler version to be reported in installation logs *before* compilation begins. Maintainer attempted fix by adding `SystemRequirements: Cargo (Rust's package manager), rustc (>= 1.67.1)` to DESCRIPTION -- this was insufficient. The actual requirement was log output from the configure script.
- **Archival text**: "Archived on 2024-09-11 for policy violations."
- **Source**: https://www.r-bloggers.com/2024/09/tales-from-open-source-development-i-your-package-is-archived/
- **Novel**: Specific Rust-related archival; highlights that DESCRIPTION field alone doesn't satisfy the logging requirement.

### Case 3: oaqc / graphlayouts / ggraph -- Cascading Dependency Archival

- **Package**: oaqc (primary), graphlayouts and ggraph (affected)
- **Date**: October 2024 (deadline October 7, 2024)
- **Reason**: oaqc archived due to invalid maintainer email address
- **CRAN text (verbatim)**: "Please see the problems shown on https://cran.r-project.org/web/checks/check_results_graphlayouts.html. Please correct before 2024-10-07 to safely retain your package on CRAN."
- **Secondary issue**: "Packages in Suggests should be used conditionally" and testing with `_R_CHECK_DEPENDS_ONLY_=true`
- **Category**: Dependencies / Cascading Archival
- **Source**: https://www.r-bloggers.com/2024/10/tales-from-open-source-development-ii-a-package-you-depend-on-is-archived/
- **Novel**: Illustrates cascading archival chain. Led to creation of the "CRAN doomsday clock" by schochastics.

### Case 4: SuperCell-related package -- Multiple Rejection Reasons

- **Package**: Bioinformatics package (SuperCell-related, name not explicitly stated)
- **Date**: July 8, 2024
- **Rejection reasons**:
  1. "Non-FOSS package license (file LICENSE)" -- CC BY-NC-ND 4.0 rejected
  2. "Suggests or Enhances not in mainstream repositories: velocyto.R"
  3. "CRAN URL not in canonical form" -- must use `https://CRAN.R-project.org/package=pkgname`
  4. "Size of tarball: 9076436 bytes" -- ~9MB, over the 5MB soft limit
  5. "Package suggested but not available for checking: 'velocyto.R'"
- **Category**: License, Dependencies, URL Format, Size
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10005.html
- **Novel**: CC BY-NC-ND 4.0 is explicitly non-FOSS and rejected despite submitter believing it was acceptable.

### Case 5: hhmR -- Missing Dependency + License Issues

- **Package**: hhmR (version 0.0.1)
- **Date**: October 17, 2024
- **Rejection reasons**:
  1. "farver is not declared in your DESCRIPTION file as any dependency" -- caused "there is no package called 'farver'" during lazy loading
  2. "License stub is invalid DCF" -- CRAN requires only the CRAN template for MIT license
  3. "Please use straight rather than directed quotes" -- in Description field around 'dendextend'
- **Category**: Dependencies, License, DESCRIPTION formatting
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10192.html

### Case 6: sidra -- First Submission Notes

- **Package**: sidra (version 0.1.3)
- **Date**: November 12, 2024
- **Notes causing rejection**:
  1. "New submission" -- standard NOTE for first-time packages
  2. "License components with restrictions and base license permitting such: GPL-3 + file LICENSE"
  3. Documentation keywords with multiple terms: `\keyword{metadados,agregados}` -- keywords should be single terms
  4. Examples timing exceeded: 11.53s elapsed on Windows, 8.767s on Debian
- **Category**: First submission, License, Documentation, Timing
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10300.html

### Case 7: chisquare -- Post-Acceptance DESCRIPTION Corrections

- **Package**: chisquare (version 1.1)
- **Date**: October 2024 (deadline November 2, 2024)
- **Issue**: After acceptance, CRAN requested formatting changes to DESCRIPTION:
  - Remove version specifications for `graphics` and `stats` in Imports
  - Update R version dependency format from `R (>= 4.0.0)` to `R (>= 4.0)`
- **Problem**: Could not resubmit with same version number ("Insufficient package version submitted: 1.1, existing: 1.1")
- **Category**: DESCRIPTION formatting, Resubmission procedure
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10197.html
- **Novel**: Post-acceptance corrections requiring version bump is a procedural friction point.

### Case 8: ProTrackR2 -- Windows Build Infrastructure Error

- **Package**: ProTrackR2
- **Date**: November 12, 2024
- **Error (verbatim)**: "Cannot create temporary file in D:\\temp\\2024_11_12_ 1_50_00_12637\\: No such file or directory"
- **Category**: Build Infrastructure
- **Details**: Error appeared on CRAN Windows builder but not on r-universe, rhub, or any other platform. Same error affected unrelated package (Amelia) simultaneously, suggesting CRAN infrastructure issue rather than package problem.
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10256.html
- **Novel**: Infrastructure-level build failures affecting multiple unrelated packages.

### Case 9: cpp11tesseract -- Clang 19 Special Check Timing

- **Package**: cpp11tesseract (version 5.3.5)
- **Date**: December 20, 2024
- **Issue**: CRAN clang 19 special checks reported excessive timing: user 18.624s, system 1.701s, elapsed 22.045s
- **Category**: Timing / Compiled Code
- **Details**: Package passed all standard checks. Failed specialized clang 19 timing test. Two submissions (original and minimized) showed identical timing results. Could not reproduce locally.
- **Source**: https://www.mail-archive.com/r-package-devel@r-project.org/msg10376.html

### Case 10: serocalculator -- Internet Access Policy Violation

- **Package**: serocalculator
- **Date**: Archived November 26, 2024
- **Reason**: "policy violation. On Internet access"
- **Category**: Internet Access
- **Resolution**: Unarchived on 2025-01-25 after fixes
- **Source**: CRAN PACKAGES.in file

---

## 3. Recurring Patterns (July-December 2024)

### Pattern A: Internet Access Violations (ESCALATING)

Multiple packages archived for internet access violations in H2 2024:
- CopernicusMarine (December 2024)
- serocalculator (November 2024)

Combined with the new rate-limit policy (rev6277, August 2024), this represents an escalation in CRAN's enforcement of internet resource handling.

**Key CRAN requirement**: "Packages which use Internet resources should fail gracefully with an informative message if the resource is not available or has changed (and not give a check warning nor error)."

**Best practice pattern** (from TheCoatlessProfessor blog):
- Use `@examplesIf interactive() && curl::has_internet()` for conditional execution
- Use `skip_if_offline()` from testthat for tests
- Mock API responses with `local_mocked_bindings()` or the `{vcr}` package
- Implement `tryCatch()` blocks with informative error messaging

### Pattern B: Temporary File Management

Recurring discussion on R-package-devel (November 2024 thread) about proper temp file handling:
- Must use `tempdir()` / `tempfile()` in examples, tests, vignettes
- Must clean up with `unlink()` afterwards
- Use `withr::local_tempfile()` and `withr::local_tempdir()` for automatic cleanup in testthat
- "Detritus in the temp directory" NOTE from R CMD check

### Pattern C: Compiled Code / Sanitizer Checks

Multiple packages struggled with clang-san/clang-ASAN checks:
- cpp11tesseract (December 2024) -- timing failure
- tidyfit (January 2025, but issue originated in late 2024) -- "call to function through pointer to incorrect function type"
- Ongoing Rust packages (timeless, September 2024) -- compiler version reporting

### Pattern D: Cascading Dependency Archivals

The oaqc case (October 2024) demonstrated how a single package archival can cascade:
- One package archived for invalid maintainer email
- Multiple dependent packages receive "at risk" notifications
- Tight deadlines (days, not weeks) for fixes

CRANhaven statistics show:
- 39% of all CRAN packages (9,089 of 23,058) have been archived at least once
- 36% of archived packages eventually return, median 33 days
- Primary archival reasons: unfixed problems (5,808), unclear (1,458), dependency failures (1,270), policy violations (644)

### Pattern E: DESCRIPTION Formatting Strictness

Consistent rejections for:
- Missing single quotes around software/package names
- Unexplained acronyms
- Incorrect DOI/URL formatting (spaces after `doi:` or `https:`)
- Unnecessary `+ file LICENSE` for standard licenses
- Invalid MIT LICENSE file content (must use CRAN template)
- Directed quotes instead of straight quotes
- Title not in Title Case
- Base R packages (graphics, stats) listed with version numbers in Imports

### Pattern F: Example Timing Constraints

Multiple packages flagged for:
- Examples exceeding 5 seconds elapsed time
- CPU time > 2.5x elapsed time (indicating unauthorized multithreading)
- Overall check time exceeding 10 minutes
- Packages using more than 2 cores in examples/tests/vignettes

---

## 4. Novel Patterns (New or Escalating in H2 2024)

### Novel 1: Rate Limit Policy (NEW in August 2024)
The rev6277 addition explicitly requiring packages to avoid HTTP 429/403 errors and be mindful of shared resources is entirely new policy text. This was not in prior versions.

### Novel 2: Package Name Persistence (NEW in August 2024)
Rev6286 codified that package names cannot be changed once submitted to CRAN.

### Novel 3: Clang 19 Special Checks
The introduction of clang 19 in CRAN's special check infrastructure caused new timing failures that were difficult to reproduce locally.

### Novel 4: Post-Acceptance Corrections Requiring Version Bump
The chisquare case shows CRAN can request DESCRIPTION corrections *after* acceptance, creating a version-bump requirement for non-functional changes.

### Novel 5: Windows Builder Infrastructure Failures
The November 2024 Windows build issue affecting multiple unrelated packages represents an infrastructure-level problem that package authors cannot diagnose or fix.

### Novel 6: Rust Compiler Logging Requirements
Beyond just declaring SystemRequirements, CRAN now requires Rust packages to output compiler version information in installation logs *before* compilation begins (not after).

---

## 5. R 4.4.x New Checks (Released 2024)

### R 4.4.0 (April 24, 2024)
- R CMD check now notes when S4-style exports are used without declaring a strong dependence on package `methods`
- `tools::checkRd()` detects more problems with `\Sexpr`-based dynamic content
- R CMD check now notes Rd files without an `\alias` (previously undocumented check)
- `checkRd()` reports Rd titles/section names ending in a period (when `_R_CHECK_RD_CHECKRD_MINLEVEL_` is -5 or smaller)

### R 4.4.1 (June 14, 2024)
- R CMD check now reports as **warnings** (not notes) gfortran's "Fortran 2018 deleted features" -- features deleted in Fortran 2008 or earlier
- Fixed: R CMD check no longer broken for packages with invalid VignetteBuilder but no vignettes

---

## 6. CRAN Winter Break 2024

CRAN was **offline for maintenance from December 23, 2025 to January 7, 2026** (confirmed from mailing list discussion about plotdap submission). For 2024, no explicit closure was documented in the search results, but 123 new packages were accepted in December 2024, suggesting processing continued through most of the month.

---

## 7. CRAN Submission Statistics

From analysis of 46,525 tracked submissions (Sept 2020 - Jan 2024):
- **65% of first-time submissions accepted** on first try
- **35% rejected** on first attempt
- **14.5%** of all submission attempts rejected
- Of rejected packages: 21.9% succeed on 2nd try, 8.2% on 3rd, 4.4% need 3+
- ~8% of submissions processed too rapidly to be captured by cransays dashboard

---

## 8. Sources

1. R-package-devel mailing list archives: https://stat.ethz.ch/pipermail/r-package-devel/
2. Mail-archive R-package-devel: https://www.mail-archive.com/r-package-devel@r-project.org/
3. CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
4. CRAN Submission Checklist: https://cran.r-project.org/web/packages/submission_checklist.html
5. CRAN Cookbook (R Consortium): https://contributor.r-project.org/cran-cookbook/
6. eddelbuettel/crp (policy diffs): https://github.com/eddelbuettel/crp
7. CRANhaven archival statistics: https://www.cranhaven.org/cran-archiving-stats.html
8. "Tales from Open Source Development" blog series: https://blog.schochastics.net/
9. "Is CRAN Holding R Back?" (Lamstein): https://www.r-bloggers.com/2025/02/is-cran-holding-r-back/
10. TheCoatlessProfessor API packages guide: https://blog.thecoatlessprofessor.com/programming/r/api-packages-and-cran-requirements/
11. CRAN Rust packages guide: https://cran.r-project.org/web/packages/using_rust.html
12. llrs.dev CRAN submission statistics: https://llrs.dev/post/2024/01/10/submission-cran-first-try/
13. coolbutuseless CRAN-checks: https://github.com/coolbutuseless/CRAN-checks

---

## 9. Recommendations for Knowledge Base Updates

### New Rules to Add

1. **INET-RATE**: Rate limit policy (rev6277). Packages must avoid triggering HTTP 429/403 errors and be mindful that other packages may use the same external resource. Severity: ARCHIVAL.

2. **DESC-RENAME**: Package names are persistent (rev6286). Cannot rename a package once submitted. Severity: REJECTION.

3. **CODE-RUSTLOG**: Rust compiler version must be reported in installation logs before compilation begins, not just in SystemRequirements. Severity: ARCHIVAL.

4. **CODE-CLANG19**: Clang 19 special checks may flag timing issues not reproducible locally. Packages with compiled code should test against CRAN's specific infrastructure.

5. **DESC-BASEPKG**: Do not specify version numbers for base R packages (graphics, stats, etc.) in Imports. Severity: REJECTION (post-acceptance correction).

6. **DESC-QUOTES**: Use straight quotes, not directed/smart quotes, in DESCRIPTION fields. Severity: REJECTION.

7. **DESC-KEYWORDS**: `\keyword{}` entries in Rd files should contain single terms, not comma-separated lists. Severity: NOTE.

### Rules to Update

1. **INET-01** (Internet access): Add the new rate-limit requirement text. Increase severity emphasis. Note that archival for internet access violations was actively occurring in H2 2024.

2. **LICENSE rules**: Add CC BY-NC-ND 4.0 as explicitly rejected (non-FOSS). Add MIT license template requirement ("only ship the CRAN template for the MIT license").

3. **SIZE rules**: Note that ~9MB packages continue to be flagged; the 5MB soft limit is actively enforced.

4. **DEPS rules**: Add cascading archival risk. Note that `_R_CHECK_DEPENDS_ONLY_=true` is used for testing conditional Suggests.

5. **TIMING rules**: Add overall 10-minute check time limit. Add clang-san special check timing.

### Open Questions

1. What is the exact process when CRAN archives a package without the maintainer noticing? Is there always an email, or can it happen silently?
2. How does the CRAN team handle Windows builder infrastructure failures -- are affected submissions automatically retried?
3. Is there a formal list of "common" acronyms that don't need explanation in DESCRIPTION?
4. What specific changes did clang 19 introduce that affect R package timing?
