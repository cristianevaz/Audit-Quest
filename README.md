# 🪶 Audit Quest (Streamlit)

Port em Python/Streamlit do jogo de auditoria originalmente feito em HTML/React.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar (Streamlit Community Cloud)

1. Suba esta pasta para um repositório no GitHub.
2. Em share.streamlit.io, clique em **New app**, escolha o repositório e use `app.py` como arquivo principal.
3. Pronto: o `requirements.txt` e o tema (`.streamlit/config.toml`) são lidos automaticamente.

## Estrutura

| Arquivo | O que tem |
|---|---|
| `app.py` | Interface (telas, tabuleiro, minigames) |
| `engine.py` | Regras do jogo, sem dependência de Streamlit |
| `game_data.py` | Tabuleiro, firmas, perguntas, eventos e cenários |
| `tests/test_engine.py` | Valida os dados e simula partidas completas |

## Adicionar perguntas

Em `game_data.py`, inclua uma linha `Q(...)` na categoria desejada. A resposta certa é sempre o
2º argumento; o jogo embaralha as alternativas.

```python
Q("Pergunta?", "Resposta certa", "Errada 1", "Errada 2", "Explicação", xp=20, cred=5, evidence="Opcional")
```

Depois rode `python tests/test_engine.py` para conferir que nada quebrou.
