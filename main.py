import json
import time
from datetime import datetime, timedelta

ARQUIVO_AGENDAS = "agendamentos.json"
ARQUIVO_PROFISSIONAIS = "profissionais.json"
ARQUIVO_CLIENTES = "clientes.json"

# --- Funções de arquivo ---
def carregar_json(nome_arquivo, padrao):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, list):
                return dados
            return padrao
    except FileNotFoundError:
        salvar_json(nome_arquivo, padrao)
        return padrao
    except json.JSONDecodeError:
        return padrao

def salvar_json(nome_arquivo, dados):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_agendamentos():
    return carregar_json(ARQUIVO_AGENDAS, [])

def salvar_agendamentos(agendamentos):
    salvar_json(ARQUIVO_AGENDAS, agendamentos)

def carregar_profissionais():
    padrao = [
        {
            "nome": "Dra. Ana",
            "horarios": {
                "segunda": {"inicio": "08:00", "fim": "18:00"},
                "terca":   {"inicio": "08:00", "fim": "18:00"},
                "quarta":  {"inicio": "08:00", "fim": "18:00"},
                "quinta":  {"inicio": "08:00", "fim": "18:00"},
                "sexta":   {"inicio": "08:00", "fim": "18:00"},
                "sabado":  {"inicio": "08:00", "fim": "14:00"}
            },
            "duracao_minutos": 30
        },
        {
            "nome": "Dr. Bruno",
            "horarios": {
                "segunda": {"inicio": "09:00", "fim": "19:00"},
                "terca":   {"inicio": "09:00", "fim": "19:00"},
                "quarta":  {"inicio": "09:00", "fim": "19:00"},
                "quinta":  {"inicio": "09:00", "fim": "19:00"},
                "sexta":   {"inicio": "09:00", "fim": "17:00"},
                "sabado":  {"inicio": "08:00", "fim": "14:00"}
            },
            "duracao_minutos": 30
        },
        {
            "nome": "Dra. Carla",
            "horarios": {
                "segunda": {"inicio": "07:00", "fim": "15:00"},
                "terca":   {"inicio": "13:00", "fim": "21:00"},
                "quarta":  {"inicio": "07:00", "fim": "15:00"},
                "quinta":  {"inicio": "13:00", "fim": "21:00"},
                "sexta":   {"inicio": "07:00", "fim": "15:00"},
                "sabado":  {"inicio": "08:00", "fim": "14:00"}
            },
            "duracao_minutos": 30
        }
    ]
    return carregar_json(ARQUIVO_PROFISSIONAIS, padrao)

def salvar_profissionais(profissionais):
    salvar_json(ARQUIVO_PROFISSIONAIS, profissionais)

def carregar_clientes():
    return carregar_json(ARQUIVO_CLIENTES, [])

def salvar_clientes(clientes):
    salvar_json(ARQUIVO_CLIENTES, clientes)

# --- Data/hora ---
def validar_data(data_str):
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
        return dt
    except ValueError:
        return None

def validar_hora(hora_str):
    try:
        return datetime.strptime(hora_str, "%H:%M")
    except ValueError:
        return None

def dia_semana_em_portugues(dt: datetime) -> str:
    dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    return dias[dt.weekday()]

def gerar_horarios_disponiveis(prof, data_str):
    dt = validar_data(data_str)
    if not dt:
        return []

    dia = dia_semana_em_portugues(dt)

    if dia == "domingo":
        return []

    horarios_dia = prof.get("horarios", {}).get(dia)
    if not horarios_dia:
        return []

    inicio_str = horarios_dia.get("inicio")
    fim_str = horarios_dia.get("fim")
    duracao = prof.get("duracao_minutos", 30)

    if not inicio_str or not fim_str:
        return []

    inicio = validar_hora(inicio_str)
    fim = validar_hora(fim_str)
    if not inicio or not fim:
        return []

    slots = []
    atual = inicio
    while atual + timedelta(minutes=duracao) <= fim:
        hora_str = atual.strftime("%H:%M")
        slots.append(hora_str)
        atual += timedelta(minutes=duracao)

    # Remove horários já ocupados nesse dia para esse profissional
    agendamentos = carregar_agendamentos()
    ocupados = set()
    for ag in agendamentos:
        if not isinstance(ag, dict):
            continue
        if ag.get("profissional") == prof["nome"] and ag.get("data") == data_str:
            ocupados.add(ag.get("hora"))

    disponiveis = [h for h in slots if h not in ocupados]
    return disponiveis

