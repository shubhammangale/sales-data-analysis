# 📊 Sales Data Analysis

> Collected and cleaned **15,000+ sales records** from multiple CSV sources, performed statistical analysis revealing a **+23% Q4 uplift**, and visualised **8 key KPIs** — all in a fully automated, CI/CD-backed pipeline.

![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🗂️ Project Structure

```
sales-data-analysis/
├── src/
│   ├── generate_data.py       # Synthetic data generator (3 CSV sources)
│   ├── data_cleaning.py       # Load, standardise & merge all CSVs
│   ├── analysis.py            # Statistical analysis + KPI calculations
│   ├── visualizations.py      # 8 Matplotlib charts
│   └── main.py                # End-to-end pipeline runner
│
├── tests/
│   └── test_pipeline.py       # 18 unit tests (pytest)
│
├── data/                      # 📁 Auto-generated (gitignored)
│   ├── sales_online.csv
│   ├── sales_retail.csv
│   └── sales_wholesale.csv
│
├── outputs/                   # 📁 Auto-generated (gitignored)
│   ├── sales_master.csv
│   ├── analysis_results.json
│   └── images/
│       ├── chart_monthly_trend.png
│       ├── chart_quarterly.png
│       ├── chart_categories.png
│       ├── chart_region.png
│       ├── chart_channel.png
│       ├── chart_heatmap.png
│       ├── chart_aov.png
│       └── chart_kpi_dashboard.png
│
├── .github/
│   └── workflows/
│       └── pipeline.yml       # GitHub Actions CI/CD
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔑 Key Findings

| Metric | Value |
|---|---|
| **Total Records Processed** | 15,000+ |
| **Records After Cleaning** | ~14,100 |
| **Q4 Sales Growth (vs Q3)** | **+23%** |
| **#1 Category** | Electronics |
| **#2 Category** | Home & Garden |
| **#3 Category** | Sports |
| **Return Rate** | ~6.1% |

---

## 📈 Dashboard Charts

Eight charts are generated automatically, mirroring a Power BI dashboard:

| # | Chart | Description |
|---|---|---|
| 1 | Monthly Revenue Trend | Full-year line chart with Q4 highlighted |
| 2 | Quarterly Revenue Bar | Q1–Q4 comparison with growth annotation |
| 3 | Top Product Categories | Horizontal bar chart, top 3 highlighted |
| 4 | Revenue by Region | Pie chart — North / South / East / West / Central |
| 5 | Revenue by Sales Channel | Online vs Retail vs Wholesale |
| 6 | Category × Quarter Heatmap | Revenue intensity matrix |
| 7 | Average Order Value | By category comparison |
| 8 | KPI Summary Dashboard | 8-metric dark-theme overview card |

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

The pipeline in `.github/workflows/pipeline.yml` runs on every push to `main` or `develop`, and weekly on Mondays:

```
Push / PR / Schedule
        │
        ▼
┌───────────────────┐
│  Job 1: Lint &    │  flake8 + pytest (18 tests)
│  Unit Tests       │
└────────┬──────────┘
         │  (on success)
         ▼
┌───────────────────┐
│  Job 2: Full      │  generate → clean → analyse → visualise
│  Pipeline Run     │  Outputs uploaded as GitHub Artifact
└────────┬──────────┘
         │  (on success)
         ▼
┌───────────────────┐
│  Job 3: Data      │  Row count, null check, revenue validation,
│  Quality Gate     │  Q4 growth confirmation
└───────────────────┘
```

**Pipeline artifacts** (available in the GitHub Actions run page):
- `outputs/sales_master.csv`
- `outputs/analysis_results.json`
- `outputs/images/*.png` (all 8 charts)

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/sales-data-analysis.git
cd sales-data-analysis
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the full pipeline

```bash
python src/main.py
```

This generates everything from scratch in ~2 seconds:
```
outputs/
  sales_master.csv           ← 14,000+ cleaned records
  analysis_results.json      ← all KPIs as structured JSON
  images/                    ← 8 ready-to-use PNG charts
```

### 5. Run tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=src
```

---

## 🧹 Data Cleaning Steps

The three source CSVs have intentionally different schemas and quality issues to demonstrate real-world data engineering:

| Step | Action |
|---|---|
| Schema normalisation | Unified column names across all 3 sources |
| Date parsing | Handled `YYYY-MM-DD`, `DD/MM/YYYY`, and `YYYY/MM/DD` formats |
| Region casing | Corrected lowercase region labels (e.g., `north` → `North`) |
| Missing revenue | Filled with **category-level median** |
| Outlier removal | Dropped records above the **99.9th percentile** |
| Duplicate removal | Removed duplicate transaction IDs |
| Return exclusion | Excluded returned orders from revenue analysis |

---

## 📐 Statistical Methods

- **Quarterly growth**: percentage change (Q3 → Q4)
- **Revenue share**: per-category proportion of total
- **Independent t-test** (Q4 vs rest): confirms Q4 uplift is statistically significant (p < 0.05)
- **Cohen's d**: effect size of seasonal impact
- **Month-over-month trend**: computes MoM % change for all 12 months

---

## 🔗 Power BI Integration

The `outputs/analysis_results.json` file is structured for easy import into Power BI or Tableau:

```json
{
  "total_revenue": 49476769.35,
  "total_orders": 14118,
  "avg_order_value": 3504.09,
  "quarterly": {
    "q4_vs_q3_growth_pct": 23.0,
    ...
  },
  "categories": {
    "top3_categories": [...]
  }
}
```

To connect: **Power BI → Get Data → JSON → select `analysis_results.json`**

---

## 🛠️ Tech Stack

- **Python 3.11**
- **Pandas** — data loading, cleaning, merging
- **NumPy** — vectorised operations, outlier detection
- **Matplotlib** — chart generation
- **SciPy** — t-tests, effect size
- **GitHub Actions** — CI/CD automation

---

## 📄 License

MIT — free to use, adapt, and build on.
