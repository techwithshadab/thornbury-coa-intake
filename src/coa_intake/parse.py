"""Deterministic parsing: certificate text -> Certificate (ADR-0007).

Every field is read by an explicit labelled pattern. A field with no match is **absent**, never
guessed — so a layout this parser has not seen produces silence rather than a plausible wrong
number, and the lot goes to a human. That asymmetry is the whole basis of ADR-0007; a "best effort"
fallback here would undo it.

Nothing in this module decides anything. It reads. `rules.py` decides.
"""

from __future__ import annotations

import re

from .domain import DateReading, Measurement
from .policy import Policy

# Every certificate in the corpus cites its method as "<name> (SPEC-7 M-nn)", which makes the method
# the most reliably extractable thing on the page — convenient, since SPEC-7 §3.1 makes it decisive.
METHOD = re.compile(r"((?:[A-Za-z][A-Za-z0-9<>&/.-]*)(?:[ ][A-Za-z0-9<>&/.-]+)* ?\(SPEC-7\s+M-\d+\))")
# Connectors that sit in front of the method name in some layouts ("via HPLC (SPEC-7 M-01)").
# They are not part of the method, and SPEC-7 §3.1 compares the method exactly.
METHOD_CONNECTOR = re.compile(
    r"^(?:(?:via|by|using|method|technique|procedure|determination|result|status|spec"
    r"|pass|fail|conforms)\b\s*[=:]?\s*)+",
    re.IGNORECASE,
)

# A number with a unit attached. Units are drawn from SPEC-7 §2 plus the variants seen in the corpus.
UNIT = r"(?:%|ppm|ppb|mg/kg|g/mL|g/ml)"
VALUE_UNIT = re.compile(rf"(-?\d+(?:\.\d+)?)\s*({UNIT})")

# A limits range in any of the forms the corpus uses: "99.0-101.0", "99.0 to 101.0", "99.0 .. 101.0",
# "[99.0-101.0]". Stripped from a line BEFORE the result is read, so a limit is never mistaken for it.
LIMITS = re.compile(
    rf"\[?\s*-?\d+(?:\.\d+)?\s*(?:{UNIT})?\s*(?:-|–|to|\.\.)\s*-?\d+(?:\.\d+)?\s*(?:{UNIT})?\s*\]?"
)

CONFORMANCE = re.compile(r"\b(PASS|FAIL|CONFORMS|DOES NOT CONFORM)\b", re.IGNORECASE)

# Thornbury item codes: three letters, three digits (MAL-505). Lot numbers carry four (ALD-5420),
# so the two shapes never collide.
MATERIAL_CODE = re.compile(r"\b[A-Z]{3}-\d{3}\b")

NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
TEXT_DATE = re.compile(rf"\b(\d{{1,2}})\s+({MONTHS})[a-z]*\.?\s+(\d{{4}})\b", re.IGNORECASE)
SLASH_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
MONTH_NUM = {m.lower(): i for i, m in enumerate(MONTHS.split("|"), start=1)}

# A document that declares its own convention in prose. Rung 2 of the ADR-0006 ladder: reading a
# document's own instructions is not inference.
STATED_DMY = re.compile(r"dates?\s+are\s+written\s+day[/ -]?month[/ -]?year", re.IGNORECASE)
STATED_MDY = re.compile(r"dates?\s+are\s+written\s+month[/ -]?day[/ -]?year", re.IGNORECASE)

GENERIC_HEADINGS = re.compile(
    r"^\s*(certificate\s+of\s+analysis|analytical\s+report|c\s*e\s*r\s*t\s*i\s*f\s*i\s*c\s*a\s*t\s*e"
    r"|results?|test\s+results?|=+|-+)\s*$",
    re.IGNORECASE,
)


def _labelled(text: str, labels: list[str]) -> str | None:
    """Read `Label ....: value` in any of the corpus's separator styles, or `|LABEL|value`."""
    for label in labels:
        esc = re.escape(label)
        for pattern in (
            rf"^\s*{esc}\s*[.\s]*[:=]\s*(.+?)\s*$",  # "Lot Number:  X"  /  "Item code : X"
            rf"^\s*{esc}\s*\.{{2,}}\s*(.+?)\s*$",  # "Reference ....... X"
            rf"^\s*\|{esc}\|(.+?)(?:\|.*)?$",  # "|LOT|X"  /  "|MFGDATE|X"
        ):
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m and m.group(1).strip():
                return m.group(1).strip()
    return None


