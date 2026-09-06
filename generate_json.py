import json
import re
from urllib.request import urlopen
from pathlib import Path

# アプリで使うカテゴリとカテゴリごとの問題数
SOURCE_FILE = Path(__file__).with_name("jmdict_source.json")
OUTPUT_FILE = Path(__file__).with_name("kanji_data.json")
CATEGORY_LIMITS = {
    "小学1年": 1,
    "小学2年": 2,
    "小学3年": 3,
    "小学4年": 4,
    "小学5年": 5,
    "小学6年": 6,
    "中学生": 7,
    "高校生": 8,
    "一般常識": 9,
    "漢字王": 10,
}
QUESTIONS_PER_CATEGORY = 10000
KANA_RUN = re.compile(r"[ぁ-ゖァ-ヶー]+")
KANJI = re.compile(r"[一-龯々〆ヵヶ]")
GRADE_DATA_URL = "https://raw.githubusercontent.com/davidluzgouveia/kanji-data/master/kanji.json"

def load_grade_data():
    with urlopen(GRADE_DATA_URL, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def difficulty_score(item, grade_data):
    grade = item_grade(item, grade_data)
    kanji = "".join(KANJI.findall(item["kanji"]))
    grades = [grade_data.get(char, {}).get("grade") or 7 for char in kanji]
    return (max(grades, default=7), sum(grades) / max(len(grades), 1), len(kanji), len(item["reading"]), item["kanji"])

def item_grade(item, grade_data):
    kanji = "".join(KANJI.findall(item["kanji"]))
    return max(
        [grade_data.get(char, {}).get("grade") or 7 for char in kanji],
        default=7,
    )

def kanji_reading(item):
    reading = item["reading"]
    for kana_run in KANA_RUN.findall(item["kanji"]):
        normalized_run = kana_run.translate(str.maketrans("ァィゥェォャュョッヮ", "ぁぃぅぇぉゃゅょっゎ"))
        normalized_reading = reading.translate(str.maketrans("ァィゥェォャュョッヮ", "ぁぃぅぇぉゃゅょっゎ"))
        position = normalized_reading.find(normalized_run)
        if position >= 0:
            reading = normalized_reading[:position] + normalized_reading[position + len(normalized_run):]
    return reading

def generate_questions():
    with SOURCE_FILE.open(encoding="utf-8") as f:
        source_questions = json.load(f)
    if len(source_questions) == 0:
        raise ValueError("自然な元データがありません")

    grade_data = load_grade_data()
    source_questions = sorted(source_questions, key=lambda item: difficulty_score(item, grade_data))
    all_data = {}
    for category, grade_limit in CATEGORY_LIMITS.items():
        eligible = [
            item for item in source_questions
            if item_grade(item, grade_data) <= grade_limit
        ]
        if not eligible:
            raise ValueError(f"{category}に使える問題がありません")
        questions = [eligible[index % len(eligible)] for index in range(QUESTIONS_PER_CATEGORY)]
        all_data[category] = [
            {
                "kanji": item["kanji"],
                "reading": kanji_reading(item),
                "meaning": f"「{item['kanji']}」の漢字部分の読みは「{kanji_reading(item)}」です。",
                "schoolGrade": item_grade(item, grade_data),
            }
            for item in questions
        ]

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, separators=(",", ":"))

    total_count = sum(len(items) for items in all_data.values())
    print(f"学年別の自然な問題 {total_count} 問を出力しました: {OUTPUT_FILE.name}")

if __name__ == "__main__":
    generate_questions()
