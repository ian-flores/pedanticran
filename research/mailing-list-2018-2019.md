# Research Report: CRAN Package Rejection Patterns -- 2018 through 2019

Generated: 2026-02-11

## Executive Summary

The 2018-2019 period was shaped by two major R releases: R 3.5.0 (April 2018) and R 3.6.0 (April 2019). The most significant package-breaking changes were: (1) serialization format v3 introduction (R 3.5) and its promotion to default (R 3.6), which silently added `Depends: R (>= 3.5.0)` to packages with regenerated data files; (2) staged installation (R 3.6), which broke 48 CRAN/Bioconductor packages that cached paths at load time; (3) `\Sexpr{}` evaluation in R CMD check (R 3.6), which caught previously-invisible documentation issues; and (4) expanded vignette and data directory checks. Traditional rejection patterns (DESCRIPTION formatting, `\dontrun` misuse, writing to user filespace, missing `\value` tags) remained the dominant reasons for first-time submission rejections. CRAN grew from approximately 12,600 active packages to over 15,200 during this period, with an average of 21 new or updated submissions per day.

## Research Question

What were the CRAN package rejection patterns from 2018 through 2019? What new checks or policy changes were introduced with R 3.5.0 and R 3.6.0? What verbatim rejection text was used?

## R Version Context

- **R 3.4.4 "Someone to Lean On"** was the latest 3.4.x release (March 2018)
- **R 3.5.0 "Joy in Playing"** was released April 23, 2018 -- major release with ALTREP, serialization v3, default byte-compilation
- **R 3.5.1** (July 2018), **R 3.5.2** (December 2018), **R 3.5.3** (March 2019) -- patch releases
- **R 3.6.0 "Planting of a Tree"** was released April 26, 2019 -- major release with staged installation, serialization v3 as default, delayed S3 registration
- **R 3.6.1** (July 2019), **R 3.6.2** (December 2019) -- patch releases

## Key Findings

### Finding 1: Serialization Format v3 -- Silent Dependency Bumps

R 3.5.0 introduced serialization format version 3, which supports custom serialization of ALTREP framework objects and records the current native encoding of unflagged strings. While format 2 remained the default in R 3.5.x, R 3.6.0 changed the default to format 3.

**Impact on packages:**

Any package that had its `.rda`, `.rds`, or `.RData` files regenerated under R 3.6.0+ would silently have those files written in format 3. When such a package was then built (e.g., for CRAN submission), R CMD build would automatically add `Depends: R (>= 3.5.0)` because serialized data in format 3 cannot be read by older R versions.

**Verbatim R CMD check/build message:**
```
NB: this package now depends on R (>= 3.5.0)
WARNING: Added dependency on R >= 3.5.0 because serialized objects in
serialize/load version 3 cannot be read in older versions of R.
```

**Scope:** This affected every package that included bundled data files and was rebuilt under R 3.6.0. Packages with large data components were especially impacted. The issue was subtle because package maintainers might not have intentionally changed their data files -- simply re-running `usethis::use_data()` or `save()` under the new R version was enough.

**Fix:**
- Explicitly use `version = 2` when saving data: `saveRDS(obj, file, version = 2)` or `save(obj, file = "data/mydata.rda", version = 2)`
- Use `tools::resaveRdaFiles("data/")` which defaults to version 2 unless the file is already in version 3
- For maximal backward compatibility, R CMD build already generates `vignette.rds` and `partial.rdb` in version 2

**Real case -- ggstatsplot (May 2018):**
- Package had `iris_long.rdata` saved in format 3
- Got the WARNING during devtools::check()
- Maintainer was confused whether to manually update DESCRIPTION's Depends field

- Source: devtools issue #1912; R 3.5.0 NEWS; R 3.6.0 NEWS

### Finding 2: Staged Installation -- Load-Time Side Effects Break Packages

R 3.6.0 introduced staged installation as the default. Under staged installation, packages are first installed to a temporary directory, then moved to the final library location after installation completes.

**What it breaks:**

Packages that cache absolute paths during installation or namespace loading break because the paths they saved point to the temporary directory, which no longer exists after the move.

**Common failure patterns:**

1. **Hard-coded paths in R code** -- Packages that call `system.file()` at the top level of an R source file and save the result:
```r
# BROKEN: saves temporary path during installation
globals$DB_PATH <- system.file("extdata", "pd.ecoli.sqlite",
                               package="pd.ecoli")
```

