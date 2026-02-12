# Pedanticran vs devtools / R CMD check

How pedanticran complements the existing R package checking ecosystem.

## The Landscape

| Layer | Tool | What it does |
|-------|------|-------------|
| Structural / syntactic | R CMD check | ~50 automated checks: package structure, NAMESPACE, R syntax, Rd syntax, compiled code, tests, vignettes |
| Convenience wrapper | devtools::check() | Same checks as R CMD check, easier to run. Adds zero additional rules. |
| Manual checklists | devtools::release() / usethis | Prompts the developer with questions but no automated enforcement |
| Partial style | goodpractice / lintr | ~230 checks but only 10-15% overlap with CRAN policy gaps (T/F, some imports) |
| Platform testing | rhub | Tests on different platforms, no policy checks |
| Post-publication | foghorn | Monitors CRAN check results after publication |
| **Human reviewer gap** | **pedanticran** | **61 unique rules no other tool catches** |

## Key Finding: devtools::check() IS R CMD check

devtools::check() is a convenience wrapper around `rcmdcheck::rcmdcheck()`, which itself calls `R CMD check`. It adds:

- Automatic `devtools::document()` before checking
- Environment variable setup (`_R_CHECK_CRAN_INCOMING_` etc.)
- Cleaner output formatting

It adds **zero additional policy checks**. The `devtools::release()` workflow and `usethis::use_release_issue()` provide manual checklists, but these are prompts for the developer to verify -- not automated enforcement.

## Coverage Classification

All 141 pedanticran rules classified by overlap:

| Classification | Count | % |
|---------------|------:|--:|
| **(C) Unique to pedanticran** | 61 | 43% |
| **(A) Overlaps with R CMD check** | 68 | 48% |
| **(B) Overlaps with devtools/goodpractice (not R CMD check)** | 12 | 9% |

### Rules Unique to Pedanticran (Category C)

These 61 rules catch things **no automated tool in the R ecosystem checks**:

#### DESCRIPTION Prose Quality (8 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Single quotes around software names | DESC-02 | Software names without quotes |
| No "for R" in title | DESC-03 | Redundant "for R" / "in R" |
| Description opening text | DESC-04 | "This package..." or "Functions for..." |
| Description 2+ sentences | DESC-05 | Single-sentence description |
| Unexplained acronyms | DESC-07 | Acronyms without expansion |
| Copyright holder role | DESC-09 | Missing cph role in Authors@R |
| Unnecessary +file LICENSE | DESC-10 | Redundant LICENSE file declaration |
| Stale Date field | DESC-13 | Date field months old at submission |

These are the **#1 category of first-time rejections**. No tool checks DESCRIPTION prose.

#### Code Policy (12 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| print/cat vs message | CODE-02 | Using print()/cat() for user messages |
| set.seed in functions | CODE-03 | Calling set.seed() without user control |
| Missing on.exit | CODE-04 | Changing options/par/wd without on.exit() |
| options(warn=-1) | CODE-05 | Suppressing warnings globally |
| Write to tempdir only | CODE-06 | Writing outside tempdir() |
| Modifying .GlobalEnv | CODE-09 | assign() to .GlobalEnv, rm(list=ls()) |
| Max 2 cores | CODE-10 | Using more than 2 CPU cores |
| No install.packages | CODE-13 | Calling install.packages() in functions |
| No SSL bypass | CODE-14 | Disabling SSL/TLS verification |
| UseLTO CPU time NOTE | CODE-17 | UseLTO triggers parallel install time NOTE |
| Don't remove failing tests | CODE-18 | Removing tests instead of fixing them |
| Staged installation compatibility | CODE-19 | Caching paths at install time breaks staged install |

`print()/cat()` vs `message()` is a **top-5 CRAN rejection reason**. Our context-aware checker reduced false positives by 89% on dplyr.

