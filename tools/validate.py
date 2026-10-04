#!/usr/bin/env python3
"""Validate PWR entries: XSD plus the cross-file rules the XSD cannot express.

Usage: python tools/validate.py [--base-ref origin/main] [--root DIR]

With --base-ref, entries are also compared with their version on that Git ref
(rules 6, 7 and 9: no un-deprecation, content_version never decreases, no deletion).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from lxml import etree

NS = {"p": "urn:pwr:entry"}
FILE_RE = re.compile(r"^PWR-(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.xml$")
# No DTD, no external entities, no network.
PARSER = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, dtd_validation=False)


def parse(source):
    return etree.fromstring(source, PARSER) if isinstance(source, bytes) else etree.parse(str(source), PARSER).getroot()


def meta(root):
    """Return the metadata fields of an entry as a dict (missing fields are None)."""
    def get(name):
        el = root.find(f"p:metadata/p:{name}", NS)
        return el.text.strip() if el is not None and el.text else None
    return {k: get(k) for k in (
        "id", "content_version", "status", "abstraction", "parent",
        "created", "modified", "replaced_by", "deprecation_reason")}


def git(root_dir, *args):
    return subprocess.run(["git", "-C", str(root_dir), *args], capture_output=True, check=False)


def validate(root_dir, base_ref=None):
    root_dir = Path(root_dir)
    errors = []
    err = lambda path, msg: errors.append(f"{path}: {msg}")

    schema = etree.XMLSchema(etree.parse(str(root_dir / "schema" / "pwr-entry.xsd")))
    entries = {}  # id -> (path, meta)

    for path in sorted((root_dir / "pwr").glob("*")):
        rel = path.relative_to(root_dir)
        m = FILE_RE.match(path.name)
        if not m:
            err(rel, "file name must match PWR-<id>-<slug>.xml (lowercase slug)")
            continue
        try:
            doc = parse(path)
        except etree.XMLSyntaxError as e:
            err(rel, f"XML syntax error: {e}")
            continue
        if doc.getroottree().docinfo.doctype:
            err(rel, "DOCTYPE declarations are not allowed")
            continue
        if not schema.validate(doc):
            for e in schema.error_log:
                err(rel, f"schema, line {e.line}: {e.message}")
            continue
        md = meta(doc)
        if int(md["id"]) != int(m.group(1)):  # rule 1
            err(rel, f"id {md['id']} does not match file name (PWR-{m.group(1)})")
        if md["id"] in entries:  # rule 2
            err(rel, f"duplicate id {md['id']} (also in {entries[md['id']][0]})")
        entries[md["id"]] = (rel, md)

    ids = {int(i) for i in entries}
    for rel, md in entries.values():
        if md["abstraction"] == "class" and md["parent"] is not None:  # rule 3
            err(rel, "class entries must not have a parent")
        if md["abstraction"] != "class" and md["parent"] is None:
            err(rel, f"{md['abstraction']} entries require a parent")
        if md["parent"] is not None and int(md["parent"]) not in ids:  # rule 4
            err(rel, f"parent {md['parent']} does not exist")
        if md["status"] == "deprecated":  # rule 5
            for f in ("replaced_by", "deprecation_reason"):
                if md[f] is None:
                    err(rel, f"deprecated entries require {f}")
        else:
            for f in ("replaced_by", "deprecation_reason"):
                if md[f] is not None:
                    err(rel, f"{f} is only allowed when status is deprecated")
        if md["replaced_by"] is not None:
            if int(md["replaced_by"]) not in ids:  # rule 4
                err(rel, f"replaced_by {md['replaced_by']} does not exist")
            elif md["replaced_by"] == md["id"]:
                err(rel, "replaced_by must not point to the entry itself")
        if md["modified"] is None:  # rule 8 (ISO dates compare as strings)
            if int(md["content_version"]) > 0:
                err(rel, "modified is required once content_version is above 0")
        elif md["modified"] < md["created"]:
            err(rel, "modified is earlier than created")

    # Rule 4: no cycle in the parent tree.
    parents = {int(i): int(m["parent"]) for i, (_, m) in entries.items() if m["parent"] is not None}
    for start in parents:
        seen, cur = {start}, parents.get(start)
        while cur is not None:
            if cur in seen:
                err(entries[str(start)][0], "parent chain contains a cycle")
                break
            seen.add(cur)
            cur = parents.get(cur)

    if base_ref:
        compare_with_base(root_dir, base_ref, entries, err)
    return errors, len(entries)


def compare_with_base(root_dir, base_ref, entries, err):
    listing = git(root_dir, "ls-tree", "-r", "--name-only", base_ref, "--", "pwr/")
    if listing.returncode != 0:
        err("git", f"cannot read ref {base_ref}: {listing.stderr.decode().strip()}")
        return
    by_id = {int(i): rel for i, (rel, _) in entries.items()}
    for name in listing.stdout.decode().split():
        m = FILE_RE.match(Path(name).name)
        if not m:
            continue
        old_id = int(m.group(1))
        if old_id not in by_id:  # rule 9
            err(name, "entry was deleted; deprecate it instead (its id stays reserved)")
            continue
        old_bytes = git(root_dir, "show", f"{base_ref}:{name}").stdout
        old = meta(parse(old_bytes))
        new = entries[str(old_id)][1]
        rel = by_id[old_id]
        if old["status"] == "deprecated" and new["status"] != "deprecated":  # rule 6
            err(rel, "a deprecated entry cannot become active again")
        if int(new["content_version"]) < int(old["content_version"]):  # rule 7
            err(rel, f"content_version decreased ({old['content_version']} -> {new['content_version']})")
        if new["modified"] is None and (root_dir / rel).read_bytes() != old_bytes:
            err(rel, "modified is required once the entry has been changed")
        if new["created"] != old["created"]:
            err(rel, "created must not change")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--base-ref")
    args = ap.parse_args()
    errors, count = validate(args.root, args.base_ref)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} error(s) in {count} valid-schema entries", file=sys.stderr)
        return 1
    print(f"OK: {count} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
