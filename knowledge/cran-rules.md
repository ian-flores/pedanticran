# CRAN Submission Rules — Complete Knowledge Base

Every rule includes: what CRAN requires, how they reject it (verbatim feedback), how to detect it, and how to fix it.

Sources: CRAN Repository Policy, CRAN Submission Checklist, CRAN Cookbook (R Consortium), ThinkR prepare-for-cran, devtools/usethis release checklist, community experience, R-package-devel and r-devel mailing list archives (2015 through September 2026), CRAN policy SVN history and `X-CRAN-Comment` archival notes, R NEWS for R 3.2 through R 4.6.1 (plus R-devel), and the R sources of `tools/R/check.R`. Coverage: 2015 through September 2026.

---

## Category: DESCRIPTION File

### DESC-01: Title Must Be in Title Case

- **Severity**: REJECTION
- **Rule**: The Title field must use Title Case. Capitalize principal words; lowercase articles (a, an, the), conjunctions (and, but, or), and prepositions (of, in, to, for) unless they begin the title.
- **CRAN says**: Rejects with note about incorrect title case.
- **Detection**: Parse the Title field. Check each word against title case rules. Use `tools::toTitleCase()` logic.
- **Fix**: Apply title case transformation. Watch for acronyms (keep uppercase), package names (keep as-is in single quotes), and small words.
- **Files**: `DESCRIPTION`
- **Since**: R 3.2.0 (2015) — automated title case validation added to R CMD check

### DESC-02: Package/Software Names Must Be in Single Quotes

- **Severity**: REJECTION
- **Rule**: All package names, software names, and API names mentioned in Title and Description must be wrapped in single quotes.
- **CRAN says**: "Please always write package names, software names and API (application programming interface) names in single quotes in title and description. e.g: --> 'python'"
- **Detection**: Scan Title and Description for known R package names (from CRAN/Bioconductor), common software names (Python, Java, C++, OpenSSL, TensorFlow, etc.), and API names without single quotes.
- **Fix**: Wrap each name in single quotes: `Python` → `'Python'`, `ggplot2` → `'ggplot2'`
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-03: No "for R" / "in R" / "with R" in Title

- **Severity**: REJECTION
- **Rule**: The Title must not contain phrases like "for R", "in R", "with R", "an R package" — it's on CRAN, so it's obviously for R.
- **CRAN says**: Rejects as redundant.
- **Detection**: Regex scan Title for `\b(for|in|with)\s+R\b` or `\bR\s+(package|library)\b` (case-insensitive, but careful not to match R inside words).
- **Fix**: Remove the redundant phrase. "A Plotting Library for R" → "A Plotting Library".
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-04: Description Must Not Start with Package Name, "A package...", or Title

- **Severity**: REJECTION
- **Rule**: The Description field must not begin with the package name, "A package that...", "This package...", or repeat the title.
- **CRAN says**: Rejects with note about description starting incorrectly.
- **Detection**: Check first word/phrase of Description against: package name, "A package", "This package", "The package", and the Title text.
- **Fix**: Rewrite opening to describe functionality directly. "Provides methods for..." or "Implements the algorithm described in..."
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-05: Description Must Be 2+ Complete Sentences

- **Severity**: REJECTION
- **Rule**: Description must be a coherent paragraph of at least 2 complete sentences. Longer is better for new packages.
- **Detection**: Count sentence-ending punctuation (periods followed by space or end of field). Check for minimum length.
- **Fix**: Expand Description to include what the package does, how, and why.
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-06: DOI/URL Formatting

- **Severity**: REJECTION
- **Rule**: References must use author-year style with DOI in angle brackets. NO space after `doi:`. Format: `Authors (year) <doi:10.prefix/suffix>`.
- **CRAN says**: "If there are references describing the methods in your package, please add these in the description field...in the form authors (year) <doi:...> with no space after 'doi:', 'https:' and angle brackets for auto-linking."
- **Detection**: Regex for `doi:\s+` (space after colon), DOIs not in angle brackets, URLs not in angle brackets.
- **Fix**: Reformat to `<doi:10.xxxx/yyyy>` with no spaces.
- **Files**: `DESCRIPTION`
- **Since**: R 3.3.0 (2016) — DOI validation in CITATION and Rd files added; format requirements enforced since ~2016-2017 policy revisions

### DESC-07: Acronyms Must Be Explained

- **Severity**: REJECTION
- **Rule**: Uncommon acronyms in Title or Description must be explained (spelled out at first use).
- **CRAN says**: "Please always explain all acronyms in the description text."
- **Detection**: Find uppercase sequences (2+ letters) that aren't common (API, URL, HTTP, SQL, CSV, JSON, XML, HTML, PDF, GUI, CLI, IDE, OS, IO, UI, ID). Flag unexplained ones.
- **Fix**: Add explanation in parentheses at first use, or spell out the acronym.
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-08: Must Use Authors@R Field

- **Severity**: REJECTION
- **Rule**: Must use the `Authors@R` field with `person()` entries, not separate Author/Maintainer fields.
- **CRAN says**: "Author field differs from that derived from Authors@R. No Authors@R field in DESCRIPTION. Please add one..."
- **Detection**: Check for presence of `Authors@R` field. Check for deprecated `Author` and `Maintainer` fields used alone.
- **Fix**: Convert to `Authors@R` with proper `person()` entries including roles (aut, cre, cph, ctb).
- **Files**: `DESCRIPTION`
- **Since**: ~2016-2017 — Authors@R field preferred since CRAN policy revisions r3747-r3874

### DESC-09: Must Include Copyright Holder (cph)

- **Severity**: REJECTION
- **Rule**: At least one person or entity must have the `cph` (copyright holder) role in Authors@R.
- **Detection**: Parse Authors@R field, check for presence of `"cph"` role.
- **Fix**: Add `"cph"` role to the appropriate person(s).
- **Files**: `DESCRIPTION`
- **Since**: ~2016-2017 — cph role requirement added during CRAN policy revisions r3747-r3874

### DESC-10: Unnecessary "+ file LICENSE"

- **Severity**: REJECTION
- **Rule**: Do not include `+ file LICENSE` in the License field unless the license requires attribution or has other restrictions (MIT, BSD). Standard licenses (GPL-2, GPL-3, LGPL) do not need it.
- **CRAN says**: "We do not need '+ file LICENSE' and the file as these are part of R. This is only needed in case of attribution requirements or other possible restrictions."
- **Detection**: Check License field for `+ file LICENSE` combined with licenses that don't require it (GPL-2, GPL-3, LGPL-2.1, LGPL-3, Apache-2.0).
- **Fix**: Remove `+ file LICENSE` and the LICENSE file for standard licenses. Keep for MIT, BSD-2-clause, BSD-3-clause.
- **Files**: `DESCRIPTION`, `LICENSE`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-11: Single Maintainer Required

- **Severity**: REJECTION
- **Rule**: Exactly one person must have the `cre` (creator/maintainer) role. Must be a person, not a mailing list. Must have a working email.
- **Detection**: Parse Authors@R, count entries with `"cre"` role. Verify it's exactly 1. Check email looks like a person (not a list address).
- **Fix**: Ensure exactly one `cre` entry with a personal email.
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DESC-12: Version Must Increase

- **Severity**: REJECTION
- **Rule**: Updates to published packages must have an increased version number. Even resubmissions after rejection should bump the version.
- **Detection**: Cannot check automatically without knowing CRAN state — flag as reminder.
- **Fix**: Bump patch version for resubmissions (0.3.1 → 0.3.2).
- **Files**: `DESCRIPTION`

### DESC-13: Stale Date Field

- **Severity**: REJECTION
- **Rule**: If the DESCRIPTION Date field is more than a month old at submission time, CRAN rejects. "The Date field is over a month old."
- **CRAN says**: "The Date field is over a month old."
- **Detection**: Parse Date field, compare to current date. Flag if >30 days old.
- **Fix**: Update Date field to today's date, or remove it entirely (Date is optional — CRAN derives it from the tarball).
- **Files**: `DESCRIPTION`

### DESC-14: Version Component Size

- **Severity**: NOTE
- **Rule**: Version components larger than 9000 trigger a NOTE. Development versions like 0.1.0.9001 are fine, but something like 1.0.12345 will be flagged.
- **CRAN says**: NOTE about "large version component"
- **Detection**: Parse Version field, check if any component > 9000.
- **Fix**: Use a smaller version number. Follow standard x.y.z convention.
- **Files**: `DESCRIPTION`

### DESC-15: Use Straight Quotes Only

