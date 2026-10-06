# R-package-devel Mailing List: CRAN Rejection Patterns (Feb 2026 - Sep 2026)

Generated: 2026-10-05

## Executive Summary

All 325 R-package-devel messages posted between 1 February and 30 September 2026 (archives 2026q1-2026q3) were read in full, together with the r-devel threads from the same months in which CRAN or R Core members discussed check changes, the R 4.6.0/4.6.1 and R-devel NEWS, the 2026 CRAN Repository Policy revisions, and the `X-CRAN-Comment` archival notes in CRAN's `PACKAGES.in`.

The main themes:

1. **Internet access is the leading cause of policy-violation archivals.** Of 29 packages archived "for policy violation" in Feb-Sep 2026 and still archived, 25 were archived "On Internet access". Seven of the 25 were repeat offenders ("repeated policy violation").
2. **About 400 packages were archived over undeliverable maintainer email**, with 278 of them between 30 April and 14 May 2026. This was by far the largest archival reason in the window.
3. **A new policy-violation reason: a cache in `~/.cache/R` larger than 100 MB that is never cleaned up.** Two packages were archived for it (June 2026). The list confirmed that R CMD check must not create or modify the user's cache at all.
4. **New `Authors@R` "possibly unsafe calls" NOTE.** Kurt Hornik added it in R-devel r89866 (10 April 2026) and backported it to R-4-6-branch. It fires on `comment(ORCID = ...)`-style mistakes.
5. **Overall check time > 10 min is enforced on the r-devel-windows pretest.** CRAN overrides it manually for large packages such as oce. The NOTE is easy to miss in the pretest email.
6. **Rd files with `\arguments` but no `\usage` get a NOTE.** Uwe Ligges said such files "should really add the usage line".
7. **The R 4.6.0 C API cut-over.** Installed headers now equal the API; non-API *variables* now get NOTEs; `R_ext/Callbacks.h` is gone; CRAN hosted transitional versions of key packages.
8. **CRAN policy revision 6738 (captured 2026-02-20)** made the rule explicit that strong dependencies must come from CRAN or the Bioconductor *software* repository.
9. **Platform-specific failures from additional-issue flavors are now reported in incoming pretests.** linux-arm64 is the main one, along with ASAN/UBSAN and gcc-16. CRAN treats these as blocking.

## Research Sources

- R-package-devel archives (primary): https://stat.ethz.ch/pipermail/r-package-devel/2026q1/, /2026q2/, /2026q3/ (full mbox text was downloaded and every message read; message URLs below were checked against the archive date index)
- r-devel archives, Feb-Sep 2026: https://stat.ethz.ch/pipermail/r-devel/ (threads involving Kurt Hornik, Simon Urbanek, Luke Tierney, Sebastian Meyer)
- CRAN archival notes: https://cran.r-project.org/src/contrib/PACKAGES.in (retrieved 2026-10-05; `X-CRAN-Comment` fields with "Archived on 2026-02..09")
- CRAN Repository Policy, current rev 6875: https://cran.r-project.org/web/packages/policies.html; revision history via the policy mirror https://github.com/eddelbuettel/crp (commits for rev6738 on 2026-02-20, rev6846 on 2026-04-21, rev6875 on 2026-05-31)
- R NEWS: https://cran.r-project.org/doc/manuals/r-release/NEWS.html (4.6.0, 4.6.1) and https://cran.r-project.org/doc/manuals/r-devel/NEWS.html
- "Using Rust in CRAN packages": https://cran.r-project.org/web/packages/using_rust.html

Caveats:
- The web search tools were rate-limited during this session, so blog posts and the mail-archive.com mirror were **not** surveyed. Everything below comes from the primary sources listed above.
- CRAN's personal rejection emails to maintainers are rarely posted verbatim. Where a maintainer paraphrases a reviewer, the text is labelled as a paraphrase.

---

## Rejection/Issue Categories

### 1. Internet Access Policy-Violation Archivals (Dominant Policy Reason)

**Packages (archived Feb-Sep 2026, still archived on 2026-10-05):** WikidataQueryServiceR, mapsFinland, nisrarr, scSorter, snvecR, peermodels, blscrapeR (repeated), annotaR, LobsterCatch, Rfssa, eudata, RcensusPkg, tidypmc, ineAtlas, rtiddlywiki, rtreeoflife, sfhelper, EEAaq (repeated), filibustr (repeated), kofdata (repeated), polite, PhytoIn, rglobi (repeated), welo. That is 25 of the 29 policy-violation archivals.

**Verbatim archive notes (PACKAGES.in):**
> "Archived on 2026-02-08 for policy violation. . On Internet access. And the maintainer does not want to correct it." (WikidataQueryServiceR)

> "Archived on 2026-09-04 for repeated policy violation. . On Internet access." (kofdata; its X-CRAN-History shows earlier Internet-access archivals in 2020, 2021 and 2024)

**List discussion (rerddapUtils, May 2026).** Pretest example timings were inflated by a slow US-government website. **Uwe Ligges:**
> "Given the timings I guess these are internet access issues with US government web sites that we frequently observe. Simply define a timeout for internet access and exit gracefully if you hit it."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012391.html

**List discussion (CopernicusMarine, Feb 2026).** A vignette failed on M1mac when a remote download failed inside stars/GDAL. **Simon Urbanek:**
> "Remote calls are always tricky, because you can't guarantee they will work, so you should always guard against failure."

> "In the end it is your responsibility since you are providing the API, the user shouldn't' need to know anything about the intricacies of what happens under the hood in other packages."

Sources: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012277.html, https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012285.html

**Related: finding every network call.** One maintainer (Lluís Revilla, repo.data) reported an earlier archival "because it accessed the internet and I had checked the connection in one place but not in others on the same file". Uwe Ligges then asked why `available.packages()` is called during checks at all: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012473.html, https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012496.html

**Key details:**
- Category: Internet & external resources
- Maps to: **NET-01**, with timeouts and failures inside third-party code (GDAL/stars) in scope
- Graceful failure must also cover:
  - network failures inside dependencies the package calls
  - timeouts, which show up as slow examples (DOC-03 NOTE) rather than errors
- Frequency: **recurring, the single largest policy-violation category.** Repeat offenders get "repeated policy violation".

---

### 2. Mass Archival for Undeliverable Maintainer Email

**Packages:** 405 packages archived Feb-Sep 2026 with this note (still archived on 2026-10-05). The wave peaked on 2026-04-30 (63), 2026-05-04 (75), 2026-05-06 (46), 2026-05-08 (34) and 2026-05-14 (60).

**Verbatim archive note:**
> "Archived on 2026-05-04 as email to the maintainer is undeliverable."

**Monthly counts (undeliverable email):** Feb 13, Mar 3, Apr 126, May 232, Jun 23, Jul 4, Aug 2, Sep 2.

