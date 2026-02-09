# Pedanticran vs devtools / R CMD check

How pedanticran complements the existing R package checking ecosystem.

## The Landscape

| Layer | Tool | What it does |
|-------|------|-------------|
| Structural / syntactic | R CMD check | ~50 automated checks: package structure, NAMESPACE, R syntax, Rd syntax, compiled code, tests, vignettes |
| Convenience wrapper | devtools::check() | Same checks as R CMD check, easier to run. Adds zero additional rules. |
| Manual checklists | devtools::release() / usethis | Prompts the developer with questions but no automated enforcement |
| Partial style | goodpractice / lintr | ~230 checks but only 10–15% overlap with CRAN policy gaps (T/F, some imports) |
| Platform testing | rhub | Tests on different platforms, no policy checks |
| Post-publication | foghorn | Monitors CRAN check results after publication |
| **Human reviewer gap** | **pedanticran** | **34 unique rules no other tool catches** |

## Key Finding: devtools::check() IS R CMD check

devtools::check() is a convenience wrapper around `rcmdcheck::rcmdcheck()`, which itself calls `R CMD check`. It adds:

- Automatic `devtools::document()` before checking
- Environment variable setup (`_R_CHECK_CRAN_INCOMING_` etc.)
- Cleaner output formatting

It adds **zero additional policy checks**. The `devtools::release()` workflow and `usethis::use_release_issue()` provide manual checklists, but these are prompts for the developer to verify — not automated enforcement.

## Coverage Classification

All 79 pedanticran rules classified by overlap:

| Classification | Count | % |
|---------------|------:|--:|
| **(C) Unique to pedanticran** | 34 | 43% |
| **(A) Overlaps with R CMD check** | 31 | 39% |
| **(B) Overlaps with devtools/goodpractice (not R CMD check)** | 10 | 13% |
| Partial overlap | 4 | 5% |

### Rules Unique to Pedanticran (Category C)

These 34 rules catch things **no automated tool in the R ecosystem checks**:

#### DESCRIPTION Prose Quality (8 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Title Case | DESC-01 | Title not in title case |
| Single quotes around software names | DESC-02 | Software names without quotes |
| No "for R" in title | DESC-03 | Redundant "for R" / "in R" |
| Description opening text | DESC-04 | "This package..." or "Functions for..." |
| Description 2+ sentences | DESC-05 | Single-sentence description |
| Unexplained acronyms | DESC-07 | Acronyms without expansion |
| Copyright holder role | DESC-09 | Missing cph role in Authors@R |
| Unnecessary +file LICENSE | DESC-10 | Redundant LICENSE file declaration |
| Stale Date field | DESC-13 | Date field months old at submission |

These are the **#1 category of first-time rejections**. No tool checks DESCRIPTION prose.

#### Code Policy (9 rules)

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
| Don't remove failing tests | CODE-18 | Removing tests instead of fixing them |

`print()/cat()` vs `message()` is a **top-5 CRAN rejection reason**. Our context-aware checker reduced false positives by 89% on dplyr.

#### Documentation Policy (3 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| \dontrun misuse | DOC-02 | Using \dontrun{} for examples that could use \donttest{} |
| Roxygen2 workflow | DOC-04 | Editing .Rd files directly instead of roxygen2 comments |
| Function names in docs | DOC-06 | Missing () after function names in documentation |

`\dontrun{}` misuse is a **top-5 rejection reason**. R CMD check allows it without complaint.

#### Process Knowledge (6 rules)

| Rule | ID | What developers don't know |
|------|-----|---------------------------|
| First submission NOTE | SUB-05 | The "New submission" NOTE is expected and harmless |
| Submission frequency | SUB-06 | CRAN limits resubmission to ~1/week for repeat failures |
| CRAN vacation periods | SUB-07 | Reduced capacity Dec–Jan and during R releases |
| License change protocol | LIC-02 | License changes must be highlighted in cran-comments.md |
| Names are permanent | NAME-02 | You cannot rename a package after publication |
| Dependency health | DEP-03 | Cascading archival risk from unhealthy dependencies |

No tool provides this tribal knowledge.

#### Other Unique Rules (3 rules)

| Rule | ID | What CRAN rejects |
|------|-----|-------------------|
| Graceful offline failure | NET-01 | Package crashes without internet |
| Rate limiting | NET-03 | No rate limiting on API calls |
| Multi-platform requirement | PLAT-01 | Package works on only one OS |
| Rust vendoring | COMP-09 | Rust crates not vendored per CRAN policy |
| Dual licensing | LIC-03 | Per-file license inconsistency |

### Rules That Overlap with R CMD check (Category A)

These 31 rules are well-handled by R CMD check. Pedanticran includes them in the knowledge base for completeness and for the `/cran-respond` skill (mapping rejection emails to fixes), but the automated checker doesn't need to duplicate them:

- NAMESPACE validation, R syntax checking, cross-reference validation
- Rd syntax, HTML5 validation, lost braces detection
- Compiled code compilation, sprintf deprecation, C23 keywords
- URL checking, spelling, package size, check timing
- License validation, dependency resolution, binary file detection

### Rules That Overlap with devtools/goodpractice (Category B)

These 10 rules are partially covered by ecosystem tools but not R CMD check:

| Rule | ID | Covered by |
|------|-----|-----------|
| T/F literals | CODE-01 | goodpractice, lintr |
| installed.packages() | CODE-08 | goodpractice |
| Missing examples | DOC-05 | goodpractice |
| DOI formatting | DESC-06 | Partial R CMD check |
| NEWS.md | MISC-01 | usethis |
| .Rbuildignore | MISC-04 | usethis |
| Case-insensitive name | NAME-01 | available package |
| Multi-platform testing | SUB-02 | rhub, devtools::check_win_devel() |
| Reverse dependencies | SUB-03 | revdepcheck |
| cran-comments.md | SUB-04 | usethis |

## Pedanticran's Unique Position

```
R CMD check         →  "Does it build and pass basic checks?"
devtools::release() →  "Did you remember to do these things?" (checklist)
goodpractice        →  "Here are some style suggestions" (partial)
pedanticran         →  "Will a CRAN reviewer accept this?" (the actual gate)
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
| Compiled code policy | no | **9 rules** |
| Rejection email parsing | no | **yes** |
| Auto-remediation | no | **yes (3 tiers)** |
| Process knowledge | no | **6 rules** |
| Requires R | yes | **no** |
| GitHub Action | no | **yes** |

## Potential Gaps

Areas where CRAN human reviewers reject but pedanticran does not yet check:

1. **Encoding issues** — Beyond smart quotes: data file encodings, vignette encoding, system-locale
2. **Vignette checks** — Build failures from missing LaTeX/Pandoc, stale pre-built vignettes
3. **NAMESPACE issues** — Missing imports, exporting internals, S3 method registration
4. **Data documentation** — Undocumented datasets, LazyData misconfiguration
5. **SystemRequirements** — Undeclared system libraries, programs, headers
6. **Maintainer email** — Mailing lists, noreply addresses, institutional addresses
7. **inst/ directory** — Large files, executables, copyright issues, inappropriate content

## Methodology

This comparison was produced in February 2026 by:
- Web research into R CMD check source code, devtools internals, goodpractice checks, and CRAN policy
- Rule-by-rule classification of all 79 pedanticran rules against R CMD check and devtools capabilities
- Validation against dplyr and glosario test packages (see `research/checker-validation.md`)
