import json
import random

# カテゴリ設定と1カテゴリあたりの問題数
CATEGORIES = ["math", "general_knowledge", "logic"]
COUNT_PER_CATEGORY = 10000

def generate_questions():
    all_data = {}

    for category in CATEGORIES:
        category_questions = []
        for i in range(1, COUNT_PER_CATEGORY + 1):
            # カテゴリごとのデータ生成ロジック
            if category == "math":
                a = random.randint(1, 1000)
                b = random.randint(1, 1000)
                item = {
                    "id": f"{category}_{i:05d}",
                    "category": category,
                    "question": f"{a} + {b} の計算結果は？",
                    "options": [str(a + b), str(a + b + 1), str(a + b - 1), str(a + b + 5)],
                    "answer": str(a + b)
                }
            else:
                item = {
                    "id": f"{category}_{i:05d}",
                    "category": category,
                    "question": f"{category}に関する問題 第{i}問",
                    "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
                    "answer": "選択肢A"
                }
            category_questions.append(item)

        all_data[category] = category_questions

    # JSONファイルへの書き出し
    output_filename = "questions_10000.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"各カテゴリ {COUNT_PER_CATEGORY} 問（合計 {len(CATEGORIES) * COUNT_PER_CATEGORY} 問）を出力しました: {output_filename}")

if __name__ == "__main__":
    generate_questions()
