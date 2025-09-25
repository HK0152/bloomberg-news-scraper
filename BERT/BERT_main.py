import fitz
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BertJapaneseTokenizer,
)
import torch, pandas as pd
import sys
from bs4 import BeautifulSoup
import re

# BERTを用いた日本語の感情分析モデルをロード
tokenizer = BertJapaneseTokenizer.from_pretrained(
    "cl-tohoku/bert-base-japanese-whole-word-masking"
)
model = AutoModelForSequenceClassification.from_pretrained(
    "koheiduck/bert-japanese-finetuned-sentiment"
)


# HTMLからテキストを抽出する関数
def extract_text_from_html(html_content):
    """
    HTMLコンテンツからテキストを抽出し、不要な要素を除去する
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # スクリプトやスタイルタグを除去
    for script in soup(["script", "style"]):
        script.decompose()
    
    # テキストを取得
    text = soup.get_text()
    
    # 改行や空白を整理
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # 不要な文字を除去
    text = re.sub(r'\s+', ' ', text)  # 複数の空白を1つに
    text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]', '', text)  # 日本語文字以外の記号を除去
    
    return text

# 感情スコアを計算する関数
def get_sentiment_score(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    prob = torch.softmax(logits, dim=1)[0]
    print(f"テキスト: {text}")
    print(
        f"  ポジティブ: {prob[2]:.4f}, ネガティブ: {prob[1]:.4f}, 中立： {prob[0]:.4f}"
    )
    return prob[2] - prob[1]  # Pos - Neg

# HTMLコンテンツから感情分析を行う関数
def analyze_html_sentiment(html_content):
    """
    HTMLコンテンツからテキストを抽出し、感情分析を実行する
    """
    print("HTMLからテキストを抽出中...")
    text_data = extract_text_from_html(html_content)
    
    if not text_data.strip():
        print("HTMLから有効なテキストを抽出できませんでした。")
        return None
    
    print(f"抽出されたテキスト: {text_data[:200]}...")  # 最初の200文字を表示
    
    # テキストを文（句点「。」）で分割
    sentences = text_data.split('。')
    sentences = [s.strip() for s in sentences if s.strip()]  # 空の文を除去
    
    print(f"{len(sentences)}個の文に分割して分析を開始します...")
    
    # 各文のスコアをリストに格納
    scores = [get_sentiment_score(s) for s in sentences]
    
    # 全文の平均スコアを計算
    if scores:
        average_score = sum(scores) / len(scores)
        positive_count = sum(1 for s in scores if s > 0.1)
        negative_count = sum(1 for s in scores if s < -0.1)
        neutral_count = len(scores) - positive_count - negative_count
        
        result = {
            'average_score': average_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_sentences': len(sentences)
        }
        
        print("\n--- HTML分析結果 ---")
        print(f"全体の平均感情スコア: {average_score:.4f}")
        print(f"ポジティブな文の数: {positive_count}")
        print(f"ネガティブな文の数: {negative_count}")
        print(f"中立的な文の数: {neutral_count}")
        print(f"総文数: {len(sentences)}")
        
        return result
    else:
        print("分析できるテキストが見つかりませんでした。")
        return None


# テスト用のサンプルテキスト
texts = [
    "テストの結果が悪くて悲しい。",
    "製品の品質にはがっかりした。",
    "テストの結果が良くてうれしい。",
    "テストの結果が普通で特に感情はない。",
    "今日は天気が良くて気持ちがいい。",
]

# 各文のスコアをリストに格納
scores = [get_sentiment_score(s.strip()) for s in texts if s.strip()]

# 全文の平均スコアを計算
if scores:
    average_score = sum(scores) / len(scores)
    positive_count = sum(1 for s in scores if s > 0.1)
    negative_count = sum(1 for s in scores if s < -0.1)
    neutral_count = len(scores) - positive_count - negative_count

    print("\n--- 分析結果 ---")
    print(f"全体の平均感情スコア: {average_score:.4f}")
    print(f"ポジティブな文の数: {positive_count}")
    print(f"ネガティブな文の数: {negative_count}")
    print(f"中立的な文の数: {neutral_count}")
else:
    print("分析できるテキストが見つかりませんでした。")

# HTML処理の使用例
print("\n" + "="*50)
print("HTML処理機能の使用例")
print("="*50)

# サンプルHTMLコンテンツ
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>商品レビュー</title>
</head>
<body>
    <h1>商品レビュー</h1>
    <div class="review">
        <p>この商品はとても良い品質で満足しています。価格も手頃でおすすめです。</p>
        <p>配送も早くて助かりました。また購入したいと思います。</p>
    </div>
    <div class="review">
        <p>残念ながら期待していたほどではありませんでした。品質に問題があります。</p>
        <p>返品を検討しています。</p>
    </div>
    <div class="review">
        <p>普通の商品です。特に良い点も悪い点もありません。</p>
    </div>
</body>
</html>
"""

# HTMLから感情分析を実行
result = analyze_html_sentiment(sample_html)

"""
# PDFファイルからテキストを抽出して感情分析を行う
pdf_file_name = "Mitsubishi.pdf" 
print(f"PDFファイルからテキストを抽出中: {pdf_file_name}")

# PDFファイルを開いてテキストを抽出
try:
    doc = fitz.open(pdf_file_name)
    # 全ページのテキストを結合して一つの文字列にする
    text_data = ""
    for page in doc:
        text_data += page.get_text()
    doc.close()
except FileNotFoundError:
    print(f"エラー: ファイル '{pdf_file_name}' が見つかりません。", file=sys.stderr)
    print("ファイル名やパスが正しいか確認してください。", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"エラー: PDFファイルの処理中に問題が発生しました。 {e}", file=sys.stderr)
    sys.exit(1)


# テキストを文（句点「。」）で分割
sentences = text_data.split('。')
print(f"{len(sentences)}個の文に分割して分析を開始します...")

# 各文のスコアをリストに格納
scores = [get_sentiment_score(s.strip()) for s in sentences if s.strip()]

# 全文の平均スコアを計算
if scores:
    average_score = sum(scores) / len(scores)
    positive_count = sum(1 for s in scores if s > 0.1)
    negative_count = sum(1 for s in scores if s < -0.1)
    neutral_count = len(scores) - positive_count - negative_count

    print("\n--- 分析結果 ---")
    print(f"全体の平均感情スコア: {average_score:.4f}")
    print(f"ポジティブな文の数: {positive_count}")
    print(f"ネガティブな文の数: {negative_count}")
    print(f"中立的な文の数: {neutral_count}")
else:
    print("分析できるテキストが見つかりませんでした。")
"""
