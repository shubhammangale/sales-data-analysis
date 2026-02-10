"""
main.py
End-to-end pipeline runner:
  1. Generate synthetic data (15,000+ records across 3 CSV sources)
  2. Clean & merge all sources
  3. Run statistical analysis
  4. Generate all 8 visualizations
"""

import sys, os, time

sys.path.insert(0, os.path.dirname(__file__))

from generate_data   import main as generate
from data_cleaning   import run  as clean
from analysis        import run  as analyse
from visualizations  import run  as visualise


def separator(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)


def main():
    start = time.time()

    separator("STEP 1/4 – Generating Sample Data")
    generate()

    separator("STEP 2/4 – Cleaning & Merging CSVs")
    clean()

    separator("STEP 3/4 – Statistical Analysis")
    analyse()

    separator("STEP 4/4 – Generating Visualizations")
    visualise()

    elapsed = time.time() - start
    separator(f"✅ Pipeline Complete ({elapsed:.1f}s)")
    print("  Outputs:")
    print("    outputs/sales_master.csv        ← cleaned dataset")
    print("    outputs/analysis_results.json   ← KPI metrics")
    print("    outputs/images/*.png            ← 8 dashboard charts")


if __name__ == '__main__':
    main()
