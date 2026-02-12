#!/usr/bin/env python3
"""Pedantic CRAN Check — Static analysis for CRAN submission readiness.

Encodes CRAN policy rules as automated checks that run without R.
Catches the pedantic issues that R CMD check misses.

Usage:
    python check.py --path /path/to/package [--severity warning] [--fail-on error]
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path


# --- Data structures ---

@dataclass
class Finding:
    rule_id: str
    severity: str  # "error", "warning", "note"
    title: str
    message: str
    file: str = ""
    line: int = 0
    cran_says: str = ""


# --- Title case logic ---

TITLE_CASE_LOWERCASE = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "in", "on", "at",
    "to", "by", "of", "with", "from", "as", "into", "onto", "upon", "vs",
    "via", "per",
}


def check_title_case(title: str) -> list[str]:
    """Check if title follows Title Case rules. Returns list of problems."""
    problems = []
    # Strip quoted names for checking
    stripped = re.sub(r"'[^']*'", "QUOTED", title)
    words = stripped.split()
    for i, word in enumerate(words):
        if word == "QUOTED" or word.isupper():  # Skip quoted names and acronyms
            continue
        if i == 0:  # First word must be capitalized
            if word[0].islower():
                problems.append(f"First word '{word}' should be capitalized")
        elif word.lower() in TITLE_CASE_LOWERCASE:
            if word[0].isupper():
                problems.append(f"'{word}' should be lowercase (article/preposition)")
        else:
            if word[0].islower() and not word.startswith("e.g"):
                problems.append(f"'{word}' should be capitalized in Title Case")
    return problems


# --- Known software/package names ---

KNOWN_SOFTWARE = {
    "python", "java", "javascript", "typescript", "c++", "rust", "go", "julia",
    "fortran", "matlab", "scala", "ruby", "perl", "php", "swift", "kotlin",
    "tensorflow", "pytorch", "keras", "openssl", "ffmpeg", "docker", "kubernetes",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "apache", "nginx",
    "git", "github", "jags", "stan", "bugs", "winbugs", "openbugs", "spark",
    "hadoop", "gdal", "geos", "proj", "grass", "qgis", "whisper", "gpt", "bert",
    "xgboost", "lightgbm", "catboost", "praat", "pandoc", "latex", "bibtex",
    "cmake", "make", "gcc", "clang", "llvm",
}


def find_unquoted_software(text: str) -> list[str]:
    """Find software names in text that aren't in single quotes."""
    unquoted = []
    # Remove already-quoted names
    cleaned = re.sub(r"'[^']*'", "", text)
    for name in KNOWN_SOFTWARE:
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, cleaned, re.IGNORECASE):
            unquoted.append(name)
    return unquoted


# --- DESCRIPTION parser ---

def parse_description(path: Path) -> dict:
    """Parse DESCRIPTION file into a dict of fields."""
    desc_file = path / "DESCRIPTION"
    if not desc_file.exists():
        return {}
    fields = {}
    current_key = None
    current_value = []
    for line in desc_file.read_text(encoding="utf-8", errors="replace").splitlines():
        # DESCRIPTION fields start with a key followed by colon
        # Authors@R is a special case — the @ is part of the field name
        m = re.match(r'^([A-Za-z][A-Za-z0-9_.@]+)\s*:', line)
        if m and not line.startswith((" ", "\t")):
            if current_key:
                fields[current_key] = " ".join(current_value).strip()
            current_key = m.group(1)
            current_value = [line[m.end():].strip()]
        elif current_key and line.startswith((" ", "\t")):
            current_value.append(line.strip())
        elif line.strip() == "":
            if current_key:
                fields[current_key] = " ".join(current_value).strip()
                current_key = None
                current_value = []
    if current_key:
        fields[current_key] = " ".join(current_value).strip()
    return fields


# --- File scanners ---

def find_r_files(path: Path) -> list[Path]:
    """Find all .R files in R/ directory."""
    r_dir = path / "R"
    if not r_dir.is_dir():
        return []
    return sorted(r_dir.glob("*.R"))


def find_rd_files(path: Path) -> list[Path]:
    """Find all .Rd files in man/ directory."""
    man_dir = path / "man"
    if not man_dir.is_dir():
        return []
    return sorted(man_dir.glob("*.Rd"))


def find_src_files(path: Path) -> list[Path]:
    """Find C/C++/Fortran files in src/ directory."""
    src_dir = path / "src"
    if not src_dir.is_dir():
        return []
    exts = ("*.c", "*.cpp", "*.cc", "*.h", "*.hpp", "*.f", "*.f90", "*.f95")
    files = []
    for ext in exts:
        files.extend(src_dir.glob(ext))
    return sorted(files)


def scan_file(filepath: Path, pattern: str, flags: int = 0) -> list[tuple[int, str]]:
    """Scan a file for regex matches. Returns [(line_num, line_text), ...]."""
    matches = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return matches
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line, flags):
            matches.append((i, line.strip()))
    return matches


def is_in_comment(line: str) -> bool:
    """Check if the significant part of a line is in a comment."""
    stripped = line.strip()
    return stripped.startswith("#")


def _function_nesting_depth(filepath: Path, target_line: int) -> int:
    """Count how many function() scopes enclose a given line number (1-indexed).

    Returns 0 if at top level, 1 if inside one function, 2+ if inside a closure.
    Used to distinguish <<- in closures (depth >= 2, modifies parent scope)
    from <<- at function top level (depth <= 1, may modify global env).
    """
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return 0

    # Track function openings via a stack of brace depths
    func_starts: list[int] = []  # brace depths where function bodies started
    brace_depth = 0

    for i, line in enumerate(lines, 1):
        if i >= target_line:
            break
        # Detect scope-creating constructs: function(), quo(), local(), etc.
        # In R, <<- inside any of these targets the enclosing scope, not global
        if re.search(r'\b(?:function\s*\(|quo\s*\(\s*\{|local\s*\(\s*\{)', line):
            func_starts.append(brace_depth)
        for ch in line:
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
                # If we've closed back to where a function started, pop it
                while func_starts and brace_depth <= func_starts[-1]:
                    func_starts.pop()

    return len(func_starts)


def _find_function_body_ranges(filepath: Path, patterns: list[str]) -> list[tuple[int, int]]:
    """Find line ranges of function bodies matching given definition patterns.

    Returns [(start_line, end_line), ...] where line numbers are 1-indexed.
    """
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []

    combined = re.compile('|'.join(patterns))
    ranges = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if combined.search(line):
            # Found a function definition — find its closing brace
            start = i + 1  # 1-indexed
            brace_depth = 0
            found_open = False
            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == '{':
                        brace_depth += 1
                        found_open = True
                    elif ch == '}':
                        brace_depth -= 1
                if found_open and brace_depth <= 0:
                    ranges.append((start, j + 1))
                    i = j + 1
                    break
            else:
                i += 1
        else:
            i += 1

    return ranges


# Patterns for print/format/summary S3 methods and R6 print methods
_PRINT_METHOD_PATTERNS = [
    r'^\s*print\.\w+\s*(<-|=)\s*function',       # print.foo <- function
    r'^\s*format\.\w+\s*(<-|=)\s*function',       # format.foo <- function
    r'^\s*summary\.\w+\s*(<-|=)\s*function',      # summary.foo <- function
    r'^\s*str\.\w+\s*(<-|=)\s*function',           # str.foo <- function
    r'^\s*show\s*(<-|=)\s*function',               # show <- function (S4)
    r'^\s*print\s*=\s*function',                   # print = function (R6/RefClass)
    r'^\s*format\s*=\s*function',                  # format = function (R6/RefClass)
]

# Patterns for display/rendering helper functions where cat() is legitimate
_DISPLAY_HELPER_PATTERNS = [
    r'^\s*cat_\w+\s*(<-|=)\s*function',           # cat_line, cat_bullet, cat_rule
    r'^\s*show_\w+\s*(<-|=)\s*function',           # show_regroups, show_query
    r'^\s*display_\w+\s*(<-|=)\s*function',        # display_results, display_header
    r'^\s*render_\w+\s*(<-|=)\s*function',         # render_line, render_output
    r'^\s*draw_\w+\s*(<-|=)\s*function',           # draw_bar, draw_progress
    r'^\s*print_\w+\s*(<-|=)\s*function',          # print_header, print_line
    r'^\s*format_\w+\s*(<-|=)\s*function',         # format_line, format_output
]


def find_print_method_ranges(filepath: Path) -> list[tuple[int, int]]:
    """Find line ranges of print/format/summary S3 methods and R6 print methods."""
    return _find_function_body_ranges(filepath, _PRINT_METHOD_PATTERNS)


def find_display_helper_ranges(filepath: Path) -> list[tuple[int, int]]:
    """Find line ranges of display/rendering helper functions."""
    return _find_function_body_ranges(filepath, _DISPLAY_HELPER_PATTERNS)


# --- Encoding helpers ---

def _has_non_ascii_bytes(filepath: Path) -> list[tuple[int, str]]:
    """Return [(line_num, line_text), ...] for lines containing non-ASCII bytes."""
    results = []
    try:
        raw = filepath.read_bytes()
    except Exception:
        return results
    for i, line in enumerate(raw.split(b'\n'), 1):
        if any(b > 0x7F for b in line):
            text = line.decode('utf-8', errors='replace').strip()
            results.append((i, text))
    return results


def _has_bom(filepath: Path) -> bool:
    """Check if file starts with UTF-8 BOM (EF BB BF)."""
    try:
        with open(filepath, 'rb') as f:
            return f.read(3) == b'\xef\xbb\xbf'
    except Exception:
        return False


def _find_vignette_files(path: Path) -> list[Path]:
    """Find vignette source files in vignettes/ directory."""
    vig_dir = path / "vignettes"
    if not vig_dir.is_dir():
        return []
    files = []
    for ext in ("*.Rmd", "*.Rnw", "*.Rtex", "*.rmd", "*.rnw", "*.qmd"):
        files.extend(vig_dir.glob(ext))
    return sorted(files)


# --- Vignette helpers ---

def parse_vignette_metadata(filepath: Path) -> dict:
    """Extract %\\Vignette* metadata from a vignette file."""
    metadata = {"engine": None, "index_entry": None, "encoding": None, "depends": None}
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return metadata
    for i, line in enumerate(text.splitlines(), 1):
        m = re.search(r'%\\VignetteEngine\{([^}]+)\}', line)
        if m:
            metadata["engine"] = (i, m.group(1).strip())
        m = re.search(r'%\\VignetteIndexEntry\{([^}]+)\}', line)
        if m:
            metadata["index_entry"] = (i, m.group(1).strip())
        m = re.search(r'%\\VignetteEncoding\{([^}]+)\}', line)
        if m:
            metadata["encoding"] = (i, m.group(1).strip())
        m = re.search(r'%\\VignetteDepends\{([^}]+)\}', line)
        if m:
            metadata["depends"] = (i, m.group(1).strip())
    return metadata


def extract_packages_from_vignette(filepath: Path) -> set[str]:
    """Extract package names used in vignette R code chunks."""
    packages = set()
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return packages
    in_chunk = False
    for line in text.splitlines():
        if re.match(r'^```\{r', line):
            in_chunk = True
            continue
        if in_chunk and line.strip().startswith('```'):
            in_chunk = False
            continue
        if in_chunk:
            for m in re.finditer(r'\b(?:library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', line):
                packages.add(m.group(1))
            for m in re.finditer(r'\b(\w+):::\w+|\b(\w+)::\w+', line):
                pkg = m.group(1) or m.group(2)
                packages.add(pkg)
    if filepath.suffix.lower() == '.rnw':
        in_chunk = False
        for line in text.splitlines():
            if re.match(r'^<<.*>>=', line):
                in_chunk = True
                continue
            if in_chunk and line.strip() == '@':
                in_chunk = False
                continue
            if in_chunk:
                for m in re.finditer(r'\b(?:library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', line):
                    packages.add(m.group(1))
                for m in re.finditer(r'\b(\w+):::\w+|\b(\w+)::\w+', line):
                    pkg = m.group(1) or m.group(2)
                    packages.add(pkg)
    return packages


def parse_desc_packages(desc: dict) -> set[str]:
    """Extract all declared package names from DESCRIPTION Imports + Suggests + Depends."""
    packages = set()
    for field_name in ("Imports", "Suggests", "Depends"):
        raw = desc.get(field_name, "")
        if raw:
            for entry in raw.split(","):
                pkg = entry.strip().split("(")[0].strip()
                if pkg and pkg != "R":
                    packages.add(pkg)
    return packages


def get_vignette_output_format(filepath: Path) -> list[tuple[int, str]]:
    """Check vignette YAML for output format declarations."""
    formats = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return formats
    in_yaml = False
    for i, line in enumerate(text.splitlines(), 1):
        if i == 1 and line.strip() == '---':
            in_yaml = True
            continue
        if in_yaml and line.strip() == '---':
            break
        if in_yaml:
            m = re.match(r'\s*output\s*:\s*(\S+)', line)
            if m:
                formats.append((i, m.group(1)))
            m = re.match(r'\s+(html_document|rmarkdown::html_document)\s*:', line)
            if m and not formats:
                formats.append((i, m.group(1)))
    return formats


# --- NAMESPACE helpers ---

KNOWN_S3_GENERICS = {
    "print", "summary", "format", "plot", "str", "as.data.frame",
    "as.list", "as.character", "as.numeric", "as.integer", "as.logical",
    "as.double", "as.complex", "as.vector", "as.matrix", "as.array",
    "c", "t", "dim", "dimnames", "length", "names", "levels",
    "merge", "subset", "transform", "within", "with",
    "Math", "Ops", "Summary", "Complex",
    "predict", "residuals", "fitted", "coef", "confint", "vcov",
    "logLik", "AIC", "BIC", "deviance", "nobs",
    "update", "anova", "model.matrix", "model.frame",
    "head", "tail", "rev", "sort", "order", "unique", "duplicated",
    "cbind", "rbind", "rep", "seq", "range", "diff", "cumsum",
    "mean", "median", "quantile", "var", "sd",
    "is.na", "is.finite", "is.infinite", "is.nan",
    "toString", "toJSON", "knit_print",
}


def parse_namespace(path: Path) -> dict:
    """Parse NAMESPACE file into structured data."""
    ns_file = path / "NAMESPACE"
    result = {
        "imports": [], "import_from": [], "exports": [],
        "export_patterns": [], "s3methods": [], "raw_lines": [],
    }
    if not ns_file.exists():
        return result
    try:
        text = ns_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return result
    result["raw_lines"] = text.splitlines()
    joined = _join_continuation_lines(text)
    for line_num, line in joined:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'import\s*\(\s*([^,)]+)', line)
        if m and not line.startswith("importFrom"):
            pkg = m.group(1).strip().strip('"').strip("'")
            result["imports"].append((pkg, line_num))
            continue
        m = re.match(r'importFrom\s*\((.+)\)', line)
        if m:
            args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
            if len(args) >= 2:
                pkg = args[0]
                for fun in args[1:]:
                    fun = fun.strip()
                    if fun:
                        result["import_from"].append((pkg, fun, line_num))
            continue
        m = re.match(r'export\s*\((.+)\)', line)
        if m and not line.startswith("exportPattern"):
            funs = [f.strip().strip('"').strip("'") for f in m.group(1).split(",")]
            for fun in funs:
                if fun:
                    result["exports"].append((fun, line_num))
            continue
        m = re.match(r'exportPattern\s*\(\s*"([^"]*)"\s*\)', line)
        if not m:
            m = re.match(r"exportPattern\s*\(\s*'([^']*)'\s*\)", line)
        if m:
            result["export_patterns"].append((m.group(1), line_num))
            continue
        m = re.match(r'S3method\s*\((.+)\)', line)
        if m:
            args = [a.strip().strip('"').strip("'") for a in m.group(1).split(",")]
            if len(args) >= 2:
                result["s3methods"].append((args[0], args[1], line_num))
            continue
    return result


def _join_continuation_lines(text: str) -> list[tuple[int, str]]:
    """Join multi-line NAMESPACE directives into single logical lines."""
    lines = text.splitlines()
    result = []
    current = ""
    start_line = 0
    paren_depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if paren_depth == 0:
                result.append((i + 1, stripped))
                continue
        if paren_depth == 0:
            current = stripped
            start_line = i + 1
        else:
            current += " " + stripped
        paren_depth += stripped.count("(") - stripped.count(")")
        if paren_depth <= 0:
            result.append((start_line, current))
            current = ""
            paren_depth = 0
    if current:
        result.append((start_line, current))
    return result


def parse_description_depends(desc: dict) -> list[str]:
    """Extract package names from the Depends field of DESCRIPTION."""
    depends_str = desc.get("Depends", "")
    if not depends_str:
        return []
    packages = []
    for item in depends_str.split(","):
        item = item.strip()
        pkg_name = re.sub(r'\s*\(.*\)', '', item).strip()
        if pkg_name:
            packages.append(pkg_name)
    return packages


# --- Data helpers ---

_DATA_BASE_EXTS = {".rda", ".rdata", ".r", ".tab", ".txt", ".csv"}
_COMPRESSION_EXTS = {".gz", ".bz2", ".xz"}


def _dataset_names_from_data_dir(data_dir: Path) -> list[tuple[str, Path]]:
    """Extract (dataset_name, file_path) for each .rda/.RData in data/."""
    datasets = []
    for f in sorted(data_dir.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() in (".rda", ".rdata"):
            datasets.append((f.stem, f))
    return datasets


def _find_documented_datasets_rd(man_dir: Path) -> set[str]:
    """Find dataset names documented in man/*.Rd via \\alias{}."""
    documented = set()
    if not man_dir.is_dir():
        return documented
    for rd in sorted(man_dir.glob("*.Rd")):
        try:
            text = rd.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r"\\alias\{([^}]+)\}", text):
            documented.add(m.group(1))
    return documented


def _find_documented_datasets_roxygen(r_dir: Path) -> set[str]:
    """Find dataset names documented via roxygen in R/*.R."""
    documented = set()
    if not r_dir.is_dir():
        return documented
    for rf in sorted(r_dir.glob("*.R")):
        try:
            text = rf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        in_roxygen = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#'"):
                in_roxygen = True
                m = re.search(r"@(?:name|rdname)\s+(\S+)", stripped)
                if m:
                    documented.add(m.group(1))
            else:
                if in_roxygen:
                    m = re.match(r'^["\']([^"\']+)["\']', stripped)
                    if m:
                        documented.add(m.group(1))
                in_roxygen = False
    return documented


def _is_valid_data_extension(filepath: Path) -> bool:
    """Check if a file has a valid extension for the data/ directory."""
    name = filepath.name.lower()
    for comp in _COMPRESSION_EXTS:
        if name.endswith(comp):
            name = name[: -len(comp)]
            break
    suffix = Path(name).suffix.lower()
    return suffix in _DATA_BASE_EXTS


# --- System requirements helpers ---

SYSTEM_LIBRARY_HEADERS = {
    "curl/curl.h": "libcurl", "libxml/parser.h": "libxml2",
    "libxml/tree.h": "libxml2", "libxml/xpath.h": "libxml2",
    "openssl/ssl.h": "OpenSSL", "openssl/evp.h": "OpenSSL",
    "openssl/sha.h": "OpenSSL", "openssl/rsa.h": "OpenSSL",
    "zlib.h": "zlib", "png.h": "libpng", "jpeglib.h": "libjpeg",
    "gdal.h": "GDAL", "ogr_api.h": "GDAL", "cpl_conv.h": "GDAL",
    "geos_c.h": "GEOS", "proj.h": "PROJ", "proj_api.h": "PROJ",
    "fftw3.h": "FFTW", "gsl/gsl_math.h": "GSL", "gsl/gsl_rng.h": "GSL",
    "gsl/gsl_vector.h": "GSL", "gsl/gsl_matrix.h": "GSL",
    "hdf5.h": "HDF5", "netcdf.h": "netCDF", "sqlite3.h": "SQLite",
    "pcre2.h": "PCRE2", "lzma.h": "liblzma", "bzlib.h": "bzip2",
    "tiff.h": "libtiff", "tiffio.h": "libtiff",
    "cairo.h": "cairo", "cairo/cairo.h": "cairo",
    "mpfr.h": "MPFR", "gmp.h": "GMP", "glpk.h": "GLPK",
    "udunits2.h": "udunits2",
    "poppler/cpp/poppler-document.h": "poppler",
    "magic.h": "libmagic", "archive.h": "libarchive",
    "sodium.h": "libsodium", "git2.h": "libgit2",
    "yaml.h": "libyaml", "zmq.h": "libzmq", "re2/re2.h": "RE2",
    "mysql/mysql.h": "MySQL", "libpq-fe.h": "PostgreSQL",
    "mariadb/mysql.h": "MariaDB", "librdf.h": "Redland",
    "raptor2/raptor2.h": "Raptor2", "rasqal/rasqal.h": "Rasqal",
    "freetype/freetype.h": "FreeType", "ft2build.h": "FreeType",
    "Imlib2.h": "Imlib2", "avformat.h": "FFmpeg",
    "libavformat/avformat.h": "FFmpeg",
    "tesseract/baseapi.h": "Tesseract",
    "leptonica/allheaders.h": "Leptonica",
    "alsa/asoundlib.h": "ALSA", "pulse/simple.h": "PulseAudio",
    "v8.h": "V8",
}

