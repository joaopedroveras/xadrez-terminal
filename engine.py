"""Motor de xadrez simples.

Avaliação por material + centralização, busca minimax com poda alpha-beta.
A força é controlada por dois parâmetros: profundidade da busca e a
probabilidade de "vacilo" (jogar um lance aleatório de propósito).

Níveis aproximados (rating humano):
    1  ~300    aleatório
    2  ~700    guloso com vacilos (nível padrão)
    3  ~1000   guloso
    4  ~1300   minimax 2 lances
    5  ~1600   minimax 3 lances
"""

from __future__ import annotations

import random

import chess

INF = 10**9

PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Bônus por ocupar o centro do tabuleiro.
CENTER_BONUS = {
    chess.PAWN: 6,
    chess.KNIGHT: 18,
    chess.BISHOP: 12,
    chess.ROOK: 2,
    chess.QUEEN: 4,
    chess.KING: 0,
}

CENTER_SQUARES = {
    chess.D4, chess.E4, chess.D5, chess.E5,
    chess.C4, chess.F4, chess.C5, chess.F5,
}

LEVELS = {
    1: {"label": "Aleatório", "rating": "~300", "depth": 1, "blunder": 0.85},
    2: {"label": "Casual", "rating": "~700", "depth": 1, "blunder": 0.35},
    3: {"label": "Intermediário", "rating": "~1000", "depth": 1, "blunder": 0.08},
    4: {"label": "Avançado", "rating": "~1300", "depth": 2, "blunder": 0.02},
    5: {"label": "Difícil", "rating": "~1600", "depth": 3, "blunder": 0.0},
}


def evaluate(board: chess.Board) -> int:
    """Avaliação em centipeões, do ponto de vista das brancas."""
    if board.is_checkmate():
        return -100_000 if board.turn == chess.WHITE else 100_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUE[piece.piece_type]
        if square in CENTER_SQUARES:
            value += CENTER_BONUS[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    return score


def material_balance(board: chess.Board) -> int:
    """Saldo de material em centipeões (positivo = brancas na frente)."""
    balance = 0
    for piece in board.piece_map().values():
        value = PIECE_VALUE[piece.piece_type]
        balance += value if piece.color == chess.WHITE else -value
    return balance


def _move_order_key(board: chess.Board, move: chess.Move) -> int:
    """Ordena lances: capturas valiosas primeiro (melhora a poda)."""
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        victim_value = PIECE_VALUE[victim.piece_type] if victim else PIECE_VALUE[chess.PAWN]
        attacker_value = PIECE_VALUE[attacker.piece_type] if attacker else 0
        return -(victim_value * 10 - attacker_value)
    if move.promotion:
        return -PIECE_VALUE[move.promotion]
    return 0


def _ordered_moves(board: chess.Board) -> list[chess.Move]:
    return sorted(board.legal_moves, key=lambda m: _move_order_key(board, m))


def _search(board: chess.Board, depth: int, alpha: int, beta: int) -> int:
    """Negamax: devolve a avaliação do ponto de vista de quem joga."""
    if depth == 0 or board.is_game_over():
        value = evaluate(board)
        return value if board.turn == chess.WHITE else -value

    best = -INF
    for move in _ordered_moves(board):
        board.push(move)
        score = -_search(board, depth - 1, -beta, -alpha)
        board.pop()

        if score > best:
            best = score
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def choose_move(
    board: chess.Board,
    level: int = 2,
    rng: random.Random | None = None,
) -> chess.Move | None:
    """Escolhe um lance para o jogador da vez. None se não houver lance."""
    rng = rng or random
    moves = list(board.legal_moves)
    if not moves:
        return None

    config = LEVELS[level]

    # Vacilo proposital: joga qualquer coisa.
    if rng.random() < config["blunder"]:
        return rng.choice(moves)

    best_score = -INF
    best_moves: list[chess.Move] = []

    for move in _ordered_moves(board):
        board.push(move)
        score = -_search(board, config["depth"] - 1, -INF, INF)
        board.pop()

        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    # Empate na avaliação: sorteia para não repetir a mesma partida.
    return rng.choice(best_moves)


def hint(board: chess.Board) -> chess.Move | None:
    """Sugestão de lance: mesma busca do nível 4, sem vacilos."""
    return choose_move(board, level=4, rng=random.Random())


def resolve_level(value: str) -> int:
    """Aceita 1-5 ou um rating aproximado (ex.: '700')."""
    value = str(value).strip().lower()
    aliases = {"facil": 1, "fácil": 1, "casual": 2, "medio": 3,
               "médio": 3, "dificil": 5, "difícil": 5}
    if value in aliases:
        return aliases[value]

    try:
        number = int(value)
    except ValueError:
        raise SystemExit(f"Nível inválido: {value!r}. Use 1-5 ou um rating (ex.: 700).")

    if 1 <= number <= 5:
        return number

    # Mapeia rating aproximado para o nível mais próximo.
    ratings = {1: 300, 2: 700, 3: 1000, 4: 1300, 5: 1600}
    return min(ratings, key=lambda lvl: abs(ratings[lvl] - number))


def describe_level(level: int) -> str:
    config = LEVELS[level]
    return f"nível {level} — {config['label']} ({config['rating']})"