# --- Máscaras ---
def mascarar_codigo(codigo: str) -> str:
    if not codigo:
        return "Sem código"
    if len(codigo) <= 6:
        return codigo[:2] + "***"
    return codigo[:3] + "***" + codigo[-3:]

def mascarar_telefone(tel: str) -> str:
    if not tel:
        return "Sem telefone"
    tel = tel.strip()
    if len(tel) <= 4:
        return tel[:2] + "**"
    return tel[:2] + "**" + tel[-2:]

# --- Simulação de "digitando..." ---
def digitar(mensagem, atraso=0.02):
    for char in mensagem:
        print(char, end="", flush=True)
        time.sleep(atraso)
    print()

def responder_bot(texto):
    time.sleep(0.3)
    print("Bot: ", end="")
    digitar(texto)

# --- Cliente: buscar ou cadastrar ---
def buscar_cliente_por_codigo(codigo):
    clientes = carregar_clientes()
    for c in clientes:
        if not isinstance(c, dict):
            continue
        if c.get("codigo", "").strip().lower() == codigo.strip().lower():
            return c
    return None

def cadastrar_novo_cliente():
    responder_bot("Vamos cadastrar a cliente. Qual é o NOME COMPLETO?")
    nome = input("Você: ").strip()
    if not nome:
        responder_bot("Preciso do nome.")
        return None

    responder_bot("Digite um CÓDIGO (CPF, telefone, etc.) para identificar a cliente.")
    codigo = input("Você: ").strip()
    if not codigo:
        responder_bot("Preciso do código.")
        return None

    # Verifica se já existe
    existente = buscar_cliente_por_codigo(codigo)
    if existente:
        responder_bot(
            f"Já existe uma cliente cadastrada com esse código:"

            f"  Nome: {existente['nome']}"

            f"  Código: {mascarar_codigo(existente['codigo'])}"

            f"  Telefone: {mascarar_telefone(existente['telefone'])}"

            f"  E-mail: {existente.get('email', '(não informado)')}"
        )
        responder_bot("Quer usar essa cliente mesmo assim? (s/n)")
        conf = input("Você: ").strip().lower()
        if conf == "s":
            return existente
        else:
            responder_bot("Então digite outro código.")
            return cadastrar_novo_cliente()

    responder_bot("Digite o TELEFONE (com DDD, só números).")
    telefone = input("Você: ").strip()
    if not telefone:
        responder_bot("Preciso do telefone.")
        return None

    responder_bot("Digite o E-MAIL (opcional).")
    email = input("Você: ").strip()

    cliente = {
        "nome": nome,
        "codigo": codigo,
        "telefone": telefone,
        "email": email
    }

    # Salva na base de clientes
    clientes = carregar_clientes()
    clientes.append(cliente)
    salvar_clientes(clientes)

    responder_bot("Cliente cadastrada com sucesso!")
    return cliente

def obter_cliente_para_agendamento():
    responder_bot("A cliente já é cadastrada na clínica? (s/n)")
    resp = input("Você: ").strip().lower()

    if resp == "s":
        responder_bot("Digite o CÓDIGO da cliente (CPF, telefone, etc.).")
        codigo = input("Você: ").strip()
        if not codigo:
            responder_bot("Preciso do código.")
            return None

        cliente = buscar_cliente_por_codigo(codigo)
        if not cliente:
            responder_bot(
                f"Nenhuma cliente encontrada com o código '{mascarar_codigo(codigo)}'. "
                "Vamos cadastrar como nova cliente."
            )
            return cadastrar_novo_cliente()

        responder_bot(
            f"Cliente encontrada:"

            f"  Nome: {cliente['nome']}"

            f"  Código: {mascarar_codigo(cliente['codigo'])}"

            f"  Telefone: {mascarar_telefone(cliente['telefone'])}"

            f"  E-mail: {cliente.get('email', '(não informado)')}"
        )
        return cliente
    else:
        # Nova cliente
        return cadastrar_novo_cliente()

