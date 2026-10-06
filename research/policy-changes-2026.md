# CRAN Policy Changes and R Release Changes: January - September 2026

Generated: 2026-10-05

## Executive Summary

The CRAN Repository Policy changed in 2026 after almost 18 months with no change. Before that, Rev 6286 (August 2024) was current. Four commits in the period matter for package authors. Two are substantive:

1. **Strong dependencies must be on CRAN or the Bioconductor *software* repository.** This was SVN r6734 (committed 2025-12-15, with a spelling fix in r6738 on 2025-12-19). It first appeared on the CRAN web page about 2026-02-20. Bioconductor annotation and experiment-data packages are now allowed only in `Suggests`/`Enhances`.
2. **New "anti-social behaviour" bullet: "Packages should not contain nor display material which might be considered divisive or give offence, such as political slogans."** This was committed as SVN r6942 on 2026-09-02. It was already on the live page, which was last modified 2026-07-27, even though that page still shows "Version $Revision: 6875 $".

The other two revisions changed nothing for authors: r6846 (2026-04-13) only adjusted texinfo node navigation, and r6875 (2026-05-31) updated a binary-package example from "R 3.1.3 / 3.2.x" to "R 3.5.3 / 3.6.x".

**R 4.6.0** was released on 2026-04-24 and **R 4.6.1** on 2026-06-24. **R 4.5.3** (2026-03-11) also falls in this window. Every R 4.6.0 prediction in `policy-changes-2025-2026.md` shipped, but two shipped in a different form. `VECTOR_PTR` was removed outright instead of being raised to a WARNING. `R_ext/Callbacks.h` was not removed; it was superseded by the new `R_ext/ObjectTable.h`. R 4.6.0 also made changes that its NEWS does not mention. The `--as-cran` source turns on four new checks: an Rcpp "not needed" WARNING, a check of relative-path URLs, a check of Rd bibentries that are cited but not shown, and an explicit 301 status in URL reports. On the infrastructure side:

- The macOS arm64 binaries now target macOS 14 (Sonoma).
- Rtools45 moved to GCC 14.3.
- The Fedora and Debian r-devel flavors now run GCC 16.2 and LLVM/clang 23.1. clang 23's libc++ change on "transitive includes" is producing a new wave of CRAN problem notifications in September 2026.

## Research Question

What changed in CRAN policy, R CMD check and CRAN infrastructure between 2026-01-01 and 2026-09-30? Which R 4.6.0 predictions from the previous research file came true?

## Method / Limitations

- The policy history comes from three sources: the CRAN SVN repository (`R-dev-web/trunk/CRAN/Policy/CRAN_policies.texi`, log read via WebDAV `REPORT` and each revision fetched via `!svn/bc/<rev>`), the eddelbuettel/crp tracker, and the live `policies.html`. The text was compared revision by revision with word diffs.
- The R changes come from the release and devel NEWS pages, plus the R 4.5, R 4.6 and trunk sources of `tools/R/check.R`. I used the sources to find `--as-cran` changes that NEWS does not mention.
- The CRAN-side check configuration comes from `R-dev-web/trunk/CRAN/QA/Kurt/` (incoming/regular check scripts and `check.Renviron`) and `QA/BDR/`.
- **Not covered:** the general web search tool was unavailable during this session, so the R-package-devel and R-devel mailing lists and third-party blogs were **not** surveyed. Anything below that comes from secondary sources is marked UNVERIFIED.

---

## Part 1: CRAN Repository Policy Revisions

### Revision history (SVN `CRAN/Policy/CRAN_policies.texi`)

| SVN rev | Commit date | Author | Log message | Substantive? |
|---|---|---|---|---|
| 6286 | 2024-08-27 | ligges | package names are persistent on CRAN | (baseline in previous report) |
| 6734 | 2025-12-15 | hornik | "Strong dependencies of CRAN packages should now be in CRAN or BioC software." | **Yes** |
| 6738 | 2025-12-19 | hornik | "Spelling." (wraps `Bioconductor` in `@I{}`) | No |
| 6846 | 2026-04-13 | hornik | "Tweaks." (`@node Top` navigation only) | No |
| 6875 | 2026-05-31 | ripley | "update version numbers" | Cosmetic |
| 6942 | 2026-09-02 | ripley | "up" | **Yes** |

The crp tracker recorded the web releases as "new rev6738" on 2026-02-20, "new rev6846" on 2026-04-21 and "new rev6875" on 2026-05-31. It has no entry after that.

- Source: https://svn.r-project.org/R-dev-web/trunk/CRAN/Policy/CRAN_policies.texi (revisions viewable as `https://svn.r-project.org/R-dev-web/!svn/bc/<rev>/trunk/CRAN/Policy/CRAN_policies.texi`)
- Source: https://github.com/eddelbuettel/crp/commits/master

### Finding 1: Strong dependencies must be on CRAN or Bioconductor *software* (r6734)

**Old text (r6286):**
> Packages on which a CRAN package depends should be available from a mainstream repository: if any mentioned in 'Suggests' or 'Enhances' fields are not from such a repository, where to obtain them at a repository should be specified in an 'Additional_repositories' field of the DESCRIPTION file ...

**New text (r6738 onward, verbatim from live page):**
> Packages on which a CRAN package depends should be available from a standard repository. The strong dependencies (i.e., packages listed in the 'Depends', 'Imports' or 'LinkingTo' fields) should be available from CRAN or the Bioconductor software repository. If any mentioned in 'Suggests' or 'Enhances' fields are not from one of these or the Bioconductor annotation and experiment data repositories, where to obtain them at a repository should be specified in an 'Additional_repositories' field of the DESCRIPTION file (as a comma-separated list of repository URLs) or for other means of access, described in the 'Description' field.

**Impact:**
- `Depends`/`Imports`/`LinkingTo` on a Bioconductor *annotation* or *experiment-data* package (for example `org.Hs.eg.db`, `BSgenome.*`, `TxDb.*`, `*Data` experiment packages) now breaks policy. These must move to `Suggests` and be used conditionally.
- Bioconductor annotation/experiment-data packages in `Suggests` do **not** need `Additional_repositories`. Any other non-CRAN, non-BioC-software `Suggests` package still does.
- "Mainstream repository" became "standard repository".

**Dates:** committed 2025-12-15. It was not on the web page on 2026-02-08, when the previous report still saw Rev 6286, and it was on the page by 2026-02-20 (crp tracker).

- Source: https://cran.r-project.org/web/packages/policies.html
- Source: SVN diff r6286 to r6734, https://svn.r-project.org/R-dev-web/!svn/bc/6734/trunk/CRAN/Policy/CRAN_policies.texi

### Finding 2: New prohibition on divisive or offensive material (r6942)

**New bullet under "malicious or anti-social" examples (verbatim):**
> Packages should not contain nor display material which might be considered divisive or give offence, such as political slogans.

