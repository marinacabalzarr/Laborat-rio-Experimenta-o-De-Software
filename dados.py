import requests
import json
import time
import csv  # Adicionado para gerar o arquivo CSV

# ==========================================
# COLOQUE SEU NOVO TOKEN DO GITHUB AQUI
# ==========================================
GITHUB_TOKEN = ""
API_URL = "https://api.github.com/graphql"

# Alterado para first: 10 para evitar o erro 502 Bad Gateway
query = """
query ($cursor: String) {
  search(query: "stars:>100 sort:stars-desc", type: REPOSITORY, first: 10, after: $cursor) {
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
    
    print("Iniciando a busca de 1000 repositórios (de 10 em 10).")
    print("Isso deve levar em torno de 5 a 8 minutos. Pode ir pegar um café! ☕")
    
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
            
            # Pausa de 2 segundos para respeitar o limite de requisições do GitHub
            time.sleep(2) 
            
        elif response.status_code in [502, 503]:
            print(f"⚠️ Erro {response.status_code}. O GitHub está ocupado. Tentando novamente em 5s...")
            time.sleep(5) 
        else:
            print(f"❌ Erro fatal: {response.status_code} - {response.text}")
            break
            
    # Retorna no máximo 1000, caso passe um pouquinho no último lote
    return todos_repositorios[:1000]

def salvar_em_csv(repositorios, nome_arquivo='repositorios_sprint2.csv'):
    cabecalhos = [
        "Nome do Repositorio", "Data de Criacao", "Data de Atualizacao", 
        "Linguagem Primaria", "Total de Releases", "Pull Requests Aceitos", 
        "Total de Issues", "Issues Fechadas"
    ]
    
    print(f"\\nIniciando a conversão para {nome_arquivo}...")
    
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=';')
        escritor.writerow(cabecalhos)
        
        for repo in repositorios:
            lang_node = repo.get("primaryLanguage")
            linguagem = lang_node.get("name") if lang_node else "N/A"
            
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
        salvar_em_csv(repos)
        print("🎉 SUCESSO! Arquivo 'repositorios_sprint2.csv' gerado perfeitamente!")
    else:
        print(f"⚠️ O script parou antes de atingir 1000. Total coletado: {len(repos) if repos else 0}")
        # Tenta salvar mesmo se não tiver chegado a 1000 para você não perder os dados
        if repos:
            salvar_em_csv(repos, 'repositorios_incompletos.csv')