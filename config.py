# Параметры парсинга
SUBREDDITS = ["news", "worldnews"]
POST_LIMIT = 1000
POSTS_PER_REQUEST = 100  # Максимум для .json (не больше 100-250) .json дает 100 max за раз, для 1000 нужно несколько запросов с пагинацией (after)
SORT_TYPE = "top"  # hot | new | top
TIME_FILTER = "month"  # day | week | month | year | all

# Пути к данным
RAW_DATA_PATH = "data/raw/posts.csv"
PROCESSED_DATA_PATH = "data/processed/posts_analyzed.csv"
METRICS_DATA_PATH = "data/processed/posts_with_metrics.csv"
CLASSIFIED_DATA_PATH = "data/processed/posts_classified.csv"

# Пороги для классификатора — подобраны под реальные перцентили r/news + r/worldnews

# score: 25%=2689, 50%=4798, 75%=10707, max=71795
HIGH_SCORE_THRESHOLD = 10000       # 75й перцентиль — пост популярный

# upvote_ratio: 25%=0.95, 50%=0.97, 75%=0.98
HIGH_RATIO_THRESHOLD = 0.98        # выше медианы
LOW_RATIO_THRESHOLD = 0.95         # ниже 25го перцентиля — спорный для этих сабреддитов

# num_comments: 25%=177, 50%=360, 75%=732, max=13937
MANY_COMMENTS_THRESHOLD = 700      # 75й перцентиль — много обсуждений

# controversy_index: 25%=4.71, 50%=12.90, 75%=32.94, max=1672
CONTROVERSY_INDEX_THRESHOLD = 33   # 75й перцентиль — спорный пост

# Пороги VADER для классификации тональности
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05

VIRAL_SCORE_THRESHOLD = 20000     # топ ~10% по score
VIRAL_COMMENTS_THRESHOLD = 1000   # топ ~15% по comments

#Статистика метрик в классифицированных данных:
#           score  upvote_ratio  num_comments  controversy_index
# count    935.00        935.00        935.00             935.00
# mean    8408.61          0.96        711.47              36.00
# std     9004.65          0.03       1182.40              89.03
# min      837.00          0.77         10.00               0.20
# 25%     2689.50          0.95        177.50               4.71
# 50%     4798.00          0.97        360.00              12.90
# 75%    10707.00          0.98        732.50              32.94
# max    71795.00          0.99      13937.00            1672.44
