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

class AlternativeSentimentAnalyzer:
    def __init__(self):
        """代替のBERTモデルを初期化"""
        print("代替BERTモデルを読み込み中...")
        try:
            # 別の日本語感情分析モデルを試す
            model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            print(f"モデル '{model_name}' の読み込みが完了しました。")
        except Exception as e:
            print(f"代替モデルの読み込みエラー: {e}")
            # フォールバック: 元のモデル
            try:
                self.tokenizer = BertJapaneseTokenizer.from_pretrained(
                    "cl-tohoku/bert-base-japanese-whole-word-masking"
                )
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    "koheiduck/bert-japanese-finetuned-sentiment"
                )
                print("フォールバック: 元のモデルを使用します。")
            except Exception as e2:
                print(f"フォールバックも失敗: {e2}")
                sys.exit(1)
    
    def clean_text(self, text: str) -> str:
        """テキストをクリーニング"""
        if pd.isna(text) or text == "":
            return ""
        
        text = str(text).strip()
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def analyze_sentiment_multilingual(self, text: str) -> float:
        """多言語BERTモデルでの感情分析"""
        if not text or text.strip() == "":
            return 0.0
        
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # 5段階評価 (1: 非常にネガティブ, 5: 非常にポジティブ)
            # スコアを-1～1の範囲に変換
            scores = predictions[0]
            weighted_score = (
                scores[0] * -1.0 +  # 1星: 非常にネガティブ
                scores[1] * -0.5 +  # 2星: ネガティブ
                scores[2] * 0.0 +   # 3星: 中立
                scores[3] * 0.5 +   # 4星: ポジティブ
                scores[4] * 1.0     # 5星: 非常にポジティブ
            )
            
            return weighted_score.item()
            
        except Exception as e:
            print(f"感情分析エラー: {e}")
            return 0.0
    
    def analyze_sentiment_original(self, text: str) -> float:
        """元のモデルでの感情分析（修正版）"""
        if not text or text.strip() == "":
            return 0.0
        
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # 出力の解釈を修正
            # ラベル0: ネガティブ, ラベル1: ポジティブ
            negative_prob = predictions[0][0].item()
            positive_prob = predictions[0][1].item()
            
            # スコア計算: ポジティブ確率 - ネガティブ確率
            sentiment_score = positive_prob - negative_prob
            
            return sentiment_score
            
        except Exception as e:
            print(f"感情分析エラー: {e}")
            return 0.0

def test_alternative_models():
    """代替モデルをテストする"""
    print("=== 代替BERT感情分析テスト ===")
    
    # テスト用の日本語テキスト
    test_texts = [
        "素晴らしい成果を上げました！",  # 明らかにポジティブ
        "最悪の結果になってしまった。",  # 明らかにネガティブ
        "普通の日でした。",  # 中立
        "今日は良い天気です。",  # ポジティブ
        "雨が降って憂鬱です。",  # ネガティブ
    ]
    
    # 多言語モデルをテスト
    print("\n=== 多言語BERTモデル (nlptown/bert-base-multilingual-uncased-sentiment) ===")
    try:
        analyzer_multi = AlternativeSentimentAnalyzer()
        
        for i, text in enumerate(test_texts, 1):
            score = analyzer_multi.analyze_sentiment_multilingual(text)
            
            if score > 0.1:
                sentiment = "ポジティブ"
            elif score < -0.1:
                sentiment = "ネガティブ"
            else:
                sentiment = "中立"
            
            print(f"{i:2d}. スコア: {score:7.4f} ({sentiment})")
            print(f"    テキスト: {text}")
            print()
    except Exception as e:
        print(f"多言語モデルのテストエラー: {e}")
    
    # シンプルなルールベースの感情分析も試す
    print("\n=== シンプルなルールベース感情分析 ===")
    
    def simple_sentiment_analysis(text):
        """シンプルなルールベースの感情分析"""
        positive_words = [
            "良い", "素晴らしい", "成功", "上昇", "増加", "利益", "成長", "改善",
            "復帰", "堅調", "上回る", "急増", "最高値", "好調", "順調"
        ]
        negative_words = [
            "悪い", "最悪", "失敗", "下落", "減少", "損失", "衰退", "悪化",
            "退社", "リセッション", "遮断", "不安", "警告", "反対", "格下げ"
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 0.5
        elif negative_count > positive_count:
            return -0.5
        else:
            return 0.0
    
    for i, text in enumerate(test_texts, 1):
        score = simple_sentiment_analysis(text)
        
        if score > 0.1:
            sentiment = "ポジティブ"
        elif score < -0.1:
            sentiment = "ネガティブ"
        else:
            sentiment = "中立"
        
        print(f"{i:2d}. スコア: {score:7.4f} ({sentiment})")
        print(f"    テキスト: {text}")
        print()

if __name__ == '__main__':
    test_alternative_models()

