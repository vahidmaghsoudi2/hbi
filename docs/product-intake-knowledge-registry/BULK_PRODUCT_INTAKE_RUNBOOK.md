# Bulk Product Intake Runbook (100–500 rows)

This utility submits Product identity rows through the existing HBI API. It does not connect to SQLite or any database directly.

## Source CSV

Required columns:

- \`brand\`
- \`product_name\`
- \`product_line\` — explicit operator choice: \`SKIN\`, \`HAIR\`, \`BEAUTY\`, \`TOOLS\`, or \`OTHER\`

Optional columns:

- \`source_key\` — stable row label; if omitted, the CSV line number is used
- \`variant\`
- \`size_value\`
- \`size_unit\`
- \`barcode_gtin\`
- \`market_region\`
- \`country_of_origin\`
- \`packaging_version\`

Do not include \`product_id\`, lifecycle, identity, QA, inventory, price, Evidence, or ProductKnowledge fields. The backend generates Product IDs and controls governance state. A batch is limited to 500 rows. All rows are validated before any API request; repeated identities in the same source file are rejected.

## Dry run

From the repository root:

\`\`\`powershell
python scripts/bulk_product_intake.py --input .\\products.csv --base-url http://127.0.0.1:8000
\`\`\`

Dry-run is the default. It validates the entire file and prints its SHA-256. It does not read a token, write a checkpoint, or call the API.

## Apply

Obtain an access token through the approved HBI authentication flow. Do not put credentials or tokens in the CSV, checkpoint, command arguments, or Git.

In PowerShell, enter the token into the current process environment, then run:

\`\`\`powershell
$secure = Read-Host "HBI bearer access token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:HBI_ACCESS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    python scripts/bulk_product_intake.py --input .\\products.csv --base-url http://127.0.0.1:8000 --apply --checkpoint .\\bulk-intake.checkpoint.json
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Item Env:HBI_ACCESS_TOKEN -ErrorAction SilentlyContinue
    $secure.Dispose()
}
\`\`\`

Use the exact API origin that the operator has separately approved. HTTPS is required for non-local targets; HTTP is accepted only for localhost/loopback. The utility does not select a database or environment for you.

## Resume

Use the same source file, target URL, and checkpoint:

\`\`\`powershell
$secure = Read-Host "HBI bearer access token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:HBI_ACCESS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    python scripts/bulk_product_intake.py --input .\\products.csv --base-url http://127.0.0.1:8000 --apply --resume --checkpoint .\\bulk-intake.checkpoint.json
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Item Env:HBI_ACCESS_TOKEN -ErrorAction SilentlyContinue
    $secure.Dispose()
}
\`\`\`

The checkpoint is written atomically after each row-state transition. An exclusive OS-level lock prevents two runner processes from using the same checkpoint concurrently; the operating system releases the lock when the process exits. It is bound to the source file SHA-256, row keys/hashes, and exact target URL. Changing any of these blocks resume.

## Read-only reconciliation

If a request becomes `UNKNOWN_OUTCOME`, the runner stops at that row and blocks further batch progress until reconciliation. This keeps the uncertain request's audit near the top of the bounded audit list.

Use the same CSV, target and checkpoint. Reconciliation uses only GET requests and records possible audit/Product matches; it never changes the row out of `UNKNOWN_OUTCOME`, never retries a POST, and never declares that a candidate was created by this batch:

```powershell
$secure = Read-Host "HBI bearer access token" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:HBI_ACCESS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    python scripts/bulk_product_intake.py --input .\products.csv --base-url http://127.0.0.1:8000 --resume --reconcile --checkpoint .\bulk-intake.checkpoint.json
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Item Env:HBI_ACCESS_TOKEN -ErrorAction SilentlyContinue
    $secure.Dispose()
}
```

Inspect the checkpoint's `reconciliation` candidates against the audit and Product Master. Ambiguous or missing evidence remains unresolved. Once the uncertain row has been reviewed, `--apply --resume` can continue with other READY rows, but it will never resend the UNKNOWN row. If an operator separately confirms that no Product was created, a new checkpoint may be started only after that disposition is documented and the source is revalidated.

## Possible matches and operator decisions

Rows classified \`POSSIBLE_MATCH_REVIEW\` are not created. Review the stored candidate Product IDs and duplicate-check audit ID. Only after an operator has explicitly decided that the incoming identity is a distinct new Product may a decision file be supplied:

\`\`\`json
{
  "sku-17": {
    "decision": "NEW",
    "reason": "Operator reviewed the candidate and confirmed a distinct product identity"
  }
}
\`\`\`

Save it as a local JSON file and resume with \`--decision-file .\\decisions.json\`. The decision is recorded against the exact duplicate-check audit and the backend verifies that its identity snapshot matches the create payload. \`EXISTING\` requires \`selected_product_id\`; \`RENAME\` requires \`final_product_name\`. Those decisions are recorded and the batch row is skipped; the tool does not create from them. If identity changes, correct the source file and start a new batch/checkpoint.

## Interrupted or uncertain requests

Any process interruption while a request is in flight, transport failure, or server error that may have occurred after commit is marked \`UNKNOWN_OUTCOME\`. Resume never resends that row. Reconcile it read-only against the duplicate-check audit and Product Master before making a separate operator decision. Do not delete or edit the checkpoint to force a retry. If the outcome remains ambiguous, leave it blocked.

## State meanings

- \`CREATED\`: API returned 201 with the generated Product ID.
- \`EXISTING\`: duplicate preflight found an exact existing Product; no create request was sent.
- \`POSSIBLE_MATCH_REVIEW\`: human review and a snapshot-bound decision are required.
- \`HUMAN_RESOLVED_SKIP\`: operator selected EXISTING or RENAME; no Product was created by this batch.
- \`PREFLIGHT_FAILED\` / \`CREATE_REJECTED\`: API rejected the request; inspect the saved response before taking any further action.
- \`UNKNOWN_OUTCOME\`: request outcome cannot be established safely; no automatic retry.

## Governance boundary

Each Product Create is an independent API transaction, not one all-or-nothing batch transaction. Successful rows remain committed if a later row fails. New Product records remain in the backend's initial DRAFT / PENDING / NEEDS_REVIEW state and receive only the existing zero-quantity Inventory anchor. This utility does not import Evidence, approve QA, verify identity, activate products, refresh ProductKnowledge, alter prices, receive stock, or change inventory quantities.

Do not use it against a live or production target until that exact target and the source file have been separately approved by the Product Owner.
