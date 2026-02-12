# Research Report: CRAN Package Rejection Patterns -- 2015 through 2017

Generated: 2026-02-11

## Executive Summary

The 2015-2017 period was one of rapid CRAN growth and progressive tightening of package quality standards. CRAN grew from roughly 6,200 packages (April 2015) to over 10,000 (January 2017), a milestone that intensified pressure on the small CRAN team. Three major R releases defined the era: R 3.2.0 (April 2015) improved URL checking and documentation validation; R 3.3.0 (May 2016) introduced stricter code analysis requiring explicit imports from non-base default packages; and R 3.4.0 (April 2017) mandated native routine registration for packages with compiled code. The R-package-devel mailing list was created in May 2015, providing the first dedicated venue for package developers to seek help with submission issues. Traditional rejection patterns (DESCRIPTION formatting, documentation gaps, writing to user filespace) persisted throughout, while new automated checks progressively caught issues that previously required manual review.

## Research Question

What were the CRAN package rejection patterns from 2015 through 2017? What new checks or policy changes were introduced with R 3.2, 3.3, and 3.4? What verbatim rejection text was used?

## R Version Context

- **R 3.2.0 "Full of Ingredients"** released April 16, 2015 -- URL checking via curlGetHeaders, new --run-dontrun/--run-donttest options, improved DESCRIPTION validation
- **R 3.2.1** released June 18, 2015 (patch)
- **R 3.2.2** released August 14, 2015 (patch)
- **R 3.2.3** released December 10, 2015 (patch)
- **R 3.2.4** released March 10, 2016 (patch)
- **R 3.2.5** released April 14, 2016 (patch)
- **R 3.3.0 "Supposedly Educational"** released May 3, 2016 -- codetools checks with base-only attachment, stricter imports
- **R 3.3.1** released June 21, 2016 (patch)
- **R 3.3.2** released October 31, 2016 (patch)
- **R 3.3.3** released March 6, 2017 (patch)
- **R 3.4.0 "You Stupid Darkness"** released April 21, 2017 -- native routine registration check, JIT compilation by default
- **R 3.4.1** released June 30, 2017 (patch)
- **R 3.4.2** released September 28, 2017 (patch)
- **R 3.4.3** released November 30, 2017 (patch)

## Key Findings

### Finding 1: R 3.2.0 -- URL Checking in R CMD check (April 2015)

R 3.2.0 introduced `curlGetHeaders()`, which retrieves HTTP/HTTPS/FTP headers, and used it in `R CMD check --as-cran` to verify URLs in package documentation. This was a significant new check that caught invalid, redirected, and non-HTTPS URLs in DESCRIPTION, CITATION, NEWS.Rd, README.md, and .Rd help files.

**Impact on packages:**
- Packages with dead links, HTTP-only URLs, or permanently redirected URLs started getting NOTEs and WARNINGs
- Required maintainers to switch from `http://` to `https://` for many URLs
- Canonical URL forms became important (e.g., `https://CRAN.R-project.org/package=pkgname`)

**R CMD check message (examples):**
```
* checking URL(s) ...
  URL: http://example.com
  Status: 301 Moved Permanently
  From: DESCRIPTION

  URL: http://broken-link.example.com
  Status: 404 Not Found
  From: man/foo.Rd
```

**Additional R 3.2.0 check changes:**
- New `--run-dontrun` and `--run-donttest` options for R CMD check, giving CRAN the ability to run `\dontrun{}` and `\donttest{}` examples during checking
- README.md files now processed during check (requires pandoc)
- Non-ASCII characters without declared encoding detected more reliably
- Unregistered S3 methods flagged as NOTE
- Overwriting registered S3 methods from base/recommended packages flagged
- Title field capitalization validated against title case conventions
- `NeedsCompilation` field auto-added by `R CMD build` if missing
- New `--test-dir` option for alternative test directory locations
- `R CMD INSTALL --built-timestamp=STAMP` for reproducible builds

- Source: R 3.2.0 NEWS; R Journal Vol. 7/1 (June 2015); R-bloggers (2015/04/r-3-2-0-is-released)

### Finding 2: R-package-devel Mailing List Created (May 2015)

The R Foundation created the R-package-devel mailing list on May 22, 2015, providing the first dedicated channel for package development help. Prior to this, package developers had to use the general R-devel list or figure out issues on their own.

