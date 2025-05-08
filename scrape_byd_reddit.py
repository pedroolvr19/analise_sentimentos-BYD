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

# Listas de frases (somente em inglês)
frases_positivas_en = [
    "beauty", "beautiful", "recommendation", "recommended", "great", "amazing", "love it",
    "fantastic", "superb", "works well", "very good", "adore", "excellent", "awesome",
    "highly recommend", "good", "nice", "pleased", "happy", "satisfied"
]

frases_negativas_en = [
    "issues", "issue", "problem", "problems", "battery loss", "battery drain", "not working",
    "terrible", "awful", "never again", "very bad", "garbage", "disappointing", "shit", "bugged",
    "poor", "bad", "unhappy", "dissatisfied", "broken", "faulty", "useless", "waste", "don't buy"
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

# Função de detecção de sentimento (apenas Positivo ou Negativo, focado em inglês)
def detectar_sentimento_binario_ingles(texto):
    texto_processado = preprocessar(texto)
    tem_positivo = any(frase in texto_processado for frase in frases_positivas_en)
    tem_negativo = any(frase in texto_processado for frase in frases_negativas_en)

    if tem_positivo:
        return "Positivo"
    elif tem_negativo:
        return "Negativo"
    else:
        return None  # Indica que não foi classificado como positivo ou negativo

# Função para extrair posts do Reddit via scraping
def scrape_reddit_posts(subreddit, limite=50):
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

            contador = 0
            for post in posts:
                if contador >= limite:
                    break

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

                # Analisar sentimento do título (usando a função binária focada em inglês)
                sentimento = detectar_sentimento_binario_ingles(titulo)

                if sentimento:
                    # Adicionar dados apenas se o sentimento for Positivo ou Negativo
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

                contador += 1

            print(f"Coletados {len(dados)} posts (apenas Positivos e Negativos em inglês)")

        else:
            print(f"Erro ao acessar o subreddit: {response.status_code}")

    except Exception as e:
        print(f"Erro durante o scraping: {e}")

    return dados

# Função para coletar posts de várias categorias
def coletar_posts_reddit(subreddit, limite_por_categoria=25):
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

                contador = 0
                for post in posts:
                    if contador >= limite_por_categoria:
                        break

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

                    # Analisar sentimento do título (usando a função binária focada em inglês)
                    sentimento = detectar_sentimento_binario_ingles(titulo)

                    if sentimento:
                        # Adicionar dados apenas se o sentimento for Positivo ou Negativo
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

                    contador += 1

                print(f"Coletados {contador} posts da categoria {categoria if categoria else 'hot'} (apenas Positivos e Negativos em inglês)")
                # Pausa para evitar bloqueio por muitas requisições
                time.sleep(2)

            else:
                print(f"Erro ao acessar {url}: {response.status_code}")

        except Exception as e:
            print(f"Erro ao processar categoria {categoria}: {e}")

    return todos_dados

# Programa principal
try:
    # Coletar posts do subreddit BYD
    posts = coletar_posts_reddit("BYD", limite_por_categoria=25)

    print(f"Total de posts coletados para análise: {len(posts)}")

    # Criar DataFrames separados para posts positivos e negativos
    positivos = [post for post in posts if post['Sentimento'] == 'Positivo']
    negativos = [post for post in posts if post['Sentimento'] == 'Negativo']

    df_positivos = pd.DataFrame(positivos)
    df_negativos = pd.DataFrame(negativos)

    # Adicionar uma coluna indicando o sentimento em cada DataFrame
    if not df_positivos.empty:
        df_positivos['Tipo_Sentimento'] = 'Positivo'
    if not df_negativos.empty:
        df_negativos['Tipo_Sentimento'] = 'Negativo'

    # Concatenar os DataFrames
    df_combinado = pd.concat([df_positivos, df_negativos], ignore_index=True)

    # Exportar o DataFrame combinado para um CSV
    if not df_combinado.empty:
        df_combinado.to_csv("sentimentos_BYD_reddit_positivos_negativos_en_binario.csv", index=False, encoding='utf-8')
        print("Análise concluída com sucesso. Arquivo salvo como 'sentimentos_BYD_reddit_positivos_negativos_en_binario.csv'")
    else:
        print("Nenhum post positivo ou negativo (em inglês) encontrado para salvar.")

except Exception as e:
    print(f"Ocorreu um erro geral: {e}")
    # Se temos alguns dados, tentamos salvar mesmo assim
    if 'posts' in locals() and posts:
        # Criar DataFrames separados para posts positivos e negativos
        positivos_erro = [post for post in posts if post['Sentimento'] == 'Positivo']
        negativos_erro = [post for post in posts if post['Sentimento'] == 'Negativo']

        df_positivos_erro = pd.DataFrame(positivos_erro)
        df_negativos_erro = pd.DataFrame(negativos_erro)

        # Adicionar uma coluna indicando o sentimento em cada DataFrame
        if not df_positivos_erro.empty:
            df_positivos_erro['Tipo_Sentimento'] = 'Positivo'
        if not df_negativos_erro.empty:
            df_negativos_erro['Tipo_Sentimento'] = 'Negativo'

        # Concatenar os DataFrames
        df_combinado_erro = pd.concat([df_positivos_erro, df_negativos_erro], ignore_index=True)
        if not df_combinado_erro.empty:
            df_combinado_erro.to_csv("sentimentos_BYD_reddit_positivos_negativos_en_binario_parcial.csv", index=False, encoding='utf-8')
            print(f"Salvos {len(df_combinado_erro)} posts positivos e negativos (em inglês) coletados antes do erro em 'sentimentos_BYD_reddit_positivos_negativos_en_binario_parcial.csv'")
        else:
            print("Nenhum post positivo ou negativo (em inglês) encontrado para salvar parcialmente.")