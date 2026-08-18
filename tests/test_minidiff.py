"""minidiff CLI 端對端測試：以子行程執行，驗證重建性質、已知案例與 git diff 對照。"""

import random
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "minidiff.py"


def _run_diff(tmp_path, old_lines, new_lines):
    """寫入兩個檔案並執行 minidiff，回傳 (結束碼, [(標記, 行內容), ...])。"""
    old = tmp_path / "old.txt"
    new = tmp_path / "new.txt"
    old.write_text("\n".join(old_lines) + ("\n" if old_lines else ""),
                   encoding="utf-8", newline="\n")
    new.write_text("\n".join(new_lines) + ("\n" if new_lines else ""),
                   encoding="utf-8", newline="\n")

    result = subprocess.run(
        [sys.executable, str(TOOL), str(old), str(new)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode in (0, 1), result.stderr
    parsed = [(line[0], line[2:]) for line in result.stdout.splitlines()]
    return result.returncode, parsed


def test_reconstruction_property_random(tmp_path):
    # diff 的核心正確性：從輸出取「 」與「-」行可重建舊檔、取「 」與「+」行可重建新檔
    rng = random.Random(11)
    for _ in range(20):
        old = [rng.choice("abcde") for _ in range(rng.randint(0, 15))]
        new = [rng.choice("abcde") for _ in range(rng.randint(0, 15))]

        returncode, diff = _run_diff(tmp_path, old, new)

        assert [content for marker, content in diff if marker in " -"] == old
        assert [content for marker, content in diff if marker in " +"] == new
        assert returncode == (1 if any(m != " " for m, _ in diff) else 0)


def test_identical_files(tmp_path):
    lines = ["alpha", "bravo", "charlie"]
    returncode, diff = _run_diff(tmp_path, lines, lines)

    assert returncode == 0
    assert all(marker == " " for marker, _ in diff)


def test_known_case(tmp_path):
    returncode, diff = _run_diff(
        tmp_path, ["a", "b", "c", "d"], ["a", "x", "c", "y"]
    )

    assert returncode == 1
    assert diff == [
        (" ", "a"),
        ("-", "b"),
        ("+", "x"),
        (" ", "c"),
        ("-", "d"),
        ("+", "y"),
    ]


def test_matches_git_diff_on_unambiguous_case(tmp_path):
    # 與業界工具對照：無歧義的案例下，差異行應與 git diff --no-index 完全一致
    old = ["alpha", "bravo", "charlie", "delta"]
    new = ["alpha", "xray", "charlie", "yankee"]
    _, diff = _run_diff(tmp_path, old, new)
    ours = [(marker, content) for marker, content in diff if marker != " "]

    git = subprocess.run(
        ["git", "diff", "--no-index", "--unified=100",
         str(tmp_path / "old.txt"), str(tmp_path / "new.txt")],
        capture_output=True, text=True, encoding="utf-8",
    )
    theirs = []
    for line in git.stdout.splitlines():
        if line.startswith(("---", "+++", "@@", "diff ", "index ")):
            continue
        if line.startswith("-"):
            theirs.append(("-", line[1:]))
        elif line.startswith("+"):
            theirs.append(("+", line[1:]))

    assert ours == theirs
