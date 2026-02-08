# R-package-devel Mailing List: CRAN Rejection Patterns (Nov 2025 - Jan 2026)

Generated: 2026-02-08

## Executive Summary

Analysis of the R-package-devel mailing list (Q4 2025 and Q1 2026 archives) and related web sources reveals 15+ distinct rejection/issue patterns from November 2025 through January 2026. Key themes include: cascading dependency archival, graceful failure requirements getting stricter enforcement, Go toolchain packages being effectively unwelcome, IP blocking during CRAN infrastructure maintenance, and continued friction around CPU time/parallelism during installation. The tarball size limit was raised from 5MB to 10MB. R-devel introduced subset assignment changes that broke packages using active bindings.

## Research Sources

- R-package-devel mailing list: https://stat.ethz.ch/pipermail/r-package-devel/ (Q4 2025, Q1 2026 archives)
- Mail Archive mirror: https://www.mail-archive.com/r-package-devel@r-project.org/
- Blog posts, CRAN policy pages, and CRAN Cookbook

---

## Rejection/Issue Categories

### 1. Cascading Dependency Archival

**Packages:** geomander + reverse dependencies (Dec 2025)

**What happened:** Christopher Kenny's package `geomander` had a broken example. Brian Ripley archived the package, which then caused all reverse dependencies to be auto-archived as well.

**Verbatim from Uwe Ligges:**
> "Please submit geomander and get it accepted first. The others will be auto-archived otherwise."

**Key details:**
- Category: Dependencies / archival
- Type: Resubmission of archived packages
- Novel: The cascading archival pattern is known but the deadline interpretation was disputed
- Ligges clarified "before" means strictly "<" (before, not on the deadline date)
- Archived packages undergo manual review, which takes longer
- The CRAN winter break (Dec 23 - Jan 7) compounded the urgency

**Source:** http://www.mail-archive.com/r-package-devel@r-project.org/msg11179.html

---

### 2. Graceful Failure in Subsequent Code (Stricter Enforcement)

**Package:** aopdata (Dec 2025)

**What happened:** Prof Ripley contacted the maintainer saying the package was not "falling gracefully." The function `read_population()` correctly returned NULL with an informative message when internet was unavailable, but subsequent ggplot2 code in the vignette errored when it received NULL and tried to access a "P001" column.

**CRAN's position (paraphrased):**
> "So it is not good enough to have a function return NULL when the subsequent code will throw an error when it gets that NULL."

**Key details:**
- Category: Code / graceful failure
- Type: Enforcement of existing policy with stricter interpretation
- Novel: CRAN now expects graceful failure not just in the function that hits the network, but in ALL downstream code in examples/vignettes that consumes the result
- The maintainer argued CRAN policy requires the *package* to fail gracefully, not downstream user code
- Duncan Murdoch recommended adding NULL checks in vignettes with informative messages

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11214.html

---

### 3. Go Toolchain Packages Effectively Blocked

**Packages:** Various Go-based packages (Nov 2025)

**What happened:** Sounkou Mahamane Toure asked CRAN to clarify its policy on Go-using packages. His package was archived, and he never received a rejection email. Key technical issues:
- Go's c-shared buildmode can crash R when multiple instances load in the same process
- Windows win-builder lacks Go on PATH
- Multiple Go runtimes in one process cause crashes (especially macOS Intel)
- High memory usage from multiple garbage-collected pools

**Expert advice from Dewey Dunnington:**
> "I would not recommend building R packages with Go dependencies" despite access to excellent Go libraries without equivalents in other languages.

**Key details:**
- Category: Dependencies / toolchain
- Type: Effective rejection (not explicit policy, but practical impossibility)
- Novel: This is a relatively new area as Go gains popularity
- Henrik Bengtsson noted tarball size limit was recently raised to 10MB
- Similar packages like adbcbigquery distribute via R-multiverse instead