It sits between "Packages should not send information about the R session..." and "Packages must not disable the stack-checking mechanism...".

**Dates and revision label:**
- The live `policies.html` has `Last-Modified: Mon, 27 Jul 2026 11:32:18 GMT`. It contains this sentence but still displays "Version $Revision: 6875 $".
- The SVN commit that adds the sentence to the texi source is r6942 (2026-09-02).
- The most likely explanation is that the page was built from an uncommitted working copy; Ripley's r6277 log message ("updates, some released but not yet committed") shows this has happened before. The live page is therefore **ahead of** its displayed revision number.
- The crp tracker (latest: rev6875, 2026-05-31) does not have this sentence.

**Impact:**
- Startup messages (`.onAttach`/`packageStartupMessage`), README/DESCRIPTION text, data, examples or vignettes that carry political slogans can now be rejected under explicit policy text.
- Detection is necessarily manual. The policy gives no definition beyond "divisive or give offence".

- Source: https://cran.r-project.org/web/packages/policies.html (fetched 2026-10-05)
- Source: https://svn.r-project.org/R-dev-web/!svn/bc/6942/trunk/CRAN/Policy/CRAN_policies.texi

### Finding 3: Cosmetic revisions (r6738, r6846, r6875)

- **r6738:** Rd/texi markup (`@I{Bioconductor}`).
- **r6846:** node navigation only. The crp HTML diff also shows the bullet rendering switching between "- " and plain bullets; this is a texi2any rendering artifact with no textual change.
- **r6875:** the binary-packages example "(e.g. R 3.1.3 when R 3.2.x is current)" became "(e.g. R 3.5.3 when R 3.6.x is current)". This is not a policy change.

- Source: crp diffs https://github.com/eddelbuettel/crp/commit/68ce2c0 and https://github.com/eddelbuettel/crp/commit/e4f4cd1

### Finding 4: Companion policy documents

- `submission_checklist.texi`: last changed r6516 (2025-03-05). **No change in 2026.**
- `using_rust.texi`: last changed r6281 (2024-08-21). **No change in 2026.**
- `external_libs.texi` ("Using external libraries in CRAN packages"):
  - r6797 (2026-02-20): the macOS arm64 library location changed from `https://mac.r-project.org/bin/darwin20/arm64/` to `https://mac.r-project.org/bin/darwin23/arm64/`, matching the new macOS 14 target (see Finding 15).
  - r6850 (2026-04-21): "remove reference to TK". The "For further advice, consult Tomas Kalibera" line for Windows/MXE was commented out.

- Source: https://svn.r-project.org/R-dev-web/trunk/CRAN/Policy/ (PROPFIND listing with per-file revisions)
- Source: https://cran.r-project.org/web/packages/external_libs.html

---

## Part 2: R 4.6.0 Prediction Scorecard

R 4.6.0 was released 2026-04-24 and R 4.6.1 on 2026-06-24 (tarball timestamps).
- Source: https://cran.r-project.org/src/base/R-4/
- Source: https://cran.r-project.org/doc/manuals/r-release/NEWS.html

| # | Prediction in `policy-changes-2025-2026.md` | Outcome | Evidence (R 4.6.0 NEWS, verbatim) |
|---|---|---|---|
| P1 | C++11/C++14 specs "becoming defunct"; `CXX11`/`CXX14` config variables reported as defunct (Finding 10) | **Shipped (stronger)** | "Support for these standards has been removed: the default C++ standard will be used. R CMD config variables CXX11, CXX14 and their associated CXXxxFLAGS, CXXxxPICFLAGS CXXxxSTD, SHLIBCXXxxLD and SHLIBCXXxxLDFLAGS variables are no longer supported and reported as 'defunct'." |
| P2 | Default C++ standard shifts to C++20 (Finding 10; "scheduled for 2026-02-08") | **Shipped** in 4.6.0. The exact date it switched in R-devel was not confirmed (UNVERIFIED). | "The default C++ standard has been changed to C++20 where available (which it is on all known platforms from 2021 on): if not C++17 is used if available otherwise C++ is not supported (as before). (GCC 16 has also switched to C++20 as its default.) Packages can request C++17 if essential." |
| P3 | `R_nchar`, `R_tryWrap` NOTE to WARNING (Finding 11) | **Shipped** | "R CMD check 'NOTE's on the use of these non-API entry points have been upgraded to 'WARNING's ...: R_nchar, R_tryWrap, Rf_GetOption, R_lsInternal, BODY, FORMALS, CLOENV, SET_TYPEOF, STRING_PTR, R_duplicate_attr, getConnection, R_data_class, STRING_PTR, SET_OBJECT, ATTRIB, SET_ATTRIB, Rf_findVarInFrame3." |
| P4 | `VECTOR_PTR` NOTE to WARNING (Findings 3, 11) | **Changed (stronger): removed** | "The function VECTOR_PTR has been removed. The non-API function DATAPTR is no longer declared in an installed header file." |
| P5 | `R_ext/Callbacks.h` and `R_ext/PrtUtil.h` no longer installed; switch to `R_ext/ObjectTable.h` (Finding 12) | **Partly changed.** `PrtUtil.h` removal shipped. `Callbacks.h` was **not** removed: the `R_ObjectTable` types moved to the new `ObjectTable.h`, and task-callback support in `Callbacks.h` was re-enabled. | "The R_ObjectTable type definitions formerly in 'R_ext/Callbacks.h' are now available in the new header file 'R_ext/ObjectTable.h'. This new header file should be used in packages instead of 'R_ext/Callbacks.h'." / "Task callback support declared in 'R_ext/Callbacks.h' has been enabled again. It was disabled for R 4.5.0." / "The non-API header file 'R_ext/PrtUtil.h' is no longer copied to the installed 'include' directory." |
| P6 | Open question: "Will CRAN update the policy document?" | **Yes.** Two substantive revisions (Part 1). | SVN log above |

Net result: 6 of 6 predictions resolved. 4 shipped as predicted (P1 shipped in a stronger form), 2 shipped in a changed form (P4, P5). None was dropped.

---

## Part 3: R CMD check, toolchain and C API changes (R 4.5.3, 4.6.0, 4.6.1)

### Finding 5: Large non-API cleanup in R 4.6.0 (C-level)

R 4.6.0 NEWS ("C-Level Facilities"), verbatim highlights:

- **Hidden** (no declarations, so compilation fails; not just a check NOTE): "These entry points are now marked as hidden and no longer have declarations in installed header files: ENVFLAGS, EXTPTR_PROT, FRAME, ENCLOS, EXTPTR_PTR, EXTPTR_TAG, HASHTAB, IS_S4_OBJECT, LEVELS, NAMED, OBJECT, R_shallow_duplicate_attr, Rf_isValidString, Rf_lazy_duplicate, Rf_NonNullStringMatch, SETLENGTH, SETLEVELS, SET_BODY, SET_CLOENV, SET_ENCLOS, SET_FORMALS, SET_ENVFLAGS, SET_FRAME, SET_GROWABLE_BIT, SET_HASHTAB, SET_NAMED, SET_S4_OBJECT, SET_TRUELENGTH, STDVEC_DATAPTR, TRUELENGTH, UNSET_S4_OBJECT, XTRUELENGTH."
- **Removed declarations:** "Declarations for non-API functions LOGICAL0, INTEGER0, REAL0, COMPLEX0, and RAW0 have been removed from installed header files."
- **Removed functions:** "The function Rf_isFrame has been removed; use Rf_isDataFrame instead." and `VECTOR_PTR` (P4).
- **Upgraded from NOTE to WARNING:** the P3 list, plus "PRCODE, SET_PRCODE, PRENV, SET_PRENV, PRVALUE, SET_PRVALUE, R_PromiseExpr, and Rf_allocSExp".
- **Newly reported:** "Non-API entry points Rf_acopy_string and Rf_lazy_duplicate have been added to those reported by R CMD check."
- **Non-API variables:** "Packages using any non-API variables will now receive check 'NOTE's."
- **New API replacements:** `R_getVar`/`R_getVarEx` (for `Rf_findVar`/`Rf_findVarInFrame`), `R_mapAttrib`, `R_getAttributes`, `R_getAttribCount`, `R_getAttribNames`, `R_hasAttrib`, `R_nrow`, `R_ncol`, `R_class`, `Rf_isScalarString`, `R_altrep_class_name`/`R_altrep_class_package` (instead of `ALTREP_CLASS`), `DATAPTR_RW` (ALTREP `Dataptr` methods only), `R_envSymbols`, `R_getRegisteredNamespace`, and the experimental bindings API (`R_GetBindingType`, `R_MakeDelayedBinding`, ...).
- `CHARACTER_DATA`/`CHARACTER_POINTER` now return `const` pointers. This can break code that writes through them.
- Graphics engine `R_GE_version` was bumped to 17, so device packages must be reinstalled.

**Impact:** packages that still call `TRUELENGTH`, `SETLENGTH`, `NAMED`, `OBJECT`, `LEVELS`, `FRAME`, `ENCLOS` and similar now fail to **compile** against R 4.6.0. Before, they got a check WARNING. This is the biggest compiled-code break of 2026.

- Source: https://cran.r-project.org/doc/manuals/r-release/NEWS.html (R 4.6.0, "C-Level Facilities")

### Finding 6: C++ standard changes (R 4.5.3 and 4.6.0)

- **R 4.5.3** (2026-03-11): "C++ standard specifications (CXX_STD = in 'src/Makevars*' and in the SystemRequirements field of the 'DESCRIPTION' file) are now checked more thoroughly. Invalid values are still ignored but now give a warning, as do contradictory specifications." and "(Preliminary) support for C++26 has been extended to Windows."
- **R 4.5.3:** "A non-zero exit status from 'cleanup', 'cleanup.win' or 'cleanup.ucrt', if requested via options --clean or --preclean, is now reported with a warning."
- **R 4.6.0:** C++20 is the default and C++11/14 support is removed (P1, P2). There is also a new `tests/C++Standards` directory for test-installing packages under different standards.

- Source: https://cran.r-project.org/doc/manuals/r-release/NEWS.html (R 4.5.3 "Package Installation"; R 4.6.0 "Significant User-Visible Changes", "Package Installation", "Checking an Installation")

### Finding 7: New `--as-cran` behaviour in R 4.6.0 that NEWS does not document

I diffed the `if (as_cran) {...}` block of `tools/R/check.R` between `R-4-5-branch` and `R-4-6-branch`. Four settings are new in R 4.6. **None of them appears in R 4.6.0 NEWS.**

| Setting | Effect | Severity |
|---|---|---|
| `_R_CHECK_RCPP_NOT_NEEDED_=TRUE` | Install output matching `"LdFlags.* has not been needed since 2013"` is added to "Found the following significant warnings". This is the message Rcpp prints when `Rcpp:::LdFlags()` or `RcppLdFlags()` is called, e.g. from `PKG_LIBS = $(shell ... Rscript -e "Rcpp:::LdFlags()")` in `src/Makevars`. | **WARNING** |
| `_R_CHECK_URLS_SHOW_301_STATUS_=TRUE` | URL reports for moved URLs now show `Status: 301` / `Message: Moved Permanently` next to "(moved to ...)". | Formatting of an existing NOTE |
| `R_check_urls_relative_paths <- TRUE` | New check step "checking relative paths in package URLs". Relative links in Rd files and vignettes are resolved against the installed package's help server, and broken ones are reported as "Found the following (possibly) invalid URLs:". | NOTE |
| `R_check_Rd_bibentries_cited_not_shown <- TRUE` | For Rd files using the new R 4.6.0 bibliography macros, reports "Bibentries cited but not shown in Rd file 'x.Rd':" (a `\bibcitet`/`\bibcitep` with no matching `\bibshow`). Also reports "Found bibentries with unexpected macro expansions. Rebuild with R >= 4.6.0?" when `build/partial.rdb` is missing or stale. | NOTE |

The CRAN team's own incoming-check script added the Rcpp check first. Comment in `check_CRAN_incoming.R`:

> "Added on 2026-02-19 and on for '--as-cran', but perhaps a bit much for the regular checks, so for now only here ...?"

So incoming submissions have been checked for this since about 2026-02-19, two months before R 4.6.0 shipped.

Rcpp's own message (current master) is:

> "'Rcpp:::LdFlags' has not been needed since 2013 (!!) and may get removed in 2027. Please update your 'Makevars'."

`Rcpp:::CxxFlags` prints a similar message, but the check regex does not match it.

- Source: https://svn.r-project.org/R/branches/R-4-6-branch/src/library/tools/R/check.R (as_cran block; `_R_CHECK_RCPP_NOT_NEEDED_` handling)
- Source: https://svn.r-project.org/R/branches/R-4-5-branch/src/library/tools/R/check.R (absence of the four settings)
- Source: https://svn.r-project.org/R/trunk/src/library/tools/R/urltools.R (`.check_package_urls_relative_paths`, `format.check_url_db`)
- Source: https://svn.r-project.org/R/trunk/src/library/tools/R/bibtools.R (`.check_Rd_bibentries_cited_not_shown`)
- Source: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/Kurt/lib/R/Scripts/check_CRAN_incoming.R
- Source: https://raw.githubusercontent.com/RcppCore/Rcpp/master/R/RcppLdpath.R

### Finding 8: New Rd features in R 4.6.0 that require `R (>= 4.6.0)`

