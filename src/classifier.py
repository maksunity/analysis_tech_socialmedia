import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from config import (
    CLASSIFIED_DATA_PATH,
    CONTROVERSY_INDEX_THRESHOLD,
    HIGH_RATIO_THRESHOLD,
    HIGH_SCORE_THRESHOLD,
    LOW_RATIO_THRESHOLD,
    MANY_COMMENTS_THRESHOLD,
    METRICS_DATA_PATH,
    VIRAL_COMMENTS_THRESHOLD,
    VIRAL_SCORE_THRESHOLD,
)


def classify_post(row):
    score = row["score"]
    ratio = row["upvote_ratio"]
    comments = row["num_comments"]
    ci = row["controversy_index"]
    sentiment = row.get("sentiment", "")

    # Вирусные — высокий score и много комментариев одновременно (проверяем первыми)
    if score >= VIRAL_SCORE_THRESHOLD and comments >= VIRAL_COMMENTS_THRESHOLD:
        return f"Вирусные ({sentiment})"

    # Популярные — высокий score, высокое одобрение, мало споров
    elif (
        score >= HIGH_SCORE_THRESHOLD
        and ratio >= HIGH_RATIO_THRESHOLD
        and comments < MANY_COMMENTS_THRESHOLD
    ):
        return f"Популярные ({sentiment})"

    # Спорные — высокий controversy_index + низкий ratio + достаточный score
    elif (
        ci >= CONTROVERSY_INDEX_THRESHOLD
        and ratio <= LOW_RATIO_THRESHOLD
        and score >= HIGH_SCORE_THRESHOLD * 0.3
    ):
        return f"Спорные ({sentiment})"

    # Негативный триггер — много комментов, низкий score и низкое одобрение
    elif (
        comments >= MANY_COMMENTS_THRESHOLD
        and ratio <= LOW_RATIO_THRESHOLD
        and score < HIGH_SCORE_THRESHOLD * 0.3
    ):
        return f"Негативный триггер ({sentiment})"

    # Всё остальное
    else:
        return f"Игнор ({sentiment})"


def classify(df):
    df = df.copy()
    df = df.dropna(subset=["score", "upvote_ratio", "num_comments"])

    df["category"] = df.apply(classify_post, axis=1)

    print("\nРаспределение категорий (абсолютное):")
    print(df["category"].value_counts())

    print("\nРаспределение категорий (доли):")
    print(df["category"].value_counts(normalize=True).round(3))

    print("\nСтатистика по классам:")
    stats = df.groupby("category")[["score", "upvote_ratio", "num_comments"]].mean().round(2)
    print(stats)

    print("\nПримеры постов по категориям:")
    for category in df["category"].unique():
        examples = df[df["category"] == category].head(3)
        print(f"\n{category}:")
        for _, row in examples.iterrows():
            print(f"  '{row['title'][:60]}...' ({row['score']}↑, {row['num_comments']} comments)")

    print("\nСтатистика метрик в классифицированных данных:")
    print(df[["score", "upvote_ratio", "num_comments", "controversy_index"]].describe().round(2))

    # Сохранение — работает и из main.py и напрямую
    classified_path_abs = os.path.join(BASE_DIR, CLASSIFIED_DATA_PATH)
    os.makedirs(os.path.dirname(classified_path_abs), exist_ok=True)
    df.to_csv(classified_path_abs, index=False)
    print(f"\nСохранено: {classified_path_abs}")

    return df


if __name__ == "__main__":
    metrics_path_abs = os.path.join(BASE_DIR, METRICS_DATA_PATH)
    df = pd.read_csv(metrics_path_abs)
    classify(df)

# Консольный вывод:

# Распределение категорий (абсолютное):
# category
# Игнор (negative)                 391
# Игнор (neutral)                  190
# Игнор (positive)                 138
# Спорные (negative)                55
# Вирусные (negative)               42
# Вирусные (neutral)                22
# Спорные (neutral)                 22
# Популярные (negative)             16
# Популярные (neutral)              14
# Спорные (positive)                13
# Вирусные (positive)                8
# Популярные (positive)              7
# Негативный триггер (negative)      3
# Негативный триггер (neutral)       2
# Name: count, dtype: int64

# Распределение категорий (доли):
# category
# Игнор (negative)                 0.424
# Игнор (neutral)                  0.206
# Игнор (positive)                 0.150
# Спорные (negative)               0.060
# Вирусные (negative)              0.046
# Вирусные (neutral)               0.024
# Спорные (neutral)                0.024
# Популярные (negative)            0.017
# Популярные (neutral)             0.015
# Спорные (positive)               0.014
# Вирусные (positive)              0.009
# Популярные (positive)            0.008
# Негативный триггер (negative)    0.003
# Негативный триггер (neutral)     0.002
# Name: proportion, dtype: float64

# Статистика по классам:
#                                   score  upvote_ratio  num_comments
# category
# Вирусные (negative)            30870.07          0.95       3729.71
# Вирусные (neutral)             30621.32          0.95       3191.50
# Вирусные (positive)            26849.38          0.94       2907.50
# Игнор (negative)                5979.33          0.96        419.77
# Игнор (neutral)                 5348.82          0.97        356.43
# Игнор (positive)                6031.91          0.96        374.36
# Негативный триггер (negative)   1951.33          0.79       1294.33
# Негативный триггер (neutral)    2192.50          0.90        849.00
# Популярные (negative)          14095.25          0.98        407.25
# Популярные (neutral)           15033.36          0.98        366.29
# Популярные (positive)          14633.86          0.98        384.86
# Спорные (negative)              9918.87          0.93       1247.67
# Спорные (neutral)               7799.41          0.93       1125.73
# Спорные (positive)              9169.54          0.94       1018.62

