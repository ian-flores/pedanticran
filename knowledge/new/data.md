# CRAN Submission Rules — Data

Rules for datasets shipped in R packages: documentation, format, size, compression, and configuration.

Sources: CRAN Repository Policy, Writing R Extensions (Chapter 1.1.6 — Data in packages), R Packages (2e) Chapter 7 — Data, R CMD check documentation, CRAN mailing list rejections (2023–2025).

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