**Source:** http://www.mail-archive.com/r-package-devel@r-project.org/msg11103.html

---

### 4. Package Archived Days After Publication

**Package:** nprcgenekeepr v1.0.8 (late Jan 2026 discussion, archival Jul 2025)

**What happened:** Published to CRAN on July 25, 2025, archived four days later on July 29, 2025. This was a repeat pattern -- same package was previously archived on 2022-11-03.

**Verbatim from CRAN metadata:**
> "Archived on 2025-07-29 as issues were not corrected in time."

**Key details:**
- Category: Testing / check failures
- Type: Post-publication archival
- The issue was a test failure in `test_print.summary.nprcgenekeeprErr.R` on Linux with r-devel
- Ben Bolker identified the specific failing test
- The test produced unexpected error output instead of remaining silent

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11262.html

---

### 5. Installation CPU Time Exceeds Elapsed Time

**Packages:** rsofun v5.1.0 (Oct 2025), multiple others

**NOTE text:**
> "Installation took CPU time 2.8 times elapsed time"

**What it means:** Package installation is using more than 2 CPU cores, violating CRAN's parallelism policy.

**Key details:**
- Category: Code / performance
- Type: NOTE that can block acceptance
- CRAN requirement: packages must not use more than 2 cores by default
- Common causes: `UseLTO` in DESCRIPTION, compilation happening twice (before and after linking), Rust packages using rayon, Go packages
- Fix: Limit threads to 1 in examples/tests/vignettes, use j-flag for compilation control

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11065.html

---

### 6. Removing Failing Tests = Rejection

**Package:** Not named (discussion ~May 2025, referenced in Nov-Jan period)

**What happened:** Developer removed failing tests and resubmitted. CRAN rejected.

**CRAN feedback (paraphrased):**
> "Removed the failing tests which is not the idea of tests."

**Key details:**
- Category: Testing
- Type: First/resubmission rejection
- Novel: Not a new rule, but frequently encountered
- Ivan Krylov suggested measuring test coverage before/after with covr package and highlighting increased coverage

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10725.html

---

### 7. False Positive from Sanitizer Check (gcc-san)

**Package:** Mega2R v1.2.0 (discussion ~Jun 2025)

**Rejection message:**
> "Package Mega2R_1.2.0.tar.gz does not pass the incoming checks automatically."

**WARNING text:**
> "Flavor: r-devel-linux-x86_64-debian-special-gcc-san
> Check: Post-processing issues found for gcc-san, Result: WARNING
> File: build_vignettes.log
> vendor/sqlite3/sqlite3.c:80239:14: runtime error: load of address..."

**Key details:**
- Category: Code / compiled code
- Type: Automated rejection
- Novel: The issue was in vendored SQLite code, confirmed as a compiler bug by the SQLite forum
- clang-asan, clang-ubsan, and valgrind all passed; only gcc-san failed
- Developer argued this was a false positive

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10895.html

---

### 8. Writing to User's Home Directory

**Package:** ironseed (~Jul 2025)

**Verbatim CRAN rejection:**
> "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies. Please omit any default path in writing functions. In your examples/vignettes/tests you can write to tempdir().
> -> tools/config.Rtools/config/configure.R"

