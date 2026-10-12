"""Regras do Audit Quest. Nenhuma dependência de Streamlit aqui.

O estado do jogo é um dict (`g`) guardado em st.session_state. Toda interação
do jogador fica em `g["pending"]`; a UI só desenha o que está pendente e chama
as funções deste módulo. `continue_turn` encerra a interação e passa a vez.
"""
import math
import random

from game_data import (
    AUDIT_QUESTIONS, BOARD_CELLS, CATEGORY_LABELS, CLIENT_SCENARIOS, COURSE_CONTENT,
    CRC_QUESTIONS, DIFFICULTY, FIRMS, GAME_EVENTS, HOURS_PER_ROLL, INVENTORY_ITEMS,
    LEVELS, MAX_HOURS, SABOTAGE_EVENTS, TRAVEL_EVENTS, WALKTHROUGH_GAMES,
)

LAST = len(BOARD_CELLS) - 1
NPC_NAME = "Zeca Urubu"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def senioridade(xp):
    """Retorna (cargo, xp do próximo nível ou None, progresso 0-100 dentro do nível)."""
    prev = 0
    for limit, title in LEVELS:
        if limit is None or xp < limit:
            progress = 100 if limit is None else (xp - prev) / (limit - prev) * 100
            return title, limit, max(0, min(100, progress))
        prev = limit
    return LEVELS[-1][1], None, 100


def fmt_delta(d):
    parts = []
    if d.get("xp"):
        parts.append(f"{d['xp']:+d} XP")
    if d.get("credibility"):
        parts.append(f"{d['credibility']:+d} cred.")
    if d.get("credits"):
        parts.append(f"{'+' if d['credits'] > 0 else '-'}C${abs(d['credits'])}")
    if d.get("hours"):
        parts.append(f"{d['hours']:+d}h")
    return ", ".join(parts)


def log(g, msg):
    g["log"].append({"msg": msg, "week": g["week"]})


def nlog(g, msg):
    """Log de ações do Zeca (também aparece no resumo da rodada)."""
    full = f"🤖 {msg}"
    log(g, full)
    g["feed"].append(full)


def flash(g, tone, text):
    g["flash"].append((tone, text))


def _set_pending(g, kind, **kw):
    g["uid"] += 1
    g["pending"] = {"kind": kind, "id": g["uid"], **kw}
    return g["pending"]


def show_message(g, title, text, tone="info"):
    _set_pending(g, "message", title=title, result={"tone": tone, "text": text})


# ---------------------------------------------------------------------------
# Criação do jogo
# ---------------------------------------------------------------------------
def _new_actor(name, firm):
    a = {
        "name": name, "position": 0, "credibility": 100, "xp": 0, "credits": 1000,
        "hours": MAX_HOURS, "firm": firm, "evidence": [], "courses": [], "learnings": [],
        "has_passed_crc": False, "skip_next": False, "correct": 0, "wrong": 0,
    }
    bonus = FIRMS[firm]["bonus"]
    if bonus["type"] == "credibility":
        a["credibility"] += bonus["value"]
    elif bonus["type"] == "credits":
        a["credits"] += bonus["value"]
    return a


def new_game(name, firm, difficulty="Normal", max_weeks=30):
    npc_firm = random.choice(list(FIRMS))
    g = {
        "player": _new_actor(name.strip() or "Pica-Pau", firm),
        "npc": _new_actor(NPC_NAME, npc_firm),
        "turn": "player", "week": 1, "busy": 0,
        "difficulty": difficulty, "max_weeks": max_weeks,
        "log": [], "feed": [], "flash": [], "pending": None,
        "over": False, "winner": None, "win_after": None,
        "dice": None, "uid": 0, "coffee": 0,
        "history": [], "stats": {}, "missed": [],
    }
    log(g, f"Você se juntou à {FIRMS[firm]['name']}!")
    nlog(g, f"{NPC_NAME} entrou na {FIRMS[npc_firm]['name']}.")
    g["feed"] = []
    _snapshot(g)
    return g


