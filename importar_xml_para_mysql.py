import xml.etree.ElementTree as ET
import mysql.connector

# Namespace usado no arquivo XML do Excel.
NAMESPACES = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}

def carregar_dados(xml_path):
    """
    Carrega dados de um arquivo XML de planilha, extraindo informações específicas.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        table = root.find('.//ss:Table', NAMESPACES)

        if table is None:
            print(f"Erro: Não foi encontrada a tag 'Table' no XML '{xml_path}'.")
            return []

        linhas = table.findall('ss:Row', NAMESPACES)
        if not linhas:
            print(f"Aviso: Nenhuma linha de dados encontrada no XML '{xml_path}'.")
            return []

        dados = []
        # Ignora a primeira linha (cabeçalho) iterando a partir do segundo elemento
        for row in linhas[1:]:
            celulas = row.findall('ss:Cell', NAMESPACES)
            # Cria um dicionário para armazenar os dados da linha pelo índice da coluna
            linha_dados = {}
            for cell in celulas:
                # O atributo 'Index' nos diz em qual coluna este dado deve estar
                index_attr = cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
                if index_attr:
                    idx = int(index_attr)
                    data_node = cell.find('ss:Data', NAMESPACES)
                    if data_node is not None and data_node.text:
                        linha_dados[idx] = data_node.text.strip()
            
            # Mapeia os dados do dicionário para um formato limpo, se a linha tiver dados.
            # Os números (1, 2, 3, 5, 6, 11) correspondem aos 'Index' das colunas no XML.
            if linha_dados:
                item = {
                    'codigo': linha_dados.get(1, ''),
                    'disciplina': linha_dados.get(2, ''),
                    'curso': linha_dados.get(3, ''),
                    'professor': linha_dados.get(5, ''), # Verifique se o índice 5 é o professor
                    'horario': linha_dados.get(6, ''),   # Verifique se o índice 6 é o horário
                    'sala': linha_dados.get(11, '')      # Verifique se o índice 11 é a sala
                }
                # Adiciona à lista apenas se houver um código de disciplina
                if item['codigo']:
                    dados.append(item)
        return dados
    except ET.ParseError as e:
        print(f"Erro ao analisar o XML: {e}")
        return []
    except Exception as e:
        print(f"Um erro inesperado ocorreu ao carregar os dados: {e}")
        return []

def conectar():
    """Função para conectar ao banco de dados."""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Thais2004!", # <-- MUDE AQUI SE NECESSÁRIO
            database="ifsp"
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

def importar_para_banco(dados):
    """
    Importa os dados carregados para a tabela 'dados_ifsp' no MySQL.
    """
    conn = conectar()
    if not conn:
        print("Não foi possível conectar ao banco. Importação abortada.")
        return

    cursor = conn.cursor()
    try:
        # Limpa a tabela para evitar duplicatas em reimportações
        cursor.execute("TRUNCATE TABLE dados_ifsp")
        print("Tabela 'dados_ifsp' limpa com sucesso.")

        sql = """
        INSERT INTO dados_ifsp (codigo, disciplina, curso, professor, horario, sala) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Converte a lista de dicionários para uma lista de tuplas para inserção
        registros_para_inserir = [
            (d['codigo'], d['disciplina'], d['curso'], d['professor'], d['horario'], d['sala'])
            for d in dados
        ]
        
        # O método executemany é muito mais eficiente para inserir múltiplos registros
        cursor.executemany(sql, registros_para_inserir)
        
        conn.commit()
        print(f"{cursor.rowcount} registros foram importados com sucesso para 'dados_ifsp'.")

    except mysql.connector.Error as err:
        print(f"Erro ao importar dados para o banco: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Iniciando importação de dados do XML para o banco de dados...")
    # Certifique-se que o arquivo 'dados_ifsp.xml' está na mesma pasta
    dados_carregados = carregar_dados('dados_ifsp.xml')
    if dados_carregados:
        importar_para_banco(dados_carregados)
    else:
        print("Nenhum dado válido foi carregado do XML. Verifique o arquivo.")
