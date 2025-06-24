# Chatbot IFSP Campinas

Chatbot inteligente que responde perguntas sobre cursos, disciplinas, professores e salas do IFSP Campinas. Utiliza MySQL + Flask + LLM para interpretar e responder com base nos dados oficiais da instituição.

## Funcionalidades
- Interpretação de linguagem natural
- Respostas a partir de banco de dados
- Interface web simples
- Integração com modelo de linguagem

## Como rodar
1. Configure o banco MySQL com os dados do IFSP.
2. Rode no terminal:

```bash
pip install -r requirements.txt
python app.py

ollama pull codellama:7b
ollama run codellama:7b