def _snapshot(g):
    p, n = g["player"], g["npc"]
    g["history"].append({
        "Semana": g["week"],
        f"{p['name']} (XP)": p["xp"], f"{p['name']} (Cred.)": p["credibility"],
        "Zeca (XP)": n["xp"], "Zeca (Cred.)": n["credibility"],
    })


# ---------------------------------------------------------------------------
# Efeitos
# ---------------------------------------------------------------------------
def apply_delta(g, who, xp=0, credibility=0, credits=0, hours=0, reducible=False):
    """Aplica variações com piso em zero. Retorna o que foi pedido após bônus de firma."""
    a = g[who]
    if credibility < 0 and reducible and a["firm"] == "amarela":
        credibility = -math.ceil(abs(credibility) * FIRMS["amarela"]["bonus"]["value"])
    a["xp"] = max(0, a["xp"] + xp)
    a["credibility"] = max(0, a["credibility"] + credibility)
    a["credits"] = max(0, a["credits"] + credits)
    a["hours"] = max(0, min(MAX_HOURS, a["hours"] + hours))
    return {"xp": xp, "credibility": credibility, "credits": credits, "hours": hours}


def apply_effect(g, who, effect, reducible=True):
    d = apply_delta(
        g, who, xp=effect.get("xp", 0), credibility=effect.get("credibility", 0),
        credits=effect.get("credits", 0), hours=effect.get("hours", 0), reducible=reducible,
    )
    if effect.get("evidence"):
        g[who]["evidence"].append(effect["evidence"])
    if effect.get("skip"):
        g[who]["skip_next"] = True
    return d


def _tone(d):
    pos = any(d.get(k, 0) > 0 for k in ("xp", "credibility"))
    neg = any(d.get(k, 0) < 0 for k in ("xp", "credibility"))
    if pos and not neg:
        return "success"
    if neg and not pos:
        return "error"
    return "info"


def _mult(g):
    return 2 if g["busy"] > 0 else 1


# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------
def prepare_question(base, category):
    """Embaralha as alternativas (a certa é sempre a primeira nos dados)."""
    opts = list(enumerate(base["options"]))
    random.shuffle(opts)
    correct = next(i for i, (orig, _) in enumerate(opts) if orig == 0)
    return {
        "question": base["question"], "options": [t for _, t in opts], "correct": correct,
        "explanation": base["explanation"], "reward": dict(base["reward"]), "category": category,
    }


def make_question(category):
    return prepare_question(random.choice(AUDIT_QUESTIONS[category]), category)


def record_answer(g, q, chosen):
    """Estatísticas do jogador (para a tela final)."""
    correct = chosen == q["correct"]
    s = g["stats"].setdefault(q["category"], {"correct": 0, "wrong": 0})
    s["correct" if correct else "wrong"] += 1
    g["player"]["correct" if correct else "wrong"] += 1
    if not correct:
        g["missed"].append({
            "category": CATEGORY_LABELS.get(q["category"], q["category"]),
            "question": q["question"], "chosen": q["options"][chosen] if chosen is not None else "-",
            "right": q["options"][q["correct"]], "explanation": q["explanation"],
        })


def grade_question(g, who, q, correct, sabotage=False):
    """Aplica recompensa ou penalidade. Retorna (texto, deltas)."""
    mult = 1 if sabotage else _mult(g)
    tag = " (em dobro: Busy Season!)" if mult == 2 else ""
    a = g[who]
    if correct:
        d = apply_delta(g, who, xp=q["reward"]["xp"] * mult,
                        credibility=q["reward"]["credibility"] * mult)
        if q["reward"].get("evidence"):
            a["evidence"].append(q["reward"]["evidence"])
        if who == "player" and q["explanation"] not in a["learnings"]:
            a["learnings"].append(q["explanation"])
        return f"Correto! {fmt_delta(d)}.{tag}", d
    if sabotage:
        d = apply_delta(g, who, credibility=-5, reducible=True)
    else:
        d = apply_delta(g, who, xp=-10 * mult, credibility=-15 * mult, reducible=True)
    return f"Incorreto! {fmt_delta(d)}.{tag}", d