CXX_STANDARD_MAP = {
    "CXX11": "C++11", "CXX14": "C++14", "CXX17": "C++17",
    "CXX20": "C++20", "CXX23": "C++23",
    "C++11": "C++11", "C++14": "C++14", "C++17": "C++17",
    "C++20": "C++20", "C++23": "C++23",
}


def _find_src_includes(path: Path) -> dict[str, list[tuple[str, int]]]:
    """Scan src/ for #include directives matching known system library headers."""
    src_dir = path / "src"
    if not src_dir.is_dir():
        return {}
    found: dict[str, list[tuple[str, int]]] = {}
    for ext in ("*.c", "*.cpp", "*.cc", "*.h", "*.hpp"):
        for f in src_dir.glob(ext):
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            rel = str(f.relative_to(path))
            for i, line in enumerate(lines, 1):
                m = re.match(r'\s*#\s*include\s*[<"]([^>"]+)[>"]', line)
                if m:
                    header = m.group(1)
                    if header in SYSTEM_LIBRARY_HEADERS:
                        lib = SYSTEM_LIBRARY_HEADERS[header]
                        found.setdefault(lib, []).append((rel, i))
    return found


def _parse_makevars_cxx_std(path: Path) -> list[tuple[str, str, int]]:
    """Parse CXX_STD from Makevars files."""
    results = []
    for name in ["src/Makevars", "src/Makevars.win"]:
        makevars = path / name
        if not makevars.exists():
            continue
        try:
            lines = makevars.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            m = re.match(r'\s*CXX_STD\s*=\s*(CXX\d+)\b', line.strip())
            if m:
                raw = m.group(1)
                normalized = CXX_STANDARD_MAP.get(raw, raw)
                results.append((normalized, name, i))
    return results


def _parse_sysreqs_cxx_standard(desc: dict) -> str | None:
    """Extract C++ standard from SystemRequirements field."""
    sysreqs = desc.get("SystemRequirements", "")
    m = re.search(r'C\+\+(\d+)', sysreqs)
    if m:
        return f"C++{m.group(1)}"
    return None


# --- Email helpers ---

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "guerrillamail.de",
    "tempmail.com", "throwaway.email", "yopmail.com", "sharklasers.com",
    "guerrillamailblock.com", "grr.la", "dispostable.com",
    "10minutemail.com", "trashmail.com", "trashmail.net", "trashmail.org",
    "maildrop.cc", "mailnesia.com", "temp-mail.org", "tempail.com",
    "tempr.email", "discard.email", "fakeinbox.com", "mailcatch.com",
    "mintemail.com", "mohmal.com", "mytemp.email", "getairmail.com",
    "getnada.com", "harakirimail.com", "mailexpire.com",
    "spamgourmet.com", "mailnator.com", "binkmail.com", "bobmail.info",
    "chammy.info", "devnullmail.com", "letthemeatspam.com",
    "mailmoat.com", "spamfree24.org", "trash-mail.com", "trashymail.com",
    "yopmail.fr", "tempmailaddress.com", "burnermail.io",
    "inboxkitten.com", "emailondeck.com", "guerrillamail.info",
    "guerrillamail.net", "tempinbox.com", "mailtemp.org",
}

MAILING_LIST_DOMAINS = {
    "googlegroups.com", "groups.io", "lists.r-forge.r-project.org",
    "lists.sourceforge.net", "lists.debian.org", "lists.gnu.org",
    "lists.fedoraproject.org", "lists.ubuntu.com", "lists.apache.org",
    "freelists.org", "listserv.uga.edu",
}

MAILING_LIST_LOCAL_PREFIXES = {
    "info", "admin", "support", "contact", "help", "office", "team",
}

MAILING_LIST_LOCAL_KEYWORDS = {
    "lists", "list", "devel", "dev-team", "team", "group",
    "announce", "discuss", "users", "-dev", "-devel", "-users", "-announce",
}

NOREPLY_PATTERNS = [
    r"^noreply@", r"^no-reply@", r"^donotreply@", r"^do-not-reply@",
    r"^notifications@github\.com$", r"@users\.noreply\.github\.com$",
    r"^bot@", r"^ci@", r"^automation@", r"^automated@",
    r"^mailer-daemon@", r"^postmaster@",
]

PLACEHOLDER_DOMAINS = {
    "example.com", "example.org", "example.net", "test.com",
    "domain.com", "email.com", "mail.com", "your-domain.com",
    "yourdomain.com", "placeholder.com",
}

PLACEHOLDER_PATTERNS = [
    r"^your\.?email@", r"^first\.?last@", r"^name@", r"^user@",
    r"^maintainer@", r"^author@", r"^package@", r"^foo@", r"^bar@",
    r"^test@", r"^todo@", r"^changeme@", r"^replace\.?me@", r"^xxx@",
]

ACADEMIC_DOMAIN_PATTERNS = [
    r"\.edu$", r"\.ac\.uk$", r"\.ac\.jp$", r"\.ac\.at$", r"\.ac\.be$",
    r"\.ac\.kr$", r"\.ac\.nz$", r"\.ac\.za$", r"\.ac\.in$", r"\.ac\.il$",
    r"\.ac\.cn$", r"\.edu\.au$", r"\.edu\.cn$", r"\.edu\.tw$",
    r"\.edu\.hk$", r"\.edu\.sg$", r"\.edu\.br$", r"\.edu\.mx$",
    r"\.edu\.pl$", r"\.edu\.tr$", r"\.edu\.co$", r"\.edu\.ar$",
    r"(?:^|\.)uni-[a-z]+\.de$", r"(?:^|\.)tu-[a-z]+\.de$",
    r"(?:^|\.)fu-berlin\.de$", r"(?:^|\.)hu-berlin\.de$",
    r"(?:^|\.)rwth-aachen\.de$",
    r"(?:^|\.)u-[a-z]+\.fr$", r"(?:^|\.)univ-[a-z]+\.fr$",
]


def _extract_email_from_person_block(block: str) -> str | None:
    """Extract email from a person() block, handling both named and positional args.

    R's person() signature: person(given, family, middle, email, role, comment, ...)
    Email can appear as:
      - Named:      email = "addr@domain"
      - Positional:  person("First", "Last", , "addr@domain", role = ...)
    """
    # Try named argument first
    email_match = re.search(r'email\s*=\s*["\']([^"\']+)["\']', block)
    if email_match:
        return email_match.group(1).strip()
    # Fall back to any quoted string containing @ (positional email)
    for m in re.finditer(r'["\']([^"\']+@[^"\']+)["\']', block):
        candidate = m.group(1)
        # Skip ORCID URLs and other non-email strings
        if '/' not in candidate and ' ' not in candidate:
            return candidate.strip()
    return None


def extract_cre_email(authors_r: str) -> str | None:
    """Extract the maintainer (cre) email from Authors@R field."""
    person_blocks = re.findall(
        r'person\s*\((?:[^()]*|\((?:[^()]*|\([^()]*\))*\))*\)',
        authors_r, re.DOTALL,
    )
    for block in person_blocks:
        if '"cre"' in block or "'cre'" in block:
            email = _extract_email_from_person_block(block)
            if email:
                return email
    return None


def _has_cre_without_email(authors_r: str) -> bool:
    """Check if there is a person with cre role but no email argument."""
    person_blocks = re.findall(
        r'person\s*\((?:[^()]*|\((?:[^()]*|\([^()]*\))*\))*\)',
        authors_r, re.DOTALL,
    )
    for block in person_blocks:
        if '"cre"' in block or "'cre'" in block:
            email = _extract_email_from_person_block(block)
            if not email:
                return True
    return False


# --- inst/ helpers ---

HIDDEN_FILE_PATTERNS = {
    ".DS_Store", ".gitkeep", ".gitignore", "Thumbs.db", "desktop.ini",
    ".Rhistory", ".RData", ".Rapp.history",
}

RESERVED_INST_DIRS = {
    "R", "data", "demo", "exec", "libs", "man", "help", "html", "Meta",
}

THIRD_PARTY_DIRS = {
    "htmlwidgets", "www", "include", "js", "css", "lib",
}

DEPRECATED_CITATION_PATTERNS = {
    "citEntry": r'\bcitEntry\s*\(',
    "personList": r'\bpersonList\s*\(',
    "as.personList": r'\bas\.personList\s*\(',
    "citHeader": r'\bcitHeader\s*\(',
    "citFooter": r'\bcitFooter\s*\(',
}

VIGNETTE_SOURCE_EXTS = {".Rmd", ".Rnw", ".Rtex"}
VIGNETTE_OUTPUT_EXTS = {".html", ".pdf"}

SUBDIR_SIZE_THRESHOLD = 1 * 1024 * 1024
LARGE_FILE_THRESHOLD = 500 * 1024


# --- Check implementations ---

def check_description_fields(path: Path, desc: dict) -> list[Finding]:
    """Check DESCRIPTION file for policy violations."""
    findings = []
    desc_file = str(path / "DESCRIPTION")

    # DESC-01: Title Case
    title = desc.get("Title", "")
    if title:
        problems = check_title_case(title)
        if problems:
            findings.append(Finding(
                rule_id="DESC-01", severity="error",
                title="Title not in Title Case",
                message=f"Title Case issues: {'; '.join(problems)}",
                file=desc_file,
                cran_says="Title must be in Title Case."
            ))

    # DESC-02: Single quotes around software names
    for field_name in ("Title", "Description"):
        text = desc.get(field_name, "")
        unquoted = find_unquoted_software(text)
        if unquoted:
            findings.append(Finding(
                rule_id="DESC-02", severity="error",
                title=f"Unquoted software names in {field_name}",
                message=f"These names need single quotes in {field_name}: {', '.join(unquoted)}",
                file=desc_file,
                cran_says="Please always write package names, software names and API names in single quotes."
            ))

    # DESC-03: No "for R" in Title
    if title and re.search(r'\b(for|in|with)\s+R\b', title):
        findings.append(Finding(
            rule_id="DESC-03", severity="error",
            title='Title contains redundant "for R"',
            message='Remove "for R", "in R", or "with R" from Title — it\'s on CRAN, so it\'s obviously for R.',
            file=desc_file,
            cran_says="Do not include 'for R' in the Title."
        ))

    # DESC-04: Description opening
    description = desc.get("Description", "")
    pkg_name = desc.get("Package", "")
    if description:
        lower_desc = description.lower()
        if lower_desc.startswith(("a package", "this package", "the package")):
            findings.append(Finding(
                rule_id="DESC-04", severity="error",
                title='Description starts with "A package..."',
                message='Description must not start with "A package...", "This package...", or the package name.',
                file=desc_file,
                cran_says="Do not start Description with the package name, title, or 'A package...'"
            ))
        elif pkg_name and lower_desc.startswith(pkg_name.lower()):
            findings.append(Finding(
                rule_id="DESC-04", severity="error",
                title="Description starts with package name",
                message=f"Description starts with '{pkg_name}'. Rephrase to describe functionality directly.",
                file=desc_file,
            ))

    # DESC-05: Description length (2+ sentences)
    if description:
        sentences = re.split(r'(?<=[.!?])\s+', description)
        if len(sentences) < 2:
            findings.append(Finding(
                rule_id="DESC-05", severity="error",
                title="Description is too short",
                message=f"Description has {len(sentences)} sentence(s). CRAN requires at least 2 complete sentences.",
                file=desc_file,
                cran_says="Description must be a paragraph of 2+ complete sentences."
            ))

    # DESC-06: DOI formatting
    if description:
        if re.search(r'doi:\s+', description):
            findings.append(Finding(
                rule_id="DESC-06", severity="error",
                title="Space after doi: in reference",
                message="DOI must have no space after colon: <doi:10.xxxx/yyyy> not <doi: 10.xxxx/yyyy>",
                file=desc_file,
                cran_says="No space after 'doi:' and angle brackets for auto-linking."
            ))

    # DESC-07: Unexplained acronyms
    common_acronyms = {
        "API", "URL", "HTTP", "HTTPS", "SQL", "CSV", "JSON", "XML", "HTML",
        "PDF", "GUI", "CLI", "IDE", "OS", "IO", "UI", "ID", "URI", "SSL",
        "TLS", "SSH", "FTP", "DNS", "TCP", "UDP", "IP", "CPU", "GPU", "RAM",
        "HPC", "AWS", "GCP", "REST", "CRAN", "ORCID", "DOI", "ISBN", "ISSN",
    }
    if description:
        acronyms = set(re.findall(r'\b[A-Z]{2,}\b', description))
        unexplained = acronyms - common_acronyms
        if unexplained:
            findings.append(Finding(
                rule_id="DESC-07", severity="warning",
                title="Possibly unexplained acronyms",
                message=f"These acronyms may need explanation: {', '.join(sorted(unexplained))}",
                file=desc_file,
                cran_says="Please always explain all acronyms in the description text."
            ))

    # DESC-08: Authors@R field
    if "Authors@R" not in desc:
        if "Author" in desc or "Maintainer" in desc:
            findings.append(Finding(
                rule_id="DESC-08", severity="error",
                title="Missing Authors@R field",
                message="Using deprecated Author/Maintainer fields. Must use Authors@R with person() entries.",
                file=desc_file,
                cran_says="No Authors@R field in DESCRIPTION. Please add one."
            ))

    # DESC-09: Copyright holder (cph)
    authors_r = desc.get("Authors@R", "")
    if authors_r and '"cph"' not in authors_r and "'cph'" not in authors_r:
        findings.append(Finding(
            rule_id="DESC-09", severity="error",
            title="Missing copyright holder (cph) role",
            message="No person with 'cph' role in Authors@R. At least one copyright holder is required.",
            file=desc_file,
            cran_says="Please add a copyright holder."
        ))

    # DESC-10: Unnecessary + file LICENSE
    license_field = desc.get("License", "")
    if "+ file LICENSE" in license_field:
        base_license = license_field.split("+")[0].strip()
        no_file_needed = {"GPL-2", "GPL-3", "LGPL-2.1", "LGPL-3", "Apache-2.0", "Artistic-2.0"}
        if base_license in no_file_needed:
            findings.append(Finding(
                rule_id="DESC-10", severity="error",
                title="Unnecessary + file LICENSE",
                message=f"License '{base_license}' does not need '+ file LICENSE'. Remove it.",
                file=desc_file,
                cran_says="We do not need '+ file LICENSE' and the file as these are part of R."
            ))

    # DESC-11: Single maintainer
    if authors_r:
        cre_count = len(re.findall(r'"cre"', authors_r))
        if cre_count == 0:
            findings.append(Finding(
                rule_id="DESC-11", severity="error",
                title="No maintainer (cre) in Authors@R",
                message="Exactly one person must have the 'cre' role.",
                file=desc_file,
            ))
        elif cre_count > 1:
            findings.append(Finding(
                rule_id="DESC-11", severity="error",
                title="Multiple maintainers (cre) in Authors@R",
                message=f"Found {cre_count} 'cre' roles. Exactly one is required.",
                file=desc_file,
            ))

    # DESC-12: Development version
    version = desc.get("Version", "")
    if ".9000" in version or ".9999" in version:
        findings.append(Finding(
            rule_id="DESC-12", severity="error",
            title="Development version number",
            message=f"Version '{version}' is a development version. CRAN requires a release version (e.g., 0.1.0).",
            file=desc_file,
        ))

    # DESC-13: Stale Date field
    date_field = desc.get("Date", "")
    if date_field:
        try:
            d = datetime.date.fromisoformat(date_field.strip())
            age = (datetime.date.today() - d).days
            if age > 30:
                findings.append(Finding(
                    rule_id="DESC-13", severity="warning",
                    title="DESCRIPTION Date field is stale",
                    message=f"Date field is '{date_field}' ({age} days old). Update or remove it before submission.",
                    file=desc_file,
                    cran_says="The Date field is over a month old."
                ))
        except ValueError:
            pass

    # DESC-14: Version component size
    version = desc.get("Version", "")
    if version:
        for component in version.split("."):
            try:
                if int(component) > 9000:
                    findings.append(Finding(
                        rule_id="DESC-14", severity="note",
                        title="Large version component",
                        message=f"Version '{version}' has a component > 9000, which triggers a NOTE.",
                        file=desc_file,
                    ))
                    break
            except ValueError:
                pass

    # DESC-15: Smart/curly quotes in DESCRIPTION
    desc_file_path = path / "DESCRIPTION"
    if desc_file_path.exists():
        desc_text = desc_file_path.read_text(encoding="utf-8", errors="replace")
        smart_quotes = re.findall(r'[\u2018\u2019\u201C\u201D]', desc_text)
        if smart_quotes:
            findings.append(Finding(
                rule_id="DESC-15", severity="error",
                title="Smart/curly quotes in DESCRIPTION",
                message=f"Found {len(smart_quotes)} smart quote character(s). Use straight ASCII quotes only.",
                file=desc_file,
                cran_says="Non-ASCII characters in DESCRIPTION."
            ))

    # CODE-17: UseLTO causes CPU time NOTE
    if "UseLTO" in desc:
        findings.append(Finding(
            rule_id="CODE-17", severity="note",
            title="UseLTO field in DESCRIPTION",
            message="UseLTO triggers parallel compilation, causing 'Installation took CPU time X times elapsed time' NOTE. Remove unless absolutely needed.",
            file=desc_file,
            cran_says="Installation took CPU time 3.5 times elapsed time"
        ))

    # License validity (basic check)
    valid_licenses = {
        "GPL-2", "GPL-3", "GPL (>= 2)", "GPL (>= 3)",
        "LGPL-2.1", "LGPL-3", "LGPL (>= 2.1)", "LGPL (>= 3)",
        "MIT + file LICENSE", "BSD_2_clause + file LICENSE", "BSD_3_clause + file LICENSE",
        "Apache License 2.0", "Apache-2.0", "Artistic-2.0",
        "CC BY 4.0", "CC BY-SA 4.0", "CC0",
        "Unlimited",
    }
    if license_field:
        # Check for placeholder text
        if "use_" in license_field.lower() or "pick a" in license_field.lower():
            findings.append(Finding(
                rule_id="LIC-01", severity="error",
                title="License is a placeholder",
                message=f"License field contains template text: '{license_field[:60]}...'",
                file=desc_file,
                cran_says="License must be from CRAN's accepted license database."
            ))

    return findings


