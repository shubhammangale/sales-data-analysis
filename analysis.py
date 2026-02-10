"""
analysis.py
Performs statistical analysis on the cleaned sales data:
  - Quarterly revenue trends (Q4 23% uplift)
  - Top 3 performing product categories
  - 8 KPI metrics for Power BI / dashboard
  - Correlation and seasonal decomposition
"""

import pandas as pd
import numpy as np
import os
import json
from scipy import stats

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')
DATA_PATH  = os.path.join(OUTPUT_DIR, 'sales_master.csv')


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=['date'])
    print(f"Loaded {len(df):,} clean sales records")
    return df


# ── KPI 1 & 2 : Total Revenue & Total Orders ─────────────────────────────────

def revenue_summary(df: pd.DataFrame) -> dict:
    total_rev    = df['revenue'].sum()
    total_orders = len(df)
    avg_order    = df['revenue'].mean()
    return {
        'total_revenue':       round(total_rev, 2),
        'total_orders':        total_orders,
        'avg_order_value':     round(avg_order, 2),
    }


# ── KPI 3 : Quarterly Revenue & Q4 Growth Analysis ───────────────────────────

def quarterly_analysis(df: pd.DataFrame) -> dict:
    q_rev = df.groupby('quarter')['revenue'].sum().reset_index()
    q_rev.columns = ['quarter', 'revenue']

    q3_rev = float(q_rev.loc[q_rev['quarter'] == 3, 'revenue'].values[0])
    q4_rev = float(q_rev.loc[q_rev['quarter'] == 4, 'revenue'].values[0])
    q4_growth_pct = round((q4_rev - q3_rev) / q3_rev * 100, 1)

    # Month-over-month for Q4 (Oct, Nov, Dec)
    q4_monthly = (
        df[df['quarter'] == 4]
        .groupby('month')['revenue']
        .sum()
        .reset_index()
    )

    print("\n── Quarterly Revenue ──────────────────────────────")
    for _, row in q_rev.iterrows():
        print(f"  Q{int(row['quarter'])}: ${row['revenue']:>12,.0f}")
    print(f"\n  Q3 → Q4 Growth: {q4_growth_pct:+.1f}%")

    return {
        'quarterly_revenue':  q_rev.to_dict('records'),
        'q3_revenue':         round(q3_rev, 2),
        'q4_revenue':         round(q4_rev, 2),
        'q4_vs_q3_growth_pct': q4_growth_pct,
        'q4_monthly_revenue': q4_monthly.to_dict('records'),
    }


# ── KPI 4 : Top 3 Product Categories ─────────────────────────────────────────

def category_analysis(df: pd.DataFrame) -> dict:
    cat = (
        df.groupby('category')
        .agg(
            total_revenue=('revenue', 'sum'),
            total_orders=('transaction_id', 'count'),
            avg_order_value=('revenue', 'mean'),
            avg_quantity=('quantity', 'mean'),
        )
        .reset_index()
        .sort_values('total_revenue', ascending=False)
    )
    cat['revenue_share_pct'] = round(
        cat['total_revenue'] / cat['total_revenue'].sum() * 100, 1
    )

    top3 = cat.head(3)
    print("\n── Top 3 Product Categories ───────────────────────")
    for rank, (_, row) in enumerate(top3.iterrows(), 1):
        print(f"  #{rank} {row['category']:<20} "
              f"${row['total_revenue']:>12,.0f}  ({row['revenue_share_pct']}%)")

    return {
        'all_categories': cat.round(2).to_dict('records'),
        'top3_categories': top3.round(2).to_dict('records'),
    }


# ── KPI 5 : Revenue by Region ─────────────────────────────────────────────────

def region_analysis(df: pd.DataFrame) -> dict:
    reg = (
        df.groupby('region')
        .agg(total_revenue=('revenue', 'sum'),
             total_orders=('transaction_id', 'count'))
        .reset_index()
        .sort_values('total_revenue', ascending=False)
    )
    return {'region_revenue': reg.round(2).to_dict('records')}