def answer_question(g, idx):
    pd = g["pending"]
    if pd["chosen"] is not None:
        return
    q = pd["q"]
    ok = idx == q["correct"]
    text, d = grade_question(g, "player", q, ok, sabotage=pd.get("sabotage", False))
    record_answer(g, q, idx)
    pd["chosen"] = idx
    pd["result"] = {"tone": "success" if ok else "error", "text": text}
    log(g, f"{g['player']['name']} {'acertou' if ok else 'errou'} a questão ({CATEGORY_LABELS.get(q['category'], '')}). {fmt_delta(d)}")


# ---------------------------------------------------------------------------
# Escolhas (eventos, clientes, viagem)
# ---------------------------------------------------------------------------
def choose_option(g, idx):
    pd = g["pending"]
    if pd["chosen"] is not None:
        return
    opt = pd["options"][idx]
    if "condition" in opt:
        branch = opt["success"] if opt["condition"](g["player"]) else opt["failure"]
        effect, feedback = branch["effect"], branch["feedback"]
    else:
        effect, feedback = opt["effect"], opt["feedback"]
    d = apply_effect(g, "player", effect)
    extra = fmt_delta(d)
    pd["chosen"] = idx
    pd["result"] = {"tone": _tone(d) if not effect.get("skip") else "info",
                    "text": feedback + (f" ({extra})" if extra else "")}
    log(g, f"{g['player']['name']} — {pd['title']}: {feedback}")


# ---------------------------------------------------------------------------
# Treinamentos e Prova CRC (quizzes de várias questões)
# ---------------------------------------------------------------------------
def training_cost(g, who, cell):
    discount = FIRMS["laranja"]["bonus"]["value"] if g[who]["firm"] == "laranja" else 1
    return round(cell["cost"] * discount * _mult(g))


def offer_training(g, cell):
    p = g["player"]
    cost = training_cost(g, "player", cell)
    _set_pending(g, "offer", title=f"{cell['icon']} {cell['name']}", cell=cell, cost=cost,
                 can_afford=p["credits"] >= cost,
                 text=f"{cell['content']}\nCusto: C${cost}. Requer aprovação em um quiz.")


def accept_training(g):
    pd = g["pending"]
    start_quiz(g, "training", cell=pd["cell"], cost=pd["cost"])


def skip_training(g):
    cell = g["pending"]["cell"]
    apply_delta(g, "player", credibility=-5)
    log(g, f"{g['player']['name']} pulou o treinamento '{cell['courseKey']}' e perdeu 5 de credibilidade.")
    show_message(g, "Treinamento ignorado",
                 "Você pulou o treinamento e perdeu 5 de credibilidade por falta de proatividade.", "error")


def start_quiz(g, mode, cell=None, cost=0):
    if mode == "crc":
        bases, cat = random.sample(CRC_QUESTIONS, 5), "crc"
        pass_score, title, intro = 3, "🏆 Prova de Suficiência CRC", "Acerte pelo menos 3 de 5 para ser aprovado."
    else:
        cat = cell["courseKey"]
        pool = AUDIT_QUESTIONS[cat]
        bases = random.sample(pool, min(3, len(pool)))
        pass_score = math.ceil(len(bases) * 0.6)
        title = f"🎓 Quiz: {cat}"
        intro = f"{cell['content']} Acerte pelo menos {pass_score} de {len(bases)} para concluir o curso."
    qs = [prepare_question(b, cat) for b in bases]
    _set_pending(g, "quiz", mode=mode, title=title, intro=intro, questions=qs, i=0, score=0,
                 chosen=None, done=False, result=None, pass_score=pass_score, cell=cell, cost=cost)