# --- Listar profissionais ---
def listar_profissionais():
    profissionais = carregar_profissionais()
    if not profissionais:
        responder_bot("Nenhum profissional cadastrado.")
        return []

    responder_bot("Profissionais disponíveis:")
    for i, prof in enumerate(profissionais, start=1):
        nome = prof.get("nome", "Sem nome")
        duracao = prof.get("duracao_minutos", 30)
        time.sleep(0.1)
        digitar(f"  {i}. {nome} (consultas de {duracao} minutos)")
    return profissionais

# --- Fluxo de agendamento ---
def fluxo_agendamento():
    # Obter cliente (nova ou existente)
    cliente = obter_cliente_para_agendamento()
    if not cliente:
        responder_bot("Não foi possível identificar/cadastrar a cliente. Agendamento cancelado.")
        return

    # Escolher profissional
    profissionais = listar_profissionais()
    if not profissionais:
        responder_bot("Sem profissionais, não dá pra agendar.")
        return

    responder_bot("Digite o NÚMERO do profissional que a cliente quer.")
    op = input("Você: ").strip()
    if not op.isdigit():
        responder_bot("Opção inválida.")
        return
    idx = int(op)
    if idx < 1 or idx > len(profissionais):
        responder_bot("Esse número não existe.")
        return
    prof = profissionais[idx - 1]

    # Escolher data
    while True:
        responder_bot("Qual a data do agendamento? (DD/MM/AAAA)")
        data = input("Você: ").strip()
        dt = validar_data(data)
        if not dt:
            responder_bot("Data inválida. Usa DD/MM/AAAA.")
            continue

        dia = dia_semana_em_portugues(dt)
        if dia == "domingo":
            responder_bot("Não atendemos aos domingos. Escolhe outra data.")
            continue
        break

    # Mostrar horários disponíveis
    disponiveis = gerar_horarios_disponiveis(prof, data)
    if not disponiveis:
        responder_bot("Não há horários disponíveis nesse dia para esse profissional.")
        return

    responder_bot(f"Horários disponíveis para {prof['nome']} em {data}:")
    for i, h in enumerate(disponiveis, start=1):
        time.sleep(0.05)
        digitar(f"  {i}. {h}")

    while True:
        responder_bot("Digite o NÚMERO do horário desejado.")
        op_h = input("Você: ").strip()
        if not op_h.isdigit():
            responder_bot("Digite só números.")
            continue
        idx_h = int(op_h)
        if idx_h < 1 or idx_h > len(disponiveis):
            responder_bot("Esse número não existe.")
            continue
        hora = disponiveis[idx_h - 1]
        break

    # Serviço
    responder_bot("Qual serviço será realizado? (ex: limpeza, restauração, avaliação)")
    servico = input("Você: ").strip()
    if not servico:
        responder_bot("Preciso do serviço.")
        return

    # Confirmar
    responder_bot(
        f"Confirmar agendamento:"

        f" Clientehttps://github.com/matheus-analyst/Chatbot.git:{cliente['nome']}({mascarar_codigo(cliente['codigo'])})"

        f"  Telefone: {mascarar_telefone(cliente['telefone'])}"

        f"  E-mail: {cliente.get('email', '(não informado)')}"

        f"  Profissional: {prof['nome']}"

        f"  Serviço: {servico}"

        f"  Data: {data} às {hora}"

        f"Confirmar? (s/n)"
    )
    conf = input("Você: ").strip().lower()
    if conf != "s":
        responder_bot("Agendamento cancelado.")
        return

    # Salvar agendamento
    agendamentos = carregar_agendamentos()
    agendamentos.append({
        "nome_cliente": cliente["nome"],
        "codigo_cliente": cliente["codigo"],
        "telefone_cliente": cliente["telefone"],
        "email_cliente": cliente.get("email", ""),
        "profissional": prof["nome"],
        "servico": servico,
        "data": data,
        "hora": hora
    })
    salvar_agendamentos(agendamentos)

    responder_bot(
        f"Agendamento confirmado! {prof['nome']} espera a cliente em {data} às {hora} para {servico}."
    )

