# CRAN Removed/Archived Packages: August 2025 - February 2026

Generated: 2026-02-08

## Executive Summary

Research across CRANberries, CRANhaven, individual CRAN package pages, and community discussions reveals significant ongoing package archival activity. In the last 35 days alone (early Jan - Feb 8 2026), approximately 183 packages were archived from CRAN. The primary drivers remain: (1) uncorrected check failures despite reminders, (2) dependency cascade removals, (3) policy violations (especially internet access), and (4) undeliverable maintainer email. A notable trend is increased enforcement around GCC 15 / C23 compiler compatibility and continued strict internet access policy enforcement.

---

## Archival Reasons: Taxonomy

Based on CRAN's own archival notices, packages are removed for these categories:

| Reason Category | Verbatim CRAN Text | Frequency |
|---|---|---|
| **Uncorrected issues** | "issues were not corrected despite reminders" / "issues were not corrected in time" / "issues were not addressed in time despite reminders" | Most common (~64% historically) |
| **Dependency cascade** | "requires archived package 'X'" | Second most common (~14%) |
| **Policy violation** | "policy violation" / "repeated policy violation" | Third (~7%) |
| **Undeliverable email** | "email to the maintainer is undeliverable" | Fourth (~2.5%) |
| **Maintainer request** | (no standard text) | Rare |
| **Orphaned** | Package listed as orphaned, then archived | Rare |

Historical data (CRANhaven study, July 2024 snapshot):
- 9,089+ packages have been archived from CRAN total
- 39% of all 23,058 packages ever on CRAN experienced archival
- 36-38% of archived packages eventually return (median 33 days)
- 50% never return

---

## Specific Packages Archived: August 2025 - February 2026

### February 2026

| Package | Date | Reason | Notes |
|---|---|---|---|
| **emodnet.wfs** | 2026-02-08 | Issues not corrected in time | |
| **WikidataQueryServiceR** | 2026-02-08 | Policy violation | |
| **WikidataR** | 2026-02-08 | Requires archived package 'WikidataQueryServiceR' | Cascade |
| **taxize** | 2026-02-08 | Requires archived package 'wikitaxa' | Cascade; major rOpenSci taxonomy package |
| **wikitaxa** | 2026-02-08 | (removed) | Triggered taxize cascade |
| **brfinance** | 2026-02-08 | (removed) | |
| **wklsr** | 2026-02-08 | (removed) | |
| **dictionar6** | 2026-02-08 | (removed) | |
| **ooplah** | 2026-02-08 | (removed) | |
| **ShinyLink** | 2026-02-08 | (removed) | |
| **taxotools** | 2026-02-08 | (removed) | |
| **tidywikidatar** | 2026-02-08 | (removed) | |
| **refdb** | 2026-02-08 | (removed) | |
| **tdigest** | 2026-02-07 | Issues not corrected despite reminders | |
| **pgenlibr** | 2026-02-06 | (removed) | |
| **unigd** | 2026-02-06 | Issues not corrected in time | |
| **NNbenchmark** | 2026-02-05 | (removed) | |
| **EcoCleanR** | 2026-02-05 | (removed) | |

### January 2026

| Package | Date | Reason | Notes |
|---|---|---|---|
| **applicable** | 2026-01-31 | Issues not corrected despite reminders | tidymodels ecosystem |
| **dataset** | 2026-01-30 | Issues not corrected in time | |
| **qs** | 2026-01-17 | Issues not corrected despite reminders | Popular serialization package |
| **fuzzyjoin** | 2026-01-16 | Issues not addressed in time despite reminders | Popular tidyverse-adjacent package by David Robinson |
| **kml** | 2026-01-16 | Requires archived package 'clv' | Cascade |
| **longitudinalData** | 2026-01-16 | Requires archived package 'clv' | Cascade |
| **kml3d** | Jan 2026 | (removed) | Likely cascade from kml/clv |
| **bdc** | Jan 2026 | (removed) | |
| **rfigshare** | Jan 2026 | (removed) | |

