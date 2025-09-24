# Bloomberg ニューススクレイパー

Bloombergのニュース記事を日付指定で取得するPythonスクレイパーです。

## 機能

- 指定した日付のBloombergニュース記事を取得
- ターミナルから日付を指定可能
- 記事のタイトル、日付、著者、本文を抽出
- サイトマップベースの効率的な記事検索
- 2000年〜2025年の全期間の記事に対応

## システムの流れ

### 全体の処理フロー

```
ユーザー入力 → 日付検証 → サイトマップ取得 → 記事URL抽出 → 結果表示
     ↓              ↓              ↓              ↓
  日付指定      形式チェック    効率的フィルタ   重複除去
```

### 詳細な処理ステップ

#### 1. **初期化フェーズ**
```
main.py 起動
    ↓
Bloomberg ニュース取得ツール表示
    ↓
ユーザーに日付入力を要求
```

#### 2. **入力検証フェーズ**
```
日付入力受信
    ↓
日付形式チェック (YYYY-MM-DD)
    ↓
有効な日付 → 処理開始
無効な日付 → エラーメッセージ表示 → 再入力要求
```

#### 3. **サイトマップ取得フェーズ**
```
Bloombergサイトマップインデックス取得
https://www.bloomberg.co.jp/feeds/cojp/sitemap_index.xml
    ↓
432件のサイトマップ一覧を取得
    ↓
効率的なフィルタリング実行
```

#### 4. **効率的フィルタリング**
```
指定日付の年・月を解析 (例: 2020-09-22 → 2020年9月)
    ↓
対象サイトマップを特定:
- sitemap_recent.xml (最近の記事)
- sitemap_news.xml (ニュース記事)  
- sitemap_2020_9.xml (2020年9月の記事)
    ↓
不要なサイトマップを除外 (429件をスキップ)
```

#### 5. **記事URL抽出フェーズ**
```
各対象サイトマップを順次処理
    ↓
XMLパースで記事URLを抽出
    ↓
lastmod日付で指定日付と照合
    ↓
一致する記事URLをリストに追加
    ↓
レート制限対策 (0.5秒待機)
```

#### 6. **結果処理フェーズ**
```
重複URLの除去
    ↓
記事数の集計
    ↓
結果の表示:
- 取得記事数
- 先頭5件のURL表示
- 処理時間の表示
```

### 処理対象サイトマップ

- `sitemap_recent.xml` - 最近の記事
- `sitemap_news.xml` - ニュース記事
- `sitemap_YYYY_M.xml` - 指定年・月の記事（例: `sitemap_2020_1.xml`）

### 効率化のポイント

#### **サイトマップフィルタリング**
- 全432件のサイトマップから、該当する3-4件のみを処理
- 処理時間を大幅短縮（約99%のサイトマップをスキップ）

#### **レート制限対策**
- 各サイトマップ処理後に0.5秒の待機
- Bloombergサーバーへの負荷を軽減

#### **エラーハンドリング**
- ネットワークエラーの自動リトライ
- 無効なサイトマップのスキップ
- 適切なUser-Agentの設定

### コードの流れ

#### **メインファイル構成**
```
main.py (エントリーポイント)
    ↓
get_bloomberg_urls_for_date() 関数呼び出し
    ↓
get_soup() 関数でHTTPリクエスト
    ↓
BeautifulSoupでXMLパース
    ↓
記事URL抽出とフィルタリング
```

#### **主要関数の役割**

| 関数名 | ファイル | 役割 |
|--------|----------|------|
| `main()` | main.py | ユーザー入力処理、メイン制御 |
| `get_bloomberg_urls_for_date()` | main.py | Bloomberg記事URL取得の核となる関数 |
| `get_soup()` | main.py | HTTPリクエストとXMLパース |
| `parse_bloomberg_article()` | article_parser.py | 記事内容の解析（将来拡張用） |

