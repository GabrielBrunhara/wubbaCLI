```
██████╗ ██╗ ██████╗██╗  ██╗    ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
██╔══██╗██║██╔════╝██║ ██╔╝    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║
██████╔╝██║██║     █████╔╝        ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
██╔══██╗██║██║     ██╔═██╗        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
██║  ██║██║╚██████╗██║  ██╗       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
```

<div align="center">

**A terminal application that makes people say _"Caralho... isso foi feito em Python?"_**

[![Python](https://img.shields.io/badge/Python-3.10%2B-00ff41?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Rich](https://img.shields.io/badge/Rich-13.7%2B-00ff41?style=flat-square)](https://github.com/Textualize/rich)
[![Rick and Morty API](https://img.shields.io/badge/API-Rick%20%26%20Morty-00ff41?style=flat-square)](https://rickandmortyapi.com)
[![License](https://img.shields.io/badge/License-MIT-00ff41?style=flat-square)](LICENSE)

*Retrô dos anos 80 · Fallout · Matrix · DOS — tudo ao mesmo tempo*

</div>

---

## O que é isso

Rick Terminal é um programa de terminal completo, construído em cima da [Rick and Morty API](https://rickandmortyapi.com), com uma interface TUI premium usando Rich.

Não é um script. É um software.

Boot screen animado. Menu navegável. Arte ASCII gerada em tempo real. Jogos. Favoritos. Histórico. Exportação. Efeitos de matrix. Cache local. Easter eggs. Tudo funcionando, tudo integrado, tudo em Python puro.

---

## Instalação

```bash
git clone https://github.com/seu-usuario/rick-terminal
cd rick-terminal

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

> Requer Python 3.10+ e conexão com a internet para buscar personagens.

---

## Como usar

```bash
# Modo completo (boot screen + menu interativo)
python main.py

# Modo clássico — comportamento original: nome + arte ASCII, sem interface
python main.py --classic

# Sem animações (mais rápido, útil em ambientes CI ou terminais lentos)
python main.py --no-effects

# Pular o boot screen e ir direto ao menu
python main.py --no-boot
```

---

## Menu

Ao iniciar, você verá uma tela de boot com barra de progresso e log de inicialização. Depois, o menu principal:

```
╭───────────────────────────   ⚡  MAIN MENU  ⚡   ────────────────────────────╮
│                                                                              │
│    A   Classic Random         Random character in pure ASCII glory           │
│    B   Character Viewer       Browse any character with full details         │
│    C   Guess Who              Identify the character from their ASCII art    │
│    D   Alive or Dead          Is this character still breathing?             │
│    E   Species Roulette       Guess the species of a random character        │
│    F   Episode Counter        How many episodes did they appear in?          │
│    G   Search Character       Find a character by name                       │
│    H   Random Episode         Explore a random episode of the show           │
│    I   Character Stats        Deep-dive statistics for any character         │
│    J   Favorites              Your bookmarked characters                     │
│    K   History                Recently viewed characters                     │
│    L   Export ASCII           Save ASCII art to TXT or HTML                  │
│    M   Settings               Configure appearance and behavior              │
│    N   Matrix Mode            Enter the Matrix… then meet a character        │
│    O   Surprise Me            Let the universe decide                        │
│    X   Exit                   Wubba lubba dub dub                            │
│                                                                              │
╰─────────────────────── Type a letter and press Enter ────────────────────────╯
```

---

## Funcionalidades

### 🎨 Character Viewer
Exibe personagem com arte ASCII à esquerda e painel de informações à direita. Suporta:
- `F` para favoritar/desfavoritar
- `E` para exportar (TXT ou HTML)
- `S` para ver estatísticas completas

### 🔍 Search
Busca por nome. Se houver apenas um resultado, abre diretamente. Se houver vários, exibe uma tabela numerada com status e contagem de episódios.

### 🎮 Jogos

| Jogo | Como funciona |
|---|---|
| **Guess Who** | Vê a arte ASCII, escolhe o nome entre 4 opções |
| **Alive or Dead** | Vê nome e dados, adivinha o status |
| **Species Roulette** | Vê o personagem, adivinha a espécie |
| **Episode Counter** | Adivinha quantos episódios o personagem apareceu |
| **Surprise Me** | O universo escolhe um dos jogos por você |

Todos os jogos têm pontuação persistida em `scores.json`.

### 📺 Random Episode
Sorteia um episódio, exibe código, data e todos os personagens. Você pode abrir qualquer personagem da lista diretamente.

### ⭐ Favoritos e Histórico
- **Favoritos**: persistidos em `favorites.json`, acessíveis a qualquer momento
- **Histórico**: últimos 50 personagens visualizados, persistidos em `history.json`, ordenados do mais recente

### 📤 Exportação
Exporte qualquer arte ASCII para:
- **TXT** — arquivo de texto simples com metadados do personagem
- **HTML** — página completa, self-contained, com fundo escuro e fonte monoespaçada

Arquivos salvos em `exports/`.

### 💾 Cache
Imagens são baixadas uma única vez e armazenadas em `ascii_cache/`. O cache pode ser limpo pelo menu de Settings.

### ⚙️ Settings
Configure tudo pelo menu `M`:

| Opção | Valores disponíveis |
|---|---|
| ASCII Width | 40 – 300 |
| Charset | `detailed` `simple` `blocks` `binary` `dense` `matrix` `braille` |
| Color Theme | `green` `cyan` `amber` `red` `purple` `white` `blue` |
| Figlet Font | `colossal` `doom` `epic` `slant` `big` `block` `digital` e outros |
| Effects | ON / OFF |
| Typing Speed | 0 – 0.2s por caractere |

As configurações são salvas em `config.json`.

### 🌧️ Matrix Mode
Chuva de caracteres em estilo Matrix toma a tela inteira. Depois, transição de portal. Depois, um personagem aleatório revelado linha por linha.

---

## Easter Eggs

Digite qualquer um dos termos abaixo diretamente no prompt do menu:

```
pickle rick
wubba lubba dub dub
portal
get schwifty
szechuan
rickroll
```

Há outros. Boa sorte.

---

## Estrutura do Projeto

```
rick-terminal/
│
├── main.py          # Entry point, flags de CLI
├── menu.py          # Loop principal e dispatch de modos
│
├── api.py           # Cliente da Rick and Morty API
├── ascii_engine.py  # Pipeline de conversão imagem → ASCII
├── cache.py         # Cache local de imagens (nunca baixa duas vezes)
│
├── effects.py       # Boot screen, matrix rain, typewriter, portal
├── ui.py            # Todos os painéis e prompts Rich
├── export.py        # Exportação para TXT e HTML
│
├── settings.py      # Configurações tipadas com persistência
├── favorites.py     # Gerenciador de favoritos
├── history.py       # Histórico de visualizações
├── games.py         # Todos os mini-jogos e score tracker
├── utils.py         # Constantes de caminhos e helpers de OS
│
├── config.json      # Preferências do usuário
├── requirements.txt
│
├── ascii_cache/     # Cache de imagens (gerado automaticamente)
└── exports/         # Arquivos exportados (gerado automaticamente)
```

---

## Dependências

```
requests    — HTTP client
Pillow      — Processamento de imagens
rich        — Interface TUI
pyfiglet    — Arte ASCII de texto
colorama    — Compatibilidade de cores cross-platform
readchar    — Leitura de input de caractere único
```

---

## Charsets disponíveis

```
detailed  →  @%#W$9876543210?!abc;:+=-,._ 
simple    →  @#*+=-:. 
blocks    →  █▓▒░ 
binary    →  10 
dense     →  MWNXK0Okxdolc:;,. 
matrix    →  ﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ01 
braille   →  ⣿⣷⣯⣟⡿⢿⣻⣽⣾⡽⢻⡟⣛⡻⢛⡓⢓⡑⢑ 
```

---

## Origem

O projeto começou como um script de ~70 linhas que baixava a imagem de um personagem aleatório do Rick and Morty e a imprimia como arte ASCII no terminal.

```python
# rick_ascii.py — o código original que gerou tudo isso
def main():
    char = get_random_character()
    fig = Figlet(font="colossal")
    print(fig.renderText(char["name"]))
    print(image_to_ascii(char["image"], width=WIDTH))
```

O `rick_ascii.py` original ainda está no repositório. O modo `--classic` preserva exatamente esse comportamento.

---

## Licença

MIT — faça o que quiser, só não destrua dimensões alternativas no processo.

---

<div align="center">

*"Nobody exists on purpose. Nobody belongs anywhere. Everybody's gonna die. Come watch TV."*

**— Morty Smith**

</div>