**Key details:**
- Category: Code / filesystem
- Type: Rejection
- The configure script (from Kevin Ushey's framework) inadvertently created a file during installation
- Developer couldn't find the file in source -- it was generated at install time

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg10852.html

---

### 9. NOTE on URLs (Platform-Specific False Positive)

**Package:** broadcast (Nov 2025)

**What happened:** CRAN check suggested the BugReports URL should be `https://github.com/tony-aw/broadcast/issues/issues` (doubled "issues") when the correct URL was `https://github.com/tony-aw/broadcast/issues/`.

**Key details:**
- Category: DESCRIPTION / URLs
- Type: NOTE (potentially blocking)
- Only appeared on r-devel-linux-x86_64-debian-gcc, not other platforms
- This appears to be a bug in the URL checking code

**Source:** http://www.mail-archive.com/r-package-devel@r-project.org/msg11131.html

---

### 10. Deprecated Dependency (qs -> qs2)

**Package:** nlmixr2rpt (Dec 2025)

**What happened:** nlmixr2rpt depended on nlmixr2est which required the qs package. The qs package was deprecated and removed from CRAN in favor of qs2.

**Key details:**
- Category: Dependencies
- Type: CRAN check error from dependency archival
- Packages need to track dependency health proactively
- Question: if upstream fixes the issue within the 2-week correction period, does downstream need to act?

**Source:** http://www.mail-archive.com/r-package-devel@r-project.org/msg11153.html

---

### 11. Subset Assignment Rule Changes Breaking Packages

**Package:** Unnamed package by Konrad Rudolph (Dec 2025)

**Error:** `"cannot change value of locked binding for '*tmp*'"`

**What happened:** R-devel revision r89121 changed how active binding functions work, preventing mutation. Packages using `eval()` to perform subset assignment to complex expressions inside active bindings broke.

**Key details:**
- Category: Code / R-devel compatibility
- Type: Platform-specific failure (r-devel-linux-x86_64-debian-gcc only)
- Luke Tierney committed a fix in r89182
- This is a recurring pattern: R-devel changes break packages before new R release

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11195.html

---

### 12. CRAN Submission Portal IP Blocking

**Timeline:** Jan 9, 2026

**What happened:** After CRAN's winter vacation (Dec 23 - Jan 7), some developers found the submission portal (xmpalantir.wu.ac.at/cransubmit/) blocked their IP addresses. Devtools had attempted submissions during the vacation period, creating incomplete entries that triggered IP blocks.

**Uwe Ligges' advice:**
> "Send your IP to [CRAN email] for a quick solution."

**Key details:**
- Category: Infrastructure
- Type: Access issue (not rejection per se)
- Hadley Wickham initially reported the issue
- Some IPs were selectively blocked (work vs home addresses)

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11242.html

---

### 13. MathJax/KaTeX Conflicts in R-devel

**Package:** metap (Dec 2025)

**What happened:** R's new enhanced HTML help system with KaTeX/MathJax support triggered HTML validation warnings: `"warning: <script> anchor 'MathJax-script' already defined"` in every .Rd file using the mathjaxr package.

**Key details:**
- Category: Documentation
- Type: NOTE (potentially blocking)
- Conflict between mathjaxr package and R's new built-in math rendering
- The developer found a solution (marked as [Solved])

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11206.html

---

### 14. Fortran Compilation Warnings on macOS

**Package:** mnormt v2.1.2 (Jan 2026)

**Errors:**
> "ld: library 'emutls_w' not found"
> "Possible change of value in conversion from REAL(8) to INTEGER(4)"

**Key details:**
- Category: Code / compiled code
- Type: Build failure
- Fortran code worked for years, broke after macOS 26.2 (Tahoe) + Xcode update
- Fix: update to gfortran 14.2
- Platform toolchain changes outside developer control can break packages

**Source:** https://www.mail-archive.com/r-package-devel@r-project.org/msg11270.html

---

### 15. macOS ARM64 Missing System Headers

**Packages:** Multiple (Nov 2025)

**What happened:** `stdio.h` and `assert.h` not found on CRAN's macOS ARM64 machines. Also `oldrel-macos-arm64` was missing Fortran.

**Key details:**
- Category: Infrastructure / platform
- Type: Build failure (CRAN infrastructure issue)
- Simon Urbanek addressed the issues
- Affects packages with compiled code

**Source:** stat.ethz.ch/pipermail/r-package-devel/2025q4/ (threads from Nov 2025)

---

## Non-FOSS License Rejections (Ongoing)

**Policy:** Packages with licenses not listed at https://svn.r-project.org/R/trunk/share/licenses/license.db will generally not be accepted.

**2025 data from R Journal:** From January 2025 to March 2025, CRAN received 7,690 package submissions. 12,213 actions took place: 9,271 (76%) auto-processed, 2,942 (24%) manual.

---

## Blog Post: "Is CRAN Holding R Back?" (Feb 2025)

**Author:** Ari Lamstein

**Triggered by:** The `acs` package was archived for a NOTE about non-portable `/bin/bash` references:
> "NOTE 'configure': /bin/bash is not portable 'cleanup': /bin/bash is not portable"

These files were introduced in 2016, nine years before archival. Cascading effect archived:
- choroplethr (11 years on CRAN, 289k downloads)
- noaastormevents
- synthACS

**Author's criticisms:**
1. Release frequency limited to "no more than every 1-2 months"
2. Forced package fragmentation
3. Documentation/vignette size limits
4. Python's PyPI allows automated publishing with no approval process (608k+ projects vs CRAN's 22k)

