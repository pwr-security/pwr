import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import validate  # noqa: E402

EXAMPLE = next((ROOT / "pwr").glob("PWR-001-*.xml"))
FULL_NAME = "<full_name>Example Contributor</full_name>"
CREDITS = f"<credits><row>{FULL_NAME}<organization>Independent</organization></row></credits>"


def _base(text):
    text = re.sub(r"\s*<credits>.*?</credits>", "", text, flags=re.S)
    text = re.sub(r"\s*<modified>.*?</modified>", "", text)
    return text.replace("</weakness>", f"  {CREDITS}\n</weakness>")


TEXT = _base(EXAMPLE.read_text())
CREATED = re.search(r"<created>(.*?)</created>", TEXT).group(1)
NAME = EXAMPLE.name


def mutate(old, new):
    assert old in TEXT, old
    return TEXT.replace(old, new, 1)


class Registry:
    """A temporary registry root holding the real schema and given entries."""
    def __init__(self, entries):
        self.dir = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT / "schema", self.dir / "schema")
        (self.dir / "pwr").mkdir()
        for name, content in entries.items():
            (self.dir / "pwr" / name).write_text(content)

    def errors(self, base_ref=None):
        return validate.validate(self.dir, base_ref)[0]

    def close(self):
        shutil.rmtree(self.dir)


class ValidateTest(unittest.TestCase):
    def check(self, entries, expect=None, **kw):
        r = Registry(entries)
        self.addCleanup(r.close)
        errors = r.errors(**kw)
        if expect is None:
            self.assertEqual(errors, [])
        else:
            self.assertTrue(any(expect in e for e in errors), errors)
        return r

    def test_example_is_valid(self):
        self.check({NAME: TEXT})

    def test_valid_variants(self):
        orcid = ("<credits><row><full_name>A B</full_name><orcid>0000-0002-1825-009X</orcid>"
                 "<organization>Independent</organization></row></credits>")
        self.check({NAME: TEXT.replace(TEXT[TEXT.index("<credits>"):TEXT.index("</credits>") + 10], orcid)})
        minimal = TEXT
        for tag in ("alternate_terms", "references", "credits"):
            minimal = minimal.replace(minimal[minimal.index(f"<{tag}>"):minimal.index(f"</{tag}>") + len(tag) + 3], "")
        self.check({NAME: minimal})

    def test_safety_notes_optional(self):
        start = TEXT.index("<safety_notes>")
        end = TEXT.index("</safety_notes>") + len("</safety_notes>")
        self.check({NAME: TEXT[:start] + TEXT[end:]})

    def test_schema_rejections(self):
        cases = {
            "unknown status": ("<status>active</status>", "<status>draft</status>"),
            "unknown abstraction": ("<abstraction>class</abstraction>", "<abstraction>group</abstraction>"),
            "schema_version != 1": ("<schema_version>1<", "<schema_version>2<"),
            "id 0": ("<id>1</id>", "<id>0</id>"),
            "negative content_version": ("<content_version>0<", "<content_version>-1<"),
            "bad date": (f"<created>{CREATED}<", "<created>03/10/2026<"),
            "non-http url": ("https://capec.mitre.org/data/definitions/390.html", "ftp://example.org/x"),
            "bad orcid": (FULL_NAME, FULL_NAME + "<orcid>1234</orcid>"),
            "bad email": (FULL_NAME, FULL_NAME + "<email>nope</email>"),
            "missing full_name": (FULL_NAME, ""),
            "missing organization": ("<organization>Independent</organization>", ""),
            "organization before orcid": ("<organization>Independent</organization>",
                                          "<organization>X</organization><orcid>0000-0002-1825-0097</orcid>"),
        }
        for label, (old, new) in cases.items():
            with self.subTest(label):
                text = mutate(old, new)
                r = Registry({NAME: text})
                self.addCleanup(r.close)
                self.assertTrue(r.errors(), label)

    def test_empty_text_rejected(self):
        start = TEXT.index("<exploitation>")
        end = TEXT.index("</exploitation>") + len("</exploitation>")
        self.check({NAME: TEXT[:start] + "<exploitation>  </exploitation>" + TEXT[end:]}, "schema")

    def test_id_must_match_file_name(self):
        self.check({"PWR-002-x.xml": TEXT}, "does not match file name")

    def test_duplicate_id(self):
        self.check({NAME: TEXT, "PWR-001-other.xml": TEXT}, "duplicate id")

    def test_bad_file_name(self):
        self.check({"entry.xml": TEXT}, "file name must match")

    def test_parent_rules(self):
        self.check({NAME: mutate("<abstraction>class", "<abstraction>base")}, "require a parent")
        self.check({NAME: mutate("</abstraction>", "</abstraction><parent>1</parent>")}, "must not have a parent")
        self.check({NAME: mutate("<abstraction>class</abstraction>",
                                 "<abstraction>base</abstraction><parent>9</parent>")}, "parent 9 does not exist")

    def test_parent_cycle(self):
        a = mutate("<abstraction>class</abstraction>", "<abstraction>base</abstraction><parent>2</parent>")
        b = a.replace("<id>1</id>", "<id>2</id>").replace("<parent>2</parent>", "<parent>1</parent>")
        self.check({NAME: a, "PWR-002-b.xml": b}, "cycle")

    def test_deprecation_rules(self):
        self.check({NAME: mutate("<status>active</status>", "<status>deprecated</status>")},
                   "require replaced_by")
        self.check({NAME: mutate("</created>", "</created><replaced_by>1</replaced_by>")},
                   "only allowed when status is deprecated")

    def test_modified_before_created(self):
        self.check({NAME: mutate("</created>", "</created><modified>2000-01-01</modified>")}, "earlier than created")

    def test_modified_required_when_content_version_above_zero(self):
        self.check({NAME: mutate("<content_version>0<", "<content_version>1<")}, "modified is required")
        self.check({NAME: mutate("<content_version>0<", "<content_version>1<").replace(
            "</created>", "</created><modified>2099-01-01</modified>")})

    def test_xxe_is_not_resolved(self):
        evil = ('<?xml version="1.0"?><!DOCTYPE w [<!ENTITY x SYSTEM "file:///etc/passwd">]>'
                + TEXT.split("?>", 1)[1].replace("<title>Physical", "<title>&x;Physical"))
        r = Registry({NAME: evil})
        self.addCleanup(r.close)
        errors = r.errors()
        self.assertTrue(any("DOCTYPE" in e for e in errors), errors)
        self.assertNotIn("root:", "\n".join(errors))


