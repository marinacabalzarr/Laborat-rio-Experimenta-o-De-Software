import requests
import json
import time
import csv  # Adicionado para gerar o arquivo CSV

# ==========================================
# COLOQUE SEU NOVO TOKEN DO GITHUB AQUI
# ==========================================
GITHUB_TOKEN = "SEU_NOVO_TOKEN_AQUI"
API_URL = "https://api.github.com/graphql"

# Aumentei para 20 repositórios por página para agilizar, mas mantendo a segurança
query = """
query ($cursor: String) {
  search(query: "stars:>100 sort:stars-desc", type: REPOSITORY, first: 20, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt
        updatedAt
        primaryLanguage { name }
        releases { totalCount }
        pullRequests(states: MERGED) { totalCount }
        totalIssues: issues { totalCount }
        closedIssues: issues(states: CLOSED) { totalCount }
      }
    }
  }
}
"""

def fetch_1000_repos():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    todos_repositorios = []
    cursor = None 
    
    print("Iniciando a busca de 1000 repositórios. Isso pode levar de 3 a 5 minutos...")
    
    # Aumentamos o limite para 1000 repositórios
    while len(todos_repositorios) < 1000:
        variables = {"cursor": cursor}
        
        response = requests.post(
            API_URL, 
            json={'query': query, 'variables': variables}, 
            headers=headers
        )
        
        if response.status_code == 200:
            dados = response.json()
            
            if 'errors' in dados:
                print("⚠️ O GitHub engasgou. Esperando 5s para tentar novamente...")
                time.sleep(5)
                continue

            search_data = dados.get('data', {}).get('search', {})
            nodes = search_data.get('nodes', [])
            
            if not nodes:
                break
                
            todos_repositorios.extend(nodes)
            print(f"✅ Baixando... {len(todos_repositorios)}/1000 repositórios coletados.")
            
            page_info = search_data.get('pageInfo', {})
            if page_info.get('hasNextPage'):
                cursor = page_info.get('endCursor')
            else:
                break
            
            time.sleep(2) 
            
        elif response.status_code in [502, 503]:
            print(f"⚠️ Erro {response.status_code}. O GitHub está ocupado. Tentando novamente em 5s...")
            time.sleep(5) 
        else:
            print(f"❌ Erro fatal: {response.status_code} - {response.text}")
            break
            
    return todos_repositorios[:1000]

def salvar_em_csv(repositorios, nome_arquivo='repositorios_sprint2.csv'):
    # Define os cabeçalhos das colunas da nossa planilha
    cabecalhos = [
        "Nome do Repositorio", "Data de Criacao", "Data de Atualizacao", 
        "Linguagem Primaria", "Total de Releases", "Pull Requests Aceitos", 
        "Total de Issues", "Issues Fechadas"
    ]
    
    print(f"\\nIniciando a conversão para {nome_arquivo}...")
    
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=';') # Usando ';' para o Excel abrir certinho no Brasil
        escritor.writerow(cabecalhos)
        
        for repo in repositorios:
            # Extração segura: se não tiver linguagem, coloca "N/A"
            lang_node = repo.get("primaryLanguage")
            linguagem = lang_node.get("name") if lang_node else "N/A"
            
            # Monta a linha com os dados do repositório
            linha = [
                repo.get("nameWithOwner", ""),
                repo.get("createdAt", ""),
                repo.get("updatedAt", ""),
                linguagem,
                repo.get("releases", {}).get("totalCount", 0),
                repo.get("pullRequests", {}).get("totalCount", 0),
                repo.get("totalIssues", {}).get("totalCount", 0),
                repo.get("closedIssues", {}).get("totalCount", 0)
            ]
            
            escritor.writerow(linha)

if __name__ == "__main__":
    repos = fetch_1000_repos()
    
    if repos and len(repos) == 1000:
        # Salva o arquivo CSV conforme exigido na Sprint 2
        salvar_em_csv(repos)
        print("🎉 SUCESSO! Arquivo 'repositorios_sprint2.csv' gerado perfeitamente!")
    else:
        print(f"⚠️ O script parou antes de atingir 1000. Total coletado: {len(repos) if repos else 0}")