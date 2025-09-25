import pandas as pd

def fix_csv_for_excel(input_file, output_file):
    """エクセル用にCSVファイルを修正する"""
    print(f"CSVファイルを読み込み中: {input_file}")
    
    # 現在のCSVファイルを読み込み
    df = pd.read_csv(input_file)
    
    print(f"データ行数: {len(df)}")
    print(f"列名: {list(df.columns)}")
    
    # エクセル用にCSVファイルを保存（UTF-8 BOM付き）
    print(f"エクセル用CSVファイルを保存中: {output_file}")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("保存完了！")
    print("\n=== エクセルでの開き方 ===")
    print("1. エクセルを開く")
    print("2. [ファイル] → [開く] → [参照]")
    print("3. ファイルの種類を「すべてのファイル」に変更")
    print("4. 生成されたCSVファイルを選択")
    print("5. テキストファイルウィザードが開いたら:")
    print("   - 区切り文字: カンマ")
    print("   - 文字コード: UTF-8")
    print("   - [完了]をクリック")
    
    return df

def create_excel_file(input_file, output_file):
    """直接エクセルファイル(.xlsx)を作成する"""
    print(f"\n=== エクセルファイル(.xlsx)を作成中 ===")
    
    # CSVファイルを読み込み
    df = pd.read_csv(input_file)
    
    # エクセルファイルとして保存
    excel_output = output_file.replace('.csv', '.xlsx')
    print(f"エクセルファイルを保存中: {excel_output}")
    
    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sentiment Analysis', index=False)
        
        # ワークシートを取得してフォーマットを調整
        worksheet = writer.sheets['Sentiment Analysis']
        
        # 列幅を自動調整
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # 最大50文字
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"エクセルファイル保存完了: {excel_output}")
    return excel_output

def main():
    """メイン関数"""
    input_file = "data_with_sentiment_scores_correct.csv"
    output_file = "data_with_sentiment_scores_excel.csv"
    
    print("=== エクセル用CSVファイル修正ツール ===")
    
    try:
        # エクセル用CSVファイルを作成
        df = fix_csv_for_excel(input_file, output_file)
        
        # エクセルファイルも作成
        excel_file = create_excel_file(input_file, output_file)
        
        print(f"\n=== 完了 ===")
        print(f"1. エクセル用CSVファイル: {output_file}")
        print(f"2. エクセルファイル: {excel_file}")
        print("\nどちらもエクセルで正しく表示されるはずです！")
        
        # データの概要を表示
        print(f"\n=== データ概要 ===")
        print(f"総行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        
        # センチメントスコアの統計
        if 'avg_sentiment_score' in df.columns:
            sentiment_scores = df['avg_sentiment_score']
            print(f"\nセンチメントスコア統計:")
            print(f"  平均: {sentiment_scores.mean():.4f}")
            print(f"  中央値: {sentiment_scores.median():.4f}")
            print(f"  標準偏差: {sentiment_scores.std():.4f}")
            print(f"  最小値: {sentiment_scores.min():.4f}")
            print(f"  最大値: {sentiment_scores.max():.4f}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
