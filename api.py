from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

app = Flask(__name__)
CORS(app)

# Configurar a conexão com o MongoDB
client = MongoClient(config.MONGO_URI)
db = client[config.DATABASE_NAME]

# Coleções
users_collection = db['users']
messages_collection = db['messages']

@app.route('/iniciaChat', methods=['POST'])
def inicia_chat():
    data = request.json
    username = data.get('usuario')
    
    if not username:
        return jsonify({"error": "Nome de usuário é obrigatório"}), 400

    # Verifica se o usuário já existe
    user = users_collection.find_one({"usuario": username})
    print(user)
    if user:
        return jsonify({"identificador": str(user['_id'])})
    
    # Cria um novo usuário
    user_id = users_collection.insert_one({"usuario": username}).inserted_id
    return jsonify({"identificador": str(user_id)})

@app.route('/listaUsuarios', methods=['GET'])
def lista_usuarios():
    users = list(users_collection.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users)

@app.route('/msgAll', methods=['POST'])
def msg_all():
    data = request.json
    identificador_usuario = data.get('identificadorUsuario')
    msg = data.get('msg')

    if not identificador_usuario or not msg:
        return jsonify({"error": "Identificador do usuário e mensagem são obrigatórios"}), 400

    user = users_collection.find_one({"_id": ObjectId(identificador_usuario)})
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Cria uma nova mensagem
    message_id = messages_collection.insert_one({
        "identificadorUsuarioRemetente": identificador_usuario,
        "msg": msg
    }).inserted_id

    return jsonify({"MsgId": str(message_id)})

@app.route('/consultaMensagens', methods=['GET'])
def consulta_mensagens():
    identificador_usuario = request.args.get('identificadorUsuario')
    
    if not identificador_usuario:
        return jsonify({"error": "Identificador do usuário é obrigatório"}), 400

    messages = list(messages_collection.find({"identificadorUsuarioRemetente": identificador_usuario}))
    for message in messages:
        message['_id'] = str(message['_id'])
    
    return jsonify(messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)