#### Documentation Policy (3 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| \dontrun misuse | DOC-02 | Using \dontrun{} for examples that could use \donttest{} |
| Roxygen2 workflow | DOC-04 | Editing .Rd files directly instead of roxygen2 comments |
| Function names in docs | DOC-06 | Missing () after function names in documentation |

`\dontrun{}` misuse is a **top-5 rejection reason**. R CMD check allows it without complaint.

#### Compiled Code Policy (2 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Rust vendoring | COMP-09 | Rust crates not vendored per CRAN policy |
| Memory sanitizer compliance | COMP-11 | ASAN/UBSAN/Valgrind errors in compiled code |

CRAN runs ASAN/UBSAN/Valgrind checks beyond what R CMD check does. Packages can pass all standard checks and still fail these.

#### Encoding (3 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Non-portable \x escapes | ENC-03 | \xNN escapes non-portable across locales |
| UTF-8 BOM in source files | ENC-04 | Byte Order Mark causes parsing issues |
| Missing VignetteEncoding | ENC-05 | Vignettes without encoding declaration |

Encoding issues are subtle and locale-dependent. R CMD check misses non-portable `\x` escapes and BOM bytes entirely.

#### Vignettes (3 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| html_document vs html_vignette | VIG-05 | html_document embeds ~600KB Bootstrap payload |
| Vignette CPU time | VIG-07 | CPU time exceeding elapsed time from threading |
| Custom vignette engine bootstrap | VIG-08 | Self-referencing VignetteBuilder chicken-and-egg |

These are practical build issues that R CMD check does not specifically diagnose.

#### NAMESPACE (2 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Broad exportPattern | NS-04 | exportPattern("^[[:alpha:]]") exports internals |
| Re-export documentation | NS-07 | Re-exported functions missing @return docs |

R CMD check notes broad export patterns but does not flag the specific anti-patterns CRAN reviewers reject. Re-export documentation gaps are a common first-submission rejection.

#### Data (3 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Missing LazyData for .rda files | DATA-03 | data/ has .rda but no LazyData: true |
| Data size exceeds 5MB | DATA-05 | Data directory exceeds CRAN limit |
| Internal sysdata.rda size | DATA-08 | Oversized R/sysdata.rda |

R CMD check warns about compression but not about missing LazyData or per-directory size limits.

#### System Requirements (6 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Undeclared system library | SYS-01 | Missing SystemRequirements for linked libraries |
| Undeclared external program | SYS-02 | system()/system2() calls without declaration |
| C++20 default transition | SYS-03 | Packages needing review for C++20 compatibility |
| Configure script missing | SYS-04 | No configure script for system library detection |
| Java source requirement | SYS-05 | .jar/.class files without java/ source directory |
| USE_C17 opt-out | SYS-07 | C23 keyword conflicts needing temporary escape hatch |

System requirement issues are installation failures, not R CMD check diagnostics. The checker cross-references `#include` headers and Makevars `-l` flags against DESCRIPTION.

#### Maintainer Email (6 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Mailing list email | EMAIL-01 | Maintainer email is a list/group address |
| Missing email in Authors@R | EMAIL-02 | cre person without email argument |
| Disposable email domain | EMAIL-03 | Temporary email provider (mailinator, etc.) |
| Placeholder email | EMAIL-04 | Template email (user@example.com) |
| Institutional email warning | EMAIL-05 | .edu address at risk of expiring |
| Noreply/automated address | EMAIL-06 | noreply@ or bot@ addresses |

Maintainer email quality is the **#1 cause of package archival** (unreachable maintainer). No tool validates email beyond basic RFC 2822 syntax.

#### inst/ Directory (2 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Missing copyright attribution | INST-05 | Bundled third-party code without copyright |
| Large files in inst/extdata | INST-06 | Per-subdirectory size exceeding 1MB |

Copyright attribution for bundled JS/CSS libraries is a FOSS compliance issue that no automated tool checks.

