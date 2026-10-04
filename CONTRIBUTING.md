# Contributing to PWR

Thank you for helping build the Physical Weakness Registry. This page explains how changes are made and what an entry must look like.

## How changes are made

Every change goes through a pull request.

1. **Fork** the repository and create a branch in your fork. Use one of these prefixes: `pwr/`, `fix/`, `schema/`, `ci/`, `docs/` (for example `pwr/tailgating`).
2. Make your change and **sign off** each commit with `git commit -s`.
3. Open a pull request against `main`. One entry per pull request.
4. The `validate` check must pass and the branch must be up to date with `main`. Pull requests are squash-merged.

The maintainers follow the same rules. A first-time contributor's workflow run needs a maintainer's approval before it starts.

## Proposing a new weakness

Open a "Propose a weakness" issue first. The title and the scope are discussed there, and a maintainer reserves the identifier for you. Identifiers are integers, shown as `PWR-<id>`, and are never reused or changed.

Name the file `PWR-<id>-<shortslug>.xml`, with the id on three digits, in `pwr/` (for example `PWR-004-insufficient-enforcement-of-one-person-per-entry-authorization.xml`).

## Writing an entry

An entry is one XML file validated by `schema/pwr-entry.xsd`. Check it locally with:

```
xmllint --noout --schema schema/pwr-entry.xsd pwr/PWR-<id>-*.xml
```

The CI runs further checks that the schema cannot express (identifier matches the file name, parent exists, version rules).

- **Title**: a noun phrase in Title Case that names the defect, not the attack, in the style of CWE ("Missing Physical Entry Control for Sensitive Area"). Attack names go in `alternate_terms` (also Title Case, optional).
- **Level**: `class` is general and has no parent. `base` is specific enough to be found and fixed, and needs a `parent`. `variant` is tied to a context or a technology.
- **Style**: short, precise sentences. A weakness describes a state, not a product. Do not state the level in the text, since `abstraction` already does.
- **Scope**: weaknesses that matter against deliberate adversaries. Fire safety and accidents are in scope only as a constraint on a mitigation, or as the cause of a security weakness.
- **Level of detail**: principle only. Never give step-by-step intrusion instructions.
- **Mitigations and safety notes**: `safety_notes` is optional. Include it when a mitigation can conflict with the safety of people (evacuation, fire rating, accessibility, emergency access).
- **References**: cite standards, CAPEC and CWE by identifier and link. Do not copy their text.
- **Credits**: a full name, an ORCID, and an organization (the legal name of your employer, or `Independent`). An email is optional and discouraged, because it stays in the Git history.
- **No XML comments** in entries.

## Changing an existing entry

- Set `modified` to the date of the change. A new entry has no `modified`.
- Increase `content_version` by one when the meaning changes. Typos and link fixes do not count.
- Entries are never deleted. To retire one, set `status` to `deprecated` and add `replaced_by` and `deprecation_reason`.

## Licensing

By signing off a commit you certify the [Developer Certificate of Origin](https://developercertificate.org/) and agree that your contribution is released under the license of the part you change: CC BY 4.0 for `pwr/` and `schema/`, MIT for everything else. See `LICENSE`. You keep the copyright on your contribution.

## Sensitive information

Do not post operational details that would help someone break into a facility. To report something sensitive, see `SECURITY.md`.
