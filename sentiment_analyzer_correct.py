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

class CorrectSentimentAnalyzer:
    def __init__(self):
        """BERTフォルダのコードを参考にした正確な感情分析器を初期化"""
        print("BERTフォルダのコードを参考にした感情分析器を初期化中...")
        try:
            # BERTフォルダのコードと同じモデルを使用
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
        
        text = str(text).strip()
        # 不要な文字を除去（BERTフォルダのコードを参考）
        text = re.sub(r'\s+', ' ', text)  # 複数の空白を1つに
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]', '', text)  # 日本語文字以外の記号を除去
        return text.strip()
    
    def get_sentiment_score(self, text: str, verbose: bool = False) -> float:
        """BERTフォルダのコードと同じ方法で感情スコアを計算"""
        if not text or text.strip() == "":
            return 0.0
        
        try:
            # BERTフォルダのコードと同じ実装
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            with torch.no_grad():
                logits = self.model(**inputs).logits
            prob = torch.softmax(logits, dim=1)[0]
            
            if verbose:
                print(f"テキスト: {text}")
                print(f"  ポジティブ: {prob[2]:.4f}, ネガティブ: {prob[1]:.4f}, 中立: {prob[0]:.4f}")
            
            # BERTフォルダのコードと同じ計算方法: Pos - Neg
            return prob[2] - prob[1]
            
        except Exception as e:
            if verbose:
                print(f"感情分析エラー: {e}")
            return 0.0
    
    def analyze_news_titles(self, news_titles: str, verbose: bool = False) -> Dict[str, Any]:
        """ニュースタイトルの感情分析（BERTフォルダのコードを参考）"""
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
        
        if verbose:
            print(f"\n--- ニュースタイトル分析開始 ---")
            print(f"分析対象タイトル数: {len(titles)}")
        
        # 各タイトルのスコアを計算
        scores = []
        for i, title in enumerate(titles):
            score = self.get_sentiment_score(title, verbose=verbose)
            scores.append(score)
            
            if verbose:
                print(f"タイトル {i+1}: {score:.4f}")
        
        # BERTフォルダのコードと同じ方法で統計を計算
        if scores:
            average_score = sum(scores) / len(scores)
            positive_count = sum(1 for s in scores if s > 0.1)
            negative_count = sum(1 for s in scores if s < -0.1)
            neutral_count = len(scores) - positive_count - negative_count
            
            if verbose:
                print(f"\n--- 分析結果 ---")
                print(f"全体の平均感情スコア: {average_score:.4f}")
                print(f"ポジティブなタイトル数: {positive_count}")
                print(f"ネガティブなタイトル数: {negative_count}")
                print(f"中立的なタイトル数: {neutral_count}")
                print(f"総タイトル数: {len(titles)}")
            
            return {
                'avg_sentiment_score': average_score,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_titles': len(titles)
            }
        else:
            return {
                'avg_sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_titles': 0
            }
    
    def test_with_sample_texts(self):
        """BERTフォルダのコードと同じテストテキストで動作確認"""
        print("\n=== BERTフォルダのコードと同じテストテキストで動作確認 ===")
        
        # BERTフォルダのコードと同じテストテキスト
        texts = [
            "テストの結果が悪くて悲しい。",
            "製品の品質にはがっかりした。",
            "テストの結果が良くてうれしい。",
            "テストの結果が普通で特に感情はない。",
            "今日は天気が良くて気持ちがいい。",
        ]
        
        print("各テキストの感情分析結果:")
        scores = []
        for i, text in enumerate(texts, 1):
            score = self.get_sentiment_score(text, verbose=True)
            scores.append(score)
            print()
        
        # 全文の平均スコアを計算（BERTフォルダのコードと同じ）
        if scores:
            average_score = sum(scores) / len(scores)
            positive_count = sum(1 for s in scores if s > 0.1)
            negative_count = sum(1 for s in scores if s < -0.1)
            neutral_count = len(scores) - positive_count - negative_count
            
            print("--- 分析結果 ---")
            print(f"全体の平均感情スコア: {average_score:.4f}")
            print(f"ポジティブな文の数: {positive_count}")
            print(f"ネガティブな文の数: {negative_count}")
            print(f"中立的な文の数: {neutral_count}")
    
    def process_csv(self, input_file: str, output_file: str, test_mode: bool = False):
        """CSVファイルを処理してセンチメントスコアを追加"""
        print(f"CSVファイルを読み込み中: {input_file}")
        df = pd.read_csv(input_file)
        
        print(f"データ行数: {len(df)}")
        
        # テストモードの場合は最初の5行のみ処理
        if test_mode:
            df = df.head(5)
            print(f"テストモード: 最初の5行のみ処理します")
        
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
            verbose = test_mode and i < 2  # テストモードでは最初の2行を詳細表示
            result = self.analyze_news_titles(news_titles, verbose=verbose)
            
            # 結果をDataFrameに設定（float型に変換）
            df.at[i, 'avg_sentiment_score'] = float(result['avg_sentiment_score'])
            df.at[i, 'positive_count'] = int(result['positive_count'])
            df.at[i, 'negative_count'] = int(result['negative_count'])
            df.at[i, 'neutral_count'] = int(result['neutral_count'])
            df.at[i, 'total_titles'] = int(result['total_titles'])
        
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
    output_file = "data_with_sentiment_scores_correct.csv"
    
    print("=== BERTフォルダのコードを参考にした正確なセンチメント分析ツール ===")
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    
    try:
        # センチメント分析器を初期化
        analyzer = CorrectSentimentAnalyzer()
        
        # まずテストテキストで動作確認
        analyzer.test_with_sample_texts()
        
        # CSVファイルを処理（全データ）
        print(f"\n{'='*60}")
        print("CSVファイルの処理を開始します（全データ）")
        print(f"{'='*60}")
        
        df = analyzer.process_csv(input_file, output_file, test_mode=False)
        
        print(f"\n=== 処理完了 ===")
        print(f"結果ファイル: {output_file}")
        print("全データの処理が完了しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