- **Bibliographic citation macros:** `\bibcitet{}`, `\bibcitep{}`, `\bibshow{}`, `\bibinfo{}{}{}`. They read bibentries from `inst/REFERENCES.R` (R format) or `inst/REFERENCES.bib` (BibTeX, needs `bibtex`), from `pkg::key`, or from R's own database. NEWS: "Bibliographic citations and references in Rd files can now be auto-generated from bibentries in bibliographic databases in R or BibTeX formats." Writing R Extensions: "For R at least 4.6.0 one can auto-generate bibliographic citations and references ...".
- **`\linkS4class[<pkg>]{<myClass>}`:** NEWS (verbatim): "Packages with the new syntax need to formally depend on 'R >= 4.6.0'."
- **New macros:** `\linkS4methods{}` and `\manual{name}{node}`.
- **README:** "Package 'README.md' files are now installed and featured in HTML help." README content is therefore more visible to users. This matters for Finding 2 and for URL checks.
- `read.dcf()` now treats lines starting with `#` as comments. This affects DESCRIPTION parsing.

- Source: https://cran.r-project.org/doc/manuals/r-release/NEWS.html (R 4.6.0 "New Features", "Utilities")
- Source: https://svn.r-project.org/R/trunk/doc/manual/R-exts.texi (section "Bibliographic citations and references")

### Finding 9: Other R 4.6.0 changes relevant to submissions

- "R CMD check now reports further clang warnings including -Wkeyword-macro." This is the C23 `bool`/`true`/`false`/`nullptr` masking issue. The previous report listed it as R 4.5.0; the R 4.6.0 NEWS lists it under 4.6.0 "Utilities", so the earlier attribution may have come from R-devel NEWS before release.
- "R CMD check when passed a tarball looks at its contents and so no longer derives the package name from the tarball name (which can now be arbitrary)."
- New package integrity and signing support (`SHA256`, `SHA256.sig`; `R CMD build --sha256`; `R CMD INSTALL --sign`). This is optional, and CRAN has not announced any requirement (none found).
- `structure(NULL, <name> = <val>)` is now **defunct** (an error), and the `tk*.slaves()` functions are deprecated.
- Custom binary package types `"<system>.binary.<build>"` were added, and the `Built` field timestamp is honoured. These matter to repository builders, not to authors.

- Source: https://cran.r-project.org/doc/manuals/r-release/NEWS.html

### Finding 10: R 4.6.1 (2026-06-24)

No new checks. Bug fixes, an updated `jss.cls`, and better plain-text rendering of `\eqn{}` for `\geq`, `\leq`, `\neq`, `\ne`. The `stl()` code was moved from Fortran to C because of a flang 22 optimisation bug.

- Source: https://cran.r-project.org/doc/manuals/r-release/NEWS.html (R 4.6.1)

### Finding 11: R-devel (future R 4.7.0) changes already visible (watch list)

These are in R-devel NEWS or trunk `check.R` as of 2026-10-05. They are **not** in any release yet.

- **`--as-cran` sets `_R_CHECK_CODOC_FUNCTIONS_MISSING_FROM_USAGES_=NA`** (trunk only). "Exported functions without usage information" is reported as INFO under `--as-cran` (NOTE when the variable is set to a true value, WARNING in some code paths). Not in NEWS; seen in source only.
- **PDF vignettes:** "tools::texi2pdf() now reports BibTeX warnings; in particular, missing references are now noted by R CMD check when re-building PDF vignettes."
- **`data/datalist`:** "R CMD build now excludes an obsolete 'data/datalist' file when the package uses 'LazyData', and reports when it added one."
- **DCF files are UTF-8:** "read.dcf() and write.dcf() now treat DCF files (such as package 'DESCRIPTION' ...) as UTF-8 ... non-UTF-8 'DESCRIPTION' files (e.g. those declaring 'Encoding: latin1') are no longer re-encoded on reading." This will affect ENC-01 guidance.
- `.Rbuildignore` patterns are applied before the package directory is copied, so broken symlinks matching an exclude pattern no longer break `R CMD build`.
- `structure()` deprecates the `.Dim`, `.Dimnames`, `.Names`, `.Tsp` and `.Label` attribute names.
- `rbinom()` was fixed, so reproducing old results needs `RNGversion("4.6")`. This can change test snapshots.

- Source: https://cran.r-project.org/doc/manuals/r-devel/NEWS.html
- Source: https://svn.r-project.org/R/trunk/src/library/tools/R/check.R

---

## Part 4: CRAN Infrastructure and Process

### Finding 12: CRAN check configuration changes (CRAN QA scripts, Hornik)

`QA/Kurt/.R/check.Renviron` changed between r6746 (header "Last updated on 2025-12-15") and r6966 (header "Last updated on 2026-08-10"):

- Added `_R_CHECK_RD_BIBENTRIES_CITED_NOT_SHOWN_=true`, `_R_CHECK_URLS_RELATIVE_PATHS_=true`, `_R_CHECK_RD_CONTENTS_USAGE_=true` and `_R_CHECK_CODOC_FUNCTIONS_MISSING_FROM_USAGES_=${...-NA}`.
- Commented out a planned `_R_CHECK_THINGS_IN_OTHER_DIRS_=true`.
- `_R_CHECK_RD_MATH_RENDERING_` default changed from `true` to `NA`. The KaTeX math check may now report as INFO rather than NOTE on CRAN's regular checks (interpretation UNVERIFIED).
- `_R_CHECK_DOC_SIZES2_` was commented out in the regular checks but **added** to the incoming checks.
- `_R_CHECK_RD_CONTENTS_USAGE_` does not appear in R 4.6 or trunk `check.R` (grep). Its effect is UNVERIFIED.

The incoming check script raised its elapsed-time limits:

| Variable | Before | After |
|---|---|---|
| `_R_INSTALL_PACKAGES_ELAPSED_TIMEOUT_` | 90m | 180m (default) |
| `_R_CHECK_ELAPSED_TIMEOUT_` | 30m | 180m (default) |
| `_R_CHECK_INSTALL_ELAPSED_TIMEOUT_` | 90m | 180m (default) |

These are hard kill limits. They are not the 10-minute check-time guidance in SIZE-02, which is unchanged.

- Source: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/Kurt/.R/check.Renviron (diff r6746 to r6966)
- Source: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/Kurt/lib/R/Scripts/check_CRAN_incoming.R

### Finding 13: Check flavors (January 2026 vs October 2026)