def check_code(path: Path, desc: dict | None = None) -> list[Finding]:
    """Check R source files for CRAN policy violations."""
    if desc is None:
        desc = {}
    findings = []
    r_files = find_r_files(path)

    for rf in r_files:
        rel = str(rf.relative_to(path))

        # CODE-01: T/F instead of TRUE/FALSE
        # Match T or F as standalone logical values (not in comments/strings)
        for lnum, line in scan_file(rf, r'(?<![A-Za-z_.])(?:=|,|\()\s*[TF]\s*(?:[,)}\]]|$)'):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-01", severity="error",
                    title="T/F instead of TRUE/FALSE",
                    message=f"Use TRUE/FALSE, not T/F: `{line[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Please write TRUE and FALSE instead of T and F."
                ))

        # CODE-02: print()/cat() for messages (skip print/format methods and comments)
        print_method_ranges = find_print_method_ranges(rf)
        display_helper_ranges = find_display_helper_ranges(rf)
        for lnum, line in scan_file(rf, r'\b(?:print|cat)\s*\('):
            if is_in_comment(line):
                continue
            # Skip print/format S3 method definitions
            if re.match(r'^\s*(?:print|format|summary|str)\.\w+', line):
                continue
            # Skip UseMethod dispatchers
            if "UseMethod" in line:
                continue
            # Skip R6/RefClass $print() and $format() method calls
            if re.search(r'\$\s*(?:print|format)\s*\(', line):
                continue
            # Skip if inside a print/format/summary method body
            if any(start <= lnum <= end for start, end in print_method_ranges):
                continue
            # Skip if inside a display/rendering helper (cat_line, show_*, etc.)
            if any(start <= lnum <= end for start, end in display_helper_ranges):
                continue
            # Skip if guarded by verbose or interactive() — CRAN allows these
            if re.search(r'if\s*\(\s*(?:verbose|interactive\s*\(\s*\))', line):
                continue
            findings.append(Finding(
                rule_id="CODE-02", severity="warning",
                title="print()/cat() used (should be message())",
                message=f"Consider message() instead: `{line[:80]}`",
                file=rel, line=lnum,
                cran_says="Instead of print()/cat() rather use message()/warning()/stop()."
            ))

        # CODE-03: set.seed() in function bodies
        for lnum, line in scan_file(rf, r'\bset\.seed\s*\('):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-03", severity="error",
                    title="set.seed() in function code",
                    message=f"Do not hardcode seeds in functions: `{line[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Please do not set a specific seed within a function."
                ))

        # CODE-04: options/par/setwd without on.exit
        # Simplified: flag any options()/par()/setwd() call
        for lnum, line in scan_file(rf, r'\b(?:options|par|setwd)\s*\('):
            if is_in_comment(line):
                continue
            if "on.exit" in line or "on.exit" in (scan_file(rf, r'on\.exit') and ""):
                continue  # Rough heuristic
            findings.append(Finding(
                rule_id="CODE-04", severity="warning",
                title="options()/par()/setwd() — check on.exit()",
                message=f"Ensure this is restored with on.exit(): `{line[:80]}`",
                file=rel, line=lnum,
                cran_says="Please ensure with an immediate call of on.exit() that the settings are reset."
            ))

        # CODE-05: options(warn = -1)
        for lnum, line in scan_file(rf, r'options\s*\(\s*warn\s*=\s*-\s*1'):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-05", severity="error",
                    title="options(warn = -1) is always rejected",
                    message="Use suppressWarnings() instead. Even with on.exit() restoration, this is rejected.",
                    file=rel, line=lnum,
                    cran_says="You are setting options(warn=-1). This is not allowed."
                ))

        # CODE-06: Writing to non-tempdir paths
        for lnum, line in scan_file(rf, r'\bgetwd\s*\(\s*\)'):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-06", severity="error",
                    title="getwd() used in file path",
                    message=f"Do not write to getwd(). Use tempdir(): `{line[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Please ensure functions do not write in the user's home filespace including getwd()."
                ))

        # CODE-08: installed.packages()
        for lnum, line in scan_file(rf, r'\binstalled\.packages\s*\('):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-08", severity="error",
                    title="installed.packages() is forbidden",
                    message="Use requireNamespace() or find.package() instead.",
                    file=rel, line=lnum,
                    cran_says="installed.packages() can be very slow. Do not use."
                ))

        # CODE-09: Global environment modification
        # <<- inside closures (depth >= 2) is standard R — modifies parent scope, not global
        for lnum, line in scan_file(rf, r'<<-'):
            if not is_in_comment(line):
                depth = _function_nesting_depth(rf, lnum)
                if depth >= 2:
                    continue  # Inside a closure — modifies enclosing function scope, not global
                findings.append(Finding(
                    rule_id="CODE-09", severity="warning",
                    title="<<- modifies parent/global environment",
                    message=f"Avoid <<- in package code: `{line[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Please do not modify the global environment."
                ))

        for lnum, line in scan_file(rf, r'rm\s*\(\s*list\s*=\s*ls\s*\('):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-09", severity="error",
                    title="rm(list = ls()) clears global environment",
                    message="This is prohibited in examples, vignettes, and demos.",
                    file=rel, line=lnum,
                ))

        # CODE-11: q() / quit()
        for lnum, line in scan_file(rf, r'\bq\s*\(\s*\)|\bquit\s*\('):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-11", severity="error",
                    title="q()/quit() terminates R session",
                    message="Use stop() to signal errors, not q()/quit().",
                    file=rel, line=lnum,
                ))

        # CODE-12: ::: to base packages
        base_pkgs = {"base", "utils", "stats", "methods", "grDevices", "graphics", "tools", "compiler", "datasets"}
        for lnum, line in scan_file(rf, r'(\w+):::'):
            if not is_in_comment(line):
                m = re.search(r'(\w+):::', line)
                if m and m.group(1) in base_pkgs:
                    findings.append(Finding(
                        rule_id="CODE-12", severity="error",
                        title=f"::: access to internal {m.group(1)} function",
                        message="Must not use ::: to access unexported objects from base packages.",
                        file=rel, line=lnum,
                    ))

        # CODE-13: install.packages() in code
        for lnum, line in scan_file(rf, r'\binstall\.packages\s*\('):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-13", severity="error",
                    title="install.packages() in package code",
                    message="Do not install packages in functions, examples, or vignettes.",
                    file=rel, line=lnum,
                    cran_says="Please do not install packages in your functions."
                ))

        # CODE-15: browser() calls
        for lnum, line in scan_file(rf, r'\bbrowser\s*\('):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-15", severity="error",
                    title="browser() statement in package code",
                    message="Remove browser() calls before submission.",
                    file=rel, line=lnum,
                    cran_says="R CMD check flags browser() under --as-cran."
                ))

        # CODE-07: Clean up temporary files
        # Find tempfile()/tempdir() calls not accompanied by unlink()/on.exit() in the same function
        for lnum, line in scan_file(rf, r'\btempfile\s*\(|\btempdir\s*\('):
            if is_in_comment(line):
                continue
            # Read the full file to check if unlink/on.exit/withr::local_tempfile is nearby
            try:
                full_text = rf.read_text(encoding="utf-8", errors="replace")
            except Exception:
                full_text = ""
            has_cleanup = bool(
                re.search(r'\bunlink\s*\(', full_text)
                or re.search(r'\bon\.exit\s*\(', full_text)
                or re.search(r'\bfile\.remove\s*\(', full_text)
                or re.search(r'\bwithr::local_tempfile\b', full_text)
                or re.search(r'\bwithr::local_tempdir\b', full_text)
            )
            if not has_cleanup:
                findings.append(Finding(
                    rule_id="CODE-07", severity="warning",
                    title="Temporary files may not be cleaned up",
                    message=f"tempfile()/tempdir() used without unlink()/on.exit() cleanup: `{line[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Found the following files/directories: detritus"
                ))
                break  # One finding per file is enough

        # CODE-10: Maximum 2 cores
        parallel_patterns = [
            (r'\bdetectCores\s*\(', 'detectCores()'),
            (r'\bparallel::detectCores\s*\(', 'parallel::detectCores()'),
            (r'\bmakeCluster\s*\(', 'makeCluster()'),
            (r'\bmclapply\s*\(', 'mclapply()'),
            (r'\bmcparallel\s*\(', 'mcparallel()'),
        ]
        try:
            full_text_10 = rf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            full_text_10 = ""
        # Check if there's a min(..., 2) capping pattern in the file
        has_core_cap = bool(
            re.search(r'\bmin\s*\(.*,\s*2\s*\)', full_text_10)
            or re.search(r'\bmin\s*\(\s*2\s*,', full_text_10)
            or re.search(r'getOption\s*\(\s*["\']mc\.cores["\']', full_text_10)
        )
        for pattern, name in parallel_patterns:
            for lnum, line in scan_file(rf, pattern):
                if is_in_comment(line):
                    continue
                if not has_core_cap:
                    findings.append(Finding(
                        rule_id="CODE-10", severity="error",
                        title="Uncapped parallel core usage",
                        message=f"{name} without min(..., 2) capping: `{line[:80]}`. CRAN requires max 2 cores.",
                        file=rel, line=lnum,
                        cran_says="Please ensure that you do not use more than 2 cores."
                    ))
        # Also flag OMP_NUM_THREADS setting without capping
        for lnum, line in scan_file(rf, r'Sys\.setenv\s*\(\s*["\']?OMP_NUM_THREADS'):
            if not is_in_comment(line):
                findings.append(Finding(
                    rule_id="CODE-10", severity="error",
                    title="OMP_NUM_THREADS set in package code",
                    message=f"Setting OMP_NUM_THREADS in package code: `{line[:80]}`. Ensure max 2 threads.",
                    file=rel, line=lnum,
                    cran_says="Please ensure that you do not use more than 2 cores."
                ))

        # CODE-14: No disabling SSL/TLS verification
        ssl_patterns = [
            r'ssl_verifypeer\s*=\s*(?:0|FALSE|F)\b',
            r'ssl\.verifypeer\s*=\s*(?:0|FALSE|F)\b',
            r'ssl_verifyhost\s*=\s*(?:0|FALSE|F)\b',
        ]
        for ssl_pat in ssl_patterns:
            for lnum, line in scan_file(rf, ssl_pat, re.IGNORECASE):
                if not is_in_comment(line):
                    findings.append(Finding(
                        rule_id="CODE-14", severity="error",
                        title="SSL/TLS verification disabled",
                        message=f"Do not disable SSL certificate verification: `{line[:80]}`",
                        file=rel, line=lnum,
                        cran_says="Must not circumvent security provisions like disabling SSL certificate verification."
                    ))

        # CODE-21: class(x) == "matrix" / "data.frame" / "array" comparisons
        for lnum, line in scan_file(rf, r'\bclass\s*\([^)]+\)\s*==\s*["\']'):
            if is_in_comment(line):
                continue
            findings.append(Finding(
                rule_id="CODE-21", severity="warning",
                title="class(x) == comparison (fragile)",
                message=f"Use inherits(x, \"class\") or is.*(x) instead of class(x) ==: `{line[:80]}`",
                file=rel, line=lnum,
                cran_says="the condition has length > 1 and only the first element will be used"
            ))

        # CODE-22: if(class(x) ...) — condition length > 1
        for lnum, line in scan_file(rf, r'\bif\s*\(\s*class\s*\('):
            if is_in_comment(line):
                continue
            findings.append(Finding(
                rule_id="CODE-22", severity="warning",
                title="if(class(...)) may have length > 1",
                message=f"class() can return length > 1 vector. Use inherits() instead: `{line[:80]}`",
                file=rel, line=lnum,
                cran_says="the condition has length > 1"
            ))

        # CODE-19: Staged installation — top-level system.file() calls
        try:
            lines_19 = rf.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            lines_19 = []
        brace_depth_19 = 0
        for i, line_19 in enumerate(lines_19, 1):
            # Track brace depth to detect top-level code
            for ch in line_19:
                if ch == '{':
                    brace_depth_19 += 1
                elif ch == '}':
                    brace_depth_19 -= 1
            if brace_depth_19 == 0 and not is_in_comment(line_19.strip()):
                # Top-level assignment with system.file()
                if re.search(r'(<-|=)\s*system\.file\s*\(', line_19):
                    findings.append(Finding(
                        rule_id="CODE-19", severity="warning",
                        title="Top-level system.file() breaks staged install",
                        message=f"system.file() at top level caches install-time paths: `{line_19.strip()[:80]}`",
                        file=rel, line=i,
                        cran_says="ERROR: installation of package had non-zero exit status"
                    ))

        # NS-08: No library()/require() in package code
        for lnum, line in scan_file(rf, r'\b(?:library|require)\s*\('):
            if is_in_comment(line):
                continue
            # Skip requireNamespace() — that's the correct pattern
            if re.search(r'\brequireNamespace\s*\(', line):
                continue
            # Skip if inside if(interactive()) or if(requireNamespace()) blocks
            if re.search(r'if\s*\(\s*interactive\s*\(\s*\)', line):
                continue
            if re.search(r'if\s*\(\s*requireNamespace\s*\(', line):
                continue
            findings.append(Finding(
                rule_id="NS-08", severity="error",
                title="library()/require() in package code",
                message=f"Use pkg::func() or NAMESPACE imports, not library()/require(): `{line[:80]}`",
                file=rel, line=lnum,
                cran_says="library() or require() calls in package code"
            ))

    # C/C++ checks
    for sf in find_src_files(path):
        rel = str(sf.relative_to(path))
        ext = sf.suffix.lower()
        if ext in (".c", ".cpp", ".cc", ".h", ".hpp"):
            for lnum, line in scan_file(sf, r'\b(?:abort|exit)\s*\('):
                if not is_in_comment(line):
                    findings.append(Finding(
                        rule_id="CODE-11", severity="error",
                        title="abort()/exit() in C/C++ code",
                        message="Use Rf_error() instead.",
                        file=rel, line=lnum,
                    ))

            # CODE-16: sprintf/vsprintf in C/C++
            for lnum, line in scan_file(sf, r'\b(?:sprintf|vsprintf)\s*\('):
                if not is_in_comment(line):
                    findings.append(Finding(
                        rule_id="CODE-16", severity="warning",
                        title="sprintf/vsprintf in compiled code",
                        message="Use snprintf/vsnprintf instead. sprintf is deprecated on macOS 13+.",
                        file=rel, line=lnum,
                    ))

            # COMP-07: Strict C function prototypes
            if ext in (".c", ".h"):
                for lnum, line in scan_file(sf, r'\b\w+\s*\(\s*\)\s*[{;]'):
                    if not is_in_comment(line):
                        # Skip if it's a function call (no type before it)
                        if re.match(r'^\s*(static\s+|extern\s+|inline\s+)?(void|int|char|double|float|long|unsigned|SEXP|Rboolean)\s+\w+\s*\(\s*\)', line):
                            findings.append(Finding(
                                rule_id="COMP-07", severity="warning",
                                title="Empty parameter list — use (void)",
                                message=f"C function with empty parens should be (void): `{line.strip()[:80]}`",
                                file=rel, line=lnum,
                                cran_says="Function declaration isn't a prototype."
                            ))

            # COMP-01: C23 keyword conflicts
            if ext in (".c", ".h"):
                c23_patterns = [
                    (r'#\s*define\s+bool\b', '#define bool'),
                    (r'#\s*define\s+true\b', '#define true'),
                    (r'#\s*define\s+false\b', '#define false'),
                    (r'\btypedef\b.*\bbool\b', 'typedef ... bool'),
                ]
                for c23_pat, c23_desc in c23_patterns:
                    for lnum, line in scan_file(sf, c23_pat):
                        # Don't use is_in_comment() here — # starts C preprocessor, not a comment
                        # C comments use // or /* */
                        stripped = line.strip()
                        if stripped.startswith("//") or stripped.startswith("/*"):
                            continue
                        findings.append(Finding(
                            rule_id="COMP-01", severity="error",
                            title="C23 keyword conflict",
                            message=f"R 4.5+ uses C23 where bool/true/false are keywords. Remove {c23_desc}: `{line.strip()[:80]}`",
                            file=rel, line=lnum,
                            cran_says="Compiler error or -Wkeyword-macro warning under C23."
                        ))

            # COMP-03: Non-API entry points
            non_api_symbols = [
                'DATAPTR', 'STRING_PTR', 'STDVEC_DATAPTR', 'SET_TYPEOF',
                'IS_LONG_VEC', 'PRCODE', 'PRENV', 'PRVALUE', 'R_nchar',
                'Rf_NonNullStringMatch', 'R_shallow_duplicate_attr',
                'Rf_StringBlank', 'TRUELENGTH', 'XLENGTH_EX', 'XTRUELENGTH',
                'VECTOR_PTR', 'R_tryWrap',
            ]
            non_api_pattern = r'\b(' + '|'.join(re.escape(s) for s in non_api_symbols) + r')\b'
            for lnum, line in scan_file(sf, non_api_pattern):
                if not is_in_comment(line):
                    m = re.search(non_api_pattern, line)
                    sym = m.group(1) if m else "unknown"
                    findings.append(Finding(
                        rule_id="COMP-03", severity="warning",
                        title=f"Non-API entry point: {sym}",
                        message=f"Use supported API equivalents: `{line.strip()[:80]}`",
                        file=rel, line=lnum,
                        cran_says="Found non-API calls to R."
                    ))

            # COMP-02: bare R API names in C++ (R_NO_REMAP)
            if ext in (".cpp", ".cc"):
                bare_api_pattern = r'(?<!\w)(?<![Rr]f_)(?:error|warning|length|mkChar|alloc(?:Vector|Matrix)|protect|unprotect)\s*\('
                for lnum, line in scan_file(sf, bare_api_pattern):
                    if not is_in_comment(line) and 'Rf_' not in line:
                        findings.append(Finding(
                            rule_id="COMP-02", severity="warning",
                            title="Bare R API name in C++ (needs Rf_ prefix)",
                            message=f"R 4.5+ compiles C++ with -DR_NO_REMAP: `{line.strip()[:80]}`",
                            file=rel, line=lnum,
                        ))

        if ext in (".f", ".f90", ".f95"):
            for lnum, line in scan_file(sf, r'\bSTOP\b'):
                findings.append(Finding(
                    rule_id="CODE-11", severity="error",
                    title="STOP in Fortran code",
                    message="Do not use STOP in Fortran code for R packages.",
                    file=rel, line=lnum,
                ))

            # COMP-08: Fortran KIND portability
            for lnum, line in scan_file(sf, r'(?:INTEGER|REAL)\s*(?:\*\d+|\(\s*KIND\s*=\s*\d+\s*\))', re.IGNORECASE):
                findings.append(Finding(
                    rule_id="COMP-08", severity="warning",
                    title="Non-portable Fortran KIND specification",
                    message=f"Use SELECTED_INT_KIND()/SELECTED_REAL_KIND() instead: `{line.strip()[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Non-portable Fortran KIND specifications."
                ))

    # COMP-06: Deprecated C++ standard in Makevars
    for makevars in [path / "src" / "Makevars", path / "src" / "Makevars.win"]:
        if makevars.exists():
            rel = str(makevars.relative_to(path))
            for lnum, line in scan_file(makevars, r'CXX_STD\s*=\s*CXX1[14]'):
                findings.append(Finding(
                    rule_id="COMP-06", severity="warning",
                    title="Deprecated C++ standard (CXX11/CXX14)",
                    message=f"Remove CXX_STD line — R defaults to C++17+: `{line.strip()[:80]}`",
                    file=rel, line=lnum,
                    cran_says="C++11/C++14 specifications are deprecated."
                ))

    # COMP-05: Configure script portability
    for script_name in ["configure", "cleanup"]:
        script = path / script_name
        if script.exists():
            rel = str(script.relative_to(path))
            for lnum, line in scan_file(script, r'^#!/bin/bash'):
                findings.append(Finding(
                    rule_id="COMP-05", severity="error",
                    title=f"{script_name} uses #!/bin/bash",
                    message="Use #!/bin/sh for portability.",
                    file=rel, line=lnum,
                    cran_says="NOTE 'configure': /bin/bash is not portable"
                ))

    # MISC-05: Non-portable Makefile features
    for makevars in [path / "src" / "Makevars", path / "src" / "Makevars.win"]:
        if makevars.exists():
            rel = str(makevars.relative_to(path))
            gnu_features = r'\b(?:ifeq|ifneq|ifdef|ifndef)\b|\$\{(?:shell|wildcard)\}'
            sys_reqs = desc.get("SystemRequirements", "")
            if "GNU make" not in sys_reqs:
                for lnum, line in scan_file(makevars, gnu_features):
                    findings.append(Finding(
                        rule_id="MISC-05", severity="warning",
                        title="Non-portable Makefile feature",
                        message=f"GNU make extension without SystemRequirements: GNU make: `{line.strip()[:80]}`",
                        file=rel, line=lnum,
                    ))

    # COMP-09: Rust package requirements
    cargo_toml = path / "src" / "Cargo.toml"
    if not cargo_toml.exists():
        cargo_toml = path / "Cargo.toml"
    if cargo_toml.exists():
        # Check for vendored crates
        has_vendor = (
            (path / "src" / "rust" / "vendor").is_dir()
            or (path / "vendor").is_dir()
            or (path / "src" / "vendor").is_dir()
        )
        if not has_vendor:
            findings.append(Finding(
                rule_id="COMP-09", severity="warning",
                title="Rust crates not vendored",
                message="Cargo.toml found but no vendor/ directory. CRAN requires vendored crate dependencies (no network during build).",
                file=str(cargo_toml.relative_to(path)),
                cran_says="Rejects packages that download Rust crates during installation."
            ))
        # Check for configure script
        if not (path / "configure").exists():
            findings.append(Finding(
                rule_id="COMP-09", severity="warning",
                title="Missing configure script for Rust package",
                message="Cargo.toml found but no configure script. CRAN requires reporting rustc version before compilation.",
                file=str(cargo_toml.relative_to(path)),
                cran_says="Must report rustc version before compilation."
            ))

    # COMP-10: Native routine registration
    src_dir = path / "src"
    if src_dir.is_dir():
        has_c_cpp = bool(list(src_dir.glob("*.c")) or list(src_dir.glob("*.cpp")) or list(src_dir.glob("*.cc")))
        if has_c_cpp:
            # Check if R code uses .Call/.C/.Fortran/.External
            has_native_call = False
            for rf in find_r_files(path):
                for _, line in scan_file(rf, r'\.Call\s*\(|\.C\s*\(|\.Fortran\s*\(|\.External\s*\('):
                    if not is_in_comment(line):
                        has_native_call = True
                        break
                if has_native_call:
                    break
            if has_native_call:
                # Check for init.c or registration.c
                has_init = (
                    (src_dir / "init.c").exists()
                    or (src_dir / "registration.c").exists()
                    or (src_dir / "init.cpp").exists()
                )
                if not has_init:
                    # Also check if any .c file contains R_registerRoutines
                    has_register = False
                    for sf in find_src_files(path):
                        for _, line in scan_file(sf, r'R_registerRoutines'):
                            has_register = True
                            break
                        if has_register:
                            break
                    if not has_register:
                        findings.append(Finding(
                            rule_id="COMP-10", severity="warning",
                            title="Missing native routine registration",
                            message="Package uses .Call()/.C() but no R_registerRoutines() found. Add src/init.c with registration.",
                            file="src/",
                            cran_says="Found no calls to: R_registerRoutines, R_useDynamicSymbols."
                        ))
                # Check NAMESPACE for useDynLib with registration
                ns = parse_namespace(path)
                ns_text = "\n".join(ns.get("raw_lines", []))
                if "useDynLib" not in ns_text:
                    findings.append(Finding(
                        rule_id="COMP-10", severity="warning",
                        title="Missing useDynLib in NAMESPACE",
                        message="Package has compiled code and uses native interfaces but NAMESPACE has no useDynLib().",
                        file="NAMESPACE",
                        cran_says="It is good practice to register native routines."
                    ))

    # COMP-12: UCRT Windows toolchain compatibility
    makevars_win = path / "src" / "Makevars.win"
    if makevars_win.exists():
        rel_mvw = str(makevars_win.relative_to(path))
        for lnum, line in scan_file(makevars_win, r'\$\(MINGW_PREFIX\)'):
            findings.append(Finding(
                rule_id="COMP-12", severity="warning",
                title="Obsolete $(MINGW_PREFIX) reference",
                message=f"$(MINGW_PREFIX) is from the old MSVCRT toolchain: `{line.strip()[:80]}`",
                file=rel_mvw, line=lnum,
                cran_says="Compilation or linking failures on Windows."
            ))
        for lnum, line in scan_file(makevars_win, r'\bdownload\.file\b'):
            findings.append(Finding(
                rule_id="COMP-12", severity="warning",
                title="Download of pre-compiled binaries in Makevars.win",
                message=f"Do not download pre-compiled binaries: `{line.strip()[:80]}`",
                file=rel_mvw, line=lnum,
                cran_says="Packages must not download pre-compiled MSVCRT libraries."
            ))
        for lnum, line in scan_file(makevars_win, r'\bCRT_|MSVCRT', re.IGNORECASE):
            findings.append(Finding(
                rule_id="COMP-12", severity="warning",
                title="MSVCRT-specific reference in Makevars.win",
                message=f"R 4.2+ uses UCRT, not MSVCRT: `{line.strip()[:80]}`",
                file=rel_mvw, line=lnum,
                cran_says="External DLLs must be compatible with UCRT."
            ))
    # Also check configure.win for download.file
    configure_win = path / "configure.win"
    if configure_win.exists():
        rel_cw = str(configure_win.relative_to(path))
        for lnum, line in scan_file(configure_win, r'\bdownload\.file\b'):
            findings.append(Finding(
                rule_id="COMP-12", severity="warning",
                title="Download of pre-compiled binaries in configure.win",
                message=f"Do not download pre-compiled binaries at install time: `{line.strip()[:80]}`",
                file=rel_cw, line=lnum,
                cran_says="Packages must not download pre-compiled MSVCRT libraries."
            ))

    # DEP-02: Suggested Packages Must Be Used Conditionally
    suggests_raw = desc.get("Suggests", "")
    if suggests_raw:
        suggested_pkgs = set()
        for entry in suggests_raw.split(","):
            pkg_name = entry.strip().split("(")[0].strip()
            if pkg_name:
                suggested_pkgs.add(pkg_name)
        for rf in r_files:
            rel = str(rf.relative_to(path))
            try:
                full_text = rf.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            lines = full_text.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                # Look for library(pkg) or require(pkg) calls
                m = re.search(r'\b(?:library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', stripped)
                if not m:
                    continue
                pkg_name = m.group(1)
                if pkg_name not in suggested_pkgs:
                    continue
                # Skip requireNamespace
                if re.search(r'\brequireNamespace\s*\(', stripped):
                    continue
                # Check if wrapped in if(requireNamespace(...)) or if(require(...))
                if re.search(r'if\s*\(\s*requireNamespace\s*\(', stripped):
                    continue
                if re.search(r'if\s*\(\s*require\s*\(', stripped):
                    continue
                findings.append(Finding(
                    rule_id="DEP-02", severity="warning",
                    title=f"Suggested package '{pkg_name}' used unconditionally",
                    message=f"library({pkg_name})/require({pkg_name}) without conditional check. Wrap in if(requireNamespace(...)): `{stripped[:80]}`",
                    file=rel, line=i,
                    cran_says="Packages in Suggests should be used conditionally."
                ))

    # CODE-20: stringsAsFactors Compatibility (heuristic)
    for rf in r_files:
        rel = str(rf.relative_to(path))
        try:
            full_text_20 = rf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        has_data_frame = bool(re.search(r'\bdata\.frame\s*\(', full_text_20))
        has_strings_as_factors = bool(re.search(r'\bstringsAsFactors\b', full_text_20))
        has_factor_usage = bool(
            re.search(r'\blevels\s*\(', full_text_20)
            or re.search(r'\bas\.factor\s*\(', full_text_20)
            or re.search(r'\bnlevels\s*\(', full_text_20)
        )
        if has_data_frame and not has_strings_as_factors and has_factor_usage:
            findings.append(Finding(
                rule_id="CODE-20", severity="note",
                title="Possible stringsAsFactors assumption",
                message="File uses data.frame() and factor functions (levels/as.factor/nlevels) but never mentions stringsAsFactors. Since R 4.0, stringsAsFactors defaults to FALSE.",
                file=rel,
                cran_says="stringsAsFactors default changed in R 4.0.0"
            ))

    # NET-01: Must Fail Gracefully When Resources Unavailable
    network_call_patterns = [
        (r'\bdownload\.file\s*\(', 'download.file()'),
        (r'\burl\s*\(', 'url()'),
        (r'\bhttr::GET\s*\(', 'httr::GET()'),
        (r'\bhttr::POST\s*\(', 'httr::POST()'),
        (r'\bcurl::curl\s*\(', 'curl::curl()'),
        (r'\bRCurl::getURL\s*\(', 'RCurl::getURL()'),
    ]
    for rf in r_files:
        rel = str(rf.relative_to(path))
        try:
            full_text = rf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = full_text.splitlines()
        has_trycatch = bool(re.search(r'\btryCatch\s*\(', full_text) or
                           re.search(r'\btry\s*\(', full_text) or
                           re.search(r'\bwithCallingHandlers\s*\(', full_text))
        if has_trycatch:
            continue  # File has error handling; skip (conservative)
        for net_pat, net_name in network_call_patterns:
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(net_pat, stripped):
                    findings.append(Finding(
                        rule_id="NET-01", severity="warning",
                        title=f"Network call ({net_name}) without error handling",
                        message=f"Wrap network calls in tryCatch()/try() for graceful failure when offline: `{stripped[:80]}`",
                        file=rel, line=i,
                        cran_says="Package must not error or produce check warnings if internet resources are unavailable."
                    ))
                    break  # One finding per file per pattern is enough
            else:
                continue
            break  # One finding per file is enough

    # COMP-04: Implicit Function Declarations (heuristic)
    # Check C files for common stdlib functions without corresponding headers
    _stdlib_header_map = {
        "malloc": "stdlib.h", "calloc": "stdlib.h", "realloc": "stdlib.h",
        "free": "stdlib.h", "atoi": "stdlib.h", "atof": "stdlib.h",
        "exit": "stdlib.h", "abort": "stdlib.h", "qsort": "stdlib.h",
        "printf": "stdio.h", "fprintf": "stdio.h", "sprintf": "stdio.h",
        "snprintf": "stdio.h", "fopen": "stdio.h", "fclose": "stdio.h",
        "fread": "stdio.h", "fwrite": "stdio.h", "fgets": "stdio.h",
        "strlen": "string.h", "strcpy": "string.h", "strncpy": "string.h",
        "strcmp": "string.h", "strncmp": "string.h", "memcpy": "string.h",
        "memset": "string.h", "memmove": "string.h", "strcat": "string.h",
        "strtok": "string.h", "strstr": "string.h",
        "sqrt": "math.h", "pow": "math.h", "fabs": "math.h",
        "log": "math.h", "exp": "math.h", "sin": "math.h",
        "cos": "math.h", "ceil": "math.h", "floor": "math.h",
    }
    src_dir = path / "src"
    if src_dir.is_dir():
        for cf in sorted(src_dir.glob("*.c")):
            rel = str(cf.relative_to(path))
            try:
                c_text = cf.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            c_lines = c_text.splitlines()
            # Collect included standard headers
            included_headers = set()
            for c_line in c_lines:
                hm = re.match(r'\s*#\s*include\s*[<"]([^>"]+)[>"]', c_line)
                if hm:
                    included_headers.add(hm.group(1))
            # Check for function usage without header
            missing_headers: dict[str, set[str]] = {}  # header -> {functions}
            for func_name, header in _stdlib_header_map.items():
                if header in included_headers:
                    continue
                # Check if the function is actually used (as a call)
                func_pat = r'\b' + re.escape(func_name) + r'\s*\('
                if re.search(func_pat, c_text):
                    missing_headers.setdefault(header, set()).add(func_name)
            for header, funcs in sorted(missing_headers.items()):
                func_list = ", ".join(sorted(funcs)[:5])
                findings.append(Finding(
                    rule_id="COMP-04", severity="note",
                    title=f"Possibly missing #include <{header}>",
                    message=f"File uses {func_list} but does not include <{header}>. This may cause implicit function declaration warnings.",
                    file=rel,
                    cran_says="Function declaration isn't a prototype."
                ))

    # LIC-03: No Dual Licensing Within Package (heuristic)
    license_field = desc.get("License", "").upper()
    _license_patterns = [
        (r'\bMIT\b', "MIT"),
        (r'\bGPL[- ]?2\b', "GPL-2"),
        (r'\bGPL[- ]?3\b', "GPL-3"),
        (r'\bAPACHE\b', "Apache"),
        (r'\bBSD\b', "BSD"),
        (r'\bLGPL\b', "LGPL"),
    ]
    if license_field:
        files_to_check_lic: list[tuple[Path, str]] = []
        for rf in r_files:
            files_to_check_lic.append((rf, str(rf.relative_to(path))))
        if src_dir.is_dir():
            for ext in ("*.c", "*.cpp", "*.cc", "*.h", "*.hpp"):
                for sf in src_dir.glob(ext):
                    files_to_check_lic.append((sf, str(sf.relative_to(path))))
        for fpath, rel in files_to_check_lic:
            try:
                header_lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()[:20]
            except Exception:
                continue
            header_text = " ".join(header_lines).upper()
            for pat, lic_name in _license_patterns:
                if re.search(pat, header_text):
                    # Check if this license contradicts DESCRIPTION
                    if lic_name.upper() not in license_field:
                        findings.append(Finding(
                            rule_id="LIC-03", severity="note",
                            title=f"Possible license mismatch in {fpath.name}",
                            message=f"File header mentions '{lic_name}' but DESCRIPTION License is '{desc.get('License', '')}'. Ensure consistency.",
                            file=rel,
                            cran_says="License components which are templates need a '+ file LICENSE' component."
                        ))
                        break  # One finding per file

    # PLAT-01: Must Work on Multiple Platforms (heuristic)
    for rf in r_files:
        rel = str(rf.relative_to(path))
        try:
            plat_text = rf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        plat_lines = plat_text.splitlines()
        # Check for platform-specific patterns without cross-platform handling
        has_platform_guard = bool(
            re.search(r'\.Platform\$OS\.type', plat_text)
            or re.search(r'Sys\.info\s*\(\s*\)', plat_text)
        )
        # Flag shell() calls — Windows-only
        for i, pline in enumerate(plat_lines, 1):
            stripped = pline.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r'\bshell\s*\(', stripped):
                findings.append(Finding(
                    rule_id="PLAT-01", severity="note",
                    title="Windows-only shell() call",
                    message=f"shell() is Windows-only. Use system2() for cross-platform compatibility: `{stripped[:80]}`",
                    file=rel, line=i,
                    cran_says="Package must work on all major platforms."
                ))
            if re.search(r'system\s*\(\s*["\']cmd\s+/c', stripped):
                findings.append(Finding(
                    rule_id="PLAT-01", severity="note",
                    title="Windows cmd.exe call in system()",
                    message=f"system('cmd /c ...') is Windows-only: `{stripped[:80]}`",
                    file=rel, line=i,
                    cran_says="Package must work on all major platforms."
                ))

    # NET-03: Rate Limit Policy (heuristic reminder)
    has_network_code = False
    for rf in r_files:
        try:
            net_text = rf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if (re.search(r'\bhttr::', net_text) or re.search(r'\bcurl::', net_text)
                or re.search(r'\bdownload\.file\s*\(', net_text)
                or re.search(r'\bhttr2::', net_text)):
            has_network_code = True
            break
    if has_network_code:
        findings.append(Finding(
            rule_id="NET-03", severity="note",
            title="Package makes network requests",
            message="Ensure API/URL calls implement rate limiting and respect server policies. CRAN checks may fail if external services are rate-limited.",
            cran_says="Packages should gracefully handle HTTP errors and rate limits."
        ))

    return findings


