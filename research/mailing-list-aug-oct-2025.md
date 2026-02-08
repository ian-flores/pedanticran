# R-package-devel Mailing List: CRAN Rejection Patterns (Aug-Oct 2025)

Generated: 2026-02-08

## Executive Summary

Analysis of the R-package-devel mailing list archives for Q3 2025 (July-September) and Q4 2025 (October-December, filtered to October) reveals recurring CRAN rejection patterns across several categories. The most common issues are: (1) sanitizer/compiler warnings treated as blocking failures, (2) writing to user filespace, (3) tarball size and CPU time violations, (4) namespace/import conflicts, and (5) dependency cascading archival. Several threads reveal frustrations with unreproducible CRAN check environments and unclear feedback from automated systems.

---

## Rejection Cases by Thread

### 1. Package: Mega2R (July 2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10895.html
- **Type:** Resubmission (update)
- **Category:** Compiler/sanitizer warnings (false positive)
- **Verbatim CRAN text:** "package Mega2R_1.2.0.tar.gz does not pass the incoming checks automatically."
- **Details:** A warning appeared during gcc-san flavor testing regarding SQLite3 code (vendor sqlite3.c). The warning indicated a runtime memory error, but the submitter argues this is a compiler bug, not a package bug. Other sanitizer checks (clang-asan, clang-ubsan, valgrind, m1-san) all passed. SQLite forum confirmed "it looks like a compiler issue not a bug in SQLite."
- **Secondary issue:** m1-san tests revealed incompatibility with development version of GenomeInfoDb (function `seqlevels<-` being moved to Seqinfo package).
- **Outcome:** Submitter received no response to appeal.
- **Novel?** Yes -- false positive from vendor code (SQLite) in a single sanitizer flavor.

### 2. Package: HLSM (May-June 2025, discussed Aug)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10698.html
- **Type:** Resubmission (previously archived)
- **Category:** Compiler/sanitizer warnings, archival legacy
- **Verbatim CRAN text:** "package HLSM_0.9.1.tar.gz does not pass the incoming checks automatically"
- **Details:** Package carries a persistent "Archived on 2024-01-19 as issues were not corrected in time" note. A clang-UBSAN warning flagged: "vendor/cigraph/src/constructors/adjacency.c:87:34: runtime error: nan is outside the range" in a dependency's C code. 24 additional compilation warnings from external package functions.
- **Novel?** No -- recurring sanitizer false-positive pattern in vendored C code.

### 3. Package: ironseed (July 2025, discussed through Aug)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10849.html
- **Type:** First submission
- **Category:** Writing to user filespace
- **Verbatim CRAN text:** "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies. Please omit any default path in writing functions. In your examples/vignettes/tests you can write to tempdir(). -> tools/config.Rtools/config/configure.R"
- **Details:** The flagged file path (tools/config.Rtools/config/configure.R) did not exist in the package source -- it was generated during installation by a configure script. Uwe Ligges ultimately clarified this was a false positive from static analysis, and the feedback could be disregarded.
- **Novel?** Partially -- the configure-script-generated file path triggering false positives is unusual.

### 4. Package: (unknown, CC BY-NC-ND 4.0 license) (early 2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10005.html
- **Type:** First submission
- **Category:** License, dependencies, URL format
- **Verbatim CRAN text (multiple issues):**
  - "Non-FOSS package license (file LICENSE)"
  - "Suggests or Enhances not in mainstream repositories: velocyto.R"
  - URL format errors (not in canonical form)
- **Details:** CC BY-NC-ND 4.0 was flagged as non-FOSS. A suggested package (velocyto.R) was not in standard repositories. URLs were not in canonical CRAN form (`https://CRAN.R-project.org/package=pkgname`).
- **Novel?** No -- standard multi-issue rejection.

### 5. Package: (unknown, test removal) (mid-2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10725.html
- **Type:** Resubmission
- **Category:** Test suite management
- **Verbatim CRAN text:** Developer "removed the failing tests which is not the idea of tests."
- **Details:** Package was rejected because the maintainer removed failing tests instead of fixing them. Ivan Krylov suggested using the 'covr' package to measure test coverage before/after, and if coverage increased, present that as justification.
- **Novel?** No -- but the specific phrasing "not the idea of tests" is useful to capture.