def answer_quiz(g, idx):
    pd = g["pending"]
    if pd["chosen"] is not None:
        return
    q = pd["questions"][pd["i"]]
    pd["chosen"] = idx
    if idx == q["correct"]:
        pd["score"] += 1
    record_answer(g, q, idx)


def next_quiz(g):
    pd = g["pending"]
    if pd["i"] < len(pd["questions"]) - 1:
        pd["i"] += 1
        pd["chosen"] = None
    else:
        _finish_quiz(g)


def _finish_quiz(g):
    pd = g["pending"]
    p = g["player"]
    passed = pd["score"] >= pd["pass_score"]
    total = len(pd["questions"])
    pd["done"] = True
    if pd["mode"] == "training":
        cell = pd["cell"]
        apply_delta(g, "player", credits=-pd["cost"])
        if passed:
            apply_delta(g, "player", xp=cell["xp"])
            p["courses"].append(cell["courseKey"])
            text = f"Aprovado ({pd['score']}/{total})! Você concluiu \"{cell['courseKey']}\": +{cell['xp']} XP, -C${pd['cost']}."
            log(g, f"{p['name']} concluiu o treinamento \"{cell['courseKey']}\" e ganhou {cell['xp']} XP.")
        else:
            text = f"Reprovado ({pd['score']}/{total}). O curso foi pago (-C${pd['cost']}), mas não foi concluído."
            log(g, f"{p['name']} pagou mas não concluiu o treinamento \"{cell['courseKey']}\".")
        pd["result"] = {"tone": "success" if passed else "error", "text": text}
        return
    # Prova CRC
    if passed:
        apply_delta(g, "player", xp=200, credibility=20)
        p["has_passed_crc"] = True
        text = f"✅ APROVADO ({pd['score']}/{total})! +200 XP, +20 cred."
        log(g, f"{p['name']} passou no exame CRC!")
        if p["position"] == LAST:
            g["win_after"] = "player"
            text += " Você já está na casa de promoção: parabéns!"
    else:
        text = f"❌ Reprovado ({pd['score']}/{total}). Você precisa estudar mais. O jogo continua."
        log(g, f"{p['name']} foi reprovado no exame CRC.")
    pd["result"] = {"tone": "success" if passed else "error", "text": text}


# ---------------------------------------------------------------------------
# Minigame: Inventário
# ---------------------------------------------------------------------------
def start_inventory(g):
    items = []
    for name, lo, hi in random.sample(INVENTORY_ITEMS, 4):
        book = random.randint(lo, hi)
        physical = book
        if random.random() < 0.5:
            physical += random.choice([-1, 1]) * random.randint(1, 5)
        items.append({"name": name, "book": book, "physical": physical})
    _set_pending(g, "inventory", title="📦 Simulação de Inventário", items=items, result=None)


def submit_inventory(g, entries):
    """`entries`: diferença (físico − sistema) informada pelo jogador, na ordem dos itens."""
    pd = g["pending"]
    found = total = false_alarms = 0
    rows = []
    for item, entry in zip(pd["items"], entries):
        diff = item["physical"] - item["book"]
        if diff != 0:
            total += 1
            ok = entry == diff
            found += ok
        else:
            ok = entry == 0
            false_alarms += (not ok)
        rows.append({**item, "diff": diff, "entry": entry, "ok": ok})
    if total == 0:
        feedback, xp, cred = "Nenhuma divergência real nesta contagem.", 20, 5
    elif found == total:
        feedback, xp, cred = f"Excelente! Você encontrou todas as {total} divergências.", 50, 15
    else:
        feedback = f"Você encontrou {found} de {total} divergências."
        xp, cred = 20 + 10 * found, 5 + 5 * found
    if false_alarms:
        feedback += f" {false_alarms} alarme(s) falso(s): -{3 * false_alarms} cred."
    d = apply_delta(g, "player", xp=xp, credibility=cred)
    if false_alarms:
        d2 = apply_delta(g, "player", credibility=-3 * false_alarms, reducible=True)
        d["credibility"] += d2["credibility"]
    g["player"]["evidence"].append("Papel de Trabalho - Contagem de Estoque")
    pd["result"] = {"tone": "success" if found == total and not false_alarms else "info",
                    "text": f"{feedback} ({fmt_delta(d)})", "rows": rows}
    log(g, f"{g['player']['name']} concluiu o inventário. {feedback}")