| Flavor | 2026-01-07 | 2026-10-05 |
|---|---|---|
| r-devel-linux-x86_64-debian-clang | clang/flang 21.1.8 | **clang/flang 23.1.0** |
| r-devel-linux-x86_64-debian-gcc | GCC 15.2.0 | **GCC 16.2.0** |
| r-devel-linux-x86_64-fedora-clang | Fedora 42, clang 21.1.0 | **Fedora 44, clang/flang 23.1.0**, new hardware |
| r-devel-linux-x86_64-fedora-gcc | Fedora 42, GCC 15.1.1 | **Fedora 44, GCC 16.2.1** |
| r-patched / r-release linux | GCC 14.3.0 | GCC 15.3.0 |
| r-devel / r-release windows | GCC 14.2.0 | **GCC 14.3.0** (Rtools45) |
| r-oldrel-windows | GCC 13.2.0 | GCC 14.3.0 |
| r-release-macos-arm64 | macOS 13.4, M1 Mac mini, Apple clang 1400 | **macOS 15.7.1, Apple M3 Ultra, Apple Clang 1700.3.19.1** |
| r-release / oldrel macos-x86_64 | macOS 13.3.1, Apple clang 1403 | unchanged |
| r-oldrel-macos-arm64 | macOS 13.4 (M1) | unchanged (now R 4.5) |

Notes:
- GCC 16 defaults to C++20. LLVM 23 libc++ dropped transitive includes (Finding 14).
- There is still no r-devel macOS flavor on the public page.

- Source: https://cran.r-project.org/web/checks/check_flavors.html (fetched 2026-10-05)
- Source: https://web.archive.org/web/20260115000000/https://cran.r-project.org/web/checks/check_flavors.html (snapshot "Last updated on 2026-01-07")

### Finding 14: clang 23 / libc++ "transitive includes" notification wave (Aug-Sep 2026)

Brian Ripley's additional-issues README for clang 23:

> "Checks using LLVM 23.1.0, released 2026-08-25." ... "libc++ has dropped a lot of transitive includes in all language modes ... Any errors caused by this should be fixable by including the correct header. To ease the transition _LIBCPP_KEEP_TRANSITIVE_INCLUDES_LLVM23 can be defined ... This macro will be removed in LLVM 24." ... "So if declaration(s) (especially in std:) are reported as missing, do ensure that the header(s) which declare them are included. Most commonly <algorithm> or <iterator> is missing." ... "People writing C and calling it C++ need to include headers such as <cstdlib>, <cstddef>, <cmath> or <ctime>. These have been needed for nullptr_t size_t fabs isnan log sqrt clock localtime time"

- The fedora-clang checks define `_LIBCPP_KEEP_TRANSITIVE_INCLUDES_LLVM23`; the debian-clang checks do not.
- SVN r6946 (2026-09-04) added a new set of CRAN notification scripts under `QA/BDR/gannet2/packages/NEW/`, including a `CRAN_clang23.R` template ("Additional_issues:clang23"). Like the other templates, it sets a 21-day deadline (`Before(21)`).
- A `Before()` helper moves any deadline that falls between 2026-09-21 and 2026-09-26 to 2026-09-27. This suggests CRAN was closed that week. That reading is an inference; no CRAN closure announcement was found (UNVERIFIED).

- Source: https://www.stats.ox.ac.uk/pub/bdr/clang23/README.txt
- Source: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/BDR/gannet2/packages/NEW/ (CRAN_clang23.R, Before.R, CRAN_suggests.R, cran_problems_escalation.R)

### Finding 15: macOS binaries move to macOS 14 (Sonoma) target on arm64

From the mac.r-project.org front page:

> "R 4.6.0 CRAN arm64 builds use Xcode 26.0.1, macOS 14 target and 14.4 SDK with package type mac.binary.sonoma-arm64."
> "We are no longer building binaries for macOS versions before 11 ... and before macOS 14 on Apple Silicon."

- Intel (`big-sur-x86_64`) stays on the macOS 11 target.
- The external libraries for arm64 moved to `darwin23/arm64` (Finding 4).
- Packages whose `configure` hard-codes `darwin20/arm64` or `big-sur-arm64` paths need updating.

- Source: https://mac.r-project.org/

### Finding 16: Rtools45 (Windows) updates; no Rtools46

- No Rtools46 exists. The Rtools index says Rtools45 is "for R versions from 4.5.0 (including R-devel)", and `.../rtools46/rtools.html` returns 404.
- **Rtools45 revision 6691:** "GCC has been updated to version 14.3 (from 14.2)". Curl gained a `secur32` dependency ("packages using curl need to be updated, unless they are already using pkg-config. No CRAN packages are affected"). Also Tcl/Tk 8.6.17 and eigen 5.0.0, among others.
- **Revision 6768** (current installer `rtools45-6768-6492.exe`): library updates (gdal 3.12.1, geos 3.14.1, proj 9.7.1, curl 8.18.0, ...) and new muparser.
- Exact release dates of these revisions are not shown on the page (UNVERIFIED). The Windows check flavors had moved from GCC 14.2.0 to 14.3.0 by October 2026.

- Source: https://cran.r-project.org/bin/windows/Rtools/
- Source: https://cran.r-project.org/bin/windows/Rtools/rtools45/rtools.html
- Source: https://cran.r-project.org/bin/windows/Rtools/rtools45/news.html

### Finding 17: Submission statistics (R Journal "Changes on CRAN")

| Period | New | Archived | Unarchived | Submissions | Auto-processed actions | Active packages at end |
|---|---|---|---|---|---|---|
| 2025-10-01 to 2025-12-31 | 590 | 594 | 158 | 7,066 | 75% | ~22,969 |
| 2026-01-01 to 2026-06-30 | 1,992 | 1,273 | 462 | 18,293 | 72% | ~24,105 |

- Final decisions in H1 2026: 27.1% auto-archive, 29.2% auto-publish, 18.2% manual archive, 25.5% manual publish.
- No issue 2026-1 column exists (404). The H1 2026 column covers six months.
- The columns contain no policy announcements.

- Source: https://journal.r-project.org/news/RJ-2025-4-cran/
- Source: https://journal.r-project.org/news/RJ-2026-2-cran/

### Finding 18: R Blog (2026)

The 2026 posts:
- "Debugging sensitivity to C math library and mingw-w64 v12" (2026-01-06)
- "Debugging sensitivity to C math library on Linux" (2026-01-30). This is the background for R 4.6.0 making `exp`, `log1p` and similar exact near special values.
- "S at 50" (2026-05-05)
- Sovereign Tech Fund milestones (2026-06-02, 2026-09-29)
- Rousseeuw Prize (2026-06-17)
- "New tricks for the R Sweave drivers" (2026-09-18)
- "Zulip chat for the R project" (2026-09-22)

None announces a CRAN policy or submission-process change. The STF posts were not read in full; their relevance to package signing is UNVERIFIED.

- Source: https://blog.r-project.org/

### Finding 19: Submission system

- The CRAN-side incoming check scripts show no change to the submission form or workflow in this period.
- R-package-devel was not surveyed (see Limitations). Any announcements made only on the mailing list are **not** captured here.

---

## Sources

