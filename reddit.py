import pandas as pd
import unicodedata
import string
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

# Configurar headers para parecer um navegador comum
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Listas de frases (em inglês e português)
frases_positivas = [
    "beauty", "beautiful", "recommendation", "recommended", "great", "amazing", "love it",
    "fantastic", "superb", "works well", "very good", "adore", "excellent", "awesome",
    "highly recommend", "good", "nice", "pleased", "happy", "satisfied",
    "beleza", "bonito", "recomendação", "recomendado", "ótimo", "incrível", "amo",
    "fantástico", "excelente", "funciona bem", "muito bom", "adoro", "sensacional",
    "altamente recomendado", "bom", "legal", "satisfeito", "feliz"
]

frases_negativas = [
    "issues", "issue", "problem", "problems", "battery loss", "battery drain", "not working",
    "terrible", "awful", "never again", "very bad", "garbage", "disappointing", "shit", "bugged",
    "poor", "bad", "unhappy", "dissatisfied", "broken", "faulty", "useless", "waste", "don't buy",
    "problemas", "problema", "perda de bateria", "dreno de bateria", "não funciona",
    "terrível", "horrível", "nunca mais", "muito ruim", "lixo", "decepcionante", "merda", "com bugs",
    "pobre", "ruim", "infeliz", "insatisfeito", "quebrado", "defeituoso", "inútil", "desperdício", "não compre"
]

# Função de pré-processamento de texto
def preprocessar(texto):
    if texto is None or not isinstance(texto, str):
        return ""
    # Converter para minúsculas
    texto = texto.lower()
    # Remover acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Remover pontuação
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

# Função de detecção de sentimento (Positivo ou Negativo)
def detectar_sentimento_binario(texto):
    texto_processado = preprocessar(texto)
    tem_positivo = any(frase in texto_processado for frase in frases_positivas)
    tem_negativo = any(frase in texto_processado for frase in frases_negativas)

    if tem_positivo and not tem_negativo:
        return "Positivo"
    elif tem_negativo and not tem_positivo:
        return "Negativo"
    else:
        return "Negativo"  # Classifica como negativo se não for positivo


# Função para extrair posts do Reddit via scraping
def scrape_reddit_posts(subreddit):
    dados = []
    url = f"https://old.reddit.com/r/{subreddit}"

    print(f"Coletando posts do subreddit r/{subreddit} via web scraping...")

    try:
        # Fazer requisição para a página do subreddit
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Parsear o HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrar todos os posts
            posts = soup.find_all('div', class_='thing')

            for post in posts:
                # Extrair título
                titulo_element = post.find('a', class_='title')
                titulo = titulo_element.text.strip() if titulo_element else "Sem título"

                # Extrair link do post
                post_link = titulo_element['href'] if titulo_element and 'href' in titulo_element.attrs else ""
                if post_link.startswith('/r/'):
                    post_link = f"https://www.reddit.com{post_link}"

                # Extrair autor
                autor_element = post.find('a', class_='author')
                autor = autor_element.text if autor_element else "Desconhecido"

                # Extrair pontuação
                score_element = post.find('div', class_='score unvoted')
                score = score_element.text if score_element else "0"
                try:
                    score = int(score)
                except:
                    score = 0

                # Extrair tempo
                time_element = post.find('time')
                post_time = time_element['datetime'] if time_element and 'datetime' in time_element.attrs else ""

                # Analisar sentimento do título
                sentimento = detectar_sentimento_binario(titulo)

                # Adicionar dados do post com o sentimento analisado
                dados.append({
                    "Título": titulo,
                    "Texto": "",  # Texto vazio porque não temos acesso ao conteúdo do post nesta visualização
                    "Sentimento": sentimento,
                    "URL": post_link,
                    "Subreddit": subreddit,
                    "Data": post_time,
                    "Autor": autor,
                    "Score": score
                })

            print(f"Coletados e analisados {len(dados)} posts")

        else:
            print(f"Erro ao acessar o subreddit: {response.status_code}")

    except Exception as e:
        print(f"Erro durante o scraping: {e}")

    return dados

