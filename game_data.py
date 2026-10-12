"""Conteúdo do Audit Quest: tabuleiro, firmas, perguntas, eventos e cenários.

Para adicionar perguntas, basta incluir uma linha `Q(...)` na categoria desejada.
A resposta certa é SEMPRE o 2º argumento; o jogo embaralha as alternativas
na hora de exibir, então não precisa se preocupar com a posição.
"""

COLS = 6  # colunas do tabuleiro (serpentina)
MAX_HOURS = 8
HOURS_PER_ROLL = 4


def Q(question, right, wrong1, wrong2, explanation, xp=20, cred=5, evidence=None):
    reward = {"xp": xp, "credibility": cred}
    if evidence:
        reward["evidence"] = evidence
    return {
        "question": question,
        "options": [right, wrong1, wrong2],
        "explanation": explanation,
        "reward": reward,
    }


# ---------------------------------------------------------------------------
# Senioridade
# ---------------------------------------------------------------------------
LEVELS = [
    (250, "Trainee"),
    (750, "Assistente I"),
    (1500, "Assistente II"),
    (3000, "Sênior I"),
    (None, "Sênior II"),
]

# ---------------------------------------------------------------------------
# Tabuleiro
# ---------------------------------------------------------------------------
BOARD_CELLS = [
    {"name": "Início", "type": "start", "icon": "🏁"},
    {"name": "Controles Internos", "type": "question", "category": "controls", "icon": "🛡️"},
    {"name": "Cliente Agressivo", "type": "client", "clientType": "Agressivo", "icon": "😠"},
    {"name": "Treinamento: Ética", "type": "training", "icon": "🎓", "cost": 100, "xp": 30,
     "courseKey": "Ética", "content": "Aprenda sobre independência e objetividade."},
    {"name": "Happy Hour", "type": "event", "icon": "🍻", "eventName": "Happy Hour da Firma"},
    {"name": "Inventário", "type": "inventory_game", "icon": "📦"},
    {"name": "Pausa para o Café", "type": "event", "icon": "☕", "eventName": "Pausa para o Café"},
    {"name": "Normas (IFRS)", "type": "question", "category": "ifrs", "icon": "📚"},
    {"name": "Viagem", "type": "event", "icon": "✈️", "eventName": "Viagem"},
    {"name": "Cliente Colaborativo", "type": "client", "clientType": "Colaborativo", "icon": "🤝"},
    {"name": "WCGW?", "type": "event", "icon": "🚨", "eventName": "WCGW Identificado!"},
    {"name": "Análise de Dados", "type": "question", "category": "data_analytics", "icon": "📊"},
    {"name": "Treinamento: Contabilidade", "type": "training", "icon": "🎓", "cost": 150, "xp": 40,
     "courseKey": "Contabilidade", "content": "Aprofunde seus conhecimentos contábeis."},
    {"name": "Revisão do Sócio", "type": "event", "icon": "🧐", "eventName": "Revisão do Sócio"},
    {"name": "Amostragem", "type": "question", "category": "sampling", "icon": "🔍"},
    {"name": "Treinamento: IFRS", "type": "training", "icon": "🎓", "cost": 120, "xp": 35,
     "courseKey": "IFRS", "content": "Domine as normas internacionais."},
    {"name": "Desafio Prático", "type": "question", "category": "practical", "icon": "🧩"},
    {"name": "Cliente Exigente", "type": "client", "clientType": "Exigente", "icon": "🕵️"},
    {"name": "Risco de Litígio", "type": "punishment", "icon": "⚖️",
     "message": "Você não confirmou se havia litígios relevantes e isso atrasou a aceitação do cliente! Perca 20 de credibilidade.",
     "effect": {"credibility": -20}},
    {"name": "Walkthrough", "type": "walkthrough_game", "icon": "🗺️"},
    {"name": "Treinamento: Amostragem", "type": "training", "icon": "🎓", "cost": 110, "xp": 25,
     "courseKey": "Amostragem", "content": "Aprenda técnicas de amostragem."},
    {"name": "Pergunta Extra", "type": "question", "category": "extra", "icon": "❓"},
    {"name": "Auditoria de Estoques", "type": "inventory_game", "icon": "📦"},
    {"name": "Mentoria com Sênior", "type": "event", "icon": "🧑‍🏫", "eventName": "Mentoria com Sênior"},
    {"name": "Treinamento: Fraudes", "type": "training", "icon": "🎓", "cost": 130, "xp": 30,
     "courseKey": "Fraudes", "content": "Identifique e previna fraudes em auditoria."},
    {"name": "Penalidade: Erro Material", "type": "punishment", "icon": "⚠️",
     "message": "Erro material detectado! Perca 12 de credibilidade e 15 XP.",
     "effect": {"credibility": -12, "xp": -15}},
    {"name": "Auditoria de Receitas", "type": "question", "category": "receitas", "icon": "💰"},
    {"name": "Treinamento: Comunicação", "type": "training", "icon": "🎓", "cost": 90, "xp": 20,
     "courseKey": "Comunicação", "content": "Melhore sua comunicação com clientes."},
    {"name": "Prova CRC", "type": "exam", "icon": "🏆"},
    {"name": "Promoção!", "type": "goal", "icon": "🏅"},
]

# ---------------------------------------------------------------------------
# Firmas
# ---------------------------------------------------------------------------
FIRMS = {
    "azul": {"name": "Big Blue", "color": "#2563eb",
             "bonus": {"type": "credibility", "value": 20, "text": "+20 Credibilidade inicial"}},
    "verde": {"name": "Big Green", "color": "#22c55e",
              "bonus": {"type": "credits", "value": 500, "text": "+C$500 Créditos iniciais"}},
    "laranja": {"name": "Big Orange", "color": "#f97316",
                "bonus": {"type": "training_discount", "value": 0.8, "text": "20% de desconto em treinamentos"}},
    "amarela": {"name": "Big Yellow", "color": "#facc15",
                "bonus": {"type": "error_reduction", "value": 0.5, "text": "50% menos perda de credibilidade por erros"}},
}

