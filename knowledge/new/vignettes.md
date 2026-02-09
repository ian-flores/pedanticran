## Category: Vignettes

### VIG-01: VignetteBuilder Not Declared in DESCRIPTION

- **Severity**: REJECTION
- **Rule**: If the package has vignette source files in `vignettes/` using a non-Sweave engine (knitr, rmarkdown, quarto), the DESCRIPTION must declare `VignetteBuilder`. For `knitr::rmarkdown` vignettes, both knitr AND rmarkdown must be in `VignetteBuilder` and listed in Suggests (or Imports).
- **CRAN says**: "Package has 'vignettes' subdirectory but apparently no vignettes. Perhaps the 'VignetteBuilder' information is missing from the DESCRIPTION file?"
- **Detection**: Parse DESCRIPTION for `VignetteBuilder` field. Scan `vignettes/*.Rmd` and `vignettes/*.Rnw` for `%\VignetteEngine{...}` declarations. If vignettes use `knitr::rmarkdown`, verify both `knitr` and `rmarkdown` appear in VignetteBuilder and in Suggests/Imports. If vignettes exist but no VignetteBuilder is declared, flag.
- **Fix**: Add `VignetteBuilder: knitr` (or `knitr, rmarkdown`) to DESCRIPTION. Add both packages to Suggests.
- **Files**: `DESCRIPTION`, `vignettes/*.Rmd`, `vignettes/*.Rnw`

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