1. CRAN Repository Policy (live): https://cran.r-project.org/web/packages/policies.html
2. CRAN policy SVN source: https://svn.r-project.org/R-dev-web/trunk/CRAN/Policy/CRAN_policies.texi
3. CRAN policy SVN revisions: https://svn.r-project.org/R-dev-web/!svn/bc/6734/trunk/CRAN/Policy/CRAN_policies.texi , .../6738/..., .../6846/..., .../6875/..., .../6942/...
4. CRAN policy tracker: https://github.com/eddelbuettel/crp/commits/master
5. Using external libraries: https://cran.r-project.org/web/packages/external_libs.html (SVN r6797, r6850)
6. R release NEWS (4.6.1, 4.6.0, 4.5.3): https://cran.r-project.org/doc/manuals/r-release/NEWS.html
7. R-devel NEWS: https://cran.r-project.org/doc/manuals/r-devel/NEWS.html
8. R source tarballs and dates: https://cran.r-project.org/src/base/R-4/
9. `check.R` R 4.6 branch: https://svn.r-project.org/R/branches/R-4-6-branch/src/library/tools/R/check.R
10. `check.R` R 4.5 branch: https://svn.r-project.org/R/branches/R-4-5-branch/src/library/tools/R/check.R
11. `check.R` trunk: https://svn.r-project.org/R/trunk/src/library/tools/R/check.R
12. `urltools.R` / `bibtools.R` trunk: https://svn.r-project.org/R/trunk/src/library/tools/R/
13. Writing R Extensions source: https://svn.r-project.org/R/trunk/doc/manual/R-exts.texi
14. CRAN incoming check script: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/Kurt/lib/R/Scripts/check_CRAN_incoming.R
15. CRAN check environment: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/Kurt/.R/check.Renviron
16. CRAN notification scripts: https://svn.r-project.org/R-dev-web/trunk/CRAN/QA/BDR/gannet2/packages/NEW/
17. clang 23 additional issues README: https://www.stats.ox.ac.uk/pub/bdr/clang23/README.txt
18. CRAN check flavors: https://cran.r-project.org/web/checks/check_flavors.html
19. CRAN check flavors, Jan 2026 snapshot: https://web.archive.org/web/20260115000000/https://cran.r-project.org/web/checks/check_flavors.html
20. R for macOS: https://mac.r-project.org/
21. Rtools: https://cran.r-project.org/bin/windows/Rtools/ and https://cran.r-project.org/bin/windows/Rtools/rtools45/news.html
22. R Journal Changes on CRAN: https://journal.r-project.org/news/RJ-2025-4-cran/ , https://journal.r-project.org/news/RJ-2026-2-cran/
23. R Blog: https://blog.r-project.org/
24. Rcpp LdFlags message: https://raw.githubusercontent.com/RcppCore/Rcpp/master/R/RcppLdpath.R

---

## Proposed knowledge base changes

Rule IDs refer to `knowledge/cran-rules.md`. These are proposals only; that file was not edited.

### (a) Updates to existing rules

**DEP-01: Strong Dependencies Must Be on CRAN or Bioconductor**
- **Rule:** change to "Packages in Depends, Imports, LinkingTo must be available from CRAN or the Bioconductor *software* repository. Bioconductor annotation and experiment-data packages may only appear in Suggests/Enhances (no `Additional_repositories` needed for them). Other non-CRAN Suggests/Enhances need `Additional_repositories` or access instructions in Description."
- **CRAN says:** add the verbatim r6734 text from Finding 1.
- **Detection:** add "flag strong deps that are BioC annotation/experiment packages (BiocManager repositories `BioCann`, `BioCexp`)".
- **Fix:** add "move BioC data/annotation packages to Suggests and use them conditionally".
- **Since:** add "Pre-2015 (general); BioC-software-only restriction since CRAN policy SVN r6734 (committed 2025-12-15, published by 2026-02-20)".

**COMP-03: Non-API Entry Points**
- **Rule:** change "R 4.6.0 will upgrade more" to "R 4.6.0 upgraded more, hid ~33 entry points (compilation now fails) and removed VECTOR_PTR and Rf_isFrame".
- **Detection:** split into three lists.
  - (i) **Compile failure (hidden/removed):** `ENVFLAGS, EXTPTR_PROT, FRAME, ENCLOS, EXTPTR_PTR, EXTPTR_TAG, HASHTAB, IS_S4_OBJECT, LEVELS, NAMED, OBJECT, R_shallow_duplicate_attr, Rf_isValidString, Rf_lazy_duplicate, Rf_NonNullStringMatch, SETLENGTH, SETLEVELS, SET_BODY, SET_CLOENV, SET_ENCLOS, SET_FORMALS, SET_ENVFLAGS, SET_FRAME, SET_GROWABLE_BIT, SET_HASHTAB, SET_NAMED, SET_S4_OBJECT, SET_TRUELENGTH, STDVEC_DATAPTR, TRUELENGTH, UNSET_S4_OBJECT, XTRUELENGTH, VECTOR_PTR, Rf_isFrame, LOGICAL0, INTEGER0, REAL0, COMPLEX0, RAW0, DATAPTR`.
  - (ii) **WARNING:** `R_nchar, R_tryWrap, Rf_GetOption, R_lsInternal, BODY, FORMALS, CLOENV, SET_TYPEOF, STRING_PTR, R_duplicate_attr, getConnection, R_data_class, SET_OBJECT, ATTRIB, SET_ATTRIB, Rf_findVarInFrame3, PRCODE, SET_PRCODE, PRENV, SET_PRENV, PRVALUE, SET_PRVALUE, R_PromiseExpr, Rf_allocSExp`.
  - (iii) **NOTE:** `Rf_acopy_string`, any non-API *variable*, plus the remaining R 4.5 list (`IS_LONG_VEC, Rf_StringBlank, XLENGTH_EX`).
  - Also flag `#include <R_ext/PrtUtil.h>`, and writes through `CHARACTER_DATA`/`CHARACTER_POINTER`.
- **Fix:** add replacements:
  - `R_getVar`/`R_getVarEx` for `Rf_findVar*`
  - `R_mapAttrib`/`R_getAttributes`/`R_hasAttrib` for `ATTRIB`
  - `R_class` for `R_data_class`
  - `Rf_isDataFrame` for `Rf_isFrame`
  - `R_altrep_class_name` for `ALTREP_CLASS`
  - `DATAPTR_RW` only inside ALTREP `Dataptr` methods
  - `R_ext/ObjectTable.h` instead of `R_ext/Callbacks.h` for `R_ObjectTable`
- **Severity:** "WARNING → REJECTION; compile ERROR for hidden entry points".
- **Since:** "R 4.3+ progressively; major tightening R 4.6.0 (2026-04-24)".

