#!/usr/bin/env python3
"""Apply compressed staff-auth path files into the repo working tree."""
from __future__ import annotations
import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).resolve().parent
manifest = json.loads((BUNDLE / "MANIFEST.json").read_text())
for item in manifest:
    raw = zlib.decompress(base64.b64decode((BUNDLE / item["blob"]).read_text()))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != item["sha256"]:
        raise SystemExit(f"hash mismatch for {item['path']}")
    target = ROOT / item["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    print("wrote", item["path"], item["bytes"], "bytes")
print("OK: staff-auth bundle applied")