- **Severity**: REJECTION
- **Rule**: DESCRIPTION file must use straight (ASCII) quotes, not directed/smart/curly quotes. Unicode quotes like \u2018, \u2019, \u201C, \u201D are rejected.
- **CRAN says**: "non-ASCII characters in DESCRIPTION" or encoding issues with smart quotes.
- **Detection**: Grep DESCRIPTION for Unicode quotation marks (\u2018 \u2019 \u201C \u201D or their UTF-8 bytes).
- **Fix**: Replace all smart/curly quotes with straight ASCII quotes (' and ").
- **Files**: `DESCRIPTION`

### DESC-16: Authors@R Must Use Only Whitelisted Calls

- **Severity**: NOTE (R CMD check); fails R CMD build/INSTALL run on a source directory with R-devel/R-4-6-branch
- **Rule**: `Authors@R` may only contain calls to `person`, `c`, `list`, `paste`, `paste0` (`as.person` was whitelisted later). Anything else, typically `comment(ORCID = ...)` or `ORCID = ...` inside `person()`, is flagged as possibly unsafe. Kurt Hornik plans to stop evaluating non-whitelisted calls altogether, and CITATION files are expected to get similar restrictions (see INST-02).
- **CRAN says**: "* checking DESCRIPTION meta-information ... NOTE / Malformed Authors@R field: / Found the following possibly unsafe calls: / comment("SwissMarbledWhite") / Please only use calls to 'person', 'c', 'list', 'paste', 'paste0'." (Kurt Hornik, r-devel, 2026-04-11, https://stat.ethz.ch/pipermail/r-devel/2026-April/084480.html). Ivan Krylov: on a source directory R CMD build and R CMD INSTALL call the same check, "which fails the build" (https://stat.ethz.ch/pipermail/r-devel/2026-April/084491.html).
- **Detection**: Parse `Authors@R` with `parse()` (do not eval). Walk the call tree and flag any function name outside {person, c, list, paste, paste0, as.person}. Specifically flag `comment(` and a named `ORCID =` argument to `person()`.
- **Fix**: Use `person("First", "Last", email = "...", role = c("aut", "cre"), comment = c(ORCID = "0000-..."))`. Replace `personList()` with `c()`.
- **Files**: `DESCRIPTION`
- **Since**: R-devel r89866 (2026-04-10), merged into R-4-6-branch; about 20 CRAN packages affected at introduction

### DESC-17: Declare an Honest Minimum R Version

- **Severity**: RECOMMENDED
- **Rule**: `Depends: R (>= x.y.z)` means "will not work below this". It does not mean "untested below this". Do not inflate it, since it cascades to every reverse dependency. Avoid a non-zero patch level unless a patch release fixed a bug you rely on (ABI compatibility is guaranteed across patch versions). Never declare versions that do not exist (e.g. 3.60).
- **CRAN says**: Simon Urbanek (R-package-devel, 2026-04): "Robin may be misunderstanding the purpose of that declaration as he seem to see it as "I didn't test it" while it really means "you're not allowed to install it, it won't work". gsl actually works perfectly fine (i.e. passes all checks with OK) at from R 3.2.0 on, so the declaration is just blatantly wrong - it should read (R >= 3.2.0)." (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012357.html) / "if the bug affects your use case then you should use 4.1.3 otherwise 4.1.0. Normally, ABI compatibility is guaranteed across all patch versions - hence the comment to make sure the requirement is not unnecessary" (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012378.html)
- **Detection**: Parse `Depends: R (>= ...)`. Flag a non-existent version (e.g. 3.8, 3.10, 3.21, 3.50, 3.60, 3.63), a patch level != 0, or a version newer than r-oldrel without an obvious trigger. Some features do justify a specific minimum, e.g. `|>` or the R 4.6.0 Rd syntax (DOC-14).
- **Fix**: Set the lowest version where checks pass. In C code, use `#if R_VERSION >= R_Version(x,y,0)` instead of raising the R requirement.
- **Files**: `DESCRIPTION`
- **Since**: Writing R Extensions guidance is long-standing; the gsl `R (>= 4.5.0)` cascade (200+ reverse dependencies) was discussed in April 2026

---

## Category: Code Behavior

### CODE-01: Use TRUE/FALSE, Not T/F

- **Severity**: REJECTION
- **Rule**: Must use `TRUE` and `FALSE` literals. `T` and `F` are regular variables, not reserved words — a user could do `T <- 42`.
- **CRAN says**: "Please write TRUE and FALSE instead of T and F. Please don't use 'T' or 'F' as vector names."
- **Detection**: Grep R files for `\bT\b` and `\bF\b` used as logical values (not inside strings, not as function params named T/F). Context-aware: look for `= T`, `= F`, `(T)`, `(F)`, `, T`, `, F`.
- **Fix**: Replace `T` with `TRUE`, `F` with `FALSE`. Rename variables named T or F.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`
- **Since**: Pre-2015 — one of the oldest and most consistently enforced CRAN rules

### CODE-02: Use message()/warning()/stop(), Not print()/cat()

- **Severity**: REJECTION
- **Rule**: Informational messages must use `message()` so users can suppress them with `suppressMessages()`. Do not use `print()` or `cat()` for status messages.
- **CRAN says**: "You write information messages to the console that cannot be easily suppressed. Instead of print()/cat() rather use message()/warning()/stop(), or if(verbose)cat(..)"
- **Detection**: Grep R source files for `print(` and `cat(` calls that aren't inside print/summary S3 methods or interactive-only functions.
- **Fix**: Replace `cat("Processing...\n")` with `message("Processing...")`. Replace `print(paste("Done:", x))` with `message("Done: ", x)`.
- **Exceptions**: print/summary methods, interactive functions, if(verbose) cat() pattern.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-03: No Hardcoded set.seed() in Functions

- **Severity**: REJECTION
- **Rule**: Functions must not call `set.seed()` with a hardcoded value. Seeds are OK in examples, vignettes, tests — not in function bodies.
- **CRAN says**: "Please do not set a specific number within a function."
- **Detection**: Find `set.seed(` inside function bodies in R/ directory. Distinguish from examples/tests/vignettes.
- **Fix**: Remove the hardcoded seed, or add a `seed` parameter that defaults to NULL (only set when user provides one).
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-04: Restore options()/par()/setwd() with on.exit()

- **Severity**: REJECTION
- **Rule**: If a function changes `options()`, `par()`, or `setwd()`, it must immediately restore them using `on.exit()`. Restore every graphics parameter you set explicitly, including mfrow/mfcol/oma ("you have to restore any parameters you set explicitly, which does include mfrow and similar as well", Simon Urbanek, 2026-07-09, https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012442.html). Coordinate parameters set by plot.window (usr, xaxp, yaxp) are expected to change. If users need to add to a multi-panel plot, return the needed settings (Uwe Ligges: "reset everything but return a list of parameters that need to be set again if you want to, e.g., add to the plot generated with modified parameters", https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012443.html).
- **CRAN says**: "Please make sure that you do not change the user's options, par or working directory. If you really have to do so within functions, please ensure with an immediate call of on.exit() that the settings are reset when the function is exited."
- **Detection**: Find calls to `options(`, `par(`, `setwd(` in function bodies. Check if followed by corresponding `on.exit(` call. The `on.exit()` must come immediately after, not later in the function.
- **Fix**: Add save-and-restore pattern:
  ```r
  old <- options(warn = 1)
  on.exit(options(old), add = TRUE)
  ```
  Save only what you change: `op <- par(mfrow = c(1, 2)); on.exit(par(op), add = TRUE)`.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-05: Never Use options(warn = -1)

- **Severity**: REJECTION
- **Rule**: `options(warn = -1)` is always rejected, even with proper `on.exit()` restoration. Use `suppressWarnings()` instead.
- **CRAN says**: "You are setting options(warn=-1) in your function. This is not allowed. Please rather use suppressWarnings() if really needed."
- **Detection**: Grep for `options(warn\s*=\s*-1)` or `options(warn\s*=\s*-\s*1)`.
- **Fix**: Replace `options(warn = -1); ...; on.exit(options(old))` with `suppressWarnings({ ... })`.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-06: Write Only to tempdir()

- **Severity**: REJECTION
- **Rule**: Must not write to user's home directory, working directory, or package directory. Only `tempdir()` and `tempfile()` are allowed for temporary files. For persistent user data, use `tools::R_user_dir()` (R >= 4.0) with user consent. `tools::R_user_dir()` caches must be small by default and actively pruned, and must not be created or modified during R CMD check (examples, tests, vignettes). R CMD check reports 'checking for new files in some other directories ... NOTE Found the following files/directories: ~/.cache/<pkg>/...'. See CODE-24.
- **CRAN says**: "Please ensure that your functions do not write by default or in your examples/vignettes/tests in the user's home filespace (including the package directory and getwd()). This is not allowed by CRAN policies." / "Archived on 2026-06-01 for policy violation. . Stores > 100 MB in ~/.cache/R and does not clean up." (nomesbr, CRAN `X-CRAN-Comment`)
- **Detection**: Find `write*`, `save*`, `writeLines`, `cat(file=`, `sink(`, `pdf(`, `png(`, etc. where the path is not derived from `tempdir()`, `tempfile()`, or `R_user_dir()`. Look for hardcoded paths, `getwd()`, `~`, `"."`. Flag `R_user_dir(` usage without (a) a size cap/pruning routine and (b) a check-time guard (e.g. defaulting to `tempdir()` when `!interactive()` or when `_R_CHECK_PACKAGE_NAME_` is set).
- **Fix**: Replace file paths with `tempfile()` or `file.path(tempdir(), "name")`. For user data, use `tools::R_user_dir("pkgname", which = "data")` (R >= 4.0).
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`
- **Since**: Pre-2015 — consistently enforced; R 4.0.0 (2020) introduced `tools::R_user_dir()` as the sanctioned persistent storage alternative; CRAN enforced migration from `rappdirs` in late 2021

### CODE-07: Clean Up Temporary Files

- **Severity**: NOTE (can cause rejection)
- **Rule**: Temporary files created in `tempdir()` must be cleaned up. Leaving them produces "Found the following files/directories" detritus NOTE.
- **CRAN says**: R CMD check NOTE: "Found the following files/directories: 'this_is_detritus382e569a7712'"
- **Detection**: Find `tempfile(` or `file.path(tempdir()` calls. Check if corresponding `unlink()` or `file.remove()` exists, or if `withr::local_tempfile()`/`withr::local_tempdir()` is used.
- **Fix**: Add `on.exit(unlink(tmpfile))` after creating temp files. Better: use `withr::local_tempfile()`.
- **Files**: `R/*.R`, `tests/**/*.R`

### CODE-08: No installed.packages()

- **Severity**: REJECTION
- **Rule**: `installed.packages()` is extremely slow and must not be used. Use targeted alternatives instead.
- **CRAN says**: "You are using installed.packages() in your code. As mentioned in the notes of installed.packages() help page, this can be very slow."
- **Detection**: Grep for `installed.packages(`.
- **Fix**: Replace with `requireNamespace("pkg", quietly = TRUE)`, `find.package("pkg")`, or `system.file(package = "pkg")`.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-09: No Modifying .GlobalEnv

- **Severity**: REJECTION
- **Rule**: Functions must not modify the global environment. No `<<-` to global scope, no `assign(..., envir = .GlobalEnv)`, no `rm(list = ls())` in examples/vignettes.
- **CRAN says**: "Please do not modify the global environment (e.g., by using <<-) in your functions."
- **Detection**: Find `<<-`, `assign(.*globalenv|\.GlobalEnv)`, `rm(list\s*=\s*ls())`.
- **Fix**: Use local environments, return values, or package-level environments instead of `<<-`.
- **Exceptions**: Shiny reactive assignments.
- **Files**: `R/*.R`, `man/*.Rd`, `vignettes/*.Rmd`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-10: Maximum 2 Cores

- **Severity**: NOTE → REJECTION
- **Rule**: Package must not use more than 2 cores in examples, vignettes, or tests. CRAN runs many checks in parallel.
- **CRAN says**: "Please ensure that you do not use more than 2 cores in your examples, vignettes, etc." / "Archived on 2026-05-15 for policy violation. . Attempts to use all CPU cores." (lavDiag, CRAN `X-CRAN-Comment`)
- **Detection**: Find `parallel::detectCores()`, `makeCluster(`, `mclapply(`, `future::plan(multisession`, etc. Check if core count is hardcoded > 2 or uses `detectCores()` without `min(..., 2)`. Flag threads spawned by embedded runtimes (TensorFlow/reticulate, OpenMP, BLAS) in vignettes. greta's vignette showed "Re-building vignettes had CPU time 4.1 times elapsed time" from TensorFlow threads (Feb 2026, https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012257.html).
- **Fix**: Cap cores: `ncores <- min(parallel::detectCores(), 2)`. Or use `getOption("mc.cores", 2L)`.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`, `man/*.Rd`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-11: No q(), quit(), or Process Termination

- **Severity**: REJECTION
- **Rule**: R code must never call `q()` or `quit()`. C/C++ code must not call `abort()`, `exit()`, `assert()`. Fortran must not call `STOP`.
- **Detection**: Grep R files for `\bq\(`, `\bquit\(`. Grep C/C++ for `abort(`, `exit(`, `assert(`. Grep Fortran for `STOP`.
- **Fix**: Use `stop()` to signal errors in R. In C, use `Rf_error()`.
- **Files**: `R/*.R`, `src/*.c`, `src/*.cpp`, `src/*.f`, `src/*.f90`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-12: No :::  to Internal Base Functions

- **Severity**: REJECTION
- **Rule**: Must not use `:::` to access unexported objects from base/recommended packages. Must not use `.Internal()` or `.Call()` to base.
- **Detection**: Grep for `:::\s*` where the package is a base/recommended package (base, utils, stats, methods, grDevices, graphics, datasets, tools, compiler). Also grep for `.Internal(`.
- **Fix**: Use public API alternatives. If none exists, file an R wish-list request.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — CRAN policy long stated "CRAN packages should use only the public API"; automated non-API checking expanded progressively from R 4.3+ (2023)

### CODE-13: No Installing Packages in Functions

- **Severity**: REJECTION
- **Rule**: Functions should not install packages. This makes examples slow and modifies the user's system.
- **CRAN says**: "Please do not install packages in your functions, examples or vignettes."
- **Detection**: Find `install.packages(`, `remotes::install_`, `devtools::install_` in R source (not in functions whose explicit purpose is installation). Scan *top-level* (non-assignment) calls in R/*.R, e.g. `library()`, `require()`, `install.packages()`, `options()`, or `lapply(pkgs, library, ...)`. R CMD check analyses the installed namespace, so these run at install time and evade its checks ("The check code by default uses tools:::.check_packages_used() on the code in the installed package, and hence cannot pick up top-level calls as these got processed when installing.", Kurt Hornik, r-devel 2026-06, https://stat.ethz.ch/pipermail/r-devel/2026-June/084612.html). Hornik is working on source-level detection.
- **Fix**: Remove installation calls. Use `requireNamespace()` to check availability instead.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### CODE-14: No Disabling SSL/TLS Verification

- **Severity**: REJECTION
- **Rule**: Must not circumvent security provisions like disabling SSL certificate verification.
- **Detection**: Find `httr::config(ssl_verifypeer = 0)`, `curl::handle_setopt(ssl_verifypeer = FALSE)`, or similar.
- **Fix**: Remove SSL bypass. Fix certificate issues properly.
- **Files**: `R/*.R`

### CODE-15: No browser() Statements

- **Severity**: REJECTION
- **Rule**: Leftover `browser()` calls in package code will cause check failures under `--as-cran`. R 4.5+ traps non-interactive debugger invocations.
- **CRAN says**: R CMD check flags browser() under `_R_CHECK_BROWSER_NONINTERACTIVE_` (enabled by --as-cran).
- **Detection**: Grep for `browser()` in R/*.R function bodies (not in commented-out lines).
- **Fix**: Remove all browser() calls. Use `debugonce()` interactively instead.
- **Files**: `R/*.R`

### CODE-16: sprintf/vsprintf in C/C++ Code

- **Severity**: NOTE → REJECTION
- **Rule**: R 4.5+ reports `sprintf` and `vsprintf` usage in compiled code on ALL platforms. macOS 13+ has deprecated sprintf entirely.
- **CRAN says**: NOTE about sprintf/vsprintf usage in compiled code.
- **Detection**: Grep src/*.c, src/*.cpp for `sprintf(` and `vsprintf(`.
- **Fix**: Replace `sprintf` with `snprintf`, `vsprintf` with `vsnprintf`.
- **Files**: `src/*.c`, `src/*.cpp`

### CODE-17: UseLTO Causes CPU Time NOTE

- **Severity**: NOTE (can cause rejection)
- **Rule**: `UseLTO: yes` in DESCRIPTION triggers parallel compilation during install, causing "Installation took CPU time X times elapsed time" NOTE.
- **CRAN says**: "Installation took CPU time 3.5 times elapsed time"
- **Detection**: Check DESCRIPTION for `UseLTO` field.
- **Fix**: Remove `UseLTO` from DESCRIPTION unless absolutely needed.
- **Files**: `DESCRIPTION`

### CODE-18: Do Not Remove Failing Tests

- **Severity**: REJECTION
- **Rule**: Removing failing tests instead of fixing them is always rejected. CRAN views this as evidence the package doesn't work correctly.
- **CRAN says**: "Removed the failing tests which is not the idea of tests."
- **Detection**: Cannot detect statically — informational rule for the respond skill.
- **Fix**: Fix the underlying test failures. If test coverage increased, present covr evidence.
- **Files**: `tests/**/*.R`

### CODE-19: Staged Installation Compatibility

- **Severity**: REJECTION
- **Rule**: Packages must not cache absolute paths at install time or namespace load time. R 3.6.0 introduced staged installation as the default: packages are first installed to a temporary directory, then moved to the final library location. Code that calls `system.file()` at the top level of an R source file and saves the result will cache the temporary path, which breaks after the move.
- **CRAN says**: "ERROR: installation of package 'PKGNAME' had non-zero exit status" (with paths pointing to the temporary staging directory)
- **Detection**: Find top-level `system.file()` calls in R source files that are assigned to variables outside of function bodies. Check `.onLoad()` for path caching via `system.file()` saved to package-level variables.
- **Fix**: Replace cached paths with function calls that compute paths at runtime. Instead of `globals$DB_PATH <- system.file(...)` at top level, use a function: `getDbPath <- function() system.file(...)`. Packages can opt out temporarily via `StagedInstall: no` in DESCRIPTION, but CRAN discourages this.
- **Files**: `R/*.R`, `DESCRIPTION`
- **Since**: R 3.6.0 (2019) — staged installation enabled by default; initially broke 48 CRAN/Bioconductor packages

### CODE-20: stringsAsFactors=FALSE Default Compatibility

- **Severity**: WARNING
- **Rule**: Since R 4.0.0, `data.frame()` and `read.table()` default to `stringsAsFactors = FALSE`. Code that relies on strings being automatically converted to factors will silently produce wrong results. This includes downstream computations on factor levels and sort orders that depended on locale-dependent factor conversion.
- **CRAN says**: Test failures or incorrect results on R >= 4.0.0 due to character columns where factors were expected.
- **Detection**: Search for `data.frame()` and `read.table()` calls without explicit `stringsAsFactors=` argument where downstream code uses `levels()`, `nlevels()`, or factor-specific operations. Flag `is.factor()` checks on columns that may now be character.
- **Fix**: Add explicit `stringsAsFactors = TRUE` where factor behavior is needed, or update code to work with character vectors. Use `factor()` explicitly when factor type is required.
- **Files**: `R/*.R`, `tests/**/*.R`
- **Since**: R 4.0.0 (2020) — reversed 22 years of default behavior (since R 0.62, 1998); broke a large number of packages

### CODE-21: class(matrix()) Returns Two-Element Vector

- **Severity**: WARNING
- **Rule**: Since R 4.0.0, `class(matrix())` returns `c("matrix", "array")` instead of just `"matrix"`. Code using `class(x) == "matrix"` will silently fail because `==` against a length-2 vector no longer yields a single TRUE/FALSE.
- **CRAN says**: "the condition has length > 1 and only the first element will be used" (interacts with CODE-22)
- **Detection**: Grep R source and test files for patterns like `class(x) == "matrix"`, `class(x) == "array"`, `length(class(x)) == 1`. Also flag `class(x) ==` comparisons generally, as other classes may gain inheritance in future R versions.
- **Fix**: Use `is.matrix()` or `inherits(x, "matrix")` instead of `class(x) == "matrix"`. Use `is()` or `inherits()` for all class checks.
- **Files**: `R/*.R`, `tests/**/*.R`
- **Since**: R 4.0.0 (2020) — matrices now inherit from "array" class

### CODE-22: if()/while() Condition Length > 1 Is an Error

- **Severity**: REJECTION
- **Rule**: Since R 4.2.0, using a vector of length > 1 as a condition in `if()` or `while()` is a runtime error (previously a warning since R 2.x). Additionally, `&&` and `||` with either argument of length > 1 gives a warning (intended to become error later).
- **CRAN says**: "Error in if (c(TRUE, FALSE)) { : the condition has length > 1"
- **Detection**: Static analysis of `if()` and `while()` conditions for expressions that may produce multi-element results: `class(x) == "something"`, vector comparisons without `any()`/`all()`, `which()` results used as conditions.
- **Fix**: Use `any()`, `all()`, or ensure conditions are scalar. Replace `if (class(x) == "matrix")` with `if (inherits(x, "matrix"))`. Replace `if (x == y)` with `if (identical(x, y))` or `if (all(x == y))` where appropriate.
- **Files**: `R/*.R`
- **Since**: R 4.2.0 (2022) — upgraded from WARNING to ERROR; CRAN gave deadline of 2022-04-04 for packages to comply before R 4.2.0 release

### CODE-23: No Divisive or Offensive Material (e.g., Political Slogans)

- **Severity**: REJECTION (archival "for policy violation")
- **Rule**: Packages must not contain or display material that might be considered divisive or give offence, such as political slogans. This applies to startup messages and banners, printed output, documentation, README (installed and shown in HTML help since R 4.6.0), DESCRIPTION, data, examples and vignettes. The policy gives no definition beyond "divisive or give offence".
- **CRAN says**: Policy: "Packages should not contain nor display material which might be considered divisive or give offence, such as political slogans." / Archival: "Archived on 2026-07-28 for policy violation. . Anti-social behaviour, displaying a political message in its banner. Version 0.8.1 has been removed." (rim, CRAN `X-CRAN-Comment`)
- **Detection**: Review flag only; never auto-fail. Scan `.onAttach`/`.onLoad` `packageStartupMessage()`/`message()`/`cat()` strings, `DESCRIPTION` Title/Description, `README.md`, `inst/` text and `R/*.R` string literals for slogan-like or non-package content (e.g. a curated keyword list; anything with "!" in a startup message). Report as "review manually".
- **Fix**: Remove the material. Restrict startup messages to package-relevant information and keep them suppressible. Put non-technical statements on an external website, not in the package.
- **Files**: `R/zzz.R`, `R/*.R`, `DESCRIPTION`, `README.md`, `man/*.Rd`, `vignettes/*`, `inst/*`
- **Since**: CRAN policy SVN r6942 (committed 2026-09-02); on the live policy page by 2026-07-27 (page still labelled Rev 6875); first archival under it 2026-07-28

### CODE-24: User Cache Must Be Bounded and Untouched by R CMD check

- **Severity**: REJECTION (archival "for policy violation")
- **Rule**: Files under `tools::R_user_dir()` (e.g. `~/.cache/R/<pkg>`) must be small by default, actively pruned, and not created or modified during examples, tests or vignettes run by R CMD check.
- **CRAN says**: Policy: "packages may store user-specific data, configuration and cache files in their respective user directories obtained from tools::R_user_dir(), provided that by default sizes are kept as small as possible and the contents are actively managed (including removing outdated material)." / "Archived on 2026-06-01 for policy violation. . Stores > 100 MB in ~/.cache/R and does not clean up." (nomesbr) / "Archived on 2026-06-01 for policy violation. . Stores > 150 MB in ~/.cache/R and does not clean up." (rcldf) / Check NOTE: "* checking for new files in some other directories ... NOTE / Found the following files/directories: / '~/.cache/rsurvstat/022e3d1edce617738e145996fea14ed7.xml'" / Ivan Krylov (not CRAN team): "running R CMD check shouldn't create or modify user files (including the cache)." (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012486.html)
- **Detection**: Find `R_user_dir(`, `rappdirs::user_cache_dir(`, and literal `~/.cache`. Flag if (a) there is no pruning or max-size logic (no `unlink`/`file.remove` on the cache dir, no age or size check), or (b) the cache path is used by default in examples/tests/vignettes without redirecting to `tempdir()`.
- **Fix**: Add a cache-size cap and expiry. Provide a `pkg_cache_clear()` function. In examples/tests set an option/env var pointing the cache to `tempdir()`, or skip caching when `!interactive()`. Declare `Depends: R (>= 4.0)` if using `R_user_dir()`.
- **Files**: `R/*.R`, `tests/**`, `vignettes/*`, `man/*.Rd`
- **Since**: Policy wording since the R 4.0 era; first size-based archivals 2026-06-01 (nomesbr, rcldf); rsurvstat given a 2026-08-21 deadline

---

## Category: Compiled Code (C/C++/Fortran)

### COMP-01: C23 Keyword Conflicts

- **Severity**: REJECTION
- **Rule**: R 4.5.0+ defaults to C23. `bool`, `true`, `false`, `nullptr` are now reserved C keywords. Code using these as variable names or redefining them will fail to compile.
- **CRAN says**: Compiler error or `-Wkeyword-macro` warning under C23.
- **Detection**: Grep src/*.c, src/*.h for `typedef.*bool`, `#define true`, `#define false`, `#define bool`, variable names `bool`, `true`, `false`.
- **Fix**: Remove redefinitions. Use `<stdbool.h>` or rely on C23 built-in keywords. For backward compatibility, use `R_USE_C17` in SystemRequirements as opt-out.
- **Files**: `src/*.c`, `src/*.h`

### COMP-02: R_NO_REMAP Required for C++

- **Severity**: REJECTION
- **Rule**: R 4.5.0+ compiles C++ with `-DR_NO_REMAP` by default. Bare R API function names (`error()`, `length()`, `warning()`, `mkChar()`) must use `Rf_` prefix.
- **CRAN says**: Compilation error from bare R API names in C++ code.
- **Detection**: Grep src/*.cpp for bare R API calls: `\berror\(`, `\blength\(`, `\bwarning\(`, `\bmkChar\(`, `\balloc`, `\bprotect\(`, `\bunprotect\(` etc. (excluding lines that already use Rf_ prefix).
- **Fix**: Replace `error(` with `Rf_error(`, `length(` with `Rf_length(`, `warning(` with `Rf_warning(`, `mkChar(` with `Rf_mkChar(`, etc.
- **Files**: `src/*.cpp`, `src/*.h`

### COMP-03: Non-API Entry Points

- **Severity**: WARNING → REJECTION; compile ERROR for hidden/removed entry points
- **Rule**: R 4.5.0 upgraded some non-API entry point NOTEs to WARNINGs. R 4.6.0 (2026-04-24) upgraded more, hid ~33 entry points (compilation now fails, not just a check finding) and removed VECTOR_PTR and Rf_isFrame. The installed R 4.6.0 headers now declare only the C API as defined in Writing R Extensions, and non-API *variables* now give NOTEs. `R_MissingArg` was re-added to the variables API and no longer gives a NOTE. Packages that do not implement new connection types must not use `Rconnection` internals. Using internal R API functions blocks submission.
- **CRAN says**: "Found non-API calls to R: [function names]" (WARNING level). R 4.6.0 NEWS: "R CMD check 'NOTE's on the use of these non-API entry points have been upgraded to 'WARNING's in preparation for removing declarations and, where possible, hiding these entry points: R_nchar, R_tryWrap, Rf_GetOption, R_lsInternal, BODY, FORMALS, CLOENV, SET_TYPEOF, STRING_PTR, R_duplicate_attr, getConnection, R_data_class, STRING_PTR, SET_OBJECT, ATTRIB, SET_ATTRIB, Rf_findVarInFrame3." / "Packages using any non-API variables will now receive check 'NOTE's." / Luke Tierney (r-devel, April 2026): "The installed C header files for R 4.6.0 should now correspond to the C API as defined by the Writing R Extensions manual: All entry points and variables declared in the headers are now part of the API." (https://stat.ethz.ch/pipermail/r-devel/2026-April/084486.html) / On R_MissingArg: "You are right: R_MissingArg is needed for this so it should be in the variables API. It is now and should no longer generate a check NOTE." (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012341.html)
- **Detection**: Grep src/ for three tiers (R 4.6.0):
  - (i) **Compile failure (hidden/removed):** ENVFLAGS, EXTPTR_PROT, FRAME, ENCLOS, EXTPTR_PTR, EXTPTR_TAG, HASHTAB, IS_S4_OBJECT, LEVELS, NAMED, OBJECT, R_shallow_duplicate_attr, Rf_isValidString, Rf_lazy_duplicate, Rf_NonNullStringMatch, SETLENGTH, SETLEVELS, SET_BODY, SET_CLOENV, SET_ENCLOS, SET_FORMALS, SET_ENVFLAGS, SET_FRAME, SET_GROWABLE_BIT, SET_HASHTAB, SET_NAMED, SET_S4_OBJECT, SET_TRUELENGTH, STDVEC_DATAPTR, TRUELENGTH, UNSET_S4_OBJECT, XTRUELENGTH, VECTOR_PTR, Rf_isFrame, LOGICAL0, INTEGER0, REAL0, COMPLEX0, RAW0, DATAPTR.
  - (ii) **WARNING:** R_nchar, R_tryWrap, Rf_GetOption, R_lsInternal, BODY, FORMALS, CLOENV, SET_TYPEOF, STRING_PTR, R_duplicate_attr, getConnection, R_data_class, SET_OBJECT, ATTRIB, SET_ATTRIB, Rf_findVarInFrame3, PRCODE, SET_PRCODE, PRENV, SET_PRENV, PRVALUE, SET_PRVALUE, R_PromiseExpr, Rf_allocSExp. (R 4.6.0 NEWS also has an earlier entry saying ATTRIB/SET_ATTRIB "will now receive check 'NOTE's"; the later upgrade entry and the R-4-6-branch `tools/R/sotools.R` `warnNonAPI` list both put them at WARNING.)
  - (iii) **NOTE:** Rf_acopy_string, any non-API *variable* (e.g. `R_NamespaceRegistry`), plus the remaining R 4.5 list (IS_LONG_VEC, Rf_StringBlank, XLENGTH_EX).
  - Also flag `#include <R_ext/PrtUtil.h>` (no longer installed), `#include <R_ext/Callbacks.h>` used for `R_ObjectTable` (use `R_ext/ObjectTable.h`), writes through `CHARACTER_DATA`/`CHARACTER_POINTER` (now `const`), and `->UTF8out`/`R_GetConnection(` outside connection implementations.
- **Fix**: Replace with supported API equivalents. See Writing R Extensions manual. Replacements: `R_getVar`/`R_getVarEx` for `Rf_findVar*`; `R_mapAttrib`/`R_getAttributes`/`R_hasAttrib` for `ATTRIB`; `R_class` for `R_data_class`; `Rf_isDataFrame` for `Rf_isFrame`; `R_altrep_class_name` for `ALTREP_CLASS`; `DATAPTR_RW` only inside ALTREP `Dataptr` methods; `R_getRegisteredNamespace` instead of `R_NamespaceRegistry`; the bindings API (`R_GetBindingType` etc.); `R_ext/ObjectTable.h` instead of `R_ext/Callbacks.h` for `R_ObjectTable`. Test with `PKG_CPPFLAGS += -DNO_LEGACY_NONAPI` on R-devel (Luke Tierney, https://stat.ethz.ch/pipermail/r-devel/2026-April/084481.html).
- **Files**: `src/*.c`, `src/*.cpp`
- **Since**: R 4.3+ progressively; major tightening R 4.6.0 (2026-04-24). CRAN hosted transitional versions of some packages with many reverse dependencies.

### COMP-04: Implicit Function Declarations (C23)

- **Severity**: REJECTION
- **Rule**: C23 removes implicit function declarations. All functions must be declared before use (via #include or explicit declaration). GCC 14+/clang 16+ with C23 make this an error.
- **CRAN says**: Compilation error about implicit function declaration.
- **Detection**: Difficult to detect statically without compiling. Flag if `src/` exists with .c files as informational reminder.
- **Fix**: Add proper `#include` directives for all used functions. Add function prototypes.
- **Files**: `src/*.c`
- **Since**: R 4.2.0 (2022) — `_R_CHECK_SRC_MINUS_W_IMPLICIT_` defaults to true; Apple clang on macOS made this an error rather than warning

### COMP-05: Configure Script Portability

- **Severity**: NOTE → REJECTION
- **Rule**: Configure scripts must use `/bin/sh`, not `/bin/bash`. Bash-specific syntax (arrays, `[[`, `${var/pattern/replacement}`) is not allowed. R 4.5+ expanded bashism checking to autoconf-generated scripts.
- **CRAN says**: "NOTE 'configure': /bin/bash is not portable"
- **Detection**: Check configure, cleanup scripts for `#!/bin/bash` shebang. Grep for bashisms: `[[`, `]]`, `${var/`, `${var:`, arrays, `source` (use `.` instead).
- **Fix**: Change shebang to `#!/bin/sh`. Replace bashisms with POSIX equivalents.
- **Files**: `configure`, `cleanup`, `tools/*`
- **Since**: Pre-2015 for `/bin/bash` detection; R 4.0.0 (2020) added optional `checkbashisms` check; R 4.5+ expanded to autoconf-generated scripts

### COMP-06: C++11/C++14 Specifications Defunct

- **Severity**: NOTE (R < 4.6) / ignored-and-defunct (R >= 4.6.0). The exact check output under 4.6.0 was not confirmed (UNVERIFIED).
- **Rule**: `CXX_STD = CXX11` or `CXX_STD = CXX14` in Makevars was deprecated. R 4.6.0 removed support for C++11/C++14: such specifications are ignored and the default C++ standard (C++20 where available) is used; `CXX11`, `CXX14`, `CXX11FLAGS`, `CXX14STD`, `SHLIBCXX11LD` etc. are reported as defunct. C++17 is the minimum.
- **CRAN says**: NOTE about deprecated C++ standard specification. R 4.6.0 NEWS: "Support for these standards has been removed: the default C++ standard will be used. R CMD config variables CXX11, CXX14 and their associated CXXxxFLAGS, CXXxxPICFLAGS CXXxxSTD, SHLIBCXXxxLD and SHLIBCXXxxLDFLAGS variables are no longer supported and reported as 'defunct'."
- **Detection**: Grep src/Makevars and src/Makevars.win for `CXX_STD\s*=\s*CXX1[14]`. Also grep `src/Makevars*` and `configure*` for `CXX1[14](FLAGS|PICFLAGS|STD)?\b|SHLIBCXX1[14]LD(FLAGS)?` and `R CMD config CXX1[14]`.
- **Fix**: Remove the `CXX_STD` line entirely (R defaults to C++17+). If C++17 features are needed explicitly, use `CXX_STD = CXX17`.
- **Files**: `src/Makevars`, `src/Makevars.win`
- **Since**: R 4.6.0 (2026-04-24)

### COMP-07: Strict C Function Prototypes

- **Severity**: NOTE → REJECTION
- **Rule**: C functions with empty parameter lists (`int foo()`) must use explicit void: `int foo(void)`. GCC 14+ with `-Wstrict-prototypes` flags these. R 4.4+ enables this warning.
- **CRAN says**: WARNING about "function declaration isn't a prototype" or strict-prototypes.
- **Detection**: Grep src/*.c, src/*.h for function declarations/definitions with empty parentheses: `\w+\s*\(\s*\)` that aren't after `=` or `,` (to avoid false positives on function calls).
- **Fix**: Add `void` to empty parameter lists: `int foo()` → `int foo(void)`.
- **Files**: `src/*.c`, `src/*.h`

### COMP-08: Fortran KIND Portability

- **Severity**: NOTE → REJECTION
- **Rule**: Hardcoded Fortran KIND values like `INTEGER(KIND=4)`, `REAL(KIND=8)`, `REAL*8` are not portable across platforms (KIND values are compiler-specific). R 4.4+ flags these.
- **CRAN says**: WARNING about non-portable Fortran KIND specifications.
- **Detection**: Grep src/*.f, src/*.f90, src/*.f95 for `KIND\s*=\s*\d+`, `INTEGER\*\d+`, `REAL\*\d+`.
- **Fix**: Use `SELECTED_INT_KIND()` and `SELECTED_REAL_KIND()` instead of hardcoded values. E.g., `INTEGER(KIND=SELECTED_INT_KIND(9))` instead of `INTEGER(KIND=4)`.
- **Files**: `src/*.f`, `src/*.f90`, `src/*.f95`

### COMP-09: Rust Package Requirements

- **Severity**: REJECTION
- **Rule**: R packages using Rust (via cargo) must: (1) vendor all crate dependencies (no network access during build), (2) report rustc version before compilation, (3) include AUTHORS file listing all crate authors. Formalized as policy since 2023. Minimum cargo/rustc version requirements must be conservative: test with a cargo at least two (preferably four or more) years old. CRAN's Linux check servers use distribution rustc. Limit `cargo build -j` to 1 or 2.
- **CRAN says**: Rejects packages that download Rust crates during installation or don't vendor dependencies. "Using Rust in CRAN packages": "test before submission with at least a two-year-old version of cargo, and preferably one four or more years old." / "The Linux servers on the CRAN check farm use system versions, and Linux distributions are often slow to update these so version requirements need to be conservative." / "Archived on 2026-05-15 for repeated policy violation. . On requirement for Rust versions." (string2path) / "Archived on 2026-04-20 as issues were not corrected in time. . Also has recent 'rustc' requirement contrary to the policy." (tynding)
- **Detection**: Check for `src/rust/` or `Cargo.toml`. If present, verify `vendor/` directory exists. Check for `configure` script that prints rustc version. Check for `AUTHORS` file. Parse `rust-version`/`edition` in Cargo.toml and version checks in configure. Flag an MSRV newer than ~2 years before the submission date, and `edition = 2024`.
- **Fix**: Run `cargo vendor` and commit the vendor directory. Add configure script that runs `rustc --version`. Create AUTHORS file from `Cargo.toml` contributor fields.
- **Files**: `src/rust/`, `Cargo.toml`, `configure`, `AUTHORS`

### COMP-10: Native Routine Registration Required

- **Severity**: NOTE → WARNING
- **Rule**: Packages using `.C()`, `.Call()`, `.Fortran()`, or `.External()` interfaces must register all native routines via `R_registerRoutines()` and disable symbol search via `R_useDynamicSymbols()` in a `src/init.c` file. The NAMESPACE must use `useDynLib(pkgname, .registration = TRUE)`.
- **CRAN says**: "Found no calls to: 'R_registerRoutines', 'R_useDynamicSymbols'. It is good practice to register native routines and to disable symbol search."
- **Detection**: Check if `src/` exists with `.c`, `.cpp`, `.f`, or `.f90` files. Grep R source files for `.C(`, `.Call(`, `.Fortran(`, `.External(`. If found, check for `src/init.c` (or equivalent) containing `R_registerRoutines`. Check NAMESPACE for `useDynLib(pkgname, .registration = TRUE)`.
- **Fix**: Generate registration code with `tools::package_native_routine_registration_skeleton(".", "src/init.c")`. Update NAMESPACE to `useDynLib(pkgname, .registration = TRUE)`. For Rcpp packages, Rcpp >= 0.12.12 handles this automatically.
- **Files**: `src/init.c`, `NAMESPACE`, `R/*.R`
- **Since**: R 3.4.0 (2017) — introduced as NOTE; one of the most impactful changes for packages with compiled code; affected thousands of packages

### COMP-11: Memory Sanitizer (ASAN/UBSAN/Valgrind) Compliance

- **Severity**: NOTE → REJECTION
- **Rule**: CRAN runs additional checks beyond standard R CMD check using AddressSanitizer (ASAN), Undefined Behavior Sanitizer (UBSAN), and valgrind. Packages with compiled code that trigger memory errors (buffer overflows, use-after-free, uninitialized memory reads, undefined behavior) in these additional checks will be flagged for correction with short deadlines (sometimes 1-2 weeks). Additional-issue results (ASAN/UBSAN, gcc-san/clang-san, valgrind, linux-arm64) are now reported in incoming pretest emails and can block acceptance. Overlapping Fortran array arguments (e.g. BLAS-style DCOPY on overlapping slices of the same array) trigger "AddressSanitizer: memcpy-param-overlap" under flang/clang and violate Fortran aliasing rules (limSolve, scheduled for removal Jun 2026).
- **CRAN says**: "==ERROR: AddressSanitizer: stack-buffer-overflow" / "runtime error: undefined behavior" / "Conditional jump or move depends on uninitialised value(s)"
- **Detection**: Cannot detect statically. Packages with C/C++/Fortran code should be tested locally with sanitizers before submission. Use Docker images with R compiled with ASAN/UBSAN (e.g., `rocker/r-devel-san`), or use rhub's sanitizer-enabled platforms. Flag Fortran calls passing two slices of the same array to a copy routine (`CALL xDCOPY(N, X(J+1), 1, X(J), 1)` pattern).
- **Fix**: Fix memory errors identified by sanitizer output. Common fixes: bounds checking on array access, initializing all variables, fixing use-after-free by managing object lifetimes, removing undefined behavior (signed integer overflow, null pointer dereference).
- **Files**: `src/*.c`, `src/*.cpp`, `src/*.f`, `src/*.f90`
- **Since**: ~2016-2017 — ASAN/UBSAN checks expanded on CRAN's Fedora and Debian check flavors; packages can pass standard R CMD check on all platforms but still fail these additional checks

### COMP-12: UCRT Windows Toolchain Compatibility

- **Severity**: REJECTION (on Windows)
- **Rule**: Since R 4.2.0, Windows uses UCRT (Universal C Runtime) exclusively via Rtools42+, dropping 32-bit support and MSVCRT. Packages must not download pre-compiled MSVCRT libraries at install time. External DLLs must be compatible with UCRT. Encoding behavior changed to UTF-8 on Windows. Rtools45 serves R 4.5.x, 4.6.x and R-devel (no Rtools46); since Rtools45 rev 6691 the compiler is GCC 14.3 and curl requires `secur32` for packages not using pkg-config.
- **CRAN says**: Compilation or linking failures on `r-devel-windows-x86_64` or `r-release-windows-x86_64` platforms.
- **Detection**: Check if package downloads pre-compiled Windows binaries at install time (grep configure.win and src/Makevars.win for `download.file`, `curl`, or `wget` calls). Check for `Makevars.ucrt` file if platform-specific build configuration is needed.
- **Fix**: Use libraries bundled with Rtools42+ instead of downloading external pre-compiled binaries. Add `Makevars.ucrt` if different build flags are needed for UCRT. Test on win-builder with R-devel before submitting.
- **Files**: `src/Makevars.win`, `src/Makevars.ucrt`, `configure.win`
- **Since**: R 4.2.0 (2022) — UCRT became the only Windows target; ~380 packages initially affected; CRAN switched incoming Windows checks to UCRT in December 2021

### COMP-13: Obsolete Rcpp Linker/Compiler Flags in Makevars

- **Severity**: WARNING → REJECTION
- **Rule**: `Rcpp:::LdFlags()` / `RcppLdFlags()` (and `RcppLdPath()`) have been unnecessary since 2013. Under `--as-cran` from R 4.6.0 (and in CRAN incoming checks since about 2026-02-19), the message they print during installation is a "significant warning". `LinkingTo: Rcpp` is all that is needed.
- **CRAN says**: "Found the following significant warnings: 'Rcpp:::LdFlags' has not been needed since 2013 (!!) and may get removed in 2027. Please update your 'Makevars'." (Check regex: `LdFlags.* has not been needed since 2013`.) CRAN incoming check script comment: "Added on 2026-02-19 and on for '--as-cran', but perhaps a bit much for the regular checks, so for now only here ...?"
- **Detection**: Grep `src/Makevars*` for `Rcpp:::LdFlags|RcppLdFlags|RcppLdPath|Rcpp:::CxxFlags`. `CxxFlags` is not matched by R's regex, so report it as a NOTE-level recommendation.
- **Fix**: Delete the `PKG_LIBS += $(shell ... Rcpp:::LdFlags())` and `PKG_CXXFLAGS = ... Rcpp:::CxxFlags()` lines. Keep `LinkingTo: Rcpp` in DESCRIPTION.
- **Files**: `src/Makevars`, `src/Makevars.win`, `src/Makevars.ucrt`, `src/Makevars.in`
- **Since**: R 4.6.0 (2026-04-24) via `_R_CHECK_RCPP_NOT_NEEDED_` in the `--as-cran` defaults (not in NEWS); CRAN incoming since about 2026-02-19

### COMP-14: Missing Standard C++ Headers (libc++ Transitive Includes, LLVM 23)

- **Severity**: ERROR on r-devel clang flavors, leading to a CRAN problem notification with a 21-day deadline
- **Rule**: C++ code must `#include` every standard header it uses. LLVM 23's libc++ dropped many transitive includes, so code that relied on `<vector>` pulling in `<algorithm>` and similar no longer compiles.
- **CRAN says**: "if declaration(s) (especially in std:) are reported as missing, do ensure that the header(s) which declare them are included. Most commonly <algorithm> or <iterator> is missing." / "People writing C and calling it C++ need to include headers such as <cstdlib>, <cstddef>, <cmath> or <ctime>." (Brian Ripley, https://www.stats.ox.ac.uk/pub/bdr/clang23/README.txt)
- **Detection**: For each `src/*.cpp|*.cc|*.h|*.hpp` translation unit, map used identifiers to their headers and flag any header not directly included. Examples: `std::sort|std::find|std::max_element` need `<algorithm>`; `std::back_inserter|std::distance|std::advance` need `<iterator>`; `std::is_same|std::enable_if` need `<type_traits>`; `size_t|nullptr_t` need `<cstddef>`; `fabs|isnan|sqrt|log` need `<cmath>`; `clock|time|localtime` need `<ctime>`; `malloc|exit|abs` need `<cstdlib>`. This is heuristic, so report as WARNING.
- **Fix**: Add the missing `#include`. Do not depend on `_LIBCPP_KEEP_TRANSITIVE_INCLUDES_LLVM23`, which will be removed in LLVM 24 (the fedora-clang checks define it; the debian-clang checks do not).
- **Files**: `src/*.cpp`, `src/*.cc`, `src/*.h`, `src/*.hpp`, `inst/include/**`
- **Since**: August/September 2026. LLVM 23.1.0 was released 2026-08-25 and adopted on the r-devel-linux debian-clang and fedora-clang flavors; CRAN `clang23` notifications began around 2026-09-04.

### COMP-15: Do Not Suppress Compiler Diagnostics

- **Severity**: WARNING → REJECTION
- **Rule**: "Significant" compiler warnings at install time (e.g. -Wuninitialized, -Warray-bounds from included headers such as Eigen/CGAL on Windows gcc) fail the pretest. Disabling them with `-Wno-*` flags or pragmas violates policy and is itself flagged as non-portable.
- **CRAN says**: Policy: "Packages should not attempt to disable compiler diagnostics, nor to remove other diagnostic information such as symbols in shared objects." / Maintainer report (SurfaceMesh, Sep 2026) after adding `-Wno-array-bounds -Wno-uninitialized`: "the check still generates a non-portability warning which means the package will not pass the CRAN pre-test" (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012550.html)
- **Detection**: Grep src/Makevars* for `-Wno-`, `-w\b`, `-fpermissive`. Grep src/ for `#pragma (GCC|clang) diagnostic ignored`.
- **Fix**: Fix the code, or update or patch the upstream header package (e.g. newer RcppEigen/RcppCGAL). If the warning comes from a dependency compiled during check, note it in submission comments. Local-only quieting is acceptable if conditioned on a developer-only signal (e.g. presence of `.git/`).
- **Files**: `src/Makevars`, `src/Makevars.win`, `src/*`
- **Since**: Long-standing policy; recurring in 2026 (LABTNSCPSS Feb 2026, SurfaceMesh Sep 2026)

---

## Category: Documentation

### DOC-01: Every Exported Function Must Have @return

- **Severity**: REJECTION
- **Rule**: All exported functions must document their return value with `@return` (roxygen2) or `\value{}` (.Rd). Even void functions need this.
- **CRAN says**: "Please add \\value to .Rd files regarding exported methods and explain the functions results in the documentation."
- **Detection**: Parse R files for `@export` without corresponding `@return`. Parse .Rd files for missing `\value{}` sections. Data set docs (`\docType{data}`) are exempt. Aim for parity with R-devel's experimental `_R_CHECK_RD_CONTENTS_VALUE_=true` (r89420, Feb 2026), which lists Rd files without \value (https://stat.ethz.ch/pipermail/r-devel/2026-February/084371.html).
- **Fix**: Add `@return` describing the class and meaning of the return value. For side-effect functions: `@return No return value, called for side effects`.
- **Files**: `R/*.R`, `man/*.Rd`
- **Since**: Pre-2015 — one of the most common rejection reasons for first-time submissions across all studied periods

### DOC-02: Don't Use \dontrun{} Unless Truly Non-Executable

- **Severity**: REJECTION
- **Rule**: `\dontrun{}` should ONLY wrap code that literally cannot run (missing external APIs, credentials, hardware). Use `\donttest{}` for slow examples, `if(interactive()){}` for interactive ones.
- **CRAN says**: "\\dontrun{} should only be used if the example really cannot be executed...Please replace \\dontrun with \\donttest."
- **Detection**: Find `\dontrun{` in .Rd files or `@examples` sections. Flag all instances for review. Auto-classify based on content (network calls vs. pure computation).
- **Fix**: Replace `\dontrun{}` with `\donttest{}` for slow examples. Use `if (interactive()) {}` for interactive code. Only keep `\dontrun{}` for truly non-executable code with a comment explaining why.
- **Files**: `R/*.R`, `man/*.Rd`
- **Since**: Pre-2015 — consistently enforced; note that R 4.0.0 (2020) changed `R CMD check --as-cran` to actually run `\donttest{}` examples, making the distinction between `\dontrun` and `\donttest` critical

### DOC-03: Examples Must Be Fast (< 5 seconds each)

- **Severity**: NOTE → REJECTION
- **Rule**: Individual examples should complete in under 5 seconds. Total check time (examples + vignettes + tests) under 10 minutes. Elapsed (wall-clock) time counts, so network waits trip the NOTE (see NET-01). No special allowance is made for algorithmically slow "workflow" examples.
- **CRAN says**: "* checking examples ... [3s/47s] NOTE / Examples with CPU (user + system) or elapsed time > 5s" (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012386.html) / Ivan Krylov (not CRAN team): "I don't think there's any special consideration for packages whose examples take too long for algorithmic reasons" (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012309.html)
- **Detection**: Cannot fully detect statically — flag examples that involve file I/O, network requests, large computations, or loops with high iteration counts. Flag if `\donttest{}` is not used.
- **Fix**: Reduce iterations, use toy datasets, precompute results, wrap slow code in `\donttest{}`.
- **Files**: `R/*.R`, `man/*.Rd`
- **Since**: Pre-2015 — consistently enforced; more impactful since R 4.0.0 (2020) which runs `\donttest{}` examples under `--as-cran`

### DOC-04: Changes Must Go in .R Files, Not .Rd Files (if using roxygen2)

- **Severity**: WASTED EFFORT
- **Rule**: If package uses roxygen2, all documentation changes must go in R source files. Editing .Rd files directly is pointless — `roxygenize()` overwrites them.
- **CRAN says**: "Since you are using 'roxygen2', please make sure to add a @return-tag in the corresponding .R-file and re-roxygenize() your .Rd-files."
- **Detection**: Check if package uses roxygen2 (look for `RoxygenNote` in DESCRIPTION, `#' @` comments in R files).
- **Fix**: Make all doc changes in R source files, then run `devtools::document()`.
- **Files**: `DESCRIPTION`, `R/*.R`

### DOC-05: All Exported Functions Should Have @examples

- **Severity**: NOTE
- **Rule**: Exported functions should include runnable examples. At least some examples must be unwrapped (not in \donttest or \dontrun).
- **CRAN says**: "All your examples are wrapped in \\donttest{} and therefore do not get tested. Please unwrap the examples if that is feasible..."
- **Detection**: Find exported functions without `@examples`. Find functions where ALL examples are wrapped.
- **Fix**: Add short, fast examples that demonstrate basic usage. Keep at least one unwrapped example per function.
- **Files**: `R/*.R`
- **Since**: Pre-2015 — consistently enforced throughout all studied periods

### DOC-06: Function Names Must Include Parentheses in Docs

- **Severity**: NOTE
- **Rule**: When mentioning function names in documentation text (DESCRIPTION, vignettes, other help pages), include parentheses: `foo()` not `foo`.
- **Detection**: Difficult to fully automate — flag function names mentioned without `()` in prose.
- **Fix**: Add `()` after function names in text: "use the `predict` function" → "use `predict()`"
- **Files**: `DESCRIPTION`, `R/*.R`, `vignettes/*.Rmd`

### DOC-07: Use Canonical CRAN/Bioconductor URLs

- **Severity**: NOTE
- **Rule**: Use canonical URL forms: `https://CRAN.R-project.org/package=pkgname` for CRAN, `https://bioconductor.org/packages/pkgname` for Bioconductor.
- **Detection**: Find non-canonical CRAN URLs (e.g., `cran.r-project.org/web/packages/...`).
- **Fix**: Replace with canonical form.
- **Files**: `R/*.R`, `man/*.Rd`, `DESCRIPTION`, `vignettes/*.Rmd`
- **Since**: R 3.2.0 (2015) — URL accessibility checking introduced; canonical CRAN URL enforcement tightened ~2019

### DOC-08: Lost Braces in Rd Documentation

- **Severity**: REJECTION
- **Rule**: R 4.3+ added `\doi{}`, `\href{}`, `\url{}` macros in Rd. Unescaped literal braces `{` `}` in Rd files now cause parsing errors. Also affects `\itemize{}` blocks using description-style items (`\item{term}{definition}` is for `\describe{}`, not `\itemize{}`).
- **CRAN says**: "Lost braces" or "unknown macro" in Rd parsing. Affected 3000+ packages when R 4.4 enforced stricter checking.
- **Detection**: Run `R CMD check` and look for "Lost braces" warnings. Statically: grep man/*.Rd for unescaped `{` or `}` outside of known macros. Check for `\itemize{ \item{...}{...} }` patterns (should use `\describe{}` instead).
- **Fix**: Escape literal braces with `\{` and `\}`. Replace `\itemize{ \item{term}{def} }` with `\describe{ \item{term}{def} }`. If using roxygen2, update to roxygen2 >= 7.3.0 which handles this automatically.
- **Files**: `man/*.Rd`, `R/*.R` (if using roxygen2)

### DOC-09: HTML5 Rd Validation

- **Severity**: NOTE → REJECTION
- **Rule**: R 4.4+ validates Rd-generated HTML against HTML5 spec. Rd files producing elements removed from HTML5 (like `<font>`, `<center>`, `<strike>`) are flagged.
- **CRAN says**: NOTE about HTML validation issues in rendered help pages.
- **Detection**: Check man/*.Rd for raw HTML that uses deprecated HTML5 elements.
- **Fix**: Remove deprecated HTML elements from Rd files. Use standard Rd formatting macros instead. Update roxygen2 to >= 7.2.1 and re-document.
- **Files**: `man/*.Rd`, `R/*.R`
- **Since**: R 4.2.0 (2022) — HTML5 validation added to `--as-cran` checks via `_R_CHECK_RD_VALIDATE_RD2HTML_`; enforcement wave with deadline 2022-09-01

### DOC-10: \donttest Examples Now Executed Under --as-cran

- **Severity**: REJECTION
- **Rule**: Since R 4.0.0, `R CMD check --as-cran` actually runs `\donttest{}` examples rather than merely instructing the tester to do so. This means code wrapped in `\donttest{}` must be correct, must not require credentials or special hardware, and must complete within CRAN's time limits. Examples that were "safe" in `\donttest{}` before R 4.0.0 may now cause check failures.
- **CRAN says**: "* checking examples ... [30s] ERROR. Running examples in 'package-Ex.R' failed"
- **Detection**: Find `\donttest{}` blocks in .Rd files or `@examples` sections. Flag examples that: contain network calls without error handling, use credentials/API keys, perform slow computations (especially plot functions like `spplot()`), or depend on non-CRAN resources. Check if examples inside `\donttest{}` would complete in < 10 seconds on slow hardware.
- **Fix**: Move truly non-runnable examples to `\dontrun{}` with a comment explaining why. Ensure `\donttest{}` examples handle failures gracefully. Add error handling around network calls. Reduce computation in plot examples. Test timing on CRAN-like hardware (roughly 2x slower than typical dev machines).
- **Files**: `R/*.R`, `man/*.Rd`
- **Since**: R 4.0.0 (2020) — `\donttest{}` examples now run by `--as-cran`; can be temporarily disabled via `_R_CHECK_DONTTEST_EXAMPLES_=false`

### DOC-11: Duplicated Vignette Titles

- **Severity**: NOTE
- **Rule**: Each vignette must have a unique title (VignetteIndexEntry). Duplicated titles cause issues because they are used as hyperlinks on CRAN package pages.
- **CRAN says**: R CMD check NOTE about duplicated vignette titles/index entries.
- **Detection**: Parse all vignette files in `vignettes/` for `%\VignetteIndexEntry{}` declarations. Flag any duplicated values.
- **Fix**: Give each vignette a unique, descriptive title in its `%\VignetteIndexEntry{}` metadata.
- **Files**: `vignettes/*.Rmd`, `vignettes/*.Rnw`
- **Since**: R 3.6.0 (2019) — R CMD check began checking for duplicated vignette titles

### DOC-12: Relative Links in Rd and Vignettes Must Resolve

- **Severity**: NOTE
- **Rule**: Relative URLs in Rd files and vignettes (for example `../doc/foo.html`, `../../otherpkg/html/topic.html`, `../help/topic`) must resolve against the installed package's help system. Broken ones are reported in a new check step.
- **CRAN says**: "checking relative paths in package URLs ... NOTE  Found the following (possibly) invalid URLs:  URL: <url>  From: <file>"
- **Detection**: Extract `\href{}`/`\url{}` targets in `man/*.Rd` and `href=`/markdown links in `vignettes/*` that have no scheme. Flag paths that point to files the package does not install (no matching `inst/doc` file, vignette output or help topic).
- **Fix**: Use `\link[pkg]{topic}` for help cross-references, `vignette("name", package = "pkg")` text, or absolute `https://CRAN.R-project.org/package=pkg/...` URLs.
- **Files**: `man/*.Rd`, `vignettes/*.Rmd`, `vignettes/*.Rnw`, `R/*.R` (roxygen)
- **Since**: R 4.6.0 (2026-04-24), `--as-cran` (`R_check_urls_relative_paths`; not in NEWS); CRAN regular checks set `_R_CHECK_URLS_RELATIVE_PATHS_=true`

### DOC-13: Rd Bibliography Citations Must Be Shown and Built with R >= 4.6.0

- **Severity**: NOTE
- **Rule**: When using the R 4.6.0 Rd bibliography macros, every entry cited with `\bibcitet{}`/`\bibcitep{}` must appear in a `\bibshow{}` (usually in `\references{}`). The tarball must be built with R >= 4.6.0 so that `build/partial.rdb` contains the expanded macros.
- **CRAN says**: "Bibentries cited but not shown in Rd file 'x.Rd':" and "Found bibentries with unexpected macro expansions.  Rebuild with R >= 4.6.0?"
- **Detection**: For each `man/*.Rd`, collect the `\bibcite[tp]{...}` keys and the `\bibshow{...}` keys (`*` means all keys cited so far). Flag cited keys not covered. If any `\bib*` macro is used, check that `build/partial.rdb` exists in the tarball, that `inst/REFERENCES.R` or `inst/REFERENCES.bib` exists for local keys, and that `bibtex` is in Suggests when `.bib` is used.
- **Fix**: Add `\references{ \bibshow{*} }`. Rebuild with R >= 4.6.0. Add `Depends: R (>= 4.6.0)` (see DOC-14).
- **Files**: `man/*.Rd`, `inst/REFERENCES.R`, `inst/REFERENCES.bib`, `DESCRIPTION`
- **Since**: R 4.6.0 (2026-04-24), `--as-cran` (`R_check_Rd_bibentries_cited_not_shown`; not in NEWS); CRAN regular checks set `_R_CHECK_RD_BIBENTRIES_CITED_NOT_SHOWN_=true`

### DOC-14: New R 4.6.0 Rd Syntax Requires `Depends: R (>= 4.6.0)`

- **Severity**: WARNING (check behaviour on older R is UNVERIFIED; NEWS states it as a requirement)
- **Rule**: Rd files that use `\linkS4class[pkg]{Class}`, `\linkS4methods{}`, `\manual{}{}` or `\bibcitet`/`\bibcitep`/`\bibshow`/`\bibinfo` need a formal `R (>= 4.6.0)` dependency.
- **CRAN says**: "Packages with the new syntax need to formally depend on 'R >= 4.6.0'." (R 4.6.0 NEWS, about `\linkS4class[<pkg>]{}`)
- **Detection**: Grep `man/*.Rd` for `\\linkS4class\[|\\linkS4methods\{|\\manual\{|\\bibcite[tp]\{|\\bibshow\{|\\bibinfo\{`. If any match, parse `Depends:` for `R (>= x.y.z)` and flag when it is missing or lower than 4.6.0.
- **Fix**: Add or raise `Depends: R (>= 4.6.0)`, or use the old form `\link[pkg:Class-class]{Class}`.
- **Files**: `man/*.Rd`, `DESCRIPTION`
- **Since**: R 4.6.0 (2026-04-24)

### DOC-15: \arguments Requires a Matching \usage

- **Severity**: NOTE (blocks pretest)
- **Rule**: An Rd file that documents `\arguments` must have a `\usage` section. Entries in `\usage` that parse as R calls must correspond to real functions with matching arguments. Overview pages and non-R (e.g. JavaScript) docs should use `\describe{}` instead of `\arguments{}`.
- **CRAN says**: "Rd files without \usage: [...] \arguments should not be documented without \usage." (pretest NOTE, "Check: Rd contents") and Uwe Ligges, 2026-09-28: "And you should really add the usage line, a usage line does not mean these are executed." (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012558.html). Ivan Krylov: "Entries in \usage{} that parse as valid R function calls must correspond to real R functions with matching arguments." (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012566.html)
- **Detection**: For each man/*.Rd, flag `\arguments{` present and `\usage{` absent. In roxygen, flag blocks documenting `NULL` or `"_PACKAGE"`-style topics that have `@param` but no `@usage`.
- **Fix**: Add `#' @usage fn(x, ...)`, or remove `@param` tags and describe arguments in `@details`/`\describe{}`.
- **Files**: `man/*.Rd`, `R/*.R`
- **Since**: Long-standing tools::checkRdContents behaviour; R 4.6.0 extended related checkDocFiles notes; seen twice Jul-Sep 2026 (causalDisco, shinylight)

---

## Category: Licensing

### LIC-01: License Must Be in CRAN Database

- **Severity**: REJECTION
- **Rule**: Only licenses from CRAN's official license database are accepted. See `https://svn.r-project.org/R/trunk/share/licenses/license.db`.
- **Detection**: Parse License field, check against known CRAN-accepted licenses (GPL-2, GPL-3, LGPL-2.1, LGPL-3, MIT, BSD-2-clause, BSD-3-clause, Apache-2.0, Artistic-2.0, CC BY 4.0, etc.).
- **Fix**: Use a standard CRAN license. For MIT: `MIT + file LICENSE` with a LICENSE file containing year and copyright holder.
- **Files**: `DESCRIPTION`, `LICENSE`

### LIC-02: License Changes Must Be Highlighted

- **Severity**: REJECTION
- **Rule**: When updating a package, any change to the License field must be explicitly mentioned in the submission comment.
- **Detection**: Compare with previous CRAN version (if update). Flag if License field changed.
- **Fix**: Add note to cran-comments.md and submission form.
- **Files**: `DESCRIPTION`, `cran-comments.md`

### LIC-03: No Dual Licensing Within Package

- **Severity**: REJECTION
- **Rule**: A package must be licensed as a whole under one license (or a standard compound like "GPL-2 | GPL-3"). Individual files cannot have different licenses from the package. CRAN's position: "A package can only be licensed as a whole."
- **CRAN says**: "A package can only be licensed as a whole."
- **Detection**: Check for per-file license headers that differ from the DESCRIPTION License field. Check for LICENSE.md files referencing multiple different licenses for different components.
- **Fix**: Choose a single license for the entire package. If incorporating code from other licenses, ensure license compatibility and note copyright holders in Authors@R with cph role.
- **Files**: `DESCRIPTION`, `LICENSE`, `R/*.R`, `src/*`

---

## Category: Size & Performance

### SIZE-01: Package Tarball Should Be < 10MB

- **Severity**: REJECTION
- **Rule**: Source tarball should not exceed 10MB. Data and documentation each limited to 5MB. **Updated Nov 2025:** Limit raised from 5MB to 10MB. Data and documentation each limited to 5MB. A modestly increased limit can be requested at submission for vendor files.
- **Detection**: Check file sizes. Identify large files (data, vignette images, bundled libraries).
- **Fix**: Compress data more aggressively. Move large datasets to separate data-only package. Reduce vignette image resolution. Remove unnecessary bundled files.
- **Files**: Entire package
- **Since**: Pre-2015 — original limit was 5MB (tarball, data, and documentation each); tarball limit raised to 10MB in November 2025

### SIZE-02: Check Time Must Be < 10 Minutes

- **Severity**: REJECTION
- **Rule**: Total time for examples + vignettes + tests must be under 10 minutes on CRAN infrastructure (which is slower than typical dev machines). The binding measurement is the r-devel-windows-x86_64 incoming pretest, which is slower than Linux. The NOTE causes automatic pretest rejection and is listed at the bottom of the pretest email, where it is easy to miss. CRAN can manually overrule it for large packages ("That's why CRAN overruled the 10 min threshold and let your package pass.", Uwe Ligges, 2026-07-14). Installation time alone (~1 minute) is "perfectly fine". If CRAN has not replied after 2 weeks, send a reminder. CRAN's incoming hard-kill timeouts were raised to 180m in 2026; these are separate from this 10-minute guidance.
- **CRAN says**: "Flavor: r-devel-windows-x86_64 / Check: Overall checktime, Result: NOTE / Overall checktime 25 min > 10 min" (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012533.html) / Uwe Ligges: "1 minute is perfectly fine. The oeverall check time should not exceed 10 minutes." [sic] (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012338.html) / "Note we receive roughly 300 messages per day (including submission mails and the mails we send out). Once 2 weeks passed, please send us a reminder in case we have not responded." (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012456.html)
- **Detection**: Run `R CMD check --as-cran` and check timing output. Flag if > 5 minutes (safety margin).
- **Fix**: Reduce test/example/vignette runtime. Use `\donttest{}` for slow examples. Skip slow tests conditionally. Use precomputed vignettes.
- **Files**: `tests/**/*.R`, `R/*.R`, `vignettes/*.Rmd`
- **Since**: Pre-2015 — consistently enforced; R 3.5.0 (2018) added configurable check timeouts via environment variables

---

## Category: Cross-Platform

### PLAT-01: Must Work on 2+ Major Platforms

- **Severity**: REJECTION
- **Rule**: Must make all reasonable efforts for cross-platform portable code. Must normally work on at least 2 of: Linux, macOS, Windows.
- **Detection**: Check for platform-specific code (system calls, file paths with backslashes, Windows-specific APIs). Check SystemRequirements field.
- **Fix**: Use cross-platform R functions. Conditional platform-specific code with `.Platform$OS.type`.
- **Files**: `R/*.R`, `src/*`, `DESCRIPTION`
- **Since**: Pre-2015 — consistently enforced; Solaris checks were particularly problematic during 2015-2019 before Solaris was dropped from CRAN check flavors

### PLAT-02: No Binary Executables in Source Package

- **Severity**: REJECTION
- **Rule**: Source packages must not contain binary executable code. Java .class/.jar files need sources in a `java/` directory.
- **Detection**: Scan for binary files (`.exe`, `.dll`, `.so`, `.dylib`, `.class`, `.o`).
- **Fix**: Remove binaries. Include source code. Build from source during installation.
- **Files**: Entire package

### PLAT-03: Hard-Coded macOS Big Sur arm64 Paths/Targets

- **Severity**: WARNING (install failure on CRAN macOS arm64 builders)
- **Rule**: From R 4.6.0, CRAN macOS arm64 binaries target macOS 14 (package type `mac.binary.sonoma-arm64`), and external libraries live under `https://mac.r-project.org/bin/darwin23/arm64/`. `configure` scripts must not hard-code `darwin20/arm64`, `big-sur-arm64` or `-mmacosx-version-min=11` for arm64. Intel (`big-sur-x86_64`) stays on the macOS 11 target.
- **CRAN says**: "R 4.6.0 CRAN arm64 builds use Xcode 26.0.1, macOS 14 target and 14.4 SDK with package type mac.binary.sonoma-arm64." / "We are no longer building binaries for macOS versions before 11 ... and before macOS 14 on Apple Silicon." (https://mac.r-project.org/). The external_libs policy now points to `darwin23/arm64` (SVN r6797).
- **Detection**: Grep `configure*`, `src/Makevars*` and `tools/*` for `darwin20/arm64`, `big-sur-arm64`, `mac.binary.big-sur-arm64`, and arm64-specific `macosx-version-min=1[0-3]`.
- **Fix**: Derive paths from `R CMD config` / `.Platform$pkgType`, or use `pkg-config`. Do not hard-code OS-versioned directories.
- **Files**: `configure`, `configure.ac`, `src/Makevars.in`, `tools/*.R`
- **Since**: R 4.6.0 (2026-04-24); external_libs policy r6797 (2026-02-20)

### PLAT-04: No Dependence on Extended Precision or OS-String Sniffing

- **Severity**: WARNING → REJECTION (via linux-arm64 / macOS arm64 additional checks)
- **Rule**: Tests must not assert results that depend on long-double precision, or on chaotic or non-converged algorithm output. arm64 has no extended precision. OS detection must not assume "not darwin" means Solaris or Linux-x86.
- **CRAN says**: "Additional issues checked: linux-arm64: Status: 4 WARNINGs, 5 NOTEs" (akin pretest email, https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012402.html) / Simon Urbanek: "TL;DR this is not macOS specific - your test example is chaotic and thus will be influenced even by small changes in the precision beyond what is guaranteed, i.e. your assumptions are not generally valid and thus the tests don't work." / "The arm CPUs used by Macs only support double precision, so any operations that are otherwise preformed with extended precision will be different." (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012306.html)
- **Detection**: Flag `expect_equal`/`identical` on floating-point results with `tolerance = 0` or tiny tolerances. Flag `R.version$os` / `Sys.info()["sysname"]` regex branches that fall through to `system("/bin/kstat ...")` or other platform-specific commands without an else-error (the akin failure came from a dependency doing `grepl("darwin|solaris", R.version$os)`).
- **Fix**: Use tolerances. Test deterministic components on saved fixtures. Test with `R --disable-long-double` builds or arm64 CI (`ubuntu-24.04-arm` runners, QEMU `--platform linux/arm64`). Use `.Platform`/`Sys.info()` with explicit cases.
- **Files**: `tests/**`, `R/*.R`
- **Since**: 2026, as linux-arm64 additional checks appear in incoming pretests

---

## Category: Dependencies

### DEP-01: Strong Dependencies Must Be on CRAN or Bioconductor

- **Severity**: REJECTION
- **Rule**: Packages in Depends, Imports, LinkingTo must be available from CRAN or the Bioconductor *software* repository. Bioconductor annotation and experiment-data packages may only appear in Suggests/Enhances (no `Additional_repositories` needed for them). Other non-CRAN Suggests/Enhances need `Additional_repositories` or access instructions in Description.
- **CRAN says**: "Packages on which a CRAN package depends should be available from a standard repository. The strong dependencies (i.e., packages listed in the 'Depends', 'Imports' or 'LinkingTo' fields) should be available from CRAN or the Bioconductor software repository. If any mentioned in 'Suggests' or 'Enhances' fields are not from one of these or the Bioconductor annotation and experiment data repositories, where to obtain them at a repository should be specified in an 'Additional_repositories' field of the DESCRIPTION file (as a comma-separated list of repository URLs) or for other means of access, described in the 'Description' field." (CRAN Repository Policy)
- **Detection**: Parse DESCRIPTION dependencies. Check each against CRAN/Bioconductor availability. Flag strong deps that are BioC annotation/experiment packages (BiocManager repositories `BioCann`, `BioCexp`; e.g. `org.Hs.eg.db`, `BSgenome.*`, `TxDb.*`, `*Data` experiment packages). These are Suggests-only.
- **Fix**: Move non-CRAN dependencies to Suggests with conditional usage, or add `Additional_repositories`. Move BioC data/annotation packages to Suggests and use them conditionally.
- **Files**: `DESCRIPTION`
- **Since**: Pre-2015 (general); BioC-software-only restriction since CRAN policy SVN r6734 (committed 2025-12-15; r6738 on 2025-12-19 only wrapped "Bioconductor" in `@I{}`), published on the live policy page by 2026-02-20

### DEP-02: Suggested Packages Must Be Used Conditionally

- **Severity**: REJECTION
- **Rule**: Packages in Suggests must be used conditionally in examples, tests, and vignettes with `requireNamespace("pkg", quietly = TRUE)`.
- **Detection**: Find `library(pkg)` or `pkg::func()` for Suggests packages without conditional wrapping.
- **Fix**: Wrap in `if (requireNamespace("pkg", quietly = TRUE)) { ... }`.
- **Files**: `R/*.R`, `tests/**/*.R`, `vignettes/*.Rmd`
- **Since**: Pre-2015 — enforcement tightened significantly in R 3.4.0 (2017) when `_R_CHECK_SUGGESTS_ONLY_` and `_R_CHECK_DEPENDS_ONLY_` were applied to vignette re-building

### DEP-03: Monitor Dependency Health

- **Severity**: RECOMMENDED
- **Rule**: If any package in Imports/Depends has failing CRAN checks or has been archived, your package is at risk of cascading removal without warning.
- **CRAN says**: "Archived on [date] as requires archived package '[name]'"
- **Detection**: Check CRAN check status of all dependencies (informational — can't fully automate without network access).
- **Fix**: Monitor dependency health at https://cran.r-project.org/web/checks/. Have contingency plans for critical dependencies. Consider CRANhaven (cranhaven.r-universe.dev) for emergency installs.
- **Files**: `DESCRIPTION`

---

## Category: Internet & External Resources

### NET-01: Must Fail Gracefully When Resources Are Unavailable

- **Severity**: REJECTION
- **Rule**: Package must not error or produce check warnings if internet resources are unavailable, changed, or rate-limited.
- **CRAN says**: "Archived on <date> for policy violation. . On Internet access." / "Archived on <date> for repeated policy violation. . On Internet access." (CRAN `X-CRAN-Comment`) / Uwe Ligges, 2026-05-18: "Given the timings I guess these are internet access issues with US government web sites that we frequently observe. Simply define a timeout for internet access and exit gracefully if you hit it." (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012391.html)
- **Detection**: Find URL requests (httr, curl, download.file). Check if wrapped in tryCatch or similar error handling.
- **Fix**: Wrap all network calls in `tryCatch()`. Return informative error messages. Use `\donttest{}` for examples requiring network. **Important (R 4.5+ enforcement):** Graceful failure must extend to ALL downstream code in examples and vignettes, not just the network-calling function itself. If `read_data()` returns NULL on failure, any vignette code that uses the result must also handle the NULL case gracefully. Set explicit timeouts (e.g. `httr2::req_timeout()`, `options(timeout = )` scoped with on.exit) and treat timeouts as failures to handle gracefully. Slow remote servers otherwise surface as example-timing NOTEs on CRAN's European check machines (DOC-03). Failures inside dependencies you call (e.g. GDAL/stars remote reads) are your responsibility: "In the end it is your responsibility since you are providing the API, the user shouldn't' need to know anything about the intricacies of what happens under the hood in other packages." (Simon Urbanek, 2026-02-18, https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012285.html). Do not assume fixed TCP ports are free; catch server-start errors ("In general, no fixed port number can be assumed to be available on the machine running R CMD check.", Ivan Krylov, https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012559.html).
- **Files**: `R/*.R`
- **Since**: Pre-2015 — CRAN policy has long required graceful failure; enforcement intensified 2020-2022 with tighter deadlines and faster archival. 2026: Internet access was the reason for 25 of 29 policy-violation archivals Feb-Sep 2026; repeat offenders are archived for "repeated policy violation".

### NET-02: Must Use HTTPS

- **Severity**: NOTE
- **Rule**: All URLs in code and documentation must use HTTPS, not HTTP.
- **Detection**: Grep for `http://` URLs (excluding localhost).
- **Fix**: Replace `http://` with `https://`.
- **Files**: `R/*.R`, `man/*.Rd`, `DESCRIPTION`, `vignettes/*.Rmd`, `README.md`
- **Since**: R 3.2.0 (2015) — URL checking introduced; HTTPS preference formalized ~2017-2019 policy; `ftps` removed as acceptable in 2023, leaving only `https`

### NET-03: Rate Limit Policy

- **Severity**: REJECTION
- **Rule**: Package code must be mindful of rate limiting on external APIs. CRAN policy revision 6277 (Aug 2024) explicitly requires packages to avoid triggering HTTP 429/403 responses, especially in automated contexts (CRAN check farms hit APIs from shared IPs).
- **CRAN says**: "Packages should be written with awareness that they will be run on shared infrastructure" (paraphrased from policy revision).
- **Detection**: Find HTTP request code. Check for rate-limiting awareness: retry logic with backoff, configurable delays, caching of responses. Flag packages making many sequential HTTP requests without delays.
- **Fix**: Add exponential backoff for retry logic. Cache responses where possible. Add configurable delay between requests. Respect Retry-After headers.
- **Files**: `R/*.R`

---

## Category: Submission Process

### SUB-01: Run R CMD check --as-cran on Exact Tarball

- **Severity**: PREREQUISITE
- **Rule**: Must run `R CMD check --as-cran` on the exact tarball that will be uploaded, using current R-devel.
- **Detection**: Remind user. Check for presence of `*.Rcheck/` directory with recent results.
- **Fix**: Build with `R CMD build .` then check with `R CMD check --as-cran <tarball>`.

### SUB-02: Test on Multiple Platforms

- **Severity**: RECOMMENDED
- **Rule**: Test on Windows (win-builder), macOS, and Linux before submitting. Use rhub for automated multi-platform testing.
- **Detection**: Remind user. Check for `rhub` in Suggests or CI configuration.
- **Fix**: Run `devtools::check_win_devel()`, `rhub::rhub_check()`.

### SUB-03: Check Reverse Dependencies (for updates)

- **Severity**: REQUIRED (for updates)
- **Rule**: Must verify that packages depending on yours still pass R CMD check after your changes.
- **Detection**: Check if package is already on CRAN. If so, remind about revdep checks.
- **Fix**: Run `revdepcheck::revdep_check()`. Document results in cran-comments.md. Add new function arguments at the end with defaults. Inserting a positional argument breaks reverse dependencies that call positionally, and CRAN emails about strong reverse-dependency conflicts ("If you're adding a new parameter to a function, the safest way to do so is to add it after all the other parameters, and set a default value so the old usage will still produced the same results.", Duncan Murdoch, https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012394.html). Base-R tooling: `tools::package_dependencies(reverse = TRUE, which = 'most')`, `utils::download.packages()`, `tools::check_packages_in_dir()`.

### SUB-04: Create cran-comments.md

- **Severity**: RECOMMENDED
- **Rule**: Document test environments, R CMD check results, and any NOTEs with explanations.
- **Detection**: Check for existence of `cran-comments.md`.
- **Fix**: Create with `usethis::use_cran_comments()`. Document: test environments, R CMD check results (0 errors, 0 warnings, 0 notes — or explain notes), reverse dependency results.

### SUB-05: First Submission Gets "New submission" NOTE

- **Severity**: INFORMATIONAL
- **Rule**: New packages always get a "New submission" NOTE. This is expected and unavoidable. Document it in cran-comments.md.
- **Detection**: Check if package is already on CRAN. If not, this NOTE will appear.
- **Fix**: Add to cran-comments.md: "This is a new submission."

### SUB-06: Submission Frequency Limit

- **Severity**: POLICY
- **Rule**: Established packages should not submit updates more than once every 1-2 months.
- **CRAN says**: "CRAN incoming feasibility, Result: NOTE ... Number of updates in past 6 months: 7" (akin, May 2026 pretest)
- **Detection**: Check last CRAN publication date (if already on CRAN).
- **Fix**: Plan releases carefully. Batch fixes together.

### SUB-07: CRAN Vacation Periods

- **Severity**: INFORMATIONAL
- **Rule**: CRAN has a winter break (~Dec 23 - Jan 7) during which no submissions are processed. Automated submission tools (devtools) during this period can trigger IP blocks. Summer closure too: 2026-08-05 to 2026-08-19. Deadline-extension requests during closures go to CRAN@R-project.org (Uwe Ligges, 2026-08-23, https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012519.html), not the list.
- **Detection**: Informational — flag if submitting in December/January.
- **Fix**: Plan submissions to avoid the vacation period. If IP is blocked, email CRAN with your IP address.

---

## Category: Package Naming

### NAME-01: Case-Insensitive Uniqueness Across All CRAN History

- **Severity**: REJECTION
- **Rule**: Package name must not match (case-insensitively) any current or past CRAN package, or any current Bioconductor package.
- **Detection**: Check proposed name against CRAN archive and Bioconductor. Use `available::available("pkgname")`.
- **Fix**: Choose a different name.
- **Files**: `DESCRIPTION`

### NAME-02: Package Names Are Permanent

- **Severity**: INFORMATIONAL
- **Rule**: Once submitted, the package name generally cannot be changed. CRAN retains naming rights.
- **Detection**: Informational — flag for first-time submissions.
- **Fix**: Choose your name carefully before first submission.

---

## Category: Miscellaneous

### MISC-01: NEWS.md Should Exist

- **Severity**: RECOMMENDED
- **Rule**: Include a NEWS.md file documenting changes between versions.
- **Detection**: Check for `NEWS.md` or `NEWS` file.
- **Fix**: Create with `usethis::use_news_md()`.

### MISC-02: URLs Must Be Valid

- **Severity**: NOTE
- **Rule**: All URLs in package files must resolve (no 404s, redirects should be updated to final URL).
- **CRAN says**: "Found the following (possibly) invalid URLs: URL: From: README.md Message: Empty URL" (saferDev pretest, May 2026, https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012388.html)
- **Detection**: Run `urlchecker::url_check()`. Flag `href=""`/`[]()` empty links in README.md, NEWS.md and vignettes (R 4.6.0 installs README.md into HTML help). Reproduce with `tools:::.pandoc_md_for_CRAN()`.
- **Fix**: Update or remove broken URLs. CRAN does not tolerate permanent redirections (301s) — update to the final URL directly. For sites behind bot protection (Cloudflare 403) or geo-blocking, avoid `\url{}` and use `\verb{}` or `\samp{}` (not `\code{}`: "\code{} is formally reserved for R code fragments [...] To disable the hyperlink, you could use \verb{} instead, or \samp{} if you want it single quotes.", Sebastian Meyer, 2026-03-03, https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012305.html), or explain in submission comments ("please simply say so in your submission comments", Uwe Ligges, 2026-04-16, https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012368.html).
- **Files**: All text files
- **Since**: R 3.2.0 (2015) — URL accessibility checking introduced; enhanced with `tools::check_package_urls()` in R 4.2.0 (2022)

### MISC-03: Spelling Should Be Correct

- **Severity**: NOTE
- **Rule**: Spelling errors in documentation trigger NOTEs. Use WORDLIST file for technical terms.
- **Detection**: Run `spelling::spell_check_package()`.
- **Fix**: Fix spelling errors. Add legitimate technical terms to `inst/WORDLIST`.
- **Files**: `R/*.R`, `man/*.Rd`, `DESCRIPTION`, `vignettes/*.Rmd`

### MISC-04: .Rbuildignore Must Be Properly Configured

- **Severity**: NOTE
- **Rule**: Development files (`.git/`, `.Rproj.user/`, CI configs, etc.) should be in `.Rbuildignore` to keep tarball clean.
- **Detection**: Check for common development files not in `.Rbuildignore`.
- **Fix**: Add entries to `.Rbuildignore`. Use `usethis::use_build_ignore()`.
- **Files**: `.Rbuildignore`

### MISC-05: Makefile Must Be POSIX-Compatible

- **Severity**: REJECTION
- **Rule**: Makefiles in src/ must use only POSIX make features, OR declare `SystemRequirements: GNU make`. Non-portable features: `ifeq`/`ifneq`, `${shell}`, `${wildcard}`, `+=`, `:=`, `$<`, `$^`, `.PHONY`.
- **CRAN says**: Check warnings about non-portable Makefile features.
- **Detection**: Grep src/Makevars for GNU make extensions. Check if SystemRequirements includes "GNU make".
- **Fix**: Either use only POSIX make features, or add `SystemRequirements: GNU make` to DESCRIPTION.
- **Files**: `src/Makevars`, `src/Makevars.win`, `DESCRIPTION`
- **Since**: R 3.3.0 (2016) — GNU extension detection in Makefiles added to R CMD check

### MISC-06: NEWS File Format Validation

- **Severity**: NOTE
- **Rule**: R 4.3+ applies stricter parsing to NEWS and NEWS.md files. Malformed headings, inconsistent version numbering, or non-standard date formats cause NOTEs.
- **CRAN says**: NOTE about "Cannot extract version info from the following section titles" or similar NEWS parsing warnings.
- **Detection**: If NEWS.md exists, check that version headings match pattern `# package version` or `# package version (date)`. Check that versions are valid R version strings.
- **Fix**: Use standard format: `# packagename 1.2.3` or `# packagename 1.2.3 (2024-01-15)`. Use `usethis::use_news_md()` for template.
- **Files**: `NEWS.md`, `NEWS`

### MISC-07: URL Permanent Redirects Not Tolerated

- **Severity**: NOTE → REJECTION
- **Rule**: CRAN does not tolerate permanent URL redirections (HTTP 301). URLs in DESCRIPTION, CITATION, README, vignettes, and Rd files must point to their final destination directly. HTTP-to-HTTPS redirects, www/non-www redirects, and domain migration redirects all trigger NOTEs. DOI redirects are exempt (DOIs always redirect).
- **CRAN says**: "Found the following (possibly) invalid URLs: URL: http://example.com From: DESCRIPTION Status: 301 Message: Moved Permanently". From R 4.6.0, `--as-cran` sets `_R_CHECK_URLS_SHOW_301_STATUS_`, so moved URLs are reported as `URL: <old> (moved to <new>)` with `Status: 301` / `Message: Moved Permanently`.
- **Detection**: Check all URLs in package files. For each URL, verify it does not return a 301 redirect status. Specifically flag: `http://` URLs where the HTTPS version exists, URLs to domains known to have migrated, URLs with `www.` when the non-www version is canonical (or vice versa). DOI URLs (`https://doi.org/...`) are exempt.
- **Fix**: Update all URLs to their final destination. Replace `http://` with `https://` where the site supports it. Use the `urlchecker` package to validate all URLs before submission: `urlchecker::url_check()`.
- **Files**: `DESCRIPTION`, `man/*.Rd`, `vignettes/*.Rmd`, `README.md`, `inst/CITATION`
- **Since**: R 3.2.0 (2015) — URL accessibility checking introduced; redirect intolerance tightened progressively through R 4.0+ (2020) with enhanced parallel URL checking; explicit 301 status display under --as-cran from R 4.6.0

---

## Category: Encoding

### ENC-01: Missing Encoding Field in DESCRIPTION

- **Severity**: WARNING
- **Rule**: If the DESCRIPTION file contains any non-ASCII characters (in Title, Description, Authors@R, or any field), the `Encoding:` field must be present. Only three encodings are portable: `UTF-8`, `latin1`, `latin2`. UTF-8 is strongly recommended.
- **CRAN says**: "If the DESCRIPTION file is not entirely in ASCII it should contain an 'Encoding' field."
- **Detection**: Read DESCRIPTION as bytes. If any byte > 0x7F exists, check that the `Encoding:` field is present.
- **Fix**: Add `Encoding: UTF-8` to DESCRIPTION.
- **Files**: `DESCRIPTION`

### ENC-02: Non-ASCII Characters in R Source Code

- **Severity**: WARNING
- **Rule**: R source files must use only ASCII characters in code. Non-ASCII characters in string literals must use `\uxxxx` or `\U{xxxxxxxx}` escape sequences. Non-ASCII in comments is tolerated but discouraged. Non-ASCII in identifiers (variable names, function names) is always rejected.
- **CRAN says**: "Portable packages must use only ASCII characters in their R code, except perhaps in comments. Use \\uxxxx escapes for other characters."
- **Detection**: Read each `R/*.R` file as bytes. For each line, check if any byte > 0x7F exists. Skip lines that are pure comments (start with `#` after optional whitespace).
- **Fix**: Replace non-ASCII characters in strings with `\uxxxx` escape sequences. Use `stringi::stri_escape_unicode()` to convert.
- **Files**: `R/*.R`

### ENC-03: Non-Portable \x Escape Sequences

- **Severity**: REJECTION
- **Rule**: Using `\xNN` escape sequences for non-ASCII characters in R strings is non-portable because `\x` produces raw bytes interpreted according to the locale's encoding. The portable alternative is `\uNNNN` which always produces Unicode code points.
- **CRAN says**: "Change strings to use \\u escapes instead of \\x, as the latter was only correct under Latin-1 encoding but not portable."
- **Detection**: Scan `R/*.R` files for `\x[0-9a-fA-F]{2}` patterns where the hex value is >= 0x80 (non-ASCII range).
- **Fix**: Replace `\xNN` with the equivalent `\uNNNN` Unicode escape. For example, `\xe9` (e-acute in Latin-1) becomes `\u00e9`.
- **Files**: `R/*.R`

### ENC-04: UTF-8 BOM in Source Files

- **Severity**: WARNING
- **Rule**: UTF-8 files must not include a Byte Order Mark (BOM, byte sequence EF BB BF). BOMs cause invisible characters in string comparisons, broken column names in data files, and LaTeX compilation failures for vignettes.
- **CRAN says**: "Found non-ASCII strings ... which cannot be translated" (when BOM causes parsing issues)
- **Detection**: Read the first 3 bytes of each source file (R/*.R, man/*.Rd, vignettes/*.Rmd, DESCRIPTION, NAMESPACE). Check if they are EF BB BF.
- **Fix**: Remove the BOM. Most editors can save as "UTF-8 without BOM". In code: read the file, strip the leading BOM bytes, write back.
- **Files**: `R/*.R`, `man/*.Rd`, `vignettes/*.Rmd`, `DESCRIPTION`, `NAMESPACE`

### ENC-05: Missing VignetteEncoding Declaration

- **Severity**: WARNING
- **Rule**: Vignette source files (.Rmd, .Rnw) must declare their encoding via `%\VignetteEncoding{UTF-8}`. Without this, vignette builds may fail on CRAN check platforms with different default locales.
- **CRAN says**: "The encoding is not UTF-8. We will only support UTF-8 in the future."
- **Detection**: Find all vignette files in `vignettes/` directory (.Rmd, .Rnw, .Rtex). Check for `%\VignetteEncoding{` directive.
- **Fix**: Add `%\VignetteEncoding{UTF-8}` to the vignette preamble. For .Rmd files, this goes in the YAML header area.
- **Files**: `vignettes/*.Rmd`, `vignettes/*.Rnw`, `vignettes/*.Rtex`

### ENC-06: Unmarked UTF-8 Strings in Data Files

- **Severity**: NOTE
- **Rule**: When R data files (.rda, .RData) contain strings with non-ASCII characters, each string should have its encoding properly marked (via `Encoding()` function). Unmarked non-ASCII strings produce a warning that can block acceptance.
- **CRAN says**: "Found N unmarked UTF-8 strings"
- **Detection**: Cannot fully detect without R. The encoding marking is internal to the serialized R object. Heuristic: if data files exist and DESCRIPTION has no `Encoding: UTF-8`, flag as a potential issue.
- **Fix**: In R, use `Encoding(x) <- "UTF-8"` for character vectors before saving. Use `tools:::.check_package_datasets()` to find problematic data.
- **Files**: `data/*.rda`, `data/*.RData`

### ENC-07: Non-ASCII in NAMESPACE File

- **Severity**: REJECTION
- **Rule**: The NAMESPACE file must contain only ASCII characters. Non-ASCII can appear if function names contain non-ASCII characters, or if the file was edited with an editor that inserted smart quotes or em-dashes.
- **CRAN says**: "Portable packages must use only ASCII characters in their R code and NAMESPACE directives."
- **Detection**: Read NAMESPACE file as bytes. Check if any byte > 0x7F exists.
- **Fix**: Replace non-ASCII characters with ASCII equivalents. Regenerate NAMESPACE with roxygen2 if applicable.
- **Files**: `NAMESPACE`

### ENC-08: Non-ASCII in Rd Files Without Encoding Declaration

- **Severity**: WARNING
- **Rule**: Rd files that contain non-ASCII characters must have their encoding declared. If DESCRIPTION has `Encoding: UTF-8`, that serves as the default for all Rd files. Otherwise, individual Rd files need `\encoding{UTF-8}`. Without proper encoding, the PDF manual build fails.
- **CRAN says**: "checking PDF version of manual ... WARNING" (LaTeX cannot handle undeclared non-ASCII characters)
- **Detection**: Check if DESCRIPTION has `Encoding:` field. For each `man/*.Rd` file with non-ASCII bytes, check that either DESCRIPTION has an Encoding field or the Rd file has an `\encoding{}` directive.
- **Fix**: Add `Encoding: UTF-8` to DESCRIPTION (preferred, covers all Rd files). Or add `\encoding{UTF-8}` to individual Rd files. If using roxygen2, add `@encoding UTF-8` tag.
- **Files**: `man/*.Rd`, `DESCRIPTION`

---

## Category: Vignettes

### VIG-01: VignetteBuilder Not Declared in DESCRIPTION

- **Severity**: REJECTION
- **Rule**: If the package has vignette source files in `vignettes/` using a non-Sweave engine (knitr, rmarkdown, quarto), the DESCRIPTION must declare `VignetteBuilder`. For `knitr::rmarkdown` vignettes, both knitr AND rmarkdown must be in `VignetteBuilder` and listed in Suggests (or Imports).
- **CRAN says**: "Package has 'vignettes' subdirectory but apparently no vignettes. Perhaps the 'VignetteBuilder' information is missing from the DESCRIPTION file?"
- **Detection**: Parse DESCRIPTION for `VignetteBuilder` field. Scan `vignettes/*.Rmd` and `vignettes/*.Rnw` for `%\VignetteEngine{...}` declarations. If vignettes use `knitr::rmarkdown`, verify both `knitr` and `rmarkdown` appear in VignetteBuilder and in Suggests/Imports. If vignettes exist but no VignetteBuilder is declared, flag.
- **Fix**: Add `VignetteBuilder: knitr` (or `knitr, rmarkdown`) to DESCRIPTION. Add both packages to Suggests.
- **Files**: `DESCRIPTION`, `vignettes/*.Rmd`, `vignettes/*.Rnw`
- **Since**: Pre-2015 — VignetteBuilder requirement consistently enforced; the specific requirement for both knitr AND rmarkdown in VignetteBuilder became common around 2015-2017

### VIG-02: Missing VignetteEngine/VignetteIndexEntry/VignetteEncoding Metadata

- **Severity**: REJECTION (VignetteEngine), NOTE (placeholder title), NOTE (encoding)
- **Rule**: Every vignette source file must contain three metadata declarations: `%\VignetteIndexEntry{Descriptive Title}` (a real title, NOT the placeholder "Vignette Title"), `%\VignetteEngine{knitr::rmarkdown}` (declares which engine processes the file), and `%\VignetteEncoding{UTF-8}` (must be UTF-8).
- **CRAN says**: "Files named as vignettes but with no recognized vignette engine: (Is a VignetteBuilder field missing?)" / NOTE "Vignette with placeholder title 'Vignette Title'"
- **Detection**: Parse each file in `vignettes/` for the three `%\Vignette*` declarations. Check VignetteIndexEntry is not "Vignette Title" or other obvious placeholder text. Verify VignetteEngine matches an engine declared in DESCRIPTION's VignetteBuilder. Verify VignetteEncoding is UTF-8.
- **Fix**: Add missing metadata declarations to vignette YAML frontmatter. Replace placeholder titles with descriptive ones. The VignetteIndexEntry should match the document's `title:` field.
- **Files**: `vignettes/*.Rmd`, `vignettes/*.Rnw`

### VIG-03: Stale Pre-built Vignettes in inst/doc

- **Severity**: WARNING
- **Rule**: If `inst/doc/` exists and contains compiled vignettes (.html, .pdf), they must match the current source vignettes in `vignettes/`. Stale pre-built vignettes cause R CMD build to silently use old versions instead of rebuilding. The `inst/doc/` directory should generally be in `.gitignore`.
- **CRAN says**: "Files in the 'vignettes' directory but no files in 'inst/doc'" / "Files in 'vignettes' but not in 'inst/doc': [filenames]" / "'inst/doc' files newer than 'vignettes' sources"
- **Detection**: If `inst/doc/` exists, check that for every `.Rmd`/`.Rnw` in `vignettes/`, a corresponding `.html`/`.pdf` exists in `inst/doc/`. Compare modification timestamps: if source is newer than compiled output, flag as stale. If `inst/doc/` has files with NO corresponding source in `vignettes/`, flag as orphaned. Flag any `inst/doc/` that is NOT in `.gitignore`.
- **Fix**: Delete `inst/doc/` and rebuild with `R CMD build`. Add `inst/doc` to `.gitignore`. Use `devtools::build()` which handles this correctly.
- **Files**: `inst/doc/`, `vignettes/`, `.gitignore`

### VIG-04: Vignette Build Dependencies Not Declared

- **Severity**: REJECTION
- **Rule**: Every package loaded or used in vignette code (`library()`, `require()`, `pkg::func()`) must be listed in DESCRIPTION's Imports or Suggests. Packages only used in vignettes should be in Suggests. Additionally, `%\VignetteDepends{pkg1, pkg2}` can declare strong vignette-only dependencies.
- **CRAN says**: "Package suggested but not available: 'pkgname'" / vignette build fails with "there is no package called 'pkgname'"
- **Detection**: Extract all `library(pkg)`, `require(pkg)`, and `pkg::func()` calls from vignette R code chunks. Cross-reference against DESCRIPTION Imports and Suggests fields. Flag any package used in vignettes but not declared in DESCRIPTION.
- **Fix**: Add missing packages to Suggests. Use `%\VignetteDepends{pkg}` in vignette YAML for packages needed unconditionally during vignette build. For packages that may not be available, add `eval = requireNamespace("pkg", quietly = TRUE)` to chunk options.
- **Files**: `vignettes/*.Rmd`, `DESCRIPTION`

### VIG-05: HTML Vignette Size — html_document vs html_vignette

- **Severity**: NOTE
- **Rule**: HTML vignettes using `output: html_document` embed a large Bootstrap/jQuery payload (~600KB) vs `html_vignette` (~10KB). Combined with base64-encoded plots, this can push documentation size past the 5MB limit or inflate the tarball beyond 10MB.
- **CRAN says**: NOTE about "installed size is X" or doc directory being too large.
- **Detection**: Check `vignettes/*.Rmd` for `output: html_document` (vs lighter `html_vignette`). If `inst/doc/*.html` exists, check file sizes (flag if any single HTML > 1MB). Check for `self_contained: true` (default for html_document) which embeds all images as base64.
- **Fix**: Use `rmarkdown::html_vignette` instead of `html_document`. Set lower DPI: `knitr::opts_chunk$set(dpi = 72)`. Compress PNG images. Set reasonable figure dimensions.
- **Files**: `vignettes/*.Rmd`, `inst/doc/*.html`

### VIG-06: Vignette Data Files in Wrong Location

- **Severity**: WARNING
- **Rule**: Data files used by vignettes must be accessible during both `R CMD build` (which builds from `vignettes/`) and `R CMD check` (which rebuilds from `inst/doc/`). If data files are in `vignettes/` but not copied to `inst/doc/`, R CMD check will error when trying to rebuild.
- **CRAN says**: Vignette rebuild fails with file-not-found errors during R CMD check.
- **Detection**: Scan vignette R code chunks for file-reading calls (`read.csv()`, `readRDS()`, `read.table()`, `readLines()`, etc.) with relative paths. Verify these files are either in `inst/` (accessible via `system.file()`), generated by vignette code, or listed in `vignettes/.install_extras`.
- **Fix**: Move data files to `inst/extdata/` and reference via `system.file("extdata", "file.csv", package = "pkgname")`. Or add a `.install_extras` file in `vignettes/` listing the data files. Or generate data programmatically within the vignette.
- **Files**: `vignettes/`, `inst/extdata/`, `vignettes/.install_extras`

### VIG-07: Vignette CPU Time Exceeds CRAN Threshold

- **Severity**: NOTE
- **Rule**: Vignette rebuilding must not have CPU time significantly exceeding elapsed time (ratio > 2.5x suggests parallel processing). Dependencies like data.table or RcppParallel may spawn threads during vignette execution.
- **CRAN says**: "Re-building vignettes had CPU time 4.1 times elapsed time"
- **Detection**: Scan vignette R chunks for parallel processing calls: `parallel::`, `mclapply`, `future::plan`, `foreach`, `data.table::setDTthreads`. Check for multi-threaded dependencies in Imports (data.table, RcppParallel, furrr). Verify thread-limiting code exists.
- **Fix**: Add thread-limiting setup chunk: `data.table::setDTthreads(2)`, `Sys.setenv(OMP_NUM_THREADS = 2, MC_CORES = 2)`. Use `\donttest{}` for computationally intensive sections. Pre-compute expensive vignettes using `.Rmd.orig` workflow.
- **Files**: `vignettes/*.Rmd`, `DESCRIPTION`

### VIG-08: Custom Vignette Engine Bootstrap Failure

- **Severity**: NOTE
- **Rule**: Packages that define their own vignette engine (e.g., quarto, R.rsp, bookdown) face a chicken-and-egg problem: R CMD check queries `tools:::vignetteEngine()` which only finds engines from installed packages. If the package itself provides the engine, it may not be installed yet during check.
- **CRAN says**: "Package has 'vignettes' subdirectory but apparently no vignettes. Perhaps the 'VignetteBuilder' information is missing from the DESCRIPTION file?"
- **Detection**: Check if DESCRIPTION's `VignetteBuilder` lists the package itself (self-referencing engine). Check if `VignetteBuilder` lists a package that is not widely installed on CRAN check farms. Flag as informational warning for manual review.
- **Fix**: For self-referencing engines, ensure the package's `.onLoad()` properly registers the engine. Pre-build vignettes so the check step doesn't need the engine. Use `R.rsp::asis` for truly static vignettes. Test on multiple platforms (Linux Debian specifically) before submitting.
- **Files**: `DESCRIPTION`, `R/zzz.R`

---

## Category: NAMESPACE

### NS-01: Import Conflicts / Namespace Collisions

- **Severity**: WARNING
- **Rule**: When two imported packages export the same function name and both are imported via `import()` or `importFrom()`, R generates "Replacing previous import" warnings during namespace loading. This blocks CRAN submission.
- **CRAN says**: "Replacing previous import 'shinydashboard::taskItem' by 'shinydashboardPlus::taskItem'"
- **Detection**: Parse NAMESPACE for all `import()` and `importFrom()` directives. When two `importFrom()` directives import the same function name from different packages, flag it. When `import()` is used for multiple packages, flag as high-risk for collisions.
- **Fix**: Use `importFrom()` selectively. When conflict is unavoidable, use `import(pkg, except=c("conflicting_fun"))` (R >= 3.6.0) or only `importFrom()` the specific functions needed from each package.
- **Files**: `NAMESPACE`

### NS-02: Prefer importFrom over import

- **Severity**: NOTE
- **Rule**: Using `import(entire_package)` in NAMESPACE instead of selective `importFrom(pkg, fun1, fun2)` is discouraged by CRAN guidelines and Bioconductor policy. Human reviewers may request changes, especially for new packages.
- **CRAN says**: "Using importFrom selectively rather than import is good practice and recommended notably when importing from packages with more than a dozen exports." (Writing R Extensions)
- **Detection**: Parse NAMESPACE for `import()` directives (as opposed to `importFrom()`). Flag any `import(pkg)` usage. Particularly flag when multiple `import()` directives exist.
- **Fix**: Replace `import(pkg)` with specific `importFrom(pkg, fun1, fun2, ...)` for each function actually used. If using roxygen2, replace `@import pkg` with `@importFrom pkg fun1 fun2`.
- **Files**: `NAMESPACE`

### NS-03: S3 Method Exported but Not Registered via S3method()

- **Severity**: NOTE
- **Rule**: Functions that look like S3 methods (e.g., `print.myclass`, `summary.myclass`) that are `export()`-ed but not registered via `S3method()` trigger a NOTE that human reviewers consistently reject.
- **CRAN says**: "Found the following apparent S3 methods exported but not registered: [function names]. See section 'Registering S3 methods' in the 'Writing R Extensions' manual."
- **Detection**: Parse NAMESPACE for `export()` directives where the function name matches `generic.class` pattern (where generic is a known S3 generic like print, summary, format, plot, `[`, `[[`, `$`, as.data.frame, etc.) and is not also registered via `S3method()`.
- **Fix**: For roxygen2 users, use `@export` on S3 methods (roxygen2 >= 7.0 automatically generates `S3method()`). For manual NAMESPACE: replace `export(print.myclass)` with `S3method(print, myclass)`.
- **Files**: `NAMESPACE`

### NS-04: Broad exportPattern

- **Severity**: NOTE
- **Rule**: Using `exportPattern("^[[:alpha:]]")` or similar broad patterns exports all functions starting with a letter, including internal helpers. CRAN human reviewers flag this, especially for new packages.
- **CRAN says**: "Exporting all functions with exportPattern('^[[:alpha:]]+') is strongly discouraged and almost always not allowed." (Bioconductor, mirrored by CRAN)
- **Detection**: Parse NAMESPACE for `exportPattern()` directives. Flag any pattern that is broadly permissive (matches most function names), including `exportPattern(".")`, `exportPattern("^[[:alpha:]]")`, `exportPattern("^[^\\.]")`.
- **Fix**: Replace `exportPattern()` with explicit `export()` directives for each public function. If using roxygen2, tag each public function with `@export` and ensure internal helpers lack this tag.
- **Files**: `NAMESPACE`

### NS-05: Depends vs Imports Misuse

- **Severity**: NOTE
- **Rule**: Packages listed in `Depends:` are loaded onto the user's search path. CRAN prefers packages in `Imports:` unless they genuinely need to be on the search path (e.g., for user-facing data or extending another package's classes).
- **CRAN says**: "The 'Depends' field should nowadays be used rarely, only for packages which are intended to be put on the search path to make their facilities available to the end user (and not to the package itself)." (Writing R Extensions)
- **Detection**: Parse DESCRIPTION for `Depends:` field. Flag any package listed in `Depends` that is not `R` itself (version constraint) or `methods` (needed for S4). Cross-reference with NAMESPACE to check if the Depends package is also imported.
- **Fix**: Move packages from `Depends:` to `Imports:` in DESCRIPTION. Add corresponding `importFrom()` directives in NAMESPACE (or `@importFrom` in roxygen2).
- **Files**: `DESCRIPTION`, `NAMESPACE`

### NS-06: No Visible Binding / Missing importFrom

- **Severity**: NOTE
- **Rule**: When R code uses functions from other packages without proper `importFrom()` or `::` qualification, R CMD check generates "no visible global function definition" or "no visible binding for global variable" NOTEs. Human reviewers consistently reject packages with these, especially new submissions.
- **CRAN says**: "no visible global function definition for 'foo'"
- **Detection**: Requires R-level analysis. Partial detection: check that packages in DESCRIPTION `Imports:` have corresponding `importFrom()` or `import()` in NAMESPACE (if not, they may rely on `::` syntax, which is valid but worth verifying).
- **Fix**: For each function from another package, either use `pkg::fun()` syntax in code, or add `importFrom(pkg, fun)` to NAMESPACE / `@importFrom pkg fun` in roxygen2. For non-standard evaluation variables (e.g., dplyr column names), use `.data$col` or `utils::globalVariables()`.
- **Files**: `NAMESPACE`, `R/*.R`
- **Since**: R 3.3.0 (2016) — code usage checking with codetools now runs with only base package attached; functions from non-base default packages (stats, utils, graphics) must be explicitly imported

### NS-07: Re-Export Documentation Requirements

- **Severity**: NOTE
- **Rule**: When re-exporting functions from other packages (e.g., the pipe `%>%` from magrittr), the re-exported function must have its own documentation page with `@return` tag. Missing documentation for re-exports triggers DOC-01 violations.
- **CRAN says**: "Please add \\value to .Rd files regarding exported methods."
- **Detection**: Parse NAMESPACE for patterns where a function is both `importFrom()`-ed and `export()`-ed (suggesting re-export). Check that corresponding .Rd documentation exists.
- **Fix**: Use roxygen2's `@importFrom pkg fun` + `@export` pattern, which generates proper re-export documentation. Or create a `R/reexports.R` file with roxygen2 blocks for re-exported objects.
- **Files**: `NAMESPACE`, `man/*.Rd`

### NS-08: No library()/require() in Package Code

- **Severity**: NOTE → REJECTION
- **Rule**: Package code in `R/*.R` must not use `library()` or `require()` to load other packages. These modify the search path and create fragile implicit dependencies. Instead, use namespace imports (`importFrom()` in NAMESPACE) or the `pkg::func()` calling convention.
- **CRAN says**: R CMD check NOTE: "library() or require() call not declared from: 'pkgname'" / "library() or require() calls in package code" / "'library' or 'require' calls in package code: [...] Please use :: or requireNamespace() instead." (`tools:::.check_packages_used(dir=)` output, Kurt Hornik, https://stat.ethz.ch/pipermail/r-devel/2026-June/084612.html)
- **Detection**: Grep `R/*.R` files for `library(` and `require(` calls that are not inside `if (interactive())` blocks or conditional checks. Distinguish from `requireNamespace()` which is correct. Scan *top-level* (non-assignment) calls in R/*.R, e.g. `library()`, `require()`, `install.packages()`, `options()`, or `lapply(pkgs, library, ...)`. R CMD check analyses the installed namespace, so these run at install time and evade its checks (Kurt Hornik, r-devel 2026-06). Hornik is working on source-level detection.
- **Fix**: Replace `library(pkg)` with proper NAMESPACE imports: add `importFrom(pkg, func)` to NAMESPACE (or `@importFrom pkg func` in roxygen2). Or use `pkg::func()` syntax. Use `requireNamespace("pkg", quietly = TRUE)` for conditional availability checks.
- **Files**: `R/*.R`, `NAMESPACE`
- **Since**: R 3.2.0 (2015) — R CMD check began noting `library()`/`require()` in package code; combined with R 3.3.0 (2016) codetools enforcement of explicit imports

### NS-09: No ::: Calls to the Package's Own Namespace

- **Severity**: NOTE (treated as blocking for new submissions)
- **Rule**: Package code should not use `pkg:::fn` to call its own internal objects. (CODE-12 covers `:::` into base and recommended packages.)
- **CRAN says**: "Check: dependencies in R code, Result: NOTE / There are ::: calls to the package's namespace in its code. A package almost never needs to use ::: for its own objects:" (saferDev pretest, May 2026, https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012388.html)
- **Detection**: Read Package from DESCRIPTION. Grep R/*.R for `<Package>:::`.
- **Fix**: Call internal functions directly by name. Within-package code sees all namespace objects.
- **Files**: `R/*.R`
- **Since**: Long-standing R CMD check NOTE; observed blocking saferDev 1.0.0 (May 2026)

---

## Category: Data

### DATA-01: Undocumented Datasets

- **Severity**: REJECTION
- **Rule**: Every dataset in `data/` must have a documentation entry. R CMD check requires all user-level objects to be documented.
- **CRAN says**: "Undocumented data sets: [dataset names]. All user-level objects in a package should have documentation entries."
- **Detection**: For each `.rda` or `.RData` file in `data/`, check that a corresponding `\alias{}` exists in `man/*.Rd` (with `\docType{data}`) or that the dataset name appears in an `@name` or `@rdname` roxygen block in `R/*.R`.
- **Fix**: Create roxygen2 documentation for each dataset, typically in `R/data.R`:
  ```r
  #' Dataset Title
  #'
  #' Description of the dataset.
  #'
  #' @format A data frame with N rows and M variables:
  #' \describe{
  #'   \item{col1}{Description}
  #' }
  #' @source \url{https://example.com}
  "dataset_name"
  ```
- **Files**: `data/*.rda`, `data/*.RData`, `man/*.Rd`, `R/*.R`

### DATA-02: LazyData Without data/ Directory

- **Severity**: NOTE
- **Rule**: Setting `LazyData: true` in DESCRIPTION when no `data/` directory exists triggers a NOTE. This commonly happens from scaffolding tools like `usethis::create_package()`.
- **CRAN says**: "checking LazyData ... NOTE 'LazyData' is specified without a 'data' directory"
- **Detection**: Parse DESCRIPTION for `LazyData: true` (or `yes`). Check if `data/` directory exists.
- **Fix**: Remove `LazyData: true` from DESCRIPTION if no `data/` directory exists.
- **Files**: `DESCRIPTION`
- **Since**: R 4.1.0 (2021) — LazyData sanity checks introduced; R CMD build began removing unnecessary LazyData fields

### DATA-03: Missing LazyData When data/ Has .rda Files

- **Severity**: NOTE
- **Rule**: When shipping `.rda` or `.RData` files in `data/`, best practice strongly recommends `LazyData: true` so users can access datasets without calling `data()`. Without it, users must call `data("dataset")` explicitly.
- **CRAN says**: Best practice per R-pkgs.org: "If you're shipping .rda files below data/, include LazyData: true in DESCRIPTION."
- **Detection**: Check if `data/` directory contains `.rda` or `.RData` files but `LazyData` is missing or set to `false`/`no` in DESCRIPTION.
- **Fix**: Add `LazyData: true` to DESCRIPTION. For very large datasets, create a `data/datalist` file instead.
- **Files**: `DESCRIPTION`, `data/`

### DATA-04: Suboptimal Data Compression

- **Severity**: WARNING
- **Rule**: Data files should use optimal compression. R CMD check warns when significantly better compression is available. When `LazyData: true` is set and data exceeds 1MB, the `LazyDataCompression` field should be set.
- **CRAN says**: "checking data for ASCII and uncompressed saves ... WARNING. Note: significantly better compression could be obtained by using R CMD build --resave-data"
- **Detection**: Check if `LazyData: true` is set, total data directory size exceeds 1MB, and `LazyDataCompression` field is missing from DESCRIPTION. Flag individual `.rda` files > 100KB as candidates for better compression.
- **Fix**: Run `tools::resaveRdaFiles("data/", compress = "auto")` or set `LazyDataCompression: xz` in DESCRIPTION. Alternatively, use `R CMD build --resave-data`.
- **Files**: `DESCRIPTION`, `data/*.rda`

### DATA-05: Data Size Exceeds 5MB Limit

- **Severity**: REJECTION
- **Rule**: CRAN policy states "neither data nor documentation should exceed 5MB" and "packages should be of the minimum necessary size." R-pkgs.org recommends data under 1MB.
- **CRAN says**: "Data exceeded 5MB limit." / "Packages should be of the minimum necessary size."
- **Detection**: Sum all file sizes in `data/` directory. Error if total exceeds 5MB (hard limit). Warn if total exceeds 1MB (soft recommendation).
- **Fix**: Use better compression (`tools::resaveRdaFiles()`), reduce dataset size, create a separate data-only package, move data to `inst/extdata/` with download functions, or host large data externally with accessor functions.
- **Files**: `data/`

### DATA-06: Non-ASCII Characters in Data Without Proper Encoding

- **Severity**: NOTE
- **Rule**: Data containing non-ASCII character strings triggers an informational NOTE. While not blocking, it draws manual review attention.
- **CRAN says**: "checking data for non-ASCII characters ... NOTE. Note: found N marked UTF-8 strings"
- **Detection**: Requires R to inspect `.rda` binary contents. Without R, can only verify that DESCRIPTION includes `Encoding: UTF-8`.
- **Fix**: Ensure character strings in data are properly marked as UTF-8 using `Encoding()`. Add `Encoding: UTF-8` to DESCRIPTION.
- **Files**: `DESCRIPTION`, `data/*.rda`

### DATA-07: Serialization Version Incompatibility

- **Severity**: WARNING
- **Rule**: Data saved with R >= 4.0 defaults to serialization version 3 (`RDA3`/`RDX3` format), which cannot be read by R < 3.5.0. This causes an automatic dependency bump.
- **CRAN says**: "NB: this package now depends on R (>= 3.5.0). WARNING: Added dependency on R >= 3.5.0 because serialized objects in serialize/load version 3 cannot be read in older versions of R."
- **Detection**: Read first bytes of `.rda` files to detect `RDA3`/`RDX3` magic bytes. If found and DESCRIPTION does not declare `Depends: R (>= 3.5.0)` or higher, flag it.
- **Fix**: Re-save data with `version = 2`: `save(data, file = "data/mydata.rda", version = 2)`, or add `Depends: R (>= 3.5.0)` to DESCRIPTION.
- **Files**: `DESCRIPTION`, `data/*.rda`
- **Since**: R 3.5.0 (2018) — serialization format v3 introduced; R 3.6.0 (2019) made format v3 the default, causing silent dependency bumps for packages rebuilt with R >= 3.6

### DATA-08: Internal sysdata.rda Size

- **Severity**: NOTE
- **Rule**: `R/sysdata.rda` holds internal (non-exported) data. It is always lazy-loaded regardless of the `LazyData` setting. Large internal data contributes to overall package size.
- **CRAN says**: Flagged under general package size checks. Internal data does not need documentation.
- **Detection**: Check for `R/sysdata.rda` existence and verify its size. Flag if > 1MB.
- **Fix**: Keep `R/sysdata.rda` small. For large internal data, consider lazy-loading from `inst/` or external sources. Do NOT document sysdata.rda objects.
- **Files**: `R/sysdata.rda`

### DATA-09: Invalid Data File Formats in data/

- **Severity**: WARNING
- **Rule**: The `data/` directory may only contain specific file types. R CMD check validates the contents.
- **CRAN says**: "checking contents of 'data' directory" — flags invalid file types.
- **Detection**: List files in `data/`. Allowed extensions: `.rda`, `.RData`, `.R`, `.r`, `.tab`, `.txt`, `.csv` (optionally compressed with `.gz`, `.bz2`, `.xz`). `.rds` files are NOT allowed in `data/` — they must go in `inst/extdata/`.
- **Fix**: Convert data to `.rda` format using `usethis::use_data()`. Move non-standard files (including `.rds`) to `inst/extdata/`.
- **Files**: `data/`

---

## Category: System Requirements

### SYS-01: Undeclared System Library in Compiled Code

- **Severity**: WARNING
- **Rule**: Packages that link against system libraries (libcurl, libxml2, OpenSSL, zlib, etc.) via compiled code in `src/` must declare those libraries in the `SystemRequirements` field. Without the declaration, the package fails to install on CRAN check machines when the configure script or linker cannot find the library.
- **CRAN says**: "configuration failed because libxml-2.0 was not found" / "cannot find -lcurl" (installation failure is the rejection mechanism)
- **Detection**: Scan `src/*.c`, `src/*.cpp`, `src/*.h` for `#include` of known system library headers (e.g., `<curl/curl.h>`, `<zlib.h>`, `<png.h>`). Also parse `src/Makevars` for `-l<library>` flags in `PKG_LIBS`. Cross-reference against `SystemRequirements` field in DESCRIPTION.
- **Fix**: Add the library name to SystemRequirements with platform install hints: `SystemRequirements: libcurl: libcurl-devel (rpm) or libcurl4-openssl-dev (deb)`
- **Files**: `DESCRIPTION`, `src/*.c`, `src/*.cpp`, `src/*.h`, `src/Makevars`

### SYS-02: Undeclared External Program or Interpreter

- **Severity**: WARNING
- **Rule**: Packages that invoke external programs via `system()`, `system2()`, or `processx::run()` — or depend on interpreters like Python, Java, or pandoc — must declare them in `SystemRequirements`. Writing R Extensions explicitly lists Perl, Python, Tcl, BUGS, JavaScript, Matlab, PHP, and shell scripts as needing declaration.
- **CRAN says**: "If your package requires one of these interpreters or an extension then this should be declared in the SystemRequirements field."
- **Detection**: Grep R source files for `system()`, `system2()`, `processx::run()` calls that invoke known external programs. Check for `reticulate::` usage (Python), `rJava::` or `.jcall()` (Java), `rmarkdown::render()` (pandoc). Cross-reference against SystemRequirements.
- **Fix**: Add the program to SystemRequirements with version if applicable: `SystemRequirements: Python (>= 3.6), pandoc (>= 2.0)`
- **Files**: `DESCRIPTION`, `R/*.R`

### SYS-03: C++20 Default Standard Transition

- **Severity**: NOTE
- **Rule**: R 4.6.0 makes C++20 the default C++ standard where available. Packages that explicitly set `CXX_STD = CXX17` in Makevars should verify compatibility with C++20 compilation. Packages still specifying `CXX_STD = CXX11` or `CXX_STD = CXX14` are covered by COMP-06 (defunct in R 4.6.0). Packages needing exactly C++17 should keep the explicit declaration; packages compatible with C++20 can remove `CXX_STD` entirely.
- **CRAN says**: R 4.6.0 NEWS: "The default C++ standard has been changed to C++20 where available (which it is on all known platforms from 2021 on): if not C++17 is used if available otherwise C++ is not supported (as before). (GCC 16 has also switched to C++20 as its default.) Packages can request C++17 if essential."
- **Detection**: Check if package has `src/` with C++ files. Check if `CXX_STD` is set in Makevars. If `CXX_STD = CXX17` is explicitly set, flag as informational for C++20 compatibility review. GCC 16.2 and clang 23 (also C++20-default toolchains) are now on the CRAN r-devel Linux flavors.
- **Fix**: For new packages: remove CXX_STD entirely (C++20 default is backward-compatible for most code). For packages needing exactly C++17: keep `CXX_STD = CXX17`. For packages needing C++20 features: set `CXX_STD = CXX20`.
- **Files**: `src/Makevars`, `src/Makevars.win`
- **Since**: R 4.6.0 (2026-04-24)

### SYS-04: Configure Script Missing for System Libraries

- **Severity**: WARNING
- **Rule**: Packages that use system libraries (detected via SYS-01) should include a `configure` script that checks for required tools and provides informative error messages. The configure script must never attempt to install dependencies itself. The CRAN Repository Policy requires packages to check for the presence of required tools; for Rust packages specifically, "configure/configure.win script should check for the presence of commands cargo and rustc."
- **CRAN says**: "The package should not attempt to install these for itself." / Configure scripts must "check for the presence of commands."
- **Detection**: Check if `src/` exists with compiled code using system libraries (from SYS-01) but no `configure` script. If `configure` exists, grep for auto-install anti-patterns (`apt-get install`, `pip install`, `npm install` being executed rather than suggested in error messages).
- **Fix**: Add a configure script that checks for required tools/libraries and provides informative error messages. Never attempt to install tools automatically. Use `pkg-config` or `AC_CHECK_LIB` for detection.
- **Files**: `configure`, `configure.ac`, `src/Makevars`

### SYS-05: Java .class/.jar Files Require Source

- **Severity**: REJECTION
- **Rule**: Packages containing `.class` or `.jar` files must include Java source code in a top-level `java/` directory, or that directory must explain how the sources can be obtained. This is a FOSS license compliance requirement.
- **CRAN says**: "For Java .class and .jar files, the sources should be in a top-level java directory in the source package (or that directory should explain how they can be obtained)." / Real rejection (CirceR, April 2024): "Package has FOSS license, installs .class/.jar but has no 'java' directory."
- **Detection**: Search for `.class` and `.jar` files anywhere in the package (especially `inst/java/`, `java/`, `inst/`). If found, check for a `java/` top-level directory. Also verify SystemRequirements mentions Java/JDK.
- **Fix**: Create a `java/` directory containing Java source files, or include a README in `java/` explaining how to obtain the sources. Declare `SystemRequirements: Java (>= 8)` (or appropriate version).
- **Files**: `DESCRIPTION`, `java/`, `inst/java/`, any `.jar`/`.class` files

### SYS-06: Contradictory C++ Standard Between SystemRequirements and Makevars

- **Severity**: WARNING
- **Rule**: The C++ standard specified in `SystemRequirements` (e.g., "C++17") must be consistent with the `CXX_STD` setting in `src/Makevars*`. R CMD check validates this since R 4.5.3 (2026-03-11) and issues a warning for contradictory specifications.
- **CRAN says**: "C++ standard specifications (CXX_STD = in 'src/Makevars*' and in the SystemRequirements field of the 'DESCRIPTION' file) are now checked more thoroughly. Invalid values are still ignored but now give a warning, as do contradictory specifications."
- **Detection**: Parse SystemRequirements for C++ standard mentions (e.g., "C++17", "C++20", "C++11"). Parse `src/Makevars*` for `CXX_STD` setting. Flag if they contradict (e.g., SystemRequirements says C++17 but Makevars says CXX20). Also flag deprecated `SystemRequirements: C++11`.
- **Fix**: Ensure SystemRequirements and Makevars CXX_STD agree. Best practice: specify only in Makevars (`CXX_STD`), not in SystemRequirements, unless human-readable documentation is desired.
- **Files**: `DESCRIPTION`, `src/Makevars`, `src/Makevars.win`
- **Since**: R 4.5.3 (2026-03-11) — the quoted text is from the R 4.5.3 NEWS

### SYS-07: USE_C17 Opt-Out for C23 Keyword Conflicts

- **Severity**: NOTE
- **Rule**: Packages with C23 keyword conflicts (`bool`, `true`, `false`, `nullptr` used as variable/parameter names) can temporarily opt out of C23 compilation by adding `USE_C17` to SystemRequirements. This is a temporary escape hatch; the proper fix is to rename conflicting identifiers.
- **CRAN says**: "Packages can opt out via `SystemRequirements: USE_C17` or `R CMD INSTALL --use-C17`."
- **Detection**: Cross-reference with COMP-01 (C23 keyword conflicts). If COMP-01 detects conflicts AND `SystemRequirements: USE_C17` is present, suppress or downgrade the COMP-01 finding. If COMP-01 detects conflicts AND no USE_C17, suggest either fixing the code or adding USE_C17 as a temporary workaround.
- **Fix**: Best: Rename conflicting identifiers to avoid C23 keywords. Temporary: Add `USE_C17` to SystemRequirements in DESCRIPTION. Ensure configure script does not override the C standard selection.
- **Files**: `DESCRIPTION`, `src/*.c`, `src/*.h`

---

## Category: Maintainer Email

### EMAIL-01: Maintainer Email Must Not Be a Mailing List

- **Severity**: REJECTION
- **Rule**: The maintainer (cre) email must belong to a person, not a mailing list, team alias, or group address.
- **CRAN says**: "The package's DESCRIPTION file must show both the name and email address of a single designated maintainer (a person, not a mailing list)."
- **Detection**: Parse the cre person's email from Authors@R. Flag if: the local part contains list keywords (lists, devel, dev-team, team, group, announce, discuss, users); the address starts with info@, admin@, support@, contact@, help@, office@, team@; or the domain is a known mailing list provider (lists.r-forge.r-project.org, lists.sourceforge.net, googlegroups.com, groups.io).
- **Fix**: Use a personal email address for the maintainer (cre) role. Team emails can go in a BugReports or Contact field.
- **Files**: `DESCRIPTION`

### EMAIL-02: Maintainer Must Have Email in Authors@R

- **Severity**: REJECTION
- **Rule**: The person with the cre role in Authors@R must have an email argument. Without it, R cannot derive the Maintainer field.
- **CRAN says**: "The package's DESCRIPTION file must show both the name and email address of a single designated maintainer."
- **Detection**: Parse Authors@R. Find the person() block with "cre" role. Verify it contains an `email =` argument.
- **Fix**: Add email to the cre person: `person("First", "Last", email = "name@domain.com", role = c("aut", "cre"))`.
- **Files**: `DESCRIPTION`

### EMAIL-03: Email Should Not Be from a Disposable Domain

- **Severity**: WARNING
- **Rule**: The maintainer email should not come from a known disposable/temporary email provider. CRAN requires long-term reachability; disposable addresses expire within hours or days.
- **CRAN says**: "Make sure this email address is likely to be around for a while and that it's not heavily filtered."
- **Detection**: Check the email domain against a curated list of known disposable email providers (mailinator.com, guerrillamail.com, tempmail.com, yopmail.com, sharklasers.com, 10minutemail.com, trashmail.com, throwaway.email, etc.).
- **Fix**: Use a permanent personal email address (Gmail, Outlook, ProtonMail, institutional, or custom domain).
- **Files**: `DESCRIPTION`

### EMAIL-04: Email Address Must Not Be a Placeholder

- **Severity**: REJECTION
- **Rule**: The maintainer email must be a real, deliverable address -- not a placeholder or example address from a template.
- **CRAN says**: "a valid (RFC 2822) email address in angle brackets"
- **Detection**: Validate the email address: must have exactly one @, non-empty local part, domain with at least one dot. Flag placeholder domains (example.com, example.org, example.net) and template patterns (your.email@, maintainer@email.com, first.last@example.com, user@domain.com). Flag addresses with spaces or missing components.
- **Fix**: Replace the placeholder with a real, working email address.
- **Files**: `DESCRIPTION`

### EMAIL-05: Institutional Email Longevity Warning

- **Severity**: NOTE
- **Rule**: Institutional email addresses (.edu, .ac.uk, .edu.au, etc.) are valid but higher risk of becoming undeliverable when the maintainer changes institutions. This is the #1 cause of CRAN package archival. Feb-Sep 2026: about 405 packages were archived for undeliverable maintainer email, 278 of them between 2026-04-30 and 2026-05-14. This was the single largest archival reason in that window. The mechanism behind the April/May wave was not announced (UNVERIFIED; it looks like a bulk deliverability sweep). Uwe Ligges also noted that outlook.com frequently blocks CRAN/win-builder mail (2026-08-08).
- **CRAN says**: "Too many people let their maintainer addresses run out of service." (Uwe Ligges, R-package-devel) / "Archived on 2026-05-04 as email to the maintainer is undeliverable." (CRAN `X-CRAN-Comment`)
- **Detection**: Flag emails from university/academic domains: .edu, .ac.uk, .ac.jp, .edu.au, .edu.cn, .uni-*.de, and similar academic TLD patterns.
- **Fix**: Consider using a stable personal email (Gmail, ProtonMail, custom domain) alongside or instead of the institutional address. If using an institutional email, update all CRAN packages promptly when changing institutions.
- **Files**: `DESCRIPTION`

### EMAIL-06: Noreply/Automated Email Addresses Are Not Allowed

- **Severity**: REJECTION
- **Rule**: The maintainer email must be actively monitored and responsive. Noreply, bot, and automated addresses cannot receive CRAN team communications.
- **CRAN says**: "That contact address must be kept up to date, and be usable for information mailed by the CRAN team without any form of filtering, confirmation."
- **Detection**: Flag emails matching noreply patterns: noreply@, no-reply@, donotreply@, do-not-reply@, notifications@github.com, *@users.noreply.github.com, bot@, ci@, automation@.
- **Fix**: Use a personal email address that you actively monitor and can respond to.
- **Files**: `DESCRIPTION`

---

## Category: inst/ Directory

### INST-01: Hidden Files in inst/

- **Severity**: REJECTION
- **Rule**: Hidden files and OS-generated metadata must not be included in `inst/`. R CMD check flags these during "checking for hidden files and directories." Common offenders: `.DS_Store` (macOS Finder), `.gitkeep` (git empty-directory placeholder), `Thumbs.db` (Windows Explorer thumbnails), `desktop.ini` (Windows folder settings), `.Rhistory`, `.RData`.
- **CRAN says**: "Found the following hidden files and directories: inst/.DS_Store, inst/.gitkeep"
- **Detection**: Recursively scan `inst/` for files whose name starts with `.` or matches known OS metadata patterns: `.DS_Store`, `.gitkeep`, `.gitignore`, `Thumbs.db`, `desktop.ini`, `.Rhistory`, `.RData`.
- **Fix**: Delete hidden files from `inst/`. Add patterns to `.Rbuildignore` if they must exist at the project root level. Use `usethis::use_build_ignore()` for systematic exclusion.
- **Files**: `inst/**`

### INST-02: Deprecated CITATION Format (citEntry/personList)

- **Severity**: WARNING
- **Rule**: The `inst/CITATION` file must use modern `bibentry()` instead of the deprecated `citEntry()`. Similarly, `personList()` and `as.personList()` must be replaced with `c()` on person objects. `citHeader()` and `citFooter()` should be replaced with `header` and `footer` arguments to `bibentry()`. Since R 4.x these old-style functions generate NOTEs under `--as-cran` and CRAN reviewers increasingly reject packages using them.
- **CRAN says**: "Package CITATION file contains call(s) to old-style citEntry(). Please use bibentry() instead." / "Package CITATION file contains call(s) to old-style personList() or as.personList(). Please use c() on person objects instead."
- **Detection**: Read `inst/CITATION`. Search for `citEntry(`, `personList(`, `as.personList(`, `citHeader(`, `citFooter(` patterns.
- **Fix**: Replace `citEntry()` with `bibentry()` (use `bibtype` instead of `entry`). Replace `personList()` / `as.personList()` with `c()`. Replace `citHeader("text")` / `citFooter("text")` with `header = "text"` / `footer = "text"` arguments to the first `bibentry()` call.
- **Files**: `inst/CITATION`

### INST-03: inst/doc Conflicts with Vignette Building

- **Severity**: WARNING
- **Rule**: When a package has vignette sources in `vignettes/`, the `inst/doc/` directory should not exist in the source tree. Since R 3.1.0, `R CMD build` populates `inst/doc/` automatically from `vignettes/`. Manually placed files in `inst/doc/` create mismatches between source vignettes and built output. Vignette source files (`.Rmd`, `.Rnw`) must never be placed directly in `inst/doc/`.
- **CRAN says**: "inst/doc directory should not contain pre-built vignettes if vignettes/ directory exists" / "Package has a VignetteBuilder field but no prebuilt vignette index."
- **Detection**: Check if `vignettes/` exists with `.Rmd`/`.Rnw` source files. If `inst/doc/` also exists with `.html`/`.pdf`/`.Rmd`/`.Rnw` files, flag the conflict. Also flag `.Rmd` or `.Rnw` source files directly in `inst/doc/`.
- **Fix**: Delete `inst/doc/` from the source tree (it is regenerated by `R CMD build`). Move any vignette sources to `vignettes/`. Add `inst/doc` to `.gitignore` (but NOT to `.Rbuildignore`).
- **Files**: `inst/doc/`, `vignettes/`

### INST-04: Reserved Subdirectory Names and Embedded Packages in inst/

- **Severity**: REJECTION
- **Rule**: Contents of `inst/` are copied to the package installation root. Subdirectories of `inst/` must not use names reserved by R's package structure: `R`, `data`, `demo`, `exec`, `libs`, `man`, `help`, `html`, `Meta`. These would overwrite or conflict with R's standard directories during installation. Additionally, `inst/` must not contain embedded packages (subdirectories with their own DESCRIPTION file).
- **CRAN says**: "inst/ subdirectories should not interfere with R's standard directories" / "Subdirectory 'inst/tinytest/testpkg' appears to contain a package"
- **Detection**: List immediate subdirectories of `inst/` and flag any matching reserved names (case-sensitive). Recursively scan `inst/` for DESCRIPTION files indicating embedded packages.
- **Fix**: Rename conflicting directories to non-reserved names. For test fixture mock packages, restructure tests to avoid embedding packages inside `inst/`.
- **Files**: `inst/*/`

### INST-05: Missing Copyright Attribution for Bundled Third-Party Code

- **Severity**: WARNING
- **Rule**: Packages that bundle third-party JavaScript, CSS, C/C++ libraries, or other external code in `inst/` must properly attribute the original authors. CRAN Repository Policy requires: "Where code is copied (or derived) from the work of others, care must be taken that any copyright/license statements are preserved and authorship is not misrepresented." Common locations: `inst/htmlwidgets/lib/`, `inst/www/`, `inst/include/`, `inst/js/`, `inst/css/`.
- **CRAN says**: "Where copyrights are held by an entity other than the package authors, this should preferably be indicated via 'cph' roles in the 'Authors@R' field, or using a 'Copyright' field (if necessary referring to an inst/COPYRIGHTS file)."
- **Detection**: Check for common third-party code directories under `inst/` (`htmlwidgets/`, `www/`, `include/`, `js/`, `css/`). If found, check for: (1) `inst/COPYRIGHTS` file, (2) `Copyright` field in DESCRIPTION, (3) `cph` roles in Authors@R beyond the package authors, (4) LICENSE/LICENCE files within the third-party directories.
- **Fix**: Add copyright holders to Authors@R with `cph` role. Create `inst/COPYRIGHTS` file listing all bundled code and their licenses. Add `Copyright` field to DESCRIPTION referencing `inst/COPYRIGHTS`. Include LICENSE files alongside bundled code.
- **Files**: `inst/htmlwidgets/`, `inst/www/`, `inst/include/`, `inst/js/`, `inst/css/`, `DESCRIPTION`, `inst/COPYRIGHTS`

### INST-06: Large Files in inst/extdata

- **Severity**: WARNING
- **Rule**: CRAN imposes a 1MB per-subdirectory soft limit (any subdirectory exceeding 1MB triggers a NOTE in R CMD check "checking installed package size"). The `inst/extdata/` directory is a common location for example data and test fixtures. The overall package tarball should not exceed 5MB without special approval. This rule enhances existing SIZE-01 with per-subdirectory awareness.
- **CRAN says**: "installed size is X.XMb, sub-directories of 1Mb or more: extdata X.XMb"
- **Detection**: Calculate total size of each subdirectory under `inst/`. Flag any subdirectory exceeding 1MB. Flag individual files over 500KB. Identify potentially compressible files (uncompressed CSV, BMP images, uncompressed text).
- **Fix**: Compress data files (use xz or bzip2 for CSV/text). Reduce image resolution. Move large datasets to a separate data package. Use `tools::R_user_dir()` for runtime-downloaded data (R >= 4.0). Consider hosting data externally with download-on-demand.
- **Files**: `inst/extdata/`, `inst/*/`

---

## R-devel Watch List (not yet enforced on CRAN release)

Changes visible in R-devel (future R 4.7.0), CRAN check configuration or R Core discussion as of 2026-10-05. Promote to rules once released or enforced.

- **ENC-01 / DESCRIPTION read as UTF-8**: "read.dcf() and write.dcf() now treat DCF files (such as package 'DESCRIPTION' ...) as UTF-8 ... non-UTF-8 'DESCRIPTION' files (e.g. those declaring 'Encoding: latin1') are no longer re-encoded on reading." `Encoding: latin1` is effectively obsolete; use UTF-8. Revisit ENC-01 when R 4.7.0 is released. (R-devel NEWS, https://cran.r-project.org/doc/manuals/r-devel/NEWS.html)
- **VIG-09 (proposed) / PDF vignettes with missing BibTeX references**: NOTE when re-building Sweave/LaTeX vignettes whose `\cite{}` keys are missing from the `.bib` files; detect by comparing `\cite{key}` keys with `\bibliography{}` files in `vignettes/*.Rnw`. "tools::texi2pdf() now reports BibTeX warnings; in particular, missing references are now noted by R CMD check when re-building PDF vignettes." (R-devel NEWS)
- **Exported functions without usage**: trunk `--as-cran` sets `_R_CHECK_CODOC_FUNCTIONS_MISSING_FROM_USAGES_=NA` (reported as INFO; NOTE when set true); CRAN's `check.Renviron` sets it too. Not in NEWS. (https://svn.r-project.org/R/trunk/src/library/tools/R/check.R)
- **Obsolete `data/datalist`**: "R CMD build now excludes an obsolete 'data/datalist' file when the package uses 'LazyData', and reports when it added one." Relevant to DATA-03. (R-devel NEWS)
- **`.Rbuildignore` applied before copying**: broken symlinks matching an exclude pattern no longer break `R CMD build`. (R-devel NEWS)
- **`structure()` attribute names**: `.Dim`, `.Dimnames`, `.Names`, `.Tsp` and `.Label` are deprecated. (R-devel NEWS)
- **`rbinom()` fix**: reproducing old results needs `RNGversion("4.6")`; may change test snapshots. (R-devel NEWS)
- **Duplicate packages in Imports/Suggests**: Kurt Hornik found 18 CRAN packages and said "I'll take a look ..."; may become a check. (https://stat.ethz.ch/pipermail/r-devel/2026-June/084618.html)
- **CITATION call whitelisting**: after DESC-16, Hornik: "The harder part will be narrowing down the calls allowed in CITATION files" (relates to INST-02). (https://stat.ethz.ch/pipermail/r-devel/2026-April/084480.html)
- **`data/*.R` scripts that load their own namespace**: break vignette-engine detection under R CMD check (Ivan Krylov). (https://stat.ethz.ch/pipermail/r-devel/2026-August/084669.html)
- **Source-level detection of top-level side-effect calls in R/**: Hornik is looking into making `tools:::.check_packages_used()` catch top-level `library()`/`install.packages()` calls (see NS-08, CODE-13). (https://stat.ethz.ch/pipermail/r-devel/2026-June/084612.html)