### 6. Package: geotopbricks (mid-2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10665.html
- **Type:** Update
- **Category:** Examples exceeding time limits
- **Verbatim CRAN text:** "Examples with CPU (user + system) or elapsed time > 5s / get.geotop.inpts.keyword.value 1.406 0.027 5.326"
- **Details:** One function example took 5.326 seconds on Debian (just barely over the 5s limit). Windows checks passed. Solution: wrap in `\donttest{}`.
- **Novel?** No -- standard timing violation.

### 7. Package: flightsbr (July 2025)

- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q3/011830.html
- **Type:** Cascading removal (dependency archived)
- **Category:** Dependency archival
- **Details:** Package removed from CRAN without warning because it depends on {parzer}, which was itself removed on July 1st. Both packages were passing all CRAN checks at the time of removal. Maintainer: "I never received any email or warning that the package would be removed."
- **Novel?** Yes -- no-warning cascading removal even when checks pass.

### 8. Package: HACSim (September 2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11038.html
- **Type:** Resubmission
- **Category:** Tarball size, namespace conflicts
- **Verbatim CRAN text (NOTE):** "Size of tarball: 13246681 bytes"
- **Verbatim CRAN text (WARNINGs):** Multiple "Replacing previous import" messages:
  - "Replacing previous import 'shinydashboard::taskItem' by 'shinydashboardPlus::taskItem'"
  - "Replacing previous import 'shinyWidgets::progressBar' by 'shinydashboardPlus::progressBar'"
  - "Replacing previous import 'shinyWidgets::alert' by 'shinyjs::alert'"
  - Plus similar warnings for: dashboardHeader, box, messageItem, dashboardSidebar, dashboardPage, notificationItem
- **Details:** Tarball is ~13MB (limit is nominally 5MB, hard limit 10MB). Namespace masking warnings from conflicting Shiny-related imports. Changing from `importFrom` to `import` did not resolve.
- **Novel?** No -- but the Shiny ecosystem namespace collision pattern is common.

### 9. Package: blosc (August 2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10955.html
- **Type:** First submission (newbie)
- **Category:** Process/submission status
- **Details:** New package submitted Aug 24, 2025. Passed automatic checks but "pending manual check." Developer could not find package on CRAN incoming page. Uwe Ligges: "CRAN received > 100 newbie submissions within three days." Manual review expected within 10 working days.
- **Novel?** No -- but the >100 newbie submissions in 3 days is useful context for expected wait times.

### 10. Package: rsofun (October 2025)

- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q4/012028.html
- **Type:** Update
- **Category:** CPU time during installation
- **Verbatim CRAN text:** "Installation took CPU time 2.8 times elapsed time"
- **Details:** Pretest failure on Debian. The CPU/elapsed time ratio suggested parallel compilation. The issue occurred during installation (not tests/examples/vignettes). Standard solutions from CRAN cookbook did not apply.
- **Novel?** Partially -- installation-phase CPU time ratio (vs. typical examples/vignette timing) is less common.

### 11. Package: boostmath (mid-2025)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10902.html
- **Type:** Update
- **Category:** CPU time during installation (LTO-related)
- **Verbatim CRAN text:** "Installation took CPU time 3.5 times elapsed time"
- **Details:** Root cause identified as "UseLTO" in DESCRIPTION file. Removing this line fixed the issue. Link Time Optimization triggers parallel compilation that CRAN flags.
- **Novel?** Yes -- UseLTO causing CPU time NOTE is a new-ish pattern.

### 12. Package: GeneralizedUmatrixGPU (October 2025)

- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q4/012024.html
- **Type:** Submission
- **Category:** Segfault on Linux
- **Verbatim error text:** "*** caught segfault *** address 0x10, cause 'memory not mapped'"
- **Details:** Package worked locally but segfaulted on CRAN's Linux testing. Docker-based testing by Dirk Eddelbuettel passed without segfault, suggesting environment-specific issue.
- **Novel?** No -- standard platform-specific segfault pattern.

### 13. Package: broadcast (October 2025)

- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q4/012027.html
- **Type:** Update
- **Category:** Build/installation timeout
- **Verbatim CRAN text:** "CPU time limit exceeded"
- **Details:** Updated package fails installation on r-devel with Fedora Clang despite passing on Windows, macOS, and GitHub Actions. Author: "It's unclear to me why exactly installation fails."
- **Novel?** No -- but "CPU time limit exceeded" during install (not check) is worth noting.

