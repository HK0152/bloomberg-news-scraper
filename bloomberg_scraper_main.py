import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

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

def get_bloomberg_urls_for_date(target_date_str):
    """Bloombergの指定された日付の記事URLを取得する（修正版）"""
    print(f"--- Bloombergの記事（{target_date_str}）を取得します ---")
    urls = []
    
    # 1. ニュースサイトマップインデックスのみを取得（証券サイトマップは除外）
    sitemap_index_urls = [
        "https://www.bloomberg.co.jp/feeds/cojp/sitemap_index.xml"  # ニュースサイトマップのみ
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
                
                # レート制限対策
                time.sleep(0.5)
                
                # 十分な記事が見つかったら終了
                if len(urls) >= 20:
                    break
            
    return urls




def main():
    """メイン関数：日付をターミナルで指定"""
    print("=== Bloomberg ニュース取得ツール ===")
    print("日付を指定してBloombergのニュース記事を取得します。\n")
    
    # 日付入力
    while True:
        date_input = input("取得したい日付を入力してください (例: 2025-09-24): ").strip()
        
        if not date_input:
            print("日付を入力してください。")
            continue
            
        # 日付形式をチェック
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            target_date = date_input
            break
        except ValueError:
            print("正しい日付形式で入力してください (YYYY-MM-DD)")
    
    print(f"\n日付: {target_date}")
    print("処理を開始します...\n")
    
    # Bloomberg
    bloomberg_urls = get_bloomberg_urls_for_date(target_date)
    print(f"取得したBloombergの記事URL数: {len(bloomberg_urls)}")
    if bloomberg_urls:
        print("（先頭5件）:")
        for url in bloomberg_urls[:5]:
            print(url)
    
    # 結果の要約
    print(f"\n=== 取得結果要約 ===")
    print(f"指定日付: {target_date}")
    print(f"Bloomberg: {len(bloomberg_urls)}件")
    print(f"合計: {len(bloomberg_urls)}件")

if __name__ == '__main__':
    main()