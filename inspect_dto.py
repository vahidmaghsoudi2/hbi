import re
from pathlib import Path

P = Path("E:/HBI")
conftest = P / "tests" / "conftest.py"

if conftest.exists():
    txt = conftest.read_text(encoding="utf-8")
    print("=== conftest.py (first 3000 chars) ===")
    print(txt[:3000])
else:
    print("conftest.py not found")
    # Try to find fixtures in test_interface.py
    ti = P / "tests" / "test_interface.py"
    if ti.exists():
        txt = ti.read_text(encoding="utf-8")
        # Find @pytest.fixture definitions
        fixtures = re.findall(r'@pytest\.fixture.*?\ndef \w+\(.*?\):\n(?:    .*\n)*', txt, re.MULTILINE)
        print("=== Fixtures found in test_interface.py ===")
        for f in fixtures[:5]:
            print(f[:500])
            print("---")