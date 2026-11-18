#!/usr/bin/env python3
"""Xadrez no terminal: jogue contra um bot simples com tabuleiro em arte ASCII.

Uso:
    python3 main.py                 # bot nível ~700, você de brancas
    python3 main.py --nivel 1000    # bot mais forte
    python3 main.py --cor preta     # bot abre de brancas
    python3 main.py --unicode       # símbolos ♔♕♖ (precisa de fonte com suporte)
    python3 main.py --no-color      # sem cores ANSI
"""

from __future__ import annotations

import argparse
import random
import sys
import time

import chess

from boardview import captured_pieces, render, should_use_color
from engine import choose_move, describe_level, hint, material_balance, resolve_level

HELP = """
Comandos:
  <lance>     jogue em SAN (e4, Nf3, O-O) ou UCI (e2e4, e7e8q)
  dica        o motor sugere um lance
  desfazer    desfaz o seu último lance e a resposta do bot
  nivel N     troca a força do bot (1-5 ou rating, ex.: nivel 700)
  novo        começa outra partida
  tabuleiro   redesenha o tabuleiro
  ajuda       mostra esta ajuda
  sair        encerra o jogo
""".strip()


def move_log(board: chess.Board) -> str:
    moves = board.move_stack
    if not moves:
        return "(nenhum lance ainda)"
    replay = chess.Board()
    parts = []
    for i, move in enumerate(moves):
        san = replay.san(move)
        if i % 2 == 0:
            parts.append(f"{i // 2 + 1}. {san}")
        else:
            parts.append(san)
        replay.push(move)
    log = " ".join(parts)
    return log if len(log) <= 110 else "..." + log[-107:]


def show_position(
    board: chess.Board,
    ascii_mode: bool,
    human_color: chess.Color,
    level: int,
    color: bool,
) -> None:
    last_move = board.move_stack[-1] if board.move_stack else None

    print()
    print(render(board, ascii_mode=ascii_mode, color=color, last_move=last_move))
    print(
        f"  Vez de: {'brancas' if board.turn == chess.WHITE else 'negras'}"
        f"   |   Você: {'brancas' if human_color == chess.WHITE else 'negras'}"
    )
    print(f"  Motor: {describe_level(level)}")

    balance = material_balance(board)
    if balance:
        side = "brancas" if balance > 0 else "negras"
        print(f"  Material: {'+' if balance > 0 else '-'}{abs(balance) / 100:.1f} a favor das {side}")

    white_lost, black_lost = captured_pieces(board, ascii_mode)
    if white_lost or black_lost:
        print(f"  Capturadas: brancas {white_lost or '—'}  |  pretas {black_lost or '—'}")

    if board.is_check():
        print("  ⚠  XEQUE!")

    print(f"  Lances: {move_log(board)}")
    print()


def parse_move(board: chess.Board, text: str) -> chess.Move | None:
    text = text.strip()
    if not text:
        return None
    candidates = [text]
    if text.startswith("0-0"):
        candidates.append("O" + text[1:])

    for candidate in candidates:
        try:
            return board.parse_san(candidate)
        except ValueError:
            pass
        try:
            return board.parse_uci(candidate)
        except ValueError:
            pass
    return None


def announce_result(board: chess.Board, human_color: chess.Color) -> None:
    if board.is_checkmate():
        winner = "brancas" if board.turn == chess.BLACK else "negras"
        human_won = (winner == "brancas") == (human_color == chess.WHITE)
        print(f"  XEQUE-MATE das {winner} — {'VOCÊ GANHOU! 🎉' if human_won else 'o bot venceu. 💀'}")
    elif board.is_stalemate():
        print("  AFOGAMENTO — empate.")
    elif board.is_insufficient_material():
        print("  Material insuficiente — empate.")
    elif board.is_seventyfive_moves() or board.is_fivefold_repetition():
        print("  Empate por regra de repetição/limite de lances.")
    else:
        print("  Fim de jogo.")


