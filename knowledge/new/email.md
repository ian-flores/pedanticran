# CRAN Submission Rules — Maintainer Email

---

## Category: Maintainer Email

### EMAIL-01: Maintainer Email Must Not Be a Mailing List

- **Severity**: REJECTION
- **Rule**: The maintainer (cre) email must belong to a person, not a mailing list, team alias, or group address.
- **CRAN says**: "The package's DESCRIPTION file must show both the name and email address of a single designated maintainer (a person, not a mailing list)."
- **Detection**: Parse the cre person's email from Authors@R. Flag if: the local part contains list keywords (lists, devel, dev-team, team, group, announce, discuss, users); the address starts with info@, admin@, support@, contact@, help@, office@, team@; or the domain is a known mailing list provider (lists.r-forge.r-project.org, lists.sourceforge.net, googlegroups.com, groups.io).
- **Fix**: Use a personal email address for the maintainer (cre) role. Team emails can go in a BugReports or Contact field.
- **Files**: `DESCRIPTION`

### EMAIL-02: Maintainer Must Have Email in Authors@R

- **Severity**: REJECTION
- **Rule**: The person with the cre role in Authors@R must have an email argument. Without it, R cannot derive the Maintainer field.
- **CRAN says**: "The package's DESCRIPTION file must show both the name and email address of a single designated maintainer."
- **Detection**: Parse Authors@R. Find the person() block with "cre" role. Verify it contains an `email =` argument.
- **Fix**: Add email to the cre person: `person("First", "Last", email = "name@domain.com", role = c("aut", "cre"))`.
- **Files**: `DESCRIPTION`

### EMAIL-03: Email Should Not Be from a Disposable Domain

- **Severity**: WARNING
- **Rule**: The maintainer email should not come from a known disposable/temporary email provider. CRAN requires long-term reachability; disposable addresses expire within hours or days.
- **CRAN says**: "Make sure this email address is likely to be around for a while and that it's not heavily filtered."
- **Detection**: Check the email domain against a curated list of known disposable email providers (mailinator.com, guerrillamail.com, tempmail.com, yopmail.com, sharklasers.com, 10minutemail.com, trashmail.com, throwaway.email, etc.).
- **Fix**: Use a permanent personal email address (Gmail, Outlook, ProtonMail, institutional, or custom domain).
- **Files**: `DESCRIPTION`

### EMAIL-04: Email Address Must Not Be a Placeholder

- **Severity**: REJECTION
- **Rule**: The maintainer email must be a real, deliverable address -- not a placeholder or example address from a template.
- **CRAN says**: "a valid (RFC 2822) email address in angle brackets"
- **Detection**: Validate the email address: must have exactly one @, non-empty local part, domain with at least one dot. Flag placeholder domains (example.com, example.org, example.net) and template patterns (your.email@, maintainer@email.com, first.last@example.com, user@domain.com). Flag addresses with spaces or missing components.
- **Fix**: Replace the placeholder with a real, working email address.
- **Files**: `DESCRIPTION`

### EMAIL-05: Institutional Email Longevity Warning

- **Severity**: NOTE
- **Rule**: Institutional email addresses (.edu, .ac.uk, .edu.au, etc.) are valid but higher risk of becoming undeliverable when the maintainer changes institutions. This is the #1 cause of CRAN package archival.
- **CRAN says**: "Too many people let their maintainer addresses run out of service." (Uwe Ligges, R-package-devel)
- **Detection**: Flag emails from university/academic domains: .edu, .ac.uk, .ac.jp, .edu.au, .edu.cn, .uni-*.de, and similar academic TLD patterns.
- **Fix**: Consider using a stable personal email (Gmail, ProtonMail, custom domain) alongside or instead of the institutional address. If using an institutional email, update all CRAN packages promptly when changing institutions.
- **Files**: `DESCRIPTION`

### EMAIL-06: Noreply/Automated Email Addresses Are Not Allowed

- **Severity**: REJECTION
- **Rule**: The maintainer email must be actively monitored and responsive. Noreply, bot, and automated addresses cannot receive CRAN team communications.
- **CRAN says**: "That contact address must be kept up to date, and be usable for information mailed by the CRAN team without any form of filtering, confirmation."
- **Detection**: Flag emails matching noreply patterns: noreply@, no-reply@, donotreply@, do-not-reply@, notifications@github.com, *@users.noreply.github.com, bot@, ci@, automation@.
- **Fix**: Use a personal email address that you actively monitor and can respond to.
- **Files**: `DESCRIPTION`
