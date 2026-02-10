"""
generate_data.py
Generates synthetic sales data mimicking real-world CSV exports from multiple sources.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
TOTAL_RECORDS = 15000
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

PRODUCT_CATEGORIES = {
    'Electronics':    {'price_range': (200, 2500), 'weight': 0.28},
    'Clothing':       {'price_range': (15,  250),  'weight': 0.22},
    'Home & Garden':  {'price_range': (25,  800),  'weight': 0.18},
    'Sports':         {'price_range': (30,  600),  'weight': 0.16},
    'Books':          {'price_range': (8,   80),   'weight': 0.10},
    'Toys':           {'price_range': (10,  200),  'weight': 0.06},
}

REGIONS = ['North', 'South', 'East', 'West', 'Central']
SALES_CHANNELS = ['Online', 'Retail Store', 'Wholesale', 'Direct Sales']
PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash']

PRODUCTS = {
    'Electronics':   ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Smart Watch',
                      'Camera', 'Monitor', 'Keyboard', 'Mouse', 'USB Hub'],
    'Clothing':      ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Shoes',
                      'Sneakers', 'Sweater', 'Shorts', 'Coat', 'Scarf'],
    'Home & Garden': ['Sofa', 'Lamp', 'Rug', 'Curtains', 'Plant Pot',
                      'Shelf', 'Mirror', 'Cushion', 'Vase', 'Candle Set'],
    'Sports':        ['Running Shoes', 'Yoga Mat', 'Dumbbell Set', 'Bicycle', 'Tennis Racket',
                      'Swimming Goggles', 'Gym Bag', 'Water Bottle', 'Resistance Bands', 'Jump Rope'],
    'Books':         ['Fiction Novel', 'Business Guide', 'Cookbook', 'Self-Help', 'Science Book',
                      'History Book', 'Art Book', 'Travel Guide', 'Programming Book', 'Biography'],
    'Toys':          ['LEGO Set', 'Board Game', 'Action Figure', 'Puzzle', 'RC Car',
                      'Doll', 'Educational Kit', 'Card Game', 'Building Blocks', 'Craft Kit'],
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def seasonal_multiplier(month):
    """Q4 gets a 23% revenue boost to match the analysis narrative."""
    seasonal = {1: 0.82, 2: 0.78, 3: 0.90, 4: 0.88,
                5: 0.95, 6: 0.97, 7: 0.93, 8: 0.91,
                9: 0.99, 10: 1.05, 11: 1.18, 12: 1.28}
    return seasonal.get(month, 1.0)


def generate_source_a(n):
    """Online sales platform export."""
    dates = [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364)) for _ in range(n)]
    categories = random.choices(
        list(PRODUCT_CATEGORIES.keys()),
        weights=[v['weight'] for v in PRODUCT_CATEGORIES.values()],
        k=n
    )
    records = []
    for i, (date, cat) in enumerate(zip(dates, categories)):
        price_range = PRODUCT_CATEGORIES[cat]['price_range']
        base_price = round(np.random.uniform(*price_range), 2)
        qty = np.random.randint(1, 6)
        mult = seasonal_multiplier(date.month)
        revenue = round(base_price * qty * mult, 2)
        records.append({
            'order_id':       f'ONL-{10000 + i}',
            'date':           date.strftime('%Y-%m-%d'),
            'product':        random.choice(PRODUCTS[cat]),
            'category':       cat,
            'region':         random.choice(REGIONS),
            'channel':        'Online',
            'quantity':       qty,
            'unit_price':     base_price,
            'revenue':        revenue,
            'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal']),
            'customer_id':    f'CUST-{random.randint(1000, 9999)}',
            'discount_pct':   round(random.uniform(0, 0.20), 2),
            'return_flag':    random.choices([0, 1], weights=[0.93, 0.07])[0],
        })
    return pd.DataFrame(records)


def generate_source_b(n):
    """Retail store POS export — slightly dirtier data."""
    dates = [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364)) for _ in range(n)]
    categories = random.choices(
        list(PRODUCT_CATEGORIES.keys()),
        weights=[v['weight'] for v in PRODUCT_CATEGORIES.values()],
        k=n
    )
    records = []
    for i, (date, cat) in enumerate(zip(dates, categories)):
        price_range = PRODUCT_CATEGORIES[cat]['price_range']
        base_price = round(np.random.uniform(*price_range), 2)
        qty = np.random.randint(1, 4)
        mult = seasonal_multiplier(date.month)
        revenue = round(base_price * qty * mult, 2)

        # Introduce some dirty data for cleaning demo
        region = random.choice(REGIONS)
        if random.random() < 0.03:   # 3% messy region names
            region = region.lower()
        if random.random() < 0.02:   # 2% missing revenue
            revenue = None

        records.append({
            'transaction_id': f'RET-{20000 + i}',
            'sale_date':       date.strftime('%d/%m/%Y'),   # different date format
            'item_name':       random.choice(PRODUCTS[cat]),
            'product_cat':     cat,
            'store_region':    region,
            'sales_channel':   random.choice(['Retail Store', 'Direct Sales']),
            'qty_sold':        qty,
            'price_each':      base_price,
            'total_revenue':   revenue,
            'payment':         random.choice(PAYMENT_METHODS),
            'cust_id':         f'C{random.randint(1000, 9999)}',
            'discount':        round(random.uniform(0, 0.15), 2),
            'returned':        random.choices([0, 1], weights=[0.95, 0.05])[0],
        })
    return pd.DataFrame(records)


def generate_source_c(n):
    """Wholesale / B2B export."""
    dates = [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364)) for _ in range(n)]
    categories = random.choices(
        list(PRODUCT_CATEGORIES.keys()),
        weights=[v['weight'] for v in PRODUCT_CATEGORIES.values()],
        k=n
    )
    records = []
    for i, (date, cat) in enumerate(zip(dates, categories)):
        price_range = PRODUCT_CATEGORIES[cat]['price_range']
        base_price = round(np.random.uniform(*price_range) * 0.85, 2)  # wholesale discount
        qty = np.random.randint(5, 50)
        mult = seasonal_multiplier(date.month)
        revenue = round(base_price * qty * mult, 2)
        records.append({
            'ref_number':    f'WHL-{30000 + i}',
            'invoice_date':  date.strftime('%Y/%m/%d'),
            'product_name':  random.choice(PRODUCTS[cat]),
            'category':      cat,
            'territory':     random.choice(REGIONS),
            'channel':       'Wholesale',
            'units':         qty,
            'unit_cost':     base_price,
            'gross_revenue': revenue,
            'payment_type':  random.choice(['Bank Transfer', 'Credit Card']),
            'account_id':    f'ACC-{random.randint(100, 999)}',
            'promo_rate':    round(random.uniform(0.05, 0.25), 2),
            'is_returned':   random.choices([0, 1], weights=[0.97, 0.03])[0],
        })
    return pd.DataFrame(records)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    split_a = int(TOTAL_RECORDS * 0.45)
    split_b = int(TOTAL_RECORDS * 0.35)
    split_c = TOTAL_RECORDS - split_a - split_b

    print(f"Generating {split_a} online records...")
    df_a = generate_source_a(split_a)
    df_a.to_csv(os.path.join(OUTPUT_DIR, 'sales_online.csv'), index=False)

    print(f"Generating {split_b} retail records...")
    df_b = generate_source_b(split_b)
    df_b.to_csv(os.path.join(OUTPUT_DIR, 'sales_retail.csv'), index=False)

    print(f"Generating {split_c} wholesale records...")
    df_c = generate_source_c(split_c)
    df_c.to_csv(os.path.join(OUTPUT_DIR, 'sales_wholesale.csv'), index=False)

    print(f"\n✅ Data saved to {OUTPUT_DIR}")
    print(f"   sales_online.csv    → {len(df_a):,} rows")
    print(f"   sales_retail.csv    → {len(df_b):,} rows")
    print(f"   sales_wholesale.csv → {len(df_c):,} rows")


if __name__ == '__main__':
    main()
