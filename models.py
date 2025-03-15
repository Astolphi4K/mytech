import sqlite3
import json
from collections import Counter




class Database:
    def __init__(self, db_name="aplicativo.db"):
        """Inicializa a conexão com o banco de dados."""
        self.db_name = db_name

    def conectar(self):
        """Cria e retorna uma conexão com o banco de dados."""
        return sqlite3.connect(self.db_name)

    def criar_tabela(self):
        """Cria a tabela login se ela não existir."""
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
        ALTER TABLE cadastro ADD COLUMN rastreamento TEXT;
""", (123456789, 1))
        conn.commit()
        conn.close()

    def inserir_usuario(self, username, password):
        """Insere um novo usuário no banco de dados."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO login (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

    def verificar_login(self, usuario, senha):
        """Verifica se o usuário e senha estão corretos no banco de dados."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login WHERE username = ? AND passowrd = ?", (usuario, senha))
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None  # Retorna True se o login for válido

    def inserir_cadastro(self, dados):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cadastro (
                nome_completo, cpf, cep, numero, bairro, complemento, uf, cidade, logradouro, 
                tipo_devolucao, produto_sku, quantidade, status, data_cadastro, postagem
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["nome"], dados["cpf"], dados["cep"], dados["numero"], dados["bairro"], 
            dados.get("complemento", ""), dados["uf"], dados["cidade"], dados.get("logradouro", ""),
            dados["tipo"], dados["produto"], dados["quantidade"], dados["status"], dados["data"], dados['postagem']
        ))

        conn.commit()
        conn.close()

    def listar_tabela(self):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cadastro ORDER BY id DESC")
        pedidos = cursor.fetchall()

        colunas = [descricao[0] for descricao in cursor.description]
        pedidos_json = [dict(zip(colunas, pedido)) for pedido in pedidos]
        conn.close()
        return json.dumps(pedidos_json, indent=4, ensure_ascii=False)  # Exibe JSON formatado
    
    def atualizar_status(self, dados):
        conn = self.conectar()
        cursor = conn.cursor()
        if dados['status'] == "Recebido CD":

            cursor.execute("""
        UPDATE cadastro
        SET status = ?, data_recebimento = ?, observacao = ?
        WHERE id = ?
    """, (dados['status'], dados['data_recebimento'], dados['observacao'], dados['id']))
        
        elif dados['status'] == "Manutenção":
            cursor.execute("""
        UPDATE cadastro
        SET status = ?, data_recebimento2 = ?
        WHERE id = ?
    """, (dados['status'], dados['data_assistencia'], dados['id']))
       

        elif dados['status'] == "Expedição":
            cursor.execute("""
        UPDATE cadastro
        SET status = ?, tecnico_responsavel = ?, detalhes_manutencao = ?
        WHERE id = ?
    """, (dados['status'], dados['tecnico'], dados['detalhes'],dados['id']))
            
        elif dados['status'] == "Enviado":
            cursor.execute("""
        UPDATE cadastro
        SET status = ?, data = ?, rastreamento = ?, tipo = ?, transportadora = ?,  valor_real = ?
        WHERE id = ?
    """, (dados['status'], dados['data_enviado'], dados['rastreamento'],dados['tipo'],dados['transportadora'],dados['preco'], dados['id']))
            
        elif dados['status'] == "Entregue":
            cursor.execute("""
        UPDATE cadastro
        SET status = ?
        WHERE id = ?
    """, (dados['status'], dados['id']))
        conn.commit()
        conn.close()

    def contar_status(self):
        """Conta quantos pedidos existem em cada status e retorna um JSON."""
        conn = sqlite3.connect("aplicativo.db")
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM cadastro")
        resultados = cursor.fetchall()  # Retorna uma lista de tuplas [('Entregue',), ('Manutenção',), ...]

        conn.close()

        # Converter a lista de tuplas para uma lista simples de status
        status_list = [row[0] for row in resultados]

        # Contar quantas vezes cada status aparece
        contagem = Counter(status_list)
   
        return json.dumps(contagem, ensure_ascii=False)
    
    def impressao_etiqueta(self,args):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM cadastro WHERE id IN ({args});")
        cadastro = cursor.fetchall()
        colunas = [descricao[0] for descricao in cursor.description]
        pedidos_json = [dict(zip(colunas, pedido)) for pedido in cadastro]
        return pedidos_json

    def contar_frete(self):
        """Conta quantos pedidos existem em cada status e retorna um JSON."""
        conn = sqlite3.connect("aplicativo.db")
        cursor = conn.cursor()

        cursor.execute("""SELECT tipo, SUM(valor_real) AS total,
                tipo || ': ' || SUM(valor_real) AS resultado_concatenado
            FROM cadastro
            GROUP BY tipo;""")
        conn.commit()
        resultados = cursor.fetchall()  # Retorna uma lista de tuplas [('Entregue',), ('Manutenção',), ...]
        result = {}
        conn.close()

        for item in resultados:
            tipo, total, concatenado = item
            if tipo and total:  # Ignorar tuplas com None ou valores inválidos
                result[tipo] = round(total, 2)  # Arredonda para 2 casas decimais

            json_result = json.dumps(result, indent=4)
       
        
        return json_result
    
    def div(self):

        conn = sqlite3.connect("aplicativo.db")
        cursor = conn.cursor()

        cursor.execute("""DELETE FROM cadastro;
                          VACUUM;""")
        conn.commit()
        resultados = cursor.fetchall()  # Retorna uma lista de tuplas [('Entregue',), ('Manutenção',), ...]

    def buscar_dados(self,filtro):
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect('aplicativo.db')
        cursor = conn.cursor()

        # Base da consulta
        query = "SELECT * FROM cadastro WHERE 1=1"
        parametros = []

        # Adicionando a condição para o intervalo de datas
        if filtro.get("data_inicio") and filtro.get("data_fim"):
            query += " AND data_cadastro BETWEEN ? AND ?"
            parametros.extend([filtro["data_inicio"], filtro["data_fim"]])
        elif filtro.get("data_inicio"):  # Caso tenha apenas a data_inicio
            query += " AND data_cadastro >= ?"
            parametros.append(filtro["data_inicio"])
        elif filtro.get("data_fim"):  # Caso tenha apenas a data_fim
            query += " AND data_cadastro <= ?"
            parametros.append(filtro["data_fim"])

        # Adicionando filtros para as outras colunas da tabela
        if filtro.get("postagem"):
            query += " AND postagem = ?"
            parametros.append(filtro["postagem"])  # Busca exata
        if filtro.get("tipo"):
            query += " AND tipo_devolucao = ?"
            parametros.append(filtro["tipo"])  # Busca exata
        if filtro.get("situacao"):
            query += " AND status = ?"
            parametros.append(filtro["situacao"])  # Busca exata

        # **Garantindo que a query seja válida**
        query += " ORDER BY id DESC"
        cursor.execute(query, parametros)
        dados = cursor.fetchall()
        colunas = [descricao[0] for descricao in cursor.description]
        pedidos_json = [dict(zip(colunas, pedido)) for pedido in dados]
        # Fechando a conexão
        conn.close()

        return pedidos_json
    
    def obter_pedido_id(self, order_id):
        conn = sqlite3.connect("aplicativo.db")
        conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cadastro WHERE id = ?", (order_id,))
        dados = cursor.fetchall()

        pedidos_json = [dict(pedido) for pedido in dados]  # Converte para lista de dicionários

        conn.close()
        
        return pedidos_json  # Retorna lista vazia [] caso não haja registros

    