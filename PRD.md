# Product Requirements Document: Tic-Tac-Toe Move Validator

**Status:** Draft  
**Version:** 1.0  
**Date:** 2026-11-10

## 1. Overview

Build a command-line program that checks whether a tic-tac-toe board is valid
and whether a move from one board to another follows the rules. The program
reads two board files and reports the move and resulting game state. It does
not modify either file.

## 2. Problem

People playing through the shared Git repository edit `BOARD.txt` by hand.
It is easy to enter a malformed board, play the wrong mark, or make more than
one move before committing. Players need a quick, repeatable way to verify a
proposed move before sharing it.

## 3. Goals

- Validate the text format and legal state of each board.
- Confirm that the second board is exactly one legal move after the first.
- Explain the move and whether the game continues, ends in a draw, or has a
  winner.
- Return a non-zero exit status and a clear error for invalid input so the
  command can be used in scripts.

## 4. Users

Players who take turns editing and reviewing `BOARD.txt` in a shared Git
repository. They may be beginners and should not need to understand game
internals to interpret an error.

## 5. User stories

- As a player, I want to compare my partner's previous board with the proposed
  board so I can confirm that exactly one legal move was made.
- As a player, I want an error to identify why a board or move is invalid so
  we can correct it.
- As a player, I want to know the move and resulting game state when a move is
  valid.

## 6. Scope

### In scope

- A command-line invocation that takes paths to a before-board file and an
  after-board file.
- Strict parsing of the repository's `BOARD.txt` format:
  three rows, three cells per row, one space between cells, and only `.`, `X`,
  or `O` as cell values. A final newline is optional.
- Validation of legal turn counts (`X` starts; the number of X marks is equal
  to the number of O marks or one greater).
- Validation of game outcomes, including wins, draws, and unreachable
  terminal positions. A position where both players win, or where play
  continued after a win, is invalid.
- Comparison that requires the before-board to be a valid, non-terminal
  position and the after-board to be a valid position reached by exactly one
  move: one `.` becomes the mark whose turn it is, and every other cell stays
  unchanged.
- Human-readable success output that identifies the mark and cell played
  (using 1-based row and column numbers) and states whether play continues,
  the game is a draw, or a player won.
- Human-readable errors on standard error and a non-zero exit status for
  malformed, illegal, or unreadable input. Successful validation exits zero.

### Out of scope

- Choosing or making a move automatically.
- Playing a complete game automatically.
- Reading a board from an image or providing a graphical interface.
- Editing `BOARD.txt`, committing changes, or integrating with GitHub.
- Machine-readable output formats such as JSON.

## 7. Functional requirements

1. The user can run the program with exactly two file paths: the before board
   and the proposed after board.
2. The program rejects a board unless it has exactly three rows and each row
   has exactly three valid cells in the specified text format.
3. The program rejects boards with impossible mark counts or impossible game
   outcomes. In particular, both players cannot have winning lines, and a
   winning position must be reachable by a final winning move.
4. The before board must not already be a win or a draw.
5. The after board must differ from the before board in exactly one cell,
   changing an empty cell to the correct player's mark.
6. On success, the program reports the move and the after-board's game state.
   On failure, it explains the problem, writes the error to standard error,
   and exits non-zero.
7. Neither input file is modified.

## 8. Acceptance criteria

- An empty board followed by a board with X in row 1, column 1 is accepted and
  reported as a legal X move with the game continuing.
- A valid X move followed by a valid O move is accepted.
- A move by the wrong player is rejected.
- No change, two changed cells, replacing an existing mark, or removing a mark
  is rejected.
- A malformed board (wrong number of rows or cells, invalid symbol, or
  incorrect separators) is rejected.
- Impossible mark counts, a board where both players win, and a position that
  could only have been reached by continuing after a win are rejected.
- A legal winning move and a legal drawing move are accepted and reported with
  the correct outcome.
- A move after a win or draw is rejected.
- Missing or unreadable input files produce a clear error and a non-zero exit
  status.

## 9. TDD approach

Implement the requirements in small red-green-refactor cycles. Start with
tests for parsing and board validity, then tests for comparing a single move,
and finally tests for CLI output and exit statuses. Each acceptance criterion
should be represented by one or more automated tests before its implementation
is considered complete.

## 10. Open implementation decision

The programming language and test framework have not yet been selected. They
should be agreed on before implementation; this PRD intentionally specifies
behavior independently of a particular stack.
