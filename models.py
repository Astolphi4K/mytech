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
        try:
            conn = self.conectar()
            cursor = conn.cursor()

            # Verificando dados
            #print("Verificando dados:")
            #print("Form Data:", dados["formData"])
            #print("Tabela Data:", dados["tabelaData"])

            # Verificando se 'tabelaData' não está vazio
            #if not dados["tabelaData"]:
            #    print("Erro: 'tabelaData' está vazio ou não existe!")
            #    return  # Retorna se não houver dados para a tabela

            # Pegando o primeiro item da tabela
            tab = dados["tabelaData"]
            print(tab)
            if not tab :
                altura_unidade = "#N/D"
                comprimento_unidade = "#N/D"
                largura_unidade = "#N/D"
                peso_unidade = "#N/D"
                precosugestao = "#N/D"
                ncm = "#N/D"
                url_image = "#N/D"
                nome_item = "#N/D"
            
            else:
                tabela_item = dados["tabelaData"][0]
                for chave in ["altura_unidade", "largura_unidade", "ncm", "nome_item", "peso_unidade", "precosugestao", "url_image"]:
                    if chave not in tabela_item:
                        print(f"Erro: Falta chave {chave} em 'tabelaData'.")
                        return  # Retorna se alguma chave da tabela estiver ausente

                    # Convertendo os dados para os tipos corretos (se necessário)
                    altura_unidade = float(tabela_item["altura_unidade"])  # Convertendo para float
                    comprimento_unidade = float(tabela_item["comprimento_unidade"])  # Convertendo para float
                    largura_unidade = float(tabela_item["largura_unidade"])  # Convertendo para float
                    peso_unidade = float(tabela_item["peso_unidade"])  # Convertendo para float
                    precosugestao = float(tabela_item["precosugestao"])  # Convertendo para float
                    ncm = tabela_item["ncm"]  # NCM é provavelmente uma string
                    url_image = tabela_item["url_image"]  # A URL da imagem permanece como string
                    nome_item = str(tabela_item["nome_item"])
                
            def tratar_valor(valor):
                if valor is None or valor == "":
                    return "#N/D"
                return valor
            

            cursor.execute("""
                INSERT INTO cadastro (
                    nome_completo, cpf, cep, numero, bairro, complemento, uf, cidade, logradouro, 
                    tipo_devolucao, produto_sku, quantidade, status, data_cadastro, ticket,
                    altura, largura,comprimento, ncm, nome_item, peso, preco_sugestao, url_image
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tratar_valor(dados["formData"]["nome"]),
                tratar_valor(dados["formData"]["cpf"]),
                tratar_valor(dados["formData"]["cep"]),
                tratar_valor(dados["formData"]["numero"]),
                tratar_valor(dados["formData"]["bairro"]),
                tratar_valor(dados["formData"]["complemento"]),
                tratar_valor(dados["formData"]["uf"]),
                tratar_valor(dados["formData"]["cidade"]),
                tratar_valor(dados["formData"]["logradouro"]),
                tratar_valor(dados["formData"]["tipo"]),
                tratar_valor(dados["formData"]["produto"]),
                tratar_valor(dados["formData"]["quantidade"]),
                tratar_valor(dados["formData"]["status"]),
                tratar_valor(dados["formData"]["data"]),
                tratar_valor(dados["formData"]['ticket']),
                tratar_valor(altura_unidade),
                tratar_valor(largura_unidade),
                tratar_valor(comprimento_unidade),
                tratar_valor(ncm),
                tratar_valor(nome_item),
                tratar_valor(peso_unidade),
                tratar_valor(precosugestao),
                tratar_valor(url_image)
            
            ))

            # Commitando a transação
            conn.commit()
            print("Dados inseridos com sucesso!")
            
        except Exception as e:
            print("Erro ao inserir os dados:", str(e))
        
        finally:
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
        try:
            if dados['status'] == "Em devolução":
                cursor.execute("""
                    UPDATE cadastro
                    SET status = ?, postagem = ?
                    WHERE id = ?""", 
                    (dados['status'], dados['postagem'], dados['id']))

            elif dados['status'] == "Recebido CD":

                cursor.execute("""
                    UPDATE cadastro
                    SET status = ?, data_recebimento = ?, observacao = ?
                    WHERE id = ?
                """, 
                (dados['status'], dados['data_recebimento'], dados['observacao'], dados['id']))
            
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
        except Exception as e:
            print("Erro ao inserir os dados:", str(e))
        
        finally:
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
    
    def delete(self):

        conn = sqlite3.connect("aplicativo.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cadastro")
        cursor.execute("""UPDATE sqlite_sequence SET seq = 0 WHERE name = 'cadastro'""")
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

    def inserir_coluna(self):
        conn = sqlite3.connect("aplicativo.db")
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE cadastro ADD COLUMN ticket REAL;")
        conn.commit()
        resultados = cursor.fetchall()  
