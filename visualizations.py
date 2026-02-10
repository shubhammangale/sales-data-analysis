"""
visualizations.py
Generates all charts saved as PNG images in outputs/images/.
Charts mirror what would appear in the Power BI dashboard.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import os, json

DATA_PATH  = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'sales_master.csv')
JSON_PATH  = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'analysis_results.json')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'images')

# Brand palette
PALETTE = ['#2563EB', '#7C3AED', '#DB2777', '#D97706', '#059669', '#DC2626', '#64748B']
BG      = '#F8FAFC'
GRID    = '#E2E8F0'

os.makedirs(IMAGES_DIR, exist_ok=True)


def styled_fig(figsize=(10, 5)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    ax.set_facecolor(BG)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRID)
    ax.spines['bottom'].set_color(GRID)
    return fig, ax


def fmt_millions(x, _):
    return f'${x/1_000_000:.1f}M'

def fmt_k(x, _):
    return f'${x/1_000:.0f}K'


# ── Chart 1: Monthly Revenue Trend ───────────────────────────────────────────

def chart_monthly_trend(df):
    monthly = (
        df.groupby(['month', 'month_name'])['revenue']
        .sum().reset_index().sort_values('month')
    )
    fig, ax = styled_fig((12, 5))
    ax.plot(monthly['month_name'], monthly['revenue'] / 1e6,
            color=PALETTE[0], linewidth=2.5, marker='o', markersize=6, zorder=3)
    ax.fill_between(range(len(monthly)), monthly['revenue'] / 1e6,
                    alpha=0.12, color=PALETTE[0])

    # Highlight Q4
    for i, row in monthly.iterrows():
        if row['month'] >= 10:
            ax.axvspan(row['month'] - 1.5, row['month'] - 0.5,
                       alpha=0.10, color=PALETTE[3], zorder=1)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.set_xlabel('Month', fontsize=11)
    ax.set_ylabel('Revenue', fontsize=11)
    ax.set_title('Monthly Revenue Trend (2023)  |  🟠 Q4 Highlighted', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly['month_name'])
    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_monthly_trend.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 2: Quarterly Revenue Bar ───────────────────────────────────────────

def chart_quarterly(df):
    q = df.groupby('quarter')['revenue'].sum().reset_index()
    labels = [f'Q{int(x)}' for x in q['quarter']]
    colors = [PALETTE[3] if x == 4 else PALETTE[0] for x in q['quarter']]

    fig, ax = styled_fig((8, 5))
    bars = ax.bar(labels, q['revenue'] / 1e6, color=colors, width=0.55, zorder=3)

    for bar, val in zip(bars, q['revenue']):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                f'${val/1e6:.2f}M', ha='center', va='bottom', fontsize=11, fontweight='bold')

    q3 = q.loc[q['quarter'] == 3, 'revenue'].values[0]
    q4 = q.loc[q['quarter'] == 4, 'revenue'].values[0]
    growth = (q4 - q3) / q3 * 100
    ax.annotate(f'+{growth:.0f}% Q4 Growth',
                xy=(3, q4 / 1e6), xytext=(2.2, q4 / 1e6 + 0.3),
                arrowprops=dict(arrowstyle='->', color='#059669', lw=1.8),
                fontsize=11, color='#059669', fontweight='bold')

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.set_title('Quarterly Revenue Comparison', fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel('Revenue')
    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_quarterly.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 3: Top Product Categories ──────────────────────────────────────────

def chart_categories(df):
    cat = (
        df.groupby('category')['revenue']
        .sum().reset_index()
        .sort_values('revenue', ascending=True)
    )
    colors = [PALETTE[1] if i >= len(cat) - 3 else '#CBD5E1'
              for i in range(len(cat))]

    fig, ax = styled_fig((10, 5))
    bars = ax.barh(cat['category'], cat['revenue'] / 1e6, color=colors, height=0.6, zorder=3)

    for bar, val in zip(bars, cat['revenue']):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'${val/1e6:.2f}M', va='center', fontsize=10)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.set_xlabel('Total Revenue')
    ax.set_title('Revenue by Product Category  |  🟣 Top 3', fontsize=13, fontweight='bold', pad=15)

    legend = [
        mpatches.Patch(color=PALETTE[1], label='Top 3 Categories'),
        mpatches.Patch(color='#CBD5E1', label='Other Categories'),
    ]
    ax.legend(handles=legend, loc='lower right')
    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_categories.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 4: Revenue by Region ────────────────────────────────────────────────

def chart_region(df):
    reg = df.groupby('region')['revenue'].sum().reset_index()
    fig, ax = styled_fig((7, 7))
    ax.axis('equal')
    ax.axis('off')

    wedges, texts, autotexts = ax.pie(
        reg['revenue'],
        labels=reg['region'],
        autopct='%1.1f%%',
        colors=PALETTE[:len(reg)],
        startangle=140,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight('bold')

    ax.set_title('Revenue Distribution by Region', fontsize=13, fontweight='bold', pad=20)
    path = os.path.join(IMAGES_DIR, 'chart_region.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 5: Sales Channel Breakdown ─────────────────────────────────────────

def chart_channel(df):
    ch = df.groupby('channel')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
    fig, ax = styled_fig((8, 5))
    bars = ax.bar(ch['channel'], ch['revenue'] / 1e6, color=PALETTE[2:2 + len(ch)], width=0.5, zorder=3)

    for bar, val in zip(bars, ch['revenue']):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.03,
                f'${val/1e6:.2f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.set_title('Revenue by Sales Channel', fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel('Revenue')
    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_channel.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 6: Category × Quarter Heatmap ──────────────────────────────────────

def chart_heatmap(df):
    pivot = df.pivot_table(index='category', columns='quarter',
                           values='revenue', aggfunc='sum') / 1e6

    fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG)
    ax.set_facecolor(BG)

    import matplotlib.cm as cm
    im = ax.imshow(pivot.values, cmap='Blues', aspect='auto')
    plt.colorbar(im, ax=ax, label='Revenue ($M)')

    ax.set_xticks(range(4))
    ax.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            ax.text(j, i, f'${val:.1f}M', ha='center', va='center',
                    fontsize=9, color='white' if val > pivot.values.max() * 0.6 else '#1E293B')

    ax.set_title('Category Revenue Heatmap by Quarter', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_heatmap.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 7: Average Order Value by Category ─────────────────────────────────

def chart_aov(df):
    aov = (
        df.groupby('category')['revenue']
        .mean().reset_index()
        .sort_values('revenue', ascending=False)
    )
    fig, ax = styled_fig((10, 5))
    bars = ax.bar(aov['category'], aov['revenue'],
                  color=PALETTE[:len(aov)], width=0.55, zorder=3)

    for bar, val in zip(bars, aov['revenue']):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 2,
                f'${val:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_title('Average Order Value by Category', fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel('Avg Order Value ($)')
    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_aov.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {path}")


# ── Chart 8: KPI Summary Card ─────────────────────────────────────────────────

def chart_kpi_summary(df):
    with open(JSON_PATH) as f:
        results = json.load(f)

    kpis = [
        ('Total Revenue',    f"${results['total_revenue']/1e6:.2f}M"),
        ('Total Orders',     f"{results['total_orders']:,}"),
        ('Avg Order Value',  f"${results['avg_order_value']:,.0f}"),
        ('Q4 Growth vs Q3',  f"+{results['quarterly']['q4_vs_q3_growth_pct']}%"),
        ('Top Category',     results['categories']['top3_categories'][0]['category']),
        ('Return Rate',      f"{results['returns']['overall_return_rate_pct']}%"),
        ('Q4 Revenue',       f"${results['quarterly']['q4_revenue']/1e6:.2f}M"),
        ('Online Share',     f"{next(c['share_pct'] for c in results['channels']['channel_revenue'] if c['channel']=='Online')}%"),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(14, 5), facecolor='#1E293B')
    fig.suptitle('Sales Performance KPI Dashboard  |  FY 2023',
                 fontsize=14, fontweight='bold', color='white', y=1.02)

    for ax, (label, value) in zip(axes.flat, kpis):
        ax.set_facecolor('#1E293B')
        ax.axis('off')
        ax.text(0.5, 0.65, value, ha='center', va='center',
                fontsize=20, fontweight='bold', color='#60A5FA',
                transform=ax.transAxes)
        ax.text(0.5, 0.25, label, ha='center', va='center',
                fontsize=10, color='#94A3B8',
                transform=ax.transAxes)
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')

    plt.tight_layout()
    path = os.path.join(IMAGES_DIR, 'chart_kpi_dashboard.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#1E293B')
    plt.close()
    print(f"  ✓ {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    df = pd.read_csv(DATA_PATH, parse_dates=['date'])
    print(f"Generating charts for {len(df):,} records...\n")

    chart_monthly_trend(df)
    chart_quarterly(df)
    chart_categories(df)
    chart_region(df)
    chart_channel(df)
    chart_heatmap(df)
    chart_aov(df)
    chart_kpi_summary(df)

    print(f"\n✅ All 8 charts saved to {IMAGES_DIR}")


if __name__ == '__main__':
    run()