# ---------------------------------------------------------------------------
# Minigame: Walkthrough
# ---------------------------------------------------------------------------
def start_walkthrough(g):
    key = random.choice(list(WALKTHROUGH_GAMES))
    data = WALKTHROUGH_GAMES[key]
    order = list(range(len(data["steps"])))
    while order == sorted(order):
        random.shuffle(order)
    _set_pending(g, "walkthrough", title=f"🗺️ {data['title']}", data=data,
                 available=order, order=[], result=None)


def walk_add(g, i):
    pd = g["pending"]
    if i in pd["available"] and pd["result"] is None:
        pd["available"].remove(i)
        pd["order"].append(i)


def walk_remove(g, i):
    pd = g["pending"]
    if i in pd["order"] and pd["result"] is None:
        pd["order"].remove(i)
        pd["available"].append(i)


def walk_check(g):
    pd = g["pending"]
    data = pd["data"]
    ok = pd["order"] == sorted(pd["order"])
    if ok:
        d = apply_effect(g, "player", {**data["reward"]})
        text = f"Ordem correta! Seu entendimento do processo foi documentado como evidência. ({fmt_delta(d)})"
        log(g, f"{g['player']['name']} validou o processo ({data['title']}).")
    else:
        d = apply_effect(g, "player", data["penalty"])
        text = f"Ordem incorreta. A confusão no entendimento do processo custou caro. ({fmt_delta(d)})"
        log(g, f"{g['player']['name']} falhou em validar o processo ({data['title']}).")
    pd["result"] = {"tone": "success" if ok else "error", "text": text}


# ---------------------------------------------------------------------------
# Entrada nas casas (jogador)
# ---------------------------------------------------------------------------
def enter_cell(g):
    p = g["player"]
    cell = BOARD_CELLS[p["position"]]
    t = cell["type"]
    title = f"{cell['icon']} {cell['name']}"
    if t == "question":
        _set_pending(g, "question", title=f"Questão: {title}", q=make_question(cell["category"]),
                     chosen=None, result=None)
    elif t == "exam":
        start_quiz(g, "crc")
    elif t == "inventory_game":
        start_inventory(g)
    elif t == "walkthrough_game":
        start_walkthrough(g)
    elif t == "event":
        if cell["eventName"] == "Viagem":
            ev = random.choice(TRAVEL_EVENTS)
            _set_pending(g, "choice", title=f"✈️ {ev['title']}", description=ev["content"],
                         options=[{"text": "Ok", "effect": {"skip": True},
                                   "feedback": "Você vai perder a próxima rodada."}],
                         chosen=None, result=None)
        else:
            pool = [e for e in GAME_EVENTS if e["title"] == cell["eventName"]] or GAME_EVENTS
            ev = random.choice(pool)
            _set_pending(g, "choice", title=f"⚡ Evento: {ev['title']}", description=ev["description"],
                         options=ev["options"], chosen=None, result=None)
    elif t == "client":
        sc = random.choice([s for s in CLIENT_SCENARIOS if s["type"] == cell["clientType"]])
        _set_pending(g, "choice", title=f"{cell['icon']} {sc['title']}", description=sc["description"],
                     options=sc["options"], chosen=None, result=None)
    elif t == "training":
        if cell["courseKey"] in p["courses"]:
            show_message(g, title, "Você já concluiu este curso. Nada a fazer aqui.", "info")
        else:
            offer_training(g, cell)
    elif t == "punishment":
        mult = _mult(g)
        d = apply_effect(g, "player", {k: v * mult for k, v in cell["effect"].items()})
        tag = " (Penalidade em dobro!)" if mult == 2 else ""
        log(g, f"{p['name']} foi penalizado: {cell['message']}{tag}")
        show_message(g, title, f"{cell['message']}{tag}\n\n{fmt_delta(d)}", "error")
    elif t == "goal":
        if p["has_passed_crc"]:
            g["win_after"] = "player"
            log(g, f"🏅 {p['name']} chegou à promoção e venceu o jogo!")
            show_message(g, "🏅 Promoção!", "Você chegou à promoção já aprovado no CRC. Parabéns!", "success")
        else:
            log(g, f"🏆 {p['name']} chegou à promoção, mas precisa passar no Exame CRC para ser efetivado!")
            flash(g, "info", "Chegou a hora da verdade! Passe no Exame de Suficiência para garantir sua promoção.")
            start_quiz(g, "crc")
    else:
        end_turn(g)


