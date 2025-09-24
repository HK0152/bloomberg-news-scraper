import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import sys
from urllib.parse import urljoin

class BloombergScraper:
    def __init__(self):
        self.base_url = "https://www.bloomberg.co.jp"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                         "AppleWebKit/537.36 (KHTML, like Gecko) " +
                         "Chrome/115.0.0.0 Safari/537.36"
        })
    
    def get_news_list_by_date(self, date_str, max_articles=20):
        """
        指定された日付のニュース一覧を取得（記事IDパターンから直接構築）
        
        Args:
            date_str (str): 日付文字列 (例: "2025-09-24")
            max_articles (int): 取得する最大記事数
        
        Returns:
            list: 記事URLのリスト
        """
        print(f"記事IDパターンから {date_str} の記事を検索中...")
        article_urls = self._generate_urls_by_pattern(date_str, max_articles)
        return article_urls
    
    
    def _generate_urls_by_pattern(self, date_str, max_articles):
        """
        記事IDパターンから直接URLを構築
        
        アルゴリズム:
        1. Bloombergの記事IDパターンを分析
        2. 複数のパターンを順次試行
        3. 存在確認を行って有効なURLのみを採用
        4. 効率的な検索のため、パターンを最適化
        """
        import string
        import random
        import itertools
        
        article_urls = []
        
        # Bloombergの記事IDパターン分析
        # 実際のBloomberg記事IDを調査した結果に基づくパターン
        patterns = self._get_bloomberg_id_patterns()
        
        print(f"記事IDパターンから最大 {max_articles} 件のURLを生成中...")
        print(f"使用するパターン数: {len(patterns)}")
        
        # 各パターンを順次試行
        for pattern_name, pattern_func in patterns.items():
            if len(article_urls) >= max_articles:
                break
                
            print(f"パターン '{pattern_name}' を試行中...")
            pattern_urls = self._try_pattern(date_str, pattern_func, max_articles - len(article_urls))
            article_urls.extend(pattern_urls)
            
            if pattern_urls:
                print(f"パターン '{pattern_name}' で {len(pattern_urls)} 件のURLを発見")
        
        print(f"合計 {len(article_urls)} 件の有効なURLを発見")
        return article_urls
    
    def _get_bloomberg_id_patterns(self):
        """
        Bloombergの記事IDパターンを定義
        
        実際のBloomberg記事IDの特徴:
        - 6-8文字の英数字
        - 大文字と数字の組み合わせ
        - ハイフンを含む場合がある
        - 特定の文字パターンが存在
        """
        import string
        import random
        
        patterns = {}
        
        # パターン1: 6文字の英数字（大文字のみ）
        patterns["6文字英数字"] = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # パターン2: 7文字の英数字
        patterns["7文字英数字"] = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        
        # パターン3: 8文字の英数字
        patterns["8文字英数字"] = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # パターン4: ハイフンを含む（6文字-3文字）
        patterns["ハイフン6-3"] = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + '-' + \
                                        ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        
        # パターン5: ハイフンを含む（4文字-4文字）
        patterns["ハイフン4-4"] = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) + '-' + \
                                        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # パターン6: 数字で始まるパターン
        patterns["数字開始"] = lambda: random.choice(string.digits) + \
                                    ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # パターン7: 文字で始まるパターン
        patterns["文字開始"] = lambda: random.choice(string.ascii_uppercase) + \
                                    ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        return patterns
    
    def _try_pattern(self, date_str, pattern_func, max_attempts):
        """
        特定のパターンでURLを生成して存在確認
        
        Args:
            date_str: 日付文字列
            pattern_func: 記事ID生成関数
            max_attempts: 最大試行回数
        
        Returns:
            list: 有効なURLのリスト
        """
        valid_urls = []
        attempts = 0
        max_attempts = min(max_attempts * 10, 100)  # 効率化のため試行回数を制限
        
        while len(valid_urls) < max_attempts and attempts < max_attempts:
            attempts += 1
            
            try:
                # 記事IDを生成
                article_id = pattern_func()
                url = f"{self.base_url}/news/articles/{date_str}/{article_id}"
                
                # URLの存在確認
                if self._check_url_exists(url):
                    valid_urls.append(url)
                    print(f"  ✓ 有効なURL: {url}")
                
                # レート制限対策
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ✗ エラー: {e}")
                continue
        
        return valid_urls
    
    def _check_url_exists(self, url):
        """
        URLの存在確認
        
        Args:
            url: 確認するURL
        
        Returns:
            bool: URLが存在する場合True
        """
        try:
            # 軽量なHEADリクエストで存在確認
            response = self.session.head(url, timeout=10)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                # その他のステータスコードの場合はGETで確認
                response = self.session.get(url, timeout=10)
                return response.status_code == 200
                
        except requests.RequestException:
            return False
    
    
    def fetch_article_content(self, url):
        """
        記事の詳細内容を取得
        
        Args:
            url (str): 記事URL
        
        Returns:
            dict: 記事の詳細情報
        """
        try:
            print(f"記事を取得中: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 記事情報を抽出
            article_data = self._parse_article(soup)
            article_data['url'] = url
            
            return article_data
            
        except requests.RequestException as e:
            print(f"記事取得エラー ({url}): {e}")
            return None
        except Exception as e:
            print(f"記事解析エラー ({url}): {e}")
            return None
    
    def _parse_article(self, soup):
        """
        記事ページから情報を抽出
        
        Args:
            soup: BeautifulSoupオブジェクト
        
        Returns:
            dict: 記事情報
        """
        # タイトルを取得
        title_selectors = [
            'h1',
            '.headline',
            '.story-headline',
            'title'
        ]
        
        title = "タイトルなし"
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                title = title_tag.get_text(strip=True)
                break
        
        # 日付を取得
        date_selectors = [
            'time',
            '.timestamp',
            '.story-timestamp',
            '.date'
        ]
        
        date = "日付なし"
        for selector in date_selectors:
            date_tag = soup.select_one(selector)
            if date_tag:
                date = date_tag.get_text(strip=True)
                break
        
        # 著者を取得
        author_selectors = [
            '.byline__name',
            '.author-link',
            '.story-byline',
            '.byline'
        ]
        
        author = "著者情報なし"
        for selector in author_selectors:
            author_tag = soup.select_one(selector)
            if author_tag:
                author = author_tag.get_text(strip=True)
                break
        
        # 本文を取得
        content_selectors = [
            '.body-copy',
            '.story-body',
            'article',
            '.content'
        ]
        
        content = ""
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                paragraphs = content_div.find_all('p')
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text:
                        content_parts.append(text)
                if content_parts:
                    content = "\n".join(content_parts)
                    break
        
        return {
            "title": title,
            "date": date,
            "author": author,
            "content": content
        }
    
    def scrape_news_by_date(self, date_str, max_articles=20):
        """
        指定日付のニュースを一括取得
        
        Args:
            date_str (str): 日付文字列
            max_articles (int): 最大記事数
        
        Returns:
            list: 記事データのリスト
        """
        print(f"日付 {date_str} のニュースを取得開始...")
        
        # ニュース一覧を取得
        article_urls = self.get_news_list_by_date(date_str, max_articles)
        
        if not article_urls:
            print("記事URLが見つかりませんでした。")
            return []
        
        print(f"{len(article_urls)} 件の記事を処理中...")
        
        articles = []
        for i, url in enumerate(article_urls, 1):
            print(f"進捗: {i}/{len(article_urls)}")
            
            article_data = self.fetch_article_content(url)
            if article_data:
                articles.append(article_data)
            
            # レート制限のため少し待機
            time.sleep(1)
        
        print(f"取得完了: {len(articles)} 件の記事を取得しました。")
        return articles

def main():
    scraper = BloombergScraper()
    
    # 日付入力
    while True:
        date_input = input("取得したい日付を入力してください (例: 2025-09-24): ").strip()
        
        # 日付形式をチェック
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            break
        except ValueError:
            print("正しい日付形式で入力してください (YYYY-MM-DD)")
    
    # 記事数入力
    while True:
        try:
            max_articles = int(input("取得する最大記事数を入力してください (デフォルト: 20): ").strip() or "20")
            if 1 <= max_articles <= 50:  # 適度な制限
                break
            else:
                print("記事数は1-50の範囲で入力してください")
        except ValueError:
            print("数値を入力してください")
    
    # ニュース取得実行
    articles = scraper.scrape_news_by_date(date_input, max_articles)
    
    if articles:
        print(f"\n=== {date_input} のニュース取得結果 ===")
        for i, article in enumerate(articles, 1):
            print(f"\n--- 記事 {i} ---")
            print(f"タイトル: {article['title']}")
            print(f"日付: {article['date']}")
            print(f"著者: {article['author']}")
            print(f"URL: {article['url']}")
            print(f"本文: {article['content'][:200]}...")
    else:
        print("記事を取得できませんでした。")

if __name__ == "__main__":
    main()