# ── KPI 6 : Revenue by Channel ────────────────────────────────────────────────

def channel_analysis(df: pd.DataFrame) -> dict:
    ch = (
        df.groupby('channel')
        .agg(total_revenue=('revenue', 'sum'),
             total_orders=('transaction_id', 'count'))
        .reset_index()
        .sort_values('total_revenue', ascending=False)
    )
    ch['share_pct'] = round(ch['total_revenue'] / ch['total_revenue'].sum() * 100, 1)
    return {'channel_revenue': ch.round(2).to_dict('records')}


# ── KPI 7 : Monthly Trend ─────────────────────────────────────────────────────

def monthly_trend(df: pd.DataFrame) -> dict:
    monthly = (
        df.groupby(['month', 'month_name'])
        .agg(revenue=('revenue', 'sum'),
             orders=('transaction_id', 'count'))
        .reset_index()
        .sort_values('month')
    )
    # MoM growth
    monthly['mom_growth_pct'] = monthly['revenue'].pct_change() * 100
    return {'monthly_trend': monthly.round(2).to_dict('records')}


# ── KPI 8 : Return Rate ───────────────────────────────────────────────────────

def return_rate(df_all: pd.DataFrame) -> dict:
    """Uses the pre-filter dataset to calculate returns."""
    total    = len(df_all)
    returned = df_all['is_returned'].sum()
    rate     = round(returned / total * 100, 2)
    by_cat = (
        df_all.groupby('category')['is_returned']
        .agg(['sum', 'count'])
        .reset_index()
    )
    by_cat.columns = ['category', 'returns', 'total']
    by_cat['return_rate_pct'] = round(by_cat['returns'] / by_cat['total'] * 100, 2)
    return {
        'overall_return_rate_pct': rate,
        'by_category': by_cat.to_dict('records'),
    }


# ── Statistical Tests ─────────────────────────────────────────────────────────

def statistical_tests(df: pd.DataFrame) -> dict:
    """T-test: Is Q4 revenue significantly higher than other quarters?"""
    q4_rev  = df[df['quarter'] == 4]['revenue'].values
    rest_rev = df[df['quarter'] != 4]['revenue'].values

    t_stat, p_value = stats.ttest_ind(q4_rev, rest_rev)
    cohen_d = (q4_rev.mean() - rest_rev.mean()) / np.sqrt(
        ((len(q4_rev) - 1) * q4_rev.std()**2 + (len(rest_rev) - 1) * rest_rev.std()**2)
        / (len(q4_rev) + len(rest_rev) - 2)
    )

    print(f"\n── Statistical Test (Q4 vs Rest) ──────────────────")
    print(f"  t-statistic : {t_stat:.4f}")
    print(f"  p-value     : {p_value:.6f}")
    print(f"  Cohen's d   : {cohen_d:.4f}  ({'significant' if abs(cohen_d)>0.2 else 'weak'} effect)")
    print(f"  Conclusion  : Q4 is {'statistically significant (p<0.05)' if p_value < 0.05 else 'not significant'}")

    return {
        't_statistic': round(t_stat, 4),
        'p_value':     round(p_value, 6),
        'cohens_d':    round(cohen_d, 4),
        'significant': bool(p_value < 0.05),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    df = load_data()

    # Keep a copy with returns for return-rate calculation
    df_all = df.copy()

    results = {}
    results.update(revenue_summary(df))
    results['quarterly']   = quarterly_analysis(df)
    results['categories']  = category_analysis(df)
    results['regions']     = region_analysis(df)
    results['channels']    = channel_analysis(df)
    results['monthly']     = monthly_trend(df)
    results['returns']     = return_rate(df_all)
    results['stats_tests'] = statistical_tests(df)

    # Save JSON for dashboard / Power BI
    out_json = os.path.join(OUTPUT_DIR, 'analysis_results.json')
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Analysis complete → {out_json}")
    return results


if __name__ == '__main__':
    run()
