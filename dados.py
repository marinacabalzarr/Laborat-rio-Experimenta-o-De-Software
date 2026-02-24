import requests
import json

GITHUB_TOKEN = "TokenGitHub"
API_URL = "https://api.github.com/graphql"

# Query GraphQL que busca os repositórios e extrai as métricas exigidas (idade, issues, pull requests, etc.)
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
    # Cabeçalhos de autenticação obrigatórios para a API do GitHub
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Inicia a busca sem nenhum marcador de página (primeira página)
    variables = {"cursor": None}
    
    # Envia a requisição POST para a API
    response = requests.post(API_URL, json={'query': query, 'variables': variables}, headers=headers)
    
    # Se a requisição for bem-sucedida, retorna os dados em formato JSON
    if response.status_code == 200:
        return response.json()
    return None

if __name__ == "__main__":
    fetch_repos()