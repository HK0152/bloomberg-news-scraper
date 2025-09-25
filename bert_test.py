import pandas as pd
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BertJapaneseTokenizer,
)
import sys
import re
from typing import List, Dict, Any

class SentimentAnalyzer:
    def __init__(self):
        """BERTモデルを初期化"""
        print("BERTモデルを読み込み中...")
        try:
            # BERTを用いた日本語の感情分析モデルをロード
            self.tokenizer = BertJapaneseTokenizer.from_pretrained(
                "cl-tohoku/bert-base-japanese-whole-word-masking"
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "koheiduck/bert-japanese-finetuned-sentiment"
            )
            print("BERTモデルの読み込みが完了しました。")
        except Exception as e:
            print(f"BERTモデルの読み込みエラー: {e}")
            sys.exit(1)
    
    def clean_text(self, text: str) -> str:
        """テキストをクリーニング"""
        if pd.isna(text) or text == "":
            return ""
        
        # 基本的なクリーニング
        text = str(text).strip()
        # 特殊文字の除去
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', ' ', text)
        # 複数の空白を単一の空白に
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def analyze_sentiment(self, text: str) -> float:
        """単一テキストの感情分析"""
        if not text or text.strip() == "":
            return 0.0
        
        try:
            # テキストをトークン化
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # モデルで予測
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # 感情スコアの計算（ネガティブ: 0, ポジティブ: 1）
            # ポジティブの確率からネガティブの確率を引いて-1～1の範囲に正規化
            positive_prob = predictions[0][1].item()  # ポジティブの確率
            negative_prob = predictions[0][0].item()  # ネガティブの確率
            
            # スコア計算: ポジティブ確率 - ネガティブ確率
            sentiment_score = positive_prob - negative_prob
            
            return sentiment_score
            
        except Exception as e:
            print(f"感情分析エラー: {e}")
            return 0.0

def test_bert_analysis():
    """BERTの感情分析をテストする"""
    print("=== BERT感情分析テスト ===")
    
    # 感情分析器を初期化
    analyzer = SentimentAnalyzer()
    
    # テスト用の日本語テキスト
    test_texts = [
        "素晴らしい成果を上げました！",  # 明らかにポジティブ
        "最悪の結果になってしまった。",  # 明らかにネガティブ
        "普通の日でした。",  # 中立
        "コロナワクチン接種より感染による免疫力強い、デルタ拡大期－米調査",  # 実際のニュース
        "ソフトバンクＧのクラウレＣＯＯは今後数週間に退社計画－関係者",  # 実際のニュース
        "ウォール街オフィス復帰へ、ＳＥＣやＯＣＣがそれでも在宅続ける理由",  # 実際のニュース
        "英はリセッション入りも、足元のエネルギー価格継続なら－ＮＩＥＳＲ",  # 実際のニュース
        "ロシア、ノルドストリーム１経由の欧州への天然ガス供給遮断も辞さず",  # 実際のニュース
    ]
    
    print("\n=== 感情分析結果 ===")
    for i, text in enumerate(test_texts, 1):
        score = analyzer.analyze_sentiment(text)
        
        # 感情の判定
        if score > 0.1:
            sentiment = "ポジティブ"
        elif score < -0.1:
            sentiment = "ネガティブ"
        else:
            sentiment = "中立"
        
        print(f"{i:2d}. スコア: {score:7.4f} ({sentiment})")
        print(f"    テキスト: {text}")
        print()
    
    # 実際のCSVデータからいくつかのニュースタイトルをテスト
    print("=== 実際のCSVデータのテスト ===")
    try:
        df = pd.read_csv("data_with_sentiment_scores.csv")
        
        # 最初の5行のニュースタイトルをテスト
        for i in range(min(5, len(df))):
            news_titles = df.iloc[i]['news_titles']
            if pd.notna(news_titles) and news_titles.strip():
                # ニュースタイトルを分割（|で区切られている）
                titles = news_titles.split('|')
                
                print(f"\n--- 行 {i+1} ---")
                print(f"元のスコア: {df.iloc[i]['avg_sentiment_score']:.4f}")
                
                for j, title in enumerate(titles[:3]):  # 最初の3つのタイトルのみ
                    title = title.strip()
                    if title:
                        score = analyzer.analyze_sentiment(title)
                        
                        if score > 0.1:
                            sentiment = "ポジティブ"
                        elif score < -0.1:
                            sentiment = "ネガティブ"
                        else:
                            sentiment = "中立"
                        
                        print(f"  タイトル{j+1}: {score:7.4f} ({sentiment})")
                        print(f"    内容: {title}")
                        print()
                        
    except Exception as e:
        print(f"CSVデータの読み込みエラー: {e}")

if __name__ == '__main__':
    test_bert_analysis()