**COMP-06: C++11/C++14 Specifications Deprecated**
- **Title:** "C++11/C++14 Specifications Defunct".
- **Severity:** "NOTE (R < 4.6) / ignored-and-defunct (R >= 4.6.0)". The exact check output under 4.6.0 was not confirmed (UNVERIFIED).
- **Rule:** "R 4.6.0 removed support for C++11/C++14: such specifications are ignored and the default C++ standard (C++20 where available) is used; `CXX11`, `CXX14`, `CXX11FLAGS`, `CXX14STD`, `SHLIBCXX11LD` etc. are reported as defunct."
- **Detection:** also grep `src/Makevars*` and `configure*` for `CXX1[14](FLAGS|PICFLAGS|STD)?\b|SHLIBCXX1[14]LD(FLAGS)?` and `R CMD config CXX1[14]`.
- **CRAN says:** the verbatim P1 text.
- **Since:** "R 4.6.0 (2026-04-24)".

**SYS-03: C++20 Default Standard Transition**
- **CRAN says:** the current quote "C++20 is now the default C++ standard where available." is **not verbatim**. Replace it with "The default C++ standard has been changed to C++20 where available ...: if not C++17 is used if available ... (GCC 16 has also switched to C++20 as its default.) Packages can request C++17 if essential."
- **Detection:** note that GCC 16.2 and clang 23 are now on the r-devel flavors.
- **Since:** "R 4.6.0 (2026-04-24)".

**SYS-06: Contradictory C++ Standard Between SystemRequirements and Makevars**
- **Rule:** "validates this since R 4.5" should be "since R 4.5.3 (2026-03-11)". The quoted text is from the R 4.5.3 NEWS, not 4.5.0.
- **Since:** add "R 4.5.3 (2026-03-11)".

**MISC-07: URL Permanent Redirects Not Tolerated**
- **CRAN says:** append "From R 4.6.0, `--as-cran` sets `_R_CHECK_URLS_SHOW_301_STATUS_`, so moved URLs are reported as `URL: <old> (moved to <new>)` with `Status: 301` / `Message: Moved Permanently`."
- **Since:** append "explicit 301 status display under --as-cran from R 4.6.0".

**COMP-12: UCRT Windows Toolchain Compatibility**
- **Rule:** append "Rtools45 serves R 4.5.x, 4.6.x and R-devel (no Rtools46); since Rtools45 rev 6691 the compiler is GCC 14.3 and curl requires `secur32` for packages not using pkg-config."

**ENC-01: Missing Encoding Field in DESCRIPTION**
- Watch-list note only; no change yet. R-devel treats DESCRIPTION as UTF-8 and no longer re-encodes `Encoding: latin1` files. Revisit when R 4.7.0 is released.

### (b) Proposed new rules

#### CODE-23: No Divisive or Offensive Material (e.g., Political Slogans)
- **Severity:** REJECTION (policy)
- **Rule:** Packages must not contain or display material that might be considered divisive or give offence, such as political slogans. This applies to startup messages, printed output, documentation, README, data and vignettes.
- **CRAN says:** "Packages should not contain nor display material which might be considered divisive or give offence, such as political slogans."
- **Detection:** heuristic and manual-review flag only.
  - Scan `.onAttach`/`.onLoad` `packageStartupMessage()`/`message()`/`cat()` strings.
  - Scan `DESCRIPTION` Title/Description, `README.md`, `inst/` text and `R/*.R` string literals for slogan-like content (e.g. a curated keyword list; anything with "!" in a startup message). Report as "review manually"; never auto-fail.
- **Fix:** Remove the material. Put non-technical statements on an external website, not in the package.
- **Files:** `R/zzz.R`, `R/*.R`, `DESCRIPTION`, `README.md`, `man/*.Rd`, `vignettes/*`, `inst/*`
- **Since:** CRAN policy SVN r6942 (committed 2026-09-02); on the live policy page by 2026-07-27 (page still labelled Rev 6875)

#### COMP-13: Obsolete Rcpp Linker/Compiler Flags in Makevars
- **Severity:** WARNING → REJECTION
- **Rule:** `Rcpp:::LdFlags()` / `RcppLdFlags()` (and `RcppLdPath()`) have been unnecessary since 2013. Under `--as-cran` from R 4.6.0 (and in CRAN incoming checks since about 2026-02-19), the message they print during installation is a "significant warning". `LinkingTo: Rcpp` is all that is needed.
- **CRAN says:** "Found the following significant warnings: 'Rcpp:::LdFlags' has not been needed since 2013 (!!) and may get removed in 2027. Please update your 'Makevars'." (Check regex: `LdFlags.* has not been needed since 2013`.)
- **Detection:** grep `src/Makevars*` for `Rcpp:::LdFlags|RcppLdFlags|RcppLdPath|Rcpp:::CxxFlags`. `CxxFlags` is not matched by R's regex, so report it as a NOTE-level recommendation.
- **Fix:** delete the `PKG_LIBS += $(shell ... Rcpp:::LdFlags())` and `PKG_CXXFLAGS = ... Rcpp:::CxxFlags()` lines. Keep `LinkingTo: Rcpp` in DESCRIPTION.
- **Files:** `src/Makevars`, `src/Makevars.win`, `src/Makevars.ucrt`, `src/Makevars.in`
- **Since:** R 4.6.0 (2026-04-24) via `_R_CHECK_RCPP_NOT_NEEDED_` in the `--as-cran` defaults (not in NEWS); CRAN incoming since about 2026-02-19

#### COMP-14: Missing Standard C++ Headers (libc++ Transitive Includes, LLVM 23)
- **Severity:** ERROR on r-devel clang flavors, leading to a CRAN problem notification with a 21-day deadline
- **Rule:** C++ code must `#include` every standard header it uses. LLVM 23's libc++ dropped many transitive includes, so code that relied on `<vector>` pulling in `<algorithm>` and similar no longer compiles.
- **CRAN says:** "if declaration(s) (especially in std:) are reported as missing, do ensure that the header(s) which declare them are included. Most commonly <algorithm> or <iterator> is missing." / "People writing C and calling it C++ need to include headers such as <cstdlib>, <cstddef>, <cmath> or <ctime>."
- **Detection:** for each `src/*.cpp|*.cc|*.h|*.hpp` translation unit, map used identifiers to their headers and flag any header not directly included. Examples: `std::sort|std::find|std::max_element` need `<algorithm>`; `std::back_inserter|std::distance|std::advance` need `<iterator>`; `std::is_same|std::enable_if` need `<type_traits>`; `size_t|nullptr_t` need `<cstddef>`; `fabs|isnan|sqrt|log` need `<cmath>`; `clock|time|localtime` need `<ctime>`; `malloc|exit|abs` need `<cstdlib>`. This is heuristic, so report as WARNING.
- **Fix:** add the missing `#include`. Do not depend on `_LIBCPP_KEEP_TRANSITIVE_INCLUDES_LLVM23`, which will be removed in LLVM 24.
- **Files:** `src/*.cpp`, `src/*.cc`, `src/*.h`, `src/*.hpp`, `inst/include/**`
- **Since:** August/September 2026. LLVM 23.1.0 was released 2026-08-25 and adopted on the r-devel-linux debian-clang and fedora-clang flavors; CRAN `clang23` notifications began around 2026-09-04.