def check_documentation(path: Path, desc: dict) -> list[Finding]:
    """Check documentation for CRAN policy violations."""
    findings = []
    uses_roxygen = "RoxygenNote" in desc
    r_files = find_r_files(path)
    rd_files = find_rd_files(path)

    # DOC-01: Missing @return tags (check R files if roxygen, else .Rd files)
    if uses_roxygen:
        for rf in r_files:
            rel = str(rf.relative_to(path))
            text = rf.read_text(encoding="utf-8", errors="replace")
            lines_list = text.splitlines()
            in_roxygen = False
            has_export = False
            has_return = False
            has_rdname = False  # @rdname/@name means docs inherited from another block
            has_internal = False  # @keywords internal — CRAN doesn't require @return
            block_start = 0
            for i, line in enumerate(lines_list, 1):
                if line.strip().startswith("#'"):
                    if not in_roxygen:
                        in_roxygen = True
                        has_export = False
                        has_return = False
                        has_rdname = False
                        has_internal = False
                        block_start = i
                    if "@export" in line:
                        has_export = True
                    if "@return" in line or "@value" in line or "@inherit" in line:
                        has_return = True
                    if "@rdname" in line or "@name" in line:
                        has_rdname = True
                    if "@keywords" in line and "internal" in line:
                        has_internal = True
                else:
                    if in_roxygen and has_export and not has_return:
                        stripped = line.strip()
                        # Skip if docs are inherited via @rdname/@name
                        if has_rdname:
                            pass
                        # Skip if marked @keywords internal
                        elif has_internal:
                            pass
                        # Skip reexports (pkg::fun or pkg::`fun`)
                        elif re.match(r'^\s*\w+(::|:::)', stripped):
                            pass
                        # Skip S3 method exports (foo.bar <- function) — they inherit from generic
                        elif re.match(r'^\s*\w+\.\w+', stripped):
                            pass
                        # Skip backtick-quoted method exports (`[.class` <- function)
                        elif stripped.startswith('`'):
                            pass
                        # Skip NULL (bare doc blocks for @name/@aliases)
                        elif stripped == 'NULL':
                            pass
                        else:
                            findings.append(Finding(
                                rule_id="DOC-01", severity="error",
                                title="Missing @return tag on exported function",
                                message="Every exported function must document its return value.",
                                file=rel, line=block_start,
                                cran_says="Please add \\value to .Rd files regarding exported methods."
                            ))
                    in_roxygen = False
    else:
        for rd in rd_files:
            rel = str(rd.relative_to(path))
            text = rd.read_text(encoding="utf-8", errors="replace")
            if "\\alias{" in text and "\\value{" not in text:
                if "\\docType{data}" not in text:  # Data docs don't need \value
                    findings.append(Finding(
                        rule_id="DOC-01", severity="error",
                        title=f"Missing \\value in {rd.name}",
                        message="Add \\value{} section describing the return value.",
                        file=rel,
                        cran_says="Please add \\value to .Rd files."
                    ))

    # DOC-02: \dontrun{} misuse
    files_to_check = [(rf, str(rf.relative_to(path))) for rf in r_files]
    files_to_check += [(rd, str(rd.relative_to(path))) for rd in rd_files]
    for f, rel in files_to_check:
        for lnum, line in scan_file(f, r'\\dontrun\b'):
            findings.append(Finding(
                rule_id="DOC-02", severity="warning",
                title="\\dontrun{} used — is it necessary?",
                message="Use \\donttest{} for slow examples, if(interactive()) for interactive ones. Keep \\dontrun{} only for truly non-executable code.",
                file=rel, line=lnum,
                cran_says="\\dontrun{} should only be used if the example really cannot be executed."
            ))

    # DOC-05: Exported functions without @examples
    if uses_roxygen:
        for rf in r_files:
            rel = str(rf.relative_to(path))
            text = rf.read_text(encoding="utf-8", errors="replace")
            lines_list = text.splitlines()
            in_roxygen = False
            has_export = False
            has_examples = False
            has_rdname = False
            has_internal = False
            block_start = 0
            for i, line in enumerate(lines_list, 1):
                if line.strip().startswith("#'"):
                    if not in_roxygen:
                        in_roxygen = True
                        has_export = False
                        has_examples = False
                        has_rdname = False
                        has_internal = False
                        block_start = i
                    if "@export" in line:
                        has_export = True
                    if "@examples" in line or "@example" in line or "@inherit" in line:
                        has_examples = True
                    if "@rdname" in line or "@name" in line:
                        has_rdname = True
                    if "@keywords" in line and "internal" in line:
                        has_internal = True
                else:
                    if in_roxygen and has_export and not has_examples:
                        stripped = line.strip()
                        # Skip if docs are inherited via @rdname/@name
                        if has_rdname:
                            pass
                        # Skip if marked @keywords internal
                        elif has_internal:
                            pass
                        # Skip reexports (pkg::fun or pkg::`fun`)
                        elif re.match(r'^\s*\w+(::|:::)', stripped):
                            pass
                        # Skip S3 method exports — they inherit from generic
                        elif re.match(r'^\s*\w+\.\w+', stripped):
                            pass
                        # Skip backtick-quoted method exports
                        elif stripped.startswith('`'):
                            pass
                        # Skip NULL (bare doc blocks for @name/@aliases)
                        elif stripped == 'NULL':
                            pass
                        else:
                            findings.append(Finding(
                                rule_id="DOC-05", severity="note",
                                title="Exported function without @examples",
                                message="Exported functions should include runnable examples.",
                                file=rel, line=block_start,
                            ))
                    in_roxygen = False

    # DOC-07: Use Canonical CRAN/Bioconductor URLs
    non_canonical_patterns = [
        (r'http://cran\.r-project\.org/web/packages/', 'https://CRAN.R-project.org/package='),
        (r'http://www\.bioconductor\.org/packages/', 'https://bioconductor.org/packages/'),
        (r'http://cran\.r-project\.org/', 'https://CRAN.R-project.org/'),
    ]
    files_for_url_check: list[tuple[Path, str]] = []
    for rd in rd_files:
        files_for_url_check.append((rd, str(rd.relative_to(path))))
    for vf in _find_vignette_files(path):
        files_for_url_check.append((vf, str(vf.relative_to(path))))
    desc_path = path / "DESCRIPTION"
    if desc_path.exists():
        files_for_url_check.append((desc_path, "DESCRIPTION"))
    for fpath, rel in files_for_url_check:
        for pat, replacement in non_canonical_patterns:
            for lnum, line in scan_file(fpath, pat, re.IGNORECASE):
                findings.append(Finding(
                    rule_id="DOC-07", severity="note",
                    title="Non-canonical CRAN/Bioconductor URL",
                    message=f"Use canonical URL form ({replacement}...): `{line[:80]}`",
                    file=rel, line=lnum,
                    cran_says="Use canonical URL forms."
                ))

    # DOC-08: Lost Braces in Rd Documentation
    for rd in rd_files:
        rel = str(rd.relative_to(path))
        try:
            text = rd.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            # Detect \itemize{ \item{text}{desc} } — wrong pattern
            # In \itemize, items should be \item text, not \item{text}{desc}
            if r'\itemize' in text:
                if re.search(r'\\item\{[^}]+\}\{', line):
                    findings.append(Finding(
                        rule_id="DOC-08", severity="warning",
                        title="Lost braces: \\item{}{} inside \\itemize",
                        message=f"\\itemize uses '\\item text', not '\\item{{text}}{{desc}}' (that's for \\describe): `{line.strip()[:80]}`",
                        file=rel, line=i,
                        cran_says="Lost braces in Rd parsing."
                    ))

    # DOC-09: HTML5 Rd Validation
    deprecated_html_tags = [
        r'<font\b', r'<center\b', r'<strike\b', r'<big\b',
        r'<small\b', r'<tt\b',
    ]
    deprecated_html_attrs = [
        r'\bbgcolor\s*=', r'\balign\s*=',
    ]
    deprecated_html_pattern = '|'.join(deprecated_html_tags + deprecated_html_attrs)
    for rd in rd_files:
        rel = str(rd.relative_to(path))
        for lnum, line in scan_file(rd, r'\\if\{html\}\{\\out\{'):
            # Check if line or nearby content uses deprecated HTML
            if re.search(deprecated_html_pattern, line, re.IGNORECASE):
                findings.append(Finding(
                    rule_id="DOC-09", severity="warning",
                    title="Deprecated HTML4 element in Rd \\out{} block",
                    message=f"Use HTML5-compatible elements (no <font>, <center>, <strike>, <big>, <small>, <tt>, bgcolor=): `{line.strip()[:80]}`",
                    file=rel, line=lnum,
                    cran_says="HTML validation issues in rendered help pages."
                ))

    # DOC-10: \donttest Examples Now Executed Under --as-cran
    files_for_donttest = [(rd, str(rd.relative_to(path))) for rd in rd_files]
    files_for_donttest += [(rf, str(rf.relative_to(path))) for rf in r_files]
    for fpath, rel in files_for_donttest:
        for lnum, line in scan_file(fpath, r'\\donttest\{'):
            findings.append(Finding(
                rule_id="DOC-10", severity="note",
                title="\\donttest{} examples ARE executed under --as-cran",
                message="Since R 4.0, \\donttest{} code runs during CRAN checks. Ensure these examples work without credentials, special hardware, or long runtimes.",
                file=rel, line=lnum,
                cran_says="Running examples in 'package-Ex.R' failed"
            ))
            break  # One finding per file is enough

    # DOC-11: Duplicated Vignette Titles
    vig_files_doc = _find_vignette_files(path)
    if vig_files_doc:
        title_map: dict[str, list[str]] = {}
        for vf in vig_files_doc:
            meta = parse_vignette_metadata(vf)
            title = None
            if meta["index_entry"]:
                title = meta["index_entry"][1]
            else:
                # Fall back to YAML title
                try:
                    text = vf.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                in_yaml = False
                for line in text.splitlines():
                    if line.strip() == '---':
                        if not in_yaml:
                            in_yaml = True
                            continue
                        else:
                            break
                    if in_yaml:
                        m = re.match(r'\s*title\s*:\s*["\']?(.+?)["\']?\s*$', line)
                        if m:
                            title = m.group(1)
                            break
            if title:
                title_map.setdefault(title, []).append(str(vf.relative_to(path)))
        for title_val, files in title_map.items():
            if len(files) > 1:
                findings.append(Finding(
                    rule_id="DOC-11", severity="warning",
                    title="Duplicated vignette title",
                    message=f"Title '{title_val}' is used by multiple vignettes: {', '.join(files)}",
                    file=files[0],
                    cran_says="Duplicated vignette titles/index entries."
                ))

    # DOC-03: Examples Must Be Fast (heuristic)
    _slow_example_patterns = [
        (r'\bSys\.sleep\s*\(', "Sys.sleep()"),
        (r'\bdownload\.file\s*\(', "download.file()"),
        (r'\bhttr::', "httr:: network call"),
        (r'\bcurl::', "curl:: network call"),
        (r'\bsystem\s*\(', "system() call"),
        (r'\bsystem2\s*\(', "system2() call"),
    ]
    for rd in rd_files:
        rel = str(rd.relative_to(path))
        try:
            rd_text = rd.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Extract examples block
        examples_match = re.search(r'\\examples\s*\{', rd_text)
        if not examples_match:
            continue
        # Find the matching closing brace
        start = examples_match.end()
        brace_depth = 1
        end = start
        for ci in range(start, len(rd_text)):
            if rd_text[ci] == '{':
                brace_depth += 1
            elif rd_text[ci] == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    end = ci
                    break
        examples_text = rd_text[start:end]
        for slow_pat, slow_desc in _slow_example_patterns:
            if re.search(slow_pat, examples_text):
                findings.append(Finding(
                    rule_id="DOC-03", severity="note",
                    title=f"Potentially slow example in {rd.name}",
                    message=f"Examples contain {slow_desc}. Ensure examples complete within 5 seconds or wrap in \\donttest{{}}.",
                    file=rel,
                    cran_says="Examples with CPU (user + system) or elapsed time > 5s"
                ))
                break  # One finding per file

    # DOC-04: Changes Go in .R Files, Not .Rd (heuristic)
    # Only flag if the project actually uses roxygen (at least one Rd file has the marker)
    if uses_roxygen and rd_files:
        has_any_roxygen_rd = False
        for rd in rd_files:
            try:
                rd_text_check = rd.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if "% Generated by roxygen2" in rd_text_check:
                has_any_roxygen_rd = True
                break
        if has_any_roxygen_rd:
            for rd in rd_files:
                rel = str(rd.relative_to(path))
                try:
                    rd_text = rd.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                if "% Generated by roxygen2" not in rd_text:
                    findings.append(Finding(
                        rule_id="DOC-04", severity="note",
                        title=f"Hand-edited Rd file in roxygen project: {rd.name}",
                        message="DESCRIPTION has RoxygenNote but this Rd file lacks '% Generated by roxygen2'. Hand-edits will be overwritten by roxygen2.",
                        file=rel,
                        cran_says="Documentation changes should be made in .R files, not .Rd files."
                    ))

    # DOC-06: Function References Should Include Parentheses (conservative)
    ns = parse_namespace(path)
    exported_funcs_doc06 = set()
    for fun, _ in ns.get("exports", []):
        exported_funcs_doc06.add(fun)
    if exported_funcs_doc06 and rd_files:
        for rd in rd_files:
            rel = str(rd.relative_to(path))
            try:
                rd_text = rd.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            # Find \description{} section
            desc_match = re.search(r'\\description\s*\{', rd_text)
            if not desc_match:
                continue
            d_start = desc_match.end()
            d_depth = 1
            d_end = d_start
            for ci in range(d_start, len(rd_text)):
                if rd_text[ci] == '{':
                    d_depth += 1
                elif rd_text[ci] == '}':
                    d_depth -= 1
                    if d_depth == 0:
                        d_end = ci
                        break
            desc_text = rd_text[d_start:d_end]
            # Look for \code{funcname} where funcname is an export without ()
            for m in re.finditer(r'\\code\{(\w+)\}', desc_text):
                fname = m.group(1)
                if fname in exported_funcs_doc06:
                    # Check it's not followed by () inside the \code{}
                    full_match = m.group(0)
                    if "()" not in full_match:
                        findings.append(Finding(
                            rule_id="DOC-06", severity="note",
                            title=f"Function reference without parentheses in {rd.name}",
                            message=f"\\code{{{fname}}} refers to an exported function. Consider \\code{{{fname}()}} for clarity.",
                            file=rel,
                            cran_says="Function references should include parentheses."
                        ))
                        break  # One finding per file

    return findings


