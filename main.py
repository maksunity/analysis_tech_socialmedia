import pandas as pd
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from src.parser import collect_posts
from src.analyzer import analyze_sentiment
from src.metrics import compute_metrics
from src.classifier import classify
from config import RAW_DATA_PATH, PROCESSED_DATA_PATH, METRICS_DATA_PATH, CLASSIFIED_DATA_PATH

RAW       = os.path.join(BASE_DIR, RAW_DATA_PATH)
PROCESSED = os.path.join(BASE_DIR, PROCESSED_DATA_PATH)
METRICS   = os.path.join(BASE_DIR, METRICS_DATA_PATH)
CLASSIFIED = os.path.join(BASE_DIR, CLASSIFIED_DATA_PATH)

os.makedirs(os.path.join(BASE_DIR, "data/raw"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data/processed"), exist_ok=True)


def step1_parse():
	print("\n[Шаг 1] Сбор данных из Reddit...")
	if os.path.exists(RAW):
		answer = input(f"Файл уже существует ({RAW_DATA_PATH}). Перезаписать? (y/n): ")
		if answer.lower() != "y":
			print("Пропускаем парсинг.")
			return
	collect_posts()


def step2_analyze():
	print("\n[Шаг 2] Анализ тональности заголовков...")
	if not os.path.exists(RAW):
		print(f"Ошибка: сначала выполни шаг 1 (нет файла {RAW_DATA_PATH})")
		return
	df = pd.read_csv(RAW)
	analyze_sentiment(df)


def step3_metrics():
	print("\n[Шаг 3] Вычисление метрик вовлечённости...")
	if not os.path.exists(PROCESSED):
		print(f"Ошибка: сначала выполни шаг 2 (нет файла {PROCESSED_DATA_PATH})")
		return
	df = pd.read_csv(PROCESSED)
	compute_metrics(df)


def step4_classify():
	print("\n[Шаг 4] Классификация постов...")
	if not os.path.exists(METRICS):
		print(f"Ошибка: сначала выполни шаг 3 (нет файла {METRICS_DATA_PATH})")
		return
	df = pd.read_csv(METRICS)
	classify(df)


def step5_summary():
	print("\n[Шаг 5] Итоговая сводка...")
	if not os.path.exists(CLASSIFIED):
		print(f"Ошибка: сначала выполни шаг 4 (нет файла {CLASSIFIED_DATA_PATH})")
		return
	df = pd.read_csv(CLASSIFIED)
	print("\n--- Средние метрики по тональности ---")
	print(df.groupby("sentiment")[["engagement_index", "controversy_index", "score"]].mean().round(2))
	print("\n--- Распределение категорий ---")
	print(df["category"].value_counts())
	print("\n--- Корреляции ---")
	corr_cols = [
		"score",
		"num_comments",
		"upvote_ratio",
		"engagement_index",
		"controversy_index",
		"vader_compound",
	]
	print(df[corr_cols].corr().round(2))


def run_all():
	print("\n[Полный пайплайн] Запускаем все шаги...")
	step1_parse()
	step2_analyze()
	step3_metrics()
	step4_classify()
	step5_summary()


MENU = """
╔══════════════════════════════════════════════╗
║       Reddit Engagement Analysis             ║
╠══════════════════════════════════════════════╣
║  1. Сбор данных из Reddit (parser)           ║
║  2. Анализ тональности (analyzer)            ║
║  3. Метрики вовлечённости (metrics)          ║
║  4. Классификация постов (classifier)        ║
║  5. Итоговая сводка                          ║
║  6. Запустить всё подряд                     ║
║  0. Выход                                    ║
╚══════════════════════════════════════════════╝
"""

ACTIONS = {
	"1": step1_parse,
	"2": step2_analyze,
	"3": step3_metrics,
	"4": step4_classify,
	"5": step5_summary,
	"6": run_all,
}

if __name__ == "__main__":
	while True:
		print(MENU)
		choice = input("Выбери шаг (0-6): ").strip()

		if choice == "0":
			print("Выход.")
			break
		elif choice in ACTIONS:
			ACTIONS[choice]()
			input("\nНажми Enter чтобы вернуться в меню...")
		else:
			print("Неверный ввод, попробуй ещё раз.")