def _read_explicit(raw: str) -> DateReading | None:
    """Rung 1 of the ADR-0006 ladder: dates that carry their own meaning. No inference."""
    if m := ISO_DATE.search(raw):
        return DateReading(raw=raw, iso=f"{m.group(1)}-{m.group(2)}-{m.group(3)}", resolution="explicit")
    if m := TEXT_DATE.search(raw):
        day, month, year = int(m.group(1)), MONTH_NUM[m.group(2).lower()[:3]], m.group(3)
        return DateReading(raw=raw, iso=f"{year}-{month:02d}-{day:02d}", resolution="explicit")
    if m := SLASH_DATE.search(raw):
        a, b, year = int(m.group(1)), int(m.group(2)), m.group(3)
        # One component exceeds 12, so the order is forced by the value itself.
        if a > 12 and b <= 12:
            return DateReading(raw=raw, iso=f"{year}-{b:02d}-{a:02d}", resolution="explicit")
        if b > 12 and a <= 12:
            return DateReading(raw=raw, iso=f"{year}-{a:02d}-{b:02d}", resolution="explicit")
    return None


def _read_ambiguous_slash(raw: str, doc_text: str, supplier: str | None, policy: Policy) -> DateReading:
    """Rungs 2-4: both components <= 12, so the document itself has to tell us, or a reviewed
    supplier convention does, or we hold. There is deliberately no rung for country of origin."""
    m = SLASH_DATE.search(raw)
    if not m:
        return DateReading(raw=raw, resolution="ambiguous")
    a, b, year = int(m.group(1)), int(m.group(2)), m.group(3)
    if a > 12 or b > 12:  # neither order works
        return DateReading(raw=raw, resolution="ambiguous")

    # Rung 2 — the document states its own convention. Reading instructions is not inference.
    if STATED_DMY.search(doc_text):
        return DateReading(raw=raw, iso=f"{year}-{b:02d}-{a:02d}", resolution="stated")
    if STATED_MDY.search(doc_text):
        return DateReading(raw=raw, iso=f"{year}-{a:02d}-{b:02d}", resolution="stated")

    # Rung 3 — a reviewed supplier convention, stamped as an INFERENCE, not a reading.
    if supplier and (conv := policy.date_conventions.get(supplier.casefold())):
        iso = f"{year}-{b:02d}-{a:02d}" if conv.order == "DMY" else f"{year}-{a:02d}-{b:02d}"
        return DateReading(raw=raw, iso=iso, resolution="inferred", evidence=", ".join(conv.evidence))

    # Rung 4 — nothing resolved it.
    return DateReading(raw=raw, resolution="ambiguous")


def _read_date(raw: str, doc_text: str, supplier: str | None, policy: Policy) -> DateReading:
    """The ADR-0006 ladder. Stop at the first rung that answers; the bottom rung is ambiguous."""
    if not raw:
        return DateReading(raw="", resolution="ambiguous")
    return _read_explicit(raw) or _read_ambiguous_slash(raw, doc_text, supplier, policy)


def _supplier(text: str, approved: frozenset[str]) -> str | None:
    """Labelled first, then a known approved name, then the first line that looks like a name.

    The third rung matters: an unapproved supplier must still be *read*, or it would be reported as
    an unreadable document rather than as the sourcing question it actually is.
    """
    if value := _labelled(text, ["SUPPLIER", "Supplier", "Manufacturer"]):
        return value
    if m := re.search(r"^\s*Issued by\s+(.+?)\.?\s*$", text, re.IGNORECASE | re.MULTILINE):
        return m.group(1).strip()
    if m := re.search(r"^\s*(.+?)\s+—\s+Certificate of Analysis\s*$", text, re.IGNORECASE | re.MULTILINE):
        return m.group(1).strip()
    for line in (ln.strip() for ln in text.splitlines()):
        if line and line.casefold() in approved:
            return line
    for line in (ln.strip() for ln in text.splitlines()):
        if not line or GENERIC_HEADINGS.match(line):
            continue
        if re.match(r"^[A-Za-zÀ-ÿŁ-ź&.'\- ]{4,60}$", line) and not line.endswith(":"):
            return line
        break
    return None


