"""System Requirements checks for pedanticran.

Implements:
  SYS-01: Undeclared system libraries (scan src/ headers, cross-ref SystemRequirements)
  SYS-02: Undeclared external programs (partial — scan R/ for system()/system2())
  SYS-05: Java .class/.jar without source (glob for .jar/.class, check java/ dir)
  SYS-06: Contradictory C++ standard specifications (parse both locations)
  SYS-07: USE_C17 opt-out cross-reference (check SystemRequirements for USE_C17)
"""

import re
from pathlib import Path

# Import Finding from parent — caller is responsible for providing the class
# This module is designed to be imported by action/check.py
import sys
import os

# Allow importing Finding from the parent check module
_parent_dir = Path(__file__).resolve().parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))


# Header-to-library mapping for SYS-01
SYSTEM_LIBRARY_HEADERS = {
    "curl/curl.h": "libcurl",
    "libxml/parser.h": "libxml2",
    "libxml/tree.h": "libxml2",
    "libxml/xpath.h": "libxml2",
    "openssl/ssl.h": "OpenSSL",
    "openssl/evp.h": "OpenSSL",
    "openssl/sha.h": "OpenSSL",
    "openssl/rsa.h": "OpenSSL",
    "zlib.h": "zlib",
    "png.h": "libpng",
    "jpeglib.h": "libjpeg",
    "gdal.h": "GDAL",
    "ogr_api.h": "GDAL",
    "cpl_conv.h": "GDAL",
    "geos_c.h": "GEOS",
    "proj.h": "PROJ",
    "proj_api.h": "PROJ",
    "fftw3.h": "FFTW",
    "gsl/gsl_math.h": "GSL",
    "gsl/gsl_rng.h": "GSL",
    "gsl/gsl_vector.h": "GSL",
    "gsl/gsl_matrix.h": "GSL",
    "hdf5.h": "HDF5",
    "netcdf.h": "netCDF",
    "sqlite3.h": "SQLite",
    "pcre2.h": "PCRE2",
    "lzma.h": "liblzma",
    "bzlib.h": "bzip2",
    "tiff.h": "libtiff",
    "tiffio.h": "libtiff",
    "cairo.h": "cairo",
    "cairo/cairo.h": "cairo",
    "mpfr.h": "MPFR",
    "gmp.h": "GMP",
    "glpk.h": "GLPK",
    "udunits2.h": "udunits2",
    "poppler/cpp/poppler-document.h": "poppler",
    "magic.h": "libmagic",
    "archive.h": "libarchive",
    "sodium.h": "libsodium",
    "git2.h": "libgit2",
    "yaml.h": "libyaml",
    "zmq.h": "libzmq",
    "re2/re2.h": "RE2",
    "mysql/mysql.h": "MySQL",
    "libpq-fe.h": "PostgreSQL",
    "mariadb/mysql.h": "MariaDB",
    "librdf.h": "Redland",
    "raptor2/raptor2.h": "Raptor2",
    "rasqal/rasqal.h": "Rasqal",
    "freetype/freetype.h": "FreeType",
    "ft2build.h": "FreeType",
    "Imlib2.h": "Imlib2",
    "avformat.h": "FFmpeg",
    "libavformat/avformat.h": "FFmpeg",
    "tesseract/baseapi.h": "Tesseract",
    "leptonica/allheaders.h": "Leptonica",
    "alsa/asoundlib.h": "ALSA",
    "pulse/simple.h": "PulseAudio",
    "v8.h": "V8",
}

# C++ standard name normalization for SYS-06
CXX_STANDARD_MAP = {
    "CXX11": "C++11",
    "CXX14": "C++14",
    "CXX17": "C++17",
    "CXX20": "C++20",
    "CXX23": "C++23",
    "C++11": "C++11",
    "C++14": "C++14",
    "C++17": "C++17",
    "C++20": "C++20",
    "C++23": "C++23",
}


def _find_src_includes(path: Path) -> dict[str, list[tuple[str, int]]]:
    """Scan src/ for #include directives matching known system library headers.

    Returns: {library_name: [(file_relative_path, line_num), ...]}
    """
    src_dir = path / "src"
    if not src_dir.is_dir():
        return {}

    found: dict[str, list[tuple[str, int]]] = {}
    exts = ("*.c", "*.cpp", "*.cc", "*.h", "*.hpp")

    for ext in exts:
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