# ---------------------------------------------------------------------------
# Dificuldade do Zeca Urubu
# ---------------------------------------------------------------------------
DIFFICULTY = {
    "Fácil": {"npc_dice": 3, "npc_acc": 0.45, "desc": "Zeca rola 1–3 e acerta ~45%"},
    "Normal": {"npc_dice": 4, "npc_acc": 0.60, "desc": "Zeca rola 1–4 e acerta ~60% (igual à versão original)"},
    "Difícil": {"npc_dice": 5, "npc_acc": 0.75, "desc": "Zeca rola 1–5 e acerta ~75%"},
}

CATEGORY_LABELS = {
    "receitas": "Receitas", "controls": "Controles Internos", "ifrs": "Normas (IFRS)",
    "sampling": "Amostragem", "practical": "Desafio Prático", "extra": "Pergunta Extra",
    "data_analytics": "Análise de Dados", "Ética": "Treinamento: Ética",
    "Contabilidade": "Treinamento: Contabilidade", "IFRS": "Treinamento: IFRS",
    "Amostragem": "Treinamento: Amostragem", "Fraudes": "Treinamento: Fraudes",
    "Comunicação": "Treinamento: Comunicação", "crc": "Prova CRC",
}

# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------
AUDIT_QUESTIONS = {
    "receitas": [
        Q("O que deve ser analisado na auditoria de receitas?",
          "Reconhecimento, documentação e corte de receitas", "Apenas valores recebidos", "Despesas pagas",
          "Reconhecimento conforme IFRS 15, documentação de contratos, análise de corte e testes de integridade são essenciais na auditoria de receitas.",
          22, 5, "Análise de Corte de Receitas"),
        Q("Qual risco é comum na auditoria de receitas?",
          "Superavaliação por reconhecimento antecipado", "Subavaliação", "Nenhum",
          "Superavaliação por reconhecimento antecipado ou falta de documentação é um risco frequente em receitas.", 18, 4),
        Q("O que é um teste de corte (cut-off) em receitas?",
          "Verificar se as vendas próximas ao fim do período foram registradas no período correto",
          "Cortar custos ao final do ano", "Interromper as vendas no fim do mês",
          "O teste de corte confere transações do início e do fim do período para garantir que a receita foi reconhecida no exercício a que pertence.",
          22, 5, "Teste de Corte de Vendas"),
        Q("Pela IFRS 15, quando a receita deve ser reconhecida?",
          "Quando a obrigação de desempenho é satisfeita (o controle é transferido ao cliente)",
          "Quando o contrato é assinado", "Quando o cliente paga",
          "A receita é reconhecida conforme a entidade satisfaz as obrigações de desempenho, ou seja, quando o cliente obtém o controle do bem ou serviço.", 22, 5),
        Q("Segundo as normas de auditoria sobre fraude, o que se presume em relação à receita?",
          "Que existe risco de fraude no reconhecimento de receita",
          "Que receita nunca envolve risco de fraude", "Que o risco só existe em empresas listadas em bolsa",
          "Há uma presunção (refutável) de que existem riscos de fraude no reconhecimento de receita, o que exige procedimentos específicos.", 24, 6),
    ],
    "controls": [
        Q("O que é segregação de funções?",
          "Separar tarefas para evitar fraudes e erros", "Juntar equipes", "Demitir funcionários",
          "Segregação de funções é um controle chave para prevenir erros e fraudes, exigindo que diferentes pessoas realizem etapas críticas do processo.",
          22, 5, "Revisão de Segregação de Funções"),
        Q('Qual o objetivo de um "walkthrough" na auditoria de controles internos?',
          "Confirmar o entendimento do processo e dos controles", "Testar 100% das transações",
          "Apenas conversar com o gestor da área",
          "O walkthrough serve para confirmar o entendimento do auditor sobre o fluxo de uma transação e a implementação dos controles desenhados, do início ao fim.",
          25, 6, "Documentação de Walkthrough"),
        Q("Qual a diferença entre teste de controle e teste substantivo?",
          "O teste de controle avalia a eficácia dos controles; o substantivo testa saldos e transações",
          "O teste de controle verifica saldos; o substantivo avalia a eficácia dos controles",
          "Não há diferença, são sinônimos",
          "Testes de controle verificam se os controles operaram eficazmente; testes substantivos detectam distorções diretamente em saldos, transações e divulgações.", 22, 5),
        Q("Qual é um exemplo de controle preventivo?",
          "Aprovação do pedido de compra antes de ele ser emitido",
          "Conciliação bancária feita no mês seguinte", "Revisão posterior de um relatório de exceções",
          "Controles preventivos impedem o erro antes que ele ocorra. Conciliações e revisões posteriores são controles detectivos.", 20, 5),
    ],
    "ifrs": [
        Q("Qual IFRS trata de Receita de Contratos com Clientes?", "IFRS 15", "IFRS 9", "IFRS 16",
          "A IFRS 15 estabelece os princípios para o reconhecimento de receita, incluindo identificação de obrigações de desempenho e alocação do preço da transação.",
          22, 5, "Análise de Contrato (IFRS 15)"),
        Q("Qual IFRS trata de instrumentos financeiros?", "IFRS 9", "IFRS 16", "IFRS 15",
          "A IFRS 9 trata de instrumentos financeiros, reconhecimento e mensuração.", 18, 4),
        Q("Qual IFRS trata de arrendamentos?", "IFRS 16", "IFRS 9", "IFRS 15",
          "A IFRS 16 trata de arrendamentos, trazendo ativos e passivos para o balanço.", 18, 4),
        Q("Qual norma trata do ativo imobilizado (Property, Plant and Equipment)?", "IAS 16", "IAS 2", "IAS 38",
          "A IAS 16 (CPC 27) trata do imobilizado. A IAS 2 trata de estoques e a IAS 38, de ativos intangíveis.", 18, 4),
        Q("Qual norma trata da redução ao valor recuperável de ativos (impairment)?", "IAS 36", "IAS 37", "IAS 12",
          "A IAS 36 (CPC 01) define quando e como reconhecer perdas por impairment. A IAS 37 trata de provisões e a IAS 12, de tributos sobre o lucro.", 20, 5),
        Q("Qual norma trata de estoques?", "IAS 2", "IAS 16", "IFRS 15",
          "A IAS 2 (CPC 16) trata de estoques: custo, valor realizável líquido e critérios de mensuração.", 18, 4),
    ],
    "sampling": [
        Q("O que é risco de amostragem?",
          "Concluir diferente do que a população inteira mostraria", "Selecionar a amostra errada", "Perder os documentos",
          "É o risco de a amostra não ser representativa da população, podendo levar a conclusões incorretas.",
          22, 5, "Cálculo de Amostra Estatística"),
        Q("O que é amostragem estatística?",
          "Seleção aleatória de itens para teste", "Testar todos os itens", "Escolher os maiores valores",
          "Amostragem estatística envolve seleção aleatória para obter evidência representativa.", 20, 5),
        Q("Qual a vantagem da amostragem estatística sobre a não estatística?",
          "Permite quantificar objetivamente o risco de amostragem",
          "Elimina completamente o risco de amostragem", "Dispensa o julgamento profissional do auditor",
          "A amostragem estatística permite medir o risco de amostragem, mas o julgamento do auditor continua necessário e o risco nunca é eliminado.", 20, 5),
        Q("Em amostragem por unidade monetária (MUS), quais itens têm maior probabilidade de seleção?",
          "Os de maior valor", "Os de menor valor", "Todos têm a mesma probabilidade",
          "Na MUS cada unidade monetária é uma unidade amostral, então itens de maior valor têm mais chances de ser selecionados.", 22, 5),
        Q("O que o auditor faz com itens individualmente significativos?",
          "Testa separadamente, fora da amostra (key items)", "Descarta da população", "Mistura aleatoriamente com os demais",
          "Itens de valor elevado ou alto risco costumam ser testados individualmente; a amostra cobre o restante da população.", 20, 5),
    ],
    "practical": [
        Q("Como agir diante de um cliente que pressiona por resultados?",
          "Manter independência e ceticismo profissional", "Ceder à pressão para manter o cliente",
          "Ignorar e focar apenas nos números",
          "Manter a independência e o ceticismo profissional é fundamental para a qualidade e integridade da auditoria, conforme a NBC PG 01.", 20, 8),
        Q('O que significa "Materialidade de Desempenho" (Tolerable Error)?',
          "Um valor menor que a materialidade geral para testar contas específicas",
          "A performance financeira da empresa", "O erro máximo que a empresa pode cometer",
          "Materialidade de Desempenho é um valor menor que a materialidade geral, usado para reduzir a probabilidade de que distorções não corrigidas e não detectadas excedam a materialidade do todo.",
          25, 5),
        Q("Você encontrou uma distorção pequena e não corrigida. O que fazer?",
          "Acumular com as demais e avaliar o efeito agregado frente à materialidade",
          "Ignorar, porque é pequena", "Ajustar o saldo você mesmo nos livros do cliente",
          "Distorções não corrigidas devem ser acumuladas: várias pequenas podem, juntas, ser relevantes. A correção cabe à administração.", 22, 6),
        Q("O cliente oferece um presente de alto valor ao final do trabalho. O que fazer?",
          "Recusar e reportar conforme a política de ética da firma", "Aceitar, se for discreto",
          "Aceitar e dividir com a equipe",
          "Presentes de valor relevante criam ameaça de interesse próprio e de familiaridade à independência.", 20, 8),
        Q("Qual o papel da carta de representação da administração?",
          "Obter confirmações formais da administração sobre responsabilidades e informações prestadas",
          "Substituir os procedimentos de auditoria", "Transferir a responsabilidade da auditoria para o cliente",
          "A carta de representação complementa a evidência de auditoria, mas nunca substitui procedimentos.", 20, 5),
    ],
    "extra": [
        Q("Qual a principal qualidade de um auditor?", "Ética e ceticismo", "Rapidez", "Popularidade",
          "Ética e ceticismo profissional são fundamentais para o auditor garantir a confiança e a qualidade do seu trabalho.", 15, 3),
        Q("O que é ceticismo profissional?",
          "Atitude questionadora e atenta a condições que possam indicar distorção",
          "Desconfiar de todas as pessoas", "Aceitar as explicações da administração",
          "É manter uma mente questionadora e avaliar criticamente as evidências, sem presumir desonestidade nem confiar cegamente.", 15, 3),
        Q("Qual opinião é emitida quando há distorção relevante e generalizada?",
          "Opinião adversa", "Opinião com ressalva", "Opinião sem modificação",
          "Distorção relevante e generalizada leva à opinião adversa. Se for relevante mas não generalizada, a opinião é com ressalva.", 18, 4),
    ],
    "data_analytics": [
        Q("Qual a vantagem de usar Análise de Dados (Data Analytics) na auditoria?",
          "Testar 100% da população de dados", "Reduzir o tempo gasto com o cliente", "Aumentar os honorários",
          "A análise de dados permite ao auditor examinar populações inteiras de dados para identificar anomalias e riscos, em vez de depender apenas de amostras.",
          30, 10, "Dashboard de Análise de Dados"),
        Q("Qual é um uso típico de análise de dados em lançamentos contábeis?",
          "Identificar lançamentos manuais fora do horário ou com valores redondos",
          "Corrigir automaticamente os lançamentos", "Substituir a avaliação de risco",
          "Testes em lançamentos manuais (horário atípico, valores redondos, usuários incomuns) ajudam a detectar risco de fraude por burla de controles.",
          28, 8, "Teste de Lançamentos Manuais"),
        Q("Antes de analisar um arquivo extraído do ERP, qual cuidado é essencial?",
          "Validar completude e integridade (reconciliar com o razão)", "Apagar linhas duplicadas sem investigar",
          "Confiar, pois o sistema é do cliente",
          "Informações produzidas pela entidade precisam ter completude e acurácia validadas antes de servir como base de testes.", 25, 8),
    ],
    # --- Quizzes dos treinamentos ---
    "Ética": [
        Q("O que significa independência na auditoria?", "Não ter interesses pessoais no cliente",
          "Ser amigo do cliente", "Fazer tudo sozinho",
          "Independência é não ter interesses pessoais ou financeiros no cliente auditado.", 20, 5),
        Q("Qual valor é essencial para o auditor?", "Integridade", "Ambição", "Descontração",
          "Integridade é fundamental para a confiança no trabalho do auditor.", 15, 5),
        Q("Qual situação representa ameaça à independência?",
          "Ter participação acionária no cliente", "Fazer o curso da mesma firma", "Participar de um evento de networking",
          "Interesse financeiro direto no cliente é uma ameaça de interesse próprio e, em regra, impede o auditor de atuar.", 20, 5),
        Q("O auditor pode divulgar informações do cliente a terceiros?",
          "Não, salvo autorização ou obrigação legal/profissional", "Sim, se forem públicas na internet",
          "Sim, para colegas de outras firmas",
          "O dever de confidencialidade só cede com autorização do cliente ou dever legal ou profissional de divulgar.", 20, 5),
    ],
    "Contabilidade": [
        Q("O que é ativo?", "Bem ou direito controlado pela empresa", "Despesa", "Obrigação",
          "Ativo é um recurso controlado pela empresa, capaz de gerar benefícios futuros.", 20, 5),
        Q("Qual demonstração apresenta o resultado do exercício?", "DRE", "Balanço Patrimonial", "DFC",
          "A Demonstração do Resultado do Exercício (DRE) mostra o lucro ou prejuízo do período.", 15, 5),
        Q("Qual é a equação patrimonial básica?", "Ativo = Passivo + Patrimônio Líquido",
          "Ativo = Receita − Despesa", "Passivo = Ativo + Patrimônio Líquido",
          "Tudo o que a empresa tem (ativo) é financiado por terceiros (passivo) ou pelos sócios (patrimônio líquido).", 20, 5),
        Q("Qual conta normalmente tem saldo devedor?", "Caixa", "Fornecedores", "Capital Social",
          "Contas de ativo (como Caixa) e de despesa têm saldo devedor. Passivo, patrimônio líquido e receita têm saldo credor.", 18, 5),
    ],
    "IFRS": [
        Q("O que significa IFRS?", "International Financial Reporting Standards",
          "Internal Financial Review System", "International Fiscal Regulation Service",
          "IFRS são as Normas Internacionais de Relatório Financeiro, emitidas pelo IASB.", 15, 5),
        Q("No Brasil, quem emite os pronunciamentos técnicos alinhados às IFRS?",
          "O Comitê de Pronunciamentos Contábeis (CPC)", "A Receita Federal", "O Banco Central",
          "O CPC emite os pronunciamentos (CPCs), que depois são endossados por reguladores como CVM e CFC.", 20, 5),
        Q("Qual IFRS trata de combinações de negócios?", "IFRS 3", "IFRS 8", "IFRS 5",
          "IFRS 3 trata de combinações de negócios. IFRS 8 trata de segmentos operacionais e IFRS 5, de ativos mantidos para venda.", 20, 5),
        Q("Pela IFRS 16, o arrendatário reconhece em geral:",
          "Um ativo de direito de uso e um passivo de arrendamento", "Apenas despesa de aluguel", "Somente um passivo",
          "A IFRS 16 trouxe para o balanço quase todos os arrendamentos, com ativo de direito de uso e passivo de arrendamento.", 20, 5),
    ],
    "Amostragem": [
        Q("Quando usar amostragem?", "Quando a população é grande", "Quando há poucos itens", "Nunca",
          "Amostragem é usada quando não é viável testar toda a população.", 15, 5),
        Q("O que é risco de amostragem?",
          "Concluir diferente do que a população inteira mostraria", "Selecionar a amostra errada", "Perder os documentos",
          "É o risco de a amostra não ser representativa da população.", 22, 5, "Cálculo de Amostra Estatística"),
        Q("Qual alteração AUMENTA o tamanho da amostra necessária?",
          "Aumento do risco avaliado de distorção relevante", "Aumento do erro tolerável", "Redução da variabilidade da população",
          "Quanto maior o risco avaliado, mais evidência é necessária. Maior erro tolerável ou população mais homogênea permitem amostras menores.", 20, 5),
        Q("Você encontrou 2 erros na amostra. O que fazer?",
          "Projetar os erros para a população e avaliar o efeito", "Corrigir os 2 e seguir adiante", "Aumentar os honorários",
          "A distorção na amostra deve ser projetada para a população para avaliar se ela excede o erro tolerável.", 20, 5),
    ],
    "Fraudes": [
        Q("O que é fraude contábil?", "Manipulação intencional de registros", "Erro não intencional", "Auditoria interna",
          "Fraude é a manipulação intencional de registros para enganar usuários das demonstrações.", 20, 5),
        Q("Qual é um sinal comum de fraude?", "Documentos alterados", "Equipe motivada", "Processos automatizados",
          "Documentos alterados ou inconsistentes podem indicar fraude.", 15, 5),
        Q("O que compõe o triângulo da fraude?", "Pressão, oportunidade e racionalização",
          "Dolo, culpa e negligência", "Risco, controle e monitoramento",
          "O triângulo de Cressey explica a fraude: alguém sob pressão, com oportunidade e capaz de racionalizar o ato.", 20, 5),
        Q("Quem tem a responsabilidade primária de prevenir e detectar fraudes?",
          "A administração e os responsáveis pela governança", "Exclusivamente o auditor externo", "Os órgãos reguladores",
          "O auditor obtém segurança razoável sobre distorções por fraude, mas a prevenção e a detecção são responsabilidades da administração.", 20, 5),
    ],
    "Comunicação": [
        Q("Por que a comunicação é importante na auditoria?", "Facilita entendimento e evita erros",
          "Aumenta o tempo de trabalho", "Reduz custos",
          "Comunicação clara facilita o entendimento e evita erros na auditoria.", 20, 5),
        Q("Como o auditor deve se comunicar com o cliente?", "De forma clara e objetiva",
          "Com termos técnicos apenas", "De maneira informal",
          "O auditor deve se comunicar de forma clara, objetiva e profissional.", 15, 5),
        Q("Ao identificar uma deficiência significativa de controle interno, o auditor deve:",
          "Comunicar por escrito à administração e aos responsáveis pela governança",
          "Comunicar só verbalmente ao analista", "Não comunicar, para evitar conflito",
          "Deficiências significativas devem ser comunicadas por escrito em tempo hábil.", 20, 5),
        Q("Qual prática melhora reuniões com o cliente?",
          "Resumir os pontos acordados e formalizar por e-mail", "Evitar registrar o que foi combinado",
          "Falar o máximo possível para impor o ritmo",
          "Formalizar combinados evita mal-entendidos e cria trilha documental.", 15, 5),
    ],
}

