from pathlib import Path
import os
import pytest

from app.hair_color.case_store import HairColorCaseStore
from scripts.hair_color_case_backup import main


def test_backup_cli_creates_verified_backup_and_rotates_old_files(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "synthetic.sqlite"
    store = HairColorCaseStore(db_path)
    store.create_case(
        case_ref="SYNTHETIC-CLI-CASE",
        event_id="SYNTHETIC-CLI-CREATE",
        intake={"goal": "SYNTHETIC: placeholder"},
    )
    monkeypatch.setenv("HBI_HAIR_COLOR_CASE_DB", str(db_path))
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir(mode=0o700)
    for i in range(3):
        old = backup_dir / f"hair-color-case-old-{i}.sqlite"
        old.write_text("old")
        os.utime(old, (100 + i, 100 + i))

    monkeypatch.setattr("sys.argv", ["backup-cli", "--backup-dir", str(backup_dir), "--retain", "2"])
    assert main() == 0
    files = sorted(backup_dir.glob("hair-color-case-*.sqlite"))
    assert len(files) == 2
    newest = next(f for f in files if f.name.startswith("hair-color-case-20"))
    restored = HairColorCaseStore.restore_from_backup(newest, tmp_path / "restore" / "recovered.sqlite")
    assert HairColorCaseStore(restored).integrity_check() == "ok"
    assert "Verified synthetic case-store backup" in capsys.readouterr().out


def test_backup_cli_requires_configured_database(monkeypatch, tmp_path):
    monkeypatch.delenv("HBI_HAIR_COLOR_CASE_DB", raising=False)
    monkeypatch.setattr("sys.argv", ["backup-cli", "--backup-dir", str(tmp_path / "backup")])
    with pytest.raises(SystemExit):
        main()