# Примеры постов по категориям:

# Вирусные (neutral):
#   'Meta and YouTube found liable in social media addiction tria...' (63182↑, 5368 comments)
#   'Delta temporarily suspends travel perks for members of Congr...' (43105↑, 1075 comments)
#   'Jury sides with rapper Afroman in Adams County trial...' (43092↑, 1274 comments)

# Вирусные (negative):
#   'Pentagon Tells Congress First Week of Iran War Cost More Tha...' (46561↑, 6468 comments)
#   'Exclusive: As many as 150 US troops wounded so far in Iran w...' (43302↑, 8995 comments)
#   'FBI warns Iran aspired to attack California with drones in r...' (40563↑, 13937 comments)

# Игнор (negative):
#   'Death of a refugee left at a Buffalo doughnut shop by Border...' (41329↑, 799 comments)
#   'Ohio firm must pay $22.5 million to mom whose baby died afte...' (28680↑, 975 comments)
#   'Israel backtracks after Italy leads outrage at denied access...' (24713↑, 346 comments)

# Игнор (neutral):
#   'UK government bans Kanye West from entering country...' (32393↑, 486 comments)
#   'Lawyers for ICE gave false information to justify detaining ...' (22985↑, 370 comments)
#   'El Salvador forcibly disappearing nationals deported from th...' (18035↑, 383 comments)

# Вирусные (positive):
#   'Army raises enlistment age to 42, eases marijuana restrictio...' (29324↑, 3402 comments)
#   'Israeli police prevent Catholic leaders from celebrating Pal...' (24730↑, 1225 comments)
#   'Europe tells Trump Iran is 'not our war'...' (32582↑, 1637 comments)

# Игнор (positive):
#   'Ms. Rachel aims to help 'close Dilley' ICE facility after sp...' (26477↑, 438 comments)
#   'Democratic-backed Chris Taylor wins Wisconsin Supreme Court ...' (24806↑, 394 comments)
#   'US fighter jet shot down over Iran, search underway for crew...' (21406↑, 494 comments)

# Популярные (negative):
#   'Epstein victims to get $72.5M from Bank of America settlemen...' (23464↑, 416 comments)
#   '3,800 workers are on strike at one of the largest meatpackin...' (13811↑, 473 comments)
#   'Pope accepts resignation of US bishop who was arrested for a...' (12392↑, 187 comments)

# Спорные (negative):
#   'Full network of clitoral nerves mapped out for first time | ...' (23442↑, 874 comments)
#   'Israeli forces kill Palestinian couple and two of their chil...' (17555↑, 1347 comments)
#   'Kendra Duggar, wife of 19 Kids and Counting's Joseph Duggar,...' (16568↑, 1006 comments)

# Популярные (neutral):
#   'Democrat flips Republican-held Florida state House district ...' (22760↑, 311 comments)
#   'FBI investigation into Kash Patel was more extensive than pr...' (17804↑, 218 comments)
#   'Hegseth has intervened in military promotions for more than ...' (15496↑, 475 comments)

# Спорные (positive):
#   'ASU free speech event canceled allegedly after Erika Kirk ob...' (20732↑, 682 comments)
#   'Defense secretary lifts suspension of 2 pilots of helicopter...' (18979↑, 1191 comments)
#   'Rescue team in Iran face 'harrowing and dangerous' search fo...' (13259↑, 1182 comments)

# Популярные (positive):
#   'World's oldest known tortoise, Jonathan, still alive despite...' (19384↑, 478 comments)
#   'France tells US NATO serves Euro-Atlantic security, not Horm...' (12669↑, 583 comments)
#   'Sri Lanka declares all Wednesdays off to conserve energy...' (10292↑, 309 comments)

# Спорные (neutral):
#   'New Covid variant has been identified and is already spreadi...' (19269↑, 1674 comments)
#   'Israel says it will seize parts of southern Lebanon as ‘defe...' (14528↑, 2320 comments)
#   'Israel deliberately targeting medical facilities in south Le...' (6230↑, 518 comments)

# Негативный триггер (neutral):
#   'Iran fires deadly missile barrage at Israel in ‘revenge’ for...' (2883↑, 723 comments)
#   'Explosion rocks Amsterdam Jewish school in what mayor says i...' (1502↑, 975 comments)

# Негативный триггер (negative):
#   'Jewish volunteer ambulances set on fire outside London synag...' (2243↑, 1530 comments)
#   'Lebanese official says man in Michigan synagogue attack lost...' (1152↑, 1507 comments)
#   'Jewish volunteer ambulances set on fire outside London synag...' (2459↑, 846 comments)

# Статистика метрик в классифицированных данных:
#           score  upvote_ratio  num_comments  controversy_index
# count    923.00        923.00        923.00             923.00
# mean    8403.68          0.96        715.26              36.16
# std     8980.21          0.03       1188.37              89.49
# min      837.00          0.77         10.00               0.20
# 25%     2695.50          0.95        177.50               4.68
# 50%     4798.00          0.97        362.00              12.87
# 75%    10633.00          0.98        736.00              33.30
# max    71815.00          0.99      13937.00            1672.44

# Сохранено: data/processed/posts_classified.csv