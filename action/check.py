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
import sys
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

        # CODE-02: print()/cat() for messages (skip print.*methods and comments)
        for lnum, line in scan_file(rf, r'\b(?:print|cat)\s*\('):
            if is_in_comment(line):
                continue
            # Skip if it's a print.something method definition
            if re.match(r'^\s*print\.\w+', line):
                continue
            # Skip if inside a method that is clearly a print/format S3 method
            if "UseMethod" in line:
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
        for lnum, line in scan_file(rf, r'<<-'):
            if not is_in_comment(line):
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
            # Find @export without @return in the same roxygen block
            blocks = re.split(r'\n(?!#\')', text)
            in_roxygen = False
            has_export = False
            has_return = False
            block_start = 0
            for i, line in enumerate(text.splitlines(), 1):
                if line.strip().startswith("#'"):
                    if not in_roxygen:
                        in_roxygen = True
                        has_export = False
                        has_return = False
                        block_start = i
                    if "@export" in line:
                        has_export = True
                    if "@return" in line:
                        has_return = True
                else:
                    if in_roxygen and has_export and not has_return:
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
            in_roxygen = False
            has_export = False
            has_examples = False
            block_start = 0
            for i, line in enumerate(text.splitlines(), 1):
                if line.strip().startswith("#'"):
                    if not in_roxygen:
                        in_roxygen = True
                        has_export = False
                        has_examples = False
                        block_start = i
                    if "@export" in line:
                        has_export = True
                    if "@examples" in line:
                        has_examples = True
                else:
                    if in_roxygen and has_export and not has_examples:
                        findings.append(Finding(
                            rule_id="DOC-05", severity="note",
                            title="Exported function without @examples",
                            message="Exported functions should include runnable examples.",
                            file=rel, line=block_start,
                        ))
                    in_roxygen = False

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
