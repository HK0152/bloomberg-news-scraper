import pandas as pd
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
import sys
import re
from typing import List, Dict, Any

class FixedSentimentAnalyzer:
    def __init__(self):
        """修正されたBERTモデルを初期化"""
        print("修正されたBERTモデルを読み込み中...")
        try:
            # より正確な多言語感情分析モデルを使用
            model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            print(f"モデル '{model_name}' の読み込みが完了しました。")
        except Exception as e:
            print(f"モデルの読み込みエラー: {e}")
            sys.exit(1)
    
    def clean_text(self, text: str) -> str:
        """テキストをクリーニング"""
        if pd.isna(text) or text == "":
            return ""
        
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
    
    def analyze_news_titles(self, news_titles: str) -> Dict[str, Any]:
        """ニュースタイトルの感情分析"""
        if pd.isna(news_titles) or news_titles.strip() == "":
            return {
                'avg_sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_titles': 0
            }
        
        # ニュースタイトルを分割（|で区切られている）
        titles = [title.strip() for title in news_titles.split('|') if title.strip()]
        
        if not titles:
            return {
                'avg_sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_titles': 0
            }
        
        sentiment_scores = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for title in titles:
            score = self.analyze_sentiment(title)
            sentiment_scores.append(score)
            
            # 感情の分類
            if score > 0.1:
                positive_count += 1
            elif score < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        # 平均スコアの計算
        avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        return {
            'avg_sentiment_score': avg_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_titles': len(titles)
        }
    
    def process_csv(self, input_file: str, output_file: str):
        """CSVファイルを処理してセンチメントスコアを追加"""
        print(f"CSVファイルを読み込み中: {input_file}")
        df = pd.read_csv(input_file)
        
        print(f"データ行数: {len(df)}")
        print("センチメント分析を開始...")
        
        # 新しい列を初期化
        df['avg_sentiment_score'] = 0.0
        df['positive_count'] = 0
        df['negative_count'] = 0
        df['neutral_count'] = 0
        df['total_titles'] = 0
        
        # 各行を処理
        for i, row in df.iterrows():
            if i % 50 == 0:
                print(f"処理中: {i+1}/{len(df)} 行")
            
            news_titles = row['news_titles']
            result = self.analyze_news_titles(news_titles)
            
            # 結果をDataFrameに設定
            df.at[i, 'avg_sentiment_score'] = result['avg_sentiment_score']
            df.at[i, 'positive_count'] = result['positive_count']
            df.at[i, 'negative_count'] = result['negative_count']
            df.at[i, 'neutral_count'] = result['neutral_count']
            df.at[i, 'total_titles'] = result['total_titles']
        
        # 結果を保存
        df.to_csv(output_file, index=False)
        print(f"結果を保存しました: {output_file}")
        
        # 統計情報を表示
        self.print_statistics(df)
        
        return df
    
    def print_statistics(self, df: pd.DataFrame):
        """統計情報を表示"""
        print("\n=== センチメント分析結果 ===")
        
        # 基本統計
        total_rows = len(df)
        rows_with_news = len(df[df['total_titles'] > 0])
        
        print(f"総行数: {total_rows}")
        print(f"ニュースがある行数: {rows_with_news}")
        
        if rows_with_news > 0:
            # センチメントスコアの統計
            sentiment_scores = df[df['total_titles'] > 0]['avg_sentiment_score']
            print(f"\nセンチメントスコア統計:")
            print(f"  平均: {sentiment_scores.mean():.4f}")
            print(f"  中央値: {sentiment_scores.median():.4f}")
            print(f"  標準偏差: {sentiment_scores.std():.4f}")
            print(f"  最小値: {sentiment_scores.min():.4f}")
            print(f"  最大値: {sentiment_scores.max():.4f}")
            
            # 感情の分布
            positive_rows = len(df[df['positive_count'] > df['negative_count']])
            negative_rows = len(df[df['negative_count'] > df['positive_count']])
            neutral_rows = len(df[df['positive_count'] == df['negative_count']])
            
            print(f"\n感情分布:")
            print(f"  ポジティブ優勢: {positive_rows} 行 ({positive_rows/rows_with_news*100:.1f}%)")
            print(f"  ネガティブ優勢: {negative_rows} 行 ({negative_rows/rows_with_news*100:.1f}%)")
            print(f"  中立: {neutral_rows} 行 ({neutral_rows/rows_with_news*100:.1f}%)")

def main():
    """メイン関数"""
    input_file = "data_with_news_titles.csv"
    output_file = "data_with_sentiment_scores_fixed.csv"
    
    print("=== 修正されたセンチメント分析ツール ===")
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    
    try:
        # センチメント分析器を初期化
        analyzer = FixedSentimentAnalyzer()
        
        # CSVファイルを処理
        df = analyzer.process_csv(input_file, output_file)
        
        print(f"\n=== 処理完了 ===")
        print(f"結果ファイル: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