class BaseRefTest(unittest.TestCase):
    def setUp(self):
        self.reg = Registry({NAME: TEXT})
        self.addCleanup(self.reg.close)
        d = self.reg.dir
        for cmd in (["init", "-q", "-b", "main"], ["add", "."],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"]):
            subprocess.run(["git", "-C", str(d), *cmd], check=True)
        self.path = d / "pwr" / NAME

    def test_unchanged_ok(self):
        self.assertEqual(self.reg.errors("main"), [])

    def test_deletion(self):
        self.path.unlink()
        self.assertTrue(any("deleted" in e for e in self.reg.errors("main")))

    def test_modified_required_after_change(self):
        self.path.write_text(mutate("<title>", "<title>Changed "))
        self.assertTrue(any("modified is required" in e for e in self.reg.errors("main")))
        self.path.write_text(mutate("<title>", "<title>Changed ").replace(
            "</created>", "</created><modified>2099-01-01</modified>"))
        self.assertEqual(self.reg.errors("main"), [])

    def test_content_version_decrease(self):
        self.path.write_text(mutate("<content_version>0<", "<content_version>3<"))
        subprocess.run(["git", "-C", str(self.reg.dir), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-qam", "bump"], check=True)
        self.path.write_text(TEXT)
        self.assertTrue(any("decreased" in e for e in self.reg.errors("main")))

    def test_undeprecate(self):
        dep = (mutate("<status>active</status>", "<status>deprecated</status>")
               .replace("</created>", "</created><replaced_by>2</replaced_by>"
                        "<deprecation_reason>Merged.</deprecation_reason>"))
        (self.reg.dir / "pwr" / "PWR-002-new.xml").write_text(TEXT.replace("<id>1</id>", "<id>2</id>"))
        self.path.write_text(dep)
        subprocess.run(["git", "-C", str(self.reg.dir), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.reg.dir), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-qm", "dep"], check=True)
        self.path.write_text(TEXT)
        self.assertTrue(any("active again" in e for e in self.reg.errors("main")))


if __name__ == "__main__":
    unittest.main()
