#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
git apply docs/homepage/logout-only.patch
echo "Applied: admin logout button removed from NewHomePage.tsx"
