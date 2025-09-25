import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# 日本語フォントの設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

class CorrelationAnalyzer:
    def __init__(self, csv_path):
        """CSVファイルを読み込み、データを準備"""
        self.df = pd.read_csv(csv_path)
        print(f"データを読み込みました: {len(self.df)} 行")
        print(f"列名: {list(self.df.columns)}")
        
        # 必要な列の存在確認
        required_columns = ['jump_width', 'avg_sentiment_score']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"必要な列 '{col}' が見つかりません")
        
        # データのクリーニング
        self.clean_data()
    
    def clean_data(self):
        """データのクリーニングと前処理"""
        print("\n=== データクリーニング ===")
        
        # 元のデータ数
        original_count = len(self.df)
        
        # 欠損値の確認
        print(f"jump_width の欠損値: {self.df['jump_width'].isna().sum()}")
        print(f"avg_sentiment_score の欠損値: {self.df['avg_sentiment_score'].isna().sum()}")
        
        # 欠損値を除去
        self.df_clean = self.df.dropna(subset=['jump_width', 'avg_sentiment_score'])
        
        # 外れ値の確認
        print(f"\n=== データの基本統計 ===")
        print(f"jump_width:")
        print(f"  平均: {self.df_clean['jump_width'].mean():.4f}")
        print(f"  標準偏差: {self.df_clean['jump_width'].std():.4f}")
        print(f"  最小値: {self.df_clean['jump_width'].min():.4f}")
        print(f"  最大値: {self.df_clean['jump_width'].max():.4f}")
        
        print(f"avg_sentiment_score:")
        print(f"  平均: {self.df_clean['avg_sentiment_score'].mean():.4f}")
        print(f"  標準偏差: {self.df_clean['avg_sentiment_score'].std():.4f}")
        print(f"  最小値: {self.df_clean['avg_sentiment_score'].min():.4f}")
        print(f"  最大値: {self.df_clean['avg_sentiment_score'].max():.4f}")
        
        print(f"\nクリーニング後のデータ数: {len(self.df_clean)} (元: {original_count})")
    
    def calculate_correlation(self):
        """相関係数の計算"""
        print("\n=== 相関分析 ===")
        
        # ピアソンの相関係数
        pearson_corr, pearson_p = pearsonr(self.df_clean['jump_width'], self.df_clean['avg_sentiment_score'])
        
        # スピアマンの相関係数
        spearman_corr, spearman_p = spearmanr(self.df_clean['jump_width'], self.df_clean['avg_sentiment_score'])
        
        print(f"ピアソンの相関係数: {pearson_corr:.4f} (p値: {pearson_p:.4f})")
        print(f"スピアマンの相関係数: {spearman_corr:.4f} (p値: {spearman_p:.4f})")
        
        # 相関の強さの解釈
        def interpret_correlation(corr):
            abs_corr = abs(corr)
            if abs_corr >= 0.7:
                return "強い相関"
            elif abs_corr >= 0.5:
                return "中程度の相関"
            elif abs_corr >= 0.3:
                return "弱い相関"
            else:
                return "ほとんど相関なし"
        
        print(f"\n相関の解釈:")
        print(f"  ピアソン: {interpret_correlation(pearson_corr)}")
        print(f"  スピアマン: {interpret_correlation(spearman_corr)}")
        
        return {
            'pearson_corr': pearson_corr,
            'pearson_p': pearson_p,
            'spearman_corr': spearman_corr,
            'spearman_p': spearman_p
        }
    
    def create_visualizations(self, correlation_results):
        """可視化の作成"""
        print("\n=== グラフ作成中 ===")
        
        # 図のサイズを設定
        fig = plt.figure(figsize=(20, 15))
        
        # 1. 散布図
        plt.subplot(2, 3, 1)
        plt.scatter(self.df_clean['jump_width'], self.df_clean['avg_sentiment_score'], 
                   alpha=0.6, s=50, color='blue')
        plt.xlabel('Jump Width', fontsize=12)
        plt.ylabel('Average Sentiment Score', fontsize=12)
        plt.title('Jump Width vs Sentiment Score\n(Scatter Plot)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # 回帰直線を追加
        z = np.polyfit(self.df_clean['jump_width'], self.df_clean['avg_sentiment_score'], 1)
        p = np.poly1d(z)
        plt.plot(self.df_clean['jump_width'], p(self.df_clean['jump_width']), 
                "r--", alpha=0.8, linewidth=2, 
                label=f'回帰直線 (傾き: {z[0]:.4f})')
        plt.legend()
        
        # 2. ヒートマップ（相関行列）
        plt.subplot(2, 3, 2)
        corr_matrix = self.df_clean[['jump_width', 'avg_sentiment_score']].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.4f', cbar_kws={'shrink': 0.8})
        plt.title('相関行列', fontsize=14, fontweight='bold')
        
        # 3. ヒストグラム（Jump Width）
        plt.subplot(2, 3, 3)
        plt.hist(self.df_clean['jump_width'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel('Jump Width', fontsize=12)
        plt.ylabel('頻度', fontsize=12)
        plt.title('Jump Width の分布', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # 4. ヒストグラム（Sentiment Score）
        plt.subplot(2, 3, 4)
        plt.hist(self.df_clean['avg_sentiment_score'], bins=30, alpha=0.7, color='lightcoral', edgecolor='black')
        plt.xlabel('Average Sentiment Score', fontsize=12)
        plt.ylabel('頻度', fontsize=12)
        plt.title('Sentiment Score の分布', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # 5. 箱ひげ図
        plt.subplot(2, 3, 5)
        data_for_box = [self.df_clean['jump_width'], self.df_clean['avg_sentiment_score']]
        labels = ['Jump Width', 'Sentiment Score']
        plt.boxplot(data_for_box, labels=labels)
        plt.title('箱ひげ図', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # 6. 統計情報の表示
        plt.subplot(2, 3, 6)
        plt.axis('off')
        
        # 統計情報のテキスト
        stats_text = f"""
        相関分析結果
        
        データ数: {len(self.df_clean)}
        
        ピアソンの相関係数:
        r = {correlation_results['pearson_corr']:.4f}
        p値 = {correlation_results['pearson_p']:.4f}
        
        スピアマンの相関係数:
        ρ = {correlation_results['spearman_corr']:.4f}
        p値 = {correlation_results['spearman_p']:.4f}
        
        Jump Width:
        平均 = {self.df_clean['jump_width'].mean():.4f}
        標準偏差 = {self.df_clean['jump_width'].std():.4f}
        
        Sentiment Score:
        平均 = {self.df_clean['avg_sentiment_score'].mean():.4f}
        標準偏差 = {self.df_clean['avg_sentiment_score'].std():.4f}
        """
        
        plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('correlation_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("グラフを 'correlation_analysis.png' として保存しました。")
    
    def create_detailed_scatter_plot(self, correlation_results):
        """詳細な散布図の作成"""
        print("\n=== 詳細散布図作成中 ===")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 散布図
        scatter = ax.scatter(self.df_clean['jump_width'], self.df_clean['avg_sentiment_score'], 
                           alpha=0.6, s=60, c=self.df_clean['avg_sentiment_score'], 
                           cmap='RdYlBu_r', edgecolors='black', linewidth=0.5)
        
        # 回帰直線
        z = np.polyfit(self.df_clean['jump_width'], self.df_clean['avg_sentiment_score'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(self.df_clean['jump_width'].min(), self.df_clean['jump_width'].max(), 100)
        ax.plot(x_line, p(x_line), "r-", linewidth=3, alpha=0.8, 
               label=f'回帰直線: y = {z[0]:.4f}x + {z[1]:.4f}')
        
        # 信頼区間（95%）
        from scipy import stats
        n = len(self.df_clean)
        x_mean = self.df_clean['jump_width'].mean()
        y_mean = self.df_clean['avg_sentiment_score'].mean()
        sxx = np.sum((self.df_clean['jump_width'] - x_mean) ** 2)
        sxy = np.sum((self.df_clean['jump_width'] - x_mean) * (self.df_clean['avg_sentiment_score'] - y_mean))
        syy = np.sum((self.df_clean['avg_sentiment_score'] - y_mean) ** 2)
        
        # 残差の標準誤差
        sse = syy - (sxy ** 2) / sxx
        mse = sse / (n - 2)
        se = np.sqrt(mse)
        
        # 信頼区間の計算
        t_val = stats.t.ppf(0.975, n - 2)
        se_pred = se * np.sqrt(1 + 1/n + (x_line - x_mean)**2 / sxx)
        
        ax.fill_between(x_line, p(x_line) - t_val * se_pred, p(x_line) + t_val * se_pred, 
                       alpha=0.2, color='red', label='95% 信頼区間')
        
        # カラーバー
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Sentiment Score', fontsize=12)
        
        # ラベルとタイトル
        ax.set_xlabel('Jump Width', fontsize=14, fontweight='bold')
        ax.set_ylabel('Average Sentiment Score', fontsize=14, fontweight='bold')
        ax.set_title('Jump Width vs Sentiment Score の相関分析\n' + 
                    f'ピアソン相関係数: r = {correlation_results["pearson_corr"]:.4f} ' +
                    f'(p = {correlation_results["pearson_p"]:.4f})', 
                    fontsize=16, fontweight='bold')
        
        # グリッドと凡例
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=12)
        
        # 統計情報をテキストで追加
        stats_text = f'n = {len(self.df_clean)}\nR² = {correlation_results["pearson_corr"]**2:.4f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('detailed_correlation_plot.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("詳細散布図を 'detailed_correlation_plot.png' として保存しました。")
    
    def run_analysis(self):
        """分析の実行"""
        print("=== Jump Width と Sentiment Score の相関分析 ===")
        
        # 相関分析
        correlation_results = self.calculate_correlation()
        
        # 可視化
        self.create_visualizations(correlation_results)
        self.create_detailed_scatter_plot(correlation_results)
        
        return correlation_results

def main():
    """メイン関数"""
    csv_path = "data_with_sentiment_scores_correct.csv"
    
    print("=== 相関分析ツール ===")
    print(f"分析対象ファイル: {csv_path}")
    
    try:
        # 分析の実行
        analyzer = CorrelationAnalyzer(csv_path)
        results = analyzer.run_analysis()
        
        print(f"\n=== 分析完了 ===")
        print(f"結果:")
        print(f"  ピアソン相関係数: {results['pearson_corr']:.4f}")
        print(f"  スピアマン相関係数: {results['spearman_corr']:.4f}")
        print(f"  グラフファイル: correlation_analysis.png, detailed_correlation_plot.png")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    main()
