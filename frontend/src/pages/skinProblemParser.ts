export type FieldValueState = "missing" | "empty" | "unknown" | "value";

export type ProblemField = {
  label: string;
  value: string;
  valueState: Exclude<FieldValueState, "missing">;
};

export type ProblemMapEntry = {
  shelfId: string;
  shelfName: string;
  name: string;
  type: string;
  relationshipRaw: string;
  disposition: string;
  pathRaw: string | null;
  pathSegments: string[];
  role: "canonical" | "cross_reference" | "unspecified";
};

export type ProblemRecord = {
  id: string;
  headingName: string;
  mapEntries: ProblemMapEntry[];
  canonicalMapEntryIndex: number | null;
  fields: ProblemField[];
};

const isProblemId = (value: string) => /^P(?:0[1-9]|[1-5]\d|6[01])$/.test(value);

function fieldValueState(value: string): ProblemField["valueState"] {
  if (value.length === 0) return "empty";
  const plain = value.replace(/\*\*/g, "").replace(/\*/g, "").replace(/<[^>]*>/g, "").trim();
  if (/^UNKNOWN$/i.test(plain)) return "unknown";
  return "value";
}

export function getFieldState(fields: ProblemField[], label: string): FieldValueState {
  const field = fields.find((item) => item.label === label);
  return field ? field.valueState : "missing";
}

function splitTableCells(line: string): string[] {
  const source = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  const cells: string[] = [];
  let current = "";
  let escaped = false;
  for (const character of source) {
    if (character === "|" && !escaped) {
      cells.push(current.trim());
      current = "";
    } else {
      current += character;
    }
    escaped = character === "\\" && !escaped;
    if (character !== "\\") escaped = false;
  }
  cells.push(current.trim());
  return cells;
}

function parseMainTable(section: string): ProblemField[] {
  const lines = section.split(/\r?\n/);
  const fields: ProblemField[] = [];
  let tableStarted = false;
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (/^\s*\|/.test(line)) {
      tableStarted = true;
      const cells = splitTableCells(line);
      if (cells.length < 2) continue;
      if (cells.every((cell) => /^:?-{3,}:?$/.test(cell))) continue;
      if (/^(فیلد|Field)$/i.test(cells[0])) continue;
      const label = cells[0];
      const value = cells.slice(1).join("|").trim();
      if (!label) continue;
      fields.push({ label, value, valueState: fieldValueState(value) });
      continue;
    }
    if (tableStarted) {
      if (!line.trim() && /^\s*\|/.test(lines[index + 1] ?? "")) continue;
      break;
    }
  }
  return fields;
}

function getSection(markdown: string, heading: RegExp, nextHeading: RegExp): string {
  const start = heading.exec(markdown);
  if (!start || start.index === undefined) return "";
  const contentStart = start.index + start[0].length;
  const tail = markdown.slice(contentStart);
  const next = nextHeading.exec(tail);
  return tail.slice(0, next?.index ?? tail.length);
}

function parseMap(mapMarkdown: string): { shelfNames: Map<string, string>; rows: Map<string, ProblemMapEntry[]> } {
  const shelfSection = getSection(mapMarkdown, /^## 2\. Lightweight Skin Problem Space\s*$/m, /^## 3\./m);
  const mapSection = getSection(mapMarkdown, /^## 4\. P01–P61 Mapping\s*$/m, /^## 5\./m);
  if (!shelfSection || !mapSection) throw new Error("Map sections 2 and 4 could not be located.");

  const shelfNames = new Map<string, string>();
  for (const line of shelfSection.split(/\r?\n/)) {
    const match = line.trim().match(/^(S\d{2})\s*[—-]\s*(.+)$/);
    if (match) shelfNames.set(match[1], match[2].trim());
  }

  const rows = new Map<string, ProblemMapEntry[]>();
  let currentShelf = "";
  for (const line of mapSection.split(/\r?\n/)) {
    const trimmed = line.trim();
    const shelfHeading = trimmed.match(/^#{1,6}\s+(S\d{2})\s*$/);
    if (shelfHeading) {
      currentShelf = shelfHeading[1];
      continue;
    }
    const match = trimmed.match(/^(P\d{2})\s+(.+?)\s+—\s+(.+?)\s+—\s+(.+?)\s+—\s+(.+?)\s*$/);
    if (!match || !isProblemId(match[1])) continue;
    const [, id, name, type, relationshipRaw, disposition] = match;
    const pathMatch = relationshipRaw.match(/S\d{2}\s*(?:→|↔|->|<->)\s*S\d{2}/);
    const pathRaw = pathMatch?.[0] ?? null;
    const pathSegments = pathRaw ? pathRaw.split(/\s*(?:→|↔|->|<->)\s*/) : [];
    const entries = rows.get(id) ?? [];
    entries.push({
      shelfId: currentShelf,
      shelfName: shelfNames.get(currentShelf) ?? "",
      name: name.trim(),
      type: type.trim(),
      relationshipRaw: relationshipRaw.trim(),
      disposition: disposition.trim(),
      pathRaw,
      pathSegments,
      role: "unspecified",
    });
    rows.set(id, entries);
  }

  const p22Entries = rows.get("P22") ?? [];
  for (const entry of p22Entries) {
    if (entry.shelfId === "S04") entry.role = "canonical";
    else if (entry.shelfId === "S09") entry.role = "cross_reference";
  }
  return { shelfNames, rows };
}

export function parseProblemRecords(mapMarkdown: string, workingRecordsMarkdown: string): ProblemRecord[] {
  const { rows: mapRows } = parseMap(mapMarkdown);
  const headings = [...workingRecordsMarkdown.matchAll(/^#{1,6}\s+(?:رکورد|Record)\s+(P\d{2})\s*[—-]\s*(.+?)\s*$/gm)]
    .filter((match) => isProblemId(match[1]));
  const records = new Map<string, ProblemRecord[]>();

  for (let index = 0; index < headings.length; index += 1) {
    const heading = headings[index];
    const id = heading[1];
    const start = (heading.index ?? 0) + heading[0].length;
    const end = index + 1 < headings.length
      ? (headings[index + 1].index ?? workingRecordsMarkdown.length)
      : workingRecordsMarkdown.length;
    const fields = parseMainTable(workingRecordsMarkdown.slice(start, end));
    const entries = records.get(id) ?? [];
    entries.push({
      id,
      headingName: heading[2].trim(),
      mapEntries: mapRows.get(id) ?? [],
      canonicalMapEntryIndex: id === "P22"
        ? (mapRows.get(id) ?? []).findIndex((entry) => entry.shelfId === "S04")
        : null,
      fields,
    });
    records.set(id, entries);
  }

  const result: ProblemRecord[] = [];
  for (let number = 1; number <= 61; number += 1) {
    const id = `P${String(number).padStart(2, "0")}`;
    const matches = records.get(id) ?? [];
    if (matches.length !== 1) {
      throw new Error(`${id}: expected exactly one record heading; found ${matches.length}.`);
    }
    const record = matches[0];
    if (!record.fields.length) throw new Error(`${id}: main field table was not found.`);
    if (!record.mapEntries.length) throw new Error(`${id}: no Map row was found.`);
    result.push(record);
  }
  return result;
}
