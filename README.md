# ♟ Xadrez no Terminal

Bot de xadrez que joga com você no terminal, com tabuleiro em arte ASCII (ou
símbolos Unicode). Escrito em Python puro, nivelado para ser um adversário
divertido em vez de imparável.

```
    a  b  c  d  e  f  g  h
+------------------------+
8 | ♜  ♞  ♝  ♛  ♚  ♝  ♞  ♜ | 8
7 | ♟  ♟  ♟  ♟  ♟  ♟  ♟  ♟ | 7
6 | .  .  .  .  .  .  .  . | 6
5 | .  .  .  .  .  .  .  . | 5
4 | .  .  .  .  ♙  .  .  . | 4
3 | .  .  .  .  .  .  .  . | 3
2 | ♙  ♙  ♙  ♙  .  ♙  ♙  ♙ | 2
1 | ♖  ♘  ♗  ♕  ♔  ♗  ♘  ♖ | 1
+------------------------+
    a  b  c  d  e  f  g  h

  Vez de: negras   |   Você: brancas
  Motor: nível 2 — Casual (~700)
  Lances: 1. e4
```

## Como rodar

```bash
git clone https://github.com/SEU-USUARIO/xadrez-terminal.git
cd xadrez-terminal

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 main.py
```

Sem ativar venv manualmente:

```bash
.venv/bin/python main.py
```

## Uso

```bash
python3 main.py                  # você de brancas, bot ~700
python3 main.py --nivel 1000     # bot mais forte
python3 main.py --nivel 5        # o mais forte que ele sabe jogar
python3 main.py --cor preta      # bot abre de brancas
python3 main.py --ascii          # letras ASCII (P N B R Q K)
python3 main.py --seed 42        # partidas reproduzíveis
```

### Comandos durante o jogo

| Comando | O que faz |
|---|---|
| `e4`, `Nf3`, `O-O`, `e2e4` | joga o lance (SAN ou UCI) |
| `dica` | o motor sugere um lance para você |
| `desfazer` | desfaz seu lance e a resposta do bot |
| `nivel 700` | troca a força do bot em tempo real |
| `novo` | começa outra partida |
| `tabuleiro` | redesenha o tabuleiro |
| `ajuda` | lista os comandos |
| `sair` | encerra o jogo |

## Níveis

| Nível | Rating aprox. | Como joga |
|---|---|---|
| 1 | ~300 | lances aleatórios |
| 2 | ~700 | guloso (1 lance à frente) com 35% de vacilo |
| 3 | ~1000 | guloso |
| 4 | ~1300 | minimax 2 lances |
| 5 | ~1600 | minimax 3 lances |

> Rating de engine não é rating humano. Esses números são estimativas para você
> calibrar o desafio — ajuste o nível até ficar competitivo e divertido.

## Como funciona

- **`python-chess`** cuida das regras (roque, en passant, promoção, xeque-mate).
- **Avaliação**: material (peão 100, cavalo 320, bispo 330, torre 500, dama 900)
  mais um bônus por ocupar as casas centrais.
- **Busca**: negamax com poda alpha-beta e ordenação de lances (capturas
  primeiro), o que deixa a profundidade 3 rápida o suficiente para o terminal.
- **Nível**: combinação de profundidade + probabilidade de lance aleatório
  ("vacilo"), que é o que abaixa a força para a faixa de iniciante.

## Estrutura

```
.
├── main.py              # interface do terminal e loop do jogo
├── engine.py            # avaliação, busca e níveis
├── tests/test_engine.py # testes com unittest
├── requirements.txt
└── README.md
```

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## Próximos passos (ideias)

- [ ] Livro de aberturas simples para variar o começo das partidas
- [ ] Tabela de peças por posição (piece-square tables) para melhorar o nível 5
- [ ] Modo "análise": mostrar a avaliação depois de cada lance
- [ ] Salvar e carregar partidas em PGN

## Licença

MIT — veja [LICENSE](LICENSE).