def _measurement(line: str, doc_id: str, canonical: str, policy: Policy) -> Measurement | None:
    """Read one result row. Returns None when the row carries no usable value."""
    method_match = METHOD.search(line)
    method = METHOD_CONNECTOR.sub("", method_match.group(1).strip()) if method_match else None

    if line.lstrip().startswith("|"):
        # Pipe form: |R|Assay|100.019|%|99.0|101.0|HPLC (...)|PASS — positional, so read it that way
        # rather than stripping limits out of a line where they are separate fields.
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 4 or not NUMBER.fullmatch(parts[2]):
            return None  # not a result row — checked, not caught
        value, unit = float(parts[2]), parts[3]
    else:
        stripped = LIMITS.sub(" ", METHOD.sub(" ", line))
        if not (m := VALUE_UNIT.search(stripped)):
            return None
        value, unit = float(m.group(1)), m.group(2)

    original_value, original_unit = None, None
    for conv in policy.conversions:
        if conv.attribute == canonical and conv.from_unit.casefold() == unit.casefold():
            original_value, original_unit = value, unit
            value, unit = value * conv.factor, conv.to_unit
            break
    if unit == "g/ml":
        unit = "g/mL"

    stated = None
    if c := CONFORMANCE.search(line):
        stated = c.group(1).upper() in ("PASS", "CONFORMS")

    return Measurement(
        attribute=canonical,
        value=value,
        unit=unit,
        source=f"{doc_id}:{line.strip()[:60]}",
        method=method,
        stated_conformance=stated,
        original_value=original_value,
        original_unit=original_unit,
    )


def _row_attribute(line: str, policy: Policy) -> str | None:
    """Which SPEC-7 attribute this row is about, or None if it is not a result row.

    Pipe rows carry a leading record marker — `|R|Assay|100.019|%|...` — so the label is the second
    field, not the first. Trying both is cheaper than a format flag, and a marker that is itself an
    attribute name is not a case that exists.
    """
    if line.lstrip().startswith("|"):
        candidates = [p.strip() for p in line.strip().strip("|").split("|")[:2]]
    else:
        candidates = [re.split(r"[:=]|\s{2,}", line.strip(), maxsplit=1)[0].strip()]
    for candidate in candidates:
        if canonical := policy.synonyms.get(candidate.casefold()):
            return canonical
    return None


def _results(text: str, doc_id: str, policy: Policy) -> tuple[Measurement, ...]:
    """Find each attribute's row. Handles the flat forms directly and the indented block form
    ("Assay:\\n result = ...\\n method = ...") by gathering the block under the heading."""
    lines = text.splitlines()
    found: dict[str, Measurement] = {}

    for i, line in enumerate(lines):
        canonical = _row_attribute(line, policy)
        if not canonical or canonical in found:
            continue

        block = line
        if not line.lstrip().startswith("|"):
            # Gather continuation lines: anything indented deeper than this heading, until a blank
            # line or a line back at the same indent. Covers both the "via <method>" style, where the
            # method sits on the next line, and the "result = / method = / status =" block style.
            indent = len(line) - len(line.lstrip())
            for nxt in lines[i + 1 : i + 8]:
                if not nxt.strip() or (len(nxt) - len(nxt.lstrip())) <= indent:
                    break
                block += " " + nxt.strip()

        if measurement := _measurement(block, doc_id, canonical, policy):
            found[canonical] = measurement

    return tuple(found.values())


def parse_certificate(extraction, policy: Policy, approved: frozenset[str]):
    """The one parse entry. Absent fields stay absent — `rules.py` decides what that means."""
    from .domain import Certificate

    text = extraction.text
    supplier = _supplier(text, approved)

    lot = _labelled(text, ["LOT", "Lot Number", "Batch", "Batch ref", "Identification", "Sample ref"])
    material = _labelled(text, ["Material No", "Item code", "CODE", "Reference"])
    if material is None or not MATERIAL_CODE.fullmatch(material):
        # Fall back to the code's shape. Distinct from a lot number, which carries four digits.
        m = MATERIAL_CODE.search(text)
        material = m.group(0) if m else None

    # Every distinct lot-like token, so a document that disagrees with itself is caught rather than
    # resolved. COA-0018 prints HLW-1185 in the header and HLW-1191 over the results.
    lot_tokens = tuple(sorted(set(re.findall(r"\b[A-Z]{3}-\d{4}\b", text))))

    mfg_raw = (
        _labelled(text, ["MFGDATE", "MFG", "Mfg date", "Date of Manufacture", "Manufactured", "Produced"])
        or ""
    )
    retest_raw = (
        _labelled(text, ["RETESTDATE", "RETEST", "Retest due", "Retest Date", "Valid until", "Re-test by"])
        or ""
    )

    return Certificate(
        doc_id=extraction.doc_id,
        lot_id=lot,
        material_no=material,
        supplier=supplier,
        manufacture_date=_read_date(mfg_raw, text, supplier, policy) if mfg_raw else None,
        retest_date=_read_date(retest_raw, text, supplier, policy) if retest_raw else None,
        results=_results(text, extraction.doc_id, policy),
        lot_id_conflicts=lot_tokens if len(lot_tokens) > 1 else (),
    )