**Key details:**
- Category: Maintainer email
- Maps to: **EMAIL-05** (institutional email longevity)
- In this window, undeliverable email (405) outnumbered "issues not corrected" (373) as an archival reason.
- The cause of the April/May wave was not announced on the lists. It looks like a bulk deliverability sweep by CRAN (**UNVERIFIED** as to mechanism).
- A related thread (MBHdesign, Sep 2026) shows the maintainer suspected an email-domain change. The real blocker was check time (see #5).
- Frequency: **recurring, very high volume.**

---

### 3. User Cache in ~/.cache/R: Size and Writes During R CMD check

**Packages:** nomesbr, rcldf (archived 2026-06-01); rsurvstat (deadline 2026-08-21, Jul 2026 thread)

**Verbatim archive notes:**
> "Archived on 2026-06-01 for policy violation. . Stores > 100 MB in ~/.cache/R and does not clean up." (nomesbr)

> "Archived on 2026-06-01 for policy violation. . Stores > 150 MB in ~/.cache/R and does not clean up." (rcldf)

**CRAN check NOTE seen by rsurvstat (verbatim, as posted by the maintainer):**
> "* checking for new files in some other directories ... NOTE
> Found the following files/directories:
>   '~/.cache/rsurvstat/022e3d1edce617738e145996fea14ed7.xml'"

**Ivan Krylov's answer** (not CRAN team) to "is there a need to disable the caching specifically for the CRAN checks":
> "Yes. In addition to caching files in designated places during normal usage (as your package does), running R CMD check shouldn't create or modify user files (including the cache)."

Sources: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012484.html, https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012486.html

**Policy text (rev 6875):**
> "packages may store user-specific data, configuration and cache files in their respective user directories obtained from tools::R_user_dir(), provided that by default sizes are kept as small as possible and the contents are actively managed (including removing outdated material)."

**Key details:**
- Maps to: **CODE-06** (currently presents `R_user_dir()` as the sanctioned escape hatch, with no caveats) and CODE-07
- Novel: the first archivals on record for cache *size or management* rather than location. The check flags any file created under `~/.cache/<pkg>` during examples, tests or vignettes.
- A separate false positive occurred on 2026-08-02: on r-devel-linux-x86_64-debian-gcc, every package got "Found the following files/directories: '~/tmp/scratch/Rtmp...'" because of Xvfb temp files. That was a CRAN machine configuration issue (Krylov: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012502.html).
  - Uwe Ligges, asked whether to act on that NOTE: "If it is true that you generate files elsewhere without cleaning up: Yes!" (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012507.html)
- Frequency: **emerging** (2 archivals plus 1 deadline in 4 months)

---

### 4. Authors@R "Possibly Unsafe Calls" (New Check, R-devel r89866 / R 4.6 branch)

**Packages:** about 20 CRAN packages, per Kurt Hornik; qvalue (Bioconductor, `as.person`); flowCore (Bioconductor, `personList`)

**Trigger:** a security report on r-devel that `Authors@R` is evaluated whenever DESCRIPTION is parsed. **Kurt Hornik (verbatim):**
> "The current situation on CRAN Authors@R uses is quite manageable: about 20 packages use "strange" calls in these, in most cases from mis-specifying the ORCID comment like
>
>   comment(ORCID = ...)
>   ORCID =
>
> instead of
>
>   comment = c(ORCID = ...)
>
> Yesterday I committed
>
> r89866 | hornik | 2026-04-10 21:31:32 +0200 (Fri, 10 Apr 2026) | 1 line
> Complain about possibly unsafe calls in Authors@R.
>
> so these calls now get speeding tickets which also give check NOTEs, like
>
> * checking DESCRIPTION meta-information ... NOTE
> Malformed Authors@R field:
>   Found the following possibly unsafe calls:
>     comment("SwissMarbledWhite")
>   Please only use calls to 'person', 'c', 'list', 'paste', 'paste0'.
>
> I will "eventually" change the reader code to no longer eval when seeing calls not in the whitelist."

Source: https://stat.ethz.ch/pipermail/r-devel/2026-April/084480.html

Follow-up: `as.person` was whitelisted "and even merged into R-4-6-branch" (Hornik, https://stat.ethz.ch/pipermail/r-devel/2026-April/084490.html).

Ivan Krylov added that the check is more than a NOTE outside R CMD check: on a source directory, R CMD build and R CMD INSTALL call the same check, "which fails the build" (https://stat.ethz.ch/pipermail/r-devel/2026-April/084491.html).

**Key details:**
- Maps to: **NEW** (closest is DESC-08)
- Hornik also said CITATION files are next: "The harder part will be narrowing down the calls allowed in CITATION files" (relates to INST-02).
- Frequency: **new check**, affecting about 20 CRAN packages at introduction

---

### 5. Overall Check Time > 10 Minutes (Pretest Auto-Reject; Manual Override Possible)

**Packages:** oce (Jun-Jul 2026), MBHdesign (Sep 2026)

**Pretest NOTE (verbatim, from the oce auto-check email):**
> "Flavor: r-devel-windows-x86_64
> Check: Overall checktime, Result: NOTE
> Overall checktime 16 min > 10 min"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012428.html

**Uwe Ligges on MBHdesign:**
> "At the bottom of the message reasons are always attached and this time it was
>
> Flavor: r-devel-windows-x86_64
> Check: Overall checktime, Result: NOTE
>    Overall checktime 25 min > 10 min
>
> mainly from
>
> * checking tests ... [14m] OK"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012533.html

Sebastian Meyer found vignette re-building at "[23m]", probably from switching off precompiled vignette data (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012535.html).

**Uwe Ligges on the oce exception:**
> "Yes, we believe it is hard to improve the timing as a lot comes from documentation and offline code checks. That's why CRAN overruled the 10 min threshold and let your package pass."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012458.html

**Uwe Ligges on install time vs check time:**
> "1 minute is perfectly fine.
>
> The oeverall check time should not exceed 10 minutes." [sic]

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012338.html

**Uwe Ligges on unanswered emails:**
> "Note we receive roughly 300 messages per day (including submission mails and the mails we send out). Once 2 weeks passed, please send us a reminder in case we have not responded."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012456.html

**Key details:**
- Maps to: **SIZE-02**
- The binding flavor is **r-devel-windows-x86_64**, which is slower than Debian.
- The NOTE is listed at the bottom of the pretest email and is easy to miss. Ben Bolker: "this timing report is really easy to miss (I've missed it at least once before)" (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012534.html).
- Exceptions are granted manually for large packages, but each submission needs a human to sign off again.
- Frequency: **recurring** (2 threads)

---

### 6. Example Timing NOTEs (> 5 s) Including Network Latency

**Packages:** integrity (Mar 2026; archived, example 6.4 s on Linux and 11.9 s on Windows); rerddapUtils (May 2026)

**Check NOTE (verbatim, reproduced by Ivan Krylov via a non-US proxy):**
> "* checking examples ... [3s/47s] NOTE
> Examples with CPU (user + system) or elapsed time > 5s"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012386.html

Ivan Krylov on integrity: "I don't think there's any special consideration for packages whose examples take too long for algorithmic reasons" (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012309.html).

**Key details:**
- Maps to: **DOC-03** (and NET-01 for the latency cause)
- Elapsed time counts, not just CPU. An example waiting on a slow overseas server trips the NOTE on the Vienna/Dortmund pretest machines even when it passes elsewhere.
- Frequency: **recurring**

---

### 7. Rd Files With \arguments but No \usage

**Packages:** shinylight (Sep 2026; JavaScript functions documented in Rd); causalDisco (Jul 2026; roxygen overview page for `plot` documented on `NULL`)

**Pretest NOTE quoted by Uwe Ligges:**
> "Flavor: r-devel-linux-x86_64-debian-gcc
> Check: Rd contents, Result: NOTE
>    Rd files without \usage:
>      'framework.shinylightFrameworkStart.Rd' 'shinylight.call.Rd'
>      [...]
>    \arguments should not be documented without \usage."

**Uwe Ligges:**
> "And you should really add the usage line, a usage line does not mean these are executed. An example would...."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012558.html

Ivan Krylov later corrected himself on what can go in `\usage`: "Entries in \usage{} that parse as valid R function calls must correspond to real R functions with matching arguments." (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012566.html). His alternative is to replace `\arguments{}` with a `\describe{}` list.

causalDisco fix (Krylov): "Since roxygen only sees NULL as the object being documented, it cannot derive a valid \usage{...} from the information it is given. You can provide `#' @usage plot(x, ...)` by hand (or remove the @param tags)." (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012470.html)

**Key details:**
- Maps to: **NEW** (Documentation)
- R 4.6.0 NEWS also says: "tools::checkDocFiles() notes more cases of usage documentation without corresponding \alias."
- Frequency: **recurring** (2 threads in 3 months; both triggered by roxygen patterns)

---

### 8. "Empty URL" in README.md and ::: Calls to the Package's Own Namespace

**Package:** saferDev 1.0.0 (new submission, May 2026; pretest-archived, later fixed)

**Pretest NOTEs (verbatim, from the CRAN auto-check email posted by the maintainer):**
> "Check: CRAN incoming feasibility, Result: NOTE
>   [...]
>   Found the following (possibly) invalid URLs:
>     URL:
>       From: README.md
>       Message: Empty URL"

> "Check: dependencies in R code, Result: NOTE
>   There are ::: calls to the package's namespace in its code. A package
>     almost never needs to use ::: for its own objects:
>     '.all_args_here_fill' '.base_op_check' [...]"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012388.html

**Cause:** an `<a href="">` in README.md. Michael Chirico: "probably 'check' only looks for empty href more recently" (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012390.html). He showed how to reproduce it with `tools:::.pandoc_md_for_CRAN()`.

**Key details:**
- Maps to: **MISC-02** (empty-href case is new) and **NEW** (`:::` to own namespace; CODE-12 only covers base and recommended packages)
- The maintainer argued the `:::` use was deliberate. The package was resubmitted with both fixed and moved to human review, which suggests the NOTE was treated as blocking for a new submission.
- R 4.6.0 NEWS: "Package 'README.md' files are now installed and featured in HTML help." README content is now more visible to checks.
- Frequency: one-off on the list; the `:::` NOTE is long-standing

---

### 9. URL Checks: 403 from Bot Protection, Geo-Blocked Hosts, R Bugzilla 418

**Packages:** parallelly (winehq.org returns 403 via Cloudflare, Mar 2026); shiny.webawesome (SSL reset from Germany, Apr 2026); any package linking bugs.r-project.org (HTTP 418 during a DDoS, Mar 2026)

**Simon Urbanek on 403 pages:**
> "Those are URLs are truly responding with an error, so short of emulating a full browser with JavaScript [...] there is no way to verify them."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012297.html

**Sebastian Meyer on suppressing the link** (he rejects the `\code{}` workaround):
> "\code{} is formally reserved for R code fragments [...] To disable the hyperlink, you could use \verb{} instead, or \samp{} if you want it single quotes."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012305.html

**Uwe Ligges on geo-blocked hosts:**
> "Anyway, please simply say so in your submission comments or tell me which package we are talking about."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012368.html

**Key details:**
- Maps to: **MISC-02**
- Frequency: **recurring** (3 threads). Bot protection on websites is growing.

---

### 10. linux-arm64 and Sanitizer "Additional Issues" Now Shown in Incoming Pretests

**Packages:**
- akin 0.3.5: pretest showed "Additional issues checked: linux-arm64: Status: 4 WARNINGs, 5 NOTEs"
- DPQ (Martin Maechler; Inf results only on linux/arm64)
- nlme (arm64 bug reproduced on Raspberry Pi)
- clustord (macOS arm64 test mismatch)
- epanet2toolkit (gcc-16 warning)
- graphpcor (gcc-san/clang-san failures from the s2 dependency)
- limSolve (clang-ASAN, scheduled for removal)

**akin pretest email (verbatim excerpts as posted):**
> "Additional issues checked: linux-arm64: Status: 4 WARNINGs, 5 NOTEs Last released version's CRAN status: OK: 13"

> "Check: whether startup messages can be suppressed, Result: NOTE sh: 1: /bin/kstat: not found"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012402.html

Root cause (Krylov): the RcppAlgos dependency detects the OS with `grepl("darwin|solaris", R.version$os)` and falls through to the Solaris `/bin/kstat` command on linux-arm64 (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012405.html).

**limSolve (ASAN):**
- Error: "ERROR: AddressSanitizer: memcpy-param-overlap" (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012424.html)
- Fix: replace overlapping Fortran `xDCOPY` calls with a dedicated move routine (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012430.html)
- Ivan Krylov: "I think this violates the Fortran standard on aliasing between dummy arguments" (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012426.html)

**Simon Urbanek on platform-sensitive tests (clustord):**
> "TL;DR this is not macOS specific - your test example is chaotic and thus will be influenced even by small changes in the precision beyond what is guaranteed, i.e. your assumptions are not generally valid and thus the tests don't work."

> "The arm CPUs used by Macs only support double precision, so any operations that are otherwise preformed with extended precision will be different."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012306.html

**Key details:**
- Maps to: **COMP-11** (sanitizers), **NEW** (arm64 / extended-precision portability; PLAT category)
- Additional-issue flavors now appear in the *incoming* pretest email next to Windows and Debian, and both the new version and the "Last released version's additional issues" are linked.
- Frequency: **recurring** (5+ threads)

---

### 11. Compiler Warnings From Dependency Headers on Windows (Cannot Be Silenced)

**Packages:** SurfaceMesh (new submission, Sep 2026; RcppEigen/RcppCGAL headers on Windows); LABTNSCPSS (systemfonts warnings under clang 21, Feb 2026)

**SurfaceMesh:** `-Wuninitialized` and `-Warray-bounds=` warnings appeared only on Windows (gcc 14.3) and blocked the pretest. The maintainer tried `-Wno-array-bounds -Wno-uninitialized` in Makevars.win and reported: "the check still generates a non-portability warning which means the package will not pass the CRAN pre-test" (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012550.html).

Dirk Eddelbuettel described a policy-compliant way to quiet compilers locally only, by testing for `.git/` (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012553.html). Michael Chirico got an upstream fix proposed in RcppCGAL (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012554.html).

**Policy (rev 6875):** "Packages should not attempt to disable compiler diagnostics, nor to remove other diagnostic information such as symbols in shared objects."

**Key details:**
- Maps to: **NEW** (Compiled code; the policy is not covered as a rule in the KB)
- For LABTNSCPSS, the systemfonts warnings came from a dependency built during install. Michael Chirico advised mentioning upstream issues to CRAN at submission (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012294.html).
- Frequency: **recurring** (2 threads; frequent in general)

---

### 12. install.packages()/library() at Top Level of R/ Files

**Packages:** LABTNSCPSS (Feb-Mar 2026), HDBRR (r-devel, Jun 2026)

LABTNSCPSS had `R/setup_package.R` calling `install.packages()` and `lapply(required_packages, library, character.only = TRUE)` at top level. **Ivan Krylov:**
> "Installing and loading packages by hand in your source code will break when a binary package is built from your source package (among other things)."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012303.html

**Kurt Hornik** on why R CMD check misses this:
> "The check code by default uses tools:::.check_packages_used() on the code in the installed package, and hence cannot pick up top-level calls as these got processed when installing."

He showed that running it on the source directory reports:
> "'library' or 'require' calls in package code: [...] Please use :: or requireNamespace() instead."

He said he is looking into fixing the source-mode checker.

Source: https://stat.ethz.ch/pipermail/r-devel/2026-June/084612.html

**Key details:**
- Maps to: **CODE-13**, **NS-08**
- Novel: a likely future R CMD check change (source-level detection of top-level side-effect calls). R CMD check currently misses top-level calls; a static checker like pedanticran can catch them.
- Frequency: recurring pattern; 2 threads

---

### 13. R 4.6.0 C-API Cut-Over (Non-API Entry Points and Variables)

**Packages:**
- trtswitch: `R_ext/Callbacks.h` not found on macOS
- packages calling `R_MissingArg`
- RStudio and rpy2: `ENCLOS`/`FRAME`/`SET_ENCLOS`
- Rcpp and others: transitional CRAN versions

**R 4.6.0 NEWS (verbatim):**
- "Packages using any non-API variables will now receive check 'NOTE's."
- "The non-API header file 'R_ext/PrtUtil.h' is no longer copied to the installed 'include' directory."
- "Packages using the non-API functions ATTRIB and SET_ATTRIB will now receive check 'NOTE's."
- "R CMD check 'NOTE's on the use of these non-API entry points have been upgraded to 'WARNING's [...]: R_nchar, R_tryWrap, Rf_GetOption, R_lsInternal, BODY, FORMALS, CLOENV, SET_TYPEOF, STRING_PTR, R_duplicate_attr, getConnection, R_data_class, STRING_PTR, SET_OBJECT, ATTRIB, SET_ATTRIB, Rf_findVarInFrame3."
- "R CMD check 'NOTE's on the use of the non-API entry points PRCODE, SET_PRCODE, PRENV, SET_PRENV, PRVALUE, SET_PRVALUE, R_PromiseExpr, and Rf_allocSExp have been upgraded to 'WARNING's"
- "R CMD check now reports further clang warnings including -Wkeyword-macro."

**Luke Tierney (R Core), r-devel:**
> "The installed C header files for R 4.6.0 should now correspond to the C API as defined by the Writing R Extensions manual: All entry points and variables declared in the headers are now part of the API. [...] A small number of packages with significant reverse dependencies have not yet completed the transition. CRAN will be hosting transitional versions for these until their maintainers submit updates."

Source: https://stat.ethz.ch/pipermail/r-devel/2026-April/084486.html

He gave `-DNO_LEGACY_NONAPI` in Makevars as a pre-test switch (https://stat.ethz.ch/pipermail/r-devel/2026-April/084481.html).

**R_MissingArg:** flagged as non-API, then put back by Luke Tierney:
> "You are right: R_MissingArg is needed for this so it should be in the variables API. It is now and should no longer generate a check NOTE."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012341.html

**Callbacks.h (Martin Maechler quoting R-devel NEWS):**
> "The non-API header files R_ext/Callbacks.h and R_ext/PrtUtil.h are no longer copied to the installed includes directory. [...] This new header file should be used in packages instead of R_ext/Callbacks.h."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012246.html

**Key details:**
- Maps to: **COMP-03** (needs an R 4.6.0 refresh), COMP-01/SYS-07 (`-Wkeyword-macro`)
- Connections API: Simon Urbanek, author of the custom connection API, said packages that do not *implement* connections "should not use the internal structures to access the internals of connections" (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012289.html)
- Frequency: **recurring, ecosystem-wide**

---

### 14. Strong Dependencies: Policy Rev 6738 Wording; Suggests Machinery

**Policy text, before (rev 6286):**
> "Packages on which a CRAN package depends should be available from a mainstream repository: if any mentioned in 'Suggests' or 'Enhances' fields are not from such a repository, where to obtain them at a repository should be specified in an 'Additional_repositories' field"

**Policy text, after (rev 6738, mirror commit 2026-02-20; still in rev 6875):**
> "Packages on which a CRAN package depends should be available from a standard repository. The strong dependencies (i.e., packages listed in the 'Depends', 'Imports' or 'LinkingTo' fields) should be available from CRAN or the Bioconductor software repository. If any mentioned in 'Suggests' or 'Enhances' fields are not from one of these or the Bioconductor annotation and experiment data repositories, where to obtain them at a repository should be specified in an [Additional_repositories field]"

Source: https://github.com/eddelbuettel/crp/commit/c6262deb4a

**List discussion:**
- rolog/rswipl (Jun 2026): a package in Suggests got installed on some CRAN machines but not others. Hornik's check server meta-package was updated to include swi-prolog (Krylov, https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012416.html).
- CVXR/Rmosek (Mar 2026): a CRAN *stub* package in Enhances broke reverse-dependency examples (https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012313.html).

**Key details:**
- Maps to: **DEP-01** (strong deps from Bioconductor annotation/experiment repos are no longer covered; they need to be in Suggests with Additional_repositories), DEP-02
- Frequency: policy change (one-off); Suggests issues recurring

---

### 15. Minimum R Version Declarations (gsl R >= 4.5.0 Cascade)

**Packages:** gsl (Depends: R (>= 4.5.0), affecting 200+ reverse dependencies such as copula)

**Simon Urbanek:**
> "Robin may be misunderstanding the purpose of that declaration as he seem to see it as "I didn't test it" while it really means "you're not allowed to install it, it won't work". gsl actually works perfectly fine (i.e. passes all checks with OK) at from R 3.2.0 on, so the declaration is just blatantly wrong - it should read (R >= 3.2.0)."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012357.html

**Simon Urbanek on patch-level requirements:**
> "if the bug affects your use case then you should use 4.1.3 otherwise 4.1.0. Normally, ABI compatibility is guaranteed across all patch versions - hence the comment to make sure the requirement is not unnecessary"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012378.html

**Ivan Krylov:** some declared R versions "(e.g. 3.8, 3.10, 3.10, 3.21, 3.50, 3.60, 3.63) never existed at all" (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012353.html)

**Key details:**
- Maps to: **NEW** (DESCRIPTION; advisory). Not a rejection reason per se.
- Related R 4.6.0 NEWS: `\linkS4class[<pkg>]{...}` "Packages with the new syntax need to formally depend on 'R >= 4.6.0'"
- Frequency: discussion; recurring pattern on CRAN

---

### 16. Reverse-Dependency Breakage From Inserting a Positional Argument

**Package:** unnamed (Alexis Dinno, May 2026). The update got "a cautioning email about a strong first order reverse dependency conflict" (maintainer paraphrase).

**Duncan Murdoch (not CRAN):**
> "If you're adding a new parameter to a function, the safest way to do so is to add it after all the other parameters, and set a default value so the old usage will still produced the same results."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012394.html

Ivan Krylov listed base tools for checking reverse dependencies: `tools::package_dependencies()`, `download.packages()`, `tools::check_packages_in_dir()` (https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012397.html).

**Key details:**
- Maps to: **SUB-03**
- Frequency: one-off on the list; a common cause of CRAN "revdep" holds

---

### 17. Restoring par(): Clarified Scope

**Simon Urbanek:**
> "you have to restore any parameters you set explicitly, which does include mfrow and similar as well."

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012442.html

**Uwe Ligges:**
> "I think Duncan explained i correctly, reset everything but return a list of parameters that need to be set again if you want to, e.g., add to the plot generated with modified parameters"

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012443.html

Simon also clarified that the coordinate-system parameters `usr`, `xaxp` and `yaxp`, set by plot.window, are expected to change and do not need restoring (https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012440.html). A cookbook PR followed: https://github.com/r-devel/cran-cookbook/pull/90

**Key details:**
- Maps to: **CODE-04**
- Frequency: clarification

---

### 18. Workspace Clean-Up in Vignettes (rm(list = ls()))

**Package:** RPointCloud (Feb 2026). The maintainer reports (paraphrase, not CRAN text) that an earlier `rm(list = ls())` at the end of vignettes was removed "after objections from a CRAN reviewer that this process could/would remove things that a user already had in their workspace". Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012279.html

**Key details:**
- Maps to: **CODE-09** (already covered)
- Frequency: recurring known pattern

---

### 19. Rust: Version Requirements Contrary to Policy

**Packages:** string2path (Rust; the package cited as the example in CRAN's own "Using Rust" document), tynding

**Verbatim archive notes:**
> "Archived on 2026-05-15 for repeated policy violation. . On requirement for Rust versions." (string2path)

> "Archived on 2026-04-20 as issues were not corrected in time. . Also has recent 'rustc' requirement contrary to the policy." (tynding)

**"Using Rust in CRAN packages" (rev 6279):**
> "test before submission with at least a two-year-old version of cargo, and preferably one four or more years old."

> "The Linux servers on the CRAN check farm use system versions, and Linux distributions are often slow to update these so version requirements need to be conservative."

**Key details:**
- Maps to: **COMP-09**, which does not currently mention the minimum toolchain-version requirement
- Frequency: **recurring** (2 archivals; "repeated" for string2path)

---

### 20. Using All CPU Cores

**Package:** lavDiag

**Verbatim archive note:**
> "Archived on 2026-05-15 for policy violation. . Attempts to use all CPU cores."

Related: greta's vignette got "Re-building vignettes had CPU time 4.1 times elapsed time" because of threads created inside TensorFlow (Krylov, https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012257.html).

**Key details:**
- Maps to: **CODE-10**, **VIG-07**
- Frequency: recurring

---

### 21. Political Message in Startup Banner

**Package:** rim

**Verbatim archive note:**
> "Archived on 2026-07-28 for policy violation. . Anti-social behaviour, displaying a political message in its banner. Version 0.8.1 has been removed."

**Policy (rev 6875):**
> "Packages should not contain nor display material which might be considered divisive or give offence, such as political slogans."

**Key details:**
- Maps to: **NEW** (no KB rule covers this policy sentence)
- Frequency: one-off

---

### 22. Fixed TCP Ports in Examples

**Package:** shinylight (Sep 2026; "createTcpServer: address already in use: 50050" in the last released version's results)

**Ivan Krylov:**
> "In general, no fixed port number can be assumed to be available on the machine running R CMD check."

He recommended catching the server-start failure with a classed condition.

Source: https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012559.html

**Key details:**
- Maps to: **NET-01** (network-adjacent graceful failure)
- Frequency: one-off

---

## Archival Statistics (Feb-Sep 2026, from PACKAGES.in X-CRAN-Comment)

These are packages whose *current* comment records an archival dated 2026-02-01..2026-09-30. Packages archived and later unarchived in the window are not counted, so these are lower bounds. 975 archival entries were classified by keyword:

| Reason (verbatim stem) | Count |
|---|---|
| "as email to the maintainer is undeliverable" | 405 |
| "as issues were not corrected despite reminders" / "in time" | 373 |
| "as requires archived package(s) ..." | 121 |
| "at the maintainer's request" / maintainer does not wish to support | 43 |
| "for (repeated) policy violation" | 29 (Internet access 25, ~/.cache/R 2, CPU cores 1, political banner 1; string2path's Rust note counted under policy) |
| other (e.g. "issues were re-introduced in update", moved to Bioconductor) | 4 |

By month: Feb 77, Mar 194, Apr 179, May 271, Jun 93, Jul 61, Aug 32, Sep 68.

---

## CRAN Infrastructure Events (2026)

| Date | Event | Source |
|------|-------|--------|
| Feb 10-12 | macOS r-devel switched from big-sur to sonoma builds; stale logs and spurious "Installation failed" (Hornik: "my fault, I had added x86_64 where I should have added arm64") | https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012258.html |
| Mar 9-11 | Win-builder msys environment corrupted by a package ("Only Win32 target is supported!"). Ligges: "Some package was apparently able to run an update for the msys environment (which must not happen)." | https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012317.html |
| Mar 12-14 | R Bugzilla returns HTTP 418 to URL checkers during a DDoS | https://stat.ethz.ch/pipermail/r-package-devel/2026q1/012320.html |
| Apr 1-2 | CRAN submissions down (email failure) | https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012346.html |
| Apr 24 | R 4.6.0 released (C++20 default; C++11/14 removed; C-API cut-over) | r-devel announcement |
| May 1-2 | Downtime: svn, winbuilder, CRAN incoming checks (Ligges announcement) | https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012374.html |
| Jun 7-8 | Spurious r-devel-linux-x86_64-debian-gcc failures; Ligges: wait, then ask Kurt Hornik | https://stat.ethz.ch/pipermail/r-package-devel/2026q2/012409.html |
| Jun 24 | R 4.6.1 released | r-devel |
| Aug 1-4 | Win-builder "'cc' is not on the path" NOTE in the compiled-code API check; fixed CRAN-side | https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012498.html |
| Aug 2-4 | Debian-gcc: "Found the following files/directories: '~/tmp/scratch/Rtmp...'" on ~100% of packages (Xvfb config) | https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012502.html |
| Aug 5-19 | CRAN submissions closed (summer vacation/maintenance; quoted by Lluís Revilla) | https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012452.html |
| Aug 23 | Ligges: deadline-extension requests "should be sent to CRAN at R-project.org" | https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012519.html |
| Aug 8 | Ligges: outlook.com frequently blocks CRAN/win-builder mail | https://stat.ethz.ch/pipermail/r-package-devel/2026q3/012512.html |

---

## Other R-devel / R Core Changes Relevant to Checks

- **Experimental `_R_CHECK_RD_CONTENTS_VALUE_`** (r89420, Sebastian Meyer): "If set to a true value, the check results will show (some of the) Rd files without \value." Useful for DOC-01 detection parity. https://stat.ethz.ch/pipermail/r-devel/2026-February/084371.html
- **R-devel NEWS:** "tools::texi2pdf() now reports BibTeX warnings; in particular, missing references are now noted by R CMD check when re-building PDF vignettes."
- **R-devel NEWS:** "R CMD build now excludes an obsolete 'data/datalist' file when the package uses 'LazyData', and reports when it added one."
- **R-devel NEWS:** "read.dcf() and write.dcf() now treat DCF files (such as package 'DESCRIPTION' [...]) as UTF-8 [...] non-UTF-8 'DESCRIPTION' files (e.g. those declaring 'Encoding: latin1') are no longer re-encoded on reading." (relevant to ENC-01: `Encoding: latin1` is effectively obsolete)
- **R 4.6.0:** "R CMD check when passed a tarball looks at its contents and so no longer derives the package name from the tarball name"
- **Duplicate packages in Imports/Suggests:** Kurt Hornik found 18 CRAN packages and said "I'll take a look ..." This may become a check (watchlist). https://stat.ethz.ch/pipermail/r-devel/2026-June/084618.html
- **data/*.R scripts that load the package namespace** break vignette-engine detection under R CMD check (Krylov; watchlist). https://stat.ethz.ch/pipermail/r-devel/2026-August/084669.html

---

## Summary of Rejection Categories Found

| Category | Count | Examples |
|----------|-------|----------|
| Internet access / graceful failure | 4 threads + 25 archivals | rerddapUtils, CopernicusMarine, repo.data, kofdata, blscrapeR |
| Maintainer email | ~405 archivals | April-May 2026 wave |
| Filesystem / cache | 1 thread + 2 archivals | rsurvstat, nomesbr, rcldf |
| DESCRIPTION | 3 | Authors@R unsafe calls, gsl R version, saferDev |
| Check/example time | 4 | oce, MBHdesign, integrity, rerddapUtils |
| Documentation (Rd) | 3 | shinylight, causalDisco, Ecfun (lost braces) |
| Compiled code / API | 6 | trtswitch, R_MissingArg, limSolve, SurfaceMesh, s2/graphpcor, epanet2toolkit |
| Platform (arm64/precision) | 4 | akin/RcppAlgos, DPQ, clustord, nlme |
| Dependencies | 4 | rolog, Rmosek/CVXR, LABTNSCPSS, HDBRR |
| Rust toolchain | 2 archivals | string2path, tynding |
| Parallelism | 1 archival + 1 thread | lavDiag, greta |
| Content policy | 1 archival | rim |
| Infrastructure false positives | 8 | see table above |

---

## Novel/Unusual Patterns (Feb 2026 - Sep 2026)

1. **Cache size and management archivals.** `R_user_dir()` is only acceptable if the cache is bounded, cleaned, and never written during R CMD check.
2. **Authors@R evaluation hardening.** A new NOTE whitelists `person`, `c`, `list`, `paste`, `paste0` (plus `as.person`; `personList` was requested), with CITATION files likely next.
3. **278 packages archived for undeliverable email in about two weeks** (30 April to 14 May 2026; 405 over Feb-Sep).
4. **R 4.6.0 headers equal the API.** Non-API variables now get NOTEs, and CRAN shipped transitional versions of key packages.
5. **Additional-issue flavors (linux-arm64, sanitizers) are gating incoming submissions,** including failures caused by dependencies.
6. **Policy rev 6738 names the Bioconductor *software* repository explicitly** for strong dependencies.
7. **Empty-href detection in README.md**, plus README.md now installed and shown in HTML help.
8. **"Political message in banner" archival**, enforcing an existing but rarely cited policy sentence.

---

## Proposed Knowledge Base Changes

### (a) Updates to Existing Rules

**NET-01 (Must Fail Gracefully When Resources Are Unavailable)**
- Add "CRAN says":
  - `Archived on <date> for policy violation. On Internet access.`
  - `Archived on <date> for repeated policy violation. On Internet access.`
  - Uwe Ligges, 2026-05-18: "Simply define a timeout for internet access and exit gracefully if you hit it."
- Append to Fix: "Set explicit timeouts (e.g. `httr2::req_timeout()`, `options(timeout = )` scoped with on.exit) and treat timeouts as failures to handle gracefully. Slow remote servers otherwise surface as example-timing NOTEs on CRAN's European check machines. Failures inside dependencies you call (e.g. GDAL/stars remote reads) are your responsibility: 'In the end it is your responsibility since you are providing the API' (Simon Urbanek, 2026-02-18). Do not assume fixed TCP ports are free; catch server-start errors."
- Append to Since: "2026: Internet access was the reason for 25 of 29 policy-violation archivals Feb-Sep 2026; repeat offenders are archived for 'repeated policy violation'."

**CODE-06 (Write Only to tempdir())**
- Append to Rule: "`tools::R_user_dir()` caches must be small by default and actively pruned, and must not be created or modified during R CMD check (examples, tests, vignettes). R CMD check reports 'checking for new files in some other directories ... NOTE Found the following files/directories: ~/.cache/<pkg>/...'."
- Add "CRAN says": `Archived on 2026-06-01 for policy violation. Stores > 100 MB in ~/.cache/R and does not clean up.`
- Append to Detection: "Flag `R_user_dir(` usage without (a) a size cap/pruning routine and (b) a check-time guard (e.g. defaulting to `tempdir()` when `!interactive()` or when `_R_CHECK_PACKAGE_NAME_` is set)."

**SIZE-02 (Check Time Must Be < 10 Minutes)**
- Add "CRAN says": `Flavor: r-devel-windows-x86_64 / Check: Overall checktime, Result: NOTE / Overall checktime 25 min > 10 min`
- Append to Rule: "The binding measurement is the r-devel-windows-x86_64 incoming pretest, which is slower than Linux. The NOTE causes automatic pretest rejection. CRAN can manually overrule it for large packages ('That's why CRAN overruled the 10 min threshold and let your package pass.', Uwe Ligges, 2026-07-14). Installation time alone (~1 minute) is 'perfectly fine'. If CRAN has not replied after 2 weeks, send a reminder."
- Severity: keep REJECTION.

**DOC-03 (Examples Must Be Fast)**
- Add "CRAN says": `checking examples ... NOTE / Examples with CPU (user + system) or elapsed time > 5s`
- Append to Rule: "Elapsed (wall-clock) time counts, so network waits trip the NOTE. No special allowance is made for algorithmically slow 'workflow' examples."

**COMP-03 (Non-API Entry Points)**
- Replace Rule with: "R 4.6.0 (April 2026): installed headers now declare only the API. Non-API *variables* now give NOTEs. ATTRIB/SET_ATTRIB give NOTEs. NOTEs were upgraded to WARNINGs for R_nchar, R_tryWrap, Rf_GetOption, R_lsInternal, BODY, FORMALS, CLOENV, SET_TYPEOF, STRING_PTR, R_duplicate_attr, getConnection, R_data_class, SET_OBJECT, Rf_findVarInFrame3, PRCODE, SET_PRCODE, PRENV, SET_PRENV, PRVALUE, SET_PRVALUE, R_PromiseExpr, Rf_allocSExp. Removed or hidden: LOGICAL0/INTEGER0/REAL0/COMPLEX0/RAW0 declarations, Rf_isFrame, VECTOR_PTR, DATAPTR declaration, ENCLOS/FRAME/HASHTAB family, SETLENGTH, TRUELENGTH, NAMED, OBJECT, IS_S4_OBJECT etc. Headers R_ext/Callbacks.h and R_ext/PrtUtil.h are no longer installed (use R_ext/ObjectTable.h). R_MissingArg was re-added to the API (Luke Tierney, 2026-03-29). Packages not implementing new connection types must not use Rconnection internals."
- Append to Detection: "grep src/ for the WARNING list above, `#include <R_ext/Callbacks.h>`, `R_NamespaceRegistry`, `->UTF8out`/`R_GetConnection(` outside connection implementations."
- Append to Fix: "Test with `PKG_CPPFLAGS += -DNO_LEGACY_NONAPI` on R-devel. Use R_getVar/R_getVarEx, R_mapAttrib/R_getAttributes, R_getRegisteredNamespace, and the binding API (R_GetBindingType etc.)."

**COMP-09 (Rust Package Requirements)**
- Append to Rule: "Minimum cargo/rustc version requirements must be conservative: test with a cargo at least two (preferably four or more) years old. CRAN's Linux check servers use distribution rustc. Limit `cargo build -j` to 1 or 2."
- Add "CRAN says":
  - `Archived on 2026-05-15 for repeated policy violation. On requirement for Rust versions.` (string2path)
  - `Also has recent 'rustc' requirement contrary to the policy.` (tynding)
- Append to Detection: "Parse `rust-version`/`edition` in Cargo.toml and version checks in configure. Flag MSRV newer than ~2 years before submission date and edition = 2024."

**CODE-10 (Maximum 2 Cores)**
- Add "CRAN says": `Archived on 2026-05-15 for policy violation. Attempts to use all CPU cores.`
- Append to Detection: "Flag threads spawned by embedded runtimes (TensorFlow/reticulate, OpenMP, BLAS) in vignettes. greta's vignette showed 'Re-building vignettes had CPU time 4.1 times elapsed time' from TensorFlow threads (Feb 2026)."

**EMAIL-05 (Institutional Email Longevity Warning)**
- Add "CRAN says": `Archived on 2026-05-04 as email to the maintainer is undeliverable.`
- Append to Rule: "Feb-Sep 2026: about 405 packages were archived for undeliverable maintainer email, 278 of them between 2026-04-30 and 2026-05-14. This was the single largest archival reason in that window."
- Consider raising Severity from NOTE to WARNING for heuristic output, since the consequence is archival.

**DEP-01 (Strong Dependencies Must Be on CRAN or Bioconductor)**
- Replace "CRAN says" / add the policy quote (rev 6738+): "The strong dependencies (i.e., packages listed in the 'Depends', 'Imports' or 'LinkingTo' fields) should be available from CRAN or the Bioconductor software repository. If any mentioned in 'Suggests' or 'Enhances' fields are not from one of these or the Bioconductor annotation and experiment data repositories, where to obtain them at a repository should be specified in an 'Additional_repositories' field."
- Append to Detection: "Strong dependencies that exist only in Bioconductor annotation/experiment-data repos are violations (Suggests-only)."
- Since: "Policy wording tightened in rev 6738 (mirrored 2026-02-20)."

**MISC-02 (URLs Must Be Valid)**
- Add "CRAN says": `Found the following (possibly) invalid URLs: URL: From: README.md Message: Empty URL`
- Append to Detection: "Flag `href=\"\"`/`[]()` empty links in README.md, NEWS.md and vignettes (R 4.6.0 installs README.md into HTML help)."
- Append to Fix: "For sites behind bot protection (Cloudflare 403) or geo-blocking, avoid `\url{}` and use `\verb{}` or `\samp{}` (not `\code{}`, per Sebastian Meyer, 2026-03-03), or explain in submission comments ('please simply say so in your submission comments', Uwe Ligges, 2026-04-16)."

**CODE-04 (Restore options()/par()/setwd())**
- Append to Rule: "Restore every graphics parameter you set explicitly, including mfrow/mfcol/oma ('you have to restore any parameters you set explicitly, which does include mfrow and similar as well', Simon Urbanek, 2026-07-09). Coordinate parameters set by plot.window (usr, xaxp, yaxp) are expected to change. If users need to add to a multi-panel plot, return the needed settings (Uwe Ligges: 'reset everything but return a list of parameters that need to be set again')."
- Append to Fix: "Save only what you change: `op <- par(mfrow = c(1, 2)); on.exit(par(op), add = TRUE)`."

**NS-08 (No library()/require() in Package Code)** and **CODE-13 (No Installing Packages in Functions)**
- Append to Detection (both): "Scan *top-level* (non-assignment) calls in R/*.R, e.g. `library()`, `require()`, `install.packages()`, `options()`, or `lapply(pkgs, library, ...)`. R CMD check analyses the installed namespace, so these run at install time and evade its checks (Kurt Hornik, r-devel 2026-06-19). Hornik is working on source-level detection."
- Add "CRAN says" to NS-08: "'library' or 'require' calls in package code: [...] Please use :: or requireNamespace() instead." (`tools:::.check_packages_used(dir=)` output)

**SUB-03 (Check Reverse Dependencies)**
- Append to Fix: "Add new function arguments at the end with defaults. Inserting a positional argument breaks reverse dependencies that call positionally, and CRAN emails about strong reverse-dependency conflicts. Base-R tooling: `tools::package_dependencies(reverse = TRUE, which = 'most')`, `utils::download.packages()`, `tools::check_packages_in_dir()`."

**SUB-07 (CRAN Vacation Periods)**
- Append to Rule: "Summer closure too: 2026-08-05 to 2026-08-19. Deadline-extension requests during closures go to CRAN@R-project.org (Uwe Ligges, 2026-08-23), not the list."

**SUB-06 (Submission Frequency Limit)**
- Add "CRAN says": `CRAN incoming feasibility, Result: NOTE ... Number of updates in past 6 months: 7` (akin, May 2026 pretest)

**COMP-11 (Sanitizer Compliance)**
- Append to Rule: "Additional-issue results (ASAN/UBSAN, gcc-san/clang-san, valgrind, linux-arm64) are now reported in incoming pretest emails and can block acceptance. Overlapping Fortran array arguments (e.g. BLAS-style DCOPY on overlapping slices of the same array) trigger 'AddressSanitizer: memcpy-param-overlap' under flang/clang and violate Fortran aliasing rules (limSolve, scheduled for removal Jun 2026)."
- Append to Detection: "Flag Fortran calls passing two slices of the same array to a copy routine (`CALL xDCOPY(N, X(J+1), 1, X(J), 1)` pattern)."

**DOC-01 (Every Exported Function Must Have @return)**
- Append to Detection: "Parity with R-devel's experimental `_R_CHECK_RD_CONTENTS_VALUE_=true` (r89420, Feb 2026), which lists Rd files without \value."

**ENC-01 (Missing Encoding Field)**
- Append: "R-devel (post-4.6) reads DESCRIPTION as UTF-8 regardless of `Encoding:`. `Encoding: latin1` DESCRIPTION files are no longer re-encoded, so use UTF-8."

### (b) Proposed NEW Rules

**DESC-16: Authors@R Must Use Only Whitelisted Calls**
- **Severity**: NOTE (check), and an ERROR in R CMD build/INSTALL from a source directory on R-devel/R-4-6-branch
- **Rule**: `Authors@R` may only contain calls to `person`, `c`, `list`, `paste`, `paste0` (`as.person` was whitelisted later). Anything else, typically `comment(ORCID = ...)` or `ORCID = ...` inside `person()`, is flagged as possibly unsafe.
- **CRAN says**: "checking DESCRIPTION meta-information ... NOTE / Malformed Authors@R field: / Found the following possibly unsafe calls: / comment("SwissMarbledWhite") / Please only use calls to 'person', 'c', 'list', 'paste', 'paste0'." (Kurt Hornik, r-devel, 2026-04-11)
- **Detection**: Parse `Authors@R` with `parse()` (do not eval). Walk the call tree and flag any function name outside {person, c, list, paste, paste0, as.person}. Specifically flag `comment(` and a named `ORCID =` argument to `person()`.
- **Fix**: Use `person("First", "Last", email = "...", role = c("aut", "cre"), comment = c(ORCID = "0000-..."))`. Replace `personList()` with `c()`.
- **Files**: `DESCRIPTION`
- **Since**: R-devel r89866 (2026-04-10), merged into R-4-6-branch

**CODE-23: User Cache Must Be Bounded and Untouched by R CMD check**
- **Severity**: REJECTION (archival "for policy violation")
- **Rule**: Files under `tools::R_user_dir()` (e.g. `~/.cache/R/<pkg>`) must be small by default, actively pruned, and not created during examples, tests or vignettes run by R CMD check.
- **CRAN says**: "Archived on 2026-06-01 for policy violation. Stores > 100 MB in ~/.cache/R and does not clean up." / "checking for new files in some other directories ... NOTE Found the following files/directories: '~/.cache/<pkg>/...'"
- **Detection**: Find `R_user_dir(`, `rappdirs::user_cache_dir(`, and literal `~/.cache`. Flag if (a) there is no pruning or max-size logic (no `unlink`/`file.remove` on the cache dir, no age or size check), or (b) the cache path is used by default in examples/tests/vignettes without redirecting to `tempdir()`.
- **Fix**: Add a cache-size cap and expiry. Provide `pkg_cache_clear()`. In examples/tests set an option/env var pointing the cache to `tempdir()`, or skip caching when `!interactive()`. Declare `Depends: R (>= 4.0)` if using R_user_dir.
- **Files**: `R/*.R`, `tests/**`, `vignettes/*`, `man/*.Rd`
- **Since**: Policy wording since R 4.0 era. First size-based archivals 2026-06-01.

**DOC-12: \arguments Requires a Matching \usage**
- **Severity**: NOTE (blocks pretest)
- **Rule**: An Rd file that documents `\arguments` must have a `\usage` section. Entries in `\usage` that parse as R calls must correspond to real functions with matching arguments. Overview pages and non-R (e.g. JavaScript) docs should use `\describe{}` instead of `\arguments{}`.
- **CRAN says**: "Rd files without \usage: [...] \arguments should not be documented without \usage." and "you should really add the usage line, a usage line does not mean these are executed." (Uwe Ligges, 2026-09-28)
- **Detection**: For each man/*.Rd, flag `\arguments{` present and `\usage{` absent. In roxygen, flag blocks documenting `NULL` or `"_PACKAGE"`-style topics that have `@param` but no `@usage`.
- **Fix**: Add `#' @usage fn(x, ...)`, or remove `@param` tags and describe arguments in `@details`/`\describe{}`.
- **Files**: `man/*.Rd`, `R/*.R`
- **Since**: Long-standing tools::checkRdContents behaviour; R 4.6.0 extended related checkDocFiles notes; seen twice Jul-Sep 2026

**NS-09: No ::: Calls to the Package's Own Namespace**
- **Severity**: NOTE (treated as blocking for new submissions)
- **Rule**: Package code should not use `pkg:::fn` to call its own internal objects.
- **CRAN says**: "There are ::: calls to the package's namespace in its code. A package almost never needs to use ::: for its own objects:"
- **Detection**: Read Package from DESCRIPTION. Grep R/*.R for `<Package>:::`.
- **Fix**: Call internal functions directly by name. Within-package code sees all namespace objects.
- **Files**: `R/*.R`
- **Since**: Long-standing R CMD check NOTE; observed blocking saferDev 1.0.0 (May 2026)

**COMP-13: Do Not Suppress Compiler Diagnostics; Fix Warnings From Headers You Use**
- **Severity**: WARNING → REJECTION
- **Rule**: "Significant" compiler warnings at install time (e.g. -Wuninitialized, -Warray-bounds from included headers such as Eigen/CGAL on Windows gcc) fail the pretest. Disabling them with `-Wno-*` flags or pragmas violates policy and is itself flagged as non-portable.
- **CRAN says**: Policy: "Packages should not attempt to disable compiler diagnostics, nor to remove other diagnostic information such as symbols in shared objects."
- **Detection**: Grep src/Makevars* for `-Wno-`, `-w\b`, `-fpermissive`. Grep src/ for `#pragma (GCC|clang) diagnostic ignored`.
- **Fix**: Fix the code, or update or patch the upstream header package (e.g. newer RcppEigen/RcppCGAL). If the warning comes from a dependency compiled during check, note it in submission comments. Local-only quieting is acceptable if conditioned on a developer-only signal (e.g. presence of `.git/`).
- **Files**: `src/Makevars`, `src/Makevars.win`, `src/*`
- **Since**: Long-standing policy; recurring 2026 (SurfaceMesh Sep 2026)

**PLAT-03: Code and Tests Must Not Depend on Extended Precision or OS-String Sniffing**
- **Severity**: WARNING → REJECTION (via linux-arm64 / macOS arm64 additional checks)
- **Rule**: Tests must not assert results that depend on long-double precision, or on chaotic or non-converged algorithm output. arm64 has no extended precision. OS detection must not assume "not darwin" means Solaris or Linux-x86.
- **CRAN says**: "Additional issues checked: linux-arm64: Status: 4 WARNINGs, 5 NOTEs" (pretest email); Simon Urbanek: "your test example is chaotic and thus will be influenced even by small changes in the precision beyond what is guaranteed"
- **Detection**: Flag `expect_equal`/`identical` on floating-point results with `tolerance = 0` or tiny tolerances. Flag `R.version$os` / `Sys.info()["sysname"]` regex branches that fall through to `system("/bin/kstat ...")` or other platform-specific commands without an else-error.
- **Fix**: Use tolerances. Test deterministic components on saved fixtures. Test with `R --disable-long-double` builds or arm64 CI (`ubuntu-24.04-arm` runners, QEMU `--platform linux/arm64`). Use `.Platform`/`Sys.info()` with explicit cases.
- **Files**: `tests/**`, `R/*.R`
- **Since**: 2026, as linux-arm64 additional checks appear in incoming pretests

**CODE-24: No Divisive or Political Content in Startup Messages or Package Material**
- **Severity**: REJECTION (archival "for policy violation")
- **Rule**: Package startup banners, messages and documentation must not contain material "which might be considered divisive or give offence, such as political slogans."
- **CRAN says**: "Archived on 2026-07-28 for policy violation. Anti-social behaviour, displaying a political message in its banner. Version 0.8.1 has been removed."
- **Detection**: Inspect `.onAttach`/`.onLoad` `packageStartupMessage()` strings for non-package content (heuristic keyword list; manual review flag).
- **Fix**: Restrict startup messages to package-relevant information, and keep them suppressible.
- **Files**: `R/zzz.R`, `R/*.R`
- **Since**: Policy sentence present in rev 6875; enforced by archival 2026-07-28

**DESC-17: Declare an Honest Minimum R Version (No Unnecessary Patch-Level or Inflated Requirements)**
- **Severity**: RECOMMENDED
- **Rule**: `Depends: R (>= x.y.z)` means "will not work below this". It is not "untested below this". Do not inflate it, since it cascades to every reverse dependency. Avoid a non-zero patch level unless a patch release fixed a bug you rely on. Never declare versions that do not exist (e.g. 3.60).
- **CRAN says**: Simon Urbanek, 2026-04-11: "it really means "you're not allowed to install it, it won't work". gsl actually works perfectly fine [...] from R 3.2.0 on, so the declaration is just blatantly wrong". WRE: do not depend on a patch level other than zero.
- **Detection**: Parse `Depends: R (>= ...)`. Flag a non-existent version, a patch level != 0 (NOTE on R < 4.3.3 per thread), or a version newer than r-oldrel without an obvious trigger (e.g. use of `\linkS4class[pkg]`, `%notin%` or `|>`, which do justify specific minimums).
- **Fix**: Set the lowest version where checks pass. Use `#if R_VERSION >= R_Version(x,y,0)` in C code instead of bumping R.
- **Files**: `DESCRIPTION`
- **Since**: WRE guidance long-standing; gsl R >= 4.5.0 cascade discussed Apr 2026

**VIG-09: PDF Vignettes Must Have No Missing BibTeX References** (watch; R-devel only)
- **Severity**: NOTE (R-devel, post-4.6.1)
- **Rule**: R CMD check re-building PDF vignettes now reports BibTeX warnings, including missing references.
- **CRAN says**: R-devel NEWS: "tools::texi2pdf() now reports BibTeX warnings; in particular, missing references are now noted by R CMD check when re-building PDF vignettes."
- **Detection**: For Sweave/LaTeX vignettes, extract `\cite{key}` keys and compare them with the keys in the `.bib` files referenced by `\bibliography{}`.
- **Fix**: Add the missing entries or fix the keys.
- **Files**: `vignettes/*.Rnw`, `vignettes/*.bib`
- **Since**: R-devel 2026 (expected R 4.7.0)

**Count of proposals:** 19 existing rule IDs to update (NET-01, CODE-06, SIZE-02, DOC-03, COMP-03, COMP-09, CODE-10, EMAIL-05, DEP-01, MISC-02, CODE-04, NS-08, CODE-13, SUB-03, SUB-07, SUB-06, COMP-11, DOC-01, ENC-01) and **9 new rules** (DESC-16, CODE-23, DOC-12, NS-09, COMP-13, PLAT-03, CODE-24, DESC-17, VIG-09).

**Watchlist (not yet rules):** duplicate packages in Imports/Suggests (Hornik investigating); CITATION call whitelisting (Hornik: "the harder part"); `data/*.R` scripts that load their own namespace; source-level detection of top-level side-effect calls in R/.