# Prova CRC: sorteia 5 do banco abaixo
CRC_QUESTIONS = [
    Q("Qual o objetivo principal da auditoria das demonstrações contábeis?",
      "Expressar uma opinião sobre a conformidade", "Encontrar todas as fraudes", "Garantir o lucro da empresa",
      "O auditor expressa opinião sobre se as demonstrações estão apresentadas adequadamente, em todos os aspectos relevantes."),
    Q("O que significa o princípio da competência?",
      "Registrar transações quando ocorrem", "Registrar quando o dinheiro entra/sai", "Registrar apenas despesas",
      "Pelo regime de competência, receitas e despesas são reconhecidas no período em que ocorrem, independentemente do caixa."),
    Q("Qual destes é um teste de controle?",
      "Observar a contagem de estoque pelo cliente", "Confirmar saldo com um banco", "Recalcular a depreciação",
      "Observar a execução de um controle é teste de controle. Confirmação e recálculo são procedimentos substantivos."),
    Q("O que é materialidade em auditoria?",
      "A importância de uma informação que influenciaria decisões", "O material usado no escritório",
      "A quantidade de papéis de trabalho",
      "Uma informação é relevante se sua omissão ou distorção puder influenciar decisões dos usuários."),
    Q("Quem é o responsável pela elaboração das demonstrações contábeis?",
      "A administração da empresa", "O auditor externo", "O conselho fiscal",
      "A administração elabora as demonstrações; o auditor opina sobre elas."),
    Q("Qual opinião o auditor emite quando as demonstrações estão livres de distorções relevantes?",
      "Opinião sem modificação", "Opinião adversa", "Abstenção de opinião",
      "Sem distorções relevantes, a opinião é não modificada (antes chamada de 'limpa')."),
    Q("Qual norma brasileira trata de materialidade no planejamento e na execução da auditoria?",
      "NBC TA 320", "NBC TA 700", "NBC TA 530",
      "A NBC TA 320 trata de materialidade. A 700 trata do relatório e a 530, de amostragem."),
    Q("Qual componente do risco de auditoria o auditor NÃO controla?",
      "Risco inerente", "Risco de detecção", "Risco de amostragem",
      "O risco inerente existe independentemente da auditoria. O auditor ajusta o risco de detecção com a natureza, a época e a extensão dos procedimentos."),
    Q("Qual procedimento é mais adequado para obter evidência sobre a existência de contas a receber?",
      "Confirmação externa com os clientes", "Recálculo da depreciação", "Leitura da ata de assembleia",
      "A confirmação externa é evidência de fonte independente e muito confiável para existência de recebíveis."),
    Q("O que são eventos subsequentes?",
      "Eventos entre a data do balanço e a data do relatório do auditor",
      "Eventos futuros planejados pela empresa", "Eventos ocorridos só no exercício seguinte, sem relação com o balanço",
      "O auditor avalia se eventos entre a data do balanço e a data do relatório exigem ajuste ou divulgação."),
    Q("O que significa o pressuposto de continuidade operacional (going concern)?",
      "Que a entidade continuará em operação no futuro previsível", "Que a entidade nunca terá prejuízo",
      "Que a entidade será vendida em breve",
      "As demonstrações são preparadas supondo que a entidade seguirá operando, salvo intenção ou necessidade de liquidação."),
    Q("Qual é um procedimento analítico?",
      "Comparar a margem bruta com a do ano anterior e investigar variações", "Contar fisicamente o estoque",
      "Confirmar saldos com bancos",
      "Procedimentos analíticos avaliam informações financeiras por meio de relações plausíveis entre dados."),
    Q("Qual é a responsabilidade do auditor em relação à fraude?",
      "Obter segurança razoável de que não há distorção relevante causada por fraude ou erro",
      "Garantir que nenhuma fraude ocorreu", "Investigar fraudes como se fosse a polícia",
      "A auditoria fornece segurança razoável, não absoluta. Há limitações inerentes, especialmente com conluio."),
    Q("Durante quanto tempo o ceticismo profissional deve ser mantido?",
      "Ao longo de toda a auditoria", "Apenas na fase de planejamento", "Só quando há suspeita de fraude",
      "O ceticismo profissional é uma postura contínua, do planejamento à emissão do relatório."),
    Q("Qual opinião é cabível quando há distorção relevante, mas não generalizada?",
      "Opinião com ressalva", "Opinião adversa", "Opinião sem modificação",
      "Distorção relevante e não generalizada resulta em opinião com ressalva."),
]