**Purpose (from announcement):**
- Provide a forum for learning about the package development process
- Build a community of R package developers who can help each other
- Reduce some of the burden on the CRAN maintainers

The mailing list archives from 2015-2019 contain 3,708 emails in 1,104 threads, organized in quarterly archives (2015q2 through present). This list became the primary source for understanding CRAN rejection patterns, as developers routinely posted rejection feedback and sought help.

- Source: R-bloggers (2015/05/the-r-foundation-announces-new-mailing-list-r-package-devel); stat.ethz.ch/mailman/listinfo/r-package-devel

### Finding 3: R 3.3.0 -- Stricter Code Analysis via codetools (May 2016)

R 3.3.0 made a significant change to `R CMD check --as-cran`: code usage analysis (via the `codetools` package) now ran with only the base package attached. Functions from default packages other than base (stats, utils, graphics, grDevices, methods, datasets) that were used in package code but not explicitly imported were reported as undefined globals.

**What it means:**
- Before R 3.3.0: Packages could use `installed.packages()` from utils or `rnorm()` from stats without explicit imports, because these packages were always loaded by default
- After R 3.3.0: Such usage triggers an "undefined global" NOTE unless the function is explicitly imported in the NAMESPACE file

**R CMD check message:**
```
* checking R code for possible problems ... NOTE
foo: no visible global function definition for 'installed.packages'
Consider adding
  importFrom("utils", "installed.packages")
to your NAMESPACE file.
```

**Impact:**
This was one of the most far-reaching changes of the period. Thousands of packages that had worked for years suddenly got NOTEs because they relied on default packages being attached. The fix required either:
1. Adding `importFrom()` directives to the NAMESPACE file
2. Using the `pkg::func()` calling convention
3. Adding `@importFrom pkg func` roxygen2 tags

**Common functions affected:** `str()`, `head()`, `tail()` (from utils); `rnorm()`, `runif()`, `lm()`, `predict()` (from stats); `plot()`, `par()`, `hist()` (from graphics).

- Source: R-devel NEWS (2015/06/29); R Journal Vol. 8/1 (June 2016)

### Finding 4: R 3.4.0 -- Native Routine Registration Requirement (April 2017)

R 3.4.0 introduced the single most impactful check of the 2015-2017 period for packages with compiled code: mandatory registration of native routines.

**Brian Ripley's announcement (February 2017, r-devel):**
> "Shortly, R CMD check --as-cran will note if registration is not fully used. Expect to be asked to add registration."

**R CMD check NOTE:**
```
* checking compiled code ... NOTE
Found no calls to: 'R_registerRoutines', 'R_useDynamicSymbols'
It is good practice to register native routines and to disable symbol search.
```

**What it requires:**
Packages using `.C()`, `.Call()`, `.Fortran()`, or `.External()` interfaces must:
1. Create a `src/init.c` file with registration tables listing all native entry points
2. Add `.registration=TRUE` to the `useDynLib()` directive in NAMESPACE

**Helper function:**
Brian Ripley and Kurt Hornik provided `tools::package_native_routine_registration_skeleton()`, available in R 3.4.0, which auto-generates the registration code by parsing the package's R code to collect all native function entry points.

**How to fix:**
```r
# Generate registration code:
tools::package_native_routine_registration_skeleton(".", "src/init.c")

# Update NAMESPACE:
# Change: useDynLib(mypackage)
# To:     useDynLib(mypackage, .registration = TRUE)
```

**Impact:**
- This was initially a NOTE but was expected to become a WARNING
- Applied to all packages with compiled C/C++/Fortran code
- Rcpp packages were particularly affected; Rcpp versions 0.12.12 and 0.12.13 (2017) added auto-generation support
- Benefits: faster symbol lookup (using tables instead of search), runtime argument count validation, reduced risk of symbol name clashes

**Additional R 3.4.0 check changes:**
- JIT byte-code compiler enabled by default at level 3 (functions compiled on first or second use)
- `R CMD check` verifies `BugReports` field is non-empty and a suitable single URL
- `*.r` files in tests/ directory recognized as tests (previously only `*.R`)
- `R CMD build` prioritizes vignettes/ over inst/doc/ with warnings about the latter
- `R CMD check` verifies inst/doc/ output files are newer than vignettes/ sources
- Environment variables `_R_CHECK_SUGGESTS_ONLY_` and `_R_CHECK_DEPENDS_ONLY_` applied to vignette re-building