def _parse_sysreqs(desc: dict) -> str:
    """Get the SystemRequirements field as lowercase for matching."""
    return desc.get("SystemRequirements", "").lower()


def _parse_makevars_cxx_std(path: Path) -> list[tuple[str, str, int]]:
    """Parse CXX_STD from Makevars files.

    Returns: [(normalized_standard, file_relative_path, line_num), ...]
    """
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
    """Extract C++ standard from SystemRequirements field.

    Returns normalized standard like 'C++17' or None.
    """
    sysreqs = desc.get("SystemRequirements", "")
    # Match patterns like "C++17", "C++20", "C++11"
    m = re.search(r'C\+\+(\d+)', sysreqs)
    if m:
        version = m.group(1)
        return f"C++{version}"
    return None


def check_system_requirements(path: Path, desc: dict) -> list:
    """Check SystemRequirements declarations.

    Returns list of Finding objects (imported from check module).
    """
    from check import Finding

    findings = []
    sysreqs_lower = _parse_sysreqs(desc)

    # --- SYS-01: Undeclared system libraries ---
    includes = _find_src_includes(path)
    for lib, locations in includes.items():
        # Check if library name appears in SystemRequirements (case-insensitive)
        if lib.lower() not in sysreqs_lower:
            first_file, first_line = locations[0]
            file_list = ", ".join(f"{f}:{ln}" for f, ln in locations[:3])
            if len(locations) > 3:
                file_list += f" (+{len(locations) - 3} more)"
            findings.append(Finding(
                rule_id="SYS-01",
                severity="warning",
                title=f"Undeclared system library: {lib}",
                message=(
                    f"Compiled code includes headers for {lib} but SystemRequirements "
                    f"does not mention it. Found in: {file_list}"
                ),
                file=first_file,
                line=first_line,
                cran_says=(
                    "Packages using external libraries should declare them in "
                    "SystemRequirements so they can be installed on build machines."
                ),
            ))

    # --- SYS-02: Undeclared external programs (partial) ---
    # Scan R/ for system()/system2() calls with known program names
    r_dir = path / "R"
    if r_dir.is_dir():
        known_programs = {
            "pandoc": "pandoc",
            "python": "Python",
            "python3": "Python",
            "java": "Java",
            "jags": "JAGS",
            "perl": "Perl",
            "php": "PHP",
            "node": "Node.js",
            "npm": "Node.js",
            "cargo": "Rust (cargo)",
            "rustc": "Rust (rustc)",
            "cmake": "CMake",
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
                # Match system("prog"), system2("prog"), processx::run("prog")
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
                                rule_id="SYS-02",
                                severity="warning",
                                title=f"Undeclared external program: {lib_name}",
                                message=(
                                    f"Code calls {prog} via system()/system2() but "
                                    f"SystemRequirements does not mention {lib_name}."
                                ),
                                file=rel,
                                line=i,
                                cran_says=(
                                    "If your package requires one of these interpreters "
                                    "or an extension then this should be declared in "
                                    "the SystemRequirements field."
                                ),
                            ))

    # --- SYS-05: Java .class/.jar files require source ---
    java_files = []
    for pattern in ["**/*.jar", "**/*.class"]:
        for f in path.rglob(pattern.split("/")[-1]):
            # Skip .git directory
            if ".git" in str(f):
                continue
            java_files.append(f)

    if java_files:
        java_dir = path / "java"
        has_java_dir = java_dir.is_dir()

        if not has_java_dir:
            file_names = [str(f.relative_to(path)) for f in java_files[:5]]
            file_list = ", ".join(file_names)
            if len(java_files) > 5:
                file_list += f" (+{len(java_files) - 5} more)"
            findings.append(Finding(
                rule_id="SYS-05",
                severity="error",
                title="Java .class/.jar files without java/ source directory",
                message=(
                    f"Found {len(java_files)} Java binary file(s) ({file_list}) "
                    f"but no top-level java/ directory with sources."
                ),
                file=str(java_files[0].relative_to(path)),
                cran_says=(
                    "For Java .class and .jar files, the sources should be in a "
                    "top-level java directory in the source package (or that "
                    "directory should explain how they can be obtained)."
                ),
            ))

        # Also check that SystemRequirements mentions Java
        if "java" not in sysreqs_lower and "jdk" not in sysreqs_lower and "jre" not in sysreqs_lower:
            findings.append(Finding(
                rule_id="SYS-05",
                severity="warning",
                title="Java files present but Java not in SystemRequirements",
                message=(
                    "Package contains .jar/.class files but SystemRequirements "
                    "does not mention Java. Add: SystemRequirements: Java (>= 8)"
                ),
                file="DESCRIPTION",
                cran_says=(
                    "For Java .class and .jar files, the sources should be in a "
                    "top-level java directory."
                ),
            ))

    # --- SYS-06: Contradictory C++ standard specifications ---
    makevars_standards = _parse_makevars_cxx_std(path)
    sysreqs_cxx = _parse_sysreqs_cxx_standard(desc)

    if sysreqs_cxx and makevars_standards:
        for makevars_std, mv_file, mv_line in makevars_standards:
            if makevars_std != sysreqs_cxx:
                findings.append(Finding(
                    rule_id="SYS-06",
                    severity="warning",
                    title="Contradictory C++ standard specifications",
                    message=(
                        f"SystemRequirements declares {sysreqs_cxx} but "
                        f"{mv_file} sets CXX_STD = {makevars_std}. "
                        f"These must be consistent."
                    ),
                    file=mv_file,
                    line=mv_line,
                    cran_says=(
                        "C++ standard specifications in src/Makevars* and "
                        "SystemRequirements are now checked more thoroughly. "
                        "Contradictory specifications give a warning."
                    ),
                ))

    # Flag deprecated C++ standard in SystemRequirements (even without Makevars)
    if sysreqs_cxx and sysreqs_cxx in ("C++11", "C++14"):
        findings.append(Finding(
            rule_id="SYS-06",
            severity="warning",
            title=f"Deprecated C++ standard in SystemRequirements: {sysreqs_cxx}",
            message=(
                f"SystemRequirements declares {sysreqs_cxx} which is deprecated. "
                f"R defaults to C++17+. Remove or update to C++17/C++20."
            ),
            file="DESCRIPTION",
            cran_says=(
                "C++11/C++14 specifications are deprecated since R 4.3."
            ),
        ))

    # --- SYS-07: USE_C17 opt-out cross-reference ---
    has_use_c17 = "use_c17" in sysreqs_lower

    if has_use_c17:
        # Check if there are actually C source files that might need it
        src_dir = path / "src"
        has_c_files = False
        if src_dir.is_dir():
            has_c_files = bool(list(src_dir.glob("*.c")) or list(src_dir.glob("*.h")))

        if not has_c_files:
            findings.append(Finding(
                rule_id="SYS-07",
                severity="note",
                title="USE_C17 declared but no C source files found",
                message=(
                    "SystemRequirements contains USE_C17 but no .c/.h files "
                    "were found in src/. The opt-out may be unnecessary."
                ),
                file="DESCRIPTION",
                cran_says=(
                    "Packages can opt out of C23 via SystemRequirements: USE_C17."
                ),
            ))

    # If C files exist and have C23 keyword issues, suggest USE_C17 as workaround
    # (This is informational — COMP-01 handles the actual detection)
    src_dir = path / "src"
    if src_dir.is_dir() and not has_use_c17:
        c23_keywords_found = False
        c23_file = ""
        c23_line = 0
        for ext in ("*.c", "*.h"):
            for f in src_dir.glob(ext):
                try:
                    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
                except Exception:
                    continue
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("//") or stripped.startswith("/*"):
                        continue
                    # Look for C23 keywords used as identifiers (variable declarations/parameters)
                    # Match: type bool; or ,bool, or (bool  — where bool is used as identifier name
                    # This is a simplified heuristic
                    if re.search(r'(?:^|[,;({\s])(?:int|char|double|float|void|unsigned|long|short|SEXP)\s+(?:bool|true|false|nullptr)\s*[,;)=\[]', stripped):
                        c23_keywords_found = True
                        c23_file = str(f.relative_to(path))
                        c23_line = i
                        break
                if c23_keywords_found:
                    break

        if c23_keywords_found:
            findings.append(Finding(
                rule_id="SYS-07",
                severity="note",
                title="C23 keyword used as identifier — consider USE_C17 opt-out",
                message=(
                    "C source code uses C23 keywords (bool/true/false/nullptr) as "
                    "identifiers. Either rename them or add USE_C17 to "
                    "SystemRequirements as a temporary workaround."
                ),
                file=c23_file,
                line=c23_line,
                cran_says=(
                    "Packages can opt out via SystemRequirements: USE_C17 "
                    "or R CMD INSTALL --use-C17."
                ),
            ))

    return findings