# --- Listar todos os agendamentos ---
def listar_agendamentos_geral():
    agendamentos = carregar_agendamentos()
    if not agendamentos:
        responder_bot("Nenhum agendamento registrado ainda.")
        return

    responder_bot("Aqui estão todos os agendamentos:")
    for i, ag in enumerate(agendamentos, start=1):
        if not isinstance(ag, dict):
            continue
        nome = ag.get("nome_cliente", "Sem nome")
        codigo = ag.get("codigo_cliente", "Sem código")
        telefone = ag.get("telefone_cliente", "Sem telefone")
        email = ag.get("email_cliente", "")
        prof = ag.get("profissional", "Sem profissional")
        servico = ag.get("servico", "Sem serviço")
        data = ag.get("data", "??/??/????")
        hora = ag.get("hora", "??:??")
        time.sleep(0.1)
        email_exibicao = email if email else "(sem e-mail)"
        digitar(
            f"  {i}. {data} {hora} - {nome} "
            f"({mascarar_codigo(codigo)}, {mascarar_telefone(telefone)})"

            f"     Profissional: {prof} | Serviço: {servico} | E-mail: {email_exibicao}"
        )

# --- Ver agendamentos de uma cliente (por código) ---
def ver_agendamentos_cliente():
    responder_bot("Digite o CÓDIGO da cliente (CPF, telefone, etc.).")
    codigo = input("Você: ").strip()
    if not codigo:
        responder_bot("Preciso do código.")
        return

    todos = carregar_agendamentos()
    filtrados = [
        ag for ag in todos
        if isinstance(ag, dict) and ag.get("codigo_cliente", "").strip().lower() == codigo.strip().lower()
    ]

    if not filtrados:
        responder_bot(f"Nenhum agendamento encontrado para o código '{mascarar_codigo(codigo)}'.")
        return

    responder_bot(f"Agendamentos da cliente (código {mascarar_codigo(codigo)}):")
    for i, ag in enumerate(filtrados, start=1):
        nome = ag.get("nome_cliente", "Sem nome")
        prof = ag.get("profissional", "Sem profissional")
        servico = ag.get("servico", "Sem serviço")
        data = ag.get("data", "??/??/????")
        hora = ag.get("hora", "??:??")
        time.sleep(0.1)
        digitar(
            f"  {i}. {data} {hora} - {nome}"

            f"     Profissional: {prof} | Serviço: {servico}"
        )

# --- Cancelar agendamento (por código da cliente) ---
def cancelar_agendamento():
    responder_bot("Digite o CÓDIGO da cliente para cancelar.")
    codigo = input("Você: ").strip()
    if not codigo:
        responder_bot("Preciso do código.")
        return

    todos = carregar_agendamentos()
    filtrados = [
        ag for ag in todos
        if isinstance(ag, dict) and ag.get("codigo_cliente", "").strip().lower() == codigo.strip().lower()
    ]

    if not filtrados:
        responder_bot(f"Nenhum agendamento encontrado para o código '{mascarar_codigo(codigo)}'.")
        return

    responder_bot("Agendamentos encontrados:")
    for i, ag in enumerate(filtrados, start=1):
        nome = ag.get("nome_cliente", "Sem nome")
        prof = ag.get("profissional", "Sem profissional")
        servico = ag.get("servico", "Sem serviço")
        data = ag.get("data", "??/??/????")
        hora = ag.get("hora", "??:??")
        time.sleep(0.1)
        digitar(
            f"  {i}. {data} {hora} - {nome}"

            f"     Profissional: {prof} | Serviço: {servico}"
        )

    responder_bot("Digite o NÚMERO do agendamento que quer cancelar (ou 0 para voltar).")
    op = input("Você: ").strip()
    if not op.isdigit():
        responder_bot("Opção inválida.")
        return
    idx = int(op)
    if idx == 0:
        responder_bot("Volta pro menu.")
        return
    if idx < 1 or idx > len(filtrados):
        responder_bot("Esse número não existe.")
        return

    ag_alvo = filtrados[idx - 1]

    indice_real = None
    for i, ag in enumerate(todos):
        if (
            isinstance(ag, dict)
            and ag.get("nome_cliente") == ag_alvo.get("nome_cliente")
            and ag.get("codigo_cliente") == ag_alvo.get("codigo_cliente")
            and ag.get("data") == ag_alvo.get("data")
            and ag.get("hora") == ag_alvo.get("hora")
            and ag.get("profissional") == ag_alvo.get("profissional")
        ):
            indice_real = i
            break

    if indice_real is None:
        responder_bot("Não encontrei esse agendamento na base.")
        return

    responder_bot(
        f"Cancelar: {ag_alvo['data']} {ag_alvo['hora']} - {ag_alvo['nome_cliente']} com {ag_alvo['profissional']}? (s/n)"
    )
    conf = input("Você: ").strip().lower()
    if conf != "s":
        responder_bot("Cancelamento desfeito.")
        return

    todos.pop(indice_real)
    salvar_agendamentos(todos)
    responder_bot("Agendamento cancelado com sucesso!")

