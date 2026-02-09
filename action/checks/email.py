"""Maintainer email checks for CRAN submission readiness.

Checks EMAIL-01 through EMAIL-06: mailing list detection, missing email,
disposable domains, placeholder addresses, institutional longevity, and
noreply/automated addresses.
"""

import re
from pathlib import Path

# Import Finding from parent check module -- when integrated, this will
# use the same Finding dataclass. For standalone use, define a compatible one.
try:
    from action.check import Finding
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class Finding:
        rule_id: str
        severity: str
        title: str
        message: str
        file: str = ""
        line: int = 0
        cran_says: str = ""


# --- Constants ---

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com",
    "guerrillamail.com",
    "guerrillamail.de",
    "tempmail.com",
    "throwaway.email",
    "yopmail.com",
    "sharklasers.com",
    "guerrillamailblock.com",
    "grr.la",
    "dispostable.com",
    "10minutemail.com",
    "trashmail.com",
    "trashmail.net",
    "trashmail.org",
    "maildrop.cc",
    "mailnesia.com",
    "temp-mail.org",
    "tempail.com",
    "tempr.email",
    "discard.email",
    "fakeinbox.com",
    "mailcatch.com",
    "mintemail.com",
    "mohmal.com",
    "mytemp.email",
    "getairmail.com",
    "getnada.com",
    "harakirimail.com",
    "mailexpire.com",
    "spamgourmet.com",
    "mailnator.com",
    "binkmail.com",
    "bobmail.info",
    "chammy.info",
    "devnullmail.com",
    "letthemeatspam.com",
    "mailmoat.com",
    "spamfree24.org",
    "trash-mail.com",
    "trashymail.com",
    "yopmail.fr",
    "tempmailaddress.com",
    "burnermail.io",
    "inboxkitten.com",
    "emailondeck.com",
    "guerrillamail.info",
    "guerrillamail.net",
    "tempinbox.com",
    "mailtemp.org",
}

MAILING_LIST_DOMAINS = {
    "googlegroups.com",
    "groups.io",
    "lists.r-forge.r-project.org",
    "lists.sourceforge.net",
    "lists.debian.org",
    "lists.gnu.org",
    "lists.fedoraproject.org",
    "lists.ubuntu.com",
    "lists.apache.org",
    "freelists.org",
    "listserv.uga.edu",
}

MAILING_LIST_LOCAL_PREFIXES = {
    "info",
    "admin",
    "support",
    "contact",
    "help",
    "office",
    "team",
}

MAILING_LIST_LOCAL_KEYWORDS = {
    "lists",
    "list",
    "devel",
    "dev-team",
    "team",
    "group",
    "announce",
    "discuss",
    "users",
    "-dev",
    "-devel",
    "-users",
    "-announce",
}

NOREPLY_PATTERNS = [
    r"^noreply@",
    r"^no-reply@",
    r"^donotreply@",
    r"^do-not-reply@",
    r"^notifications@github\.com$",
    r"@users\.noreply\.github\.com$",
    r"^bot@",
    r"^ci@",
    r"^automation@",
    r"^automated@",
    r"^mailer-daemon@",
    r"^postmaster@",
]

PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "test.com",
    "domain.com",
    "email.com",
    "mail.com",
    "your-domain.com",
    "yourdomain.com",
    "placeholder.com",
}

PLACEHOLDER_PATTERNS = [
    r"^your\.?email@",
    r"^first\.?last@",
    r"^name@",
    r"^user@",
    r"^maintainer@",
    r"^author@",
    r"^package@",
    r"^foo@",
    r"^bar@",
    r"^test@",
    r"^todo@",
    r"^changeme@",
    r"^replace\.?me@",
    r"^xxx@",
]

ACADEMIC_DOMAIN_PATTERNS = [
    r"\.edu$",
    r"\.ac\.uk$",
    r"\.ac\.jp$",
    r"\.ac\.at$",
    r"\.ac\.be$",
    r"\.ac\.kr$",
    r"\.ac\.nz$",
    r"\.ac\.za$",
    r"\.ac\.in$",
    r"\.ac\.il$",
    r"\.ac\.cn$",
    r"\.edu\.au$",
    r"\.edu\.cn$",
    r"\.edu\.tw$",
    r"\.edu\.hk$",
    r"\.edu\.sg$",
    r"\.edu\.br$",
    r"\.edu\.mx$",
    r"\.edu\.pl$",
    r"\.edu\.tr$",
    r"\.edu\.co$",
    r"\.edu\.ar$",
    r"(?:^|\.)uni-[a-z]+\.de$",
    r"(?:^|\.)tu-[a-z]+\.de$",
    r"(?:^|\.)fu-berlin\.de$",
    r"(?:^|\.)hu-berlin\.de$",
    r"(?:^|\.)rwth-aachen\.de$",
    r"(?:^|\.)u-[a-z]+\.fr$",
    r"(?:^|\.)univ-[a-z]+\.fr$",
]


