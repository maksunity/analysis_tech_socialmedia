import os
import sys
import time

import pandas as pd
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
	POST_LIMIT,
	POSTS_PER_REQUEST,
	RAW_DATA_PATH,
	SORT_TYPE,
	SUBREDDITS,
	TIME_FILTER,
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH_ABS = os.path.join(BASE_DIR, RAW_DATA_PATH)

def collect_from_subreddit(subreddit, limit, headers):
	posts = []
	after = None
	max_requests = 15
	request_count = 0

	print(f"\nПарсим r/{subreddit}, {SORT_TYPE} за {TIME_FILTER}...")

	while len(posts) < limit:
		if request_count >= max_requests:
			print(f"Достигнут лимит запросов ({max_requests})")
			break

		url = f"https://www.reddit.com/r/{subreddit}/{SORT_TYPE}.json"
		params = {"limit": POSTS_PER_REQUEST, "t": TIME_FILTER}
		# Пагинация страниц через параметр "after"
		if after:
			params["after"] = after

		try:
			response = requests.get(url, headers=headers, params=params, timeout=10)
			response.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(f"Ошибка запроса: {e}")
			break

		data = response.json()["data"]
		request_count += 1
		new_posts = 0

		for post in data["children"]:
			if len(posts) >= limit:
				break
			p = post["data"]
			posts.append(
				{
					#p.get - безопасный доступ к полям, чтобы избежать KeyError
					"id": p.get("id", ""),
					"title": p.get("title", ""),
					"score": p.get("score", 0),
					"upvote_ratio": p.get("upvote_ratio", 0.0),
					"num_comments": p.get("num_comments", 0),
					"created_utc": p.get("created_utc", 0),
					"permalink": p.get("permalink", ""),
					"subreddit": subreddit,
				}
			)
			new_posts += 1

		print(f"  Запрос {request_count}: +{new_posts} постов, всего {len(posts)}")

		after = data.get("after")
		if not after:
			print("  Больше постов нет")
			break

		time.sleep(1)

	return posts


def collect_posts():
	all_posts = []
	headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

	# Делим лимит равномерно между сабреддитами
	limit_per_subreddit = POST_LIMIT // len(SUBREDDITS)

	for subreddit in SUBREDDITS:
		posts = collect_from_subreddit(subreddit, limit_per_subreddit, headers)
		all_posts.extend(posts)

	df = pd.DataFrame(all_posts)

	# Дедупликация по id (на случай пересечений между сабреддитами)
	before = len(df)
	df = df.drop_duplicates(subset="id")
	after_dedup = len(df)
	if before != after_dedup:
		print(f"Удалено дубликатов: {before - after_dedup}")

	os.makedirs(os.path.dirname(RAW_DATA_PATH_ABS), exist_ok=True)
	df.to_csv(RAW_DATA_PATH_ABS, index=False)
	print(f"\nГотово. Собрано постов: {len(df)} → {RAW_DATA_PATH_ABS}")
	return df


if __name__ == "__main__":
	collect_posts()

#Консольный вывод:
# Парсим r/news, top за month...
#   Запрос 1: +100 постов, всего 100
#   Запрос 2: +100 постов, всего 200
#   Запрос 3: +100 постов, всего 300
#   Запрос 4: +100 постов, всего 400
#   Запрос 5: +58 постов, всего 458
#   Больше постов нет

# Парсим r/worldnews, top за month...
#   Запрос 1: +100 постов, всего 100
#   Запрос 2: +100 постов, всего 200
#   Запрос 3: +100 постов, всего 300
#   Запрос 4: +100 постов, всего 400
#   Запрос 5: +65 постов, всего 465
#   Больше постов нет