def check_structure(path: Path, desc: dict) -> list[Finding]:
    """Check package structure and files."""
    findings = []

    # MISC-01: NEWS.md
    if not (path / "NEWS.md").exists() and not (path / "NEWS").exists():
        findings.append(Finding(
            rule_id="MISC-01", severity="note",
            title="No NEWS.md file",
            message="Recommended: create NEWS.md to document changes between versions.",
        ))

    # SUB-04: cran-comments.md
    if not (path / "cran-comments.md").exists():
        findings.append(Finding(
            rule_id="SUB-04", severity="note",
            title="No cran-comments.md",
            message="Create with usethis::use_cran_comments() to document test environments and R CMD check results.",
        ))

    # PLAT-02: Binary files
    binary_exts = {".exe", ".dll", ".so", ".dylib", ".o", ".class"}
    for ext in binary_exts:
        for f in path.rglob(f"*{ext}"):
            if ".git" in str(f):
                continue
            findings.append(Finding(
                rule_id="PLAT-02", severity="error",
                title=f"Binary file in source package: {f.name}",
                message="Source packages must not contain binary executable code.",
                file=str(f.relative_to(path)),
            ))

    # SIZE-01: Large files
    for f in path.rglob("*"):
        if ".git" in str(f) or not f.is_file():
            continue
        size_mb = f.stat().st_size / (1024 * 1024)
        if size_mb > 5:
            findings.append(Finding(
                rule_id="SIZE-01", severity="error",
                title=f"File exceeds 5MB: {f.name} ({size_mb:.1f}MB)",
                message="Data and documentation each limited to 5MB.",
                file=str(f.relative_to(path)),
            ))
        elif size_mb > 1:
            findings.append(Finding(
                rule_id="SIZE-01", severity="warning",
                title=f"Large file: {f.name} ({size_mb:.1f}MB)",
                message="Package tarball should not exceed 10MB total.",
                file=str(f.relative_to(path)),
            ))

    # NET-02: HTTP URLs (scan all text files)
    text_exts = {".R", ".Rd", ".md", ".Rmd", ".txt", ".yml", ".yaml", ".json"}
    for f in path.rglob("*"):
        if ".git" in str(f) or not f.is_file() or f.suffix not in text_exts:
            continue
        for lnum, line in scan_file(f, r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)'):
            findings.append(Finding(
                rule_id="NET-02", severity="warning",
                title="HTTP URL (should be HTTPS)",
                message=f"Use https:// instead: `{line[:80]}`",
                file=str(f.relative_to(path)), line=lnum,
            ))

    # .Rbuildignore check
    rbuildignore = path / ".Rbuildignore"
    if rbuildignore.exists():
        content = rbuildignore.read_text(encoding="utf-8", errors="replace")
        dev_files = {
            ".Rhistory": r"\.Rhistory",
            ".git": r"\.git",
        }
        for name, pattern in dev_files.items():
            if (path / name).exists() and pattern not in content:
                findings.append(Finding(
                    rule_id="MISC-04", severity="warning",
                    title=f"{name} not in .Rbuildignore",
                    message=f"Add '^{pattern}$' to .Rbuildignore",
                ))

    # MISC-06: NEWS file format
    news_file = path / "NEWS.md"
    if news_file.exists():
        text = news_file.read_text(encoding="utf-8", errors="replace")
        headings = re.findall(r'^#\s+(.+)$', text, re.MULTILINE)
        for heading in headings:
            # Check for version-like pattern
            if not re.search(r'\d+\.\d+', heading):
                findings.append(Finding(
                    rule_id="MISC-06", severity="note",
                    title="NEWS.md heading may not be parseable",
                    message=f"Heading '{heading[:60]}' may not be recognized as a version heading.",
                    file="NEWS.md",
                ))

    # Wire in submission readiness checks
    findings.extend(check_submission_readiness(path, desc))

    return findings


# --- Submission readiness checks ---

def check_submission_readiness(path: Path, desc: dict) -> list[Finding]:
    """Emit informational reminders about CRAN submission readiness."""
    findings = []
    version = desc.get("Version", "")
    desc_file = str(path / "DESCRIPTION")

    # COMP-11: Memory Sanitizer Compliance
    src_dir = path / "src"
    if src_dir.is_dir():
        has_compiled = bool(
            list(src_dir.glob("*.c")) or list(src_dir.glob("*.cpp"))
            or list(src_dir.glob("*.cc")) or list(src_dir.glob("*.f"))
            or list(src_dir.glob("*.f90")) or list(src_dir.glob("*.f95"))
        )
        if has_compiled:
            findings.append(Finding(
                rule_id="COMP-11", severity="note",
                title="Compiled code requires sanitizer testing",
                message="Package has compiled code. Run under ASAN/UBSAN/valgrind before CRAN submission: R CMD check --use-valgrind",
                file="src/",
                cran_says="Package has issues with memory access or undefined behavior."
            ))

    # CODE-18: Do Not Remove Failing Tests (heuristic)
    tests_dir = path / "tests"
    r_dir = path / "R"
    if tests_dir.is_dir():
        test_files = list(tests_dir.glob("*.R")) + list(tests_dir.rglob("test*.R"))
        # Deduplicate
        test_files = list(set(test_files))
        r_files = list(r_dir.glob("*.R")) if r_dir.is_dir() else []
        if len(test_files) == 0 and len(r_files) >= 5:
            findings.append(Finding(
                rule_id="CODE-18", severity="note",
                title="tests/ directory exists but has no test files",
                message=f"Package has {len(r_files)} R source files but tests/ contains no .R test files. Ensure tests were not removed.",
                file="tests/",
                cran_says="Tests should not be removed to avoid check failures."
            ))

    # SIZE-02: Check Time Must Be Under 10 Minutes
    has_tests = tests_dir.is_dir() and any(tests_dir.rglob("*.R"))
    has_vignettes = (path / "vignettes").is_dir() and any(_find_vignette_files(path))
    has_compiled = src_dir.is_dir() and bool(
        list(src_dir.glob("*.c")) or list(src_dir.glob("*.cpp"))
        or list(src_dir.glob("*.cc")) or list(src_dir.glob("*.f"))
        or list(src_dir.glob("*.f90"))
    )
    if has_tests and has_vignettes and has_compiled:
        findings.append(Finding(
            rule_id="SIZE-02", severity="note",
            title="Package has tests, vignettes, and compiled code",
            message="Packages with all three may approach the 10-minute check time limit. Profile with R CMD check --timings.",
            cran_says="Total check time must not exceed 10 minutes."
        ))

    # NS-06: No Visible Binding / Missing Imports (reminder)
    r_dir_sub = path / "R"
    if r_dir_sub.is_dir() and any(r_dir_sub.glob("*.R")):
        findings.append(Finding(
            rule_id="NS-06", severity="note",
            title="Run R CMD check for binding analysis",
            message="Static analysis cannot fully detect missing imports or 'no visible binding' issues. Run 'R CMD check' for complete binding analysis.",
            cran_says="no visible binding for global variable"
        ))

    # SUB-01: Run R CMD check --as-cran
    findings.append(Finding(
        rule_id="SUB-01", severity="note",
        title="Pre-submission checklist: R CMD check --as-cran",
        message="Run 'R CMD check --as-cran' on the built tarball and fix all ERRORs and WARNINGs before submission.",
        cran_says="Please fix and resubmit."
    ))

    # SUB-02: Test on Multiple Platforms
    findings.append(Finding(
        rule_id="SUB-02", severity="note",
        title="Pre-submission checklist: multi-platform testing",
        message="Test on at least 2 platforms (e.g., via R-hub or win-builder) before CRAN submission.",
        cran_says="Package check results depend on the platform."
    ))

    # SUB-03: Check Reverse Dependencies
    if version and ".9000" not in version and ".9999" not in version:
        # Looks like a release version; may be an update with reverse deps
        if not version.startswith("0.") and version != "1.0.0":
            findings.append(Finding(
                rule_id="SUB-03", severity="note",
                title="Pre-submission checklist: reverse dependency check",
                message="If this package is already on CRAN, run revdepcheck::revdep_check() before updating.",
                file=desc_file,
                cran_says="Did you check reverse dependencies?"
            ))

    # SUB-05: First Submission Gets "New submission" NOTE
    if version.startswith("0.") or version == "1.0.0":
        findings.append(Finding(
            rule_id="SUB-05", severity="note",
            title="First CRAN submission expected NOTE",
            message=f"Version '{version}' looks like a first release. A 'New submission' NOTE from CRAN is expected and harmless.",
            file=desc_file,
            cran_says="New submission"
        ))

    # SUB-06: Submission Frequency Limit
    findings.append(Finding(
        rule_id="SUB-06", severity="note",
        title="CRAN submission frequency limit",
        message="CRAN limits resubmissions to once every 1-2 months for the same package. Plan accordingly.",
        cran_says="Packages should not be resubmitted more than once every 1-2 months."
    ))

    # SUB-07: CRAN Vacation Periods
    current_month = datetime.date.today().month
    if current_month == 12 or current_month in (7, 8):
        month_name = datetime.date.today().strftime("%B")
        findings.append(Finding(
            rule_id="SUB-07", severity="note",
            title="CRAN vacation period",
            message=f"Current month is {month_name}. CRAN volunteers may be on vacation, causing longer review times.",
            cran_says="CRAN maintainers take vacations."
        ))

    # NAME-02: Package Names Are Permanent
    if version.startswith("0.") or version == "1.0.0":
        pkg_name = desc.get("Package", "")
        findings.append(Finding(
            rule_id="NAME-02", severity="note",
            title="Package names are permanent",
            message=f"Package name '{pkg_name}' cannot be changed after CRAN acceptance. Choose carefully.",
            file=desc_file,
            cran_says="Package names cannot be changed after acceptance."
        ))

    # LIC-02: License Changes Must Be Highlighted
    license_field = desc.get("License", "")
    if "file license" in license_field.lower() or "file licence" in license_field.lower():
        findings.append(Finding(
            rule_id="LIC-02", severity="note",
            title="License changes must be highlighted",
            message="Package uses a custom license file. If updating, highlight license changes in cran-comments.md.",
            file=desc_file,
            cran_says="License changes should be noted in the cran-comments."
        ))

    # ENC-06 + DATA-06: Unmarked UTF-8 Strings in Data / Non-ASCII Characters in Data
    data_dir = path / "data"
    if data_dir.is_dir():
        data_files = list(data_dir.glob("*.rda")) + list(data_dir.glob("*.RData"))
        if data_files:
            findings.append(Finding(
                rule_id="ENC-06", severity="note",
                title="Check data files for encoding issues",
                message="Package has .rda/.RData files. Verify no unmarked UTF-8 strings or non-ASCII characters in data (requires R: tools::checkRdaFiles()).",
                file="data/",
                cran_says="Found non-ASCII strings which cannot be translated."
            ))
            findings.append(Finding(
                rule_id="DATA-06", severity="note",
                title="Check data files for non-ASCII characters",
                message="Package has .rda/.RData files. Verify data does not contain non-ASCII characters without proper encoding declaration (requires R: tools::checkRdaFiles()).",
                file="data/",
                cran_says="Found non-ASCII strings which cannot be translated."
            ))

    return findings


# --- Encoding checks ---

def check_encoding(path: Path, desc: dict) -> list[Finding]:
    """Check for encoding issues (ENC-01 through ENC-08, excluding ENC-06)."""
    findings = []
    desc_file = str(path / "DESCRIPTION")
    has_encoding_field = "Encoding" in desc

    # ENC-01: Missing Encoding field when non-ASCII present in DESCRIPTION
    desc_path = path / "DESCRIPTION"
    if desc_path.exists():
        non_ascii_lines = _has_non_ascii_bytes(desc_path)
        if non_ascii_lines and not has_encoding_field:
            first_line = non_ascii_lines[0]
            findings.append(Finding(
                rule_id="ENC-01", severity="warning",
                title="Missing Encoding field in DESCRIPTION",
                message=f"DESCRIPTION contains non-ASCII characters (line {first_line[0]}) but has no Encoding field. Add 'Encoding: UTF-8'.",
                file=desc_file, line=first_line[0],
                cran_says="If the DESCRIPTION file is not entirely in ASCII it should contain an 'Encoding' field."
            ))

    # ENC-02: Non-ASCII in R source code
    for rf in find_r_files(path):
        rel = str(rf.relative_to(path))
        non_ascii_lines = _has_non_ascii_bytes(rf)
        for lnum, line_text in non_ascii_lines:
            if is_in_comment(line_text):
                continue
            findings.append(Finding(
                rule_id="ENC-02", severity="warning",
                title="Non-ASCII character in R source",
                message=f"Non-ASCII on non-comment line. Use \\uxxxx escapes: `{line_text[:80]}`",
                file=rel, line=lnum,
                cran_says="Portable packages must use only ASCII characters in their R code."
            ))

    # ENC-03: Non-portable \x escape sequences
    for rf in find_r_files(path):
        rel = str(rf.relative_to(path))
        for lnum, line_text in scan_file(rf, r'\\x[89a-fA-F][0-9a-fA-F]'):
            if is_in_comment(line_text):
                continue
            findings.append(Finding(
                rule_id="ENC-03", severity="error",
                title="Non-portable \\x escape sequence",
                message=f"Use \\uNNNN instead of \\xNN for non-ASCII: `{line_text[:80]}`",
                file=rel, line=lnum,
                cran_says="Change strings to use \\u escapes instead of \\x."
            ))

    # ENC-04: UTF-8 BOM in source files
    files_to_check_bom: list[Path] = []
    for name in ["DESCRIPTION", "NAMESPACE"]:
        p = path / name
        if p.exists():
            files_to_check_bom.append(p)
    files_to_check_bom.extend(find_r_files(path))
    files_to_check_bom.extend(find_rd_files(path))
    files_to_check_bom.extend(_find_vignette_files(path))
    for fp in files_to_check_bom:
        if _has_bom(fp):
            rel = str(fp.relative_to(path))
            findings.append(Finding(
                rule_id="ENC-04", severity="warning",
                title=f"UTF-8 BOM in {fp.name}",
                message="File starts with UTF-8 BOM (EF BB BF). Remove the BOM — save as 'UTF-8 without BOM'.",
                file=rel, line=1,
                cran_says="Found non-ASCII strings which cannot be translated."
            ))

    # ENC-05: Missing VignetteEncoding declaration
    for vf in _find_vignette_files(path):
        rel = str(vf.relative_to(path))
        try:
            text = vf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if 'VignetteEncoding' not in text:
            findings.append(Finding(
                rule_id="ENC-05", severity="warning",
                title=f"Missing VignetteEncoding in {vf.name}",
                message="Add '%\\VignetteEncoding{UTF-8}' to the vignette preamble.",
                file=rel,
                cran_says="The encoding is not UTF-8. We will only support UTF-8 in the future."
            ))

    # ENC-07: Non-ASCII in NAMESPACE
    ns_path = path / "NAMESPACE"
    if ns_path.exists():
        non_ascii_lines = _has_non_ascii_bytes(ns_path)
        for lnum, line_text in non_ascii_lines:
            findings.append(Finding(
                rule_id="ENC-07", severity="error",
                title="Non-ASCII character in NAMESPACE",
                message=f"NAMESPACE must be ASCII-only: `{line_text[:80]}`",
                file="NAMESPACE", line=lnum,
                cran_says="Portable packages must use only ASCII characters in their NAMESPACE directives."
            ))

    # ENC-08: Non-ASCII in Rd files without encoding declaration
    for rd in find_rd_files(path):
        rel = str(rd.relative_to(path))
        non_ascii_lines = _has_non_ascii_bytes(rd)
        if not non_ascii_lines:
            continue
        if has_encoding_field:
            continue
        try:
            rd_text = rd.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if r'\encoding{' in rd_text:
            continue
        first_line = non_ascii_lines[0]
        findings.append(Finding(
            rule_id="ENC-08", severity="warning",
            title=f"Non-ASCII in {rd.name} without encoding declaration",
            message=f"Rd file has non-ASCII (line {first_line[0]}) but no encoding declared. Add 'Encoding: UTF-8' to DESCRIPTION or '\\encoding{{UTF-8}}' to the Rd file.",
            file=rel, line=first_line[0],
            cran_says="checking PDF version of manual ... WARNING"
        ))

    return findings


