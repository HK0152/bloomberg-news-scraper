import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
import time
from datetime import datetime
import sys
import os

# textフォルダのscraper_templateをインポート
sys.path.append('text')
from scraper_template import fetch_bloomberg_article, parse_article

# HTTPリクエスト時のヘッダー
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_article_with_retry(url, max_retries=3):
    """
    リトライ機能付きで記事を取得する
    """
    for attempt in range(max_retries):
        try:
            print(f"  記事取得中 (試行 {attempt + 1}/{max_retries}): {url}")
            html = fetch_bloomberg_article(url)
            return html
        except Exception as e:
            print(f"  エラー (試行 {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # 2秒待機してリトライ
            else:
                print(f"  最大リトライ回数に達しました: {url}")
                return None

def parse_article_enhanced(html, url):
    """
    記事のHTMLを解析して情報を抽出（改良版）
    """
    if not html:
        return {
            "title": "取得失敗",
            "date": "取得失敗", 
            "author": "取得失敗",
            "content": "取得失敗",
            "url": url
        }
    
    try:
        soup = BeautifulSoup(html, "html.parser")

        # タイトルを取得（複数のセレクタを試行）
        title_selectors = [
            "h1",
            ".headline",
            ".story-headline", 
            "title",
            "[data-testid='headline']"
        ]
        
        title = "タイトルなし"
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                title = title_tag.get_text(strip=True)
                if title and len(title) > 5:  # 有効なタイトルかチェック
                    break

        # 日付を取得（複数のセレクタを試行）
        date_selectors = [
            "time",
            ".timestamp",
            ".story-timestamp",
            ".date",
            "[data-testid='timestamp']"
        ]
        
        date = "日付なし"
        for selector in date_selectors:
            date_tag = soup.select_one(selector)
            if date_tag:
                date = date_tag.get_text(strip=True)
                if date and len(date) > 5:  # 有効な日付かチェック
                    break

        # 本文を取得（複数のセレクタを試行）
        content_selectors = [
            ".body-copy",
            ".story-body",
            "article",
            ".content",
            "[data-module='ArticleBody']",
            ".article-body"
        ]
        
        content = ""
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div and isinstance(content_div, Tag):
                paragraphs = content_div.find_all("p")
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:  # 短すぎるテキストは除外
                        content_parts.append(text)
                if content_parts:
                    content = "\n".join(content_parts)
                    break

        # 著者情報を取得（複数のセレクタを試行）
        author_selectors = [
            ".byline__name",
            ".author-link",
            ".story-byline",
            ".byline",
            "[data-testid='byline']"
        ]
        
        author = "著者情報なし"
        for selector in author_selectors:
            author_tag = soup.select_one(selector)
            if author_tag:
                author = author_tag.get_text(strip=True)
                if author and len(author) > 2:  # 有効な著者名かチェック
                    break

        return {
            "title": title,
            "date": date,
            "author": author,
            "content": content,
            "url": url
        }
        
    except Exception as e:
        print(f"  記事解析エラー: {e}")
        return {
            "title": "解析失敗",
            "date": "解析失敗",
            "author": "解析失敗", 
            "content": "解析失敗",
            "url": url
        }

def process_urls_to_articles(input_csv_path, output_csv_path, max_articles_per_date=3):
    """
    URLのCSVファイルから記事を取得してテキスト化し、新しいCSVに保存する
    
    Args:
        input_csv_path (str): 入力CSVファイルのパス（URLが含まれる）
        output_csv_path (str): 出力CSVファイルのパス
        max_articles_per_date (int): 日付あたりの最大記事数
    """
    print("=== URLから記事を取得してテキスト化します ===")
    
    # CSVファイルを読み込み
    try:
        df = pd.read_csv(input_csv_path)
        print(f"CSVファイルを読み込みました: {len(df)} 行")
        print(f"列名: {list(df.columns)}")
    except Exception as e:
        print(f"CSVファイルの読み込みエラー: {e}")
        return
    
    # 日付ごとに記事をグループ化
    date_groups = df.groupby('date')
    print(f"処理対象の日付数: {len(date_groups)}")
    
    # 結果を格納するリスト
    results = []
    
    # 各日付について記事を取得
    for date_str, group in date_groups:
        print(f"\n--- 日付: {date_str} ---")
        urls = group['bloomberg_url'].tolist()
        
        # 最大記事数に制限
        urls_to_process = urls[:max_articles_per_date]
        print(f"処理するURL数: {len(urls_to_process)}")
        
        for i, url in enumerate(urls_to_process, 1):
            print(f"  記事 {i}/{len(urls_to_process)}: {url}")
            
            try:
                # 記事を取得
                html = fetch_article_with_retry(url)
                
                # 記事を解析
                article_data = parse_article_enhanced(html, url)
                
                # 結果をリストに追加
                results.append({
                    'date': date_str,
                    'bloomberg_url': url,
                    'title': article_data['title'],
                    'author': article_data['author'],
                    'content': article_data['content'],
                    'article_date': article_data['date']
                })
                
                print(f"    ✓ タイトル: {article_data['title'][:50]}...")
                
                # レート制限対策
                time.sleep(1)
                
            except Exception as e:
                print(f"    ✗ エラー: {e}")
                # エラーでも空のデータを追加
                results.append({
                    'date': date_str,
                    'bloomberg_url': url,
                    'title': "取得失敗",
                    'author': "取得失敗",
                    'content': "取得失敗",
                    'article_date': "取得失敗"
                })
                continue
    
    # 結果をCSVファイルに保存
    if results:
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"\n=== 処理完了 ===")
        print(f"取得した記事総数: {len(results)}")
        print(f"結果を保存しました: {output_csv_path}")
        
        # 結果のサンプルを表示
        print(f"\n結果のサンプル（先頭5件）:")
        for i, row in result_df.head().iterrows():
            print(f"  {row['date']}: {row['title'][:50]}...")
    else:
        print("取得した記事がありませんでした。")

