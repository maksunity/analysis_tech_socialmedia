import os
import sys

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from config import NEGATIVE_THRESHOLD, POSITIVE_THRESHOLD, PROCESSED_DATA_PATH, RAW_DATA_PATH

# VADER инициализируется один раз на уровне модуля чтобы не создавать новый экземпляр для каждой строки
sia = SentimentIntensityAnalyzer()


def get_sentiment_label(compound):
	if compound >= POSITIVE_THRESHOLD:
		return "positive"
	elif compound <= NEGATIVE_THRESHOLD:
		return "negative"
	return "neutral"


def analyze_sentiment(df):
	# Очистка пустых заголовков
	df = df.copy()
	df["title"] = df["title"].fillna("").astype(str)

	# Полные VADER scores
	df["vader_scores"] = df["title"].apply(lambda t: sia.polarity_scores(t)) # Промежуточный словарь от VADER (с ключами 'neg', 'neu', 'pos', 'compound')
	df["vader_compound"] = df["vader_scores"].apply(lambda s: s["compound"]) # Выделяем только compound для классификации ( от -1 до 1)
	df["vader_pos"] = df["vader_scores"].apply(lambda s: s["pos"]) # Для позитивной оценки
	df["vader_neg"] = df["vader_scores"].apply(lambda s: s["neg"]) # Для негативной оценки
	df["vader_neu"] = df["vader_scores"].apply(lambda s: s["neu"]) # Для нейтральной оценки
	df = df.drop(columns=["vader_scores"])  # убираем словарь, оставляем числа

	df["sentiment"] = df["vader_compound"].apply(get_sentiment_label) # Классификация на основе compound с порогами из config.py

	print("\nРаспределение тональности:")
	print(df["sentiment"].value_counts())
	print(f"\nСредний compound: {df['vader_compound'].mean():.3f}")

	# Сохранение
	os.makedirs(os.path.join(BASE_DIR, os.path.dirname(PROCESSED_DATA_PATH)), exist_ok=True)
	processed_path_abs = os.path.join(BASE_DIR, PROCESSED_DATA_PATH)
	df.to_csv(processed_path_abs, index=False)
	print(f"Сохранено: {processed_path_abs}")

	return df


if __name__ == "__main__":
	raw_path_abs = os.path.join(BASE_DIR, RAW_DATA_PATH)
	df = pd.read_csv(raw_path_abs)
	df = analyze_sentiment(df)
	print(df[["title", "sentiment", "vader_compound"]].head(10))

# Консольный вывод:
# Распределение тональности:
# sentiment
# negative    507
# neutral     250
# positive    166
# Name: count, dtype: int64

# Средний compound: -0.214
# Сохранено: data/processed/posts_analyzed.csv
#                                                title sentiment  vader_compound
# 0  Meta and YouTube found liable in social media ...   neutral          0.0000
# 1  Pentagon Tells Congress First Week of Iran War...  negative         -0.5994
# 2  Exclusive: As many as 150 US troops wounded so...  negative         -0.5267
# 3  Delta temporarily suspends travel perks for me...   neutral          0.0000
# 4  Jury sides with rapper Afroman in Adams County...   neutral          0.0000
# 5  Death of a refugee left at a Buffalo doughnut ...  negative         -0.5994
# 6  FBI warns Iran aspired to attack California wi...  negative         -0.7351
# 7  Pentagon preparing for weeks of ground operati...   neutral          0.0000
# 8  Charlie Kirk bullet analysis finds no conclusi...  negative         -0.2960
# 9  Former FBI Director Robert Mueller, who invest...   neutral          0.0000