- Source: stat.ethz.ch/pipermail/r-devel/2017-February/073755.html; Dirk Eddelbuettel blog (2017/03/29); R-bloggers (2017/03/1-easy-package-registration); ironholds.org/registering-routines; thecoatlessprofessor.com

### Finding 5: Traditional Rejection Patterns (Consistent Throughout 2015-2017)

The traditional rejection reasons documented in 2016-era blog posts and the ThinkR "prepare-for-cran" checklist (created on GitHub during this period) remained the dominant causes of first-submission rejection. These mirror patterns seen in later periods but were codified as community knowledge during 2015-2017.

#### DESCRIPTION Issues

**Software names not in single quotes (2016 blog post, ggnetwork package):**
> "Please single quote software names."

**Title not in title case (2016 blog post):**
> "The mandatory 'Title' field...should use title case (that is, use capitals for the principal words)."

**Software names not properly capitalized (2016 blog post):**
> Required proper capitalization of 'Github', 'Travis-CI', etc. instead of lowercase forms.

**HTTP instead of HTTPS URLs (2016 blog post):**
> Author "used a link with http, should have been https."

**Missing VignetteIndexEntry (2016 blog post, ggnetwork):**
> "Package has a VignetteBuilder field but no prebuilt vignette index."

This occurred when packages included a VignetteBuilder field but failed to include `%\VignetteIndexEntry{}` and `%\VignetteEngine{}` metadata in vignette files.

**Unimported non-base functions (2016 blog post):**
> "no visible global function definition for 'installed.packages'"

The fix required adding `importFrom("utils", "installed.packages")` to NAMESPACE.

#### Code Issues

All the traditional code issues were consistently enforced:
- `T`/`F` instead of `TRUE`/`FALSE`
- `print()`/`cat()` for messages (should use `message()`/`warning()`)
- Hardcoded `set.seed()` in functions
- `options()`/`par()`/`setwd()` not restored with `on.exit()`
- Writing to user filespace (must use `tempdir()`)
- Modifying `.GlobalEnv`
- Using `installed.packages()`
- Using `options(warn = -1)` (must use `suppressWarnings()`)
- Installing packages within functions
- Using more than 2 cores

#### Documentation Issues

- Missing `\value` tags on exported functions
- `\dontrun{}` misuse (should be `\donttest{}` or `if(interactive()){}`)
- All examples wrapped in `\donttest{}`
- Check time exceeding 10 minutes

- Source: R-bloggers (2016/03/submitting-packages-to-cran); R-bloggers (2016/07/submitting-your-first-package-to-cran-my-experience); github.com/ThinkR-open/prepare-for-cran

### Finding 6: Suggested Packages and Vignette Dependencies

During 2015-2017, CRAN tightened enforcement of the "Suggests is not Depends" principle. This became particularly important for vignettes that used Suggested packages.

**The problem:**
- Packages listed in `Suggests` are not guaranteed to be installed
- CRAN runs checks with `_R_CHECK_DEPENDS_ONLY_=true` (the "noSuggests" check)
- Vignettes that called `library(suggested_pkg)` unconditionally failed these checks

**The solution (codified during this period):**
```r
# At the beginning of each vignette:
required <- c("pkg1", "pkg2")
if (!all(sapply(required, requireNamespace, quietly = TRUE)))
  knitr::opts_chunk$set(eval = FALSE)
```

**VignetteBuilder field requirements tightened:**
- If a vignette uses `knitr::rmarkdown` engine, both `knitr` AND `rmarkdown` must be listed in the `VignetteBuilder` field
- Both must also be in `Suggests` (since rmarkdown is only Suggested by knitr, not automatically available)

**R 3.4.0 enforcement:**
`R CMD check` now applied `_R_CHECK_SUGGESTS_ONLY_` and `_R_CHECK_DEPENDS_ONLY_` to vignette re-building, catching more cases where Suggested packages were used unconditionally.

- Source: R-bloggers (2017/03/suggests-and-vignettes); Writing R Extensions manual; R 3.4.0 NEWS

### Finding 7: Memory Access and Sanitizer Checks

Starting around 2016-2017, CRAN expanded its use of AddressSanitizer (ASAN) and valgrind for detecting memory errors in compiled code. Prof. Brian Ripley's machines at Oxford ran these additional checks, which caught issues invisible to standard R CMD check.

