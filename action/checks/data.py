"""Data directory checks for CRAN submission readiness.

Checks: DATA-01 (undocumented datasets), DATA-02 (LazyData without data/),
DATA-03 (missing LazyData), DATA-04 (suboptimal compression),
DATA-05 (data size limits), DATA-08 (sysdata.rda size), DATA-09 (invalid formats).
"""

import re
from pathlib import Path

# Import Finding from parent — when integrated into check.py, this import
# is replaced by the existing dataclass.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from check import Finding


# Allowed extensions in data/ directory (case-insensitive base, optional compression suffix)
_DATA_BASE_EXTS = {".rda", ".rdata", ".r", ".tab", ".txt", ".csv"}
_COMPRESSION_EXTS = {".gz", ".bz2", ".xz"}


def _dataset_names_from_data_dir(data_dir: Path) -> list[tuple[str, Path]]:
    """Extract (dataset_name, file_path) for each .rda/.RData in data/."""
    datasets = []
    for f in sorted(data_dir.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() in (".rda", ".rdata"):
            # Dataset name = filename without extension
            name = f.stem
            datasets.append((name, f))
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
        # Only consider files that are data documentation
        if "\\docType{data}" in text:
            for m in re.finditer(r"\\alias\{([^}]+)\}", text):
                documented.add(m.group(1))
        else:
            # Even without \docType{data}, an \alias matches a dataset name
            for m in re.finditer(r"\\alias\{([^}]+)\}", text):
                documented.add(m.group(1))
    return documented


def _find_documented_datasets_roxygen(r_dir: Path) -> set[str]:
    """Find dataset names documented via roxygen in R/*.R.

    Looks for patterns like:
      #' @name dataset_name
      #' @rdname dataset_name
      "dataset_name"   (bare string as last expression in roxygen block)
    """
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
                # Check for @name or @rdname
                m = re.search(r"@(?:name|rdname)\s+(\S+)", stripped)
                if m:
                    documented.add(m.group(1))
            else:
                if in_roxygen:
                    # The line right after a roxygen block: bare string = dataset name
                    m = re.match(r'^["\']([^"\']+)["\']', stripped)
                    if m:
                        documented.add(m.group(1))
                in_roxygen = False
    return documented


def _is_valid_data_extension(filepath: Path) -> bool:
    """Check if a file has a valid extension for the data/ directory."""
    name = filepath.name.lower()
    # Strip compression suffixes first
    for comp in _COMPRESSION_EXTS:
        if name.endswith(comp):
            name = name[: -len(comp)]
            break
    # Check base extension
    suffix = Path(name).suffix.lower()
    return suffix in _DATA_BASE_EXTS


def check_data(path: Path, desc: dict) -> list[Finding]:
    """Check data directory for CRAN policy violations."""
    findings = []
    data_dir = path / "data"
    man_dir = path / "man"
    r_dir = path / "R"
    desc_file = str(path / "DESCRIPTION")

    has_data_dir = data_dir.is_dir()
    lazy_data = desc.get("LazyData", "").strip().lower() in ("true", "yes")

    # --- DATA-02: LazyData without data/ directory ---
    if lazy_data and not has_data_dir:
        findings.append(Finding(
            rule_id="DATA-02",
            severity="note",
            title="LazyData set without data/ directory",
            message="DESCRIPTION has 'LazyData: true' but no data/ directory exists. Remove LazyData field.",
            file=desc_file,
            cran_says="'LazyData' is specified without a 'data' directory",
        ))

    if not has_data_dir:
        # DATA-08: Check sysdata.rda even without data/
        _check_sysdata(path, findings)
        return findings

    # Collect data files
    data_files = [f for f in sorted(data_dir.iterdir()) if f.is_file()]
    rda_datasets = _dataset_names_from_data_dir(data_dir)

    # --- DATA-01: Undocumented datasets ---
    if rda_datasets:
        documented_rd = _find_documented_datasets_rd(man_dir)
        documented_rox = _find_documented_datasets_roxygen(r_dir)
        documented = documented_rd | documented_rox

        for name, filepath in rda_datasets:
            if name not in documented:
                findings.append(Finding(
                    rule_id="DATA-01",
                    severity="error",
                    title=f"Undocumented dataset: {name}",
                    message=f"Dataset '{name}' (from {filepath.name}) has no documentation. "
                            f"Add roxygen docs in R/data.R or create man/{name}.Rd with \\docType{{data}}.",
                    file=str(filepath.relative_to(path)),
                    cran_says="Undocumented data sets. All user-level objects in a package should have documentation entries.",
                ))

    # --- DATA-03: Missing LazyData when data/ has .rda files ---
    has_rda = any(f.suffix.lower() in (".rda", ".rdata") for f in data_files)
    if has_rda and not lazy_data:
        findings.append(Finding(
            rule_id="DATA-03",
            severity="note",
            title="Missing LazyData field",
            message="data/ contains .rda/.RData files but DESCRIPTION lacks 'LazyData: true'. "
                    "Users must call data() explicitly to load datasets.",
            file=desc_file,
            cran_says="If you're shipping .rda files below data/, include LazyData: true in DESCRIPTION.",
        ))

    # --- DATA-05: Data size exceeds limits ---
    total_size = sum(f.stat().st_size for f in data_files if f.is_file())
    total_mb = total_size / (1024 * 1024)

    if total_mb > 5:
        findings.append(Finding(
            rule_id="DATA-05",
            severity="error",
            title=f"Data directory exceeds 5MB ({total_mb:.1f}MB)",
            message="CRAN policy: 'neither data nor documentation should exceed 5MB'. "
                    "Use better compression, subset data, or host externally.",
            file="data/",
            cran_says="Data exceeded 5MB limit.",
        ))
    elif total_mb > 1:
        findings.append(Finding(
            rule_id="DATA-05",
            severity="warning",
            title=f"Data directory exceeds 1MB ({total_mb:.1f}MB)",
            message="R-pkgs.org recommends data under 1MB. Consider better compression "
                    "(tools::resaveRdaFiles) or hosting large data externally.",
            file="data/",
            cran_says="Packages should be of the minimum necessary size.",
        ))

    # --- DATA-04: Suboptimal compression ---
    if lazy_data and total_mb > 1:
        lazy_compression = desc.get("LazyDataCompression", "").strip()
        if not lazy_compression:
            findings.append(Finding(
                rule_id="DATA-04",
                severity="warning",
                title="Missing LazyDataCompression for large data",
                message=f"LazyData is true and data/ is {total_mb:.1f}MB but LazyDataCompression is not set. "
                        f"Add 'LazyDataCompression: xz' (or bzip2) to DESCRIPTION.",
                file=desc_file,
                cran_says="significantly better compression could be obtained by using R CMD build --resave-data",
            ))

    # Also flag individual large .rda files regardless of LazyData
    for f in data_files:
        if f.suffix.lower() in (".rda", ".rdata"):
            size_kb = f.stat().st_size / 1024
            if size_kb > 100:
                findings.append(Finding(
                    rule_id="DATA-04",
                    severity="note",
                    title=f"Large data file: {f.name} ({size_kb:.0f}KB)",
                    message="Consider running tools::resaveRdaFiles() with compress='auto' for optimal compression.",
                    file=str(f.relative_to(path)),
                    cran_says="significantly better compression could be obtained",
                ))

    # --- DATA-09: Invalid data file formats ---
    for f in data_files:
        if not _is_valid_data_extension(f):
            ext = f.suffix
            msg = f"File '{f.name}' has invalid extension '{ext}' for data/ directory."
            if ext.lower() == ".rds":
                msg += " .rds files are not allowed in data/ -- move to inst/extdata/."
            else:
                msg += " Allowed: .rda, .RData, .R, .tab, .txt, .csv (optionally .gz/.bz2/.xz compressed)."
            findings.append(Finding(
                rule_id="DATA-09",
                severity="warning",
                title=f"Invalid file format in data/: {f.name}",
                message=msg,
                file=str(f.relative_to(path)),
                cran_says="checking contents of 'data' directory",
            ))

    # --- DATA-08: sysdata.rda ---
    _check_sysdata(path, findings)

    return findings


def _check_sysdata(path: Path, findings: list[Finding]) -> None:
    """Check R/sysdata.rda for size issues."""
    sysdata = path / "R" / "sysdata.rda"
    if sysdata.exists():
        size_mb = sysdata.stat().st_size / (1024 * 1024)
        if size_mb > 1:
            findings.append(Finding(
                rule_id="DATA-08",
                severity="note",
                title=f"Large internal data: R/sysdata.rda ({size_mb:.1f}MB)",
                message="R/sysdata.rda is large and contributes to package size. "
                        "Consider reducing or loading from external source.",
                file="R/sysdata.rda",
                cran_says="Packages should be of the minimum necessary size.",
            ))