# ---------------------------------------------------------------------------
# Walkthroughs (passos na ordem correta; o jogo embaralha)
# ---------------------------------------------------------------------------
WALKTHROUGH_GAMES = {
    "compras": {
        "title": "Walkthrough: Processo de Compras",
        "description": "Um assistente do cliente descreveu o processo de compras. Coloque os passos na ordem correta para validar seu entendimento.",
        "steps": [
            "A área solicitante abre uma Ordem de Compra (PO) no sistema.",
            "O gestor da área aprova a Ordem de Compra.",
            "A equipe de Compras realiza três cotações com fornecedores.",
            "O produto é recebido e a nota fiscal é lançada no sistema.",
        ],
        "reward": {"xp": 35, "credibility": 10, "evidence": "Mapeamento do Processo de Compras"},
        "penalty": {"credibility": -15, "xp": -5},
    },
    "vendas": {
        "title": "Walkthrough: Ciclo de Vendas",
        "description": "O time comercial explicou como uma venda acontece. Ordene as etapas para confirmar seu entendimento do fluxo.",
        "steps": [
            "O cliente envia o pedido de venda.",
            "A área de crédito analisa e aprova o limite do cliente.",
            "O estoque é separado e a mercadoria é expedida com nota fiscal.",
            "A venda é contabilizada e o recebimento é conciliado.",
        ],
        "reward": {"xp": 35, "credibility": 10, "evidence": "Mapeamento do Ciclo de Vendas"},
        "penalty": {"credibility": -15, "xp": -5},
    },
    "fechamento": {
        "title": "Walkthrough: Fechamento Contábil",
        "description": "A controladoria descreveu o fechamento mensal. Coloque as etapas na ordem em que acontecem.",
        "steps": [
            "As contas são conciliadas e os lançamentos de ajuste são preparados.",
            "O gerente revisa e aprova os lançamentos manuais.",
            "O período contábil é bloqueado no sistema.",
            "As demonstrações são geradas e revisadas pela diretoria.",
        ],
        "reward": {"xp": 40, "credibility": 12, "evidence": "Mapeamento do Fechamento Contábil"},
        "penalty": {"credibility": -15, "xp": -5},
    },
}