**Check infrastructure:**
- `gcc-ASAN`: AddressSanitizer for detecting buffer overflows, use-after-free, etc.
- `gcc-UBSAN`: Undefined Behavior Sanitizer for detecting undefined behavior in C/C++
- `valgrind`: Memory error detection (slower but catches uninitialized memory use)

**Example (vcfR package, 2017):**
```
==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffe1d3c3f83
READ of size 1 at 0x7ffe1d3c3f83
```

**Impact:**
- Packages that passed standard R CMD check on all platforms could still be flagged or archived for ASAN/valgrind errors
- These checks were not available on typical developer machines, making debugging difficult
- Developers had to set up Docker containers with specially-compiled R to reproduce the issues locally
- CRAN sent short-deadline notices (sometimes 1-2 weeks) to fix these issues before archival

**CRAN check pages reported these as:**
- `r-devel-linux-x86_64-debian-gcc` (with ASAN/UBSAN)
- `r-devel-linux-x86_64-fedora-gcc` (with ASAN/UBSAN)
- Additional issue types: `gcc-ASAN`, `gcc-UBSAN`, `valgrind`

- Source: knausb.github.io/2017/06/cran-memory-error; reside-ic.github.io blog posts; CRAN check issue kinds

### Finding 8: Package Size Enforcement (5MB Limit)

Throughout 2015-2017, the CRAN package size limit was 5MB for the source tarball. This was strictly enforced and was a common rejection reason for packages bundling large datasets or vendored libraries.

**CRAN policy (2015 snapshot):**
> "Neither data nor documentation should exceed 5MB. Where a large amount of data is required, consideration should be given to a separate data-only package which can be updated only rarely."

**Common size-related issues:**
- Large CSV/RDA datasets bundled in `data/` or `inst/extdata/`
- High-resolution images in vignettes
- Vendored JavaScript libraries (for htmlwidgets packages)
- Bundled compiled library sources in `src/`

Note: This limit was later raised to 10MB in November 2025.

- Source: CRAN Repository Policy (2015 snapshot via Microsoft CRAN mirror)

### Finding 9: GNU Make and Makevars Portability

CRAN consistently checked for GNU-specific extensions in Makefiles throughout this period. Packages using GNU make features in `src/Makevars` were flagged.

**R CMD check message:**
```
* checking for GNU extensions in Makefiles ... WARNING
Found the following files/directories containing GNU extensions:
  src/Makevars
Portable Makefiles do not use GNU extensions such as +=, :=,
$(shell), $(wildcard), ifeq ... endif.
See section 'Writing portable packages' in the 'Writing R Extensions' manual.
```

**Common violations:**
- `+=` (append to variable)
- `:=` (immediate assignment)
- `$(shell ...)` (command substitution)
- `$(wildcard ...)` (file globbing)
- `ifeq ... endif` (conditionals)
- `#!/bin/bash` instead of `#!/bin/sh` in configure scripts

- Source: Writing R Extensions manual; CRAN Repository Policy

### Finding 10: Cross-Platform Issues and Non-FOSS Licenses

**Platform-specific failures:**
Packages were frequently rejected or archived for failures on specific CRAN check platforms. During 2015-2017, the check infrastructure included:
- `r-devel-linux-x86_64-debian-clang`
- `r-devel-linux-x86_64-debian-gcc`
- `r-devel-linux-x86_64-fedora-clang`
- `r-devel-linux-x86_64-fedora-gcc`
- `r-patched-linux-x86_64` and `r-release-linux-x86_64`
- `r-release-osx-x86_64` (macOS)
- `r-devel-windows-ix86+x86_64` and `r-release-windows-ix86+x86_64`

**Non-FOSS license rejection:**
Packages with non-FOSS (Free and Open Source Software) licenses were rejected outright:
> "Non-FOSS package license (file LICENSE)"

CRAN only accepted licenses from its official license database. This was especially problematic for packages wrapping proprietary software or using custom license terms.

**CMake dependency issues (2017):**
The `cmaker` package was refused from CRAN due to cross-platform issues, specifically Windows portability of CMake dependencies. While 47 CRAN packages already used CMakeLists.txt files, the dependency management approach mattered.

- Source: R-package-devel mailing list (2017q2); CRAN Repository Policy; CRAN package licenses page