#### DOC-12: Relative Links in Rd and Vignettes Must Resolve
- **Severity:** NOTE
- **Rule:** Relative URLs in Rd files and vignettes (for example `../doc/foo.html`, `../../otherpkg/html/topic.html`, `../help/topic`) must resolve against the installed package's help system. Broken ones are reported in a new check step.
- **CRAN says:** "checking relative paths in package URLs ... NOTE  Found the following (possibly) invalid URLs:  URL: <url>  From: <file>"
- **Detection:** extract `\href{}`/`\url{}` targets in `man/*.Rd` and `href=`/markdown links in `vignettes/*` that have no scheme. Flag paths that point to files the package does not install (no matching `inst/doc` file, vignette output or help topic).
- **Fix:** use `\link[pkg]{topic}` for help cross-references, `vignette("name", package = "pkg")` text, or absolute `https://CRAN.R-project.org/package=pkg/...` URLs.
- **Files:** `man/*.Rd`, `vignettes/*.Rmd`, `vignettes/*.Rnw`, `R/*.R` (roxygen)
- **Since:** R 4.6.0 (2026-04-24), `--as-cran` (`R_check_urls_relative_paths`; not in NEWS)

#### DOC-13: Rd Bibliography Citations Must Be Shown and Built with R >= 4.6.0
- **Severity:** NOTE
- **Rule:** When using the R 4.6.0 Rd bibliography macros, every entry cited with `\bibcitet{}`/`\bibcitep{}` must appear in a `\bibshow{}` (usually in `\references{}`). The tarball must be built with R >= 4.6.0 so that `build/partial.rdb` contains the expanded macros.
- **CRAN says:** "Bibentries cited but not shown in Rd file 'x.Rd':" and "Found bibentries with unexpected macro expansions.  Rebuild with R >= 4.6.0?"
- **Detection:** for each `man/*.Rd`, collect the `\bibcite[tp]{...}` keys and the `\bibshow{...}` keys (`*` means all keys cited so far). Flag cited keys not covered. If any `\bib*` macro is used, check that `build/partial.rdb` exists in the tarball, that `inst/REFERENCES.R` or `inst/REFERENCES.bib` exists for local keys, and that `bibtex` is in Suggests when `.bib` is used.
- **Fix:** add `\references{ \bibshow{*} }`. Rebuild with R >= 4.6.0. Add `Depends: R (>= 4.6.0)`.
- **Files:** `man/*.Rd`, `inst/REFERENCES.R`, `inst/REFERENCES.bib`, `DESCRIPTION`
- **Since:** R 4.6.0 (2026-04-24), `--as-cran` (`R_check_Rd_bibentries_cited_not_shown`; not in NEWS)

#### DOC-14: New R 4.6.0 Rd Syntax Requires `Depends: R (>= 4.6.0)`
- **Severity:** WARNING (check behaviour on older R is UNVERIFIED; NEWS states it as a requirement)
- **Rule:** Rd files that use `\linkS4class[pkg]{Class}`, `\linkS4methods{}`, `\manual{}{}` or `\bibcitet`/`\bibcitep`/`\bibshow`/`\bibinfo` need a formal `R (>= 4.6.0)` dependency.
- **CRAN says:** "Packages with the new syntax need to formally depend on 'R >= 4.6.0'." (R 4.6.0 NEWS, about `\linkS4class[<pkg>]{}`)
- **Detection:** grep `man/*.Rd` for `\\linkS4class\[|\\linkS4methods\{|\\manual\{|\\bibcite[tp]\{|\\bibshow\{|\\bibinfo\{`. If any match, parse `Depends:` for `R (>= x.y.z)` and flag when it is missing or lower than 4.6.0.
- **Fix:** add or raise `Depends: R (>= 4.6.0)`, or use the old form `\link[pkg:Class-class]{Class}`.
- **Files:** `man/*.Rd`, `DESCRIPTION`
- **Since:** R 4.6.0 (2026-04-24)

#### PLAT-03: Hard-Coded macOS Big Sur arm64 Paths/Targets
- **Severity:** WARNING (install failure on CRAN macOS arm64 builders)
- **Rule:** From R 4.6.0, CRAN macOS arm64 binaries target macOS 14 (package type `mac.binary.sonoma-arm64`), and external libraries live under `https://mac.r-project.org/bin/darwin23/arm64/`. `configure` scripts must not hard-code `darwin20/arm64`, `big-sur-arm64` or `-mmacosx-version-min=11` for arm64.
- **CRAN says:** "R 4.6.0 CRAN arm64 builds use Xcode 26.0.1, macOS 14 target and 14.4 SDK with package type mac.binary.sonoma-arm64." (mac.r-project.org). The external_libs policy now points to `darwin23/arm64` (SVN r6797).
- **Detection:** grep `configure*`, `src/Makevars*` and `tools/*` for `darwin20/arm64`, `big-sur-arm64`, `mac.binary.big-sur-arm64`, and arm64-specific `macosx-version-min=1[0-3]`.
- **Fix:** derive paths from `R CMD config` / `.Platform$pkgType`, or use `pkg-config`. Do not hard-code OS-versioned directories.
- **Files:** `configure`, `configure.ac`, `src/Makevars.in`, `tools/*.R`
- **Since:** R 4.6.0 (2026-04-24); external_libs policy r6797 (2026-02-20)

### Count

- **Updates to existing rules:** 7 (DEP-01, COMP-03, COMP-06, SYS-03, SYS-06, MISC-07, COMP-12), plus 1 watch-list note (ENC-01).
- **New rules:** 7 (CODE-23, COMP-13, COMP-14, DOC-12, DOC-13, DOC-14, PLAT-03).
- **Watch list (R-devel, not yet rules):**
  - `_R_CHECK_CODOC_FUNCTIONS_MISSING_FROM_USAGES_`
  - BibTeX missing-reference NOTEs for PDF vignettes
  - obsolete `data/datalist` with LazyData
  - DESCRIPTION read as UTF-8
  - `structure()` `.Dim`/`.Names` deprecation
  - `rbinom()` RNG change

## Open Questions

1. Why does the live policy page still say "Revision 6875" when it contains r6942 text? Will the next build change the label?
2. What exactly does `_R_CHECK_RD_CONTENTS_USAGE_` (set in CRAN's `check.Renviron`) do? It is not present in R 4.6 or trunk `check.R`.
3. Was CRAN closed during 2026-09-21 to 2026-09-26? This is inferred only from the notification-deadline helper.
4. Did R-package-devel announcements (not surveyed) add submission-process changes that are not visible in SVN?