### November - December 2025

| Package | Date | Reason | Notes |
|---|---|---|---|
| **checkpoint** | 2025-11-07 | Issues not corrected despite reminders | Microsoft/Revolution Analytics package |
| **fdicdata** | 2025-11-11 | Repeated policy violation | |
| **fipp** | 2025-11-27 | Email to the maintainer is undeliverable | |
| **clrng** | 2025-11-28 | Email to the maintainer is undeliverable | |
| **pocketapi** | 2025-12-12 | (removed) | |
| **nutriNetwork** | Late 2025 | (removed) | |
| **HTGM3D** | Late 2025 | (removed) | |
| **NetGreg** | Late 2025 | (removed) | |
| **viralmodels** | Late 2025 | (removed) | |
| **viraldomain** | Late 2025 | (removed) | |

### October 2025

| Package | Date | Reason | Notes |
|---|---|---|---|
| **codebook** | 2025-10-26 | Policy violation | |
| **repo.data** | 2025-10-01 | Policy violation | Lluis Revilla's CRAN metadata package |

### August - September 2025

| Package | Date | Reason | Notes |
|---|---|---|---|
| **BEAMR** | 2025-09-17 | Email to the maintainer is undeliverable | |
| **AntMAN** | 2025-09-17 | Email to the maintainer is undeliverable | |
| **robustcov** | 2025-09-17 | Email to the maintainer is undeliverable | Batch of 3 on same day |

---

## Observed Patterns and Waves

### Pattern 1: Dependency Cascade Removals

When a package is archived, all packages that depend on it (in Imports/Depends) are also archived unless they remove the dependency in time. This creates cascade waves:

**clv cascade (Jan 2026):** clv archived -> kml, longitudinalData, kml3d all removed
**WikidataQueryServiceR cascade (Feb 2026):** WikidataQueryServiceR archived for policy violation -> WikidataR, tidywikidatar removed
**wikitaxa cascade (Feb 2026):** wikitaxa archived -> taxize (major package) removed
**acs cascade (Feb 2025):** acs archived for /bin/bash NOTE -> choroplethr, noaastormevents, synthACS removed (43,037 combined downloads in 2024)

This is historically the second most common reason for archival (~14% of all archivals). Many of these packages return once the dependency is fixed.

### Pattern 2: Internet Access Policy Enforcement

CRAN continues aggressive enforcement of its internet access policy. Packages that access external APIs/web services must fail gracefully when resources are unavailable.

Recent policy violation archivals include:
- **rusquant** (2025-04-28) - repeated policy violations on Internet access
- **fdicdata** (2025-11-11) - repeated policy violation
- **WikidataQueryServiceR** (2026-02-08) - policy violation (likely internet access related given package purpose)

This pattern has been enforced more heavily since 2024 when CopernicusMarine, filibustr, and others were archived for the same reason.

### Pattern 3: Undeliverable Email Batches

CRAN periodically processes batches of packages with bouncing maintainer emails:

- **2025-09-17 batch:** BEAMR, AntMAN, robustcov (3 packages same day)
- **2025-11-27/28:** fipp, clrng (back-to-back days)
- Earlier in 2025: kpmt (Apr 27), rpcss (Apr 5), expectreg (Jun 6), ecpc (Jul 23)

### Pattern 4: Check Failure Deadlines Not Met

The most common archival reason. CRAN sends reminders when R CMD check produces errors/warnings. If not fixed within the deadline (typically 2-4 weeks), the package is archived.

Notable recent examples:
- **fuzzyjoin** (2026-01-16) - popular package, issues not addressed in time
- **qs** (2026-01-17) - popular serialization package
- **checkpoint** (2025-11-07) - Microsoft package
- **applicable** (2026-01-31) - tidymodels ecosystem
- **tdigest** (2026-02-07)
- **unigd** (2026-02-06)

### Pattern 5: GCC 15 / C23 Compiler Impact (Emerging)