### Finding 11: CRAN Growth Pressure and Archival Patterns

**CRAN growth milestones:**
- April 2015: ~6,200 packages
- April 2016: ~8,000 packages
- January 27, 2017: **10,000 packages** milestone reached (at a rate of 6.3 new packages per day)
- Number of maintainers grew from ~5,289 (August 2016) to ~5,845 (January 2017)

**Archival patterns (period-general statistics):**
- 39% of all packages ever on CRAN have been archived at some point
- 64% of archived packages never return
- 36% eventually get unarchived (median return time: ~33 days)
- Top archival reasons: (1) uncorrected check errors (4,366 events historically), (2) dependency failures (767 events), (3) policy violations (<500 events), (4) email/contact issues

**Archival enforcement during major releases:**
> "Packages for which R CMD check gives an 'ERROR' when a new R x.y.0 version is released will be archived unless the maintainer has set a firm deadline for an upcoming update."
>
> "Maintainers will be asked to update packages which show any warnings or significant notes, especially at around the time of a new x.y.0 release."

This meant that each of the three major releases (3.2.0, 3.3.0, 3.4.0) triggered waves of emails to maintainers, followed by archivals of non-responsive packages.

- Source: CRAN Repository Policy; llrs.dev/post/2021/12/07/reasons-cran-archivals; cranhaven.org/cran-archiving-stats.html; R-bloggers (2017/01/cran-now-has-10000-r-packages); rviews.rstudio.com (2017/01/06/10000-cran-packages)

### Finding 12: Graceful Failure for Internet Resources

CRAN continued enforcing the requirement that packages using internet resources must fail gracefully. This was increasingly important as more packages wrapped web APIs.

**CRAN Repository Policy (in effect 2015-2017):**
> "Packages which use Internet resources should fail gracefully with an informative message if the resource is not available or has changed (and not give a check warning nor error)."

**Practical implications:**
- All network calls must be wrapped in `tryCatch()`
- Examples using internet resources should be in `\donttest{}` or `\dontrun{}`
- Tests depending on external services need `skip_on_cran()` or conditional execution
- Vignettes must handle network failures (use precomputed results or conditional execution)

- Source: CRAN Repository Policy

## Recurring Patterns

Based on the research, these were the most frequent rejection/issue categories during 2015-2017, ordered by estimated frequency:

1. **DESCRIPTION formatting** -- Title case, single quotes, acronyms, URLs, Authors@R
2. **Missing \value documentation** -- Universal for first-time submissions
3. **Unimported non-base functions** -- Especially after R 3.3.0 codetools changes
4. **\dontrun{} misuse** -- Should be \donttest{} or if(interactive())
5. **Writing to user filespace** -- Must use tempdir()
6. **Native routine registration** -- NEW in R 3.4.0, affected all packages with compiled code
7. **print()/cat() for messages** -- Must use message()/warning()
8. **URL problems** -- Dead links, HTTP not HTTPS, non-canonical forms (NEW enforcement in R 3.2.0)
9. **options()/par() not restored** -- Must use on.exit()
10. **Package/vignette too slow or too large** -- Time/size limits consistently enforced
11. **Suggested package not used conditionally** -- Tightened enforcement throughout period
12. **Memory safety issues in compiled code** -- ASAN/valgrind checks expanded

## Novel Patterns (New in 2015-2017)

These were new or newly enforced during the 2015-2017 period:

| Pattern | Trigger | R Version | Impact |
|---------|---------|-----------|--------|
| URL checking in packages | curlGetHeaders() integration | R 3.2.0 | All packages with URLs |
| --run-dontrun/--run-donttest options | New check options | R 3.2.0 | Packages relying on dontrun to hide problems |
| S3 method overwrite detection | New check | R 3.2.0 | Packages overwriting base S3 methods |
| Title case validation | New check | R 3.2.0 | All packages |
| Stricter codetools with base-only | Default package detach | R 3.3.0 | Thousands of packages using stats/utils/graphics without imports |
| Native routine registration | New R CMD check NOTE | R 3.4.0 | All packages with .C/.Call/.Fortran/.External |
| BugReports field validation | New check | R 3.4.0 | Packages with malformed BugReports |
| Vignette rebuild with SUGGESTS_ONLY | Environment variable enforcement | R 3.4.0 | Packages with Suggested vignette dependencies |
| JIT compilation by default | Level 3 JIT | R 3.4.0 | Some packages with timing-sensitive code |
| ASAN/UBSAN expanded checks | Additional check infrastructure | ~2016-2017 | Packages with compiled code and memory bugs |

