<div align="center">

# 📊 Sales Analyzer

### A menu-driven terminal app that turns raw sales records into instant insights

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?logo=numpy&logoColor=white)
![Requests](https://img.shields.io/badge/requests-HTTP-2E7D32)
![Interface](https://img.shields.io/badge/interface-CLI-black)

*Press a number. Get an answer. No commands to memorise.*

</div>

---

## ✨ What is this?

**Sales Analyzer** downloads dummy sales records from a public API, loads them into a
**pandas** DataFrame, crunches the numbers with **NumPy**, and lets you explore everything
from a simple numbered menu in your terminal.

Want the highest sale? Press `1`. The worst month? Press `4`. A full breakdown of March?
Press `6`, type `March`, done.

## 🚀 Features

| Key | What you get |
|:---:|---|
| `1` | 🏆 **Highest single sale**, with product, date, region and customer |
| `2` | 📉 **Lowest single sale** |
| `3` | 📈 **Best month** by total revenue |
| `4` | 🥀 **Worst month** by total revenue |
| `5` | 🗓️ **Full monthly report**: total, count, average, highest, lowest for all 12 months |
| `6` | 🔍 **Month lookup**: type a month (`3` or `March`) to see its total, highest and lowest sale |
| `7` | 🛍️ **Top 5 products** by revenue |
| `8` | 🌍 **Sales by region** with a bar chart |
| `9` | 🧮 **Statistics summary**: mean, median, std deviation, percentiles, correlation (NumPy) |
| `10` | 📅 **Sales by weekday** with the strongest day highlighted |
| `11` | 💾 **Export** the monthly report to `monthly_report.csv` |
| `12` | 🔄 **Refresh** the data from the API |
| `0` | 👋 **Exit** |

Extras: colored output (automatically disabled when piping), friendly error handling for
invalid input, and an **offline fallback** so the app still works without internet.

## 🖥️ Preview

```text
============================================================
                       SALES ANALYZER
============================================================
  [ 1]  Highest single sale
  [ 2]  Lowest single sale
  [ 3]  Best month (total revenue)
  [ 4]  Worst month (total revenue)
  [ 5]  Full monthly report
  [ 6]  Look up one month (max / min / total)
  [ 7]  Top 5 products
  [ 8]  Sales by region
  [ 9]  Statistics summary
  [10]  Sales by weekday
  [11]  Export monthly report to CSV
  [12]  Refresh data from API
  [ 0]  Exit

Press a number and hit Enter: 1

============================================================
                    HIGHEST SINGLE SALE
============================================================
  Product  : Monitor
  Amount   : $4,648.43
  Quantity : 10
  Date     : 25 Dec 2025 (Thursday)
  Region   : East
  Order ID : 926   Customer ID: 90
```

<details>
<summary><b>More sample screens (click to expand)</b></summary>

**Sales by region (`8`)**

```text
  North     $504,655.57  ##############################
  South     $465,792.56  ###########################
  East      $431,619.03  #########################
  West      $426,302.34  #########################
```

**Statistics summary (`9`)**

```text
  Records            : 1,500
  Total revenue      : $1,828,369.50
  Mean sale          : $1,218.91
  Median sale        : $924.67
  Std deviation      : $1,020.42
  25th / 75th pct    : $386.88 / $1,797.56
  90th percentile    : $2,747.89
  Quantity vs sales  : correlation 0.62
```

> Numbers above come from the offline dummy data and will differ when the API is used.

</details>

## 📦 Project structure

```text
sales-analyzer/
├── sales_analyzer.py    # the whole application
├── requirements.txt     # numpy, pandas, requests
└── README.md            # you are here
```

## ⚙️ Installation

**1. Clone or download** the project and open a terminal inside the folder.

**2. (Recommended) create a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

## ▶️ Usage

```bash
python sales_analyzer.py
```

Then just type a number from the menu and press **Enter**. After each result, press
**Enter** again to return to the menu.

## 🧠 How it works

```text
 DummyJSON API ──► requests ──► pandas DataFrame ──► NumPy / pandas analysis ──► terminal menu
        │                                ▲
        └── (offline?) ── NumPy-generated dummy data ──┘
```

1. **Fetch**: `requests` calls `https://dummyjson.com/carts?limit=0`, which returns shopping
   carts with products, quantities, prices and discounts.
2. **Flatten**: every product line in every cart becomes one **sale record**
   (`sales` = discounted total of that line).
3. **Enrich**: the API does not provide dates or regions, so the app adds a random-but-reproducible
   **date** (year 2025) and **region** (North / South / East / West) to each order using a fixed
   NumPy seed. Results are therefore identical on every run.
4. **Analyse**: pandas handles grouping and aggregation (`groupby`, `agg`, `reindex`), while NumPy
   handles statistics (`mean`, `median`, `std`, `percentile`, `corrcoef`).
5. **Present**: a simple `while` loop shows the menu and dispatches to the matching function.

### 🛟 Offline fallback

If the API is unreachable (no internet, firewall, timeout), the app prints a notice and generates
1,500 realistic dummy sales with NumPy instead, so every menu option keeps working.

## 🧩 Tech stack

- **Python 3.9+**
- **pandas** for tabular data and aggregation
- **NumPy** for numerical statistics
- **requests** for the API call

## 🛠️ Customise it

| I want to… | Change this |
|---|---|
| Use a different year | `YEAR` at the top of `sales_analyzer.py` |
| Change the regions | `REGIONS` list |
| Generate more offline data | `generate_offline_data(n=1500)` |
| Add a new menu option | Write a function taking `df`, then add a `("13", "Label", function)` line to `MENU` |
| Point at another API | Edit `API_URL` and adjust `fetch_from_api()` |

## 🗺️ Ideas for next steps

- 📊 Plot charts with matplotlib
- 🔎 Filter by region or product
- 📆 Year-over-year comparison
- 🧪 Unit tests with pytest

## 📄 License

Free to use for learning and personal projects.

<div align="center">

Made with 🐍 Python, pandas and NumPy

</div>