#### **データフロー**
```
入力: "2020-09-22"
    ↓
日付解析: 2020年9月
    ↓
サイトマップ特定: sitemap_2020_9.xml
    ↓
XML取得・パース
    ↓
記事URL抽出: 42件
    ↓
結果表示: URL一覧
```

## 必要なライブラリ

```bash
pip install -r requirements.txt
```

または個別にインストール：

```bash
pip install requests beautifulsoup4 lxml
```

## 使用方法

### 1. 仮想環境の有効化

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. スクレイパーの実行

```bash
python main.py
```

### 3. 対話形式での設定

実行後、以下の情報を入力します：

1. **日付**: 取得したい日付を入力（例: 2025-09-24）

### 4. 結果の確認

- ターミナルに取得した記事の概要が表示されます
- 記事URLの一覧が表示されます

### 実行例

```bash
$ python main.py
=== Bloomberg ニュース取得ツール ===
日付を指定してBloombergのニュース記事を取得します。

取得したい日付を入力してください (例: 2025-09-24): 2020-09-22

日付: 2020-09-22
処理を開始します...

--- Bloombergの記事（2020-09-22）を取得します ---
サイトマップインデックスを取得中: https://www.bloomberg.co.jp/feeds/cojp/sitemap_index.xml
サイトマップインデックス取得成功: 432 件のサイトマップを発見
サイトマップを処理中: https://www.bloomberg.co.jp/feeds/cojp/sitemap_recent.xml
サイトマップを処理中: https://www.bloomberg.co.jp/feeds/cojp/sitemap_news.xml
サイトマップを処理中: https://www.bloomberg.co.jp/feeds/cojp/sitemap_2020_9.xml
記事URL発見: https://www.bloomberg.co.jp/news/articles/2020-09-22/QH2FMYT0AFB701
記事URL発見: https://www.bloomberg.co.jp/news/articles/2020-09-22/QH251GDWRGG501
記事URL発見: https://www.bloomberg.co.jp/news/articles/2020-09-22/QH2TSNDWLU6L01
...
取得したBloombergの記事URL数: 42
（先頭5件）:
https://www.bloomberg.co.jp/news/articles/2020-09-22/QH2FMYT0AFB701
https://www.bloomberg.co.jp/news/articles/2020-09-22/QH251GDWRGG501
https://www.bloomberg.co.jp/news/articles/2020-09-22/QH2TSNDWLU6L01
https://www.bloomberg.co.jp/news/articles/2020-09-22/QH2BEHDWX2Q301
https://www.bloomberg.co.jp/news/articles/2020-09-22/QH2ZF0DWX2Q401

=== 取得結果要約 ===
指定日付: 2020-09-22
Bloomberg: 42件
合計: 42件
```

## ファイル構成

- `main.py`: メインスクリプト
- `bloomberg_scraper_class.py`: Bloomberg専用スクレイパークラス
- `article_parser.py`: 記事解析用のテンプレート関数

## 特徴

### 効率的な処理
- 指定日付の年・月のサイトマップのみを処理
- 不要なサイトマップの処理を回避
- レート制限を考慮した適切な待機時間

### 包括的なカバレッジ
- 2000年〜2025年の全期間の記事に対応
- 432件のサイトマップから効率的に検索
- 重複記事の自動除去

### 堅牢性
- エラーハンドリングの実装
- ネットワークエラーへの対応
- 適切なUser-Agentの設定

## 注意事項

- Bloombergのサイト構造変更により動作しない場合があります
- レート制限を考慮して、記事取得間に適切な待機時間を設けています
- 利用規約を遵守してご使用ください

## トラブルシューティング

### 記事が取得できない場合

1. 指定した日付に記事が存在するか確認
2. Bloombergのサイト構造が変更されていないか確認
3. ネットワーク接続を確認

### エラーが発生した場合

詳細なエラー情報が表示されるので、エラーメッセージを確認してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。