## Timeline of Key Events

| Date | Event |
|------|-------|
| April 16, 2015 | R 3.2.0 released: URL checking, --run-dontrun, improved DESCRIPTION validation |
| May 22, 2015 | R-package-devel mailing list created |
| May 3, 2016 | R 3.3.0 released: codetools checks with base-only attachment |
| February 2017 | Brian Ripley announces native routine registration check on r-devel |
| January 27, 2017 | CRAN reaches 10,000 packages |
| March 2017 | tools::package_native_routine_registration_skeleton() announced |
| April 21, 2017 | R 3.4.0 released: native routine registration NOTE, JIT by default |

## Comparison with Current Knowledge Base

### Already Well-Covered

The existing knowledge base covers the following patterns that were active during 2015-2017:

- **DESC-01 through DESC-15**: All DESCRIPTION formatting rules were in effect and actively enforced
- **CODE-01 through CODE-14**: All code behavior rules apply
- **DOC-01 through DOC-05**: Documentation rules (missing \value, \dontrun misuse, examples)
- **LIC-01 through LIC-03**: License rules
- **SIZE-01, SIZE-02**: Size and performance limits (note: 5MB limit in this period, now 10MB)
- **PLAT-01, PLAT-02**: Cross-platform requirements
- **DEP-01, DEP-02**: Dependency rules
- **NET-01, NET-02**: Internet resource graceful failure

### Patterns from 2015-2017 NOT Currently in Knowledge Base

The following patterns were significant during 2015-2017 but are not explicitly covered as historical rules:

1. **Native routine registration (R 3.4.0)**: The requirement for `R_registerRoutines` / `R_useDynamicSymbols` in `src/init.c` and `.registration=TRUE` in NAMESPACE is not documented as a rule. While largely resolved by modern Rcpp and roxygen2, legacy packages still need this.

2. **Codetools undefined globals (R 3.3.0)**: The requirement to explicitly import from non-base default packages is implicitly covered by good NAMESPACE practice but not called out as a historical transition that broke thousands of packages.

3. **ASAN/UBSAN/valgrind additional checks**: The existence and impact of these additional memory safety checks is not documented. Packages can pass all standard checks but fail these.

4. **VignetteBuilder field requiring both knitr and rmarkdown**: The specific requirement that `knitr::rmarkdown` engine vignettes need both packages in VignetteBuilder is not documented.

### Recommendations for Knowledge Base Updates

1. **Consider adding a COMP rule for native routine registration**: While this is largely automated now, packages migrating from pre-2017 code may still lack registration. The check message "Found no calls to: 'R_registerRoutines', 'R_useDynamicSymbols'" could be documented.

2. **Consider adding a DEP rule for vignette builder declarations**: Incomplete VignetteBuilder fields (missing rmarkdown when using knitr::rmarkdown) continue to cause issues.

3. **Note historical context for SIZE-01**: The 5MB limit was in effect during this period; the current 10MB limit is a 2025 change.

4. **COMP rules about ASAN/UBSAN**: Document that CRAN runs additional memory safety checks beyond standard R CMD check, and packages with compiled code should be tested with sanitizers before submission.

## CRAN Infrastructure Notes

During 2015-2017, the CRAN check infrastructure was less standardized than today:
- Win-builder was the primary Windows check service (r-hub did not yet exist; it launched in 2019)
- macOS checks used x86_64 only (M1/ARM not yet relevant)
- ASAN/UBSAN checks ran on specific Fedora and Debian flavors
- The CRAN team (Kurt Hornik, Uwe Ligges, Brian Ripley, and others) managed submission reviews largely manually
- Submission delays and "lost" submissions were reported on the mailing list (e.g., jtools v0.6.0 in August 2017)

## Open Questions

1. **Exact archival counts per year for 2015-2017**: The detailed year-by-year archival statistics are not available from public sources. The Kaggle "R Package History on CRAN" dataset or the CRAN archive history file would need to be analyzed.

2. **eddelbuettel/crp policy diffs for 2015-2017**: The CRAN Repository Policy Watch repository has commits from this period but the specific commit messages from 2015-2017 were not accessible in the current GitHub pagination (oldest visible commits start from January 2018).