# Itens possíveis no minigame de inventário (nome, faixa de quantidade no sistema)
INVENTORY_ITEMS = [
    ("Notebooks", 100, 200), ("Monitores", 150, 250), ("Teclados", 250, 350),
    ("Mouses", 250, 350), ("Headsets", 80, 160), ("Cadeiras", 40, 120),
    ("Impressoras", 10, 40),
]

# ---------------------------------------------------------------------------
# Eventos
# ---------------------------------------------------------------------------
GAME_EVENTS = [
    {"title": "Café com o Sócio",
     "description": "Você encontra um sócio na copa. Ele oferece um conselho.",
     "options": [{"text": "Ouvir atentamente", "effect": {"credibility": 15, "xp": 10},
                  "feedback": "O sócio gostou da sua atenção e você ganhou credibilidade e XP."}]},
    {"title": "Revisão do Sócio",
     "description": "O sócio da auditoria chegou de surpresa para revisar seus papéis de trabalho. Seus documentos precisam estar impecáveis.",
     "options": [
         {"text": "Apresentar o trabalho com confiança",
          "condition": lambda p: len(p["evidence"]) >= 3,
          "success": {"effect": {"credibility": 20, "xp": 15},
                      "feedback": "O sócio ficou impressionado com a qualidade e organização do seu trabalho. Você ganhou muita credibilidade!"},
          "failure": {"effect": {"credibility": -15},
                      "feedback": "O sócio encontrou falhas na sua documentação e questionou sua preparação. Você perdeu credibilidade."}},
         {"text": "Tentar enrolar e focar nos pontos positivos", "effect": {"credibility": -25, "xp": -10},
          "feedback": "O sócio percebeu sua tentativa de desviar o foco e fez perguntas difíceis que você não soube responder. Grande perda de credibilidade."}]},
    {"title": "Happy Hour da Firma",
     "description": "É o happy hour semanal. Uma ótima chance para socializar, mas cuidado com o que você fala.",
     "options": [
         {"text": "Fazer networking com o Sênior/Gerente", "effect": {"xp": 10, "credibility": 10},
          "feedback": "Você tem uma conversa produtiva sobre o projeto e carreira. Sua proatividade foi notada."},
         {"text": "Desabafar sobre o cliente com os colegas", "effect": {"credibility": -10},
          "feedback": "A conversa foi um alívio, mas um gerente ouviu parte da reclamação. Sua postura foi questionada."},
         {"text": "Aproveitar para relaxar e conhecer a equipe", "effect": {"credibility": 5},
          "feedback": "Você fortaleceu os laços com a equipe, o que melhora o ambiente de trabalho."}]},
    {"title": "WCGW Identificado!",
     "description": 'Você identificou um "What Could Go Wrong" (WCGW) no processo de compras do cliente: faturas podem ser pagas em duplicidade. O que você faz?',
     "options": [
         {"text": "Desenvolver um teste substantivo para pagamentos",
          "effect": {"xp": 20, "credibility": 10, "evidence": "Teste de Pagamentos em Duplicidade"},
          "feedback": "Excelente! Você aplicou o conceito de WCGW para planejar um procedimento de auditoria eficaz."},
         {"text": "Confiar que o controle de aprovação do gerente pega tudo", "effect": {"credibility": -15},
          "feedback": "Confiar apenas em um controle sem testá-lo diretamente para o risco identificado é arriscado. Você perdeu credibilidade."}]},
    {"title": "WCGW Identificado!",
     "description": 'WCGW no ciclo de estoques: itens obsoletos podem continuar no saldo sem provisão para perda. O que você faz?',
     "options": [
         {"text": "Testar a provisão de obsolescência com base no aging do estoque",
          "effect": {"xp": 20, "credibility": 10, "evidence": "Teste de Obsolescência de Estoque"},
          "feedback": "Muito bem! Você ligou o risco a um procedimento específico sobre a avaliação do estoque."},
         {"text": "Aceitar a estimativa da administração sem questionar", "effect": {"credibility": -15},
          "feedback": "Estimativas contábeis exigem avaliação crítica. Aceitar sem testar custou credibilidade."}]},
    {"title": "WCGW Identificado!",
     "description": 'WCGW no ciclo de vendas: vendas podem ser registradas antes da entrega ao cliente. O que você faz?',
     "options": [
         {"text": "Executar teste de corte nas últimas e primeiras vendas do período",
          "effect": {"xp": 20, "credibility": 10, "evidence": "Teste de Corte de Vendas"},
          "feedback": "Boa! O teste de corte endereça diretamente o risco de reconhecimento no período errado."},
         {"text": "Confiar no relatório de vendas gerado pelo cliente sem validá-lo", "effect": {"credibility": -15},
          "feedback": "Relatórios do cliente precisam ter completude e acurácia validadas antes de servir de base."}]},
    {"title": "Pausa para o Café",
     "description": "Você faz uma pausa para um café e encontra um colega que te dá uma dica valiosa sobre o projeto.",
     "options": [{"text": "Agradecer a dica", "effect": {"xp": 10, "credibility": 5},
                  "feedback": "A dica foi útil e você aplicou no seu trabalho, ganhando XP e credibilidade."}]},
    {"title": "Mentoria com Sênior",
     "description": "Um sênior te chama para conversar sobre sua carreira e oferece um conselho.",
     "options": [
         {"text": "Pedir feedback sobre seu trabalho", "effect": {"xp": 15, "credibility": 10},
          "feedback": "O sênior apreciou sua proatividade em buscar desenvolvimento e te deu um feedback construtivo."},
         {"text": "Apenas ouvir", "effect": {"xp": 5, "credibility": 5},
          "feedback": "Você ouviu atentamente e aprendeu com a experiência do sênior."}]},
]

