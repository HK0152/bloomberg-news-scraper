from transformers import pipeline

# 感情分析パイプラインの作成
# 事前学習モデル: https://huggingface.co/koheiduck/bert-japanese-finetuned-sentiment
sentiment_analyzer = pipeline("sentiment-analysis", model="koheiduck/bert-japanese-finetuned-sentiment")

# 解析したいテキスト（リストで複数指定も可能）
texts = [
    "この映画はとても面白かった。",
    "製品の品質にはがっかりした。",
    "今日は天気が良くて気持ちがいい。"
]

# 感情分析の実行
results = sentiment_analyzer(texts)

# 結果の表示
for text, result in zip(texts, results):
    print(f"テキスト: {text}")
    print(f"  ラベル: {result['label']}, スコア: {result['score']:.4f}")