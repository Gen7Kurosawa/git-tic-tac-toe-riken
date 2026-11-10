import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "main.py"
EMPTY = ". . .\n. . .\n. . ."


def run_validator(tmp_path: Path, before: str | Path, after: str | Path):
    before_path = tmp_path / "before.txt"
    after_path = tmp_path / "after.txt"

    if isinstance(before, Path):
        before_path = before
    else:
        before_path.write_text(before, encoding="utf-8")

    if isinstance(after, Path):
        after_path = after
    else:
        after_path.write_text(after, encoding="utf-8")

    return subprocess.run(
        [sys.executable, str(CLI), str(before_path), str(after_path)],
        capture_output=True,
        text=True,
        check=False,
    )


def assert_rejected(result: subprocess.CompletedProcess[str]):
    assert result.returncode != 0
    assert result.stderr.strip()


def test_accepts_and_reports_first_x_move(tmp_path: Path):
    result = run_validator(tmp_path, EMPTY, "X . .\n. . .\n. . .")

    assert result.returncode == 0, result.stderr
    output = result.stdout.lower()
    assert "x" in output
    assert "row 1" in output
    assert "column 1" in output
    assert "continu" in output


def test_accepts_consecutive_legal_x_and_o_moves(tmp_path: Path):
    result = run_validator(
        tmp_path,
        "X . .\n. . .\n. . .",
        "X . .\n. O .\n. . .",
    )

    assert result.returncode == 0, result.stderr
    output = result.stdout.lower()
    assert "o" in output
    assert "row 2" in output
    assert "column 2" in output


def test_accepts_board_without_final_newline(tmp_path: Path):
    result = run_validator(tmp_path, EMPTY, "X . .\n. . .\n. . .")

    assert result.returncode == 0, result.stderr


def test_accepts_board_with_final_newline(tmp_path: Path):
    result = run_validator(tmp_path, EMPTY, "X . .\n. . .\n. . .\n")

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("before", "after", "case"),
    [
        (EMPTY, ". . .\n. O .\n. . .", "wrong player"),
        (EMPTY, EMPTY, "no change"),
        (EMPTY, "X O .\n. . .\n. . .", "two changed cells"),
        ("X . .\n. . .\n. . .", "O . .\n. . .\n. . .", "replace a mark"),
        ("X . .\n. . .\n. . .", ". . .\n. . .\n. . .", "remove a mark"),
    ],
)
def test_rejects_illegal_move(tmp_path: Path, before: str, after: str, case: str):
    result = run_validator(tmp_path, before, after)

    assert_rejected(result)


@pytest.mark.parametrize(
    "malformed",
    [
        ". . .\n. . .",  # Only two rows.
        ". . .\n. . .\n. . .\n. . .",  # Four rows.
        ". .\n. . .\n. . .",  # Too few cells.
        ". . . .\n. . .\n. . .",  # Too many cells.
        ". . .\n. . .\n. . Z",  # Invalid symbol.
        ".. . .\n. . .\n. . .",  # Invalid cell token.
        ".  . .\n. . .\n. . .",  # More than one space.
        ". . .\n. . .\n. . .\n\n",  # Extra blank row.
    ],
)
def test_rejects_malformed_board(tmp_path: Path, malformed: str):
    result = run_validator(tmp_path, malformed, EMPTY)

    assert_rejected(result)


@pytest.mark.parametrize(
    "invalid",
    [
        "O . .\n. . .\n. . .",  # O cannot move first.
        "X X .\n. . .\n. . .",  # X has moved twice before O.
        "X X X\nO O O\n. . .",  # Both players have winning lines.
        "X X X\nO O .\nO . .",  # O played after X had already won.
    ],
)
def test_rejects_impossible_board_state(tmp_path: Path, invalid: str):
    result = run_validator(tmp_path, EMPTY, invalid)

    assert_rejected(result)


def test_rejects_move_from_a_won_board(tmp_path: Path):
    before = "X X X\nO O .\n. . ."
    after = "X X X\nO O O\n. . ."

    result = run_validator(tmp_path, before, after)

    assert_rejected(result)


def test_rejects_move_from_a_drawn_board(tmp_path: Path):
    before = "X O X\nX O O\nO X X"
    after = "X O X\nX O O\nO X X"

    result = run_validator(tmp_path, before, after)

    assert_rejected(result)


def test_reports_winning_move(tmp_path: Path):
    before = "X X .\nO O .\n. . ."
    after = "X X X\nO O .\n. . ."

    result = run_validator(tmp_path, before, after)

    assert result.returncode == 0, result.stderr
    output = result.stdout.lower()
    assert "x" in output
    assert "win" in output


def test_reports_drawing_move(tmp_path: Path):
    before = "X O X\nX O O\nO X ."
    after = "X O X\nX O O\nO X X"

    result = run_validator(tmp_path, before, after)

    assert result.returncode == 0, result.stderr
    assert "draw" in result.stdout.lower()


@pytest.mark.parametrize("missing", ["before", "after"])
def test_reports_missing_input_file(tmp_path: Path, missing: str):
    before = tmp_path / "before.txt"
    after = tmp_path / "after.txt"
    before.write_text(EMPTY, encoding="utf-8")
    after.write_text("X . .\n. . .\n. . .", encoding="utf-8")
    (tmp_path / f"{missing}.txt").unlink()

    result = subprocess.run(
        [sys.executable, str(CLI), str(before), str(after)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert_rejected(result)


def test_reports_unreadable_input_path(tmp_path: Path):
    before = tmp_path / "before.txt"
    before.mkdir()
    after = tmp_path / "after.txt"
    after.write_text("X . .\n. . .\n. . .", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(CLI), str(before), str(after)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert_rejected(result)


def test_does_not_modify_input_files(tmp_path: Path):
    before = "X . .\n. . .\n. . ."
    after = "X . .\n. O .\n. . ."
    before_path = tmp_path / "before.txt"
    after_path = tmp_path / "after.txt"
    before_path.write_text(before, encoding="utf-8")
    after_path.write_text(after, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(CLI), str(before_path), str(after_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert before_path.read_text(encoding="utf-8") == before
    assert after_path.read_text(encoding="utf-8") == after