R 4.5.0+ defaults to C23 when the compiler supports it. GCC 15 defaults to C23 (gnu23). This means:
- `bool`, `true`, `false` are now C keywords (previously needed stdbool.h)
- `typedef int bool;` and similar patterns now cause compiler errors
- Packages with compiled code that haven't been updated may fail checks

CRAN's check infrastructure includes explicit gcc15 and C23 check flavors. Packages failing these checks are being flagged and will face archival if not corrected. This is a potential source of a larger archival wave as GCC 15 becomes the default compiler on more platforms.

### Pattern 6: Volume Trend

CRANhaven reports **183 packages archived in the last 35 days** (as of Feb 8, 2026). This is a high rate -- roughly 5+ packages per day. Historically:
- ~9,089 total archival events across CRAN's history
- Average was lower in earlier years; the rate has been increasing as the repository grows (21,000+ active packages)

---

## Community Response

### CRANhaven

CRANhaven (cranhaven.org) has emerged as a safety net, maintaining archived packages via r-universe so users can still install them:
```r
install.packages("pkgname", repos = "https://cranhaven.r-universe.dev")
```

### "Is CRAN Holding R Back?" (Feb 2025)

Ari Lamstein's influential blog post questioned whether CRAN's strict enforcement is counterproductive. Key arguments:
- The acs package was archived for a NOTE about `/bin/bash` not being portable -- an issue present for 9 years with no user impact
- Cascade archived choroplethr + 2 other packages (43K combined downloads/year)
- CRAN's 1-2 month minimum between updates is restrictive compared to PyPI/npm
- Short deadlines for fixes don't accommodate maintainers' real-world schedules

### R Consortium Working Group

The R Consortium's r-repositories-wg has an open issue (#8) about archived CRAN packages. Proposed solutions include community-maintained rescue repositories and better transparency about archival processes. Activity on this issue has been limited since 2022.

---

## Implications for Pedantic CRAN

These findings suggest several areas where the pedanticran tool should check:

1. **Internet access handling** - Verify all functions accessing external resources fail gracefully with informative messages (not errors or warnings)
2. **Dependency health** - Warn if any Imports/Depends packages are at risk of archival (have failing checks)
3. **Compiled code C23 compatibility** - Check for `typedef int bool`, non-portable configure scripts, deprecated C constructs
4. **Maintainer email validity** - Remind maintainers to verify their DESCRIPTION email is deliverable
5. **noSuggests compatibility** - Ensure Suggests packages are used conditionally
6. **Configure script portability** - Check for `/bin/bash` shebangs (should be `/bin/sh` or use `#!/usr/bin/env bash`)

---

## Sources

- CRANberries removed packages: http://dirk.eddelbuettel.com/cranberries/cran/removed/
- CRANhaven dashboard: https://www.cranhaven.org/dashboard-live.html
- CRANhaven archival statistics: https://www.cranhaven.org/cran-archiving-stats.html
- CRAN Repository Policy: https://cran.r-project.org/web/packages/policies.html
- CRAN Package Check Issue Kinds: https://cran.r-project.org/web/checks/check_issue_kinds.html
- "Is CRAN Holding R Back?" by Ari Lamstein: https://arilamstein.com/blog/2025/02/12/is-cran-holding-r-back/
- "Reasons why packages are archived on CRAN" by Lluis Revilla: https://llrs.dev/post/2021/12/07/reasons-cran-archivals/
- R Consortium Archived CRAN Packages discussion: https://github.com/RConsortium/r-repositories-wg/issues/8
- R-hub cransays dashboard: https://r-hub.github.io/cransays/articles/dashboard.html
- Individual CRAN package pages (cran.r-project.org/web/packages/*/index.html) for: taxize, fuzzyjoin, qs, checkpoint, codebook, fdicdata, WikidataQueryServiceR, WikidataR, emodnet.wfs, kml, longitudinalData, applicable, dataset, tdigest, unigd
