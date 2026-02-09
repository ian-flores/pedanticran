"""INST checks -- inst/ directory CRAN policy violations.

Rules implemented:
  INST-01: Hidden files in inst/
  INST-02: Deprecated CITATION format (citEntry/personList)
  INST-03: inst/doc conflicts with vignettes/
  INST-04: Reserved subdirectory names / embedded packages
  INST-05: Missing copyright for bundled third-party code
  INST-06: Large inst/ subdirectory sizes (enhances SIZE-01)
"""

import re
from pathlib import Path

# Import Finding from parent check module -- when integrated into check.py,
# this import will be removed and Finding will already be in scope.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from check import Finding


# --- Constants ---

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

# 1 MB threshold for per-subdirectory size NOTE
SUBDIR_SIZE_THRESHOLD = 1 * 1024 * 1024
# 500 KB threshold for individual large files
LARGE_FILE_THRESHOLD = 500 * 1024


def check_inst_directory(path: Path, desc: dict) -> list[Finding]:
    """Check inst/ directory for CRAN policy violations."""
    findings = []
    inst_dir = path / "inst"
    if not inst_dir.is_dir():
        return findings

    findings.extend(_check_hidden_files(path, inst_dir))
    findings.extend(_check_citation_format(path, inst_dir))
    findings.extend(_check_inst_doc_conflicts(path, inst_dir))
    findings.extend(_check_reserved_dirs(path, inst_dir))
    findings.extend(_check_third_party_copyright(path, inst_dir, desc))
    findings.extend(_check_subdir_sizes(path, inst_dir))

    return findings


def _check_hidden_files(path: Path, inst_dir: Path) -> list[Finding]:
    """INST-01: Hidden files in inst/."""
    findings = []
    for f in inst_dir.rglob("*"):
        if not f.is_file():
            continue
        name = f.name
        # Files starting with . or matching known OS metadata
        if name.startswith(".") or name in HIDDEN_FILE_PATTERNS:
            findings.append(Finding(
                rule_id="INST-01",
                severity="error",
                title=f"Hidden file in inst/: {name}",
                message=f"Remove '{name}' from inst/ or add to .Rbuildignore. "
                        f"Hidden files trigger a NOTE in R CMD check.",
                file=str(f.relative_to(path)),
                cran_says="Found the following hidden files and directories.",
            ))
    return findings


def _check_citation_format(path: Path, inst_dir: Path) -> list[Finding]:
    """INST-02: Deprecated CITATION format (citEntry/personList)."""
    findings = []
    citation_file = inst_dir / "CITATION"
    if not citation_file.is_file():
        return findings

    try:
        text = citation_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    for func_name, pattern in DEPRECATED_CITATION_PATTERNS.items():
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line):
                replacement = {
                    "citEntry": "bibentry()",
                    "personList": "c() on person objects",
                    "as.personList": "c() on person objects",
                    "citHeader": "header argument to bibentry()",
                    "citFooter": "footer argument to bibentry()",
                }[func_name]
                findings.append(Finding(
                    rule_id="INST-02",
                    severity="warning",
                    title=f"Deprecated {func_name}() in CITATION",
                    message=f"Replace {func_name}() with {replacement}.",
                    file=str(citation_file.relative_to(path)),
                    line=i,
                    cran_says=f"Package CITATION file contains call(s) to old-style {func_name}().",
                ))
                break  # One finding per deprecated function is enough

    return findings


def _check_inst_doc_conflicts(path: Path, inst_dir: Path) -> list[Finding]:
    """INST-03: inst/doc conflicts with vignettes/."""
    findings = []
    vignettes_dir = path / "vignettes"
    inst_doc_dir = inst_dir / "doc"

    if not vignettes_dir.is_dir() or not inst_doc_dir.is_dir():
        return findings

    # Check if vignettes/ has source files
    has_vignette_sources = any(
        f.suffix in VIGNETTE_SOURCE_EXTS
        for f in vignettes_dir.iterdir()
        if f.is_file()
    )

    if not has_vignette_sources:
        return findings

    # Check if inst/doc has built output or source files
    inst_doc_files = [f for f in inst_doc_dir.iterdir() if f.is_file()]
    has_output = any(f.suffix in VIGNETTE_OUTPUT_EXTS for f in inst_doc_files)
    has_source = any(f.suffix in VIGNETTE_SOURCE_EXTS for f in inst_doc_files)

    if has_output:
        findings.append(Finding(
            rule_id="INST-03",
            severity="warning",
            title="inst/doc contains pre-built vignettes",
            message="Delete inst/doc/ from the source tree. "
                    "R CMD build populates it automatically from vignettes/. "
                    "Add inst/doc to .gitignore (not .Rbuildignore).",
            file="inst/doc",
            cran_says="inst/doc directory should not contain pre-built vignettes "
                      "if vignettes/ directory exists.",
        ))

    if has_source:
        source_files = [f.name for f in inst_doc_files if f.suffix in VIGNETTE_SOURCE_EXTS]
        findings.append(Finding(
            rule_id="INST-03",
            severity="warning",
            title="Vignette sources in inst/doc/ instead of vignettes/",
            message=f"Move vignette sources to vignettes/: {', '.join(source_files[:5])}",
            file="inst/doc",
            cran_says="Vignette sources must be in vignettes/, not inst/doc/.",
        ))

    return findings


