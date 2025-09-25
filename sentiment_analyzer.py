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
        
        # 不要な文字を除去
        text = str(text)
        text = re.sub(r'\s+', ' ', text)  # 複数の空白を1つに
        text = text.strip()
        
        return text
    
    def get_sentiment_score(self, text: str) -> Dict[str, float]:
        """単一テキストの感情スコアを計算"""
        if not text or text.strip() == "":
            return {
                'sentiment_score': 0.0,
                'positive_prob': 0.0,
                'negative_prob': 0.0,
                'neutral_prob': 0.0
            }
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                logits = self.model(**inputs).logits
            prob = torch.softmax(logits, dim=1)[0]
            
            # モデルの出力: [neutral, negative, positive]
            neutral_prob = float(prob[0])
            negative_prob = float(prob[1])
            positive_prob = float(prob[2])
            
            # センチメントスコア: ポジティブ - ネガティブ (-1.0 ～ 1.0)
            sentiment_score = positive_prob - negative_prob
            
            return {
                'sentiment_score': sentiment_score,
                'positive_prob': positive_prob,
                'negative_prob': negative_prob,
                'neutral_prob': neutral_prob
            }
        except Exception as e:
            print(f"感情分析エラー (テキスト: {text[:50]}...): {e}")
            return {
                'sentiment_score': 0.0,
                'positive_prob': 0.0,
                'negative_prob': 0.0,
                'neutral_prob': 0.0
            }
    
    def analyze_news_titles(self, news_titles: str) -> Dict[str, Any]:
        """ニュースタイトル文字列を分析"""
        if pd.isna(news_titles) or news_titles == "":
            return {
                'avg_sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_titles': 0,
                'individual_scores': []
            }
        
        # ニュースタイトルを分割（| で区切られている）
        titles = [self.clean_text(title) for title in news_titles.split('|')]
        titles = [title for title in titles if title]  # 空のタイトルを除去
        
        if not titles:
            return {
                'avg_sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_titles': 0,
                'individual_scores': []
            }
        
        # 各タイトルの感情スコアを計算
        individual_scores = []
        for title in titles:
            score_data = self.get_sentiment_score(title)
            individual_scores.append(score_data['sentiment_score'])
        
        # 統計を計算
        avg_sentiment_score = sum(individual_scores) / len(individual_scores)
        positive_count = sum(1 for score in individual_scores if score > 0.1)
        negative_count = sum(1 for score in individual_scores if score < -0.1)
        neutral_count = len(individual_scores) - positive_count - negative_count
        
        return {
            'avg_sentiment_score': avg_sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_titles': len(titles),
            'individual_scores': individual_scores
        }

def process_csv_with_sentiment(input_csv_path: str, output_csv_path: str):
    """CSVファイルのニュースタイトルにセンチメントスコアを追加"""
    print("=== ニュースタイトルのセンチメント分析を開始 ===")
    
    # CSVファイルを読み込み
    try:
        df = pd.read_csv(input_csv_path)
        print(f"CSVファイルを読み込みました: {len(df)} 行")
        print(f"列名: {list(df.columns)}")
    except Exception as e:
        print(f"CSVファイルの読み込みエラー: {e}")
        return
    
    # センチメントアナライザーを初期化
    analyzer = SentimentAnalyzer()
    
    # 結果を格納するリスト
    sentiment_results = []
    
    # 各行のニュースタイトルを分析
    for i, row in df.iterrows():
        print(f"進捗: {i+1}/{len(df)} - 日付: {row['date']}")
        
        news_titles = row.get('news_titles', '')
        result = analyzer.analyze_news_titles(news_titles)
        
        sentiment_results.append({
            'avg_sentiment_score': result['avg_sentiment_score'],
            'positive_count': result['positive_count'],
            'negative_count': result['negative_count'],
            'neutral_count': result['neutral_count'],
            'total_titles': result['total_titles']
        })
        
        # 進捗表示
        if (i + 1) % 50 == 0:
            print(f"  {i+1}行処理完了")
    
    # 結果をDataFrameに追加
    sentiment_df = pd.DataFrame(sentiment_results)
    
    # 元のDataFrameに結果を結合
    result_df = pd.concat([df, sentiment_df], axis=1)
    
    # 結果をCSVファイルに保存
    result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\n=== 処理完了 ===")
    print(f"処理した行数: {len(result_df)}")
    print(f"結果を保存しました: {output_csv_path}")
    
    # 結果の統計を表示
    print(f"\n=== センチメント分析結果の統計 ===")
    print(f"平均センチメントスコア: {result_df['avg_sentiment_score'].mean():.4f}")
    print(f"ポジティブなニュースの総数: {result_df['positive_count'].sum()}")
    print(f"ネガティブなニュースの総数: {result_df['negative_count'].sum()}")
    print(f"中立的なニュースの総数: {result_df['neutral_count'].sum()}")
    print(f"分析したニュースタイトルの総数: {result_df['total_titles'].sum()}")
    
    # サンプル結果を表示
    print(f"\n=== サンプル結果（先頭5件）===")
    for i, row in result_df.head().iterrows():
        print(f"日付: {row['date']}")
        print(f"  センチメントスコア: {row['avg_sentiment_score']:.4f}")
        print(f"  ポジティブ: {row['positive_count']}, ネガティブ: {row['negative_count']}, 中立: {row['neutral_count']}")
        print(f"  ニュースタイトル: {row['news_titles'][:100]}...")
        print()

def main():
    """メイン関数"""
    input_csv = "data_with_news_titles.csv"
    output_csv = "data_with_sentiment_scores.csv"
    
    print("=== Bloomberg ニュース センチメント分析ツール ===")
    print(f"入力ファイル: {input_csv}")
    print(f"出力ファイル: {output_csv}")
    
    # センチメント分析を実行
    process_csv_with_sentiment(input_csv, output_csv)
    
    print(f"\n=== 全処理完了 ===")
    print(f"センチメントスコア付きデータ: {output_csv}")

if __name__ == '__main__':
    main()




