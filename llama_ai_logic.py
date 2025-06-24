# llama_ai_logic.py

import requests
import json
import re

class LlamaChatbotLogic:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="codellama:7b"):
        self.ollama_url = ollama_url
        self.model_name = model_name

        self.db_schema = """
        CREATE TABLE dados_ifsp (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(50),
            disciplina VARCHAR(255),
            curso VARCHAR(255),
            professor VARCHAR(255),
            horario VARCHAR(100),
            sala VARCHAR(100)
        );
        """

        self.example_sql_instructions = """
        -- Pergunta: "quais disciplinas o professor sovat ministra?"
        -- SQL: SELECT DISTINCT disciplina FROM dados_ifsp WHERE professor LIKE '%sovat%';

        -- Pergunta: "qual a sala da aula de engenharia de software?"
        -- SQL: SELECT DISTINCT sala FROM dados_ifsp WHERE disciplina LIKE '%Engenharia de Software%';

        -- Pergunta: "lista de cursos"
        -- SQL: SELECT DISTINCT curso FROM dados_ifsp ORDER BY curso;

        -- Pergunta: "me mostra todos os professores"
        -- SQL: SELECT DISTINCT professor FROM dados_ifsp ORDER BY professor;

        -- Pergunta: "quais disciplinas tem na sala C201?"
        -- SQL: SELECT DISTINCT disciplina FROM dados_ifsp WHERE sala LIKE '%C201%';

        -- Pergunta: "Quantos alunos tem no IFSP?"
        -- SQL: FORA_DO_ESCOPO
        """

    def prompt(self, user_message):
        message_lower = user_message.lower()

        # Respostas prontas para saudações e despedidas
        if any(saud in message_lower for saud in ["bom dia", "boa tarde", "boa noite", "olá", "oi", "oii", "e aí"]):
            return {
                "message": "Olá! Sou o Chatbot do IFSP Campinas. Como posso te ajudar com informações sobre cursos, disciplinas, professores, horários e salas?",
                "sql": None
            }

        if any(despedida in message_lower for despedida in ["tchau", "até logo", "obrigado", "obrigada", "valeu", "sair"]):
            return {
                "message": "De nada! Se precisar de mais alguma coisa, é só perguntar. Tenha um ótimo dia!",
                "sql": None
            }

        # Prompt enviado para a IA
        full_prompt = f"""
        Você é um assistente que traduz perguntas sobre o IFSP Campinas em consultas SQL para a tabela `dados_ifsp`.

        ## Estrutura da Tabela:
        {self.db_schema}

        ## Exemplos:
        {self.example_sql_instructions}

        ## Regras:
        1. A resposta deve conter apenas a consulta SQL começando com SELECT e terminando com ;.
        2. Use LIKE e SELECT DISTINCT para evitar repetições.
        3. Se não souber a resposta, escreva FORA_DO_ESCOPO.

        Pergunta do Usuário: "{user_message}"
        SQL:
        """

        try:
            response = requests.post(
                self.ollama_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_ctx": 4096
                    }
                }),
                timeout=180
            )
            response.raise_for_status()
            result = response.json()
            resposta_bruta = result.get("response", "").strip()
            sql_query = self._validate_and_extract_sql(resposta_bruta)

            if sql_query == "FORA_DO_ESCOPO":
                return {"message": "Desculpe, essa pergunta está fora do meu escopo. Posso ajudar com cursos, disciplinas, professores, salas e horários.", "sql": None}
            elif sql_query:
                return {"message": f"Entendi que você perguntou sobre '{user_message}'. Buscando as informações...", "sql": sql_query}
            else:
                return {"message": "Não consegui gerar uma consulta válida. Reformule a pergunta, por favor.", "sql": None}

        except requests.exceptions.RequestException as e:
            return {"message": f"Erro na comunicação com a IA: {e}", "sql": None}

    def _validate_and_extract_sql(self, text):
        if "FORA_DO_ESCOPO" in text.upper():
            return "FORA_DO_ESCOPO"

        match = re.search(r"SELECT\s+.*?;", text, re.IGNORECASE | re.DOTALL)
        if not match:
            return None

        sql_candidate = match.group(0).strip()
        if any(keyword in sql_candidate.lower() for keyword in ["insert", "update", "delete", "drop", "alter"]):
            return None

        return sql_candidate
