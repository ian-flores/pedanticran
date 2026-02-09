"""Encoding checks for CRAN packages.

Checks for ENC-01 through ENC-08 (excluding ENC-06 which requires R).

When integrating into check.py, paste the helper functions and check_encoding()
into the file. They use Finding, scan_file, is_in_comment, find_r_files, and
find_rd_files which are already defined in check.py.
"""

from pathlib import Path


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
    for ext in ("*.Rmd", "*.Rnw", "*.Rtex", "*.rmd", "*.rnw"):
        files.extend(vig_dir.glob(ext))
    return sorted(files)


def check_encoding(path: Path, desc: dict) -> list[Finding]:
    """Check for encoding issues (ENC-01 through ENC-08, excluding ENC-06)."""
    findings = []
    desc_file = str(path / "DESCRIPTION")
    has_encoding_field = "Encoding" in desc

    # --- ENC-01: Missing Encoding field when non-ASCII present in DESCRIPTION ---
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

    # --- ENC-02: Non-ASCII in R source code ---
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

    # --- ENC-03: Non-portable \x escape sequences ---
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

    # --- ENC-04: UTF-8 BOM in source files ---
    files_to_check_bom = []
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

    # --- ENC-05: Missing VignetteEncoding declaration ---
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

    # --- ENC-07: Non-ASCII in NAMESPACE ---
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

    # --- ENC-08: Non-ASCII in Rd files without encoding declaration ---
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