### 14. Package: DiNAMIC.Duo (October 2025)

- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q4/012026.html
- **Type:** Check failure
- **Category:** External service connectivity
- **Verbatim error text:** "SSL connect error [aug2020.archive.ensembl.org]: OpenSSL/3.2.4: error:0A0000C6:SSL routines::packet length too long"
- **Details:** Package uses biomaRt to connect to Ensembl archive. The archive is periodically unavailable. Developer needs graceful failure handling per CRAN standards.
- **Novel?** No -- standard external service availability pattern. But the specific SSL error on CRAN's OpenSSL version is notable.

### 15. Package: nprcgenekeepr (July 2025, discussed later)

- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11261.html
- **Type:** Archived after publication
- **Category:** Test failure on r-devel
- **Details:** Published July 25, archived July 29 -- just 4 days. Archived because of a test failure on r-devel Linux that produces unexpected output from `print(summary(qcStudbook(pedOne, reportErrors = TRUE)))`.
- **CRAN notice:** "Archived on 2025-07-29 as issues were not corrected in time."
- **Novel?** Yes -- archived 4 days after publication is extremely fast and suggests the issue existed pre-publication but only manifested on r-devel.

### 16. Package: (Russell Lenth's package) (August 2025)

- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q3/011885.html
- **Type:** Mandatory update
- **Category:** Deadline vs. CRAN vacation conflict
- **Details:** Package had errors in R-devel and needed fixing by Aug 26. But CRAN was on vacation until Aug 19, and the maintainer was traveling Aug 17-27. The fix was ready but couldn't be submitted in time.
- **Novel?** Yes -- Catch-22 between CRAN vacation and package deadline is a systemic issue.

---

## Recurring CRAN Rejection Patterns (August-October 2025)

### Category 1: Compiler/Sanitizer Warnings (gcc-san, clang-UBSAN)
- **Frequency:** 4+ threads in this period
- **Common verbatim text:** "does not pass the incoming checks automatically"
- **Pattern:** Warnings in vendored C/C++ code (SQLite, igraph, Armadillo) that appear only on specific CRAN check flavors (gcc-san, clang-UBSAN) and are often false positives or upstream compiler issues.
- **Challenge:** Developers cannot reproduce these locally, even with rhub Docker images.

### Category 2: Writing to User Filespace
- **Frequency:** 2+ threads
- **Common verbatim text:** "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace"
- **Pattern:** Functions with default file paths that write outside tempdir(). Also triggered by configure scripts generating files in unexpected locations.

### Category 3: Timing Violations (CPU time, elapsed time)
- **Frequency:** 4+ threads
- **Common verbatim text:** "Examples with CPU (user + system) or elapsed time > 5s" / "Installation took CPU time X.X times elapsed time" / "CPU time limit exceeded"
- **Pattern:** Examples slightly over 5s threshold; installation-phase parallel compilation flagged; UseLTO causing CPU time inflation.

### Category 4: Package Size
- **Frequency:** 2+ threads
- **Common verbatim text:** "Size of tarball: NNNNN bytes" (as a NOTE)
- **Pattern:** Packages exceeding 5MB (soft limit) or 10MB (hard limit). Especially common with packages including data or Shiny UI resources.

### Category 5: Namespace/Import Conflicts
- **Frequency:** 2+ threads
- **Common verbatim text:** "Replacing previous import 'pkg1::fun' by 'pkg2::fun'"
- **Pattern:** Multiple Shiny-related packages (shinydashboard, shinydashboardPlus, shinyWidgets, shinyjs) exporting overlapping function names. Not easily resolved by changing import strategy.

### Category 6: Dependency Cascading Archival
- **Frequency:** 3+ threads
- **Pattern:** Package A depends on Package B; Package B is archived; Package A is automatically archived without warning to its maintainer, even if Package A passes all checks. This is a systemic CRAN issue that generates significant developer frustration.

### Category 7: Test Suite Issues
- **Frequency:** 2+ threads
- **Common verbatim text:** "removed the failing tests which is not the idea of tests"
- **Pattern:** Developers remove failing tests as a shortcut. CRAN rejects this approach. Also: tests that pass locally but fail on r-devel due to dependency changes.

