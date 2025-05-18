import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel("Apple marca análise de sentimento.xlsx")

df.columns = df.columns.str.strip()

tweets = df["Texto"] 

analyzer = SentimentIntensityAnalyzer()

def analisar_sentimento(texto):
    scores = analyzer.polarity_scores(str(texto))
    return pd.Series([scores['neg'], scores['neu'], scores['pos'], scores['compound']])

df[['neg', 'neu', 'pos', 'compound']] = tweets.apply(analisar_sentimento)

def classificar_sentimento(compound):
    if compound >= 0.05:
        return "positivo"
    elif compound <= -0.05:
        return "negativo"
    else:
        return "neutro"

df["sentimento"] = df["compound"].apply(classificar_sentimento)

df.to_excel("Vader_tweets_apple_analisados.xlsx", index=False)
print("Arquivo salvo com sucesso!")