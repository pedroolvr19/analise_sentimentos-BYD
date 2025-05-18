import requests
import pandas as pd
from datetime import datetime

frases_positivas = [
    "otimo", "excelente", "funciona bem", "gostei muito", "gostei mt",
    "recomendo", "incrivel", "muito bom", "mt bom",  "adoro", "maravilhoso", "perfeito"
]

frases_negativas = [
    "pessimo", "horrivel", "nao funciona", "odiei", "n", "lixo",
    "terrivel", "nunca mais", "muito ruim", "mt ruim", "lixo", "decepcionante", "merda", "caralho", "bugado"
]

def gerar_query(base_keywords, frases):
    frases_query = " OR ".join([f'"{frase}"' if " " in frase else frase for frase in frases])
    base_query = " OR ".join(base_keywords)
    return f"({base_query}) ({frases_query}) lang:pt -is:retweet"

# Parâmetros
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAABUN1QEAAAAA9fYZsiKBuKlHOQYVS0FZzEUSzfo%3D7FTNZTd96mf4SLcwD2ZeexgnMAwclueVuovBkkxDe5b0y' 
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
base_keywords = ["apple", "iphone", "macbook"]

# Função para buscar e salvar tweets
def buscar_e_salvar(query, nome_arquivo):
    params = {
        "query": query,
        "tweet.fields": "created_at,lang",
        "expansions": "author_id",
        "user.fields": "location,username",
        "max_results": 100
    }

    response = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    data = response.json()

    if "data" not in data:
        print(f"Nenhum tweet encontrado para: {nome_arquivo}")
        return

    tweets = data["data"]
    users = {u["id"]: u for u in data["includes"]["users"]}
    rows = []

    for tweet in tweets:
        user = users[tweet["author_id"]]
        rows.append({
            "usuario": user["username"],
            "texto": tweet["text"],
            "link": f"https://twitter.com/{user['username']}/status/{tweet['id']}",
            "data": tweet["created_at"],
            "local": user.get("location", "Desconhecido")
        })

    df = pd.DataFrame(rows)
    df.to_excel(nome_arquivo, index=False)
    print(f"Salvo: {nome_arquivo}")

query_positiva = gerar_query(base_keywords, frases_positivas)
query_negativa = gerar_query(base_keywords, frases_negativas)

buscar_e_salvar(query_positiva, "tweets_positivos.xlsx")
buscar_e_salvar(query_negativa, "tweets_negativos.xlsx")