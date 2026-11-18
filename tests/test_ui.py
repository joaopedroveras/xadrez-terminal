import unittest

import chess

from boardview import captured_pieces, render


class TestRender(unittest.TestCase):
    def test_posicao_inicial_tem_32_pecas(self):
        board = chess.Board()
        text = render(board, color=False)
        total = sum(text.count(glyph) for glyph in "♙♘♗♖♕♔♟♞♝♜♛♚")
        self.assertEqual(total, 32)

    def test_tabuleiro_tem_oito_linhas_de_casas(self):
        board = chess.Board()
        text = render(board, color=False)
        board_rows = [line for line in text.splitlines() if "│" in line]
        self.assertEqual(len(board_rows), 8)
        for row in board_rows:
            self.assertEqual(row.count("│"), 9)

    def test_peca_aparece_na_casa_certa(self):
        board = chess.Board()
        board.push_san("e4")
        text = render(board, color=False)
        row4 = next(line for line in text.splitlines() if line.startswith("4 "))
        # e4 é a quinta casa da linha
        cells = row4.split("│")[1:-1]
        self.assertIn("♙", cells[4])
        self.assertIn("·", cells[3])

    def test_modo_ascii_nao_usa_unicode(self):
        board = chess.Board()
        text = render(board, color=False, ascii_mode=True)
        self.assertIn("P", text)
        self.assertIn("k", text)
        self.assertNotIn("♙", text)

    def test_destaque_de_ultima_jogada_usa_cor(self):
        board = chess.Board()
        board.push_san("e4")
        text = render(board, color=True, last_move=board.peek())
        # e2 e e4 são casas claras: o destaque usa o tom de casa clara.
        self.assertIn("\x1b[48;5;222m", text)

    def test_destaque_em_casa_escura(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        text = render(board, color=True, last_move=board.peek())
        # e7 e e5 são casas escuras.
        self.assertIn("\x1b[48;5;71m", text)

    def test_sem_cor_nao_emite_ansi(self):
        board = chess.Board()
        text = render(board, color=False)
        self.assertNotIn("\x1b[", text)

    def test_letras_das_colunas_alinhadas_com_as_casas(self):
        board = chess.Board()
        lines = render(board, color=False, ascii_mode=True).splitlines()
        label = lines[0]
        # Cada casa avança 4 caracteres: a letra deve cair no centro de cada uma.
        for index, name in enumerate("abcdefgh"):
            self.assertEqual(label.index(name), 4 + 4 * index)
        self.assertEqual(label, lines[-1])

    def test_tabuleiro_invertido(self):
        board = chess.Board()
        text = render(board, color=False, flipped=True)
        first_row = next(line for line in text.splitlines() if "│" in line)
        self.assertTrue(first_row.startswith("1 "))
        self.assertIn("♖", first_row)


class TestCapturadas(unittest.TestCase):
    def test_sem_capturas_no_inicio(self):
        board = chess.Board()
        white_lost, black_lost = captured_pieces(board)
        self.assertEqual(white_lost, "")
        self.assertEqual(black_lost, "")

    def test_peao_capturado_aparece_na_lista(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("d5")
        board.push_san("exd5")
        white_lost, black_lost = captured_pieces(board)
        self.assertEqual(black_lost, "♟")
        self.assertEqual(white_lost, "")


class TestRegressaoBispoA3(unittest.TestCase):
    """Caso reportado: parecia que um peão 'virava bispo', mas era captura legal."""

    def test_captura_na_diagonal_longa_e_legal(self):
        board = chess.Board()
        for san in ("e4", "b6", "Bc4", "e5", "Nf3", "Ba6",
                    "O-O", "b5", "Bb3", "h5", "a3", "Bxa3"):
            board.push_san(san)
        self.assertTrue(board.is_valid())
        # Foi o bispo de f8, e não o de a6, que capturou em a3.
        self.assertEqual(board.piece_at(chess.A3), chess.Piece(chess.BISHOP, chess.BLACK))
        self.assertEqual(board.piece_at(chess.A6), chess.Piece(chess.BISHOP, chess.BLACK))


if __name__ == "__main__":
    unittest.main()