#### Licensing (2 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| License change protocol | LIC-02 | License changes not highlighted in submission |
| Dual licensing | LIC-03 | Per-file license inconsistency |

#### Network (2 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Graceful offline failure | NET-01 | Package crashes without internet |
| Rate limiting | NET-03 | No rate limiting on API calls |

#### Process Knowledge (6 rules)

| Rule | ID | What developers don't know |
|------|-----|---------------------------|
| Run check on exact tarball | SUB-01 | Must check the exact tarball you upload |
| First submission NOTE | SUB-05 | The "New submission" NOTE is expected and harmless |
| Submission frequency | SUB-06 | CRAN limits resubmission to ~1/week for repeat failures |
| CRAN vacation periods | SUB-07 | Reduced capacity Dec-Jan and during R releases |
| Names are permanent | NAME-02 | You cannot rename a package after publication |
| Dependency health | DEP-03 | Cascading archival risk from unhealthy dependencies |

No tool provides this tribal knowledge.

#### Cross-Platform (1 rule)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Multi-platform requirement | PLAT-01 | Package works on only one OS |

### Rules That Overlap with R CMD check (Category A)

These 68 rules are well-handled by R CMD check. Pedanticran includes them in the knowledge base for completeness and for the `/cran-respond` skill (mapping rejection emails to fixes), but the automated checker doesn't need to duplicate them:

