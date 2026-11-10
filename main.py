import argparse
import sys
from pathlib import Path


Board = tuple[tuple[str, ...], ...]
WINNING_LINES = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


class BoardError(ValueError):
    """Raised when a board's format or game state is invalid."""


def parse_board(text: str) -> Board:
    if text.endswith("\n"):
        text = text[:-1]

    rows = text.split("\n")
    if len(rows) != 3:
        raise BoardError("board must contain exactly three rows")

    board_rows = []
    for row_number, row in enumerate(rows, start=1):
        cells = row.split(" ")
        if len(cells) != 3 or any(cell not in {".", "X", "O"} for cell in cells):
            raise BoardError(
                f"row {row_number} must contain three cells separated by one space"
            )
        board_rows.append(tuple(cells))

    board = tuple(board_rows)
    validate_position(board)
    return board


def has_won(board: Board, mark: str) -> bool:
    return any(
        all(board[row][column] == mark for row, column in line)
        for line in WINNING_LINES
    )


def game_state(board: Board) -> str:
    if has_won(board, "X"):
        return "X wins"
    if has_won(board, "O"):
        return "O wins"
    if all(cell != "." for row in board for cell in row):
        return "draw"
    return "play continues"


def validate_position(board: Board) -> None:
    x_count = sum(cell == "X" for row in board for cell in row)
    o_count = sum(cell == "O" for row in board for cell in row)
    if x_count not in {o_count, o_count + 1}:
        raise BoardError("board has an impossible number of X and O marks")

    x_wins = has_won(board, "X")
    o_wins = has_won(board, "O")
    if x_wins and o_wins:
        raise BoardError("both players cannot have winning lines")
    if x_wins and x_count != o_count + 1:
        raise BoardError("X can only win after an X move")
    if o_wins and x_count != o_count:
        raise BoardError("O can only win after an O move")

    winning_mark = "X" if x_wins else "O" if o_wins else None
    if winning_mark is not None:
        for row in range(3):
            for column in range(3):
                if board[row][column] != winning_mark:
                    continue
                previous = [list(cells) for cells in board]
                previous[row][column] = "."
                previous_board = tuple(tuple(cells) for cells in previous)
                if not has_won(previous_board, "X") and not has_won(
                    previous_board, "O"
                ):
                    return
        raise BoardError("winning position could only be reached after an earlier win")


def read_board(path: Path) -> Board:
    try:
        text = path.read_bytes().decode("utf-8")
    except OSError as error:
        raise BoardError(f"cannot read {path}: {error.strerror or error}") from error
    except UnicodeDecodeError as error:
        raise BoardError(f"{path} is not valid UTF-8 text") from error
    return parse_board(text)


def validate_move(before: Board, after: Board) -> tuple[str, int, int]:
    if game_state(before) != "play continues":
        raise BoardError("the before board is already a terminal position")

    changes = [
        (row, column)
        for row in range(3)
        for column in range(3)
        if before[row][column] != after[row][column]
    ]
    if len(changes) != 1:
        raise BoardError("boards must differ in exactly one cell")

    row, column = changes[0]
    if before[row][column] != ".":
        raise BoardError("a move must replace an empty cell")

    expected_mark = "X" if sum(cell == "X" for cells in before for cell in cells) == sum(
        cell == "O" for cells in before for cell in cells
    ) else "O"
    if after[row][column] != expected_mark:
        raise BoardError(f"the next move must be {expected_mark}")

    return expected_mark, row + 1, column + 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a tic-tac-toe move between two board files."
    )
    parser.add_argument("before", type=Path, help="path to the board before the move")
    parser.add_argument("after", type=Path, help="path to the proposed board")
    args = parser.parse_args(argv)

    try:
        before = read_board(args.before)
        after = read_board(args.after)
        mark, row, column = validate_move(before, after)
        print(f"Legal move: {mark} at row {row}, column {column}. {game_state(after)}.")
    except BoardError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