3. **R 3.3.0 codetools impact numbers**: While we know the change affected "thousands" of packages, exact numbers of packages that received the undefined globals NOTE after R 3.3.0 are not publicly documented.

4. **Exact date the native routine registration NOTE became a WARNING**: Brian Ripley indicated the NOTE would "presumably turn into a WARNING at some point" but the exact timeline is unclear.

5. **First-time submission rejection rate during this period**: The 35% first-time rejection rate documented by llrs.dev covers 2020-2024. Whether the rate was higher or lower during 2015-2017 is unknown.

## Sources

- R-package-devel mailing list archives: https://stat.ethz.ch/pipermail/r-package-devel/ (2015q2 through 2017q4)
- Mail Archive mirror: https://www.mail-archive.com/r-package-devel@r-project.org/
- R 3.2.0 release announcement: https://www.r-bloggers.com/2015/04/r-3-2-0-is-released-using-the-installr-package-to-upgrade-in-windows-os/
- R 3.4.0 release announcement: https://stat.ethz.ch/pipermail/r-announce/2017/000612.html
- R Journal "Changes in R" (Vol 7/1, June 2015): https://journal.r-project.org/news/RJ-2015-1-r-changes/
- R Journal "Changes in R" (Vol 8/1, June 2016): https://journal.r-project.org/news/RJ-2016-1-r-changes/
- R Journal "Changes in R" (Vol 9/1, June 2017): https://journal.r-project.org/news/RJ-2017-1-ch/
- Brian Ripley on native routine registration (r-devel, February 2017): https://stat.ethz.ch/pipermail/r-devel/2017-February/073755.html
- Dirk Eddelbuettel -- Easy Package Registration: http://dirk.eddelbuettel.com/blog/2017/03/29/
- Registering Routines with Rcpp (ironholds.org): https://ironholds.org/registering-routines/
- TheCoatlessProfessor -- Registration of Entry Points: https://thecoatlessprofessor.com/programming/r/registration-of-entry-points-in-compiled-code-loaded-into-r/
- R-bloggers -- Submitting packages to CRAN (March 2016): https://www.r-bloggers.com/2016/03/submitting-packages-to-cran/
- R-bloggers -- Submitting your first package to CRAN (July 2016): https://www.r-bloggers.com/2016/07/submitting-your-first-package-to-cran-my-experience/
- R-bloggers -- Suggests and Vignettes (March 2017): https://www.r-bloggers.com/2017/03/suggests-and-vignettes/
- CRAN now has 10,000 packages (January 2017): https://blog.revolutionanalytics.com/2017/01/cran-10000.html
- 10,000 CRAN Packages (R Views): https://rviews.rstudio.com/2017/01/06/10000-cran-packages/
- On the growth of CRAN packages (April 2016): https://www.r-bloggers.com/2016/04/on-the-growth-of-cran-packages/
- ThinkR prepare-for-cran: https://github.com/ThinkR-open/prepare-for-cran
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
- CRAN Repository Policy (May 2015 snapshot): https://cran.microsoft.com/snapshot/2015-05-11/web/packages/policies.html
- eddelbuettel/crp (CRAN Repository Policy Watch): https://github.com/eddelbuettel/crp
- Reasons why packages are archived on CRAN: https://llrs.dev/post/2021/12/07/reasons-cran-archivals/
- CRANhaven archiving statistics: https://www.cranhaven.org/cran-archiving-stats.html
- CRAN memory error debugging (vcfR, 2017): https://knausb.github.io/2017/06/cran-memory-error/
- CRAN Package Check Issue Kinds: https://cran.r-project.org/web/checks/check_issue_kinds.html
- CRAN URL checks: https://cran.r-project.org/web/packages/URL_checks.html
- Writing R Extensions manual: https://cran.r-project.org/doc/manuals/r-release/R-exts.html
- R NEWS (historical): https://cran.r-project.org/doc/manuals/r-release/NEWS.3.html
- noSuggests check: https://www.stats.ox.ac.uk/pub/bdr/noSuggests/
- R-hub blog -- How to keep up with CRAN policies: https://blog.r-hub.io/2019/05/29/keep-up-with-cran/
- MichaelChirico/r-devel-archive (mailing list archive): https://github.com/MichaelChirico/r-devel-archive
