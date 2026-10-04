# PWR: Physical Weakness Registry

[![validate](https://img.shields.io/github/actions/workflow/status/pwr-security/pwr/validate.yml?branch=main&label=validate)](https://github.com/pwr-security/pwr/actions/workflows/validate.yml)
[![schema](https://img.shields.io/badge/schema-v1-blue)](schema/pwr-entry.xsd)
[![website](https://img.shields.io/website?url=https%3A%2F%2Fpwr-security.org&label=pwr-security.org)](https://pwr-security.org)

An open registry of physical security weaknesses.

Each entry defines a single weakness as a defective state, such as an absent, insufficient or bypassable control. It is neither an attack technique nor a product advisory. Entries carry a stable identifier, an abstraction level, applicability, consequences, potential mitigations, safety considerations and normative references, so that they can be cited directly in assessment reports.

Published at [pwr-security.org](https://pwr-security.org).

## Repository structure

| Path | Description |
|---|---|
| `pwr/` | Registry entries, one XML file per weakness (`PWR-<id>-<slug>.xml`) |
| `schema/` | XML Schema (XSD 1.0) for entries |
| `tools/` | Validation tooling |
| `tests/` | Tests for the validation tooling |

## Validation

Requires Python 3 and the dependencies listed in `requirements.txt`.

```sh
pip install -r requirements.txt
python tools/validate.py
python -m unittest discover -s tests
```

## Responsible use

This registry is intended for authorized security assessments and defensive work. Perform testing only with explicit written authorization; laws governing lock bypass and unauthorized entry vary by jurisdiction.

Entries describe principles, prerequisites and consequences. They do not contain operational, step-by-step intrusion instructions.
