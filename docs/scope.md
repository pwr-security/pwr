# Scope

The Physical Weakness Registry (PWR) lists weaknesses in the physical security of facilities: the conditions that let a deliberate adversary reach people, assets or information they should not reach, or that let a security control fail.

## The rule

A weakness is in scope if exploiting it requires a deliberate adversary, or if it describes a physical security control that fails to do its job.

## In scope

- Entry to buildings, rooms and zones: doors, windows and other openings, locks, barriers, turnstiles, visitor handling.
- Access credentials: badges, keys, codes, their issuing, cloning and revocation.
- Monitoring and response: video surveillance, intrusion detection, alarms, and the people who act on them.
- Logging of physical access: what is recorded, kept, protected and reviewed.
- Weaknesses of the organization's own security processes that let the above fail.

## Out of scope

- **Fire safety, accidents and natural hazards.** They appear only as a constraint on a mitigation (for example, a lock must not block evacuation), or as the cause of a security weakness (for example, an emergency exit that doubles as an unguarded entrance).
- **Weaknesses of hardware and software products**, such as a flaw in a specific reader or controller. These belong to CWE and CVE. PWR describes the state of a facility, not a product.
- **Network and software security** that has no physical component.
- **Specific facilities, organizations or people.** The registry describes general weaknesses, never targets.

## Boundaries with other catalogs

| Catalog | Relation to PWR |
|---|---|
| CWE | Weaknesses in hardware and software. PWR starts where the facility begins. Mentioned as a reference at the boundary, never copied. |
| CAPEC | Attack patterns. PWR names the weakness, and CAPEC may be cited as a reference for how it is abused. |
| ISO/IEC 27001, NIST SP 800-53 | Control catalogs. They say what to implement. PWR says what goes wrong when it is missing. Cited by identifier only. |

## Borderline cases

When a proposal could fit in or out, ask:

1. Does it need an adversary to cause harm, or does harm occur without one? Without one, it is out.
2. Is the defect in the facility's arrangement or in a product? In a product, it is out.
3. Would a security assessor report it as a finding about physical security? If yes, it is likely in.

If doubt remains, open an issue and discuss it before writing the entry.
