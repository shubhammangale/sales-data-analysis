"""
tests/test_pipeline.py
Unit tests for data cleaning and analysis modules.
"""

import pytest
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """Minimal cleaned sales dataframe for testing."""
    np.random.seed(0)
    n = 500
    quarters = np.random.choice([1, 2, 3, 4], n, p=[0.22, 0.23, 0.25, 0.30])
    months = {1: [1,2,3], 2: [4,5,6], 3: [7,8,9], 4: [10,11,12]}
    month_list = [np.random.choice(months[q]) for q in quarters]

    return pd.DataFrame({
        'transaction_id': [f'T-{i}' for i in range(n)],
        'date':           pd.date_range('2023-01-01', periods=n, freq='D')[:n],
        'product_name':   np.random.choice(['Laptop', 'T-Shirt', 'Sofa', 'Shoes'], n),
        'category':       np.random.choice(
                              ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys'], n),
        'region':         np.random.choice(['North', 'South', 'East', 'West', 'Central'], n),
        'channel':        np.random.choice(['Online', 'Retail Store', 'Wholesale'], n),
        'quantity':       np.random.randint(1, 10, n),
        'unit_price':     np.random.uniform(20, 1000, n).round(2),
        'revenue':        np.random.uniform(50, 5000, n).round(2),
        'quarter':        quarters,
        'month':          month_list,
        'month_name':     [pd.Timestamp(2023, m, 1).strftime('%b') for m in month_list],
        'is_returned':    np.zeros(n, dtype=int),
    })


# ── Data Shape Tests ──────────────────────────────────────────────────────────

def test_df_has_required_columns(sample_df):
    required = ['transaction_id', 'date', 'category', 'revenue', 'region', 'quarter']
    for col in required:
        assert col in sample_df.columns, f"Missing column: {col}"


def test_no_null_revenue(sample_df):
    assert sample_df['revenue'].isnull().sum() == 0


def test_revenue_positive(sample_df):
    assert (sample_df['revenue'] > 0).all()


def test_quarters_valid(sample_df):
    assert set(sample_df['quarter'].unique()).issubset({1, 2, 3, 4})


def test_no_duplicate_transaction_ids(sample_df):
    assert sample_df['transaction_id'].duplicated().sum() == 0


# ── Cleaning Logic Tests ──────────────────────────────────────────────────────

def test_region_normalisation():
    """Lowercase region names should be title-cased."""
    df = pd.DataFrame({'region': ['north', 'SOUTH', 'East', 'west', 'Central']})
    df['region'] = df['region'].str.title()
    assert list(df['region']) == ['North', 'South', 'East', 'West', 'Central']


def test_missing_revenue_filled():
    """Missing revenues should be filled with category median."""
    df = pd.DataFrame({
        'category': ['Electronics', 'Electronics', 'Electronics', 'Books'],
        'revenue':  [100.0, 200.0, None, 50.0],
    })
    df['revenue'] = df.groupby('category')['revenue'].transform(
        lambda x: x.fillna(x.median())
    )
    assert df['revenue'].isnull().sum() == 0
    assert df.loc[2, 'revenue'] == 150.0  # median of [100, 200]


def test_outlier_removal():
    """Values above 99.9th percentile should be removed."""
    df = pd.DataFrame({'revenue': list(range(1, 1001)) + [9_999_999]})
    cap = df['revenue'].quantile(0.999)
    df_clean = df[df['revenue'] <= cap]
    assert 9_999_999 not in df_clean['revenue'].values


def test_duplicate_removal():
    df = pd.DataFrame({
        'transaction_id': ['A', 'A', 'B'],
        'revenue': [100, 100, 200],
    })
    df_clean = df.drop_duplicates(subset=['transaction_id'])
    assert len(df_clean) == 2


# ── Analysis Tests ────────────────────────────────────────────────────────────

def test_quarterly_revenue_shape(sample_df):
    q = sample_df.groupby('quarter')['revenue'].sum()
    assert len(q) == 4


def test_top3_categories(sample_df):
    cat = sample_df.groupby('category')['revenue'].sum().nlargest(3)
    assert len(cat) == 3


def test_revenue_share_sums_to_100(sample_df):
    cat = sample_df.groupby('category')['revenue'].sum()
    share = (cat / cat.sum() * 100).round(1)
    assert abs(share.sum() - 100.0) < 0.5   # allow rounding tolerance


def test_monthly_trend_has_12_months(sample_df):
    monthly = sample_df.groupby('month')['revenue'].sum()
    assert len(monthly) <= 12


def test_q4_growth_calculation():
    q_rev = pd.Series({3: 1_000_000, 4: 1_230_000})
    growth = (q_rev[4] - q_rev[3]) / q_rev[3] * 100
    assert abs(growth - 23.0) < 0.01


# ── KPI Metric Tests ──────────────────────────────────────────────────────────

def test_avg_order_value(sample_df):
    aov = sample_df['revenue'].mean()
    assert aov > 0
    assert isinstance(aov, float)


def test_return_rate(sample_df):
    rate = sample_df['is_returned'].sum() / len(sample_df) * 100
    assert 0 <= rate <= 100


def test_channel_revenue_coverage(sample_df):
    ch = sample_df.groupby('channel')['revenue'].sum()
    assert ch.sum() == pytest.approx(sample_df['revenue'].sum(), rel=1e-6)