# --- Vignette checks ---

def check_vignettes(path: Path, desc: dict) -> list[Finding]:
    """Check vignette configuration and metadata."""
    findings = []
    vig_files = _find_vignette_files(path)
    if not vig_files:
        return findings

    # VIG-01: VignetteBuilder not declared
    vb_raw = desc.get("VignetteBuilder", "")
    vb_list = [x.strip().lower() for x in vb_raw.split(",") if x.strip()] if vb_raw else []

    if not vb_raw:
        has_non_sweave = False
        for vf in vig_files:
            if vf.suffix.lower() in ('.rmd', '.qmd'):
                has_non_sweave = True
                break
            meta = parse_vignette_metadata(vf)
            if meta["engine"] and "sweave" not in meta["engine"][1].lower():
                has_non_sweave = True
                break
        if has_non_sweave:
            findings.append(Finding(
                rule_id="VIG-01", severity="error",
                title="VignetteBuilder not declared in DESCRIPTION",
                message="Package has vignettes using a non-Sweave engine but no VignetteBuilder field. Add VignetteBuilder: knitr to DESCRIPTION and knitr to Suggests.",
                file=str(path / "DESCRIPTION"),
                cran_says="Package has 'vignettes' subdirectory but apparently no vignettes. Perhaps the 'VignetteBuilder' information is missing from the DESCRIPTION file?"
            ))
    else:
        for vf in vig_files:
            meta = parse_vignette_metadata(vf)
            if meta["engine"]:
                engine_val = meta["engine"][1]
                if "knitr::rmarkdown" in engine_val:
                    declared_pkgs = parse_desc_packages(desc)
                    if "rmarkdown" not in declared_pkgs and "rmarkdown" not in vb_list:
                        findings.append(Finding(
                            rule_id="VIG-01", severity="error",
                            title="rmarkdown not declared for knitr::rmarkdown vignettes",
                            message=f"Vignette '{vf.name}' uses knitr::rmarkdown engine but rmarkdown is not in Suggests or VignetteBuilder.",
                            file=str(vf.relative_to(path)),
                            line=meta["engine"][0],
                            cran_says="Package has 'vignettes' subdirectory but apparently no vignettes."
                        ))
                        break

    # VIG-02: Missing metadata per vignette
    placeholder_titles = {"vignette title", "vignette-title", "untitled"}
    for vf in vig_files:
        rel = str(vf.relative_to(path))
        meta = parse_vignette_metadata(vf)
        if not meta["engine"]:
            findings.append(Finding(
                rule_id="VIG-02", severity="error",
                title=f"Missing %\\VignetteEngine in {vf.name}",
                message="Every vignette must declare its processing engine. Add %\\VignetteEngine{knitr::rmarkdown} to the YAML frontmatter.",
                file=rel,
                cran_says="Files named as vignettes but with no recognized vignette engine."
            ))
        if not meta["index_entry"]:
            findings.append(Finding(
                rule_id="VIG-02", severity="error",
                title=f"Missing %\\VignetteIndexEntry in {vf.name}",
                message="Every vignette must declare its title for the vignette index.",
                file=rel,
            ))
        elif meta["index_entry"][1].lower().strip() in placeholder_titles:
            findings.append(Finding(
                rule_id="VIG-02", severity="warning",
                title=f"Placeholder VignetteIndexEntry in {vf.name}",
                message=f"VignetteIndexEntry is '{meta['index_entry'][1]}' which is a placeholder. Replace with a descriptive title.",
                file=rel, line=meta["index_entry"][0],
                cran_says="Vignette with placeholder title 'Vignette Title'."
            ))
        if not meta["encoding"]:
            findings.append(Finding(
                rule_id="VIG-02", severity="note",
                title=f"Missing %\\VignetteEncoding in {vf.name}",
                message="Add %\\VignetteEncoding{UTF-8} to the YAML frontmatter.",
                file=rel,
            ))
        elif meta["encoding"][1] != "UTF-8":
            findings.append(Finding(
                rule_id="VIG-02", severity="note",
                title=f"Non-UTF-8 VignetteEncoding in {vf.name}",
                message=f"VignetteEncoding is '{meta['encoding'][1]}'. CRAN expects UTF-8.",
                file=rel, line=meta["encoding"][0],
            ))

    # VIG-03: Stale pre-built vignettes in inst/doc
    inst_doc = path / "inst" / "doc"
    if inst_doc.is_dir():
        inst_doc_files = {f.stem: f for f in inst_doc.iterdir() if f.suffix.lower() in ('.html', '.pdf')}
        vig_sources = {f.stem: f for f in vig_files}
        for stem, src_file in vig_sources.items():
            if stem not in inst_doc_files:
                findings.append(Finding(
                    rule_id="VIG-03", severity="warning",
                    title=f"Vignette source without pre-built output: {src_file.name}",
                    message=f"'{src_file.name}' exists in vignettes/ but no matching .html/.pdf in inst/doc/.",
                    file=str(src_file.relative_to(path)),
                    cran_says="Files in 'vignettes' but not in 'inst/doc'."
                ))
        for stem, out_file in inst_doc_files.items():
            if stem not in vig_sources:
                findings.append(Finding(
                    rule_id="VIG-03", severity="warning",
                    title=f"Orphaned pre-built vignette: {out_file.name}",
                    message=f"'{out_file.name}' in inst/doc/ has no matching source in vignettes/.",
                    file=str(out_file.relative_to(path)),
                ))
        for stem in vig_sources:
            if stem in inst_doc_files:
                src_mtime = vig_sources[stem].stat().st_mtime
                out_mtime = inst_doc_files[stem].stat().st_mtime
                if src_mtime > out_mtime:
                    findings.append(Finding(
                        rule_id="VIG-03", severity="warning",
                        title=f"Stale pre-built vignette: {inst_doc_files[stem].name}",
                        message=f"Source '{vig_sources[stem].name}' is newer than pre-built '{inst_doc_files[stem].name}'. Rebuild vignettes.",
                        file=str(inst_doc_files[stem].relative_to(path)),
                    ))
        gitignore = path / ".gitignore"
        if gitignore.exists():
            gi_text = gitignore.read_text(encoding="utf-8", errors="replace")
            if "inst/doc" not in gi_text:
                findings.append(Finding(
                    rule_id="VIG-03", severity="note",
                    title="inst/doc/ not in .gitignore",
                    message="Best practice: add inst/doc to .gitignore.",
                    file=".gitignore",
                ))

    # VIG-04: Vignette build dependencies not declared
    declared_pkgs = parse_desc_packages(desc)
    pkg_name = desc.get("Package", "")
    if pkg_name:
        declared_pkgs.add(pkg_name)
    base_pkgs = {"base", "utils", "stats", "methods", "grDevices", "graphics",
                 "tools", "compiler", "datasets", "grid", "parallel", "splines",
                 "stats4", "tcltk"}
    declared_pkgs.update(base_pkgs)
    for vf in vig_files:
        used_pkgs = extract_packages_from_vignette(vf)
        undeclared = used_pkgs - declared_pkgs
        if undeclared:
            rel = str(vf.relative_to(path))
            findings.append(Finding(
                rule_id="VIG-04", severity="error",
                title=f"Undeclared vignette dependencies in {vf.name}",
                message=f"Packages used in vignette but not in DESCRIPTION: {', '.join(sorted(undeclared))}. Add them to Suggests.",
                file=rel,
                cran_says="Package suggested but not available."
            ))

    # VIG-05: HTML vignette size
    for vf in vig_files:
        if vf.suffix.lower() not in ('.rmd', '.qmd'):
            continue
        rel = str(vf.relative_to(path))
        output_formats = get_vignette_output_format(vf)
        for line_num, fmt in output_formats:
            if fmt in ("html_document", "rmarkdown::html_document"):
                findings.append(Finding(
                    rule_id="VIG-05", severity="note",
                    title=f"html_document output in {vf.name}",
                    message="Using html_document instead of html_vignette adds ~600KB. Switch to rmarkdown::html_vignette.",
                    file=rel, line=line_num,
                    cran_says="Installed size is too large."
                ))
    if inst_doc.is_dir():
        for html_file in inst_doc.glob("*.html"):
            size_mb = html_file.stat().st_size / (1024 * 1024)
            if size_mb > 1.0:
                findings.append(Finding(
                    rule_id="VIG-05", severity="warning",
                    title=f"Large HTML vignette: {html_file.name} ({size_mb:.1f}MB)",
                    message="HTML vignette exceeds 1MB. Use html_vignette output, lower DPI, and compress images.",
                    file=str(html_file.relative_to(path)),
                    cran_says="Installed size is too large."
                ))

    # VIG-08: Custom Vignette Engine Bootstrap
    vb_raw = desc.get("VignetteBuilder", "")
    if vb_raw:
        pkg_name = desc.get("Package", "")
        vb_entries = [x.strip() for x in vb_raw.split(",") if x.strip()]
        # Check if package lists itself as VignetteBuilder
        if pkg_name and pkg_name in vb_entries:
            findings.append(Finding(
                rule_id="VIG-08", severity="warning",
                title="Package lists itself as VignetteBuilder",
                message=f"VignetteBuilder includes '{pkg_name}' — the package itself. This creates a bootstrap problem: the engine won't be available during R CMD check.",
                file=str(path / "DESCRIPTION"),
                cran_says="Package has 'vignettes' subdirectory but apparently no vignettes."
            ))
        # Check if VignetteBuilder package is in Suggests but not Imports
        imports_raw = desc.get("Imports", "")
        imports_pkgs = set()
        if imports_raw:
            for entry in imports_raw.split(","):
                p = entry.strip().split("(")[0].strip()
                if p:
                    imports_pkgs.add(p)
        suggests_raw = desc.get("Suggests", "")
        suggests_pkgs = set()
        if suggests_raw:
            for entry in suggests_raw.split(","):
                p = entry.strip().split("(")[0].strip()
                if p:
                    suggests_pkgs.add(p)
        for vb_entry in vb_entries:
            if vb_entry == pkg_name:
                continue  # Already flagged above
            if vb_entry in suggests_pkgs and vb_entry not in imports_pkgs:
                findings.append(Finding(
                    rule_id="VIG-08", severity="warning",
                    title=f"VignetteBuilder '{vb_entry}' is in Suggests, not Imports",
                    message=f"'{vb_entry}' is listed as VignetteBuilder but only in Suggests. Move to Imports to ensure availability during vignette building.",
                    file=str(path / "DESCRIPTION"),
                    cran_says="Package has 'vignettes' subdirectory but apparently no vignettes."
                ))

    # VIG-06: Vignette Data Files in Wrong Location (heuristic)
    _data_read_patterns = [
        r'\bread\.csv\s*\(', r'\breadRDS\s*\(', r'\bload\s*\(',
        r'\bread\.table\s*\(', r'\bread\.delim\s*\(',
        r'\bread_csv\s*\(', r'\bfread\s*\(',
    ]
    data_read_combined = '|'.join(_data_read_patterns)
    for vf in vig_files:
        rel = str(vf.relative_to(path))
        try:
            vig_text = vf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        in_chunk = False
        for i, vline in enumerate(vig_text.splitlines(), 1):
            if re.match(r'^```\{r', vline):
                in_chunk = True
                continue
            if in_chunk and vline.strip().startswith('```'):
                in_chunk = False
                continue
            if not in_chunk:
                continue
            if re.search(data_read_combined, vline):
                # Check for suspicious relative paths
                path_match = re.search(r'["\'](\.\./[^"\']+|data/[^"\']+)["\']', vline)
                if path_match:
                    ref_path = path_match.group(1)
                    findings.append(Finding(
                        rule_id="VIG-06", severity="note",
                        title=f"Possibly incorrect data file path in {vf.name}",
                        message=f"Vignette references '{ref_path}'. Data files for vignettes should be in inst/extdata/ or vignettes/.",
                        file=rel, line=i,
                        cran_says="Vignette data files should be accessible at vignette build time."
                    ))
                    break  # One finding per file

    # VIG-07: Vignette CPU Time (heuristic)
    _heavy_vignette_patterns = [
        (r'\bparallel::', "parallel:: usage"),
        (r'\bforeach\b', "foreach usage"),
        (r'\bfuture::', "future:: usage"),
        (r'\bfurrr::', "furrr:: usage"),
        (r'\bmicrobenchmark\b', "microbenchmark usage"),
        (r'\bbench::mark\b', "bench::mark usage"),
    ]
    for vf in vig_files:
        rel = str(vf.relative_to(path))
        try:
            vig_text = vf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for heavy_pat, heavy_desc in _heavy_vignette_patterns:
            if re.search(heavy_pat, vig_text):
                findings.append(Finding(
                    rule_id="VIG-07", severity="note",
                    title=f"Potentially heavy computation in {vf.name}",
                    message=f"Vignette contains {heavy_desc}. Consider pre-computing results or using eval=FALSE for heavy chunks. CRAN limits vignette build time.",
                    file=rel,
                    cran_says="Vignette build time exceeded limit."
                ))
                break  # One finding per vignette

    return findings


# --- NAMESPACE checks ---

def check_namespace(path: Path, desc: dict) -> list[Finding]:
    """Check NAMESPACE for CRAN policy violations (NS-01 through NS-05)."""
    findings = []
    ns_file = path / "NAMESPACE"
    if not ns_file.exists():
        return findings
    ns_rel = "NAMESPACE"
    ns = parse_namespace(path)

    # NS-01: Import conflicts
    func_sources: dict[str, list[tuple[str, int]]] = {}
    for pkg, fun, line_num in ns["import_from"]:
        func_sources.setdefault(fun, []).append((pkg, line_num))
    for fun, sources in func_sources.items():
        unique_pkgs = set(s[0] for s in sources)
        if len(unique_pkgs) > 1:
            line = sources[0][1]
            findings.append(Finding(
                rule_id="NS-01", severity="warning",
                title=f"Import conflict: '{fun}' imported from multiple packages",
                message=f"Function '{fun}' is imported from: {', '.join(sorted(unique_pkgs))}. This causes 'Replacing previous import' warnings.",
                file=ns_rel, line=line,
                cran_says="Replacing previous import by another import.",
            ))
    if len(ns["imports"]) > 1:
        pkgs = [i[0] for i in ns["imports"]]
        findings.append(Finding(
            rule_id="NS-01", severity="warning",
            title="Multiple full namespace imports risk collisions",
            message=f"import() used for multiple packages: {', '.join(pkgs)}.",
            file=ns_rel, line=ns["imports"][0][1],
            cran_says="Replacing previous import by another import.",
        ))

    # NS-02: Prefer importFrom over import
    accepted_full_import = {"methods"}
    for pkg, line_num in ns["imports"]:
        if pkg.lower() in {p.lower() for p in accepted_full_import}:
            continue
        findings.append(Finding(
            rule_id="NS-02", severity="note",
            title=f"Full namespace import of '{pkg}'",
            message=f"import({pkg}) imports the entire namespace. Prefer importFrom({pkg}, fun1, fun2, ...).",
            file=ns_rel, line=line_num,
            cran_says="Using importFrom selectively rather than import is good practice.",
        ))

    # NS-03: S3 method exported but not registered
    registered = set()
    for generic, cls, _ in ns["s3methods"]:
        registered.add(f"{generic}.{cls}")
    for fun, line_num in ns["exports"]:
        if "." not in fun:
            continue
        parts = fun.split(".", 1)
        generic_candidate = parts[0]
        class_candidate = parts[1] if len(parts) > 1 else ""
        if not class_candidate:
            continue
        if generic_candidate in KNOWN_S3_GENERICS and fun not in registered:
            findings.append(Finding(
                rule_id="NS-03", severity="note",
                title=f"S3 method '{fun}' exported but not registered",
                message=f"Use S3method({generic_candidate}, {class_candidate}) instead of export({fun}).",
                file=ns_rel, line=line_num,
                cran_says="Found the following apparent S3 methods exported but not registered.",
            ))

    # NS-04: Broad exportPattern
    for pattern, line_num in ns["export_patterns"]:
        is_broad = pattern in (".", "^[[:alpha:]]", "^[^\\.]", "^[^.]",
                               "^[[:alpha:]]+", "^[[:alpha:]].*")
        if not is_broad and re.match(r'^\^?\[', pattern) and len(pattern) < 20:
            if "alpha" in pattern or ("^" in pattern and "." in pattern):
                is_broad = True
        if is_broad:
            findings.append(Finding(
                rule_id="NS-04", severity="note",
                title=f"Broad exportPattern: '{pattern}'",
                message=f"exportPattern(\"{pattern}\") exports most/all functions. Use explicit export() directives.",
                file=ns_rel, line=line_num,
                cran_says="Exporting all functions with exportPattern is strongly discouraged.",
            ))

    # NS-05: Depends vs Imports misuse
    depends_pkgs = parse_description_depends(desc)
    accepted_depends = {"R", "methods"}
    ns_imported = set()
    for pkg, _ in ns["imports"]:
        ns_imported.add(pkg)
    for pkg, _, _ in ns["import_from"]:
        ns_imported.add(pkg)
    for pkg in depends_pkgs:
        if pkg in accepted_depends:
            continue
        message = f"Package '{pkg}' is in Depends but should likely be in Imports."
        if pkg not in ns_imported:
            message += f" '{pkg}' is not imported in NAMESPACE either."
        findings.append(Finding(
            rule_id="NS-05", severity="note",
            title=f"'{pkg}' in Depends instead of Imports",
            message=message, file="DESCRIPTION",
            cran_says="The Depends field should nowadays be used rarely.",
        ))

    # NS-07: Re-Export Documentation Requirements
    # Find functions that are both importFrom'd and export'd — these are re-exports
    imported_funcs: dict[str, str] = {}  # func -> pkg
    for pkg, fun, _ in ns["import_from"]:
        imported_funcs[fun] = pkg
    exported_funcs = set()
    for fun, _ in ns["exports"]:
        exported_funcs.add(fun)
    reexports = exported_funcs & set(imported_funcs.keys())
    if reexports:
        man_dir = path / "man"
        documented = set()
        if man_dir.is_dir():
            for rd in sorted(man_dir.glob("*.Rd")):
                try:
                    text = rd.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                for m in re.finditer(r"\\alias\{([^}]+)\}", text):
                    # Strip Rd-level backslash escapes (e.g., \% -> %)
                    alias = m.group(1).replace("\\", "")
                    documented.add(alias)
                    # Also add the raw form for exact match
                    documented.add(m.group(1))
        for fun in sorted(reexports):
            if fun not in documented:
                findings.append(Finding(
                    rule_id="NS-07", severity="note",
                    title=f"Re-exported '{fun}' lacks documentation",
                    message=f"'{fun}' is imported from '{imported_funcs[fun]}' and re-exported but has no .Rd documentation.",
                    file=ns_rel,
                    cran_says="Please add \\value to .Rd files regarding exported methods."
                ))

    return findings


# --- Data checks ---