# ---------------------------------------------------------------------------
# Ações do jogador
# ---------------------------------------------------------------------------
def can_act(g):
    return g["turn"] == "player" and g["pending"] is None and not g["over"]


def player_roll(g):
    if not can_act(g):
        return
    p = g["player"]
    if p["hours"] < HOURS_PER_ROLL:
        p["hours"] = MAX_HOURS
        log(g, "Horas estouradas: folga compensatória para não violar a política de hora extra.")
        show_message(g, "⏰ Horas estouradas",
                     "Projeto com horas estouradas! Você perde este turno e volta ao trabalho com 8h.", "error")
        return
    if p["skip_next"]:
        p["skip_next"] = False
        log(g, f"{p['name']} pulou a rodada.")
        show_message(g, "✈️ Recuperação", "Você está se recuperando da viagem e perdeu esta rodada!", "info")
        return
    roll = random.randint(1, 6)
    g["dice"] = roll
    p["hours"] -= HOURS_PER_ROLL
    p["position"] = min(p["position"] + roll, LAST)
    log(g, f"{p['name']} tirou {roll} no dado e caiu em {BOARD_CELLS[p['position']]['name']}.")
    enter_cell(g)


def drink_coffee(g):
    if not can_act(g):
        return
    p = g["player"]
    cost = 100 if g["busy"] > 0 else 50
    if p["credits"] < cost:
        flash(g, "error", "Créditos insuficientes para o café!")
        return
    p["credits"] -= cost
    p["hours"] = min(MAX_HOURS, p["hours"] + 2)
    p["xp"] += 10
    g["coffee"] += 1
    log(g, f"{p['name']} tomou um café por C${cost} e recuperou 2 horas e 10 XP.")
    flash(g, "success", f"Café! -C${cost}, +2h, +10 XP.")
    if g["coffee"] % 3 == 0:
        flash(g, "warning", 'O gerente apareceu na copa: "Vocês estão acabando com o café da firma! Vamos focar na auditoria, pessoal!"')


def continue_turn(g):
    g["pending"] = None
    if g["win_after"]:
        declare_winner(g, g["win_after"])
        return
    end_turn(g)


def declare_winner(g, who):
    g["over"] = True
    g["winner"] = who
    g["pending"] = None
    _snapshot(g)


# ---------------------------------------------------------------------------
# Passagem de turno, Busy Season e prazo do ano fiscal
# ---------------------------------------------------------------------------
def end_turn(g):
    if g["over"]:
        return
    g["pending"] = None
    nxt = "npc" if g["turn"] == "player" else "player"
    new_week = g["week"] + (1 if nxt == "player" else 0)
    busy = max(0, g["busy"] - 1)
    if 5 < new_week < 15 and g["busy"] == 0 and random.random() < 0.2:
        busy = 5
        log(g, "🔥 Busy Season começou! Custos, recompensas e penalidades dobrados.")
        flash(g, "error", "🔥 Busy Season começou! Custos, recompensas e penalidades dobrados.")
    g["turn"], g["week"], g["busy"] = nxt, new_week, busy
    if nxt == "player":
        _snapshot(g)
        if g["week"] > g["max_weeks"]:
            g["over"], g["winner"] = True, "none"
            log(g, "O ano fiscal terminou e ninguém foi efetivado.")
        return
    run_npc_turn(g)


