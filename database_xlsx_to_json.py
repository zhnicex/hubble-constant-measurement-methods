#!/usr/bin/env python3
"""Convert the Hubble-constant XLSX database into machine-readable JSON.

The workbook is the single source of truth:
  - Database sheet: method records.
  - Schema sheet: field definitions, controlled vocabularies, and style legend.

For style-coded fields (currently Target, Facility, and Data Product), controlled
vocabulary values are inferred by matching font colours / cell fills against the
legend in the Schema sheet. Rich-text runs are supported. Style-coded fields
always use one normalized array shape, with each controlled-vocabulary value
explicitly paired with the description fragment carrying its style.

Outputs:
  schema.json      field definitions + controlled vocabularies
  methods.json     normalized method data
  validation.json  conversion warnings/errors

No third-party Python packages are required; the script reads XLSX as OOXML.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET
from zipfile import ZipFile

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN_NS, "r": REL_NS}

# Stable machine IDs. Display labels remain in the XLSX and may be edited freely.
FIELD_ALIASES = {
    "method": "method",
    "principle": "principle",
    "target": "target",
    "facility": "facility",
    "data product": "data_product",
    "physical quantity": "physical_quantities",
    "physical quantities": "physical_quantities",
    "detail": "details",
    "details": "details",
    "$h_0$ inference route": "h0_inference_route",
    "h0 inference route": "h0_inference_route",
    "redshift range": "redshift_range",
    "redshift": "redshift_range",
    "z": "redshift_range",
    "cosmic epoch": "cosmic_epoch",
    "cosmological model dependence": "cosmological_model_dependence",
    "cosmological model dependency": "cosmological_model_dependence",
    "reference": "references",
    "references": "references",
}

OBSERVATION_FIELDS = {"target", "facility", "data_product", "physical_quantities"}
FIELD_TYPES = {
    "method": "string",
    "principle": "controlled_vocabulary",
    "target": "controlled_vocabulary_with_description",
    "facility": "controlled_vocabulary_with_description",
    "data_product": "controlled_vocabulary_with_description",
    "physical_quantities": "array[string]",
    "details": "string",
    "h0_inference_route": "array[controlled_vocabulary]",
    "redshift_range": "structured_redshift",
    "cosmic_epoch": "controlled_vocabulary",
    "cosmological_model_dependence": "controlled_vocabulary",
    "references": "array[reference]",
}

OBSERVATION_ROLE_DEFINITIONS = {
    "primary": (
        "defines the method's principal astronomical target and is used for "
        "method discovery/filtering"
    ),
    "auxiliary": (
        "supporting observation, such as host-galaxy redshift measurement, "
        "which is retained in the full observation chain but is not used as "
        "a primary target filter"
    ),
}

# Match only an explicit host-galaxy description. A generic galaxy target must
# remain primary (for example, "galaxy (lens)" or "galaxy (survey)").
HOST_GALAXY_RE = re.compile(r"\bhost(?:\s|[-‐‑‒–—])+galax(?:y|ies)\b", re.IGNORECASE)


@dataclass
class Style:
    font_color: str | None = None
    fill_color: str | None = None


@dataclass
class RichRun:
    text: str
    font_color: str | None = None


@dataclass
class Cell:
    value: str | None = None
    style_id: int = 0
    style: Style = field(default_factory=Style)
    rich_runs: list[RichRun] = field(default_factory=list)


@dataclass
class VocabEntry:
    value: str
    definition: str | None
    style: Style


@dataclass
class Vocab:
    field_id: str
    assignment: str
    style_channels: list[str]
    entries: list[VocabEntry]


class XlsxReader:
    """Minimal OOXML reader for values, merged cells, styles, and rich text."""

    def __init__(self, path: Path):
        self.path = path
        self.zip = ZipFile(path)
        self.shared_strings: list[tuple[str, list[RichRun]]] = []
        self.cell_styles: list[Style] = []
        self.sheet_paths: dict[str, str] = {}
        self._load_styles()
        self._load_shared_strings()
        self._load_sheet_paths()

    def close(self) -> None:
        self.zip.close()

    def _load_styles(self) -> None:
        root = ET.fromstring(self.zip.read("xl/styles.xml"))
        fonts = root.find("m:fonts", NS)
        fills = root.find("m:fills", NS)
        xfs = root.find("m:cellXfs", NS)

        font_colors: list[str | None] = []
        if fonts is not None:
            for font in fonts:
                font_colors.append(_xml_color(font.find("m:color", NS)))

        fill_colors: list[str | None] = []
        if fills is not None:
            for fill in fills:
                pattern = fill.find("m:patternFill", NS)
                if pattern is None or pattern.attrib.get("patternType") != "solid":
                    fill_colors.append(None)
                else:
                    fill_colors.append(_xml_color(pattern.find("m:fgColor", NS)))

        self.cell_styles = []
        if xfs is not None:
            for xf in xfs:
                font_id = int(xf.attrib.get("fontId", "0"))
                fill_id = int(xf.attrib.get("fillId", "0"))
                self.cell_styles.append(
                    Style(
                        font_color=font_colors[font_id] if font_id < len(font_colors) else None,
                        fill_color=fill_colors[fill_id] if fill_id < len(fill_colors) else None,
                    )
                )

    def _load_shared_strings(self) -> None:
        if "xl/sharedStrings.xml" not in self.zip.namelist():
            return
        root = ET.fromstring(self.zip.read("xl/sharedStrings.xml"))
        result: list[tuple[str, list[RichRun]]] = []
        for si in root.findall("m:si", NS):
            run_nodes = si.findall("m:r", NS)
            if run_nodes:
                runs: list[RichRun] = []
                full = []
                for run in run_nodes:
                    t = run.find("m:t", NS)
                    text = (t.text or "") if t is not None else ""
                    props = run.find("m:rPr", NS)
                    color = _xml_color(props.find("m:color", NS)) if props is not None else None
                    runs.append(RichRun(text=text, font_color=color))
                    full.append(text)
                result.append(("".join(full), runs))
            else:
                # Plain strings can occasionally contain multiple <t> nodes.
                text = "".join((t.text or "") for t in si.findall(".//m:t", NS))
                result.append((text, []))
        self.shared_strings = result

    def _load_sheet_paths(self) -> None:
        workbook = ET.fromstring(self.zip.read("xl/workbook.xml"))
        rels = ET.fromstring(self.zip.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship")
        }
        for sheet in workbook.findall("m:sheets/m:sheet", NS):
            name = sheet.attrib["name"]
            rid = sheet.attrib[f"{{{REL_NS}}}id"]
            target = rel_map[rid]
            if not target.startswith("/"):
                target = "xl/" + target.lstrip("/")
            else:
                target = target.lstrip("/")
            self.sheet_paths[name] = target

    def read_sheet(self, name: str, expand_merges: bool = False) -> dict[str, Cell]:
        if name not in self.sheet_paths:
            raise KeyError(f"Sheet not found: {name!r}. Available: {list(self.sheet_paths)}")
        root = ET.fromstring(self.zip.read(self.sheet_paths[name]))
        cells: dict[str, Cell] = {}

        for node in root.findall(".//m:sheetData/m:row/m:c", NS):
            ref = node.attrib["r"]
            style_id = int(node.attrib.get("s", "0"))
            style = deepcopy(self.cell_styles[style_id]) if style_id < len(self.cell_styles) else Style()
            value, rich_runs = self._cell_value(node)
            cells[ref] = Cell(value=value, style_id=style_id, style=style, rich_runs=rich_runs)

        if expand_merges:
            merge_cells = root.find("m:mergeCells", NS)
            if merge_cells is not None:
                for merge in merge_cells.findall("m:mergeCell", NS):
                    start, end = merge.attrib["ref"].split(":")
                    top = cells.get(start, Cell())
                    min_col, min_row = _split_ref(start)
                    max_col, max_row = _split_ref(end)
                    for row in range(min_row, max_row + 1):
                        for col in range(min_col, max_col + 1):
                            ref = f"{_col_name(col)}{row}"
                            if ref not in cells or not _clean(cells[ref].value):
                                cells[ref] = deepcopy(top)
        return cells

    def _cell_value(self, node: ET.Element) -> tuple[str | None, list[RichRun]]:
        cell_type = node.attrib.get("t")
        if cell_type == "inlineStr":
            is_node = node.find("m:is", NS)
            if is_node is None:
                return None, []
            runs = []
            run_nodes = is_node.findall("m:r", NS)
            if run_nodes:
                text_parts = []
                for run in run_nodes:
                    t = run.find("m:t", NS)
                    text = (t.text or "") if t is not None else ""
                    props = run.find("m:rPr", NS)
                    color = _xml_color(props.find("m:color", NS)) if props is not None else None
                    runs.append(RichRun(text=text, font_color=color))
                    text_parts.append(text)
                return "".join(text_parts), runs
            return "".join((t.text or "") for t in is_node.findall(".//m:t", NS)), []

        v = node.find("m:v", NS)
        if v is None or v.text is None:
            return None, []
        if cell_type == "s":
            idx = int(v.text)
            if idx >= len(self.shared_strings):
                return None, []
            return self.shared_strings[idx]
        if cell_type == "b":
            return "TRUE" if v.text == "1" else "FALSE", []
        return v.text, []


def _xml_color(node: ET.Element | None) -> str | None:
    """Return explicit RGB as #RRGGBB; theme/indexed colours are not classification colours."""
    if node is None:
        return None
    rgb = node.attrib.get("rgb")
    if rgb:
        rgb = rgb.upper()
        if len(rgb) == 8:  # ARGB -> RGB
            rgb = rgb[2:]
        return "#" + rgb
    return None


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _normalize_label(label: str) -> str:
    x = label.strip().lower()
    x = x.replace("−", "-").replace("–", "-")
    x = re.sub(r"\s+", " ", x)
    return x


