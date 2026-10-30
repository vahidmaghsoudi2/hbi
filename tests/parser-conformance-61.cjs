#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const vm = require("node:vm");
const { execFileSync } = require("node:child_process");
const ts = require(path.join(process.cwd(), "frontend", "node_modules", "typescript"));

const root = process.cwd();
const readHead = (file) => execFileSync("git", ["show", `HEAD:${file}`], { cwd: root, encoding: "utf8" });
const blobSha = (content) => crypto.createHash("sha1").update(`blob ${Buffer.byteLength(content)}\0`).update(content).digest("hex");
const parserPath = "frontend/src/pages/skinProblemParser.ts";
const parserSource = readHead(parserPath);
const mapSource = readHead("docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md");
const recordsSource = readHead("docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md");
const fixture = JSON.parse(fs.readFileSync(path.join(root, "tests/fixtures/skin-problem-bank-expected-61.json"), "utf8"));
const compiled = ts.transpileModule(parserSource, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const sandbox = { exports: {}, module: { exports: {} }, require };
sandbox.module.exports = sandbox.exports;
vm.runInNewContext(compiled, sandbox, { filename: parserPath });
const { parseProblemRecords, getFieldState } = sandbox.module.exports;
const actual = parseProblemRecords(mapSource, recordsSource);
const expectedById = new Map(fixture.r.map((row) => [row[0], row]));
const failures = [];
const results = [];
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
for (const record of actual) {
  const expected = expectedById.get(record.id);
  const diffs = [];
  if (!expected) {
    diffs.push("missing Expected fixture row");
  } else {
    const expectedMapNormalized = expected[3].map((entry) => [entry[0], fixture.v[entry[1]], fixture.v[entry[2]], fixture.v[entry[3]], fixture.v[entry[4]]]);
    const actualMapNormalized = record.mapEntries.map((entry) => [entry.shelfId, entry.name, entry.type, entry.relationshipRaw, entry.disposition]);
    if (!same(actualMapNormalized, expectedMapNormalized)) diffs.push("Map entries mismatch: " + JSON.stringify({ expected: expectedMapNormalized, actual: actualMapNormalized }));
    const expectedFields = expected[4].map(([keyIndex, valueIndex]) => [fixture.k[keyIndex], fixture.v[valueIndex]]);
    const actualFields = record.fields.map((field) => [field.label, field.value]);
    if (!same(actualFields, expectedFields)) diffs.push("field sequence/value mismatch: " + JSON.stringify({ expected: expectedFields, actual: actualFields }));
    const typeField = record.fields.find((field) => field.label === "نوع واحد" || field.label === "Unit type");
    const expectedType = fixture.v[expected[3][0][2]];
    const normalizeType = (value) => value.replace(/\\*\\*/g, "").replace(/`/g, "").split(/\\s+—\\s+/)[0].toLowerCase().replace(/\\s*\\/\\s*/g, "/").replace(/\\s+/g, " ").trim();
    if (!typeField || normalizeType(typeField.value) !== normalizeType(expectedType)) diffs.push("Markdown-insensitive Unit type comparison failed: " + JSON.stringify({ expected: expectedType, actual: typeField?.value ?? null }));
    if (record.id === "P22") {
      const roles = record.mapEntries.map((entry) => [entry.shelfId, entry.role]);
      if (record.canonicalMapEntryIndex !== 0 || !same(roles, [["S04", "canonical"], ["S09", "cross_reference"]])) diffs.push("P22 must be one record with S04 canonical and S09 cross-reference: " + JSON.stringify(roles));
    }
    if (record.id === "P16") {
      const path = record.mapEntries[0]?.pathRaw;
      if (path !== "S02→S07") diffs.push("P16 Map path mismatch: " + String(path));
    }
    if (record.id === "P51" && !record.fields.some((field) => field.label === "Need eligibility")) diffs.push("P51 Need eligibility field missing");
  }
  results.push({ id: record.id, status: diffs.length ? "FAIL" : "PASS", field_count: record.fields.length, map_entry_count: record.mapEntries.length, differences: diffs });
  if (diffs.length) failures.push(...diffs.map((detail) => ({ id: record.id, detail })));
}
if (actual.length !== 61) failures.push({ id: "ALL", detail: `expected 61 records, got ${actual.length}` });
for (const id of expectedById.keys()) if (!actual.some((record) => record.id === id)) failures.push({ id, detail: "Expected record not parsed" });

// Missing, empty and explicit UNKNOWN are distinct states; source fixture contains no empty-valued fields.
const sample = [{ label: "empty", value: "", valueState: "empty" }, { label: "unknown", value: "**UNKNOWN**", valueState: "unknown" }];
const stateChecks = {
  missing: getFieldState(sample, "absent") === "missing",
  empty: getFieldState(sample, "empty") === "empty",
  unknown: getFieldState(sample, "unknown") === "unknown",
};
const fieldStateCounts = { missing: 0, empty: 0, unknown: 0, value: 0 };
for (const record of actual) {
  for (const label of fixture.k) fieldStateCounts[getFieldState(record.fields, label)] += 1;
}
if (Object.values(stateChecks).some((ok) => !ok)) failures.push({ id: "STATE_MODEL", detail: "Missing/Empty/UNKNOWN distinction failed: " + JSON.stringify(stateChecks) });

const head = execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim();
const summary = {
  head,
  parser_blob_sha: blobSha(parserSource),
  map_blob_sha: blobSha(mapSource),
  working_records_blob_sha: blobSha(recordsSource),
  fixture_sha256: crypto.createHash("sha256").update(fs.readFileSync(path.join(root, "tests/fixtures/skin-problem-bank-expected-61.json"))).digest("hex"),
  expected_fixture_records: fixture.r.length,
  parsed_records: actual.length,
  pass: results.filter((row) => row.status === "PASS").length,
  fail: results.filter((row) => row.status === "FAIL").length,
  state_checks: stateChecks,
  field_state_counts: fieldStateCounts,
  results,
  differences: failures,
};
console.log(JSON.stringify(summary, null, 2));
if (failures.length) process.exitCode = 1;