# ---------------------------------------------------------------------------
# Zeca Urubu
# ---------------------------------------------------------------------------
def run_npc_turn(g):
    npc, cfg = g["npc"], DIFFICULTY[g["difficulty"]]
    g["feed"] = []
    if npc["skip_next"]:
        npc["skip_next"] = False
        nlog(g, f"{NPC_NAME} está se recuperando da viagem e perdeu esta rodada.")
        end_turn(g)
        return
    roll = random.randint(1, cfg["npc_dice"])
    npc["position"] = min(npc["position"] + roll, LAST)
    cell = BOARD_CELLS[npc["position"]]
    nlog(g, f"{NPC_NAME} tirou {roll} e caiu em {cell['icon']} {cell['name']}.")
    if npc["position"] == g["player"]["position"] and npc["position"] > 0:
        _sabotage(g)
        return
    _npc_cell_action(g, cell, cfg["npc_acc"])
    if not g["over"]:
        end_turn(g)


def _npc_crc(g, acc):
    npc = g["npc"]
    score = sum(random.random() < acc for _ in range(5))
    if score >= 3:
        apply_delta(g, "npc", xp=200, credibility=20)
        npc["has_passed_crc"] = True
        nlog(g, f"{NPC_NAME} passou no exame CRC ({score}/5).")
        return True
    nlog(g, f"{NPC_NAME} foi reprovado no exame CRC ({score}/5).")
    return False


def _npc_cell_action(g, cell, acc):
    npc, t = g["npc"], cell["type"]
    if t == "question":
        q = make_question(cell["category"])
        ok = random.random() < acc
        _, d = grade_question(g, "npc", q, ok)
        nlog(g, f"{NPC_NAME} {'acertou' if ok else 'errou'} a questão. {fmt_delta(d)}")
    elif t == "event":
        if cell["eventName"] == "Viagem":
            npc["skip_next"] = True
            nlog(g, f"{NPC_NAME} teve problemas na viagem e perderá a próxima rodada.")
        else:
            nlog(g, f"{NPC_NAME} passou pelo evento: {cell['name']}.")
    elif t == "client":
        change = 5 if random.random() > 0.5 else -5
        apply_delta(g, "npc", credibility=change)
        nlog(g, f"{NPC_NAME} lidou com o cliente ({change:+d} cred.).")
    elif t == "training":
        cost = training_cost(g, "npc", cell)
        if cell["courseKey"] not in npc["courses"] and npc["credits"] >= cost and random.random() > 0.5:
            apply_delta(g, "npc", credits=-cost, xp=cell["xp"])
            npc["courses"].append(cell["courseKey"])
            nlog(g, f"{NPC_NAME} fez o curso '{cell['courseKey']}' (+{cell['xp']} XP).")
    elif t == "punishment":
        mult = _mult(g)
        d = apply_effect(g, "npc", {k: v * mult for k, v in cell["effect"].items()})
        nlog(g, f"{NPC_NAME} foi penalizado ({fmt_delta(d)}).")
    elif t == "inventory_game":
        if random.random() < acc:
            apply_delta(g, "npc", xp=30, credibility=10)
            nlog(g, f"{NPC_NAME} fechou o inventário sem divergências (+30 XP, +10 cred.).")
        else:
            apply_delta(g, "npc", credibility=-5, reducible=True)
            nlog(g, f"{NPC_NAME} deixou divergências passarem no inventário (-5 cred.).")
    elif t == "walkthrough_game":
        data = random.choice(list(WALKTHROUGH_GAMES.values()))
        if random.random() < acc:
            d = apply_effect(g, "npc", data["reward"])
            nlog(g, f"{NPC_NAME} validou um walkthrough ({fmt_delta(d)}).")
        else:
            d = apply_effect(g, "npc", data["penalty"])
            nlog(g, f"{NPC_NAME} errou um walkthrough ({fmt_delta(d)}).")
    elif t == "exam":
        _npc_crc(g, acc)
    elif t == "goal":
        if npc["has_passed_crc"] or _npc_crc(g, acc):
            nlog(g, f"🏅 {NPC_NAME} chegou à promoção!")
            declare_winner(g, "npc")


