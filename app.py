from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

DB_PATH = '/app/db/carteira.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bitcoin (
            id INTEGER PRIMARY KEY,
            data_compra TEXT NOT NULL,
            valor_compra REAL NOT NULL,
            quantidade REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_cotacao_atual():
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCBRL')
        data = response.json()
        return float(data['price'])
    except Exception as e:
        # Fallback para CoinGecko
        try:
            response_fallback = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl')
            return response_fallback.json()['bitcoin']['brl']
        except:
            raise ValueError('Falha em todas as APIs')

@app.route('/api/bitcoin', methods=['GET'])
def get_bitcoin():
    try:
        cotacao = get_cotacao_atual()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        registros = conn.execute('SELECT * FROM bitcoin').fetchall()
        
        if not registros:
            return jsonify([]), 200  # Retorna vazio se não houver dados

        resultados = []
        for reg in registros:
            registro = dict(reg)
            registro.update({
                'valor_atual': round(reg['quantidade'] * cotacao, 2),
                'lucro': round(reg['quantidade'] * cotacao - reg['valor_compra'], 2),
                'cotacao_atual': cotacao
            })
            resultados.append(registro)
            
        return jsonify(resultados), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 503  # Erro específico de API
    except Exception as e:
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/bitcoin', methods=['POST'])
def add_bitcoin():
    try:
        data = request.get_json()
        if not data or not all(field in data for field in ['data_compra', 'valor_compra', 'quantidade']):
            return jsonify({'error': 'Dados incompletos'}), 400

        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO bitcoin (data_compra, valor_compra, quantidade)
            VALUES (?, ?, ?)
        ''', (data['data_compra'], float(data['valor_compra']), float(data['quantidade'])))  # Correção aqui
        conn.commit()
        return jsonify({'message': 'Registro criado'}), 201
        
    except ValueError:
        return jsonify({'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bitcoin/<int:id>', methods=['PUT'])
def update_bitcoin(id):
    try:
        data = request.get_json()
        required = ['data_compra', 'valor_compra', 'quantidade']
        
        if not data or not all(field in data for field in required):
            return jsonify({'error': 'Dados incompletos'}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bitcoin SET
                data_compra = ?,
                valor_compra = ?,
                quantidade = ?
            WHERE id = ?
        ''', (data['data_compra'], float(data['valor_compra']), float(data['quantidade']), id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Registro não encontrado'}), 404
            
        conn.commit()
        return jsonify({'message': 'Atualizado com sucesso'}), 200

    except ValueError:
        return jsonify({'error': 'Valores inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bitcoin/<int:id>', methods=['DELETE'])
def delete_bitcoin(id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bitcoin WHERE id = ?', (id,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Registro não encontrado'}), 404
            
        conn.commit()
        return jsonify({'message': 'Excluído com sucesso'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3005)