2. **Hard-coded paths in shared objects** -- Packages that embed absolute installation paths via linker rpath settings in compiled code

**Impact:** 48 packages failed to install with staged installation but worked with non-staged installation (21 CRAN + 4 Bioconductor packages with hard-coded R code paths; 2 CRAN + 2 Bioconductor packages with hard-coded shared object paths).

**Verbatim error pattern:**
```
ERROR: installation of package 'PKGNAME' had non-zero exit status
```
With further investigation revealing that `system.file()` returns paths under the temporary staging directory.

**Platforms affected:** Linux, Solaris, macOS (not Windows, which does not use staged installation in the same way).

**Fix for R code paths:**
```r
# FIXED: compute path at runtime
getDbPath <- function() system.file("extdata", "pd.ecoli.sqlite",
                                    package="pd.ecoli")
```

**Fix for shared object paths:** Use static linking or symbolic dynamic linker variables like `$ORIGIN` (Linux/Solaris) or `@loader_path` (macOS).

**Opt-out:** Add `StagedInstall: no` to DESCRIPTION, or use `--no-staged-install` flag, or set `R_INSTALL_STAGED=false`.

**Real cases:**
- `later` package (r-lib/later#93): staged install failure on R >= 3.6.0
- `Rblpapi` package (Rblp/Rblpapi#290): staged install failure requiring workaround
- `MBSStools` package (leppott/MBSStools#27): install failure on R 3.6.0
- `pd.ecoli` and similar Bioconductor annotation packages with top-level `system.file()` calls

- Source: R Blog "Staged Install" (blog.r-project.org/2019/02/14/staged-install/); R 3.6.0 NEWS

### Finding 3: Default Byte-Compilation on Installation (R 3.5.0)

R 3.5.0 changed the default so that all packages are byte-compiled on installation.

**Verbatim NEWS:**
```
All packages are by default byte-compiled on installation. This makes
the installed packages larger (usually marginally so) and may affect
the format of messages and tracebacks.
```

**Impact on CRAN packages:**
- Installed package sizes increased (usually marginally)
- Packages that relied on specific message or traceback formatting could break
- The byte-compilation step added time to package installation, which affected packages that were already near the CRAN check time limit
- Byte-compilation requires lazy loading, so packages that did not use lazy loading could encounter issues

### Finding 4: ALTREP Framework and Compact Sequences (R 3.5.0)

R 3.5.0 introduced the ALTREP (Alternative Representations) framework, making integer sequences like `1:n`, `seq_along()`, and `seq_len()` use compact internal representations.

**Verbatim NEWS:**
```
Arithmetic sequences created by 1:n, seq_along, and the like now use
compact internal representations via the ALTREP framework.
```

**Impact on packages:**
- Packages with C/C++ code that directly manipulated R vector internals (SEXP structures) could break if they assumed traditional vector layouts
- The `data.table` package reported that interaction of multiple threads operating on ALTREP compact vectors could cause R's garbage collector to malfunction, leading to memory explosion
- Packages using `NAMED` or `SET_NAMED` in C code needed to switch to `MAYBE_REFERENCED`, `MAYBE_SHARED`, and `MARK_NOT_MUTABLE` macros
- `Writing R Extensions` was updated to document these new macros

### Finding 5: \Sexpr{} Evaluation in R CMD check (R 3.6.0)

R 3.6.0 added evaluation of `\Sexpr{}` expressions in Rd files before checking their contents.

**Verbatim NEWS:**
```
R CMD check now evaluates \Sexpr{} expressions (including those in macros)
before checking the contents of 'Rd' files and so detects issues both
in evaluating the expressions and in the expanded contents.
```

**Impact:** Packages using dynamic content in Rd documentation (via `\Sexpr{}`) were now checked for both evaluation errors and the validity of the expanded output. Previously, only the unexpanded Rd source was checked, masking issues in the generated content. Packages using the `lifecycle` package's badge macros were particularly affected, as these rely on `\Sexpr[stage=install]{...}` to insert badge images.

**Related check message:**
```
Package has help file(s) containing install/render-stage \Sexpr{}
expressions but no prebuilt PDF manual.
```

### Finding 6: Expanded R CMD check Checks (R 3.5.0 and R 3.6.0)

Both major releases added new R CMD check validations:

#### R 3.5.0 New Checks

**Vignette dependency checking:**
```
R CMD check now also applies the settings of environment variables
_R_CHECK_SUGGESTS_ONLY_ and _R_CHECK_DEPENDS_ONLY_ to the re-building
of vignettes.
```
This meant packages whose vignettes used Suggested packages without proper conditional checks would fail the "noSuggests" test.

**Timeout support:**
```
It is now possible to set 'timeouts' (elapsed-time limits) for most
parts of R CMD check via environment variables.
```
CRAN began using these to enforce time limits on checks more precisely.

**CRLF line endings in shell scripts:**
```
R CMD check checks for and R CMD build corrects CRLF line endings in
shell scripts 'configure' and 'cleanup' (even on Windows).
```

**Temporary directory detritus:**
```
R CMD check has a new option to mitigate checks leaving files/directories
in '/tmp', which is part of --as-cran.
```

#### R 3.6.0 New Checks

**Comprehensive data directory checks:**
```
R CMD check has more comprehensive checks on the 'data' directory and
the functioning of data() in a package.
```

**Vignette improvements:**
```
R CMD check now tries re-building all vignettes rather than stopping
at the first error: whilst doing so it adds 'bookmarks' to the log.
```

**Duplicated vignette titles:**
```
R CMD check now checks for duplicated vignette titles (also known as
'index entries'): they are used as hyperlinks on CRAN package pages
and so do need to be unique.
```

**Line endings for C++ headers:**
```
R CMD check now checks line endings of files with extension '.hpp' and
those under 'inst/include'. The check now includes that a non-empty
file is terminated with a newline.
```

**Configure file source verification:**
```
R CMD check now checks autoconf-generated 'configure' files have their
corresponding source files, including optionally attempting to
regenerate them on platforms with autoreconf.
```

**OpenMP macro checking:**
```
R CMD check now optionally checks makefiles for correct and portable
use of the SHLIB_OPENMP_*FLAGS macros.
```

### Finding 7: Delayed S3 Method Registration (R 3.6.0)

R 3.6.0 introduced a major new NAMESPACE feature: delayed S3 method registration using `S3method()` directives.

**Verbatim NEWS:**
```
S3method() directives in 'NAMESPACE' can now also be used to perform
delayed S3 method registration.
```

**What this means:** Packages can now register S3 methods for generics from Suggested (not Imported) packages. The method is only registered when the suggested package's namespace is loaded. The NAMESPACE syntax is:
```
if (getRversion() >= "3.6.0") {
  S3method(pkg::generic, class)
}
```

**Impact on CRAN packages:**
- Packages no longer needed to hard-depend on packages just to provide S3 methods for their generics
- The `vctrs` package introduced `s3_register()` as a backport for packages needing to support R < 3.6.0
- Reduced the Imports burden for many packages, especially tidyverse-adjacent ones
- CRAN began noting when S3 method registrations overwrote previous registrations: "When loading namespaces, S3 method registrations which overwrite previous registrations are now noted by default"

### Finding 8: URL Checking and Canonical CRAN URLs

During 2018-2019, CRAN's URL checking became increasingly strict. R CMD check --as-cran validates URLs in DESCRIPTION, CITATION, NEWS.Rd, NEWS.md, README.md, and Rd help pages.

**Verbatim R CMD check message:**
```
Found the following (possibly) invalid URLs:
  URL: https://example.com/old-page
    From: man/function.Rd
    Status: 404
    Message: Not Found
```

**Canonical CRAN URL enforcement (2019):**
Packages were expected to use the canonical form for CRAN package links:
```
https://CRAN.R-project.org/package=pkgname
```
Non-canonical forms (e.g., `https://cran.r-project.org/web/packages/pkgname/index.html`) triggered NOTEs.

**Real case -- data.table (April 2018):**
- Submission flagged for invalid URLs returning 404 from Nabble forum links
- Category: Documentation / URL validity

### Finding 9: Solaris Check Failures

During 2018-2019, CRAN continued testing packages on Oracle Solaris 10 using Oracle Developer Studio (ODS) and GCC compilers. Solaris-specific failures were a persistent source of frustration for package maintainers.

**Common Solaris issues:**
- Different compiler behavior (ODS vs GCC) causing compilation failures
- Segfaults in unit tests that did not occur on Linux or macOS
- Linker differences affecting shared object loading
- `rpath` issues exacerbated by staged installation (R 3.6.0)

**Real case -- rvinecopulib (August 2018):**
- Package compiled successfully but produced a segfault in unit tests on Solaris only
- Threatened with removal unless Solaris errors were corrected
- No reproduction possible on other platforms

**CRAN's typical communication:**
```
Dear maintainer,

package [PKGNAME] has issues with the current CRAN checks that need
to be fixed before [DATE].

Please find the results at:
https://cran.r-project.org/web/checks/check_results_[PKGNAME].html

Best,
[CRAN team member]
```

### Finding 10: Continued Traditional Rejection Patterns

The most common rejection reasons during 2018-2019 remained the traditional patterns that have persisted across all eras. Based on the ThinkR "prepare-for-cran" collaborative checklist and the R-package-devel mailing list discussions:

#### DESCRIPTION Issues

**Software names not in single quotes:**
> "Please always write package names, software names and API (application programming interface) names in single quotes in title and description."

**Title not in title case:**
> "The Title field should be in title case."

**Redundant text in title:**
> "Please remove 'in R' / 'with R' / 'A package for' from the title."

**Unexplained acronyms:**
> "Please always explain all acronyms in the description text."

**Missing Authors@R with cph role:**
CRAN expects the `cph` (copyright holder) role in Authors@R.

**DOI/URL formatting:**
> "Please add these in the description field...in the form <doi:...> with no space after 'doi:' and angle brackets for auto-linking."

#### Documentation Issues

**Missing \value tags:**
> "Please add \value to .Rd files regarding exported methods and explain the functions results in the documentation."
> "If a function does not return a value, please document that too, e.g., \value{No return value, called for side effects}"

**\dontrun{} misuse:**
> "\dontrun{} should only be used if the example really cannot be executed (e.g., because of missing additional software, missing API keys, ...) by the user."
> "Please replace \dontrun with \donttest."
> "Please unwrap the examples if they are executable in < 5 sec."

**All examples wrapped:**
> "All your examples are wrapped in \donttest{} and therefore do not get tested. Please unwrap the examples if that is feasible."

**No @noRd on undocumented internal functions:**
Internal functions with partial documentation need the `@noRd` roxygen2 tag.

#### Code Issues

**Writing to user filespace:**
> "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies."

**print()/cat() for messages:**
> "Instead of print()/cat() rather use message()/warning() or if(verbose)cat(..) if you really have to write text to the console."

**options()/par() not restored:**
> "Please make sure that you do not change the user's options, par or working directory. If you really have to do so within functions, please ensure with an immediate call of on.exit() that the settings are reset when the function is exited."

**T/F instead of TRUE/FALSE:**
> "Please write TRUE and FALSE instead of T and F."

**set.seed() in functions:**
> "Please do not set a seed to a specific number within a function."

**Examples exceeding time limit:**
> (NOTE) "Overall checktime 20 min > 10 min"

Individual examples were expected to run in under 5-10 seconds CPU time.

**Automated rejection email:**
> "package [your package] does not pass the incoming checks automatically, please see the following pre-tests:"

### Finding 11: Internet Resource Graceful Failure

The CRAN Repository Policy requirement for graceful failure when internet resources are unavailable was actively enforced during 2018-2019:

> "Packages which use Internet resources should fail gracefully with an informative message if the resource is not available or has changed (and not give a check warning nor error)."

Packages wrapping web APIs were particularly targeted. The enforcement pattern was:
1. CRAN detects check failure when API is unavailable
2. Maintainer receives email with short deadline (sometimes 1-2 weeks)
3. Package archived if not fixed in time

**Best practice pattern:**
```r
result <- tryCatch(
  download.file(url, destfile, quiet = TRUE),
  error = function(e) {
    message("Internet resource not available: ", conditionMessage(e))
    return(NULL)
  }
)
```

### Finding 12: download.file() Default Method Change (R 3.6.0)

R 3.6.0 changed the default download method:

**Verbatim NEWS:**
```
download.file() on Windows now uses URLdecode() to determine the file
extension, and uses binary transfer (mode = "wb") also for file
extension '.rds'.
```

The default method for `download.file()` and `url()` changed to prefer `"libcurl"` except for `file://` URLs. This affected packages that relied on the previous default behavior (typically `"wininet"` on Windows or `"internal"` on Unix).

**Impact:** Packages that depended on specific HTTP behavior of the old default method (e.g., cookie handling, redirect behavior, SSL certificate verification) could break silently. Packages downloading `.rds` files on Windows now got proper binary transfer by default, fixing a class of subtle data corruption bugs.

### Finding 13: Compiler and Platform Issues (GCC 9, Late 2019)

In November 2019, CRAN began testing packages against GCC 9.2.1 and Clang 9.0.0 on Debian. This introduced new compiler warnings that affected packages with C/C++ code.

**Affected platforms:**
- `r-devel-linux-x86_64-debian-clang`
- `r-devel-linux-x86_64-debian-gcc`

Packages with compiled code that triggered new warnings under GCC 9 or Clang 9 received ERROR results on these platforms. Package maintainers were given short deadlines to fix issues or face archival.

## CRAN Statistics

### Package Counts

| Date | Active Packages | Source |
|------|----------------|--------|
| 2018-06-30 | ~12,582 | R Journal RJ-2018-1 |
| 2019-12-31 | ~15,227 | R Journal RJ-2019-2 |

### Submissions and Archivals

**2018 H1 (approx. Jan-Jun 2018):**
- 1,178 new packages added
- 493 packages archived
- 18 packages unarchived
- 0 packages permanently removed
- CRAN received approximately 2,122 submissions in June 2018 alone
- Average of 21 new/updated submissions per day

**2019 H2 (approx. Aug-Dec 2019):**
- 632 new packages added
- 182 packages archived
- 27 packages unarchived

## Recurring Patterns

Based on the research, these were the most frequent rejection/issue categories during 2018-2019, ordered by estimated frequency:

1. **DESCRIPTION formatting** -- Title case, single quotes around package names, acronyms, DOI formatting, Authors@R with cph
2. **Missing \value documentation** -- Nearly universal for first-time submissions
3. **\dontrun{} misuse** -- Should be \donttest{} or if(interactive())
4. **Writing to user filespace** -- Must use tempdir()
5. **Serialization format v3 dependency** -- Silent R >= 3.5.0 dependency added (NEW in this period)
6. **print()/cat() for messages** -- Must use message()/warning()
7. **options()/par() not restored** -- Must use on.exit()
8. **Internet resource graceful failure** -- Must handle unavailable URLs
9. **Examples too slow / all wrapped** -- Must have unwrapped executable examples
10. **Staged installation failures** -- system.file() cached at load time (NEW in this period)

## Novel Patterns (New in 2018-2019)

These were new or newly enforced during 2018-2019:

| Pattern | Trigger | Impact |
|---------|---------|--------|
| Serialization v3 dependency bump | R 3.5.0 (format introduced), R 3.6.0 (default changed) | Any package with bundled data rebuilt under R 3.6.0 |
| Staged installation failures | R 3.6.0 default staged install | 48 CRAN/Bioconductor packages |
| \Sexpr{} evaluation in R CMD check | R 3.6.0 new check | Packages with dynamic Rd content |
| Default byte-compilation | R 3.5.0 default change | All packages (increased install size/time) |
| ALTREP compact sequences | R 3.5.0 new framework | Packages with C code manipulating vector internals |
| Delayed S3 method registration | R 3.6.0 new NAMESPACE feature | Opportunity to reduce Imports dependencies |
| Duplicated vignette titles check | R 3.6.0 new check | Packages with multiple vignettes |
| Data directory comprehensive check | R 3.6.0 expanded check | Packages with non-standard data/ contents |
| CRLF line endings in configure/cleanup | R 3.5.0 new check | Packages developed on Windows with shell scripts |
| Vignette dependency checking | R 3.5.0 expanded check | Packages using Suggests in vignettes without conditional checks |
| Canonical CRAN URL enforcement | ~2019 | Packages with non-canonical CRAN links |
| GCC 9 / Clang 9 compiler warnings | Late 2019 | Packages with compiled C/C++ code |
| download.file() default change | R 3.6.0 | Packages relying on old download behavior |
| Line ending checks for .hpp files | R 3.6.0 new check | Packages with C++ headers |
| autoconf configure source verification | R 3.6.0 new check | Packages with configure scripts |

## CRAN Infrastructure Notes

### Check Platforms (2018-2019)

CRAN maintained check results across multiple platforms ("flavors"):
- `r-devel-linux-x86_64-debian-clang`
- `r-devel-linux-x86_64-debian-gcc`
- `r-devel-windows-ix86+x86_64`
- `r-patched-linux-x86_64`
- `r-patched-solaris-x86`
- `r-release-linux-x86_64`
- `r-release-windows-ix86+x86_64`
- `r-release-osx-x86_64`
- `r-oldrel-windows-ix86+x86_64`
- `r-oldrel-osx-x86_64`

### CRAN Archive Snapshots

Starting February 2018, CRAN began preserving snapshots of check results pages at the time of package archival, available at `https://cran-archive.r-project.org/web/checks/`.

### Additional Checks Infrastructure

Brian Ripley's infrastructure at Oxford continued running "additional checks" including:
- `_R_CHECK_DEPENDS_ONLY_=true` (noSuggests check)
- `_R_CHECK_SUGGESTS_ONLY_=true`
- Address sanitizer (ASAN) and undefined behavior sanitizer (UBSAN) checks
- Valgrind memory analysis

These were not visible through standard R CMD check and caused unexpected failures for maintainers who had passing checks locally.

## Recommendations for Knowledge Base Updates

Based on this research, the following should be added or updated in the pedanticran knowledge base:

### New Rules to Add

1. **SERIAL-01: Serialization Format v3 Dependency** (R 3.5.0+/R 3.6.0+)
   - Severity: WARNING
   - Verbatim: `WARNING: Added dependency on R >= 3.5.0 because serialized objects in serialize/load version 3 cannot be read in older versions of R.`
   - Detection: Check .rda/.rds files for serialization version; compare against declared R dependency
   - Fix: Use `version = 2` in save/saveRDS calls, or explicitly declare `Depends: R (>= 3.5.0)`

2. **INSTALL-01: Staged Installation Compatibility** (R 3.6.0+)
   - Severity: ERROR
   - Detection: Check for top-level `system.file()` calls saved to variables at package level; check .onLoad() for path caching
   - Fix: Replace cached paths with function calls that compute paths at runtime

3. **DOC-10: \Sexpr{} Evaluation Errors** (R 3.6.0+)
   - Severity: ERROR or WARNING
   - Detection: Evaluate \Sexpr{} expressions in Rd files for errors
   - Fix: Ensure all \Sexpr{} expressions evaluate cleanly

4. **DOC-11: Duplicated Vignette Titles** (R 3.6.0+)
   - Severity: NOTE
   - Detection: Compare VignetteIndexEntry values across vignettes
   - Fix: Ensure each vignette has a unique title

5. **BUILD-01: CRLF Line Endings in Shell Scripts** (R 3.5.0+)
   - Severity: NOTE
   - Detection: Check configure and cleanup scripts for CRLF line endings
   - Fix: Convert to LF line endings

### Rules to Update

1. **Existing data compression rules**: Note that `tools::resaveRdaFiles()` defaults to version 2 serialization for backward compatibility
2. **Existing vignette rules**: Note that R 3.5.0+ applies `_R_CHECK_DEPENDS_ONLY_` to vignette rebuilding
3. **Existing URL rules**: Add canonical CRAN URL format requirement `https://CRAN.R-project.org/package=pkgname`

## Open Questions

1. **Exact archival counts for 2018 H2 and 2019 H1:** The R Journal articles for these periods (RJ-2018-2 and RJ-2019-1) were not fully extractable from this research. The H1 2018 figure of 493 archivals and the H2 2019 figure of 182 archivals are confirmed.

2. **CRAN policy diff for 2018-2019:** The eddelbuettel/crp GitHub repository tracks all policy changes via SVN mirroring, but specific diffs for this period were not extracted. The repository is available for detailed inspection.

3. **Encoding check changes:** R 3.5.0's serialization format v3 improved encoding handling (recording native encoding of unflagged strings), but the exact impact on CRAN check encoding warnings is unclear. The broader UTF-8 standardization effort was still underway during this period.

4. **Submission rejection rate for this period specifically:** The llrs.dev analysis covering Sep 2020 - Jan 2024 shows 35% first-time rejection rate and 14.5% overall rejection rate, but period-specific rates for 2018-2019 are not available.

5. **R 3.6.0 `import(, except=)` support:** While R 3.6.0 appears to have formalized the `except` argument for `import()` NAMESPACE directives, the exact impact on CRAN packages is unclear.

## Sources

- R 3.5.0 announcement: https://stat.ethz.ch/pipermail/r-announce/2018/000628.html
- R 3.5.0 NEWS: https://www.r-statistics.com/2018/04/r-3-5-0-is-released-major-release-with-many-new-features/
- R 3.6.0 announcement: https://stat.ethz.ch/pipermail/r-announce/2019/000641.html
- R 3.6.0 NEWS: https://cran-archive.r-project.org/bin/windows/base/old/3.6.0/NEWS.R-3.6.0.html
- R NEWS (all versions): https://cran.r-project.org/doc/manuals/r-release/NEWS.3.html
- R Blog -- Staged Install: https://blog.r-project.org/2019/02/14/staged-install/
- R Blog -- S3 Method Lookup: https://blog.r-project.org/2019/08/19/s3-method-lookup/
- devtools issue #1912 (serialization v3): https://github.com/r-lib/devtools/issues/1912
- DataPackageR issue #75 (serialization v3): https://github.com/ropensci/DataPackageR/issues/75
- later issue #93 (staged install): https://github.com/r-lib/later/issues/93
- Rblpapi issue #290 (staged install): https://github.com/Rblp/Rblpapi/issues/290
- MBSStools issue #27 (staged install): https://github.com/leppott/MBSStools/issues/27
- R-package-devel mailing list archives: https://stat.ethz.ch/pipermail/r-package-devel/ (2018q1-2019q4)
- Mail Archive mirror: https://www.mail-archive.com/r-package-devel@r-project.org/
- R-hub blog -- How to keep up with CRAN policies: https://blog.r-hub.io/2019/05/29/keep-up-with-cran/
- R-hub blog -- How to get help with R package development: https://blog.r-hub.io/2019/04/11/r-package-devel/
- R-hub blog -- CRAN checks: https://blog.r-hub.io/2019/04/25/r-devel-linux-x86-64-debian-clang/
- R-hub blog -- URL checks: https://blog.r-hub.io/2020/12/01/url-checks/
- ThinkR prepare-for-cran: https://github.com/ThinkR-open/prepare-for-cran
- JEFworks blog -- Get your R package on CRAN: https://jef.works/blog/2018/06/18/get-your-package-on-cran-in-10-steps/
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
- CRAN Repository Policy Watch (eddelbuettel/crp): https://github.com/eddelbuettel/crp
- CRAN Cookbook: https://contributor.r-project.org/cran-cookbook/
- R Journal "Changes on CRAN" (RJ-2018-1): https://journal.r-project.org/news/RJ-2018-1-cran/
- R Journal "Changes on CRAN" (RJ-2019-2): https://journal.r-project.org/news/RJ-2019-2-cran/
- llrs.dev CRAN submission statistics: https://llrs.dev/post/2024/01/10/submission-cran-first-try/
- llrs.dev CRAN archival analysis: https://llrs.dev/post/2021/12/07/reasons-cran-archivals/
- CRAN archived check results: https://cran-archive.r-project.org/web/checks/
- noSuggests check: https://www.stats.ox.ac.uk/pub/bdr/noSuggests/
- CRAN Package Check Flavors: https://cran.r-project.org/web/checks/check_flavors.html
- Revolution Analytics -- Big changes in R 3.5.0: https://blog.revolutionanalytics.com/2018/04/r-350.html
- Revolution Analytics -- What's new in R 3.6.0: https://blog.revolutionanalytics.com/2019/05/whats-new-in-r-360.html
- vctrs s3_register: https://vctrs.r-lib.org/reference/s3_register.html
- roxygen2 issue #796 (delayed S3 registration): https://github.com/r-lib/roxygen2/issues/796
- R-hub blog -- Solaris checking: https://blog.r-hub.io/2020/05/14/checking-your-r-package-on-solaris/
- Reside-IC -- Debugging CRAN additional checks: https://reside-ic.github.io/blog/debugging-and-fixing-crans-additional-checks-errors/
- R-package-devel Solaris thread (2018): https://stat.ethz.ch/pipermail/r-package-devel/2018q3/002999.html
- rOPENSCI HTTP testing book -- Graceful failure: https://books.ropensci.org/http-testing/graceful.html
- data.table URL issue #2756: https://github.com/Rdatatable/data.table/issues/2756
- R sf isFALSE issue #1342: https://github.com/r-spatial/sf/issues/1342
