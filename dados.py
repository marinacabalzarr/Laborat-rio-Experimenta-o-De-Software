import requests
import json

GITHUB_TOKEN = "SEU_NOVO_TOKEN_AQUI"

API_URL = "https://api.github.com/graphql"

query = """
query ($cursor: String) {
  search(query: "stars:>10000 sort:stars-desc", type: REPOSITORY, first: 10, after: $cursor) {
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

def fetch_repos():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("Testando conexão com o GitHub API...")
    variables = {"cursor": None}
    
    response = requests.post(API_URL, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        print("✅ Conexão bem sucedida! Primeira página capturada.")
        return dados
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")
        return None

if _name_ == "_main_":
    fetch_repos()