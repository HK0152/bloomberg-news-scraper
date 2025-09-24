import requests
from bs4 import BeautifulSoup, Tag

def fetch_bloomberg_article(url):
    headers = {
        # User-Agent を設定しないとブロックされることがあるので一応入れておく
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                    "AppleWebKit/537.36 (KHTML, like Gecko) " +
                    "Chrome/115.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parse_bloomberg_article(html):
    """
    Bloomberg記事のHTMLを解析して情報を抽出
    """
    soup = BeautifulSoup(html, "html.parser")

    # タイトルを取得（複数のセレクタを試行）
    title_selectors = [
        "h1",
        ".headline",
        ".story-headline", 
        "title"
    ]
    
    title = "タイトルなし"
    for selector in title_selectors:
        title_tag = soup.select_one(selector)
        if title_tag:
            title = title_tag.get_text(strip=True)
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
            break

    return {
        "title": title,
        "date": date,
        "author": author,
        "content": content
    }

def parse_article(html):
    """
    後方互換性のためのラッパー関数
    """
    return parse_bloomberg_article(html)
