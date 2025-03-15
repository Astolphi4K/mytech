from flask import Blueprint
from flask import render_template, request,jsonify, make_response
import json
from models import Database

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')


@main_routes.route('/submit_login', methods=['POST'])
def submit_login():
    
    email = request.form.get('email')
    senha = request.form.get('password')

    resultado_login = Database().verificar_login(email,senha)
    
    if resultado_login:
        resp = make_response(jsonify({"status": "success"}))
        resp.set_cookie("user", email, max_age=60 * 60 * 24)  # Cookie dura 1 dia
        return resp
    else:
        return jsonify({'status': 'fail'})


@main_routes.route("/verificar_login", methods=["GET"])
def verificar_login():
    user = request.cookies.get("user")
    if user:
        return jsonify({"logged_in": True, "user": user})
    return jsonify({"logged_in": False})

@main_routes.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"message": "Logout realizado com sucesso!"}))
    resp.set_cookie("user", "", expires=0)  # Remove o cookie
    return resp


@main_routes.route('/menu')
def menu():
    return render_template('menu.html')
@main_routes.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')
@main_routes.route('/retornos')
def retornos():
    return render_template('retornos.html')

@main_routes.route("/dados_retornos")
def dados_retornos():
    cadastros = Database().listar_tabela()
    
    return jsonify(json.loads(cadastros))

@main_routes.route('/alterarsituacao', methods=['POST'])
def alterarsituacao():
    b = request.json
    Database().atualizar_status(b)

    return jsonify({'status': 'success'})
   

@main_routes.route('/integracao')
def integracao():
    return render_template("integracao.html")

@main_routes.route('/submit_form', methods=['POST'])
def submit_form():

    try:
        dados = request.json  # Pega os dados enviados pelo frontend
        Database().inserir_cadastro(dados)

        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route("/contagem_status", methods=["GET"])
def contagem_status():
    try:
        data = Database().contar_status()
        data = json.loads(data)
        dados_normalizados = {
            "emConserto": data.get("Manutenção", 0),
            "emExpedicao": data.get("Expedição", 0),
            "enviados": data.get("Enviado", 0),
            "emDevolucao": data.get("Em devolução", 0),
            "recebidoCD": data.get("Recebido CD", 0),
            "entregue": data.get("Entregue", 0)
    }


        return jsonify({"status": "success", "data": dados_normalizados})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route("/imprimir_etiquetas",  methods=["GET"])
def imprimir_etiquetas():
    id_param = request.args.get('id')

    data = Database().impressao_etiqueta(id_param) or []
    json_data = json.dumps(data)
    return render_template('print.html', data=json_data)

@main_routes.route("/obter_valores",methods=["GET"])
def obter_valores():
    try:
        data = Database().contar_frete()
        data = json.loads(data)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route('/buscar', methods=['POST'])
def buscar():
    try:
        dados = request.json
        dados = Database().buscar_dados(dados)
        if not dados:
               return jsonify({"status":"fail","message": "Nenhuma devolução encontrada!"}), 401
        else:
            return jsonify({"status": "success", "data" : dados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from flask import jsonify

@main_routes.route("/orders/<int:order_id>")
def order_page(order_id):
    pedidos = Database().obter_pedido_id(order_id)

    if not pedidos:
        return "Pedido não encontrado", 404

    return render_template("order.html", order=pedidos[0])  # Passa o dicionário direto

@main_routes.route("/api/orders/<int:order_id>")
def order_api(order_id):
    pedidos = Database().obter_pedido_id(order_id)

    if not pedidos:
        return jsonify({"error": "Pedido não encontrado"}), 404

    return jsonify(pedidos[0])  # Retorna JSON puro na API