# --- Email extraction ---

def extract_cre_email(authors_r: str) -> str | None:
    """Extract the maintainer (cre) email from Authors@R field.

    Parses person() blocks, finds the one with "cre" role, and returns
    the email argument. Uses DOTALL for multi-line person() blocks.
    """
    # Match person() blocks -- handle nested parens (e.g. role = c("aut", "cre"))
    # by using a pattern that matches balanced parentheses up to 2 levels deep.
    person_blocks = re.findall(
        r'person\s*\((?:[^()]*|\((?:[^()]*|\([^()]*\))*\))*\)',
        authors_r,
        re.DOTALL,
    )
    for block in person_blocks:
        if '"cre"' in block or "'cre'" in block:
            email_match = re.search(r'email\s*=\s*["\']([^"\']+)["\']', block)
            if email_match:
                return email_match.group(1).strip()
    return None


def _has_cre_without_email(authors_r: str) -> bool:
    """Check if there is a person with cre role but no email argument."""
    person_blocks = re.findall(
        r'person\s*\((?:[^()]*|\((?:[^()]*|\([^()]*\))*\))*\)',
        authors_r,
        re.DOTALL,
    )
    for block in person_blocks:
        if '"cre"' in block or "'cre'" in block:
            email_match = re.search(r'email\s*=\s*["\']([^"\']+)["\']', block)
            if not email_match:
                return True
    return False


# --- Check function ---