def check_data(path: Path, desc: dict) -> list[Finding]:
    """Check data directory for CRAN policy violations."""
    findings = []
    data_dir = path / "data"
    man_dir = path / "man"
    r_dir = path / "R"
    desc_file = str(path / "DESCRIPTION")
    has_data_dir = data_dir.is_dir()
    lazy_data = desc.get("LazyData", "").strip().lower() in ("true", "yes")

    # DATA-02: LazyData without data/ directory
    if lazy_data and not has_data_dir:
        findings.append(Finding(
            rule_id="DATA-02", severity="note",
            title="LazyData set without data/ directory",
            message="DESCRIPTION has 'LazyData: true' but no data/ directory exists. Remove LazyData field.",
            file=desc_file,
            cran_says="'LazyData' is specified without a 'data' directory",
        ))

    if not has_data_dir:
        # DATA-08: Check sysdata.rda even without data/
        sysdata = path / "R" / "sysdata.rda"
        if sysdata.exists():
            size_mb = sysdata.stat().st_size / (1024 * 1024)
            if size_mb > 1:
                findings.append(Finding(
                    rule_id="DATA-08", severity="note",
                    title=f"Large internal data: R/sysdata.rda ({size_mb:.1f}MB)",
                    message="R/sysdata.rda is large and contributes to package size.",
                    file="R/sysdata.rda",
                    cran_says="Packages should be of the minimum necessary size.",
                ))
        return findings

    data_files = [f for f in sorted(data_dir.iterdir()) if f.is_file()]
    rda_datasets = _dataset_names_from_data_dir(data_dir)

    # DATA-01: Undocumented datasets
    if rda_datasets:
        documented = _find_documented_datasets_rd(man_dir) | _find_documented_datasets_roxygen(r_dir)
        for name, filepath in rda_datasets:
            if name not in documented:
                findings.append(Finding(
                    rule_id="DATA-01", severity="error",
                    title=f"Undocumented dataset: {name}",
                    message=f"Dataset '{name}' (from {filepath.name}) has no documentation.",
                    file=str(filepath.relative_to(path)),
                    cran_says="Undocumented data sets. All user-level objects in a package should have documentation entries.",
                ))

    # DATA-03: Missing LazyData when data/ has .rda files
    has_rda = any(f.suffix.lower() in (".rda", ".rdata") for f in data_files)
    if has_rda and not lazy_data:
        findings.append(Finding(
            rule_id="DATA-03", severity="note",
            title="Missing LazyData field",
            message="data/ contains .rda/.RData files but DESCRIPTION lacks 'LazyData: true'.",
            file=desc_file,
            cran_says="If you're shipping .rda files below data/, include LazyData: true in DESCRIPTION.",
        ))

    # DATA-05: Data size exceeds limits
    total_size = sum(f.stat().st_size for f in data_files if f.is_file())
    total_mb = total_size / (1024 * 1024)
    if total_mb > 5:
        findings.append(Finding(
            rule_id="DATA-05", severity="error",
            title=f"Data directory exceeds 5MB ({total_mb:.1f}MB)",
            message="CRAN policy: 'neither data nor documentation should exceed 5MB'.",
            file="data/",
            cran_says="Data exceeded 5MB limit.",
        ))
    elif total_mb > 1:
        findings.append(Finding(
            rule_id="DATA-05", severity="warning",
            title=f"Data directory exceeds 1MB ({total_mb:.1f}MB)",
            message="R-pkgs.org recommends data under 1MB. Consider better compression.",
            file="data/",
            cran_says="Packages should be of the minimum necessary size.",
        ))

    # DATA-04: Suboptimal compression
    if lazy_data and total_mb > 1:
        lazy_compression = desc.get("LazyDataCompression", "").strip()
        if not lazy_compression:
            findings.append(Finding(
                rule_id="DATA-04", severity="warning",
                title="Missing LazyDataCompression for large data",
                message=f"LazyData is true and data/ is {total_mb:.1f}MB but LazyDataCompression is not set.",
                file=desc_file,
                cran_says="significantly better compression could be obtained by using R CMD build --resave-data",
            ))
    for f in data_files:
        if f.suffix.lower() in (".rda", ".rdata"):
            size_kb = f.stat().st_size / 1024
            if size_kb > 100:
                findings.append(Finding(
                    rule_id="DATA-04", severity="note",
                    title=f"Large data file: {f.name} ({size_kb:.0f}KB)",
                    message="Consider running tools::resaveRdaFiles() with compress='auto'.",
                    file=str(f.relative_to(path)),
                    cran_says="significantly better compression could be obtained",
                ))

    # DATA-09: Invalid data file formats
    for f in data_files:
        if not _is_valid_data_extension(f):
            ext = f.suffix
            msg = f"File '{f.name}' has invalid extension '{ext}' for data/ directory."
            if ext.lower() == ".rds":
                msg += " .rds files are not allowed in data/ -- move to inst/extdata/."
            else:
                msg += " Allowed: .rda, .RData, .R, .tab, .txt, .csv (optionally compressed)."
            findings.append(Finding(
                rule_id="DATA-09", severity="warning",
                title=f"Invalid file format in data/: {f.name}",
                message=msg, file=str(f.relative_to(path)),
                cran_says="checking contents of 'data' directory",
            ))

    # DATA-07: Serialization Version Incompatibility
    # Check .rda/.RData files for serialization v3 format
    depends_r_version = None
    depends_str = desc.get("Depends", "")
    r_version_match = re.search(r'R\s*\(\s*>=\s*([0-9.]+)\s*\)', depends_str)
    if r_version_match:
        depends_r_version = r_version_match.group(1)
    for f in data_files:
        if f.suffix.lower() not in (".rda", ".rdata"):
            continue
        try:
            with open(f, 'rb') as fh:
                header = fh.read(10)
        except Exception:
            continue
        is_v3 = False
        # Check for uncompressed RDX3/RDA3 magic
        if header[:4] in (b'RDX3', b'RDA3'):
            is_v3 = True
        # Check for gzip-compressed data (starts with 1f 8b)
        elif header[:2] == b'\x1f\x8b':
            import gzip
            try:
                with gzip.open(f, 'rb') as gz:
                    inner = gz.read(10)
                if inner[:4] in (b'RDX3', b'RDA3'):
                    is_v3 = True
            except Exception:
                pass
        # Check for xz-compressed data (starts with FD 37 7A 58 5A 00)
        elif header[:6] == b'\xfd7zXZ\x00':
            import lzma
            try:
                with lzma.open(f, 'rb') as xz:
                    inner = xz.read(10)
                if inner[:4] in (b'RDX3', b'RDA3'):
                    is_v3 = True
            except Exception:
                pass
        # Check for bz2-compressed data (starts with BZ)
        elif header[:2] == b'BZ':
            import bz2
            try:
                with bz2.open(f, 'rb') as bz:
                    inner = bz.read(10)
                if inner[:4] in (b'RDX3', b'RDA3'):
                    is_v3 = True
            except Exception:
                pass
        if is_v3:
            rel_f = str(f.relative_to(path))
            if depends_r_version:
                # Parse version to check if >= 3.5.0
                parts = depends_r_version.split(".")
                try:
                    major, minor = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
                except ValueError:
                    major, minor = 0, 0
                if major < 3 or (major == 3 and minor < 5):
                    findings.append(Finding(
                        rule_id="DATA-07", severity="warning",
                        title=f"Serialization v3 data incompatible with declared R version",
                        message=f"'{f.name}' uses serialization v3 (requires R >= 3.5.0) but Depends declares R >= {depends_r_version}.",
                        file=rel_f,
                        cran_says="Added dependency on R >= 3.5.0 because serialized objects in serialize/load version 3 cannot be read in older versions of R."
                    ))
            else:
                findings.append(Finding(
                    rule_id="DATA-07", severity="warning",
                    title=f"Serialization v3 data adds implicit R >= 3.5.0 dependency",
                    message=f"'{f.name}' uses serialization v3. Add 'Depends: R (>= 3.5.0)' to DESCRIPTION or re-save with version 2.",
                    file=rel_f,
                    cran_says="Added dependency on R >= 3.5.0 because serialized objects in serialize/load version 3 cannot be read in older versions of R."
                ))

    # DATA-08: sysdata.rda
    sysdata = path / "R" / "sysdata.rda"
    if sysdata.exists():
        size_mb = sysdata.stat().st_size / (1024 * 1024)
        if size_mb > 1:
            findings.append(Finding(
                rule_id="DATA-08", severity="note",
                title=f"Large internal data: R/sysdata.rda ({size_mb:.1f}MB)",
                message="R/sysdata.rda is large and contributes to package size.",
                file="R/sysdata.rda",
                cran_says="Packages should be of the minimum necessary size.",
            ))

    return findings


# --- System requirements checks ---

def check_system_requirements(path: Path, desc: dict) -> list[Finding]:
    """Check SystemRequirements declarations."""
    findings = []
    sysreqs_lower = desc.get("SystemRequirements", "").lower()

    # SYS-01: Undeclared system libraries
    includes = _find_src_includes(path)
    for lib, locations in includes.items():
        if lib.lower() not in sysreqs_lower:
            first_file, first_line = locations[0]
            file_list = ", ".join(f"{f}:{ln}" for f, ln in locations[:3])
            if len(locations) > 3:
                file_list += f" (+{len(locations) - 3} more)"
            findings.append(Finding(
                rule_id="SYS-01", severity="warning",
                title=f"Undeclared system library: {lib}",
                message=f"Compiled code includes headers for {lib} but SystemRequirements does not mention it. Found in: {file_list}",
                file=first_file, line=first_line,
                cran_says="Packages using external libraries should declare them in SystemRequirements.",
            ))

    # SYS-02: Undeclared external programs
    r_dir = path / "R"
    if r_dir.is_dir():
        known_programs = {
            "pandoc": "pandoc", "python": "Python", "python3": "Python",
            "java": "Java", "jags": "JAGS", "perl": "Perl", "php": "PHP",
            "node": "Node.js", "npm": "Node.js", "cargo": "Rust (cargo)",
            "rustc": "Rust (rustc)", "cmake": "CMake",
        }
        for rf in sorted(r_dir.glob("*.R")):
            try:
                lines = rf.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            rel = str(rf.relative_to(path))
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                m = re.search(
                    r'(?:system2?\s*\(\s*|processx::run\s*\(\s*)["\'](\w+)["\']',
                    stripped,
                )
                if m:
                    prog = m.group(1).lower()
                    if prog in known_programs:
                        lib_name = known_programs[prog]
                        if lib_name.lower() not in sysreqs_lower:
                            findings.append(Finding(
                                rule_id="SYS-02", severity="warning",
                                title=f"Undeclared external program: {lib_name}",
                                message=f"Code calls {prog} via system()/system2() but SystemRequirements does not mention {lib_name}.",
                                file=rel, line=i,
                                cran_says="If your package requires one of these interpreters or an extension then this should be declared in the SystemRequirements field.",
                            ))

    # SYS-05: Java .class/.jar files require source
    java_files = []
    for ext in ("*.jar", "*.class"):
        for f in path.rglob(ext):
            if ".git" not in str(f):
                java_files.append(f)
    if java_files:
        java_dir = path / "java"
        if not java_dir.is_dir():
            file_names = [str(f.relative_to(path)) for f in java_files[:5]]
            file_list = ", ".join(file_names)
            if len(java_files) > 5:
                file_list += f" (+{len(java_files) - 5} more)"
            findings.append(Finding(
                rule_id="SYS-05", severity="error",
                title="Java .class/.jar files without java/ source directory",
                message=f"Found {len(java_files)} Java binary file(s) ({file_list}) but no top-level java/ directory with sources.",
                file=str(java_files[0].relative_to(path)),
                cran_says="For Java .class and .jar files, the sources should be in a top-level java directory.",
            ))
        if "java" not in sysreqs_lower and "jdk" not in sysreqs_lower and "jre" not in sysreqs_lower:
            findings.append(Finding(
                rule_id="SYS-05", severity="warning",
                title="Java files present but Java not in SystemRequirements",
                message="Package contains .jar/.class files but SystemRequirements does not mention Java.",
                file="DESCRIPTION",
                cran_says="For Java .class and .jar files, the sources should be in a top-level java directory.",
            ))

    # SYS-06: Contradictory C++ standard specifications
    makevars_standards = _parse_makevars_cxx_std(path)
    sysreqs_cxx = _parse_sysreqs_cxx_standard(desc)
    if sysreqs_cxx and makevars_standards:
        for makevars_std, mv_file, mv_line in makevars_standards:
            if makevars_std != sysreqs_cxx:
                findings.append(Finding(
                    rule_id="SYS-06", severity="warning",
                    title="Contradictory C++ standard specifications",
                    message=f"SystemRequirements declares {sysreqs_cxx} but {mv_file} sets CXX_STD = {makevars_std}.",
                    file=mv_file, line=mv_line,
                    cran_says="Contradictory C++ standard specifications give a warning.",
                ))
    if sysreqs_cxx and sysreqs_cxx in ("C++11", "C++14"):
        findings.append(Finding(
            rule_id="SYS-06", severity="warning",
            title=f"Deprecated C++ standard in SystemRequirements: {sysreqs_cxx}",
            message=f"SystemRequirements declares {sysreqs_cxx} which is deprecated. R defaults to C++17+.",
            file="DESCRIPTION",
            cran_says="C++11/C++14 specifications are deprecated since R 4.3.",
        ))

    # SYS-07: USE_C17 opt-out cross-reference
    has_use_c17 = "use_c17" in sysreqs_lower
    if has_use_c17:
        src_dir = path / "src"
        has_c_files = False
        if src_dir.is_dir():
            has_c_files = bool(list(src_dir.glob("*.c")) or list(src_dir.glob("*.h")))
        if not has_c_files:
            findings.append(Finding(
                rule_id="SYS-07", severity="note",
                title="USE_C17 declared but no C source files found",
                message="SystemRequirements contains USE_C17 but no .c/.h files were found in src/.",
                file="DESCRIPTION",
                cran_says="Packages can opt out of C23 via SystemRequirements: USE_C17.",
            ))

    # SYS-03: C++20 Default Standard Transition
    makevars_cxx = _parse_makevars_cxx_std(path)
    for std_val, mv_file, mv_line in makevars_cxx:
        if std_val in ("C++11", "C++14"):
            # Already covered by COMP-06, but emit SYS-03 NOTE too
            findings.append(Finding(
                rule_id="SYS-03", severity="note",
                title=f"Deprecated C++ standard: {std_val}",
                message=f"{mv_file} sets CXX_STD to {std_val} which is being deprecated. R 4.6+ defaults to C++20.",
                file=mv_file, line=mv_line,
                cran_says="R 4.6.0: C++20 is now the default C++ standard where available."
            ))
        elif std_val == "C++17":
            findings.append(Finding(
                rule_id="SYS-03", severity="note",
                title="Explicit C++17 standard set — review C++20 compatibility",
                message=f"{mv_file} sets CXX_STD to CXX17. R 4.6+ defaults to C++20. Verify compatibility or remove CXX_STD line.",
                file=mv_file, line=mv_line,
                cran_says="R 4.6.0: C++20 is now the default C++ standard where available."
            ))

    # SYS-04: Configure Script Missing for System Libraries
    src_dir = path / "src"
    if src_dir.is_dir():
        has_compiled_code = bool(
            list(src_dir.glob("*.c")) or list(src_dir.glob("*.cpp")) or
            list(src_dir.glob("*.cc")) or list(src_dir.glob("*.f")) or
            list(src_dir.glob("*.f90")) or list(src_dir.glob("*.f95"))
        )
        has_sysreqs = bool(desc.get("SystemRequirements", "").strip())
        if has_compiled_code and has_sysreqs:
            has_configure = (
                (path / "configure").exists() or
                (path / "configure.ac").exists() or
                (path / "configure.in").exists()
            )
            if not has_configure:
                findings.append(Finding(
                    rule_id="SYS-04", severity="note",
                    title="Missing configure script for package with SystemRequirements",
                    message=f"Package has compiled code and SystemRequirements but no configure/configure.ac/configure.in script.",
                    file="DESCRIPTION",
                    cran_says="Packages should check for the presence of required tools."
                ))

    return findings


# --- Maintainer email checks ---

