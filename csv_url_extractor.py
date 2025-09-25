import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import csv

# HTTPリクエスト時のヘッダー
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_soup(url):
    """指定されたURLからBeautifulSoupオブジェクトを取得する"""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'xml')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_bloomberg_urls_for_date(target_date_str, max_urls=10):
    """Bloombergの指定された日付の記事URLを取得する"""
    print(f"--- Bloombergの記事（{target_date_str}）を取得します ---")
    urls = []
    
    # 1. ニュースサイトマップインデックスのみを取得
    sitemap_index_urls = [
        "https://www.bloomberg.co.jp/feeds/cojp/sitemap_index.xml"
    ]
    
    for sitemap_index_url in sitemap_index_urls:
        print(f"サイトマップインデックスを取得中: {sitemap_index_url}")
        index_soup = get_soup(sitemap_index_url)
        if not index_soup:
            continue
            
        print(f"サイトマップインデックス取得成功: {len(index_soup.find_all('loc'))} 件のサイトマップを発見")
        
        # 2. 各サイトマップから記事URLを抽出（効率化：指定日付の年・月のサイトマップのみ）
        target_dt = datetime.strptime(target_date_str, '%Y-%m-%d')
        target_year_month = f"sitemap_{target_dt.year}_{target_dt.month}"
        
        for loc in index_soup.find_all('loc'):
            sitemap_url = loc.text
            
            # 効率化：指定日付の年・月のサイトマップまたは最近のサイトマップのみを処理
            if (target_year_month in sitemap_url or 
                'sitemap_recent' in sitemap_url or 
                'sitemap_news' in sitemap_url):
                print(f"サイトマップを処理中: {sitemap_url}")
                
                # 3. サイトマップから記事URLを取得
                article_soup = get_soup(sitemap_url)
                if not article_soup:
                    continue
                    
                # 4. 日付が一致する記事URLを抽出
                for url_tag in article_soup.find_all('url'):
                    lastmod = url_tag.find('lastmod')
                    if lastmod and lastmod.text.startswith(target_date_str):
                        article_url = url_tag.find('loc').text
                        urls.append(article_url)
                        print(f"記事URL発見: {article_url}")
                        
                        # 最大URL数に達したら終了
                        if len(urls) >= max_urls:
                            break
                
                # レート制限対策
                time.sleep(0.5)
                
                # 十分な記事が見つかったら終了
                if len(urls) >= max_urls:
                    break
            
    return urls

def process_csv_with_urls(input_csv_path, output_csv_path, max_urls_per_date=5):
    """
    CSVファイルから日付を読み取り、各日付のBloombergのURLを取得して新しいCSVに保存する
    
    Args:
        input_csv_path (str): 入力CSVファイルのパス
        output_csv_path (str): 出力CSVファイルのパス
        max_urls_per_date (int): 日付あたりの最大URL数
    """
    print("=== CSVファイルから日付を読み取り、BloombergのURLを取得します ===")
    
    # CSVファイルを読み込み
    try:
        df = pd.read_csv(input_csv_path)
        print(f"CSVファイルを読み込みました: {len(df)} 行")
        print(f"列名: {list(df.columns)}")
    except Exception as e:
        print(f"CSVファイルの読み込みエラー: {e}")
        return
    
    # 日付列を確認
    if 'date' not in df.columns:
        print("エラー: 'date'列が見つかりません")
        return
    
    # 重複を除いた日付のリストを取得
    unique_dates = df['date'].dropna().unique()
    print(f"処理対象の日付数: {len(unique_dates)}")
    
    # 結果を格納するリスト
    results = []
    
    # 各日付についてURLを取得
    for i, date_str in enumerate(unique_dates, 1):
        print(f"\n進捗: {i}/{len(unique_dates)} - 日付: {date_str}")
        
        try:
            # 日付形式をチェック
            datetime.strptime(date_str, '%Y-%m-%d')
            
            # BloombergのURLを取得
            urls = get_bloomberg_urls_for_date(date_str, max_urls_per_date)
            
            # 結果をリストに追加
            for url in urls:
                results.append({
                    'date': date_str,
                    'bloomberg_url': url
                })
            
            print(f"日付 {date_str}: {len(urls)} 件のURLを取得")
            
            # レート制限対策
            time.sleep(1)
            
        except ValueError as e:
            print(f"日付形式エラー ({date_str}): {e}")
            continue
        except Exception as e:
            print(f"エラー ({date_str}): {e}")
            continue
    
    # 結果をCSVファイルに保存
    if results:
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"\n=== 処理完了 ===")
        print(f"取得したURL総数: {len(results)}")
        print(f"結果を保存しました: {output_csv_path}")
        
        # 結果のサンプルを表示
        print(f"\n結果のサンプル（先頭5件）:")
        for i, row in result_df.head().iterrows():
            print(f"  {row['date']}: {row['bloomberg_url']}")
    else:
        print("取得したURLがありませんでした。")

def main():
    """メイン関数"""
    input_csv = "data.csv"
    output_csv = "bloomberg_urls.csv"
    max_urls_per_date = 5  # 日付あたりの最大URL数
    
    print("=== Bloomberg URL取得ツール ===")
    print(f"入力ファイル: {input_csv}")
    print(f"出力ファイル: {output_csv}")
    print(f"日付あたりの最大URL数: {max_urls_per_date}")
    
    # 処理実行
    process_csv_with_urls(input_csv, output_csv, max_urls_per_date)

if __name__ == '__main__':
    main()