### Category 8: License and URL Issues
- **Frequency:** 2+ threads
- **Common verbatim text:** "Non-FOSS package license" / "CRAN URL not in canonical form"
- **Pattern:** CC BY-NC-ND 4.0 flagged as non-FOSS; URLs not in canonical `https://CRAN.R-project.org/package=X` form.

### Category 9: Process/Timing Issues
- **Frequency:** 3+ threads
- **Pattern:** Submission status lost, >100 newbie submissions in 3 days causing delays, deadline conflicts with CRAN vacation periods, packages archived days after publication.

---

## Notable Policy Discussions (Oct 2025)

### Go Language Packages
- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q4/ (CRAN Policy on Go using Packages)
- No formal CRAN policy for Go packages exists. Go's `c-shared` buildmode can crash R if multiple Go modules load. Recommended approach: IPC via Nanomsg instead of direct integration. Go packages may be better suited for R-multiverse than CRAN.

### Makefile Extensions
- **Source:** https://stat.ethz.ch/pipermail/r-package-devel/2025q4/012023.html
- Binary compliance: either use only POSIX make features, or declare `SystemRequirements: GNU make`. No middle ground. Common pitfalls: ifeq/ifneq, ${shell}, ${wildcard}, +=, :=, $<, $^, .PHONY.

### Rf_lazy_duplicate Moved to nonAPI (Oct 2025)
- **Source:** R-package-devel Q4 2025 thread by Iris Simmons, Tomas Kalibera
- Functions being moved to nonAPI will break packages that use them directly. Packages need to update to use supported API alternatives.

### Author Field / ORCID Formatting
- **Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10875.html
- NOTE: "Author field differs from that derived from Authors@R" triggered by ORCID identifiers formatted differently (angle brackets vs parentheses). Appears to be a temporary inconsistency between R versions.

---

## CRAN Cookbook: Complete Rejection Reason Reference

