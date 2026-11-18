import random
import unittest

import chess

from engine import (
    LEVELS,
    choose_move,
    describe_level,
    evaluate,
    material_balance,
    resolve_level,
)


class TestEvaluation(unittest.TestCase):
    def test_posicao_inicial_equilibrada(self):
        self.assertEqual(evaluate(chess.Board()), 0)

    def test_xeque_mate_e_pontuado(self):
        board = chess.Board()
        for san in ("f3", "e5", "g4", "Qh4#"):
            board.push_san(san)
        self.assertTrue(board.is_checkmate())
        # Brancas levaram mate: avaliação do ponto de vista delas é péssima.
        self.assertEqual(evaluate(board), -100_000)

    def test_saldo_de_material(self):
        board = chess.Board("7k/8/8/8/8/8/8/KQ6 w - - 0 1")
        self.assertEqual(material_balance(board), 900)


class TestBusca(unittest.TestCase):
    def test_todos_os_niveis_jogam_lance_legal(self):
        board = chess.Board()
        for level in LEVELS:
            with self.subTest(level=level):
                move = choose_move(board, level=level, rng=random.Random(0))
                self.assertIn(move, board.legal_moves)

    def test_sem_lances_quando_em_mate(self):
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        self.assertTrue(board.is_checkmate())
        self.assertIsNone(choose_move(board, level=4))

    def test_encontra_mate_em_um(self):
        board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 w - - 0 1")
        move = choose_move(board, level=4, rng=random.Random(0))
        board.push(move)
        self.assertTrue(board.is_checkmate(), f"esperava mate, jogou {move}")


class TestNiveis(unittest.TestCase):
    def test_resolve_por_numero_de_nivel(self):
        self.assertEqual(resolve_level("3"), 3)

    def test_resolve_por_rating(self):
        self.assertEqual(resolve_level("700"), 2)
        self.assertEqual(resolve_level("1600"), 5)

    def test_resolve_por_apelido(self):
        self.assertEqual(resolve_level("facil"), 1)

    def test_descricao_inclui_rating(self):
        self.assertIn("~700", describe_level(2))


if __name__ == "__main__":
    unittest.main()
