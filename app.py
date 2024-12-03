from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import os
import json
from dotenv import load_dotenv
import traceback
import pandas as pd

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração básica do Flask
app = Flask(__name__, static_url_path='/static', template_folder='templates')
CORS(app)  # Habilita CORS para permitir conexões de diferentes origens

# Configuração do banco de dados utilizando variáveis de ambiente
DB_HOST = os.getenv('DB_HOST')  # Endereço do servidor do banco
DB_USER = os.getenv('DB_USER')  # Usuário do banco de dados
DB_PASSWORD = os.getenv('DB_PASSWORD')  # Senha do banco de dados
DB_NAME = os.getenv('DB_NAME')  # Nome do banco de dados

# Rota principal que renderiza o arquivo HTML da aplicação
@app.route("/")
def index():
    """Renderiza a página principal."""
    return render_template("index.html")

# Rota que retorna as modalidades esportivas únicas armazenadas no banco de dados
@app.route('/api/modalidade', methods=['GET'])
def get_modalidade():
    """Retorna uma lista de modalidades esportivas."""
    try:
        # Conexão com o banco de dados
        connection = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = connection.cursor()
        
        # Consulta SQL para buscar as modalidades únicas
        query = "SELECT DISTINCT modalidade FROM Esportivo"
        cursor.execute(query)
        
        # Extrai os resultados em uma lista
        modalidade = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        # Caso ocorra um erro, exibe a mensagem detalhada no log
        error_message = f"Erro ao buscar modalidades: {e}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": "Erro ao buscar modalidades."}), 500
    finally:
        # Garante o fechamento do cursor e da conexão
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return jsonify(modalidade)  # Retorna a lista de modalidades como JSON

# Rota para buscar dados filtrados com base nos parâmetros fornecidos
@app.route('/api/dados', methods=['GET'])
def get_data():
    """Retorna dados filtrados com base nos parâmetros fornecidos."""
    try:
        # Coleta os parâmetros de filtro fornecidos pela requisição
        estado = request.args.get('estado')
        remuneracao = request.args.get('remuneracao', type=float)
        modalidade = request.args.get('modalidade')
        genero = request.args.get('genero')
        estadoCivil = request.args.get('estadoCivil')
        escolaridade = request.args.get('escolaridade')

        # Conexão com o banco de dados
        connection = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Consulta SQL que aplica os filtros com OR para parâmetros nulos
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
        # Parâmetros correspondentes para os filtros
        params = (
            estado, estado, remuneracao, remuneracao,
            modalidade, modalidade, genero, genero,
            estadoCivil, estadoCivil, escolaridade, escolaridade
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        data = cursor.fetchall()  # Recupera os resultados da consulta
    except Exception as e:
        # Caso ocorra um erro, exibe a mensagem detalhada no log
        error_message = f"Erro ao buscar dados: {e}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": "Erro ao buscar dados."}), 500
    finally:
        # Garante o fechamento do cursor e da conexão
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return jsonify(data)  # Retorna os dados como JSON

# Rota para gerar um arquivo JSON contendo dados extraídos do banco
@app.route('/api/json', methods=['GET'])
def generate_json():
    """Gera e salva um arquivo JSON com dados do banco."""
    try:
        # Conexão com o banco de dados
        connection = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        # Consulta SQL para extrair os dados completos
        query = """
        SELECT 
            c.idCadastro, c.email, g.genero, d.estado, e.remuneracao, es.modalidade
        FROM Cadastro c
        JOIN Geral g ON c.idCadastro = g.idCadastro
        JOIN Demografico d ON c.idCadastro = d.idCadastro
        JOIN Economico e ON c.idCadastro = e.idCadastro
        JOIN Esportivo es ON c.idCadastro = es.idCadastro
        """
        df = pd.read_sql(query, connection)  # Converte os dados para um DataFrame pandas
        
        # Define o caminho do arquivo JSON
        json_file_path = os.path.join(os.getcwd(), 'dados.json')
        
        # Salva o DataFrame como um arquivo JSON
        df.to_json(json_file_path, orient='records', force_ascii=False)
        return jsonify({"message": "Arquivo JSON gerado com sucesso!"})
    except Exception as e:
        # Caso ocorra um erro, exibe a mensagem detalhada no log
        error_message = f"Erro ao gerar JSON: {e}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": "Erro ao gerar JSON."}), 500
    finally:
        if connection:
            connection.close()  # Garante o fechamento da conexão com o banco

# Inicializa o servidor Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Porta padrão ou definida em variáveis de ambiente
    app.run(debug=False, host='0.0.0.0', port=port)
