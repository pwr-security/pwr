# Editorial Policy

This policy sets how entries are written, so that the registry stays consistent and safe to publish.

## Principles

- **A weakness is a state, not an attack and not a product.** The title names the defect. Attack names go in `alternate_terms`. Products and vendors do not appear in titles.
- **Principle level only.** An entry explains why something is weak, never how to break in step by step. Do not list tools, techniques or procedures that give operational help.
- **Short and precise.** Minimal sentences, no filler. The text must read as a reference, not as an essay or a generated summary.
- **Sourced.** Statements that depend on a standard or a publication cite it by identifier and link in `references`.

## Titles and terms

- A noun phrase in Title Case, starting with an idiom such as Missing, Improper, Insufficient, Excessive, Use of or Unprotected.
- Alternate terms use the same capitalization and are optional.

## Language

English, American spelling ("unauthorized", "behavior"). Use plain words and avoid idioms.

## Fields

- **Description**: one or two sentences. Do not state the level of abstraction.
- **Applicability**: where the weakness applies, and what is not affected.
- **Exploitation**: the principle by which the weakness is abused, in one or two sentences.
- **Consequences**: an impact and its details. Use Confidentiality, Integrity, Availability, or a precise term (Access control, Accountability).
- **Potential mitigations**: measures phrased as actions. Do not recommend a product.
- **Safety notes**: optional. Use them when a mitigation could conflict with the safety of people (evacuation, fire rating, accessibility, emergency access, ventilation). Omit the section otherwise.

## Levels

- A **class** is a general weakness with no parent.
- A **base** is specific enough to be found and fixed. This is the level to cite in a report.
- A **variant** applies a base to a particular context or technology. Create one only when it needs its own description or mitigations.

Prefer a base and a clear parent over several near-duplicate entries. Before proposing an entry, check that no existing one already covers it.

## References and third-party content

- Cite CAPEC, CWE, ISO/IEC 27001, NIST SP 800-53 and similar sources by identifier and link.
- Never copy their text. Write your own.
- Do not claim compatibility or endorsement by any of them.

## Credits

Each credit has a full name or an ORCID, and an organization (the legal name, or `Independent`). Emails are optional and discouraged, because they stay in the Git history.

## Changes and retirement

- A change in meaning raises `content_version` by one. Typos and link fixes do not.
- Entries are never deleted. A retired entry becomes `deprecated`, with `replaced_by` and `deprecation_reason`.

## Review checklist

- Does the title name a defect in the right style?
- Is the entry in scope (see `scope.md`)?
- Is it free of operational detail?
- Are references correct, and is no text copied?
- Does it validate, and is its parent right?
