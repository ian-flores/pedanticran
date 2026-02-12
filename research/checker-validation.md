# Pedantic CRAN Checker — Validation Report

Validation of `action/check.py` against two real R packages: one large CRAN-published package and one small non-CRAN package.

**Date**: 2026-02-11
**Checker version**: 141 rules across 19 categories, 279 tests

---

## Packages Tested

| | **dplyr** | **glosario** |
|---|---|---|
| **Source** | [tidyverse/dplyr](https://github.com/tidyverse/dplyr) | [carpentries/glosario-r](https://github.com/carpentries/glosario-r) |
| **Version** | 1.2.0.9000 (dev branch) | 0.2 |
| **CRAN status** | Published (since 2014) | Not on CRAN |
| **R source files** | 106 | 14 |
| **Compiled code** | 14 C/C++ files | None |
| **Maintainer** | Hadley Wickham (Posit) | Greg Wilson (Carpentries) |
| **License** | MIT | MIT |

Note: `carpentries/glosario` (the main repo) is a Jekyll website, not an R package. The R package is at `carpentries/glosario-r`.

---

## Results Summary

| Severity | dplyr | dplyr (excl. FP) | glosario |
|----------|------:|------------------:|---------:|
| **Errors** (blocking) | 16 | 15 | 3 |
| **Warnings** (may block) | 209 | 16 | 6 |
| **Notes** (recommended) | 30 | 30 | 15 |
| **Total** | **255** | **61** | **24** |

The raw dplyr total of 255 includes **191 DOC-08 false positives** and **1 NS-08 false positive** (see analysis below). Excluding false positives, the effective total is **63** findings, with 61 being package-specific and 2 being false positives from other rules.

### Comparison with Previous Validation (2026-02-08)

| | Previous | Current | Delta | Notes |
|---|---:|---:|---:|---|
| **dplyr total** | 45 | 255 (63 effective) | +210 (+18 effective) | 192 false positives from new DOC-08 and NS-08 rules |
| **glosario total** | 12 | 24 | +12 | 12 new advisory notes (SUB-*, NS-06, etc.) |
| **Rule count** | 130 | 141 | +11 | New rules in CODE, COMP, DATA, DOC, ENC, LIC, NAME, NS, SUB, VIG |
| **Test count** | 65+ checks | 279 tests | — | Now with full unit test coverage |
| **Categories** | 19 | 19 | 0 | Same category structure |

---

## dplyr — Detailed Breakdown

### Why these findings?

This is dplyr's **development branch** (v1.2.0.9000), not the release tarball that goes to CRAN. Some findings (DESC-12, MISC-06) are expected on dev branches. The remaining DOC-01/DOC-05 findings are on standalone exported functions that genuinely lack `@return` or `@examples` — these would be cleaned up before a CRAN release.

### Findings by Rule

| Rule | Count | Severity | What it found | Assessment |
|------|------:|----------|---------------|------------|
| DOC-08 | 191 | warning | `\item{}{}` in Rd files flagged as "lost braces inside \itemize" | **FALSE POSITIVE** — 181 are inside `\arguments{}`, 10 inside `\describe{}`, 0 actually inside `\itemize{}`. See analysis below. |
| DOC-01 | 11 | error | Missing `@return` on exported functions: `desc()`, `near()`, `order_by()`, `join_by()`, `compute()`/`collect()`, `auto_copy()`, `vars()`, `all_vars()`/`any_vars()`, `group_cols()`, `tbl()`. | True positive |
| ENC-05 | 6 | warning | Missing `%\VignetteEncoding{UTF-8}` in all 6 vignettes. | True positive |
| VIG-02 | 6 | note | Same vignette encoding issue from the vignette-check perspective. | True positive |
| DOC-05 | 5 | note | Missing `@examples` on `vars()`, `all_vars()`, `auto_copy()`, `tbl()`, and orphaned `@export` in `dbplyr.R`. | True positive |
| DOC-06 | 4 | note | Function references without parentheses in `new_grouped_df.Rd`, `ntile.Rd`, `sample_n.Rd`, `tbl_vars.Rd`. | True positive (advisory) |
| DOC-02 | 4 | warning | `\dontrun{}` in examples (`copy-to.R`, `progress.R` and their `.Rd` files) — database examples needing live connection. | True positive (justified usage) |
| NET-02 | 3 | warning | HTTP URLs in R and Rd files. Legacy URLs that should be HTTPS. | True positive |
| DOC-10 | 2 | note | `\donttest{}` in `explain.Rd` — reminder that these run under `--as-cran` since R 4.0. | True positive (advisory) |
| VIG-04 | 2 | error | Undeclared vignette dependencies: `shiny` in `programming.Rmd`, `readr` in `recoding-replacing.Rmd`. | True positive |
| NS-02 | 2 | note | Full namespace imports of `rlang` and `vctrs`. | True positive (advisory) |
| COMP-03 | 1 | warning | Non-API entry point `PRVALUE` in `src/chop.cpp`. R internals not in the public API. | True positive |
| COMP-11 | 1 | note | Compiled code requires sanitizer testing (ASAN/UBSAN/valgrind). | True positive (advisory) |
| CODE-04 | 1 | warning | `options()` without visible `on.exit()` in `locale.R`. | True positive |
| CODE-20 | 1 | note | Possible `stringsAsFactors` assumption in `grouped-df.R` — uses `is.factor()` / `as.factor()`. | Borderline — legitimate factor handling, not a stringsAsFactors assumption |
| NS-08 | 1 | error | `library()/require()` detected in `zzz.R:26`. | **FALSE POSITIVE** — the text `library(plyr); library(dplyr)` is inside a string literal within `packageStartupMessage()`, not an actual library() call. |
| NS-01 | 1 | warning | Multiple full namespace imports risk collisions. | True positive |
| VIG-08 | 1 | warning | VignetteBuilder `knitr` in Suggests, not Imports. | **FALSE POSITIVE** — knitr in Suggests is the standard recommended practice for VignetteBuilder dependencies per R Writing Extensions. |
| SIZE-01 | 1 | warning | `revdep/` directory at 1.2MB. | True positive (normal for dev branch) |
| SIZE-02 | 1 | note | Package has tests, vignettes, and compiled code (check time advisory). | True positive (advisory) |
| DESC-05 | 1 | error | Description is 1 sentence. | Borderline — sentence splitter too strict on nested comma structure |
| DESC-12 | 1 | error | Development version `.9000`. | True positive (expected on dev branch) |
| MISC-06 | 1 | note | NEWS heading "dplyr (development version)" not version-parseable. | True positive |
| LIC-02 | 1 | note | Custom license file — highlight changes in cran-comments.md. | True positive (advisory) |
| ENC-06 | 1 | note | Data files should be checked for encoding issues. | True positive (advisory) |
| DATA-06 | 1 | note | Data files should be checked for non-ASCII characters. | True positive (advisory) |
| NS-06 | 1 | note | Run R CMD check for complete binding analysis. | True positive (advisory) |
| SUB-01 | 1 | note | Pre-submission checklist: R CMD check --as-cran. | True positive (advisory) |
| SUB-02 | 1 | note | Pre-submission checklist: multi-platform testing. | True positive (advisory) |
| SUB-06 | 1 | note | CRAN submission frequency limit reminder. | True positive (advisory) |

### Assessment

- **True positives**: 61 findings — DOC-01 (11), ENC-05 (6), VIG-02 (6), DOC-05 (5), DOC-06 (4), DOC-02 (4), NET-02 (3), DOC-10 (2), VIG-04 (2), NS-02 (2), COMP-03, COMP-11, CODE-04, NS-01, SIZE-01, SIZE-02, DESC-12, MISC-06, LIC-02, ENC-06, DATA-06, NS-06, SUB-01, SUB-02, SUB-06
- **Borderline**: DESC-05 (sentence detection too strict), CODE-20 (legitimate factor handling flagged as stringsAsFactors assumption)
- **False positives**: DOC-08 (191 — all in `\arguments{}` or `\describe{}`, none in `\itemize{}`), NS-08 (1 — library() inside string literal), VIG-08 (1 — standard knitr-in-Suggests pattern)
- **False positive rate**: 75.7% raw (193 of 255), but concentrated in one rule (DOC-08). Excluding DOC-08: 3.1% (2 of 64).

---

## glosario — Detailed Breakdown

### Context

glosario is a small multilingual glossary package from The Carpentries, not currently published on CRAN. It uses R6 classes for glossary entries. The finding count increased from 12 to 24 primarily due to new advisory notes.

### Findings by Rule

| Rule | Count | Severity | What it found | New? |
|------|------:|----------|---------------|------|
| DOC-05 | 4 | note | Exported functions (`define`, `gdef`, `list_glosario_terms`, `validate_document`) lack `@examples`. | |
| NET-02 | 2 | warning | `http://www.loc.gov/standards/iso639-2/...` in `iso639.R` and `iso639.Rd`. Should be HTTPS. | |
| CODE-07 | 2 | warning | `tempfile()`/`tempdir()` without `unlink()`/`on.exit()` cleanup in `entry.R` and `parse.R`. | Yes |
| DOC-01 | 1 | error | `list_glosario_terms` missing `@return` tag. | |
| DESC-05 | 1 | error | Description is 1 sentence. Needs a second sentence. | |
| DESC-09 | 1 | error | No `cph` role in Authors@R. Needs at least one copyright holder. | |
| CODE-02 | 1 | warning | `print()` in `validate_document.R:36`. Should be `message()`. | |
| VIG-08 | 1 | warning | VignetteBuilder `knitr` in Suggests, not Imports. | Yes (false positive) |
| MISC-01 | 1 | note | No NEWS.md file. | |
| SUB-04 | 1 | note | No cran-comments.md file. | |
| SUB-01 | 1 | note | Pre-submission checklist: R CMD check --as-cran. | Yes (advisory) |
| SUB-02 | 1 | note | Pre-submission checklist: multi-platform testing. | Yes (advisory) |
| SUB-05 | 1 | note | First CRAN submission expected NOTE. | Yes (advisory) |
| SUB-06 | 1 | note | CRAN submission frequency limit. | Yes (advisory) |
| NS-06 | 1 | note | Run R CMD check for binding analysis. | Yes (advisory) |
| NAME-02 | 1 | note | Package names are permanent. | Yes (advisory) |
| LIC-02 | 1 | note | Custom license file advisory. | Yes (advisory) |
| ENC-06 | 1 | note | Check data files for encoding issues. | Yes (advisory) |
| DATA-06 | 1 | note | Check data files for non-ASCII characters. | Yes (advisory) |

### Assessment

- **True positives**: 23 of 24 findings are legitimate
- **False positives**: VIG-08 (1 — knitr in Suggests is standard practice)
- **False positive rate**: 4.2% (1 of 24)
- **If submitting to CRAN**: 3 blocking issues must be fixed (DESC-05, DESC-09, DOC-01)
- **New findings vs previous**: 11 new rules fired, all advisory notes except CODE-07 (2 true positives about uncleaned temp files) and VIG-08 (1 false positive)

### What Would `/cran-fix` Auto-Fix?

| Fix | Tier | Rule | Action |
|-----|------|------|--------|
| FIX-HTTP | Tier 1 | NET-02 | `http://` -> `https://` (2 files) |
| FIX-CPH | Tier 2 | DESC-09 | Add `"cph"` role to first author |
| FIX-RETURN | Tier 2 | DOC-01 | Add `@return` to 1 function |
| FIX-DESCRIPTION-TEXT | Tier 3 | DESC-05 | Rewrite Description (needs user input) |

After auto-fix: 0 errors, 4 warnings (CODE-02, CODE-07 x2, VIG-08), 15 notes.

---

## False Positive Analysis

### DOC-08: Critical False Positive (191 findings on dplyr)

The DOC-08 check ("lost braces: `\item{}{}` inside `\itemize`") has a scoping bug. It checks whether `\itemize` appears **anywhere in the file** (`if r'\itemize' in text`), then flags **every** `\item{name}{desc}` pattern in the file — including those correctly placed inside `\arguments{}` and `\describe{}` blocks.

| Context | Count | Correct syntax? | Assessment |
|---------|------:|:----------------:|------------|
| Inside `\arguments{}` | 181 | Yes | **False positive** — `\item{param}{desc}` is required here |
| Inside `\describe{}` | 10 | Yes | **False positive** — `\item{name}{desc}` is required here |
| Inside `\itemize{}` | 0 | No | Would be true positive (none found) |

**Root cause**: The check needs to parse Rd block nesting to determine whether a given `\item{}{}` is inside `\itemize{}` (wrong) vs `\arguments{}` or `\describe{}` (correct).

**Impact**: This single rule accounts for 74.9% of all dplyr findings and 100% of its false positives. Fixing this would bring the dplyr false positive rate from 75.7% to 3.1%.

### NS-08: String Literal False Positive (1 finding on dplyr)

The NS-08 check flags `library()`/`require()` calls in package code. It matched `library(plyr); library(dplyr)` in `R/zzz.R:26`, but this text is inside a string literal passed to `packageStartupMessage()` — it's instructional text for users, not an actual library() call.

**Root cause**: The `scan_file()` regex matches `library(...)` patterns regardless of whether they're inside string literals.

### VIG-08: Standard Practice False Positive (1 finding each on dplyr and glosario)

The VIG-08 check flags VignetteBuilder packages that are in Suggests instead of Imports. However, placing knitr in Suggests (not Imports) is the **standard recommended practice** per R Writing Extensions. VignetteBuilder packages are needed only for building vignettes, not at runtime.

---

## False Positive Reduction (Existing)

The checker includes multiple layers of context-aware filtering to avoid flagging legitimate code patterns. These remain effective.

### DOC-01/DOC-05: Roxygen Block Awareness

| Pattern | What it skips | Example |
|---------|--------------|---------|
| `@rdname`/`@name` | Docs inherited from shared block | `#' @rdname group_data` |
| `@keywords internal` | Internal functions don't need full docs | `#' @keywords internal` |
| `@inherit` | Inherits sections from another function | `#' @inherit dbplyr::sql` |
| Reexports | `pkg::fun` — docs live in originating package | `tibble::as_tibble` |
| S3 methods | `foo.bar` inherits from generic | `group_data.data.frame` |
| Backtick methods | Operator/method overloads | `` `[.grouped_df` <- function `` |
| NULL blocks | Doc blocks for `@name`/`@aliases` grouping | `NULL` after roxygen |

**Impact on dplyr:**

| Check | Before filtering | After filtering | Reduction |
|-------|----------------:|---------------:|-----------:|
| DOC-01 | 378 | 11 | 97% |
| DOC-05 | 359 | 5 | 99% |

### CODE-02: Display Context Awareness

| Pattern | What it skips |
|---------|--------------|
| S3 method definitions | `print.foo <- function(...)` line |
| S3 method bodies | `cat()`/`print()` inside brace-delimited body |
| R6/RefClass methods | `print = function` inside R6 class |
| Display helper functions | Functions named `cat_*`, `show_*`, `display_*`, `render_*`, `draw_*`, `print_*`, `format_*` |
| Verbose/interactive guards | `if(verbose)` or `if(interactive())` |
| `UseMethod()` dispatchers | Generic function definitions |
| R6 method calls | `self$print()`, `x$format()` |

**Impact on dplyr:** 19 naive findings -> 0 after filtering (100% reduction).

### CODE-09: Closure-Aware `<<-` Detection

**Impact on dplyr:** 6 findings -> 0 (all were `<<-` inside closures/condition handlers/tidy eval quosures).

---

## New Rules Since Previous Validation

11 new rules were added since the previous validation (130 -> 141). Of these, the following fired on the test packages:

| Rule | Category | dplyr | glosario | Assessment |
|------|----------|------:|--------:|------------|
| DOC-08 | Documentation | 191 | 0 | **False positive** — needs Rd block nesting awareness |
| DOC-06 | Documentation | 4 | 0 | True positive — function refs without `()` |
| DOC-10 | Documentation | 2 | 0 | True positive — `\donttest{}` runs under `--as-cran` |
| CODE-07 | Code | 0 | 2 | True positive — uncleaned temp files |
| CODE-20 | Code | 1 | 0 | Borderline — legitimate factor usage |
| COMP-03 | Compiled | 1 | 0 | True positive — non-API R internals |
| COMP-11 | Compiled | 1 | 0 | True positive — sanitizer testing advisory |
| NS-08 | Namespace | 1 | 0 | **False positive** — matched string literal |
| VIG-08 | Vignettes | 1 | 1 | **False positive** — knitr in Suggests is standard |
| SUB-01/02/05/06 | Submission | 2 | 4 | True positive — pre-submission advisories |
| NAME-02 | Naming | 0 | 1 | True positive — name permanence advisory |
| LIC-02 | License | 1 | 1 | True positive — license change advisory |
| ENC-06 | Encoding | 1 | 1 | True positive — data encoding advisory |
| DATA-06 | Data | 1 | 1 | True positive — data non-ASCII advisory |
| NS-06 | Namespace | 1 | 1 | True positive — R CMD check binding advisory |
| SIZE-02 | Size | 1 | 0 | True positive — check time advisory |

---

## Recommended Fixes

Based on this validation, three checker bugs should be addressed:

1. **DOC-08 (critical)**: Parse Rd block nesting so `\item{name}{desc}` is only flagged when actually inside `\itemize{}`, not inside `\arguments{}` or `\describe{}`. This would eliminate 191 false positives on dplyr.

2. **NS-08 (moderate)**: Skip matches inside string literals. The regex should not flag `library()`/`require()` when they appear inside quoted strings.

3. **VIG-08 (minor)**: Remove or downgrade the check that flags VignetteBuilder packages in Suggests. This is standard R practice, not an error.

---

## Conclusions

1. **The checker's core rules remain accurate** — DOC-01, DOC-05, ENC-05, VIG-02, VIG-04, NET-02, NS-01/NS-02, CODE-04, DESC-05, DESC-12, MISC-06 all produce correct results, unchanged from the previous validation.
2. **New advisory rules add value** — DOC-06, DOC-10, CODE-07, COMP-03, COMP-11, SUB-*, and other new rules provide useful pre-submission guidance.
3. **DOC-08 has a critical false positive bug** — 191 of 191 findings on dplyr are false positives due to incorrect `\itemize` scoping. This is the highest-priority fix.
4. **Excluding DOC-08, false positive rate is ~3%** — 2 false positives (NS-08, VIG-08) out of 64 findings on dplyr, and 1 false positive (VIG-08) out of 24 on glosario.
5. **Including DOC-08, false positive rate is ~69%** — 193 false positives out of 279 combined findings. This makes the raw output unusable for CI without fixing DOC-08.
6. **The rule count grew from 130 to 141** with 279 unit tests providing coverage.
7. **DOC-01/DOC-05 filtering remains effective** — 97-99% false positive reduction via roxygen inheritance awareness.
8. **CODE-02 and CODE-09 filtering remain effective** — 100% false positive elimination on dplyr.