def undo(board: chess.Board, human_color: chess.Color) -> None:
    if not board.move_stack:
        print("  Nada para desfazer.")
        return
    board.pop()
    while board.move_stack and board.turn != human_color:
        board.pop()


def play(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    level = resolve_level(args.nivel)
    human_color = chess.BLACK if args.cor.lower().startswith("p") else chess.WHITE
    ascii_mode = not args.unicode
    color = should_use_color(args.no_color)

    board = chess.Board()

    print()
    print("  ♟  XADREZ NO TERMINAL  ♟")
    print(f"  Você joga de {'brancas' if human_color == chess.WHITE else 'negras'}.")
    print(f"  Bot: {describe_level(level)}")
    print("  Digite 'ajuda' para ver os comandos.")
    print()

    while True:
        if board.is_game_over():
            show_position(board, ascii_mode, human_color, level, color)
            announce_result(board, human_color)
            print("  Digite 'novo' para jogar de novo ou 'sair'.")
            try:
                command = input("  > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n  Até a próxima!")
                return
            if command in {"novo", "new"}:
                board = chess.Board()
                continue
            if command in {"sair", "quit", "q", "exit"}:
                print("  Até a próxima!")
                return
            continue

        show_position(board, ascii_mode, human_color, level, color)

        if board.turn == human_color:
            try:
                raw = input("  Seu lance > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Até a próxima!")
                return

            command = raw.lower()

            if command in {"sair", "quit", "q", "exit"}:
                print("  Até a próxima!")
                return
            if command in {"ajuda", "help", "h", "?"}:
                print(HELP)
                continue
            if command in {"tabuleiro", "board"}:
                continue
            if command in {"novo", "new"}:
                board = chess.Board()
                continue
            if command in {"desfazer", "undo"}:
                undo(board, human_color)
                continue
            if command in {"dica", "hint"}:
                suggestion = hint(board)
                if suggestion:
                    print(f"  💡 Sugestão: {board.san(suggestion)}")
                continue
            if command.startswith("nivel") or command.startswith("nível"):
                parts = raw.split()
                if len(parts) > 1:
                    try:
                        level = resolve_level(parts[1])
                        print(f"  Motor ajustado para {describe_level(level)}.")
                    except SystemExit as exc:
                        print(f"  {exc}")
                else:
                    print(f"  Nível atual: {describe_level(level)}")
                continue

            move = parse_move(board, raw)
            if move is None:
                print("  ❌ Lance inválido. Tente SAN (Nf3) ou UCI (g1f3).")
                continue
            board.push(move)

        else:
            print("  Bot pensando...", end="\r", flush=True)
            started = time.perf_counter()
            move = choose_move(board, level=level, rng=rng)
            elapsed = time.perf_counter() - started
            if move is None:
                continue
            san = board.san(move)
            board.push(move)
            print(f"  🤖 Bot jogou: {san} ({elapsed:.2f}s)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Xadrez no terminal contra um bot simples em arte ASCII."
    )
    parser.add_argument("--nivel", default="2",
                        help="força do bot: 1-5 ou rating aproximado (padrão: 2 ≈ 700)")
    parser.add_argument("--cor", default="branca", choices=["branca", "preta"],
                        help="cor que você joga (padrão: branca)")
    parser.add_argument("--unicode", action="store_true",
                        help="usa símbolos de xadrez (♔♕♖) em vez de letras; "
                             "precisa de uma fonte monoespaçada com esses glifos")
    parser.add_argument("--no-color", action="store_true",
                        help="desliga as cores ANSI do tabuleiro")
    parser.add_argument("--seed", type=int, default=None,
                        help="semente aleatória (para partidas reproduzíveis)")
    args = parser.parse_args()

    try:
        play(args)
    except KeyboardInterrupt:
        print("\n  Até a próxima!")
        sys.exit(0)


if __name__ == "__main__":
    main()