def check_maintainer_email(path: Path, desc: dict) -> list[Finding]:
    """Check maintainer email quality against CRAN policies.

    Args:
        path: Path to the R package root directory.
        desc: Parsed DESCRIPTION fields as a dict.

    Returns:
        List of Finding objects for any violations detected.
    """
    findings = []
    desc_file = str(path / "DESCRIPTION")
    authors_r = desc.get("Authors@R", "")

    if not authors_r:
        # No Authors@R field -- DESC-08 already catches this
        return findings

    # Check for cre without email (EMAIL-02)
    if _has_cre_without_email(authors_r):
        findings.append(Finding(
            rule_id="EMAIL-02",
            severity="error",
            title="Maintainer (cre) has no email in Authors@R",
            message="The person with 'cre' role must have an email argument. "
                    "Add email = \"name@domain.com\" to the cre person() entry.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show both the name "
                      "and email address of a single designated maintainer.",
        ))
        # No email to check further rules against
        return findings

    email = extract_cre_email(authors_r)
    if not email:
        # Could not parse email -- might be a complex R expression
        return findings

    email_lower = email.lower()

    # EMAIL-04: Placeholder / invalid format
    # Basic format validation
    if "@" not in email or email.count("@") != 1:
        findings.append(Finding(
            rule_id="EMAIL-04",
            severity="error",
            title="Invalid email format for maintainer",
            message=f"Email '{email}' does not contain exactly one '@' symbol.",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings

    local_part, domain = email_lower.rsplit("@", 1)

    if not local_part:
        findings.append(Finding(
            rule_id="EMAIL-04",
            severity="error",
            title="Empty local part in maintainer email",
            message=f"Email '{email}' has an empty local part (before @).",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings

    if "." not in domain:
        findings.append(Finding(
            rule_id="EMAIL-04",
            severity="error",
            title="Invalid domain in maintainer email",
            message=f"Email domain '{domain}' has no dot -- not a valid domain.",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings

    if " " in email:
        findings.append(Finding(
            rule_id="EMAIL-04",
            severity="error",
            title="Space in maintainer email address",
            message=f"Email '{email}' contains spaces. Remove all spaces.",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings

    # EMAIL-06: Noreply/automated addresses (check before mailing list / placeholder)
    for pattern in NOREPLY_PATTERNS:
        if re.search(pattern, email_lower):
            findings.append(Finding(
                rule_id="EMAIL-06",
                severity="error",
                title="Noreply/automated email address",
                message=f"Email '{email}' is a noreply or automated address. "
                        "CRAN requires an email that can receive and respond to mail.",
                file=desc_file,
                cran_says="That contact address must be kept up to date, and be "
                          "usable for information mailed by the CRAN team without "
                          "any form of filtering, confirmation.",
            ))
            return findings

    # EMAIL-01: Mailing list addresses (check before placeholder patterns)
    if domain in MAILING_LIST_DOMAINS:
        findings.append(Finding(
            rule_id="EMAIL-01",
            severity="error",
            title="Maintainer email is a mailing list address",
            message=f"Email '{email}' uses mailing list domain '{domain}'. "
                    "CRAN requires a personal email, not a mailing list.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show both the name "
                      "and email address of a single designated maintainer "
                      "(a person, not a mailing list).",
        ))
        return findings

    # Check local part for mailing list prefixes
    local_base = local_part.split(".")[0] if "." in local_part else local_part
    if local_base in MAILING_LIST_LOCAL_PREFIXES:
        findings.append(Finding(
            rule_id="EMAIL-01",
            severity="error",
            title="Maintainer email looks like a generic/team address",
            message=f"Email '{email}' starts with '{local_base}@' which "
                    "suggests a team or generic address. CRAN requires a "
                    "personal email for the maintainer.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show both the name "
                      "and email address of a single designated maintainer "
                      "(a person, not a mailing list).",
        ))
        return findings

    # Check for mailing list keywords in local part
    for keyword in MAILING_LIST_LOCAL_KEYWORDS:
        if keyword in local_part:
            findings.append(Finding(
                rule_id="EMAIL-01",
                severity="error",
                title="Maintainer email contains mailing list keyword",
                message=f"Email '{email}' contains '{keyword}' which suggests "
                        "a mailing list. CRAN requires a personal email.",
                file=desc_file,
                cran_says="The package's DESCRIPTION file must show both the name "
                          "and email address of a single designated maintainer "
                          "(a person, not a mailing list).",
            ))
            return findings

    # Check for domain starting with "lists."
    if domain.startswith("lists."):
        findings.append(Finding(
            rule_id="EMAIL-01",
            severity="error",
            title="Maintainer email is on a lists.* domain",
            message=f"Email '{email}' uses domain '{domain}' which is a "
                    "mailing list server. Use a personal email address.",
            file=desc_file,
            cran_says="The package's DESCRIPTION file must show both the name "
                      "and email address of a single designated maintainer "
                      "(a person, not a mailing list).",
        ))
        return findings

    # EMAIL-04: Placeholder domains and patterns
    if domain in PLACEHOLDER_DOMAINS:
        findings.append(Finding(
            rule_id="EMAIL-04",
            severity="error",
            title="Placeholder email domain",
            message=f"Email '{email}' uses placeholder domain '{domain}'. "
                    "Replace with a real, working email address.",
            file=desc_file,
            cran_says="a valid (RFC 2822) email address in angle brackets",
        ))
        return findings

    for pattern in PLACEHOLDER_PATTERNS:
        if re.match(pattern, email_lower):
            findings.append(Finding(
                rule_id="EMAIL-04",
                severity="error",
                title="Placeholder email address",
                message=f"Email '{email}' looks like a template placeholder. "
                        "Replace with a real, working email address.",
                file=desc_file,
                cran_says="a valid (RFC 2822) email address in angle brackets",
            ))
            return findings

    # EMAIL-03: Disposable email domains
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        findings.append(Finding(
            rule_id="EMAIL-03",
            severity="warning",
            title="Disposable email domain",
            message=f"Email '{email}' uses disposable domain '{domain}'. "
                    "CRAN requires a long-lived email address. Use a permanent "
                    "provider (Gmail, Outlook, ProtonMail, or custom domain).",
            file=desc_file,
            cran_says="Make sure this email address is likely to be around for "
                      "a while and that it's not heavily filtered.",
        ))

    # EMAIL-05: Institutional email longevity warning
    for pattern in ACADEMIC_DOMAIN_PATTERNS:
        if re.search(pattern, domain):
            findings.append(Finding(
                rule_id="EMAIL-05",
                severity="note",
                title="Institutional email may not outlast career changes",
                message=f"Email '{email}' uses an academic domain. "
                        "University emails often become undeliverable after "
                        "leaving the institution -- the #1 cause of CRAN "
                        "package archival. Consider a stable personal email.",
                file=desc_file,
                cran_says="Too many people let their maintainer addresses run "
                          "out of service.",
            ))
            break

    return findings