def _sabotage(g):
    s = random.choice(SABOTAGE_EVENTS)
    title = "😈 Sabotagem do Zeca Urubu!"
    nlog(g, s["feedback"])
    for who in ("player", "npc"):
        if s.get("effect", {}).get(who):
            apply_effect(g, who, s["effect"][who], reducible=False)
    action = s.get("action")
    if action == "extra_question":
        _set_pending(g, "question", title=title, intro=s["description"],
                     q=make_question("extra"), chosen=None, result=None, sabotage=True)
    elif action == "lose_evidence":
        ev = g["player"]["evidence"]
        if ev:
            lost = ev.pop()
            log(g, f"Evidência perdida: '{lost}'.")
            show_message(g, title, f"{s['description']}\n\nEvidência perdida: {lost}.", "error")
        else:
            show_message(g, title, f"{s['description']}\n\nVocê não tinha nenhuma evidência para perder. Sorte sua!", "info")
    else:
        show_message(g, title, f"{s['description']}\n\n{s['feedback']}", "error")


# ---------------------------------------------------------------------------
# Resultado final
# ---------------------------------------------------------------------------
def final_score(g):
    p = g["player"]
    return p["xp"] + p["credibility"] + p["credits"] // 10 + (300 if g["winner"] == "player" else 0)


def stats_rows(g):
    return [
        {"Tema": CATEGORY_LABELS.get(k, k), "Acertos": v["correct"], "Erros": v["wrong"]}
        for k, v in sorted(g["stats"].items())
    ]


def build_report(g):
    p = g["player"]
    cargo = senioridade(p["xp"])[0]
    result = {"player": "Promovido(a)", "npc": "Não promovido(a): o Zeca foi efetivado", "none": "Ano fiscal encerrado sem promoção"}[g["winner"]]
    total = p["correct"] + p["wrong"]
    lines = [
        f"# Relatório de Auditoria: {p['name']}", "",
        f"- **Firma:** {FIRMS[p['firm']]['name']}",
        f"- **Resultado:** {result}",
        f"- **Cargo final:** {cargo}",
        f"- **XP:** {p['xp']} | **Credibilidade:** {p['credibility']} | **Créditos:** C${p['credits']}",
        f"- **Pontuação final:** {final_score(g)}",
        f"- **Semanas:** {g['week']} | **Dificuldade do Zeca:** {g['difficulty']}",
        f"- **Respostas:** {p['correct']} certas de {total}", "",
        "## Evidências coletadas", *([f"- {e}" for e in p["evidence"]] or ["- Nenhuma"]), "",
        "## Cursos concluídos", *([f"- {c}" for c in p["courses"]] or ["- Nenhum"]), "",
        "## Aprendizados-chave", *([f"- {x}" for x in p["learnings"]] or ["- Nenhum"]), "",
        "## Revisão dos erros",
    ]
    if g["missed"]:
        for m in g["missed"]:
            lines += [f"**[{m['category']}] {m['question']}**",
                      f"- Sua resposta: {m['chosen']}", f"- Correta: {m['right']}", f"- Por quê: {m['explanation']}", ""]
    else:
        lines.append("Nenhum erro. Impecável!")
    return "\n".join(lines)
