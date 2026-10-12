"""Audit Quest: interface Streamlit. As regras ficam em engine.py e o conteúdo em game_data.py."""
import html
import math

import pandas as pd
import streamlit as st

import engine as E
from game_data import BOARD_CELLS, COLS, DIFFICULTY, FIRMS, COURSE_CONTENT, RULES_MD

st.set_page_config(page_title="Audit Quest", page_icon="🪶", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp, .stApp button, .stApp input { font-family: 'Inter', sans-serif; }
.block-container { max-width: 1180px; padding-top: 1.6rem; }
.stButton button { width: 100%; border-radius: 10px; }
.aq-card { border: 1px solid rgba(255,255,255,.14); border-radius: 14px; padding: 14px 16px;
  background: rgba(45,55,72,.55); }
.aq-card.active { border-color: #63b3ed; box-shadow: 0 0 14px rgba(99,179,237,.55); }
.aq-name { font-weight: 800; font-size: 1.1rem; display: flex; align-items: center; gap: 8px; }
.aq-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.aq-sub { font-size: .78rem; opacity: .7; margin-top: 2px; }
.aq-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }
.aq-stat { background: rgba(255,255,255,.07); border-radius: 8px; padding: 4px 8px; font-weight: 600; font-size: .9rem; }
.aq-level { margin-top: 10px; font-size: .85rem; font-weight: 600; color: #b794f4; }
.aq-bar { height: 8px; background: #2d3748; border-radius: 6px; overflow: hidden; margin-top: 6px; }
.aq-bar > div { height: 100%; background: #4299e1; }
.aq-center { text-align: center; padding-top: 8px; }
.aq-week { font-size: 1.5rem; font-weight: 800; }
.aq-board { display: grid; grid-template-columns: repeat(__COLS__, 1fr); gap: 8px; }
.aq-cell { position: relative; border-radius: 10px; padding: 18px 3px 8px; text-align: center; font-size: .7rem;
  font-weight: 600; color: #fff; border: 2px solid rgba(255,255,255,.25); min-height: 84px; line-height: 1.15; }
.aq-cell .ic { font-size: 1.35rem; display: block; margin-bottom: 2px; }
.aq-cell .n { position: absolute; top: 3px; left: 7px; font-size: .6rem; opacity: .65; }
.aq-cell .cost { position: absolute; bottom: -7px; left: -5px; background: #6b46c1; border-radius: 10px; padding: 1px 7px; font-size: .62rem; }
.aq-cell .toks { position: absolute; top: -9px; right: -7px; display: flex; gap: 2px; }
.aq-cell.here { box-shadow: 0 0 0 3px #63b3ed, 0 0 14px rgba(99,179,237,.7); }
.aq-tok { width: 22px; height: 22px; border-radius: 50%; border: 2px solid #fff; font-size: .68rem; font-weight: 800;
  display: inline-flex; align-items: center; justify-content: center; }
.aq-tok.p { background: #3182ce; } .aq-tok.z { background: #c53030; }
.t-q { background: linear-gradient(135deg,#2b6cb0,#4c51bf); }
.t-train { background: linear-gradient(135deg,#6b46c1,#805ad5); }
.t-client { background: linear-gradient(135deg,#d69e2e,#dd6b20); }
.t-event { background: linear-gradient(135deg,#0d9488,#0891b2); }
.t-bad { background: linear-gradient(135deg,#c53030,#b83280); }
.t-goal { background: linear-gradient(135deg,#2f855a,#38a169); border-color: #ecc94b; }
.t-def { background: linear-gradient(135deg,#4a5568,#2d3748); }
.aq-legend { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: .75rem; opacity: .85; margin-top: 12px; }
.aq-legend span::before { content: ''; display: inline-block; width: 10px; height: 10px; border-radius: 3px;
  margin-right: 5px; background: var(--c); }
.aq-dice { width: 74px; height: 74px; border-radius: 14px; background: #fff; color: #1a202c; font-size: 2.6rem;
  font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
@media (max-width: 640px) { .aq-cell { font-size: .58rem; min-height: 72px; } .aq-cell .ic { font-size: 1.05rem; } }
</style>
""".replace("__COLS__", str(COLS))

st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def md(text):
    """Escapa '$' para o Streamlit não interpretar 'C$100 ... C$50' como fórmula LaTeX."""
    return str(text).replace("$", "\\$")


def h(text):
    return html.escape(str(text)).replace("$", "&#36;")


def result_box(res):
    box = {"success": st.success, "error": st.error, "info": st.info, "warning": st.warning}[res["tone"]]
    box(md(res["text"]))


def continue_btn(g, pd_, label="Continuar ▶"):
    st.button(label, key=f"cont_{pd_['id']}", on_click=E.continue_turn, args=(g,), type="primary")


def option_buttons(pd_, labels, callback, g):
    for i, label in enumerate(labels):
        st.button(md(label), key=f"opt_{pd_['id']}_{pd_.get('i', 0)}_{i}", on_click=callback, args=(g, i))


def marked_options(q, chosen):
    for i, opt in enumerate(q["options"]):
        icon = "✅" if i == q["correct"] else ("❌" if i == chosen else "▫️")
        st.markdown(f"{icon} {md(opt)}")


# ---------------------------------------------------------------------------
# Tela de início
# ---------------------------------------------------------------------------
def start_game():
    firm = st.session_state.get("setup_firm")
    if not firm:
        return
    st.session_state.g = E.new_game(
        st.session_state.get("setup_name", ""), firm,
        st.session_state.get("setup_diff", "Normal"), st.session_state.get("setup_weeks", 30),
    )


def pick_firm(key):
    st.session_state.setup_firm = key


def render_setup():
    st.markdown("# 🪶 Audit Quest")
    st.caption("Suba na carreira, passe na Prova CRC e chegue à promoção antes do Zeca Urubu.")
    st.text_input("Seu nome de auditor", placeholder="Pica-Pau", key="setup_name")
    st.markdown("#### Escolha sua firma")
    selected = st.session_state.get("setup_firm")
    cols = st.columns(len(FIRMS))
    for col, (key, firm) in zip(cols, FIRMS.items()):
        with col:
            border = "#63b3ed" if selected == key else "rgba(255,255,255,.14)"
            st.markdown(
                f'<div class="aq-card" style="border:2px solid {border}">'
                f'<div style="height:8px;border-radius:4px;background:{firm["color"]};margin-bottom:10px"></div>'
                f'<div class="aq-name">{h(firm["name"])}</div>'
                f'<div class="aq-sub" style="font-size:.85rem;opacity:.85;margin-top:6px">{h(firm["bonus"]["text"])}</div></div>',
                unsafe_allow_html=True,
            )
            st.button("Selecionada ✓" if selected == key else "Escolher", key=f"firm_{key}",
                      on_click=pick_firm, args=(key,), type="primary" if selected == key else "secondary")
    c1, c2 = st.columns(2)
    with c1:
        st.select_slider("Dificuldade do Zeca Urubu", options=list(DIFFICULTY), value="Normal", key="setup_diff")
        st.caption(DIFFICULTY[st.session_state.get("setup_diff", "Normal")]["desc"])
    with c2:
        st.slider("Prazo do ano fiscal (semanas)", 15, 50, 30, key="setup_weeks")
        st.caption("Se ninguém for promovido até lá, o ano fiscal acaba sem promoção.")
    st.button("▶ Iniciar jogo", on_click=start_game, type="primary", disabled=not selected)
    if not selected:
        st.caption("Escolha uma firma para começar.")
    runs = st.session_state.get("runs", [])
    if runs:
        st.markdown("#### Partidas desta sessão")
        st.dataframe(pd.DataFrame(runs), hide_index=True)


# ---------------------------------------------------------------------------
# Cabeçalho e tabuleiro
# ---------------------------------------------------------------------------
def actor_card(a, active, is_npc=False):
    title, _, prog = E.senioridade(a["xp"])
    firm = FIRMS[a["firm"]]
    hours = "" if is_npc else f'<div class="aq-stat" title="Horas de trabalho">⏰ {a["hours"]}h</div>'
    return (
        f'<div class="aq-card{" active" if active else ""}">'
        f'<div class="aq-name">{"🦅" if is_npc else "🪶"} {h(a["name"])}'
        f'<span class="aq-dot" style="background:{firm["color"]}" title="{h(firm["name"])}"></span></div>'
        f'<div class="aq-sub">{h(firm["name"])} · casa {a["position"]}/{E.LAST}</div>'
        f'<div class="aq-stats">'
        f'<div class="aq-stat" title="Credibilidade">🏆 {a["credibility"]}</div>'
        f'<div class="aq-stat" title="XP">💡 {a["xp"]}</div>'
        f'<div class="aq-stat" title="Créditos">C&#36; {a["credits"]}</div>{hours}</div>'
        f'<div class="aq-level">{h(title)}</div>'
        f'<div class="aq-bar"><div style="width:{prog:.0f}%"></div></div></div>'
    )


def render_header(g):
    c1, c2, c3 = st.columns([4, 2.2, 4])
    c1.markdown(actor_card(g["player"], g["turn"] == "player"), unsafe_allow_html=True)
    c3.markdown(actor_card(g["npc"], g["turn"] == "npc", True), unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="aq-center"><div class="aq-week">Semana {g["week"]}</div>'
            f'<div class="aq-sub">de {g["max_weeks"]} no ano fiscal</div></div>',
            unsafe_allow_html=True,
        )
        st.progress(min(1.0, g["week"] / g["max_weeks"]))


def cell_class(t):
    return {"punishment": "t-bad", "training": "t-train", "question": "t-q", "inventory_game": "t-q",
            "walkthrough_game": "t-q", "client": "t-client", "event": "t-event", "exam": "t-goal",
            "goal": "t-goal", "start": "t-goal"}.get(t, "t-def")


def board_html(g):
    p_pos, n_pos = g["player"]["position"], g["npc"]["position"]
    initial = (g["player"]["name"][:1] or "P").upper()
    cells = []
    for r in range(math.ceil(len(BOARD_CELLS) / COLS)):
        idxs = list(range(r * COLS, min((r + 1) * COLS, len(BOARD_CELLS))))
        if r % 2:  # serpentina: linhas ímpares correm da direita para a esquerda
            idxs.reverse()
        for i in idxs:
            cell = BOARD_CELLS[i]
            toks = ""
            if p_pos == i:
                toks += f'<span class="aq-tok p" title="{h(g["player"]["name"])}">{h(initial)}</span>'
            if n_pos == i:
                toks += '<span class="aq-tok z" title="Zeca Urubu">Z</span>'
            cost = ""
            if cell["type"] == "training":
                cost = f'<span class="cost">C&#36;{E.training_cost(g, "player", cell)}</span>'
            cells.append(
                f'<div class="aq-cell {cell_class(cell["type"])}{" here" if p_pos == i else ""}" title="{h(cell["name"])}">'
                f'<span class="n">{i}</span><span class="toks">{toks}</span>'
                f'<span class="ic">{cell["icon"]}</span>{h(cell["name"])}{cost}</div>'
            )
    legend = "".join(f'<span style="--c:{c}">{label}</span>' for c, label in [
        ("#4c51bf", "Perguntas e minigames"), ("#805ad5", "Treinamentos"), ("#dd6b20", "Clientes"),
        ("#0891b2", "Eventos"), ("#c53030", "Penalidades"), ("#38a169", "Início, CRC e Promoção")])
    return f'<div class="aq-board">{"".join(cells)}</div><div class="aq-legend">{legend}</div>'


# ---------------------------------------------------------------------------
# Interações pendentes
# ---------------------------------------------------------------------------
def r_message(g, pd_):
    st.subheader(pd_["title"])
    result_box(pd_["result"])
    continue_btn(g, pd_)


def r_question(g, pd_):
    q = pd_["q"]
    st.subheader(pd_["title"])
    if pd_.get("intro"):
        st.warning(md(pd_["intro"]))
    st.markdown(f"**{md(q['question'])}**")
    if pd_["chosen"] is None:
        option_buttons(pd_, q["options"], E.answer_question, g)
    else:
        marked_options(q, pd_["chosen"])
        result_box(pd_["result"])
        st.caption("💡 " + md(q["explanation"]))
        continue_btn(g, pd_)


def r_choice(g, pd_):
    st.subheader(pd_["title"])
    st.markdown(md(pd_["description"]))
    if pd_["chosen"] is None:
        option_buttons(pd_, [o["text"] for o in pd_["options"]], E.choose_option, g)
    else:
        st.markdown(f"**Sua escolha:** {md(pd_['options'][pd_['chosen']]['text'])}")
        result_box(pd_["result"])
        continue_btn(g, pd_)


def r_offer(g, pd_):
    st.subheader(pd_["title"])
    st.markdown(md(pd_["text"]).replace("\n", "  \n"))
    c1, c2 = st.columns(2)
    with c1:
        st.button(md(f"Fazer treinamento (C${pd_['cost']})"), key=f"acc_{pd_['id']}", type="primary",
                  on_click=E.accept_training, args=(g,), disabled=not pd_["can_afford"])
    with c2:
        st.button("Pular (-5 de credibilidade)", key=f"skp_{pd_['id']}", on_click=E.skip_training, args=(g,))
    if not pd_["can_afford"]:
        st.caption("Créditos insuficientes para este curso.")


def r_quiz(g, pd_):
    n = len(pd_["questions"])
    st.subheader(pd_["title"])
    st.caption(md(pd_["intro"]))
    if pd_["done"]:
        result_box(pd_["result"])
        continue_btn(g, pd_)
        return
    st.progress(pd_["i"] / n, text=f"Questão {pd_['i'] + 1} de {n} · acertos: {pd_['score']}")
    q = pd_["questions"][pd_["i"]]
    st.markdown(f"**{md(q['question'])}**")
    if pd_["chosen"] is None:
        option_buttons(pd_, q["options"], E.answer_quiz, g)
    else:
        marked_options(q, pd_["chosen"])
        (st.success if pd_["chosen"] == q["correct"] else st.error)("Correto!" if pd_["chosen"] == q["correct"] else "Incorreto.")
        st.caption("💡 " + md(q["explanation"]))
        last = pd_["i"] == n - 1
        st.button("Ver resultado ▶" if last else "Próxima ▶", key=f"next_{pd_['id']}_{pd_['i']}",
                  on_click=E.next_quiz, args=(g,), type="primary")


def _submit_inventory(g, pid, n):
    E.submit_inventory(g, [int(st.session_state.get(f"inv_{pid}_{i}", 0)) for i in range(n)])


def r_inventory(g, pd_):
    st.subheader(pd_["title"])
    items = pd_["items"]
    if pd_["result"] is None:
        st.markdown("Compare a quantidade do **sistema** com a **contagem física** e informe a diferença "
                    "(físico − sistema) de cada item. Use **0** quando não houver divergência.")
        head = st.columns([2, 1.2, 1.2, 1.6])
        for c, t in zip(head, ["Item", "Sistema", "Físico", "Sua diferença"]):
            c.markdown(f"**{t}**")
        for i, it in enumerate(items):
            row = st.columns([2, 1.2, 1.2, 1.6])
            row[0].write(it["name"])
            row[1].write(it["book"])
            row[2].write(it["physical"])
            row[3].number_input("diferença", key=f"inv_{pd_['id']}_{i}", min_value=-99, max_value=99,
                                value=0, step=1, label_visibility="collapsed")
        st.button("Finalizar e apurar diferenças", key=f"inv_ok_{pd_['id']}", type="primary",
                  on_click=_submit_inventory, args=(g, pd_["id"], len(items)))
    else:
        result_box(pd_["result"])
        for r in pd_["result"]["rows"]:
            st.markdown(f"{'✅' if r['ok'] else '❌'} **{r['name']}**: sistema {r['book']}, físico {r['physical']}, "
                        f"diferença real {r['diff']:+d}, você informou {r['entry']:+d}")
        continue_btn(g, pd_)


def r_walkthrough(g, pd_):
    data = pd_["data"]
    st.subheader(pd_["title"])
    st.markdown(md(data["description"]))
    if pd_["result"] is None:
        left, right = st.columns(2)
        with left:
            st.markdown("**Passos disponíveis** (clique para adicionar)")
            for i in pd_["available"]:
                st.button(md(data["steps"][i]), key=f"wa_{pd_['id']}_{i}", on_click=E.walk_add, args=(g, i))
        with right:
            st.markdown("**Sua ordem** (clique para remover)")
            if not pd_["order"]:
                st.caption("Nenhum passo escolhido ainda.")
            for pos, i in enumerate(pd_["order"], 1):
                st.button(md(f"{pos}. {data['steps'][i]}"), key=f"wr_{pd_['id']}_{i}", on_click=E.walk_remove, args=(g, i))
        st.button("Verificar ordem", key=f"wc_{pd_['id']}", type="primary", on_click=E.walk_check, args=(g,),
                  disabled=len(pd_["order"]) != len(data["steps"]))
    else:
        result_box(pd_["result"])
        st.markdown("**Ordem correta:**")
        for pos, step in enumerate(data["steps"], 1):
            st.markdown(f"{pos}. {md(step)}")
        continue_btn(g, pd_)


RENDERERS = {"message": r_message, "question": r_question, "choice": r_choice, "offer": r_offer,
             "quiz": r_quiz, "inventory": r_inventory, "walkthrough": r_walkthrough}


def render_controls(g):
    p = g["player"]
    cost = 100 if g["busy"] > 0 else 50
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.markdown(f'<div class="aq-dice">{g["dice"] or "🎲"}</div>', unsafe_allow_html=True)
    c2.button("🎲 Jogar dados", key="roll", type="primary", on_click=E.player_roll, args=(g,))
    c3.button(md(f"☕ Café (C${cost}): +2h e +10 XP"), key="coffee", on_click=E.drink_coffee, args=(g,))
    if p["hours"] < 4:
        st.warning("⏰ Você está sem horas. Jogar o dado agora custa o turno. Um café devolve 2h.")


# ---------------------------------------------------------------------------
# Abas: log, papel de trabalho, evolução
# ---------------------------------------------------------------------------
def render_tabs(g):
    t_log, t_work, t_chart = st.tabs(["📜 Log", "📋 Papel de trabalho", "📈 Evolução"])
    with t_log:
        with st.container(height=320):
            for e in reversed(g["log"]):
                st.markdown(f"**S{e['week']}** · {md(e['msg'])}")
    with t_work:
        p = g["player"]
        a, b, c = st.columns(3)
        a.markdown("**Evidências coletadas**")
        for ev in p["evidence"] or []:
            a.markdown(f"📄 {md(ev)}")
        if not p["evidence"]:
            a.caption("Nenhuma evidência ainda.")
        b.markdown("**Cursos concluídos**")
        for course in p["courses"]:
            b.markdown(f"🎓 **{course}**")
            b.caption(COURSE_CONTENT[course])
        if not p["courses"]:
            b.caption("Nenhum curso concluído.")
        c.markdown("**Aprendizados-chave**")
        for item in p["learnings"]:
            c.markdown(f"💡 {md(item)}")
        if not p["learnings"]:
            c.caption("Nenhum aprendizado registrado.")
    with t_chart:
        df = pd.DataFrame(g["history"]).drop_duplicates("Semana", keep="last")
        if len(df) < 2:
            st.caption("O gráfico aparece depois da primeira rodada.")
        else:
            df = df.set_index("Semana")
            xp_cols = [c for c in df.columns if "(XP)" in c]
            cr_cols = [c for c in df.columns if "(Cred.)" in c]
            st.markdown("**XP**")
            st.line_chart(df[xp_cols])
            st.markdown("**Credibilidade**")
            st.line_chart(df[cr_cols])


# ---------------------------------------------------------------------------
# Tela do jogo
# ---------------------------------------------------------------------------
def render_game(g):
    if g["busy"] > 0:
        st.markdown("<style>.stApp{background:radial-gradient(circle at top,#4a0e0e,#1a202c 70%)}</style>",
                    unsafe_allow_html=True)
    while g["flash"]:
        tone, text = g["flash"].pop(0)
        st.toast(md(text), icon={"success": "✅", "error": "🚨", "warning": "⚠️"}.get(tone, "ℹ️"))
    render_header(g)
    if g["busy"] > 0:
        st.error(f"🔥 BUSY SEASON ({g['busy']} turnos restantes): recompensas, penalidades e custos em dobro!")
    st.write("")
    if g["feed"]:
        with st.expander("🦅 O que o Zeca Urubu fez na última rodada", expanded=g["pending"] is None):
            for line in g["feed"]:
                st.markdown("- " + md(line.replace("🤖 ", "")))
    with st.container(border=True):
        if g["pending"]:
            RENDERERS[g["pending"]["kind"]](g, g["pending"])
        else:
            render_controls(g)
    st.markdown(board_html(g), unsafe_allow_html=True)
    st.write("")
    render_tabs(g)


# ---------------------------------------------------------------------------
# Tela final
# ---------------------------------------------------------------------------
def reset_game():
    st.session_state.g = None


def render_end(g):
    p = g["player"]
    if not g.get("recorded"):
        g["recorded"] = True
        st.session_state.setdefault("runs", []).append({
            "Jogador": p["name"], "Firma": FIRMS[p["firm"]]["name"], "Dificuldade": g["difficulty"],
            "Resultado": {"player": "Promovido", "npc": "Zeca venceu", "none": "Sem promoção"}[g["winner"]],
            "Semanas": g["week"], "Pontuação": E.final_score(g),
        })
    if g["winner"] == "player":
        st.markdown("# 🏆 Parabéns!")
        st.success("Você apresentou um bom desempenho e foi promovido!")
    elif g["winner"] == "npc":
        st.markdown("# 😢 Fim de jogo")
        st.error("Zeca Urubu foi promovido como diferenciado e acabou o budget desse ano fiscal. Mais sorte na próxima vez!")
    else:
        st.markdown("# 📆 Ano fiscal encerrado")
        st.warning("O prazo acabou e ninguém foi efetivado. Tente de novo, e aproveite melhor as semanas.")
    m = st.columns(5)
    m[0].metric("Cargo final", E.senioridade(p["xp"])[0])
    m[1].metric("XP", p["xp"])
    m[2].metric("Credibilidade", p["credibility"])
    m[3].metric("Créditos", f"C$ {p['credits']}")
    m[4].metric("Pontuação", E.final_score(g))
    total = p["correct"] + p["wrong"]
    if total:
        st.markdown(f"**Aproveitamento:** {p['correct']} acertos em {total} questões ({p['correct'] / total:.0%})")
    rows = E.stats_rows(g)
    if rows:
        st.markdown("#### Desempenho por tema")
        st.bar_chart(pd.DataFrame(rows).set_index("Tema"))
    if g["missed"]:
        with st.expander(f"📚 Revisar {len(g['missed'])} erro(s)"):
            for m_ in g["missed"]:
                st.markdown(f"**[{md(m_['category'])}] {md(m_['question'])}**")
                st.markdown(f"- Você marcou: {md(m_['chosen'])}  \n- Correta: {md(m_['right'])}")
                st.caption("💡 " + md(m_["explanation"]))
    c1, c2 = st.columns(2)
    c1.download_button("📄 Baixar relatório de auditoria", data=E.build_report(g),
                       file_name="relatorio_audit_quest.md", mime="text/markdown")
    c2.button("Jogar novamente", on_click=reset_game, type="primary")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
st.session_state.setdefault("g", None)
g = st.session_state.g

with st.sidebar:
    st.markdown("### Como jogar")
    st.markdown(md(RULES_MD))
    if g and not g["over"]:
        st.divider()
        st.button("Reiniciar jogo", on_click=reset_game)

if g is None:
    render_setup()
elif g["over"]:
    render_end(g)
else:
    render_game(g)