def _check_reserved_dirs(path: Path, inst_dir: Path) -> list[Finding]:
    """INST-04: Reserved subdirectory names and embedded packages."""
    findings = []

    # Check immediate subdirectories against reserved names
    for d in sorted(inst_dir.iterdir()):
        if not d.is_dir():
            continue
        if d.name in RESERVED_INST_DIRS:
            findings.append(Finding(
                rule_id="INST-04",
                severity="error",
                title=f"Reserved directory name: inst/{d.name}",
                message=f"inst/{d.name}/ conflicts with R's standard package "
                        f"directory. Rename to avoid overwriting R internals "
                        f"during installation.",
                file=str(d.relative_to(path)),
                cran_says="inst/ subdirectories should not interfere with "
                          "R's standard directories.",
            ))

    # Check for embedded packages (DESCRIPTION files in subdirectories)
    for desc_file in inst_dir.rglob("DESCRIPTION"):
        # Skip the top-level inst/DESCRIPTION if it exists (unlikely but possible)
        if desc_file.parent == inst_dir:
            continue
        rel_dir = desc_file.parent.relative_to(path)
        findings.append(Finding(
            rule_id="INST-04",
            severity="error",
            title=f"Embedded package in {rel_dir}",
            message=f"Found DESCRIPTION file at {desc_file.relative_to(path)}, "
                    f"indicating an embedded package. Restructure tests or "
                    f"move fixture packages outside inst/.",
            file=str(desc_file.relative_to(path)),
            cran_says="Subdirectory appears to contain a package.",
        ))

    return findings


def _check_third_party_copyright(path: Path, inst_dir: Path, desc: dict) -> list[Finding]:
    """INST-05: Missing copyright for bundled third-party code."""
    findings = []

    # Identify third-party code directories
    third_party_found = []
    for d in inst_dir.iterdir():
        if d.is_dir() and d.name.lower() in THIRD_PARTY_DIRS:
            # Check if it contains actual code files (JS, CSS, C/C++ headers)
            code_exts = {".js", ".css", ".c", ".cpp", ".h", ".hpp", ".ts", ".min.js", ".min.css"}
            has_code = any(
                f.suffix in code_exts
                for f in d.rglob("*")
                if f.is_file()
            )
            if has_code:
                third_party_found.append(d.name)

    # Also check for htmlwidgets with nested lib/ directories
    hw_dir = inst_dir / "htmlwidgets"
    if hw_dir.is_dir():
        lib_dir = hw_dir / "lib"
        if lib_dir.is_dir() and any(lib_dir.iterdir()):
            if "htmlwidgets" not in third_party_found:
                third_party_found.append("htmlwidgets/lib")

    if not third_party_found:
        return findings

    # Check for attribution mechanisms
    has_copyrights_file = (inst_dir / "COPYRIGHTS").is_file()
    has_copyright_field = "Copyright" in desc
    authors_r = desc.get("Authors@R", "")
    # Count cph roles -- a rough heuristic
    cph_count = len(re.findall(r'"cph"', authors_r)) + len(re.findall(r"'cph'", authors_r))

    if not has_copyrights_file and not has_copyright_field and cph_count < 2:
        dirs_str = ", ".join(f"inst/{d}" for d in third_party_found[:5])
        findings.append(Finding(
            rule_id="INST-05",
            severity="warning",
            title="Bundled third-party code may lack copyright attribution",
            message=f"Found third-party code in {dirs_str}. "
                    f"Add inst/COPYRIGHTS file, Copyright field in DESCRIPTION, "
                    f"or 'cph' roles in Authors@R for external copyright holders.",
            file="DESCRIPTION",
            cran_says="Where copyrights are held by an entity other than the "
                      "package authors, this should preferably be indicated via "
                      "'cph' roles in the 'Authors@R' field, or using a "
                      "'Copyright' field.",
        ))

    return findings


def _check_subdir_sizes(path: Path, inst_dir: Path) -> list[Finding]:
    """INST-06: Large inst/ subdirectory sizes (enhances SIZE-01)."""
    findings = []

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
            msg = (f"inst/{d.name}/ is {size_mb:.1f}MB "
                   f"(exceeds 1MB per-subdirectory threshold). "
                   f"R CMD check will produce a NOTE about installed package size.")
            if large_files:
                top = sorted(large_files, key=lambda x: -x[1])[:3]
                details = ", ".join(
                    f"{f.name} ({s / (1024 * 1024):.1f}MB)" for f, s in top
                )
                msg += f" Largest files: {details}."
            findings.append(Finding(
                rule_id="INST-06",
                severity="warning",
                title=f"Large inst/ subdirectory: {d.name}/ ({size_mb:.1f}MB)",
                message=msg,
                file=str(rel_dir),
                cran_says=f"installed size is X.XMb, sub-directories of 1Mb or "
                          f"more: {d.name} {size_mb:.1f}Mb",
            ))

    return findings