Cross-referencing with the CRAN Cookbook (https://contributor.r-project.org/cran-cookbook/), here are ALL documented rejection reasons with verbatim text:

### Code Issues
| Issue | Verbatim CRAN Text |
|-------|-------------------|
| T/F instead of TRUE/FALSE | "Please write TRUE and FALSE instead of T and F." |
| Hardcoded seed | "Please do not set a seed to a specific number within a function." |
| print()/cat() for messages | "You write information messages to the console that cannot be easily suppressed...use message()/warning()" |
| Options not restored | "Please ensure with an immediate call of on.exit() that settings are reset when function exited." |
| Writing to home dir | "Please ensure functions do not write by default in user's home filespace...write to tempdir()" |
| Temp file detritus | NOTE for "detritus in the temp directory" |
| Writing to .GlobalEnv | "Please do not modify the global environment (e.g., by using <<-) in your functions." |
| installed.packages() | "installed.packages() can be very slow...use find.package or requireNamespace" |
| warn = -1 | "This is not allowed. Please rather use suppressWarnings() if really needed." |
| Installing packages | "Please do not install packages in functions, examples or vignettes." |
| More than 2 cores | "Please ensure that you do not use more than 2 cores in examples, vignettes, etc." |

### DESCRIPTION Issues
| Issue | Verbatim CRAN Text |
|-------|-------------------|
| Unquoted software names | "Please always write package names, software names and API names in single quotes" |
| Unexplained acronyms | "Please always explain all acronyms in the description text" |
| Unnecessary LICENSE file | "We do not need '+ file LICENSE' and the file as these are part of R" |
| Title not in title case | "The Title field should be in title case." |
| Missing Authors@R | "No Authors@R field in DESCRIPTION. Please add one" |
| Bad reference formatting | "Remove the space after <doi:...> to enable the reference link" |

### General Issues
| Issue | Verbatim CRAN Text |
|-------|-------------------|
| Short Description | "Please add more details about the package functionality and implemented methods in your Description text." |
| dontrun misuse | "\\dontrun{} should only be used if the example really cannot be executed... Please replace \\dontrun with \\donttest." |
| All examples in donttest | "All your examples are wrapped in \\donttest{} and therefore do not get tested." |
| Package too large | "A CRAN package should not be larger than 5 MB. Please reduce the size." |

---

## CRAN Archival Statistics (Background Context)

From CRANhaven and Lluis Revilla's research:

- **39% of all CRAN packages** (9,089 of 23,058) have been archived at least once
- **Top archival reasons:**
  1. Package problems not corrected in time (60% of events, 5,150 packages)
  2. Dependency archival (11%)
  3. Policy violations (7%, 644 packages)
  4. Miscellaneous (5%) -- licensing, R version incompatibility, authorship disputes
  5. Maintainer email failures (3%, 228 packages)
- **36-38% of archived packages eventually return** to CRAN
- **Median return time:** ~33 days
- **95% of resubmissions** are eventually accepted

---

## Sources

### Mailing List Archives
- R-package-devel Q3 2025: https://stat.ethz.ch/pipermail/r-package-devel/2025q3/
- R-package-devel Q4 2025: https://stat.ethz.ch/pipermail/r-package-devel/2025q4/
- mail-archive.com mirror: https://www.mail-archive.com/r-package-devel@r-project.org/

### CRAN Official Resources
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
- CRAN Submission Checklist: https://cran.r-project.org/web/packages/submission_checklist.html

### Community Resources
- CRAN Cookbook (Code Issues): https://contributor.r-project.org/cran-cookbook/code_issues.html
- CRAN Cookbook (DESCRIPTION Issues): https://contributor.r-project.org/cran-cookbook/description_issues.html
- CRAN Cookbook (General Issues): https://contributor.r-project.org/cran-cookbook/general_issues.html
- CRANhaven Archiving Statistics: https://www.cranhaven.org/cran-archiving-stats.html
- Lluis Revilla - Reasons for CRAN Archivals: https://llrs.dev/post/2021/12/07/reasons-cran-archivals/

### Specific Thread URLs
- Mega2R false positive: https://www.mail-archive.com/r-package-devel@r-project.org/msg10895.html
- HLSM secondary issues: https://www.mail-archive.com/r-package-devel@r-project.org/msg10698.html
- ironseed user filespace: https://www.mail-archive.com/r-package-devel@r-project.org/msg10849.html
- Test removal rejection: https://www.mail-archive.com/r-package-devel@r-project.org/msg10725.html
- geotopbricks timing: https://www.mail-archive.com/r-package-devel@r-project.org/msg10665.html
- flightsbr removal: https://stat.ethz.ch/pipermail/r-package-devel/2025q3/011830.html
- HACSim warnings: https://www.mail-archive.com/r-package-devel@r-project.org/msg11038.html
- blosc submission status: https://www.mail-archive.com/r-package-devel@r-project.org/msg10955.html
- boostmath CPU time: https://www.mail-archive.com/r-package-devel@r-project.org/msg10902.html
- nprcgenekeepr archived: https://www.mail-archive.com/r-package-devel@r-project.org/msg11261.html
- Resubmitting archived packages: https://www.mail-archive.com/r-package-devel@r-project.org/msg11187.html
- CRAN Policy on Go: https://www.mail-archive.com/r-package-devel@r-project.org/msg11113.html
- Author field NOTE: https://www.mail-archive.com/r-package-devel@r-project.org/msg10875.html

---

## Recommendations for pedanticran Knowledge Base

1. **Add sanitizer false-positive guidance** -- many rejections stem from vendored C code triggering gcc-san/clang-UBSAN warnings that cannot be reproduced locally.
2. **Add UseLTO warning** -- `UseLTO: yes` in DESCRIPTION triggers "Installation took CPU time X times elapsed time" NOTE.
3. **Expand cascading dependency archival coverage** -- packages can be archived without warning when a dependency is archived, even if they pass all checks.
4. **Add Go language package guidance** -- no formal CRAN policy exists; IPC recommended over direct integration.
5. **Add Makefile portability checks** -- binary compliance (POSIX only, or declare GNU make requirement).
6. **Add nonAPI function detection** -- R internals like Rf_lazy_duplicate being moved to nonAPI will break packages.
7. **Strengthen test removal detection** -- "removed the failing tests which is not the idea of tests" is a direct CRAN quote.
8. **Add namespace collision detection** -- particularly for Shiny ecosystem packages with overlapping exports.

## Open Questions

1. What is the exact threshold for the CPU/elapsed time ratio that triggers a NOTE? (Appears to be ~2x)
2. Is there a formal policy on how quickly a newly published package can be archived? (nprcgenekeepr was archived 4 days after publication)
3. When will CRAN formalize Go language package policy?
4. How many packages were affected by the Rf_lazy_duplicate -> nonAPI change?