# Função para coletar posts de várias categorias
def coletar_posts_reddit(subreddit):
    todos_dados = []
    categorias = ["", "top/", "new/", "rising/"]

    for categoria in categorias:
        url = f"https://old.reddit.com/r/{subreddit}/{categoria}"
        print(f"Acessando: {url}")

        try:
            # Fazer requisição para a página do subreddit
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # Parsear o HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Encontrar todos os posts
                posts = soup.find_all('div', class_='thing')

                for post in posts:
                    # Extrair título
                    titulo_element = post.find('a', class_='title')
                    titulo = titulo_element.text.strip() if titulo_element else "Sem título"

                    # Extrair link do post
                    post_link = titulo_element['href'] if titulo_element and 'href' in titulo_element.attrs else ""
                    if post_link.startswith('/r/'):
                        post_link = f"https://www.reddit.com{post_link}"

                    # Extrair autor
                    autor_element = post.find('a', class_='author')
                    autor = autor_element.text if autor_element else "Desconhecido"

                    # Extrair pontuação
                    score_element = post.find('div', class_='score unvoted')
                    score = score_element.text if score_element else "0"
                    try:
                        score = int(score)
                    except:
                        score = 0

                    # Extrair tempo
                    time_element = post.find('time')
                    post_time = time_element['datetime'] if time_element and 'datetime' in time_element.attrs else ""

                    # Analisar sentimento do título
                    sentimento = detectar_sentimento_binario(titulo)

                    # Adicionar dados do post com o sentimento analisado
                    todos_dados.append({
                        "Título": titulo,
                        "Texto": "",  # Texto vazio porque não temos acesso ao conteúdo do post nesta visualização
                        "Sentimento": sentimento,
                        "URL": post_link,
                        "Subreddit": subreddit,
                        "Categoria": categoria.strip('/') if categoria else "hot",
                        "Data": post_time,
                        "Autor": autor,
                        "Score": score
                    })

                print(f"Coletados e analisados {len(posts)} posts da categoria {categoria if categoria else 'hot'}")
                # Pausa para evitar bloqueio por muitas requisições
                time.sleep(2)

            else:
                print(f"Erro ao acessar {url}: {response.status_code}")

        except Exception as e:
            print(f"Erro ao processar categoria {categoria}: {e}")

    return todos_dados

# Função para identificar falsos positivos e negativos
def identificar_falsos(df, frases_positivas, frases_negativas):
    falsos_positivos = []
    falsos_negativos = []
    
    for index, row in df.iterrows():
        titulo = preprocessar(row['Título'])
        sentimento_previsto = row['Sentimento']
        
        tem_positivo = any(frase in titulo for frase in frases_positivas)
        tem_negativo = any(frase in titulo for frase in frases_negativas)
        
        if sentimento_previsto == "Positivo" and tem_negativo:
            falsos_positivos.append(row.to_dict())
        elif sentimento_previsto == "Negativo" and tem_positivo:
            falsos_negativos.append(row.to_dict())
            
    return pd.DataFrame(falsos_positivos), pd.DataFrame(falsos_negativos)

# Programa principal
try:
    # Coletar e analisar posts do subreddit apple
    posts = coletar_posts_reddit("apple")

    print(f"Total de posts coletados e analisados: {len(posts)}")

    # Criar DataFrame com todos os posts e seus sentimentos
    df_analisado = pd.DataFrame(posts)

    # Identificar falsos positivos e negativos
    df_falsos_positivos, df_falsos_negativos = identificar_falsos(df_analisado, frases_positivas, frases_negativas)

    # Contar a ocorrência de cada sentimento
    contagem_sentimentos = df_analisado['Sentimento'].value_counts()
    print("\nContagem de Sentimentos:")
    print(contagem_sentimentos)

    # Exibir resultados
    print("\nResultados:")
    print(df_analisado.to_string(index=False))

    # Exportar os resultados para um único arquivo CSV, sem duplicatas
    df_analisado.drop_duplicates(subset=['Título'], inplace=True)  # Remover duplicatas pelo título
    df_analisado.to_csv("sentimentos_apple_reddit_todos.csv", index=False, encoding='utf-8')

    print("Análise concluída com sucesso. Os resultados foram salvos em 'sentimentos_apple_reddit_todos.csv'")

except Exception as e:
    print(f"Ocorreu um erro geral: {e}")
    # Se temos alguns dados, tentamos salvar mesmo assim
    if 'posts' in locals() and posts:
        try:
            df_analisado_erro = pd.DataFrame(posts)
            df_analisado_erro.drop_duplicates(subset=['Título'], inplace=True)  # Remover duplicatas antes de salvar
            df_analisado_erro.to_csv("sentimentos_apple_reddit_todos_parcial.csv", index=False, encoding='utf-8')
            print(f"Salvos {len(df_analisado_erro)} posts com análise de sentimento coletados antes do erro em 'sentimentos_apple_reddit_todos_parcial.csv'")
        except Exception as e_salvar:
            print(f"Erro ao salvar arquivo parcial: {e_salvar}")
            print("Por favor, verifique as permissões de escrita no diretório e tente novamente.")
    else:
        print("Nenhum post foi coletado para salvar parcialmente.")
