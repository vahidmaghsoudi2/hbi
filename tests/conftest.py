"""HBI shared fixtures for Phase 2.

IMPORTANT:
- This file must not change existing Phase 1 test behavior.
- Add shared fixtures only when required by API tests.
"""

from pathlib import Path

import pytest


@pytest.fixture()
def project_root() -> Path:
    """Return HBI project root directory."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def hbi_db_path(project_root: Path) -> Path:
    """Return default HBI SQLite database path."""
    return project_root / "data" / "hbi.db"
