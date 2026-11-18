"""Desenho do tabuleiro no terminal.

Tabuleiro com casas alternadas, última jogada destacada, rei em xeque em
vermelho e lista de peças capturadas. Funciona com cores ANSI (256 cores) ou
em modo texto puro para terminais sem suporte.
"""

from __future__ import annotations

import os
import sys

import chess

UNICODE_GLYPHS = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}
ASCII_GLYPHS = {c: c for c in "PNBRQKpnbrqk"}

START_COUNTS = {
    chess.PAWN: 8,
    chess.KNIGHT: 2,
    chess.BISHOP: 2,
    chess.ROOK: 2,
    chess.QUEEN: 1,
    chess.KING: 1,
}

RESET = "\x1b[0m"


class Theme:
    """Paleta do tabuleiro. Com color=False, todos os códigos ficam vazios.

    A cor do texto é escolhida pela casa (contraste), não pela peça: peças
    brancas são vazadas e pretas são cheias, então o formato já distingue os
    lados mesmo em terminais de 256 cores.
    """

    def __init__(self, color: bool):
        if color:
            self.light_square = "\x1b[48;5;187m"
            self.dark_square = "\x1b[48;5;101m"
            self.on_light = "\x1b[38;5;16m"
            self.on_dark = "\x1b[38;5;231m"
            self.last_move_light = "\x1b[48;5;222m"
            self.last_move_dark = "\x1b[48;5;71m"
            self.check_square = "\x1b[48;5;160m"
            self.empty = "\x1b[38;5;243m"
            self.frame = "\x1b[38;5;245m"
            self.bold = "\x1b[1m"
            self.reset = RESET
        else:
            self.light_square = self.dark_square = ""
            self.on_light = self.on_dark = ""
            self.last_move_light = self.last_move_dark = ""
            self.check_square = ""
            self.empty = self.frame = self.bold = ""
            self.reset = ""


def should_use_color(no_color: bool = False) -> bool:
    """Cores só quando faz sentido: terminal interativo e sem NO_COLOR."""
    if no_color or os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _is_dark_square(square: int) -> bool:
    return (chess.square_file(square) + chess.square_rank(square)) % 2 == 0


def render(
    board: chess.Board,
    *,
    ascii_mode: bool = False,
    color: bool = True,
    flipped: bool = False,
    last_move: chess.Move | None = None,
) -> str:
    """Devolve o tabuleiro pronto para imprimir."""
    theme = Theme(color)
    glyphs = ASCII_GLYPHS if ascii_mode else UNICODE_GLYPHS
    empty = "." if ascii_mode else "·"

    if ascii_mode:
        top_left, top_tee, top_right = "+", "+", "+"
        bottom_left, bottom_tee, bottom_right = "+", "+", "+"
        left_tee, cross, right_tee = "+", "+", "+"
        horizontal, vertical = "-", "|"
    else:
        top_left, top_tee, top_right = "┌", "┬", "┐"
        bottom_left, bottom_tee, bottom_right = "└", "┴", "┘"
        left_tee, cross, right_tee = "├", "┼", "┤"
        horizontal, vertical = "─", "│"

    files = "abcdefgh" if not flipped else "hgfedcba"
    ranks = list(range(8, 0, -1))
    if flipped:
        ranks.reverse()

    highlighted = set()
    if last_move is not None:
        highlighted = {last_move.from_square, last_move.to_square}

    king_square = board.king(board.turn) if board.is_check() else None

    def cell(square: int) -> str:
        piece = board.piece_at(square)
        dark = _is_dark_square(square)

        if square == king_square:
            background = theme.check_square
        elif square in highlighted:
            background = theme.last_move_dark if dark else theme.last_move_light
        else:
            background = theme.dark_square if dark else theme.light_square

        if piece is None:
            return f"{background}{theme.empty} {empty} {theme.reset}"

        foreground = theme.on_dark if dark else theme.on_light
        if ascii_mode:
            foreground += theme.bold
        return f"{background}{foreground} {glyphs[piece.symbol()]} {theme.reset}"

    def border(left: str, middle: str, right: str) -> str:
        return theme.frame + left + (horizontal * 3 + middle) * 7 + horizontal * 3 + right + theme.reset

    columns = [chess.square(chess.FILE_NAMES.index(name), 0) for name in files]
    cell_width = 3

    label = " " * (2 + 1 + 1) + "".join(
        f"{name}{' ' * (cell_width - 1)}" for name in files
    )
    label = label.rstrip()

    def row(rank: int) -> list[str]:
        return [
            cell(chess.square(chess.square_file(square), rank - 1))
            for square in columns
        ]

    lines = [label, "  " + border(top_left, top_tee, top_right)]

    for index, rank in enumerate(ranks):
        lines.append(
            theme.frame + f"{rank:<2}" + vertical + theme.reset
            + vertical.join(row(rank))
            + theme.frame + vertical + theme.reset
        )
        if index < len(ranks) - 1:
            lines.append("  " + border(left_tee, cross, right_tee))

    lines.append("  " + border(bottom_left, bottom_tee, bottom_right))

    lines.append(label)

    return "\n".join(lines)


def captured_pieces(
    board: chess.Board, ascii_mode: bool = False
) -> tuple[str, str]:
    """Peças que saíram do tabuleiro: (brancas capturadas, negras capturadas)."""
    glyphs = ASCII_GLYPHS if ascii_mode else UNICODE_GLYPHS
    present: dict[chess.Color, dict[int, int]] = {chess.WHITE: {}, chess.BLACK: {}}
    for piece in board.piece_map().values():
        present[piece.color][piece.piece_type] = (
            present[piece.color].get(piece.piece_type, 0) + 1
        )

    result = []
    for color in (chess.WHITE, chess.BLACK):
        missing = []
        for piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP,
                           chess.KNIGHT, chess.PAWN):
            count = START_COUNTS[piece_type] - present[color].get(piece_type, 0)
            symbol = chess.Piece(piece_type, color).symbol()
            missing.append(glyphs[symbol] * count)
        result.append("".join(missing))

    return result[0], result[1]
