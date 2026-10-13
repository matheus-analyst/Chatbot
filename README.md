# 🦷 Sistema de Agendamento – Clínica Odontológica

Sistema simples de agendamento para clínica odontológica, desenvolvido em **Python** e rodando diretamente no **Spck Editor (Android)**, **PyDroid3 (Android)** e em qualquer ambiente Python 3.

Ele gerencia:

- ✅ Cadastro de clientes  
- ✅ Cadastro de profissionais (dentistas) com horários de atendimento  
- ✅ Agendamento de consultas (segunda a sexta em horário comercial e sábado até 14:00)  
- ✅ Visualização, cancelamento e relatórios de agendamentos  
- ✅ Exportação de relatório diário em arquivo `.txt`

**Arquivo principal:** `main.py`  
**Repositório:** https://github.com/matheus-analyst/Chatbot.git

---

## 🚀 Como usar no Spck Editor (Android)

### Requisitos

- Aplicativo **Spck Editor** instalado no Android  
- Python 3 configurado no Spck (o próprio app já oferece um ambiente Python)  
- Permissão para escrever arquivos na pasta do projeto

### Passos

1. Clone ou baixe este repositório no seu dispositivo.  
2. Abra o **Spck Editor**.  
3. Abra a pasta do projeto (onde está o `main.py`).  
4. Execute o arquivo `main.py` pelo Spck (botão de “Run”/“Play”).  

Na primeira execução, o programa vai criar automaticamente:

- `clientes.json`  
- `profissionais.json`  
- `agendamentos.json`

Esses arquivos funcionam como “banco de dados” local.

---

## 📱 Como usar no PyDroid3 (Android)

### Requisitos

- Aplicativo **PyDroid3** instalado no Android  
- Python 3 (já incluso no PyDroid3)  
- Permissão para escrever arquivos na pasta do projeto

### Passos

1. Clone ou baixe este repositório no seu dispositivo.  
2. Abra o **PyDroid3**.  
3. Crie um novo arquivo Python ou abra o `main.py` dentro da pasta do projeto.  
4. Execute o script (botão de “Play” no PyDroid3).  

Na primeira execução, o programa vai criar automaticamente:

- `clientes.json`  
- `profissionais.json`  
- `agendamentos.json`

Esses arquivos funcionam como “banco de dados” local.

---

## 💻 Como usar via terminal (PC / Linux / macOS / Android com terminal Python)

### Requisitos

- Python 3 instalado  
- Terminal / prompt de comando

### Passos

1. Clone o repositório:

```bash
git clone [https://github.com/matheus-analyst/Chatbot.git](https://github.com/matheus-analyst/Chatbot.git)
cd Chatbot