- **DESCRIPTION**: Title case (DESC-01), DOI format (DESC-06), Authors@R (DESC-08), single maintainer (DESC-11), version increase (DESC-12), version component size (DESC-14), smart quotes (DESC-15)
- **Code behavior**: Temp file detritus (CODE-07), q()/quit() (CODE-11), ::: to base (CODE-12), browser() (CODE-15), sprintf (CODE-16), stringsAsFactors (CODE-20), class(matrix) (CODE-21), if-length>1 (CODE-22)
- **Compiled code**: C23 keywords (COMP-01), R_NO_REMAP (COMP-02), non-API calls (COMP-03), implicit declarations (COMP-04), configure portability (COMP-05), C++11/14 deprecated (COMP-06), strict prototypes (COMP-07), Fortran KIND (COMP-08), routine registration (COMP-10), UCRT compatibility (COMP-12)
- **Documentation**: Missing @return (DOC-01), example timing (DOC-03), lost braces (DOC-08), HTML5 validation (DOC-09), \donttest execution (DOC-10), duplicate vignette titles (DOC-11)
- **Licensing**: License in CRAN DB (LIC-01)
- **Size/Performance**: Tarball size (SIZE-01), check time (SIZE-02)
- **Cross-platform**: No binaries (PLAT-02)
- **Dependencies**: Strong deps on CRAN (DEP-01), conditional Suggests (DEP-02)
- **Network**: HTTPS URLs (NET-02)
- **Miscellaneous**: URL validity (MISC-02), spelling (MISC-03), Makefile POSIX (MISC-05), NEWS format (MISC-06), URL redirects (MISC-07)
- **Encoding**: Missing Encoding field (ENC-01), non-ASCII in R source (ENC-02), unmarked UTF-8 in data (ENC-06), non-ASCII in NAMESPACE (ENC-07), non-ASCII in Rd (ENC-08)
- **Vignettes**: VignetteBuilder (VIG-01), metadata (VIG-02), stale inst/doc (VIG-03), build deps (VIG-04), data file location (VIG-06)
- **NAMESPACE**: Import conflicts (NS-01), S3 method registration (NS-03), no visible binding (NS-06), library/require in code (NS-08)
- **Data**: Undocumented datasets (DATA-01), LazyData without data/ (DATA-02), suboptimal compression (DATA-04), non-ASCII in data (DATA-06), serialization version (DATA-07), invalid formats (DATA-09)
- **System requirements**: Contradictory C++ standard (SYS-06)
- **inst/**: Hidden files (INST-01), deprecated CITATION (INST-02), inst/doc conflicts (INST-03), reserved names (INST-04)

### Rules That Overlap with devtools/goodpractice (Category B)

These 12 rules are partially covered by ecosystem tools but not R CMD check:

| Rule | ID | Covered by |
|------|-----|-----------|
| T/F literals | CODE-01 | goodpractice, lintr |
| installed.packages() | CODE-08 | goodpractice |
| Missing examples | DOC-05 | goodpractice |
| Canonical CRAN/Bioc URLs | DOC-07 | urlchecker |
| Case-insensitive name | NAME-01 | available package |
| Multi-platform testing | SUB-02 | rhub, devtools::check_win_devel() |
| Reverse dependencies | SUB-03 | revdepcheck |
| cran-comments.md | SUB-04 | usethis |
| NEWS.md | MISC-01 | usethis |
| .Rbuildignore | MISC-04 | usethis |
| Prefer importFrom | NS-02 | goodpractice |
| Depends vs Imports | NS-05 | goodpractice |

## Pedanticran's Unique Position

```
R CMD check         ->  "Does it build and pass basic checks?"
devtools::release() ->  "Did you remember to do these things?" (checklist)
goodpractice        ->  "Here are some style suggestions" (partial)
pedanticran         ->  "Will a CRAN reviewer accept this?" (the actual gate)
```

## Closest Competitor: goodpractice

The `goodpractice` package is the nearest tool. Comparison:

| Capability | goodpractice | pedanticran |
|-----------|:---:|:---:|
| T/F detection | yes | yes |
| DESCRIPTION prose rules | no | **8 rules** |
| print/cat vs message | no | **yes (context-aware)** |
| \dontrun misuse | no | **yes** |
| on.exit pairing | partial (setwd only) | **yes (options, par, wd)** |
| Compiled code policy | no | **12 rules** |
| Encoding rules | no | **8 rules** |
| Vignette rules | no | **8 rules** |
| NAMESPACE rules | no | **8 rules** |
| Data rules | no | **9 rules** |
| System requirements | no | **7 rules** |
| Maintainer email | no | **6 rules** |
| inst/ directory | no | **6 rules** |
| Rejection email parsing | no | **yes** |
| Auto-remediation | no | **yes (3 tiers)** |
| Process knowledge | no | **6 rules** |
| Requires R | yes | **no** |
| GitHub Action | no | **yes** |

## Previously Identified Gaps -- Now Covered

The original report (February 2026, 79-rule version) identified 7 areas where CRAN human reviewers reject but pedanticran did not yet check. All 7 are now covered by the expanded 141-rule knowledge base:

1. **Encoding issues** -- Covered by ENC-01 through ENC-08 (8 rules)
2. **Vignette checks** -- Covered by VIG-01 through VIG-08 (8 rules)
3. **NAMESPACE issues** -- Covered by NS-01 through NS-08 (8 rules)
4. **Data documentation** -- Covered by DATA-01 through DATA-09 (9 rules)
5. **SystemRequirements** -- Covered by SYS-01 through SYS-07 (7 rules)
6. **Maintainer email** -- Covered by EMAIL-01 through EMAIL-06 (6 rules)
7. **inst/ directory** -- Covered by INST-01 through INST-06 (6 rules)

These 52 new rules were sourced from the same R-package-devel mailing list archives (2023-2025) and CRAN Repository Policy revisions that informed the original knowledge base.

## Methodology

This comparison was produced in February 2026 (updated February 11, 2026) by:
- Web research into R CMD check source code, devtools internals, goodpractice checks, and CRAN policy
- Rule-by-rule classification of all 141 pedanticran rules against R CMD check and devtools capabilities
- Validation against dplyr and glosario test packages (see `research/checker-validation.md`)
- Original classification covered 79 rules; expanded to 141 rules across 19 categories (up from 12)