**Source:** https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/

---

## Twitter/Mastodon Package Archival

- **twitteR**: Archived 2025-02-17 ("issues were not corrected despite reminders")
- **rtweet**: Archived 2025-04-07 ("issues were not corrected despite reminders")

---

## CRAN Infrastructure Events

| Date | Event |
|------|-------|
| Dec 23, 2025 | CRAN submissions close for winter break |
| Jan 7, 2026 | CRAN submissions reopen |
| Jan 9, 2026 | IP blocking issues reported (devtools submissions during break triggered blocks) |

---

## Tarball Size Limit Change

The CRAN source package tarball size limit was increased from 5MB to 10MB (noted by Henrik Bengtsson in Nov 2025 thread). The new policy text:
> "Source package tarballs should if possible not exceed 10MB."

This was previously 5MB. A modestly increased limit can be requested at submission for vendor files.

---

## Summary of Rejection Categories Found

| Category | Count | Examples |
|----------|-------|----------|
| Dependencies / archival | 3 | geomander cascade, qs deprecation, acs cascade |
| Code / graceful failure | 2 | aopdata, general policy |
| Code / performance | 1 | rsofun CPU time |
| Code / compiled code | 3 | Mega2R gcc-san, mnormt Fortran, macOS headers |
| Code / filesystem | 1 | ironseed writing to home |
| Code / R-devel compat | 1 | subset assignment changes |
| Testing | 2 | Removed tests, nprcgenekeepr |
| DESCRIPTION / URLs | 1 | broadcast URL doubling |
| Documentation | 1 | MathJax conflicts |
| Dependencies / toolchain | 1 | Go packages |
| Infrastructure | 2 | IP blocking, submission portal |
| Licensing | 1 | Non-FOSS (ongoing) |

---

## Novel/Unusual Patterns (Nov 2025 - Jan 2026)

1. **Graceful failure now extends to downstream code in vignettes** -- not just the network-calling function
2. **Go packages effectively blocked** -- no explicit policy but practical impossibility
3. **Tarball size limit raised to 10MB** -- positive change for packages with vendored dependencies
4. **R-devel active binding changes** -- broke packages using eval-based subset assignment
5. **CRAN submission IP blocking after winter break** -- devtools submissions during maintenance triggered blocks
6. **MathJax conflicts with R's new math rendering** -- new friction from R's enhanced help system
7. **macOS toolchain updates breaking Fortran** -- gfortran 14.2 required

## Recommendations for Knowledge Base Updates

1. Add rule for "graceful failure must cover downstream code in vignettes/examples"
2. Add rule about Go toolchain packages being practically unacceptable
3. Update tarball size limit from 5MB to 10MB
4. Add warning about R-devel compatibility testing being essential
5. Add note about CRAN winter break timing and devtools interaction
6. Add rule about not removing failing tests as a fix strategy
7. Add rule about cascading dependency archival and sequential resubmission
8. Add note about deprecated dependency monitoring (qs -> qs2 pattern)
