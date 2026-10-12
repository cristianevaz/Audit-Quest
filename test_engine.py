"""Rode com `python -m pytest tests` (ou `python tests/test_engine.py`).

Valida os dados do jogo (útil ao adicionar perguntas) e simula partidas completas.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import engine as E
from game_data import AUDIT_QUESTIONS, BOARD_CELLS, CRC_QUESTIONS, FIRMS


def _all_questions():
    for cat, qs in AUDIT_QUESTIONS.items():
        for q in qs:
            yield cat, q
    for q in CRC_QUESTIONS:
        yield "crc", q


def test_question_data():
    for cat, q in _all_questions():
        assert len(q["options"]) == 3 and len(set(q["options"])) == 3, (cat, q["question"])
        assert q["explanation"].strip(), (cat, q["question"])


def test_board_references():
    for cell in BOARD_CELLS:
        if cell["type"] == "question":
            assert cell["category"] in AUDIT_QUESTIONS, cell["name"]
        if cell["type"] == "training":
            assert len(AUDIT_QUESTIONS[cell["courseKey"]]) >= 3, cell["name"]
    assert BOARD_CELLS[0]["type"] == "start" and BOARD_CELLS[-1]["type"] == "goal"


def test_shuffle_keeps_correct_answer():
    for cat, q in _all_questions():
        for _ in range(5):
            p = E.prepare_question(q, cat)
            assert p["options"][p["correct"]] == q["options"][0]


def _play(seed):
    random.seed(seed)
    g = E.new_game("T", list(FIRMS)[seed % 4], ["Fácil", "Normal", "Difícil"][seed % 3], 30)
    for _ in range(5000):
        if g["over"]:
            return g
        pd = g["pending"]
        if pd is None:
            E.player_roll(g)
            continue
        k = pd["kind"]
        if k == "message":
            E.continue_turn(g)
        elif k == "question":
            E.answer_question(g, random.randrange(3)) if pd["chosen"] is None else E.continue_turn(g)
        elif k == "choice":
            E.choose_option(g, 0) if pd["chosen"] is None else E.continue_turn(g)
        elif k == "offer":
            E.accept_training(g) if pd["can_afford"] else E.skip_training(g)
        elif k == "quiz":
            if pd["done"]:
                E.continue_turn(g)
            elif pd["chosen"] is None:
                E.answer_quiz(g, random.randrange(3))
            else:
                E.next_quiz(g)
        elif k == "inventory":
            E.submit_inventory(g, [0] * len(pd["items"])) if pd["result"] is None else E.continue_turn(g)
        elif k == "walkthrough":
            if pd["result"] is not None:
                E.continue_turn(g)
            elif pd["available"]:
                E.walk_add(g, pd["available"][0])
            else:
                E.walk_check(g)
    raise AssertionError("jogo não terminou")


def test_full_games():
    for seed in range(300):
        g = _play(seed)
        assert g["winner"] in ("player", "npc", "none")
        for a in (g["player"], g["npc"]):
            assert a["xp"] >= 0 and a["credibility"] >= 0 and a["credits"] >= 0
        assert E.build_report(g)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