def add_titles_to_original_csv(original_csv_path, articles_csv_path, output_csv_path):
    """
    元のdata.csvにニュースタイトルを補完する
    
    Args:
        original_csv_path (str): 元のdata.csvのパス
        articles_csv_path (str): 記事データのCSVのパス
        output_csv_path (str): 出力CSVファイルのパス
    """
    print("=== 元のCSVにニュースタイトルを補完します ===")
    
    try:
        # 元のCSVを読み込み
        original_df = pd.read_csv(original_csv_path)
        print(f"元のCSVを読み込みました: {len(original_df)} 行")
        
        # 記事データのCSVを読み込み
        articles_df = pd.read_csv(articles_csv_path)
        print(f"記事データを読み込みました: {len(articles_df)} 行")
        
        # 日付ごとに記事タイトルを結合
        date_titles = {}
        for _, row in articles_df.iterrows():
            date = row['date']
            title = row['title']
            
            if date not in date_titles:
                date_titles[date] = []
            date_titles[date].append(title)
        
        # 元のCSVにニュースタイトル列を追加
        original_df['news_titles'] = original_df['date'].map(
            lambda x: ' | '.join(date_titles.get(x, ['記事なし']))
        )
        
        # 結果を保存
        original_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"補完完了: {output_csv_path}")
        
        # サンプルを表示
        print(f"\n補完結果のサンプル（先頭3件）:")
        for i, row in original_df.head(3).iterrows():
            print(f"  {row['date']}: {row['news_titles'][:100]}...")
            
    except Exception as e:
        print(f"CSV補完エラー: {e}")

def main():
    """メイン関数"""
    input_csv = "bloomberg_urls.csv"
    articles_csv = "bloomberg_articles.csv"
    original_csv = "data.csv"
    enhanced_csv = "data_with_news_titles.csv"
    max_articles_per_date = 3  # 日付あたりの最大記事数
    
    print("=== Bloomberg URL → 記事テキスト化ツール ===")
    print(f"入力ファイル: {input_csv}")
    print(f"記事データ出力: {articles_csv}")
    print(f"元のCSV: {original_csv}")
    print(f"補完済みCSV: {enhanced_csv}")
    print(f"日付あたりの最大記事数: {max_articles_per_date}")
    
    # ステップ1: URLから記事を取得してテキスト化
    print(f"\n【ステップ1】URLから記事を取得してテキスト化")
    process_urls_to_articles(input_csv, articles_csv, max_articles_per_date)
    
    # ステップ2: 元のCSVにニュースタイトルを補完
    print(f"\n【ステップ2】元のCSVにニュースタイトルを補完")
    add_titles_to_original_csv(original_csv, articles_csv, enhanced_csv)
    
    print(f"\n=== 全処理完了 ===")
    print(f"1. 記事データ: {articles_csv}")
    print(f"2. 補完済みデータ: {enhanced_csv}")

if __name__ == '__main__':
    main()




