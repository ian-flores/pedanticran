# CRAN Policy Evolution 2023-2025

Generated: 2026-02-08

## Executive Summary

From 2023 through mid-2025, CRAN underwent significant tightening of enforcement across compiled code standards (C/C++ safety, non-API entry points, Fortran modernization), documentation quality (lost braces, Rd validation), and package size/vendoring requirements. R versions 4.3, 4.4, and 4.5 each introduced new R CMD check diagnostics that became immediate CRAN enforcement vectors. Community friction peaked in early 2025 with the "Is CRAN Holding R Back?" debate, spawning alternative repositories (CRANhaven, R-multiverse) and institutional responses (CRAN Cookbook, R Consortium working groups). The EU Cyber Resilience Act (effective 2027) looms as a future forcing function for all R package repositories.

---

## 1. CRAN Repository Policy Document Revisions

Source: [eddelbuettel/crp](https://github.com/eddelbuettel/crp/commits/master) -- tracking CRAN Repository Policy SVN revisions.

### Timeline of Revisions

| Date | Revision | Key Content Changes |
|------|----------|-------------------|
| 2023-07-12 | rev5686 | Added vendor.tar.xz guidance: "Source package tarballs should if possible not exceed 10MB. It is much preferred that third-party source software should be included within the package (as e.g. a vendor.tar.xz file) than be downloaded at installation." |
| 2023-07-23 | rev5709 | Removed `ftps` as acceptable secure download protocol; only `https` remains. Minor toolchain update. |
| 2023-07-25 | rev5711 | Minor revision (version bump, no substantive policy text change). |
| 2024-02-17 | rev5892 | Major HTML reformatting (Texinfo 7.1). No substantive policy text changes -- purely structural/rendering update. |
| 2024-04-04 | rev6097 | Formatting cleanup: DOI/ISBN/SSL/TLS wrapped in `<abbr>` tags. No new policy requirements. |
| 2024-08-20 | rev6277 | Reverted to Texinfo 6.8 formatting. No substantive policy text changes. |
| 2024-08-27 | rev6286 | Re-applied Texinfo 7.1 formatting. No substantive policy text changes. Most recent revision as of Feb 2026. |

### Key Observation

The policy document itself changed relatively little in substance between 2023-2025. The July 2023 revisions (vendor.tar.xz preference, ftps removal) were the only meaningful content changes. Most 2024 revisions were toolchain/formatting oscillations between Texinfo 6.8 and 7.1. **The real enforcement tightening came through R CMD check changes in R releases, not through policy document updates.**

---

## 2. R Version Changes Affecting CRAN Checks

### R 4.3.0 (April 2023)

Major new checks introduced:
- **sprintf/vsprintf deprecation**: R CMD check now reports if `sprintf()` or `vsprintf()` are found in compiled code. Must replace with `snprintf()`/`vsnprintf()`. Driven by macOS 13 deprecation and buffer overflow security risks.
- **C++ standard specification**: NOTE raised when packages specify `SystemRequirements: C++11` or `CXX_STD=CXX11`, since C++11 is the minimum since R 4.0.0 and C++17 is now the default.
- **Strict C function prototypes**: Warning for C function declarations without explicit prototypes (e.g., `int myfun()` instead of `int myfun(void)`).
- **browser() detection**: Non-interactive debugger invocations trapped via `_R_CHECK_BROWSER_NONINTERACTIVE_` (enabled by `--as-cran`), catching leftover `browser()` statements.
- **Rd file validation**: More checking of `.Rd` files -- invalid email addresses, invalid URIs, empty `\item` labels.
- **NEWS.md validation**: Reports problems when reading package news in markdown format.
- **KaTeX math rendering**: Optional check (included in `--as-cran`) for HTML math rendering via KaTeX.
- **Fortran random number generator**: Reports use of `RANDOM_NUMBER()` and its initialization subroutines.
- **Vignette error escalation**: Errors in re-building vignettes reported as ERROR rather than WARNING when vignette running was skipped.

Source: [R 4.3.0 Release Announcement](https://stat.ethz.ch/pipermail/r-announce/2023/000691.html), [Tidyverse blog on compiled code requirements](https://tidyverse.org/blog/2023/03/cran-checks-compiled-code/)

### R 4.3.x Point Releases (2023)

- **R 4.3.1** (June 2023): Bug fixes, no major new checks.
- **R 4.3.2** (Oct 2023): Compiler reporting improvements. R CMD check now reports the C and Fortran compilers used and the OS/build info.
- **R 4.3.3** (Feb 2024): `\Sexpr` evaluation failure messages now include Rd file name and line numbers. Bug fixes.

### R 4.4.0 (April 2024)

Major new checks introduced:
- **"Lost braces" detection**: The headline change. R CMD check now notes "lost braces" found by `tools::checkRd()`. Affected **over 3,000 CRAN packages**. Common triggers: Rd macros missing initial backslash (`code{...}` instead of `\code{...}`), unescaped set notation (`{1, 2}` needing `\{1, 2\}`), `\itemize` lists using `\describe`-style `\item{label}{description}`.
- **Rd files without \alias**: R CMD check notes Rd files lacking an `\alias`, as long documented in Writing R Extensions.
- **Non-portable Fortran KIND**: Warns on `INTEGER(KIND=4)`, `REAL(KIND=8)`, etc. Controlled by `_R_CHECK_FORTRAN_KIND_DETAILS_`.
- **Deprecated `as.data.frame` methods**: Twelve `as.data.frame.<class>()` methods formally deprecated.

Source: [R 4.4.0 Release Announcement](https://stat.ethz.ch/pipermail/r-announce/2024/000701.html), [R Journal Changes in R](https://journal.r-project.org/news/RJ-2024-2-rcore/)

### R 4.4.x Point Releases (2024-2025)

- **R 4.4.1** (June 2024):
  - Non-API entry points `Rf_setSVector`, `Rf_StringFalse`, `Rf_StringTrue`, `Rf_isBlankString` added to those reported by R CMD check.
  - Fortran 2018 deleted features now reported as **warnings** (previously notes).
  - `R_atof` and `R_strtod` formally documented as API.
- **R 4.4.2** (Oct 2024): Bug fixes.
- **R 4.4.3** (Feb 2025): Bug fixes.

### R 4.5.0 (April 2025)

Major new checks introduced:
- **Non-API entry point escalation**: Many NOTEs on non-API entry points upgraded to **WARNINGs**, signaling imminent removal of declarations. New entries added: `COMPLEX0`, `DDVAL`, `ENSURE_NAMEDMAX`, `ENVFLAGS`, `FRAME`, `HASHTAB`, `INTERNAL`, `IS_ASCII`, `IS_UTF8`, `LEVELS`, `NAMED`, `PRSEEN`, `RDEBUG`, `REAL0`, `Rf_findVarInFrame3`, `SYMVALUE`, `VECTOR_PTR`, `XLENGTH_EX`, `XTRUELENGTH`, and more.
- **Bad symbols in shared objects**: Reports bad symbols linked from local static libraries (PR#18789).

Source: [R 4.5.0 Release Announcement](https://stat.ethz.ch/pipermail/r-announce/2025/000710.html)

---

## 3. CRAN Infrastructure Changes

### Check Flavors (as of early 2026)

CRAN runs 13 primary check flavors:

| Category | Flavors |
|----------|---------|
| Linux x86_64 | r-devel-linux-x86_64-debian-clang, r-devel-linux-x86_64-debian-gcc, r-devel-linux-x86_64-fedora-clang, r-devel-linux-x86_64-fedora-gcc, r-patched-linux-x86_64, r-release-linux-x86_64 |
| Windows x86_64 | r-devel-windows-x86_64, r-release-windows-x86_64, r-oldrel-windows-x86_64 |
| macOS | r-release-macos-arm64, r-release-macos-x86_64, r-oldrel-macos-arm64, r-oldrel-macos-x86_64 |

Source: [CRAN Package Check Flavors](https://cran.r-project.org/web/checks/check_flavors.html)

### Additional Issue Kinds (Beyond Standard R CMD check)

CRAN runs extensive additional checks beyond the standard flavors:

**Compiler & Compilation**: C23 mode, gcc-only issues, gcc15 pre-release, Intel oneAPI compilers, LTO type mismatches

**Memory & Safety**: clang-ASAN, clang-UBSAN, gcc-ASAN, gcc-UBSAN, valgrind, zero-length access segfaults

**Linear Algebra**: ATLAS, BLAS, MKL, OpenBLAS alternative implementations

**Code Analysis**: rchk (static analysis of C/C++), rcnst (corruption of constants), noRemap (-DR_NO_REMAP)

**Environment Testing**: M1mac (arm64), musl (Alpine Linux), noLD (no long double), noOMP (no OpenMP), noSuggests (without suggested packages), rlibro (read-only library), Strict (STRICT_R_HEADERS), donttest (including \donttest examples)

Source: [CRAN Package Check Issue Kinds](https://cran.r-project.org/web/checks/check_issue_kinds.html)

### Submission Portal

The CRAN submission portal (https://cran.r-project.org/submit.html) and checklist (https://cran.r-project.org/web/packages/submission_checklist.html) remained structurally stable through this period. The submission checklist emphasizes:
- Running `R CMD check --as-cran` with current R-devel before submission
- Testing on win-builder and R-hub
- Proper DESCRIPTION formatting with ORCID and ROR identifiers
- Author-year citation style with DOI/ISBN/URL in Description field

### CRAN Cookbook (2024)

The [CRAN Cookbook](https://contributor.r-project.org/cran-cookbook/) launched in 2024 as an R Consortium-funded Special Project Grant. Curated by Jasmine Daly and Beni Altmann with a steering committee (Heather Turner, Bettina Grun, Gwynn Gebeyehu), it provides structured guidance for common CRAN submission issues organized by category (general, DESCRIPTION, documentation, code).

---

## 4. Major Community Events

### "Is CRAN Holding R Back?" Debate (February 2025)

**Trigger**: The `acs` package was archived for a NOTE about `/bin/bash is not portable` in configure/cleanup scripts -- a cosmetic issue that caused no user-facing problems. This cascaded to archive `choroplethr`, `noaastormevents`, and `synthACS` (43,037 combined downloads in 2024 from RStudio mirror).

**Key Arguments** (Ari Lamstein, Feb 12 2025):
- Archiving for a non-impactful NOTE seems disproportionate
- Short fix windows create undue pressure on volunteer maintainers
- CRAN's size limits forced `choroplethr` to be split across packages and vignettes stripped
- Release rate limits ("no more than every 1-2 months") slow development
- Cascade archival affects innocent downstream packages

**Community Response**: Widespread discussion on R-bloggers, R Weekly, social media. The debate crystallized long-simmering frustration about CRAN's volunteer-driven but sometimes opaque decision-making.

**Resolution**: `choroplethr` v4.0.0 returned to CRAN in April 2025 under new maintainer (Zhaochen He).

Source: [Ari Lamstein blog](https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/), [R-bloggers coverage](https://www.r-bloggers.com/2025/02/is-cran-holding-r-back/)

### CRANhaven Launch and Growth

[CRANhaven](https://www.cranhaven.org/) provides a safety net repository for recently archived CRAN packages (up to 5 weeks). Key features:
- Automatically detects archival via CRANberries
- Removes packages when unarchived on CRAN
- R-universe powered
- Proof-of-concept status, updated hourly
- Dashboard tracking ~130 packages archived/removed in any 35-day window

CRANhaven also published important archival statistics (see Section 5).

Source: [CRANhaven](https://www.cranhaven.org/), [CRANhaven GitHub](https://github.com/cranhaven/cranhaven.r-universe.dev)

### R-multiverse Launch (2024-2025)

[R-multiverse](https://r-multiverse.org/) launched as a community-curated dual repository:
- **Community repository**: Continuous builds of contributed packages
- **Production repository**: Quarterly snapshots with tested dependencies (latest: 59 packages, deployed 2025-12-15, R 4.5 compatible)
- Powered by R-universe infrastructure
- Targets packages outside CRAN/Bioconductor scope (e.g., compiled code needing non-standard toolchains)
- Does NOT replace CRAN; works alongside it
- Named an R Consortium Top-Level Project (February 2025)

Source: [R-multiverse overview](https://r-multiverse.org/overview.html), [R-multiverse production](https://r-multiverse.org/production.html)

### R-universe Growth

R-universe (by rOpenSci) continued expanding as a universal R package distribution platform, named an R Consortium Top-Level Project in February 2025. It serves as infrastructure for both CRANhaven and R-multiverse.

Source: [rOpenSci R-universe](https://ropensci.org/r-universe/)

### data.table Non-API Crisis (2024-2025)

The `data.table` package -- one of R's most critical packages -- faced potential archival risk over non-API entry point usage. data.table relies on internal R structures (`TRUELENGTH`, `SETLENGTH`, `SET_TRUELENGTH`) for its signature by-reference modification operations. These are being progressively restricted by R-core:
- `tools:::nonAPI` grew from 259 entries (R 3.3.3) to 272+ entries (R 4.4.2)
- NOTEs upgraded to WARNINGs in R 4.5.0
- ALTREP objects (R 3.5+) are incompatible with TRUELENGTH
- Sparked extensive R-devel discussion (234 mentions of "API" per month)

This case illustrated the tension between CRAN's push for API compliance and the reality that some widely-used packages depend on internal structures for performance.

Source: [data.table non-API entry points blog](https://rdatatable-community.github.io/The-Raft/posts/2025-01-13-non-api-use/), [R-bloggers coverage](https://www.r-bloggers.com/2025/01/use-of-non-api-entry-points-in-data-table/)

### EU Cyber Resilience Act (2024-2027)

The EU Cyber Resilience Act (entered into force December 10, 2024) will require compliance for all software repositories distributing packages in the EU by October 2027. The R Consortium is seeking funding to help CRAN and community repositories plan for compliance. This represents a potentially transformative regulatory pressure on CRAN's operations.

Source: [R Consortium 2025 plans](https://r-consortium.org/posts/moving-forward-to-meet-new-challenges-in-2025/)

### R Consortium Initiatives

- **Repositories Working Group** (established 2022): Continues work on repository governance and quality standards
- **CRAN Cookbook** (2024 grant): Published comprehensive submission guidance
- **R Submissions Working Group**: Pilot programs with FDA for regulatory R package submissions; FDA eCTD Technical Conformance Guide (August 2025 revision) informed by this collaboration
- **ISC Grants**: 13 new infrastructure projects funded in 2024

Source: [R Consortium projects](https://r-consortium.org/all-projects/2025-group-1.html)

### Using Rust in CRAN Packages (2023)

CRAN published an official [guidance document for Rust packages](https://cran.r-project.org/web/packages/using_rust.html) in mid-2023. Key requirements:
- Cargo crates must be vendored (`cargo vendor`) for offline installation
- GitHub is not considered sufficiently reliable for build-time downloads
- Parallel cargo builds limited to N=1 or 2
- Authorship/copyright of Rust dependencies must be declared in DESCRIPTION

This was discussed on r-package-devel in July 2023 and represents CRAN's first formal policy for a modern systems language beyond C/C++/Fortran.

Source: [CRAN Using Rust page](https://cran.r-project.org/web/packages/using_rust.html), [r-package-devel feedback](https://stat.ethz.ch/pipermail/r-package-devel/2023q3/009331.html)

---

## 5. Archival Statistics

### Overall CRAN Scale

- **Total packages ever on CRAN**: ~23,058
- **Currently available** (early 2026): ~23,039
- **Total ever archived**: ~9,089 (39% of all packages ever on CRAN)

### Archival Reasons (by frequency)

| Reason | Count |
|--------|-------|
| Package problems not fixed in time | 5,808 |
| Mixed/unclear circumstances | 1,458 |
| Dependency archived (cascade) | 1,270 |
| Policy violations | 644 |
| Maintainer email failures | 228 |

### Return Rates

- **38% of archived packages eventually return** to CRAN
- **48.7% attempt resubmission** after archival
- **95% of resubmitted packages are eventually accepted**
- Median time to return: **~33 days** (Q1: 9 days, Q3: 125 days, max: 3,292 days)

### Repeat Archival

| Times Archived | Packages |
|---------------|----------|
| 1 time | 3,361 |
| 2 times | 662 |
| 3+ times | 251 |

Repeat-archived packages return slightly faster (median 28 days vs 33 days).

### First-Time Submission Statistics (Revilla 2024)

Based on ~174 weeks of submission data (Sep 2020 - Jan 2024):
- **65% of first-time submissions accepted without rejection**
- 21.9% need 1 resubmission
- 8.2% need 2 resubmissions
- 4.9% need 3+ resubmissions
- **6.8% of accepted packages later fully archived** (all versions removed)

### Temporal Patterns

- Most packages archived within 2 weeks of first acceptance
- Archival activity clusters around R release dates (2022-2023 trend)
- No strong seasonal pattern otherwise
- CRANhaven dashboard tracks ~130 packages archived/removed per 35-day window

Source: [CRANhaven archival statistics](https://www.cranhaven.org/cran-archiving-stats.html), [Revilla submission analysis](https://llrs.dev/post/2024/01/10/submission-cran-first-try/)

---

## 6. Enforcement Trend Analysis

### Categories That Got Stricter (2023-2025)

1. **Compiled Code Safety** (MOST SIGNIFICANT)
   - 2023: sprintf/vsprintf deprecated, C++ standard enforcement, strict prototypes
   - 2024: non-API entry points expanded, Fortran modernization warnings
   - 2025: non-API NOTEs escalated to WARNINGs, more entry points restricted
   - Trajectory: Accelerating. R-core is systematically closing off internal access.

2. **Documentation Quality**
   - 2024: "Lost braces" check (3,000+ packages affected), Rd alias requirements
   - The lost braces change was the single largest mass-impact check addition.

3. **Package Size and Vendoring**
   - 2023: Explicit 10MB tarball guidance, vendor.tar.xz preference codified
   - 2023: Rust vendoring requirements formalized
   - Direction: Increasingly strict about not downloading at build/install time.

4. **Secure Communications**
   - 2023: ftps removed from acceptable protocols (https only)
   - Ongoing: SSL/TLS certificate verification must not be circumvented.

5. **Fortran Modernization**
   - 2024: Non-portable KIND warnings, deleted Fortran features flagged
   - 2024: Fortran random number generator usage reported

### Categories That Remained Stable

- **DESCRIPTION metadata requirements**: Largely unchanged since pre-2023.
- **License requirements**: No significant changes.
- **Testing time limits**: Still "as little CPU time as possible" and 2-core limit.
- **Package naming**: No policy changes.

### Categories with Community Push-Back

- **NOTE-based archival**: Community strongly objects to archiving for NOTEs (vs ERRORs/WARNINGs). The acs/choroplethr case was emblematic.
- **Release rate limits**: "No more than every 1-2 months" frustrates rapid development.
- **Short fix windows**: Tight deadlines before archival disadvantage volunteer maintainers.
- **Cascade archival**: Downstream packages archived for upstream dependency issues they don't control.

### Year-by-Year Focus

| Year | Primary Enforcement Focus |
|------|--------------------------|
| 2023 | C/C++ modernization (sprintf, C++ std, prototypes); Rust policy; vendoring |
| 2024 | Documentation quality (lost braces); non-API entry points; Fortran modernization |
| 2025 | Non-API escalation (NOTE->WARNING); community governance debate; alternative repos |

---

## 7. Implications for pedanticran

### High-Priority Rules to Cover

1. **Non-API entry points**: The highest-impact evolving enforcement area. pedanticran should detect use of functions in `tools:::nonAPI` and flag them with severity based on whether R CMD check currently NOTEs or WARNINGs them.

2. **sprintf/vsprintf usage**: Simple grep-based detection, but still catches packages in 2025-2026.

3. **Lost braces in Rd**: Can detect with regex patterns for common cases (unescaped `{`/`}`, `\item{}{}`-style in `\itemize`).

4. **C++ standard specification**: Flag `CXX_STD=CXX11` in src/Makevars as unnecessary.

5. **Vendor.tar.xz guidance**: Check for downloading at install time vs vendoring.

6. **Fortran KIND portability**: Flag `INTEGER(KIND=4)`, `REAL(KIND=8)` etc.

7. **browser() statements**: Detect leftover debug calls.

### Medium-Priority Rules

8. **Package size**: Check tarball size against 10MB guideline.
9. **Secure downloads**: Verify only https used (not http/ftp/ftps).
10. **NEWS.md format**: Validate markdown news format.
11. **Rd file completeness**: Check for missing \alias, \description.

### Trend-Based Recommendations

- **Non-API compliance will be the dominant CRAN issue for 2026-2027.** As WARNINGs become ERRORs, packages using internal R structures face forced migration. pedanticran should prioritize this.
- **Documentation checks will continue expanding.** Each R release adds more Rd validation.
- **The alternative repo ecosystem is growing but CRAN remains dominant.** pedanticran serves a real need -- CRAN submission remains the goal for most R package developers.
- **EU CRA compliance may introduce entirely new requirements by 2027.** Worth monitoring but too speculative for current rules.

---

## Sources

- [CRAN Repository Policy](https://cran.r-project.org/web/packages/policies.html)
- [eddelbuettel/crp - Policy revision tracking](https://github.com/eddelbuettel/crp/commits/master)
- [R 4.3.0 Release](https://stat.ethz.ch/pipermail/r-announce/2023/000691.html)
- [R 4.4.0 Release](https://stat.ethz.ch/pipermail/r-announce/2024/000701.html)
- [R 4.5.0 Release](https://stat.ethz.ch/pipermail/r-announce/2025/000710.html)
- [Tidyverse: New CRAN requirements for C/C++](https://tidyverse.org/blog/2023/03/cran-checks-compiled-code/)
- [CRAN Check Flavors](https://cran.r-project.org/web/checks/check_flavors.html)
- [CRAN Check Issue Kinds](https://cran.r-project.org/web/checks/check_issue_kinds.html)
- [Ari Lamstein: Is CRAN Holding R Back?](https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/)
- [CRANhaven](https://www.cranhaven.org/)
- [CRANhaven Archival Statistics](https://www.cranhaven.org/cran-archiving-stats.html)
- [R-multiverse](https://r-multiverse.org/)
- [Revilla: Submissions accepted on first try](https://llrs.dev/post/2024/01/10/submission-cran-first-try/)
- [data.table non-API entry points](https://rdatatable-community.github.io/The-Raft/posts/2025-01-13-non-api-use/)
- [CRAN Cookbook](https://contributor.r-project.org/cran-cookbook/)
- [R Consortium 2025 Plans](https://r-consortium.org/posts/moving-forward-to-meet-new-challenges-in-2025/)
- [CRAN: Using Rust](https://cran.r-project.org/web/packages/using_rust.html)
- [CRAN Submission Checklist](https://cran.r-project.org/web/packages/submission_checklist.html)
