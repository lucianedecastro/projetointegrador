from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import os
import json
from dotenv import load_dotenv
import traceback

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__, static_url_path='/static', template_folder='templates')
CORS(app)

# Configuração do banco de dados
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


@app.route("/")
def index():
    """Renderiza a página principal."""
    return render_template("index.html")


@app.route('/api/modalidades', methods=['GET'])
def get_modalidades():
    """Retorna uma lista de modalidades esportivas."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = connection.cursor()
        query = "SELECT DISTINCT modalidade FROM Esportivo"
        cursor.execute(query)
        modalidades = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        error_message = f"Erro ao buscar modalidades: {e}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": "Erro ao buscar modalidades."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return jsonify(modalidades)


@app.route('/api/dados', methods=['GET'])
def get_data():
    """Retorna dados filtrados com base nos parâmetros fornecidos."""
    try:
        estado = request.args.get('estado')
        remuneracao = request.args.get('remuneracao', type=float)
        modalidade = request.args.get('modalidade')
        genero = request.args.get('genero')
        estadoCivil = request.args.get('estadoCivil')
        escolaridade = request.args.get('escolaridade')

        connection = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )

        query = """
        SELECT 
            c.idCadastro, c.email, g.genero, d.estado, e.remuneracao, es.modalidade
        FROM Cadastro c
        JOIN Geral g ON c.idCadastro = g.idCadastro
        JOIN Demografico d ON c.idCadastro = d.idCadastro
        JOIN Economico e ON c.idCadastro = e.idCadastro
        JOIN Esportivo es ON c.idCadastro = es.idCadastro
        WHERE 
            (d.estado = %s OR %s IS NULL) AND
            (e.remuneracao >= %s OR %s IS NULL) AND
            (es.modalidade = %s OR %s IS NULL) AND
            (g.genero = %s OR %s IS NULL) AND
            (g.estadoCivil = %s OR %s IS NULL) AND
            (e.escolaridade = %s OR %s IS NULL)
        """
        params = (
            estado, estado, remuneracao, remuneracao,
            modalidade, modalidade, genero, genero,
            estadoCivil, estadoCivil, escolaridade, escolaridade
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        data = cursor.fetchall()
    except Exception as e:
        error_message = f"Erro ao buscar dados: {e}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": "Erro ao buscar dados."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return jsonify(data)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)