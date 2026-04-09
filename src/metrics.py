import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from config import PROCESSED_DATA_PATH, METRICS_DATA_PATH


def compute_metrics(df):
	print("Вычисляем метрики вовлечённости...")

	df = df.copy()

	# Очистка
	df = df.dropna(subset=["score", "num_comments", "upvote_ratio"])
	df["upvote_ratio"] = df["upvote_ratio"].fillna(1.0)

	# Основные метрики
    # Индекс вовлечённости
	df["engagement_index"] = df["num_comments"] / (df["score"] + 1) 
      	# Cколько обсуждения приходится на единицу апвотов. +1: защита от деления на ноль при score = 0.
		# Высокий: много комментариев относительно лайков, пост “обсуждаемый”.
		# Низкий: лайков много, но обсуждение слабее.
    # Индекс спорности
	df["controversy_index"] = df["num_comments"] * (1 - df["upvote_ratio"])
		# Спорность через комбинацию объема обсуждения и доли дизсогласия аудитории.
		# Если upvote_ratio близок к 1, множитель малый, спорность падает.
		# Если upvote_ratio ниже и комментариев много, индекс растет.

	# Дополнительные метрики
    # Индекс "ярости" (rage_ratio) — сочетание вовлечённости и негативной реакции
	df["rage_ratio"] = df["engagement_index"] * (1 - df["upvote_ratio"]) # Напряженное обсуждение с поправкой на спорность реакции. 
    
	# Общая вовлечённость (total_interaction) — сумма лайков и комментариев
	df["total_interaction"] = df["score"] + df["num_comments"]
    
	# Сила эмоций (emotion_strength) — абсолютное значение compound от VADER, чтобы оценить интенсивность эмоциональной реакции независимо от её полярности. И позитивный, и негативный “сильный” пост получат высокое значение.
	df["emotion_strength"] = df["vader_compound"].abs()
      

	print("\nСтатистики метрик:")
	print(df[["engagement_index", "controversy_index", "rage_ratio"]].describe().round(2))

	return df


if __name__ == "__main__":
    processed_path_abs = os.path.join(BASE_DIR, PROCESSED_DATA_PATH)
    metrics_path_abs = os.path.join(BASE_DIR, METRICS_DATA_PATH)

    df = pd.read_csv(processed_path_abs)
    df = compute_metrics(df)

    print("\nКорреляции:")
    corr_cols = ["score", "num_comments", "upvote_ratio",
                 "engagement_index", "controversy_index",
                 "rage_ratio", "vader_compound"]
    print(df[corr_cols].corr().round(2))

    os.makedirs(os.path.dirname(metrics_path_abs), exist_ok=True)
    df.to_csv(metrics_path_abs, index=False) 
    print(f"Сохранено: {metrics_path_abs}")
    
# Консольный вывод:
# Вычисляем метрики вовлечённости...

# Статистики метрик:
#        engagement_index  controversy_index  rage_ratio
# count            923.00             923.00      923.00
# mean               0.09              36.16        0.00
# std                0.08              89.49        0.01
# min                0.00               0.20        0.00
# 25%                0.04               4.68        0.00
# 50%                0.07              12.87        0.00
# 75%                0.12              33.30        0.01
# max                1.31            1672.44        0.30

# Корреляции:
#                    score  num_comments  upvote_ratio  engagement_index  controversy_index  rage_ratio  vader_compound
# score               1.00          0.66         -0.01             -0.07               0.48       -0.05           -0.02
# num_comments        0.66          1.00         -0.22              0.39               0.91        0.20           -0.07
# upvote_ratio       -0.01         -0.22          1.00             -0.57              -0.38       -0.64            0.09
# engagement_index   -0.07          0.39         -0.57              1.00               0.45        0.83           -0.07
# controversy_index   0.48          0.91         -0.38              0.45               1.00        0.36           -0.08
# rage_ratio         -0.05          0.20         -0.64              0.83               0.36        1.00           -0.06
# vader_compound     -0.02         -0.07          0.09             -0.07              -0.08       -0.06            1.00
# Сохранено: data/processed/posts_with_metrics.csv

# upvote_ratio → engagement_index  : -0.57  ключевой результат
# upvote_ratio → rage_ratio        : -0.64  подтверждение гипотезы
# vader_compound → num_comments    : -0.07  слабая связь тональности
# vader_compound → controversy     : -0.08  и вовлечённости