def _canonical_field(label: str) -> str:
    key = _normalize_label(label)
    if key in FIELD_ALIASES:
        return FIELD_ALIASES[key]
    # Conservative fallback for future columns.
    key = re.sub(r"\$|\\|\{|\}", "", key)
    key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    return key or "field"


def _split_label_definition(text: str) -> tuple[str, str | None]:
    if ":" not in text:
        return text.strip(), None
    label, definition = text.split(":", 1)
    return label.strip(), definition.strip() or None


def _split_ref(ref: str) -> tuple[int, int]:
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    if not m:
        raise ValueError(f"Invalid cell reference: {ref}")
    col_letters, row = m.groups()
    col = 0
    for ch in col_letters:
        col = col * 26 + (ord(ch) - 64)
    return col, int(row)


def _col_name(col: int) -> str:
    chars = []
    while col:
        col, rem = divmod(col - 1, 26)
        chars.append(chr(65 + rem))
    return "".join(reversed(chars))


def _max_row(cells: dict[str, Cell]) -> int:
    return max((_split_ref(ref)[1] for ref in cells), default=0)


def _max_col(cells: dict[str, Cell]) -> int:
    return max((_split_ref(ref)[0] for ref in cells), default=0)


def _dedupe(items: Iterable[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _slugify(text: str) -> str:
    replacements = {
        "σ": "sigma",
        "Σ": "sigma",
        "α": "alpha",
        "β": "beta",
        "γ": "gamma",
        "&": " and ",
        "+": " plus ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "method"


def observation_role(targets: Any) -> str:
    """Classify an observation from its target descriptions only.

    An observation is auxiliary only when it has at least one target and every
    target description explicitly says host galaxy/galaxies. Missing targets,
    missing descriptions, and mixed host/non-host targets remain primary.
    """
    if not isinstance(targets, list) or not targets:
        return "primary"
    descriptions = [
        target.get("description")
        for target in targets
        if isinstance(target, dict)
    ]
    if len(descriptions) != len(targets):
        return "primary"
    return (
        "auxiliary"
        if all(isinstance(text, str) and HOST_GALAXY_RE.search(text) for text in descriptions)
        else "primary"
    )


def build_schema(reader: XlsxReader, database_cells: dict[str, Cell], schema_cells: dict[str, Cell]) -> tuple[dict[str, Any], dict[str, Vocab], dict[str, int]]:
    """Build compact schema.json and runtime vocabulary maps from the Schema sheet."""
    # Database header mapping is authoritative for the actual data columns.
    db_col_to_field: dict[int, str] = {}
    fields: dict[str, Any] = {}
    for col in range(1, _max_col(database_cells) + 1):
        value = _clean(database_cells.get(f"{_col_name(col)}1", Cell()).value)
        if not value:
            continue
        field_id = _canonical_field(value)
        db_col_to_field[col] = field_id
        fields[field_id] = {
            "label": value,
            "definition": None,
            "source_column": _col_name(col),
            "scope": "observation" if field_id in OBSERVATION_FIELDS else "method",
            "type": FIELD_TYPES.get(field_id, "string"),
            "controlled_vocabulary": False,
        }

    vocabularies: dict[str, Vocab] = {}
    notes: dict[str, Any] = {}

    # Schema row 1 gives definitions; rows below give vocab entries by column.
    for col in range(1, _max_col(schema_cells) + 1):
        header_cell = schema_cells.get(f"{_col_name(col)}1")
        header_text = _clean(header_cell.value if header_cell else None)
        if not header_text:
            continue
        label, definition = _split_label_definition(header_text)
        field_id = _canonical_field(label)

        if field_id in fields:
            fields[field_id]["definition"] = definition
            # Use the cleaned Schema label as display label, keeping Database column separately.
            fields[field_id]["label"] = label
        else:
            # A header not present in Database (e.g. distance ladder) is a note.
            notes[field_id] = {"label": label, "definition": definition}

        raw_entries: list[tuple[str, Cell]] = []
        for row in range(2, _max_row(schema_cells) + 1):
            cell = schema_cells.get(f"{_col_name(col)}{row}")
            text = _clean(cell.value if cell else None)
            if text:
                raw_entries.append((text, cell))

        if not raw_entries or field_id not in fields:
            continue

        explicit_font = any(cell.style.font_color for _, cell in raw_entries)
        explicit_fill = any(cell.style.fill_color for _, cell in raw_entries)
        if explicit_font or explicit_fill:
            assignment = "style_legend"
            channels = []
            if explicit_font:
                channels.append("font_color")
            if explicit_fill:
                channels.append("fill_color")
            # In a style legend the cell text itself is the controlled value.
            # Colons can be part of the value (e.g. "EM: radio band ...").
            entries = [
                VocabEntry(value=text, definition=None, style=deepcopy(cell.style))
                for text, cell in raw_entries
            ]
        else:
            assignment = "exact_text"
            channels = []
            entries = []
            for text, cell in raw_entries:
                value, entry_def = _split_label_definition(text)
                entries.append(VocabEntry(value=value, definition=entry_def, style=deepcopy(cell.style)))

        vocab = Vocab(field_id=field_id, assignment=assignment, style_channels=channels, entries=entries)
        vocabularies[field_id] = vocab
        fields[field_id]["controlled_vocabulary"] = True

    controlled_json: dict[str, Any] = {}
    for field_id, vocab in vocabularies.items():
        item: dict[str, Any] = {
            "assignment": vocab.assignment,
            "entries": [],
        }
        if vocab.style_channels:
            item["style_channels"] = vocab.style_channels
        for entry in vocab.entries:
            e: dict[str, Any] = {"value": entry.value, "definition": entry.definition}
            if vocab.assignment == "style_legend":
                e["style"] = {
                    "font_color": entry.style.font_color,
                    "fill_color": entry.style.fill_color,
                }
            item["entries"].append(e)
        controlled_json[field_id] = item

    # observation_role is derived during conversion rather than read from a
    # workbook column, so its schema definition is maintained here.
    fields["observation_role"] = {
        "label": "Observation Role",
        "definition": "whether an observation defines the principal target or supports it",
        "scope": "observation",
        "type": "controlled_vocabulary",
        "controlled_vocabulary": True,
    }
    controlled_json["observation_role"] = {
        "assignment": "derived",
        "entries": [
            {"value": value, "definition": definition}
            for value, definition in OBSERVATION_ROLE_DEFINITIONS.items()
        ],
    }

    schema = {
        "schema_version": "2.1.0",
        "fields": fields,
        "controlled_vocabularies": controlled_json,
        "notes": notes,
    }
    return schema, vocabularies, db_col_to_field


def classify_style(cell: Cell, vocab: Vocab) -> list[str]:
    """Map a cell (including rich text runs) to one or more style-coded CV values."""
    if vocab.assignment != "style_legend":
        return []

    font_colors = []
    if cell.rich_runs:
        font_colors.extend(run.font_color for run in cell.rich_runs if run.text.strip() and run.font_color)
    if cell.style.font_color:
        font_colors.append(cell.style.font_color)
    font_colors = _dedupe(font_colors)

    fill_colors = [cell.style.fill_color] if cell.style.fill_color else []

    font_map: dict[str, list[str]] = {}
    fill_map: dict[str, list[str]] = {}
    for entry in vocab.entries:
        if entry.style.font_color:
            font_map.setdefault(entry.style.font_color, []).append(entry.value)
        if entry.style.fill_color:
            fill_map.setdefault(entry.style.fill_color, []).append(entry.value)

    # Preserve the order in which colours occur in the source rich text.
    matches = []
    for color in font_colors:
        matches.extend(font_map.get(color, []))
    for color in fill_colors:
        matches.extend(fill_map.get(color, []))
    return _dedupe(matches)


def classify_style_entries(cell: Cell, vocab: Vocab) -> list[dict[str, str]]:
    """Pair each style-coded controlled value with its own description."""
    if vocab.assignment != "style_legend":
        return []

    font_map: dict[str, list[str]] = {}
    fill_map: dict[str, list[str]] = {}
    for entry in vocab.entries:
        if entry.style.font_color:
            font_map.setdefault(entry.style.font_color, []).append(entry.value)
        if entry.style.fill_color:
            fill_map.setdefault(entry.style.fill_color, []).append(entry.value)

    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(value: str, description: str) -> None:
        description = description.strip()
        pair = (value, description)
        if description and pair not in seen:
            result.append({"controlled_vocabulary": value, "description": description})
            seen.add(pair)

    # A rich-text run without its own colour inherits the cell font colour in
    # Excel. This is common when only one fragment is recoloured: for example,
    # a galaxy-coloured cell whose final "cluster" run is explicitly purple.
    # Treating colourless runs as unclassified would silently drop the galaxy
    # fragment as soon as any explicitly coloured run is present.
    styled_runs = [
        (run, run.font_color or cell.style.font_color)
        for run in cell.rich_runs
        if (
            run.text.strip()
            and (run.font_color or cell.style.font_color)
            and font_map.get(run.font_color or cell.style.font_color or "")
        )
    ]
    if styled_runs:
        for run, effective_color in styled_runs:
            for value in font_map.get(effective_color or "", []):
                add(value, run.text)
        if cell.style.fill_color:
            for value in fill_map.get(cell.style.fill_color, []):
                add(value, cell.value or "")
        return result

    description = _clean(cell.value) or ""
    if cell.style.font_color:
        for value in font_map.get(cell.style.font_color, []):
            add(value, description)
    if cell.style.fill_color:
        for value in fill_map.get(cell.style.fill_color, []):
            add(value, description)
    return result


def parse_references(text: str | None, issues: list[dict[str, Any]], row: int) -> list[dict[str, Any]]:
    if not text or text.strip().lower() in {"n/a", "na", "/", "\\", "-"}:
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append({"level": "error", "row": row, "field": "references", "message": f"Invalid JSON: {exc}"})
        return [{"text": text, "url": None}]

    flat = []
    def walk(x: Any) -> None:
        if isinstance(x, list):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            flat.append({"text": x.get("text"), "url": x.get("url")})
        elif x is not None:
            issues.append({"level": "warning", "row": row, "field": "references", "message": f"Ignored unexpected reference item: {x!r}"})
    walk(value)
    return flat


def parse_physical_quantities(text: str | None) -> list[str]:
    if not text:
        return []
    return _dedupe(part.strip() for part in re.split(r"[,\n]+", text) if part.strip())


def parse_controlled_values(text: str | None, allowed: set[str] | None = None) -> list[str]:
    """Parse one or more controlled-vocabulary values from a method-level cell.

    Multi-value cells may use line breaks, semicolons, or a spaced `` + ``
    separator. An exact vocabulary match is checked first so punctuation inside
    a future controlled value is never split accidentally.
    """
    if not text:
        return []
    value = text.strip()
    if allowed and value in allowed:
        return [value]
    return _dedupe(
        part.strip()
        for part in re.split(r"(?:\r?\n|;|\s+\+\s+)", value)
        if part.strip()
    )


def _parse_number(token: str) -> float | None:
    token = token.strip().replace("$", "").replace("\\", "")
    token = token.replace("{", "").replace("}", "")
    token = token.replace("−", "-").replace("–", "-")
    token = token.replace("approx", "").replace("sim", "")
    token = token.strip(" ~=<>≤≥")
    try:
        return float(token)
    except ValueError:
        return None


def parse_redshift(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    display = text.strip()
    components = []

    for raw_line in re.split(r"[\n;]+", display):
        line = raw_line.strip()
        if not line:
            continue
        role = None
        body = line
        if ":" in line:
            possible_role, rest = line.split(":", 1)
            if not re.search(r"\d", possible_role):
                role = possible_role.strip()
                body = rest.strip()

        body = body.replace("$", "").replace("\\leq", "<=").replace("\\geq", ">=")
        body = body.replace("≤", "<=").replace("≥", ">=").replace("−", "-").replace("–", "-")
        approximate = "~" in body or "\\sim" in raw_line or "≈" in body

        range_match = re.search(r"(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)", body)
        if range_match:
            comp = {
                "role": role,
                "min": float(range_match.group(1)),
                "max": float(range_match.group(2)),
            }
            if approximate:
                comp["approximate"] = True
            components.append(comp)
            continue

        bound_match = re.search(r"(<=|>=|<|>)\s*~?\s*(\d+(?:\.\d+)?)", body)
        if bound_match:
            op, number = bound_match.groups()
            number = float(number)
            comp = {"role": role, "bound": op, "value": number}
            if approximate:
                comp["approximate"] = True
            components.append(comp)
            continue

        number_match = re.search(r"~?\s*(\d+(?:\.\d+)?)", body)
        if number_match:
            comp = {"role": role, "value": float(number_match.group(1))}
            if approximate:
                comp["approximate"] = True
            components.append(comp)

    result: dict[str, Any] = {"display": display, "components": components}
    maxima = []
    target_maxima = []
    early_scale_terms = ("standard ruler", "sound horizon", "recombination", "last scattering")
    for comp in components:
        value = comp.get("max", comp.get("value"))
        if value is None:
            continue
        maxima.append(float(value))
        role = (comp.get("role") or "").lower()
        if not any(term in role for term in early_scale_terms):
            target_maxima.append(float(value))
    if target_maxima:
        result["z_max"] = max(target_maxima)
    elif maxima:
        result["z_max"] = max(maxima)
    if maxima:
        result["z_max_all_components"] = max(maxima)
    return result


def build_methods(
    database_cells: dict[str, Cell],
    schema: dict[str, Any],
    vocabularies: dict[str, Vocab],
    db_col_to_field: dict[int, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    max_row = _max_row(database_cells)

    field_to_col = {field_id: col for col, field_id in db_col_to_field.items()}
    method_col = field_to_col.get("method")
    if not method_col:
        raise ValueError("Database sheet must contain a Method column")

    # Group contiguous rows by the merged/expanded Method value.
    groups: list[tuple[str, list[int]]] = []
    current_name = None
    current_rows: list[int] = []
    for row in range(2, max_row + 1):
        method = _clean(database_cells.get(f"{_col_name(method_col)}{row}", Cell()).value)
        if not method:
            continue
        if method != current_name:
            if current_name is not None:
                groups.append((current_name, current_rows))
            current_name = method
            current_rows = [row]
        else:
            current_rows.append(row)
    if current_name is not None:
        groups.append((current_name, current_rows))

    allowed_exact = {
        field_id: {entry.value for entry in vocab.entries}
        for field_id, vocab in vocabularies.items()
        if vocab.assignment == "exact_text"
    }

    methods = []
    used_ids: dict[str, int] = {}
    for method_name, rows in groups:
        first_row = rows[0]
        method_id = _slugify(method_name)
        if method_id in used_ids:
            used_ids[method_id] += 1
            issues.append({"level": "warning", "row": first_row, "field": "method", "message": f"Duplicate method id {method_id!r}; suffix added"})
            method_id = f"{method_id}-{used_ids[method_id]}"
        else:
            used_ids[method_id] = 1

        def first_value(field_id: str) -> str | None:
            col = field_to_col.get(field_id)
            if not col:
                return None
            for row in rows:
                value = _clean(database_cells.get(f"{_col_name(col)}{row}", Cell()).value)
                if value:
                    return value
            return None

        method: dict[str, Any] = {"id": method_id, "name": method_name}

        for field_id in ("principle", "details", "cosmic_epoch", "cosmological_model_dependence"):
            value = first_value(field_id)
            method[field_id] = value
            if value and field_id in allowed_exact and value not in allowed_exact[field_id]:
                issues.append({
                    "level": "error",
                    "row": first_row,
                    "field": field_id,
                    "message": f"Value {value!r} is not in the Schema controlled vocabulary",
                })

        route_allowed = allowed_exact.get("h0_inference_route")
        routes = parse_controlled_values(first_value("h0_inference_route"), route_allowed)
        method["h0_inference_route"] = routes
        for value in routes:
            if route_allowed is not None and value not in route_allowed:
                issues.append({
                    "level": "error",
                    "row": first_row,
                    "field": "h0_inference_route",
                    "message": f"Value {value!r} is not in the Schema controlled vocabulary",
                })

        redshift_text = first_value("redshift_range")
        method["redshift_range"] = parse_redshift(redshift_text)
        method["references"] = parse_references(first_value("references"), issues, first_row)

        observations = []
        seen_observations = set()
        for row in rows:
            obs: dict[str, Any] = {}
            has_content = False

            for field_id in ("target", "facility", "data_product"):
                col = field_to_col.get(field_id)
                if not col:
                    continue
                cell = database_cells.get(f"{_col_name(col)}{row}", Cell())
                description = _clean(cell.value)
                if not description:
                    obs[field_id] = None
                    continue
                has_content = True
                vocab = vocabularies.get(field_id)
                entries = classify_style_entries(cell, vocab) if vocab else []
                obs[field_id] = entries
                if vocab and vocab.assignment == "style_legend" and not entries:
                    issues.append({
                        "level": "error",
                        "row": row,
                        "field": field_id,
                        "message": f"Could not match cell style to Schema legend for {description!r}",
                    })

            obs["observation_role"] = observation_role(obs.get("target"))

            pq_col = field_to_col.get("physical_quantities")
            pq_text = _clean(database_cells.get(f"{_col_name(pq_col)}{row}", Cell()).value) if pq_col else None
            quantities = parse_physical_quantities(pq_text)
            obs["physical_quantities"] = quantities
            has_content = has_content or bool(quantities)

            if has_content:
                signature = json.dumps(obs, ensure_ascii=False, sort_keys=True)
                if signature not in seen_observations:
                    observations.append(obs)
                    seen_observations.add(signature)

        method["observations"] = observations
        methods.append(method)

    report = {
        "method_count": len(methods),
        "error_count": sum(i["level"] == "error" for i in issues),
        "warning_count": sum(i["level"] == "warning" for i in issues),
        "issues": issues,
    }
    return {"schema_version": schema["schema_version"], "methods": methods}, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert database.xlsx into schema.json and methods.json")
    parser.add_argument("xlsx", nargs="?", default="database.xlsx", help="Input XLSX workbook")
    parser.add_argument("--out-dir", default=".", help="Output directory (default: current directory)")
    parser.add_argument("--strict", action="store_true", help="Return non-zero exit code if validation errors are found")
    parser.add_argument("--combined", action="store_true", help="Also write database.json containing schema + methods")
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    reader = XlsxReader(xlsx_path)
    try:
        database_cells = reader.read_sheet("Database", expand_merges=True)
        schema_cells = reader.read_sheet("Schema", expand_merges=False)
        schema, vocabularies, db_col_to_field = build_schema(reader, database_cells, schema_cells)
        methods, report = build_methods(database_cells, schema, vocabularies, db_col_to_field)
    finally:
        reader.close()

    (out_dir / "schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "methods.json").write_text(json.dumps(methods, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.combined:
        combined = {"schema": schema, "methods": methods["methods"]}
        (out_dir / "database.json").write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Converted {xlsx_path}")
    print(f"Methods: {report['method_count']}")
    print(f"Validation: {report['error_count']} error(s), {report['warning_count']} warning(s)")
    print(f"Wrote: {out_dir / 'schema.json'}")
    print(f"Wrote: {out_dir / 'methods.json'}")
    print(f"Wrote: {out_dir / 'validation.json'}")
    if args.combined:
        print(f"Wrote: {out_dir / 'database.json'}")

    return 1 if args.strict and report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