# --- Relatório do dia (por data) ---
def relatorio_do_dia():
    while True:
        responder_bot("Qual data você quer ver o relatório? (DD/MM/AAAA)")
        data = input("Você: ").strip()
        dt = validar_data(data)
        if not dt:
            responder_bot("Data inválida. Usa DD/MM/AAAA.")
            continue
        break

    todos = carregar_agendamentos()
    filtrados = [
        ag for ag in todos
        if isinstance(ag, dict) and ag.get("data") == data
    ]

    if not filtrados:
        responder_bot(f"Nenhum agendamento encontrado para {data}.")
        return

    responder_bot(f"Relatório de {data}:")
    for i, ag in enumerate(filtrados, start=1):
        nome = ag.get("nome_cliente", "Sem nome")
        prof = ag.get("profissional", "Sem profissional")
        servico = ag.get("servico", "Sem serviço")
        hora = ag.get("hora", "??:??")
        time.sleep(0.1)
        digitar(
            f"  {i}. {hora} - {nome}"

            f"     Profissional: {prof} | Serviço: {servico}"
        )

    responder_bot("Fim do relatório.")

# --- Exportar relatório do dia ---
def exportar_relatorio_do_dia():
    while True:
        responder_bot("Qual data você quer exportar o relatório? (DD/MM/AAAA)")
        data = input("Você: ").strip()
        dt = validar_data(data)
        if not dt:
            responder_bot("Data inválida. Usa DD/MM/AAAA.")
            continue
        break

    todos = carregar_agendamentos()
    filtrados = [
        ag for ag in todos
        if isinstance(ag, dict) and ag.get("data") == data
    ]

    if not filtrados:
        responder_bot(f"Nenhum agendamento encontrado para {data}.")
        return

    nome_arquivo = "relatorio_" + data.replace("/", "") + ".txt"
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    linhas = []
    linhas.append(f"Relatório de agendamentos - {data}")
    linhas.append(f"Relatório gerado em: {agora}")
    linhas.append("-" * 50)

    for i, ag in enumerate(filtrados, start=1):
        nome = ag.get("nome_cliente", "Sem nome")
        prof = ag.get("profissional", "Sem profissional")
        servico = ag.get("servico", "Sem serviço")
        hora = ag.get("hora", "??:??")
        linha = f"{i}. {hora} - {nome} | Profissional: {prof} | Serviço: {servico}"
        linhas.append(linha)

    linhas.append("-" * 50)
    linhas.append("Fim do relatório.")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("".join(linhas))

    responder_bot(f"Relatório exportado para '{nome_arquivo}'.")

# --- Menu ---
def menu_principal():
    print()
    digitar("Bot: Olá! Sou o assistente de agendamentos da clínica.", 0.02)
    time.sleep(0.2)
    digitar(
        "Bot: Opções:"

        "  1 = Agendar"

        "  2 = Ver todos os agendamentos"

        "  3 = Ver agendamentos de uma cliente"

        "  4 = Cancelar agendamento"

        "  5 = Relatório do dia"

        "  6 = Exportar relatório"

        "  7 = Sair",
        0.02,
    )

    while True:
        op = input("Você: ").strip()
        if op == "1":
            fluxo_agendamento()
        elif op == "2":
            listar_agendamentos_geral()
        elif op == "3":
            ver_agendamentos_cliente()
        elif op == "4":
            cancelar_agendamento()
        elif op == "5":
            relatorio_do_dia()
        elif op == "6":
            exportar_relatorio_do_dia()
        elif op == "7":
            responder_bot("Até mais!")
            break
        else:
            responder_bot("Opção inválida. Usa 1 a 7."
                
                        "  1 = Agendar"

        "  2 = Ver todos os agendamentos"

        "  3 = Ver agendamentos de uma cliente"

        "  4 = Cancelar agendamento"

        "  5 = Relatório do dia"

        "  6 = Exportar relatório"

        "  7 = Sair",
                
            )

if __name__ == "__main__":
    menu_principal()