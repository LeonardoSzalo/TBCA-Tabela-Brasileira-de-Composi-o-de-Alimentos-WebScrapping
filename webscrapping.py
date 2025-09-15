# -*- coding: utf-8 -*-
import json
import requests
import re
import time
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
ARQUIVO_SAIDA = "tbca_dados_completos.json"
URL_BASE_LISTA = 'http://www.tbca.net.br/base-dados/composicao_alimentos.php'
URL_BASE_ALIMENTO = 'http://www.tbca.net.br/base-dados/int_composicao_alimentos.php'


def parse_medida_caseira_header(header_text):
    """
    Usa Regex para analisar o cabeçalho de uma coluna de medida caseira.
    Exemplo de entrada: "Pedaço/ Unidade/ Fatia (M) (80 g)"
    Retorna um dicionário com as informações separadas.
    """
    # Expressão Regular para encontrar descrição, tamanho (opcional) e gramas.
    # Trata tanto números inteiros quanto decimais para as gramas.
    pattern = r"(.+?)\s*(?:\((.+?)\))?\s*\((\d+[\.,]?\d*)\s*g\)"
    match = re.search(pattern, header_text)

    if match:
        # Extrai os grupos capturados pelo Regex
        return {
            "descricao": match.group(1).strip(),
            "tamanho": match.group(2),  # Pode ser None se não existir
            "gramas": float(match.group(3).replace(',', '.'))  # Converte para número
        }
    return None


def extrair_dados_alimento(cod_alimento, classe_alimento):
    """
    Função principal para raspar os detalhes da página de um único alimento.
    """
    url = f'{URL_BASE_ALIMENTO}?cod_produto={cod_alimento}'
    print(f"  > Buscando dados para o código: {cod_alimento}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Lança um erro para status ruins (404, 500, etc)
    except requests.exceptions.RequestException as e:
        print(f"    [ERRO] Falha ao acessar a página do alimento {cod_alimento}. Erro: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        descricao_raw = soup.find('h5', {'id': 'overview'}).text
        # Limpa o texto para pegar apenas a descrição
        descricao = descricao_raw.split('Descrição:')[1].split('<<')[0].strip()
    except (AttributeError, IndexError):
        descricao = "Descrição não encontrada"

    # Agora procuramos pela tabela usando seu ID único 'tabela1'
    table = soup.find('table', id='tabela1')

    if not table:
        print(f"    [AVISO] Tabela de nutrientes (id='tabela1') não encontrada para '{cod_alimento} - {descricao}'. Pulando este item.")
        return None

    headers_text = [th.text.strip() for th in table.find_all('th')]
    
    medidas_caseiras_info = []
    for header_text in headers_text[3:]:
        parsed_header = parse_medida_caseira_header(header_text)
        if parsed_header:
            medidas_caseiras_info.append(parsed_header)

    nutrientes_100g = []
    dados_nutricionais_medidas = [{} for _ in medidas_caseiras_info]

    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cells = [td.text.strip() for td in row.find_all('td')]
        if len(cells) < 3: continue

        componente, unidade, valor_100g = cells[0], cells[1], cells[2]
        
        # Armazena os dados por 100g
        nutrientes_100g.append({"componente": componente, "unidade": unidade, "valor": valor_100g})
        
        # Itera sobre as células restantes, que correspondem às medidas caseiras
        for i, medida_info in enumerate(medidas_caseiras_info):
            idx_celula = 3 + i
            if idx_celula < len(cells):
                dados_nutricionais_medidas[i][componente] = {"valor": cells[idx_celula], "unidade": unidade}
    
    # Monta o objeto final combinando as informações das medidas
    medidas_caseiras_final = []
    for i, medida_info in enumerate(medidas_caseiras_info):
        medidas_caseiras_final.append({
            "descricao_medida": medida_info["descricao"],
            "tamanho_medida": medida_info["tamanho"],
            "gramas_equivalentes": medida_info["gramas"],
            "composicao": dados_nutricionais_medidas[i]
        })

    # Estrutura o JSON final para o alimento
    alimento_json = {
        'codigo': cod_alimento,
        'classe': classe_alimento,
        'descricao': descricao,
        'composicao_100g': nutrientes_100g,
        'medidas_caseiras': medidas_caseiras_final
    }

    return alimento_json


def main():
    """
    Função principal que orquestra todo o processo de scraping.
    """
    print("--- FASE 1: Coletando a lista de todos os alimentos ---")
    cod_alimentos = []
    pagina_atual = 1
    while True:
        print(f"Buscando página de listagem nº {pagina_atual}...")
        try:
            response = requests.get(URL_BASE_LISTA, params={'pagina': pagina_atual}, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  [ERRO] Falha ao buscar a página {pagina_atual}. Assumindo fim da lista. Erro: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        
        tr_elements = soup.select('tbody > tr')
        if not tr_elements:
            print("Nenhum alimento encontrado nesta página. Finalizando a coleta da lista.")
            break
        
        for tr in tr_elements:
            tds = tr.find_all('td')
            if len(tds) >= 5:
                cod = tds[0].text.strip()
                classe = tds[4].text.strip()
                cod_alimentos.append((cod, classe))
        
        pagina_atual += 1
        time.sleep(0.5) # Pausa educada para não sobrecarregar o servidor

    cod_alimentos = sorted(list(set(cod_alimentos)))
    print(f"\nColeta da lista finalizada. Total de {len(cod_alimentos)} alimentos únicos encontrados.")
    
    print(f"\n--- FASE 2: Iniciando a extração de dados. Os resultados serão salvos em '{ARQUIVO_SAIDA}' ---")
    
    todos_os_alimentos = []
    try:
        for i, (cod, classe) in enumerate(cod_alimentos):
            print(f"\nProcessando alimento {i + 1} de {len(cod_alimentos)}...")
            dados_alimento = extrair_dados_alimento(cod, classe)
            if dados_alimento:
                todos_os_alimentos.append(dados_alimento)
                print(f"  > Dados de '{dados_alimento['descricao']}' processados com sucesso.")
            
            # Salva o progresso a cada 20 alimentos para não perder o trabalho
            if (i + 1) > 0 and (i + 1) % 20 == 0:
                print(f"\n--- Salvando progresso parcial no arquivo... ---")
                with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as file:
                    json.dump(todos_os_alimentos, file, ensure_ascii=False, indent=4)

            time.sleep(0.5) # Pausa educada

    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário. Salvando os dados coletados até agora...")
    
    finally:
        print(f"\n--- Processo finalizado. Salvando todos os dados em '{ARQUIVO_SAIDA}' ---")
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as file:
            # O parâmetro ensure_ascii=False é o que corrige a codificação.
            # O parâmetro indent=4 formata o JSON para ser mais legível.
            json.dump(todos_os_alimentos, file, ensure_ascii=False, indent=4)
        print("Salvo com sucesso!")


# Ponto de entrada do script
if __name__ == "__main__":
    main()