TRAVEL_EVENTS = [
    {"title": "Voo Atrasado",
     "content": "Seu voo atrasou e você chegou exausto ao cliente. Você ficará uma rodada sem jogar para se recuperar."},
    {"title": "Hotel sem energia",
     "content": "O hotel ficou sem energia e você não conseguiu preparar os papéis de trabalho. Você ficará uma rodada sem jogar."},
    {"title": "Bagagem extraviada",
     "content": "Sua mala com o notebook de reserva foi extraviada. Você perde um tempo precioso e ficará uma rodada sem jogar."},
]

CLIENT_SCENARIOS = [
    {"type": "Agressivo", "title": "Cliente Agressivo",
     "description": "O CFO do cliente está pressionando por respostas rápidas e quer que você ignore certos procedimentos para acelerar o fechamento.",
     "options": [
         {"text": "Manter postura profissional e explicar a necessidade dos procedimentos",
          "effect": {"credibility": 15, "xp": 10},
          "feedback": "Você manteve a postura, demonstrou independência e ganhou credibilidade."},
         {"text": "Ceder à pressão para não criar atrito", "effect": {"credibility": -15},
          "feedback": "Você cedeu à pressão, comprometendo a qualidade da auditoria e perdendo credibilidade."}]},
    {"type": "Agressivo", "title": "Cliente Agressivo",
     "description": "O gerente financeiro liga às 22h cobrando um 'ok' prévio sobre a opinião, antes de você concluir os testes.",
     "options": [
         {"text": "Explicar que a conclusão depende de evidência suficiente e acionar o sócio sobre o prazo",
          "effect": {"credibility": 15, "xp": 10},
          "feedback": "Você protegeu a independência e envolveu a pessoa certa. Credibilidade em alta."},
         {"text": "Dar um 'sinal verde' informal para acalmar o cliente", "effect": {"credibility": -20},
          "feedback": "Antecipar conclusões sem evidência comprometeu a auditoria."}]},
    {"type": "Colaborativo", "title": "Cliente Colaborativo",
     "description": "A equipe do cliente está disposta a ajudar e já separou todos os documentos que você pediu.",
     "options": [
         {"text": "Agradecer e aproveitar para aprofundar os testes", "effect": {"credibility": 5, "xp": 10},
          "feedback": "Você aproveitou a boa relação para fazer um trabalho ainda melhor. Ganhou XP e credibilidade."},
         {"text": "Aceitar tudo sem questionar", "effect": {"credibility": -5},
          "feedback": "Mesmo com um cliente colaborativo, o ceticismo profissional não pode ser abandonado. Você perdeu uma oportunidade de aprofundar a análise."}]},
    {"type": "Colaborativo", "title": "Cliente Colaborativo",
     "description": "O cliente oferece acesso direto ao ERP para você extrair os dados que precisa.",
     "options": [
         {"text": "Aceitar e validar a completude e a integridade dos dados extraídos",
          "effect": {"credibility": 8, "xp": 15},
          "feedback": "Acesso ágil, mas com validação. Exatamente como deve ser."},
         {"text": "Usar os relatórios sem validar a origem", "effect": {"credibility": -10},
          "feedback": "Dados sem validação de completude e acurácia não servem como evidência confiável."}]},
    {"type": "Exigente", "title": "Cliente Exigente",
     "description": "O cliente questiona cada item da sua solicitação de documentos, pedindo justificativas detalhadas para tudo.",
     "options": [
         {"text": "Explicar pacientemente a relevância de cada documento para a auditoria",
          "effect": {"credibility": 10, "xp": 5},
          "feedback": "Sua comunicação clara e profissional fortaleceu a confiança do cliente no processo."},
         {"text": "Ficar irritado e responder de forma genérica", "effect": {"credibility": -10},
          "feedback": "A falta de paciência gerou um atrito desnecessário e prejudicou a relação com o cliente."}]},
    {"type": "Exigente", "title": "Cliente Exigente",
     "description": "O cliente pede para revisar seus papéis de trabalho antes de você finalizar.",
     "options": [
         {"text": "Explicar que os papéis pertencem ao auditor e compartilhar apenas o necessário",
          "effect": {"credibility": 10, "xp": 5},
          "feedback": "Você preservou a propriedade e a confidencialidade dos papéis sem criar atrito."},
         {"text": "Entregar todos os papéis para evitar discussão", "effect": {"credibility": -12},
          "feedback": "Entregar a documentação inteira expôs informações que não deveriam ser compartilhadas."}]},
]

