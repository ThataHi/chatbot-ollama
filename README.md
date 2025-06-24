# Chatbot IFSP Campinas

Chatbot inteligente que responde perguntas sobre cursos, disciplinas, professores e salas do IFSP Campinas. Utiliza MySQL + Flask + LLM (MetaAI) para interpretar e responder com base nos dados oficiais da instituição.

## Funcionalidades
- Interpretação de linguagem natural
- Respostas a partir de banco de dados
- Interface web simples
- Integração com modelo de linguagem (MetaAI)

## Como rodar
1. Configure o banco MySQL com os dados do IFSP.
2. Ajuste `meta_ai_api.py` com a integração real da MetaAI.
3. Rode com:

```bash
pip install -r requirements.txt
python app.py
