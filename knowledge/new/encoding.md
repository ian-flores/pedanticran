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
