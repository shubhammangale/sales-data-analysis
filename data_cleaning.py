"""
data_cleaning.py
Loads, cleans, and merges all CSV sources into a single master dataset.
"""

import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')
log = logging.getLogger(__name__)

DATA_DIR   = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_online(path: str) -> pd.DataFrame:
    """Standardise the online channel CSV."""
    df = pd.read_csv(path)
    log.info(f"Online raw: {len(df):,} rows")

    df = df.rename(columns={
        'order_id':       'transaction_id',
        'date':           'date',
        'product':        'product_name',
        'category':       'category',
        'region':         'region',
        'channel':        'channel',
        'quantity':       'quantity',
        'unit_price':     'unit_price',
        'revenue':        'revenue',
        'payment_method': 'payment_method',
        'customer_id':    'customer_id',
        'discount_pct':   'discount_pct',
        'return_flag':    'is_returned',
    })
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df


def load_retail(path: str) -> pd.DataFrame:
    """Standardise the retail channel CSV (messy dates & casing)."""
    df = pd.read_csv(path)
    log.info(f"Retail raw: {len(df):,} rows")

    df = df.rename(columns={
        'transaction_id': 'transaction_id',
        'sale_date':      'date',
        'item_name':      'product_name',
        'product_cat':    'category',
        'store_region':   'region',
        'sales_channel':  'channel',
        'qty_sold':       'quantity',
        'price_each':     'unit_price',
        'total_revenue':  'revenue',
        'payment':        'payment_method',
        'cust_id':        'customer_id',
        'discount':       'discount_pct',
        'returned':       'is_returned',
    })
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
    df['region'] = df['region'].str.title()  # Fix lowercase region names
    return df


def load_wholesale(path: str) -> pd.DataFrame:
    """Standardise the wholesale channel CSV."""
    df = pd.read_csv(path)
    log.info(f"Wholesale raw: {len(df):,} rows")

    df = df.rename(columns={
        'ref_number':    'transaction_id',
        'invoice_date':  'date',
        'product_name':  'product_name',
        'category':      'category',
        'territory':     'region',
        'channel':       'channel',
        'units':         'quantity',
        'unit_cost':     'unit_price',
        'gross_revenue': 'revenue',
        'payment_type':  'payment_method',
        'account_id':    'customer_id',
        'promo_rate':    'discount_pct',
        'is_returned':   'is_returned',
    })
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    return df


# ── Cleaning ──────────────────────────────────────────────────────────────────

def clean_combined(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning steps to the merged dataset."""

    initial_len = len(df)
    log.info(f"Combined before cleaning: {initial_len:,} rows")

    # 1. Drop rows with null dates
    df = df.dropna(subset=['date'])
    log.info(f"After dropping null dates: {len(df):,} rows")

    # 2. Fill missing revenue with median of same category
    missing_rev = df['revenue'].isna().sum()
    if missing_rev:
        df['revenue'] = df.groupby('category')['revenue'].transform(
            lambda x: x.fillna(x.median())
        )
        log.info(f"Filled {missing_rev} missing revenue values with category median")

    # 3. Remove obvious outliers (revenue > 99.9th percentile)
    upper_cap = df['revenue'].quantile(0.999)
    outliers = (df['revenue'] > upper_cap).sum()
    df = df[df['revenue'] <= upper_cap]
    log.info(f"Removed {outliers} revenue outliers (>{upper_cap:,.0f})")

    # 4. Remove duplicate transaction IDs
    dupes = df.duplicated(subset=['transaction_id']).sum()
    df = df.drop_duplicates(subset=['transaction_id'])
    log.info(f"Dropped {dupes} duplicate transaction IDs")

    # 5. Remove returns from revenue analysis
    returns = df['is_returned'].sum()
    df_clean = df[df['is_returned'] == 0].copy()
    log.info(f"Excluded {returns} returned transactions")

    # 6. Derived columns
    df_clean['year']    = df_clean['date'].dt.year
    df_clean['month']   = df_clean['date'].dt.month
    df_clean['quarter'] = df_clean['date'].dt.quarter
    df_clean['month_name'] = df_clean['date'].dt.strftime('%b')
    df_clean['week']    = df_clean['date'].dt.isocalendar().week.astype(int)

    log.info(f"\n✅ Clean dataset: {len(df_clean):,} rows "
             f"({initial_len - len(df_clean):,} removed)")
    return df_clean


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> pd.DataFrame:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df_online    = load_online(os.path.join(DATA_DIR, 'sales_online.csv'))
    df_retail    = load_retail(os.path.join(DATA_DIR, 'sales_retail.csv'))
    df_wholesale = load_wholesale(os.path.join(DATA_DIR, 'sales_wholesale.csv'))

    df_all = pd.concat([df_online, df_retail, df_wholesale], ignore_index=True)
    df_clean = clean_combined(df_all)

    out_path = os.path.join(OUTPUT_DIR, 'sales_master.csv')
    df_clean.to_csv(out_path, index=False)
    log.info(f"\nMaster dataset saved → {out_path}")
    return df_clean


if __name__ == '__main__':
    run()
