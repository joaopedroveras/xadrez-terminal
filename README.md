# ♟ Xadrez no Terminal

Bot de xadrez que joga com você no terminal, com tabuleiro em arte ASCII (ou
símbolos Unicode). Escrito em Python puro, nivelado para ser um adversário
divertido em vez de imparável.

```
    a  b  c  d  e  f  g  h
  +---+---+---+---+---+---+---+---+
8 | r | n | b | q | k | b | n | r |
  +---+---+---+---+---+---+---+---+
7 | p | p | p | p | p | p | p | p |
  +---+---+---+---+---+---+---+---+
6 | . | . | . | . | . | . | . | . |
  +---+---+---+---+---+---+---+---+
5 | . | . | . | . | . | . | . | . |
  +---+---+---+---+---+---+---+---+
4 | . | . | . | . | P | . | . | . |
  +---+---+---+---+---+---+---+---+
3 | . | . | . | . | . | . | . | . |
  +---+---+---+---+---+---+---+---+
2 | P | P | P | P | . | P | P | P |
  +---+---+---+---+---+---+---+---+
1 | R | N | B | Q | K | B | N | R |
  +---+---+---+---+---+---+---+---+
    a  b  c  d  e  f  g  h

  Vez de: negras   |   Você: brancas
  Motor: nível 2 — Casual (~700)
  Lances: 1. e4
```

Com cor, as casas alternam claro/escuro, a última jogada fica destacada em verde
e o rei em xeque fica vermelho. Peças maiúsculas são brancas, minúsculas pretas.

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
python3 main.py --unicode        # símbolos ♔♕♖ em vez de letras
python3 main.py --no-color       # sem cores
python3 main.py --seed 42        # partidas reproduzíveis
```

### Fontes e cores

O padrão usa **letras** (`K Q R B N P` e minúsculas) porque muitas fontes
monoespaçadas não têm os símbolos de xadrez. Quando faltam, o terminal busca em
outras fontes e o resultado desalinha — em especial o peão preto `♟`, que em
alguns sistemas é renderizado como emoji colorido de largura dupla.

Se a sua fonte tiver o bloco de xadrez completo (Nerd Fonts, DejaVu Sans Mono,
Noto Sans Mono completo), use `--unicode` para ver as peças de verdade:

```bash
python3 main.py --unicode
```

As cores são desligadas sozinhas quando a saída não é um terminal (ex.: pipe ou
arquivo) e quando a variável `NO_COLOR` está definida.

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
├── boardview.py         # desenho do tabuleiro (cores, destaque, capturadas)
├── engine.py            # avaliação, busca e níveis
├── tests/               # testes com unittest
│   ├── test_engine.py
│   └── test_ui.py
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