def check_maintainer_email(path: Path, desc: dict) -> list[Finding]:
    """Check maintainer email quality against CRAN policies."""
    findings = []
    desc_file = str(path / "DESCRIPTION")
    authors_r = desc.get("Authors@R", "")
    if not authors_r:
        return findings

    # EMAIL-02: cre without email
    if _has_cre_without_email(authors_r):
        findings.append(Finding(
            rule_id="EMAIL-02", severity="error",
            title="Maintainer (cre) has no email in Authors@R",
            message="The person with 'cre' role must have an email argument.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show both the name and email address of a single designated maintainer.",
        ))
        return findings

    email = extract_cre_email(authors_r)
    if not email:
        return findings

    email_lower = email.lower()

    # EMAIL-04: Basic format validation
    if "@" not in email or email.count("@") != 1:
        findings.append(Finding(
            rule_id="EMAIL-04", severity="error",
            title="Invalid email format for maintainer",
            message=f"Email '{email}' does not contain exactly one '@' symbol.",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings

    local_part, domain = email_lower.rsplit("@", 1)
    if not local_part:
        findings.append(Finding(
            rule_id="EMAIL-04", severity="error",
            title="Empty local part in maintainer email",
            message=f"Email '{email}' has an empty local part (before @).",
            file=desc_file,
        ))
        return findings
    if "." not in domain:
        findings.append(Finding(
            rule_id="EMAIL-04", severity="error",
            title="Invalid domain in maintainer email",
            message=f"Email domain '{domain}' has no dot.",
            file=desc_file,
        ))
        return findings
    if " " in email:
        findings.append(Finding(
            rule_id="EMAIL-04", severity="error",
            title="Space in maintainer email address",
            message=f"Email '{email}' contains spaces.",
            file=desc_file,
        ))
        return findings

    # EMAIL-06: Noreply/automated addresses
    for pattern in NOREPLY_PATTERNS:
        if re.search(pattern, email_lower):
            findings.append(Finding(
                rule_id="EMAIL-06", severity="error",
                title="Noreply/automated email address",
                message=f"Email '{email}' is a noreply or automated address.",
                file=desc_file,
                cran_says="That contact address must be kept up to date, and be usable for information mailed by the CRAN team.",
            ))
            return findings

    # EMAIL-01: Mailing list addresses
    if domain in MAILING_LIST_DOMAINS:
        findings.append(Finding(
            rule_id="EMAIL-01", severity="error",
            title="Maintainer email is a mailing list address",
            message=f"Email '{email}' uses mailing list domain '{domain}'. CRAN requires a personal email.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show both the name and email address of a single designated maintainer (a person, not a mailing list).",
        ))
        return findings
    local_base = local_part.split(".")[0] if "." in local_part else local_part
    if local_base in MAILING_LIST_LOCAL_PREFIXES:
        findings.append(Finding(
            rule_id="EMAIL-01", severity="error",
            title="Maintainer email looks like a generic/team address",
            message=f"Email '{email}' starts with '{local_base}@' which suggests a team address.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show the email address of a single designated maintainer (a person, not a mailing list).",
        ))
        return findings
    for keyword in MAILING_LIST_LOCAL_KEYWORDS:
        if keyword in local_part:
            findings.append(Finding(
                rule_id="EMAIL-01", severity="error",
                title="Maintainer email contains mailing list keyword",
                message=f"Email '{email}' contains '{keyword}' which suggests a mailing list.",
                file=desc_file,
                cran_says="The package's DESCRIPTION file must show the email address of a single designated maintainer.",
            ))
            return findings
    if domain.startswith("lists."):
        findings.append(Finding(
            rule_id="EMAIL-01", severity="error",
            title="Maintainer email is on a lists.* domain",
            message=f"Email '{email}' uses domain '{domain}' which is a mailing list server.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show the email address of a single designated maintainer.",
        ))
        return findings

    # EMAIL-04: Placeholder domains and patterns
    if domain in PLACEHOLDER_DOMAINS:
        findings.append(Finding(
            rule_id="EMAIL-04", severity="error",
            title="Placeholder email domain",
            message=f"Email '{email}' uses placeholder domain '{domain}'.",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings
    for pattern in PLACEHOLDER_PATTERNS:
        if re.match(pattern, email_lower):
            findings.append(Finding(
                rule_id="EMAIL-04", severity="error",
                title="Placeholder email address",
                message=f"Email '{email}' looks like a template placeholder.",
                file=desc_file,
                cran_says="a valid (RFC 2822) email address in angle brackets",
            ))
            return findings

    # EMAIL-03: Disposable email domains
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        findings.append(Finding(
            rule_id="EMAIL-03", severity="warning",
            title="Disposable email domain",
            message=f"Email '{email}' uses disposable domain '{domain}'. Use a permanent provider.",
            file=desc_file,
            cran_says="Make sure this email address is likely to be around for a while.",
        ))

    # EMAIL-05: Institutional email longevity warning
    for pattern in ACADEMIC_DOMAIN_PATTERNS:
        if re.search(pattern, domain):
            findings.append(Finding(
                rule_id="EMAIL-05", severity="note",
                title="Institutional email may not outlast career changes",
                message=f"Email '{email}' uses an academic domain. Consider a stable personal email.",
                file=desc_file,
                cran_says="Too many people let their maintainer addresses run out of service.",
            ))
            break

    return findings


# --- inst/ directory checks ---

def check_inst_directory(path: Path, desc: dict) -> list[Finding]:
    """Check inst/ directory for CRAN policy violations."""
    findings = []
    inst_dir = path / "inst"
    if not inst_dir.is_dir():
        return findings

    # INST-01: Hidden files in inst/
    for f in inst_dir.rglob("*"):
        if not f.is_file():
            continue
        name = f.name
        if name.startswith(".") or name in HIDDEN_FILE_PATTERNS:
            findings.append(Finding(
                rule_id="INST-01", severity="error",
                title=f"Hidden file in inst/: {name}",
                message=f"Remove '{name}' from inst/ or add to .Rbuildignore.",
                file=str(f.relative_to(path)),
                cran_says="Found the following hidden files and directories.",
            ))

    # INST-02: Deprecated CITATION format
    citation_file = inst_dir / "CITATION"
    if citation_file.is_file():
        try:
            text = citation_file.read_text(encoding="utf-8", errors="replace")
            for func_name, pattern in DEPRECATED_CITATION_PATTERNS.items():
                for i, line in enumerate(text.splitlines(), 1):
                    if re.search(pattern, line):
                        replacement = {
                            "citEntry": "bibentry()", "personList": "c() on person objects",
                            "as.personList": "c() on person objects",
                            "citHeader": "header argument to bibentry()",
                            "citFooter": "footer argument to bibentry()",
                        }[func_name]
                        findings.append(Finding(
                            rule_id="INST-02", severity="warning",
                            title=f"Deprecated {func_name}() in CITATION",
                            message=f"Replace {func_name}() with {replacement}.",
                            file=str(citation_file.relative_to(path)), line=i,
                            cran_says=f"Package CITATION file contains call(s) to old-style {func_name}().",
                        ))
                        break
        except Exception:
            pass

    # INST-03: inst/doc conflicts with vignettes/
    vignettes_dir = path / "vignettes"
    inst_doc_dir = inst_dir / "doc"
    if vignettes_dir.is_dir() and inst_doc_dir.is_dir():
        has_vignette_sources = any(
            f.suffix in VIGNETTE_SOURCE_EXTS for f in vignettes_dir.iterdir() if f.is_file()
        )
        if has_vignette_sources:
            inst_doc_files = [f for f in inst_doc_dir.iterdir() if f.is_file()]
            has_output = any(f.suffix in VIGNETTE_OUTPUT_EXTS for f in inst_doc_files)
            has_source = any(f.suffix in VIGNETTE_SOURCE_EXTS for f in inst_doc_files)
            if has_output:
                findings.append(Finding(
                    rule_id="INST-03", severity="warning",
                    title="inst/doc contains pre-built vignettes",
                    message="Delete inst/doc/ from the source tree. R CMD build populates it automatically.",
                    file="inst/doc",
                    cran_says="inst/doc directory should not contain pre-built vignettes if vignettes/ directory exists.",
                ))
            if has_source:
                source_files = [f.name for f in inst_doc_files if f.suffix in VIGNETTE_SOURCE_EXTS]
                findings.append(Finding(
                    rule_id="INST-03", severity="warning",
                    title="Vignette sources in inst/doc/ instead of vignettes/",
                    message=f"Move vignette sources to vignettes/: {', '.join(source_files[:5])}",
                    file="inst/doc",
                    cran_says="Vignette sources must be in vignettes/, not inst/doc/.",
                ))

    # INST-04: Reserved subdirectory names and embedded packages
    for d in sorted(inst_dir.iterdir()):
        if not d.is_dir():
            continue
        if d.name in RESERVED_INST_DIRS:
            findings.append(Finding(
                rule_id="INST-04", severity="error",
                title=f"Reserved directory name: inst/{d.name}",
                message=f"inst/{d.name}/ conflicts with R's standard package directory. Rename it.",
                file=str(d.relative_to(path)),
                cran_says="inst/ subdirectories should not interfere with R's standard directories.",
            ))
    for desc_file_found in inst_dir.rglob("DESCRIPTION"):
        if desc_file_found.parent == inst_dir:
            continue
        rel_dir = desc_file_found.parent.relative_to(path)
        findings.append(Finding(
            rule_id="INST-04", severity="error",
            title=f"Embedded package in {rel_dir}",
            message=f"Found DESCRIPTION file at {desc_file_found.relative_to(path)}, indicating an embedded package.",
            file=str(desc_file_found.relative_to(path)),
            cran_says="Subdirectory appears to contain a package.",
        ))

    # INST-05: Missing copyright for bundled third-party code
    third_party_found = []
    for d in inst_dir.iterdir():
        if d.is_dir() and d.name.lower() in THIRD_PARTY_DIRS:
            code_exts = {".js", ".css", ".c", ".cpp", ".h", ".hpp", ".ts", ".min.js", ".min.css"}
            has_code = any(f.suffix in code_exts for f in d.rglob("*") if f.is_file())
            if has_code:
                third_party_found.append(d.name)
    hw_dir = inst_dir / "htmlwidgets"
    if hw_dir.is_dir():
        lib_dir = hw_dir / "lib"
        if lib_dir.is_dir() and any(lib_dir.iterdir()):
            if "htmlwidgets" not in third_party_found:
                third_party_found.append("htmlwidgets/lib")
    if third_party_found:
        has_copyrights_file = (inst_dir / "COPYRIGHTS").is_file()
        has_copyright_field = "Copyright" in desc
        authors_r = desc.get("Authors@R", "")
        cph_count = len(re.findall(r'"cph"', authors_r)) + len(re.findall(r"'cph'", authors_r))
        if not has_copyrights_file and not has_copyright_field and cph_count < 2:
            dirs_str = ", ".join(f"inst/{d}" for d in third_party_found[:5])
            findings.append(Finding(
                rule_id="INST-05", severity="warning",
                title="Bundled third-party code may lack copyright attribution",
                message=f"Found third-party code in {dirs_str}. Add inst/COPYRIGHTS file or 'cph' roles in Authors@R.",
                file="DESCRIPTION",
                cran_says="Where copyrights are held by an entity other than the package authors, this should preferably be indicated via 'cph' roles.",
            ))

    # INST-06: Large inst/ subdirectory sizes
    for d in sorted(inst_dir.iterdir()):
        if not d.is_dir():
            continue
        total_size = 0
        large_files = []
        for f in d.rglob("*"):
            if not f.is_file():
                continue
            try:
                fsize = f.stat().st_size
            except OSError:
                continue
            total_size += fsize
            if fsize > LARGE_FILE_THRESHOLD:
                large_files.append((f, fsize))
        if total_size > SUBDIR_SIZE_THRESHOLD:
            size_mb = total_size / (1024 * 1024)
            rel_dir = d.relative_to(path)
            msg = f"inst/{d.name}/ is {size_mb:.1f}MB (exceeds 1MB per-subdirectory threshold)."
            if large_files:
                top = sorted(large_files, key=lambda x: -x[1])[:3]
                details = ", ".join(f"{f.name} ({s / (1024 * 1024):.1f}MB)" for f, s in top)
                msg += f" Largest files: {details}."
            findings.append(Finding(
                rule_id="INST-06", severity="warning",
                title=f"Large inst/ subdirectory: {d.name}/ ({size_mb:.1f}MB)",
                message=msg, file=str(rel_dir),
                cran_says=f"installed size is X.XMb, sub-directories of 1Mb or more: {d.name} {size_mb:.1f}Mb",
            ))

    return findings


# --- Online check helpers ---

# Base R packages that don't need CRAN/Bioconductor validation
BASE_R_PACKAGES = {
    "R", "base", "compiler", "datasets", "grDevices", "graphics", "grid",
    "methods", "parallel", "splines", "stats", "stats4", "tcltk", "tools",
    "utils",
}

# Known valid R-ecosystem words that aspell would flag
R_ECOSYSTEM_WORDS = {
    "anova", "bioconductor", "CMD", "cph", "CRAN", "cre", "DataFrame",
    "dplyr", "ggplot", "ggplot2", "knitr", "LazyData", "Makevars",
    "NAMESPACE", "Rcpp", "Rd", "Rmd", "roxygen", "roxygen2",
    "RoxygenNote", "rmarkdown", "Rnw", "RSQLite", "Shiny", "tibble",
    "tidyr", "tidyverse", "vignette", "vignettes", "useDynLib",
    "VignetteBuilder", "VignetteEncoding", "VignetteEngine",
    "VignetteIndexEntry", "testthat",
}


def _collect_urls_from_files(path, desc):
    """Collect all URLs from DESCRIPTION, man/*.Rd, vignettes/, README.md.

    Returns [(url, relative_file, line_number), ...] with duplicates removed.
    """
    url_pattern = re.compile(r'https?://[^\s<>")\]},\']+')
    results = []
    seen_urls = set()

    def _add_urls_from_file(filepath, rel_path):
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return
        for i, line in enumerate(text.splitlines(), 1):
            for m in url_pattern.finditer(line):
                url = m.group(0).rstrip(".,;:!?)")
                if url not in seen_urls:
                    seen_urls.add(url)
                    results.append((url, rel_path, i))

    desc_file = path / "DESCRIPTION"
    if desc_file.exists():
        _add_urls_from_file(desc_file, "DESCRIPTION")

    man_dir = path / "man"
    if man_dir.is_dir():
        for rd in sorted(man_dir.glob("*.Rd")):
            _add_urls_from_file(rd, str(rd.relative_to(path)))

    vig_dir = path / "vignettes"
    if vig_dir.is_dir():
        for ext in ("*.Rmd", "*.Rnw", "*.Rtex", "*.rmd", "*.rnw", "*.qmd"):
            for vf in sorted(vig_dir.glob(ext)):
                _add_urls_from_file(vf, str(vf.relative_to(path)))

    readme = path / "README.md"
    if readme.exists():
        _add_urls_from_file(readme, "README.md")

    return results


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """HTTP handler that does not follow redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _http_head_no_redirect(url, timeout=10):
    """Make an HTTP HEAD request without following redirects.

    Returns (status_code, redirect_location).
    Returns (-1, error_msg) on connection failure.
    """
    try:
        opener = urllib.request.build_opener(_NoRedirectHandler)
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "pedanticran-checker/1.0")
        response = opener.open(req, timeout=timeout)
        return (response.status, response.headers.get("Location", ""))
    except urllib.error.HTTPError as e:
        location = ""
        if hasattr(e, "headers"):
            location = e.headers.get("Location", "")
        return (e.code, location)
    except Exception as e:
        return (-1, str(e))


def check_urls_online(path, desc):
    """MISC-02 and MISC-07: Check URLs for validity and permanent redirects."""
    findings = []
    urls = _collect_urls_from_files(path, desc)

    for url, rel_file, line_num in urls:
        if "doi.org/" in url:
            continue

        time.sleep(0.1)

        try:
            status, location = _http_head_no_redirect(url, timeout=10)
        except Exception:
            continue

        if status == -1:
            continue

        if 400 <= status < 600:
            findings.append(Finding(
                rule_id="MISC-02", severity="warning",
                title=f"Broken URL (HTTP {status})",
                message=f"URL returned HTTP {status}: {url}",
                file=rel_file, line=line_num,
                cran_says="Found the following (possibly) invalid URLs."
            ))
        elif status == 301:
            redirect_target = location or "(unknown)"
            findings.append(Finding(
                rule_id="MISC-07", severity="note",
                title="URL has permanent redirect (301)",
                message=f"URL permanently redirects: {url} -> {redirect_target}",
                file=rel_file, line=line_num,
                cran_says="Found the following (possibly) invalid URLs: Status: 301 Moved Permanently"
            ))

    return findings


def check_spelling_online(desc):
    """MISC-03: Check spelling in Title and Description fields using aspell."""
    findings = []
    desc_file = "DESCRIPTION"

    aspell_path = shutil.which("aspell")
    if not aspell_path:
        findings.append(Finding(
            rule_id="MISC-03", severity="note",
            title="Spell check skipped (aspell not found)",
            message="Install aspell for spell checking: apt-get install aspell / brew install aspell",
            file=desc_file,
        ))
        return findings

    for field_name in ("Title", "Description"):
        text = desc.get(field_name, "")
        if not text:
            continue

        try:
            result = subprocess.run(
                [aspell_path, "list", "--lang=en"],
                input=text, capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                continue

            misspelled = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
            r_words_lower = {w.lower() for w in R_ECOSYSTEM_WORDS}
            misspelled = {w for w in misspelled if w.lower() not in r_words_lower}
            misspelled = {w for w in misspelled if w and len(w) > 1}

            if misspelled:
                words_str = ", ".join(sorted(misspelled)[:10])
                suffix = f" (and {len(misspelled) - 10} more)" if len(misspelled) > 10 else ""
                findings.append(Finding(
                    rule_id="MISC-03", severity="note",
                    title=f"Possible misspellings in {field_name}",
                    message=f"Potentially misspelled words: {words_str}{suffix}. Add valid terms to inst/WORDLIST.",
                    file=desc_file,
                    cran_says="Possibly misspelled words in DESCRIPTION."
                ))

        except (subprocess.TimeoutExpired, Exception):
            continue

    return findings


def _parse_dependency_packages(desc):
    """Extract package names from Depends, Imports, and LinkingTo fields."""
    packages = []
    for field_name in ("Depends", "Imports", "LinkingTo"):
        raw = desc.get(field_name, "")
        if raw:
            for entry in raw.split(","):
                pkg = entry.strip().split("(")[0].strip()
                if pkg and pkg not in BASE_R_PACKAGES:
                    packages.append(pkg)
    return packages


def _check_cran_package_exists(pkg, timeout=10):
    """Check if a package exists on CRAN. Returns True if found."""
    url = f"https://cran.r-project.org/web/packages/{pkg}/index.html"
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "pedanticran-checker/1.0")
        response = urllib.request.urlopen(req, timeout=timeout)
        return response.status == 200
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False


def _check_bioconductor_package_exists(pkg, timeout=10):
    """Check if a package exists on Bioconductor. Returns True if found."""
    url = f"https://bioconductor.org/packages/{pkg}/"
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "pedanticran-checker/1.0")
        response = urllib.request.urlopen(req, timeout=timeout)
        return response.status == 200
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False


def check_dependencies_online(desc):
    """DEP-01 and DEP-03: Check dependencies on CRAN/Bioconductor and health."""
    findings = []
    desc_file = "DESCRIPTION"
    packages = _parse_dependency_packages(desc)
    additional_repos = desc.get("Additional_repositories", "")

    for pkg in packages:
        time.sleep(0.1)

        try:
            on_cran = _check_cran_package_exists(pkg)
        except Exception:
            continue

        if on_cran:
            time.sleep(0.1)
            try:
                check_url = f"https://cran.r-project.org/web/checks/check_results_{pkg}.html"
                req = urllib.request.Request(check_url)
                req.add_header("User-Agent", "pedanticran-checker/1.0")
                response = urllib.request.urlopen(req, timeout=10)
                check_page = response.read().decode("utf-8", errors="replace")
                error_count = check_page.count(">ERROR<")
                if error_count >= 2:
                    findings.append(Finding(
                        rule_id="DEP-03", severity="note",
                        title=f"Dependency '{pkg}' has CRAN check errors",
                        message=f"Package '{pkg}' has ERROR results on {error_count} platforms. Monitor at https://cran.r-project.org/web/checks/check_results_{pkg}.html",
                        file=desc_file,
                        cran_says="Archived on [date] as requires archived package."
                    ))
            except Exception:
                pass
            continue

        try:
            on_bioc = _check_bioconductor_package_exists(pkg)
        except Exception:
            continue

        if on_bioc:
            continue

        if additional_repos:
            findings.append(Finding(
                rule_id="DEP-01", severity="note",
                title=f"Dependency '{pkg}' not on CRAN/Bioconductor",
                message=f"Package '{pkg}' not found on CRAN or Bioconductor. It may be from Additional_repositories: {additional_repos}",
                file=desc_file,
            ))
        else:
            findings.append(Finding(
                rule_id="DEP-01", severity="error",
                title=f"Dependency '{pkg}' not on CRAN or Bioconductor",
                message=f"Package '{pkg}' in Depends/Imports/LinkingTo is not available on CRAN or Bioconductor. CRAN requires all strong dependencies to be on CRAN or Bioconductor.",
                file=desc_file,
                cran_says="Package required but not available."
            ))

    return findings


def check_package_name_online(desc):
    """NAME-01: Check if the package name already exists on CRAN."""
    findings = []
    desc_file = "DESCRIPTION"
    pkg_name = desc.get("Package", "")
    if not pkg_name:
        return findings

    try:
        exists_on_cran = _check_cran_package_exists(pkg_name)
    except Exception:
        return findings

    if exists_on_cran:
        version = desc.get("Version", "")
        if ".9000" in version or ".9999" in version:
            findings.append(Finding(
                rule_id="NAME-01", severity="note",
                title=f"Package name '{pkg_name}' exists on CRAN (development version detected)",
                message=f"Package '{pkg_name}' already exists on CRAN. Your version '{version}' is a development version, so this is likely an update.",
                file=desc_file,
            ))
        else:
            findings.append(Finding(
                rule_id="NAME-01", severity="note",
                title=f"Package name '{pkg_name}' exists on CRAN",
                message=f"Package '{pkg_name}' already exists on CRAN. If this is a new submission, you'll need to choose a different name.",
                file=desc_file,
                cran_says="Package name must be case-insensitively unique across CRAN."
            ))

    return findings


# --- Output formatting ---

SEVERITY_ORDER = {"error": 0, "warning": 1, "note": 2}
SEVERITY_EMOJI = {"error": "❌", "warning": "⚠️", "note": "ℹ️"}
SEVERITY_GH = {"error": "error", "warning": "warning", "note": "notice"}


def format_github_annotation(f: Finding) -> str:
    """Format as GitHub Actions annotation."""
    level = SEVERITY_GH[f.severity]
    location = ""
    if f.file:
        location += f"file={f.file}"
        if f.line:
            location += f",line={f.line}"
    title = f"[{f.rule_id}] {f.title}"
    msg = f.message
    if f.cran_says:
        msg += f" | CRAN: {f.cran_says}"
    if location:
        return f"::{level} {location}::{title}: {msg}"
    return f"::{level} ::{title}: {msg}"


def format_console(f: Finding) -> str:
    """Format for console output."""
    emoji = SEVERITY_EMOJI[f.severity]
    loc = ""
    if f.file:
        loc = f" ({f.file}"
        if f.line:
            loc += f":{f.line}"
        loc += ")"
    return f"  {emoji} [{f.rule_id}] {f.title}{loc}\n     {f.message}"


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Pedantic CRAN Check")
    parser.add_argument("--path", default=".", help="Path to R package")
    parser.add_argument("--severity", default="warning", choices=["error", "warning", "note"],
                        help="Minimum severity to report")
    parser.add_argument("--fail-on", default="error", choices=["error", "warning", "note"],
                        help="Fail the check at this severity level")
    parser.add_argument("--online", action="store_true",
                        help="Enable checks requiring network access (URL validation, CRAN lookups, spell check)")
    args = parser.parse_args()

    pkg_path = Path(args.path).resolve()
    min_sev = SEVERITY_ORDER[args.severity]
    fail_sev = SEVERITY_ORDER[args.fail_on]

    # Verify it's an R package
    if not (pkg_path / "DESCRIPTION").exists():
        print(f"::error::No DESCRIPTION file found at {pkg_path}. Is this an R package?")
        sys.exit(1)

    desc = parse_description(pkg_path)
    pkg_name = desc.get("Package", "unknown")
    pkg_version = desc.get("Version", "?")

    print(f"\n{'=' * 60}")
    print(f"  Pedantic CRAN Check — {pkg_name} v{pkg_version}")
    print(f"{'=' * 60}\n")

    # Run all checks
    all_findings: list[Finding] = []
    all_findings.extend(check_description_fields(pkg_path, desc))
    all_findings.extend(check_code(pkg_path, desc))
    all_findings.extend(check_documentation(pkg_path, desc))
    all_findings.extend(check_structure(pkg_path, desc))
    all_findings.extend(check_encoding(pkg_path, desc))
    all_findings.extend(check_vignettes(pkg_path, desc))
    all_findings.extend(check_namespace(pkg_path, desc))
    all_findings.extend(check_data(pkg_path, desc))
    all_findings.extend(check_system_requirements(pkg_path, desc))
    all_findings.extend(check_maintainer_email(pkg_path, desc))
    all_findings.extend(check_inst_directory(pkg_path, desc))

    # Online checks (require network access)
    if args.online:
        all_findings.extend(check_urls_online(pkg_path, desc))
        all_findings.extend(check_spelling_online(desc))
        all_findings.extend(check_dependencies_online(desc))
        all_findings.extend(check_package_name_online(desc))

    # Filter by minimum severity
    findings = [f for f in all_findings if SEVERITY_ORDER[f.severity] <= min_sev]
    findings.sort(key=lambda f: SEVERITY_ORDER[f.severity])

    # Count by severity
    counts = {"error": 0, "warning": 0, "note": 0}
    for f in findings:
        counts[f.severity] += 1

    # Output GitHub annotations (if in CI)
    is_ci = os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")
    if is_ci:
        for f in findings:
            print(format_github_annotation(f))

    # Console output (always)
    if counts["error"]:
        print("BLOCKING (will be rejected):")
        for f in findings:
            if f.severity == "error":
                print(format_console(f))
        print()

    if counts["warning"]:
        print("WARNINGS (may cause rejection):")
        for f in findings:
            if f.severity == "warning":
                print(format_console(f))
        print()

    if counts["note"]:
        print("NOTES (recommended improvements):")
        for f in findings:
            if f.severity == "note":
                print(format_console(f))
        print()

    # Summary
    total = sum(counts.values())
    print(f"{'=' * 60}")
    print(f"  {counts['error']} errors, {counts['warning']} warnings, {counts['note']} notes ({total} total)")
    print(f"{'=' * 60}")

    # Set GitHub outputs
    if is_ci:
        ghout = os.environ.get("GITHUB_OUTPUT", "")
        if ghout:
            with open(ghout, "a") as f:
                f.write(f"issues={total}\n")
                f.write(f"errors={counts['error']}\n")
                f.write(f"warnings={counts['warning']}\n")
                f.write(f"notes={counts['note']}\n")

    # Exit code
    should_fail = any(SEVERITY_ORDER[f.severity] <= fail_sev for f in findings)
    sys.exit(1 if should_fail else 0)


if __name__ == "__main__":
    main()
