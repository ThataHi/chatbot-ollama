# app.py

from flask import Flask, render_template, request, jsonify
import mysql.connector
from llama_ai_logic import LlamaChatbotLogic

app = Flask(__name__)
ai = LlamaChatbotLogic()

def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Thais2004!",
            database="ifsp"
        )
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o banco: {err}")
        return None

def formatar_resultados_sql(cursor):
    try:
        resultados = cursor.fetchall()
        if not resultados:
            return "Não encontrei nenhuma informação correspondente à sua pergunta."

        colunas = [desc[0] for desc in cursor.description]
        if len(resultados) == 1 and len(colunas) == 1:
            return str(resultados[0][0])

        linhas_formatadas = []
        for linha in resultados:
            itens_linha = [str(item) for item in linha]
            linhas_formatadas.append(" | ".join(itens_linha))

        return "<br>".join(linhas_formatadas)

    except Exception as e:
        print(f"Erro ao formatar resultados: {e}")
        return "Erro ao processar os dados do banco."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'Mensagem não pode ser vazia.'}), 400

    print(f"Mensagem recebida do usuário: {user_message}")
    response_data = ai.prompt(user_message)
    response_message = response_data.get("message", "Ocorreu um erro inesperado.")
    sql_query = response_data.get("sql")

    if sql_query:
        print(f"IA gerou SQL: {sql_query}")
        conn = conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql_query)
                resultado = formatar_resultados_sql(cursor)
                response_message += f"<br><br><b>Resultados:</b><br>{resultado}"
            except mysql.connector.Error as err:
                print(f"Erro SQL: {err}")
                response_message = "Erro ao consultar o banco de dados."
            finally:
                if 'cursor' in locals(): cursor.close()
                conn.close()
        else:
            response_message = "Erro ao conectar ao banco de dados."

    print(f"Resposta final enviada ao usuário: {response_message}")
    return jsonify({'response': response_message})

if __name__ == '__main__':
    app.run(debug=True)