# Efeitos podem usar: xp, credibility, credits, hours
SABOTAGE_EVENTS = [
    {"description": "O Zeca Urubu 'acidentalmente' derramou café no seu notebook! Você perde 100 créditos para o conserto.",
     "effect": {"player": {"credits": -100}},
     "feedback": "Você perdeu C$100 porque esqueceu de pedir reembolso."},
    {"description": "O Zeca Urubu questionou seu trabalho na frente do gerente. Você precisa responder uma pergunta extra para provar seu conhecimento.",
     "action": "extra_question",
     "feedback": "Zeca Urubu te colocou numa saia justa!"},
    {"description": "Zeca Urubu 'pegou os créditos' por uma análise complexa que você fez. Ele ganha 15 XP e você perde 15 XP.",
     "effect": {"player": {"xp": -15}, "npc": {"xp": 15}},
     "feedback": "Zeca Urubu levou a fama pelo seu trabalho! Você perdeu 15 XP."},
    {"description": "Na tentativa de 'ajudar' a organizar, Zeca Urubu escondeu um dos seus papéis de trabalho. Você perde uma evidência coletada.",
     "action": "lose_evidence",
     "feedback": "Sua evidência sumiu! A 'organização' do Zeca Urubu te custou caro."},
    {"description": "Zeca Urubu espalhou um boato de que você está com dificuldades no projeto. Sua credibilidade foi abalada.",
     "effect": {"player": {"credibility": -10}},
     "feedback": "Um boato malicioso te fez perder 10 de credibilidade. Obra do Zeca Urubu!"},
    {"description": "Zeca Urubu marcou uma call longa com o cliente bem no seu horário de foco. Você perde 4 horas de trabalho.",
     "effect": {"player": {"hours": -4}},
     "feedback": "Zeca Urubu consumiu 4 horas do seu dia com uma reunião 'urgente'."},
    {"description": "Zeca Urubu 'esqueceu' de repassar o e-mail do gerente com o novo escopo. Você parece desatualizado.",
     "effect": {"player": {"credibility": -8}},
     "feedback": "Falta de informação custou 8 de credibilidade. Obra do Zeca Urubu!"},
]

COURSE_CONTENT = {
    "Ética": "A ética profissional é a base da confiança na auditoria. O auditor deve manter independência, integridade e objetividade.",
    "Contabilidade": "A contabilidade é a linguagem dos negócios. Um auditor precisa dominá-la para identificar distorções relevantes.",
    "IFRS": "As Normas Internacionais de Relatório Financeiro (IFRS) são o padrão global para demonstrações contábeis.",
    "Amostragem": "A amostragem permite ao auditor obter evidências sobre uma população a partir de uma amostra representativa.",
    "Fraudes": "O curso de fraudes aborda a identificação de sinais e a investigação de transações suspeitas.",
    "Comunicação": "Comunicação eficaz é chave para o sucesso do auditor na interação com clientes e equipe.",
}

RULES_MD = """
**Objetivo:** chegar à casa **Promoção!** e passar na **Prova CRC** antes do Zeca Urubu.

**Turno:** jogue o dado (1–6) ou tome um café. Cada jogada gasta **4h**; com menos de 4h você perde o turno
(e as horas voltam a 8). Café custa C$50, devolve 2h e dá 10 XP, e não gasta o turno.

**Credibilidade 🏆** e **XP 💡** sobem com acertos, eventos bons e cursos. Erros, penalidades e
sabotagens fazem os dois caírem (nunca abaixo de zero).

**Busy Season 🔥:** entre as semanas 6 e 14 pode começar uma temporada de 5 turnos em que
recompensas, penalidades e custos são **dobrados**.

**Firmas:** Big Blue (+20 cred.), Big Green (+C$500), Big Orange (−20% em cursos),
Big Yellow (−50% de perda de credibilidade por erros).

**Zeca Urubu 🦅** joga depois de você. Se ele cair na sua casa, ele te sabota.
"""
