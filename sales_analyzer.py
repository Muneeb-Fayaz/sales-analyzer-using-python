#!/usr/bin/env python3
"""
Sales Analyzer - a menu driven terminal app.

Fetches dummy sales records from a public API (DummyJSON), analyses them with
pandas + NumPy and lets you explore the results by pressing a single number.
If the API cannot be reached, it falls back to locally generated dummy data so
the app always works.
"""

import calendar
import sys

import numpy as np
import pandas as pd
import requests

API_URL = "https://dummyjson.com/carts?limit=0"
SEED = 42  # keeps the generated dates/regions the same on every run
REGIONS = ["North", "South", "East", "West"]
YEAR = 2025

USE_COLOR = sys.stdout.isatty()


# --------------------------------------------------------------------------- #
# Small display helpers
# --------------------------------------------------------------------------- #
def paint(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else str(text)


def money(value):
    return f"${value:,.2f}"


def title(text):
    line = "=" * 60
    print(f"\n{paint(line, '36')}\n{paint(text.center(60), '1;36')}\n{paint(line, '36')}")


def month_label(number):
    return calendar.month_name[int(number)]


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def fetch_from_api():
    """Download carts from the dummy API and flatten them to one row per sale."""
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    carts = response.json()["carts"]

    rows = []
    for cart in carts:
        for item in cart["products"]:
            rows.append(
                {
                    "order_id": cart["id"],
                    "user_id": cart["userId"],
                    "product": item["title"],
                    "quantity": item["quantity"],
                    "unit_price": item["price"],
                    "sales": item["discountedTotal"],
                }
            )
    df = pd.DataFrame(rows)

    # The API has no dates / regions, so we add them (reproducibly) per order.
    rng = np.random.default_rng(SEED)
    order_ids = df["order_id"].unique()
    dates = pd.Timestamp(YEAR, 1, 1) + pd.to_timedelta(
        rng.integers(0, 365, len(order_ids)), unit="D"
    )
    regions = rng.choice(REGIONS, len(order_ids))
    lookup = pd.DataFrame({"order_id": order_ids, "date": dates, "region": regions})
    return df.merge(lookup, on="order_id")


def generate_offline_data(n=1500):
    """Fallback: build dummy sales entirely with NumPy."""
    rng = np.random.default_rng(SEED)
    products = ["Laptop", "Phone", "Headphones", "Keyboard", "Monitor",
                "Mouse", "Tablet", "Camera", "Speaker", "Smartwatch"]
    quantity = rng.integers(1, 11, n)
    unit_price = rng.uniform(5, 500, n).round(2)
    discount = rng.uniform(0, 0.25, n)
    return pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1),
            "user_id": rng.integers(1, 200, n),
            "product": rng.choice(products, n),
            "quantity": quantity,
            "unit_price": unit_price,
            "sales": (quantity * unit_price * (1 - discount)).round(2),
            "date": pd.Timestamp(YEAR, 1, 1)
            + pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
            "region": rng.choice(REGIONS, n),
        }
    )


def load_data():
    print("Fetching sales data from the API ...")
    try:
        df = fetch_from_api()
        source = "DummyJSON API"
    except (requests.RequestException, KeyError, ValueError) as err:
        print(paint(f"  Could not use the API ({err.__class__.__name__}). "
                    "Using offline dummy data instead.", "33"))
        df = generate_offline_data()
        source = "offline generator"

    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.day_name()
    print(paint(f"  Loaded {len(df):,} sales records from {source}.", "32"))
    return df


# --------------------------------------------------------------------------- #
# Analysis helpers
# --------------------------------------------------------------------------- #
def monthly_report(df):
    report = (
        df.groupby("month")["sales"]
        .agg(total="sum", orders="count", average="mean", highest="max", lowest="min")
        .reindex(range(1, 13))
        .fillna(0)
    )
    report.insert(0, "month_name", [month_label(m) for m in report.index])
    return report


def print_record(row):
    print(f"  Product  : {row['product']}")
    print(f"  Amount   : {paint(money(row['sales']), '1;32')}")
    print(f"  Quantity : {row['quantity']}")
    print(f"  Date     : {row['date']:%d %b %Y} ({row['weekday']})")
    print(f"  Region   : {row['region']}")
    print(f"  Order ID : {row['order_id']}   Customer ID: {row['user_id']}")


def ask_month():
    text = input("Enter a month (1-12 or name, e.g. 3 or March): ").strip().lower()
    if text.isdigit() and 1 <= int(text) <= 12:
        return int(text)
    if len(text) >= 3:
        for number in range(1, 13):
            if calendar.month_name[number].lower().startswith(text[:3]):
                return number
    print(paint("  That is not a valid month.", "31"))
    return None


# --------------------------------------------------------------------------- #
# Menu actions
# --------------------------------------------------------------------------- #
def highest_sale(df):
    title("HIGHEST SINGLE SALE")
    print_record(df.loc[df["sales"].idxmax()])


def lowest_sale(df):
    title("LOWEST SINGLE SALE")
    print_record(df.loc[df["sales"].idxmin()])


def best_month(df):
    title("BEST MONTH (by total revenue)")
    report = monthly_report(df)
    m = report["total"].idxmax()
    print(f"  {report.loc[m, 'month_name']} earned {paint(money(report.loc[m, 'total']), '1;32')} "
          f"from {int(report.loc[m, 'orders'])} sales.")


def worst_month(df):
    title("WORST MONTH (by total revenue)")
    report = monthly_report(df)
    m = report["total"].idxmin()
    print(f"  {report.loc[m, 'month_name']} earned {paint(money(report.loc[m, 'total']), '1;31')} "
          f"from {int(report.loc[m, 'orders'])} sales.")


def full_monthly_report(df):
    title("MONTHLY SALES REPORT")
    report = monthly_report(df)
    view = report.copy()
    for col in ["total", "average", "highest", "lowest"]:
        view[col] = view[col].map(money)
    view["orders"] = view["orders"].astype(int)
    view.index.name = "#"
    print(view.to_string())
    print(f"\n  Year total: {paint(money(report['total'].sum()), '1;32')}")


def month_lookup(df):
    month = ask_month()
    if month is None:
        return
    subset = df[df["month"] == month]
    title(f"{month_label(month).upper()} SNAPSHOT")
    if subset.empty:
        print("  No sales recorded in this month.")
        return
    print(f"  Total revenue : {money(subset['sales'].sum())}")
    print(f"  Sales count   : {len(subset)}")
    print(f"  Average sale  : {money(subset['sales'].mean())}")
    print(paint("\n  Highest sale of the month:", "1"))
    print_record(subset.loc[subset["sales"].idxmax()])
    print(paint("\n  Lowest sale of the month:", "1"))
    print_record(subset.loc[subset["sales"].idxmin()])


def top_products(df):
    title("TOP 5 PRODUCTS BY REVENUE")
    top = (df.groupby("product")
             .agg(revenue=("sales", "sum"), units=("quantity", "sum"))
             .sort_values("revenue", ascending=False)
             .head(5))
    top["revenue"] = top["revenue"].map(money)
    print(top.to_string())


def sales_by_region(df):
    title("SALES BY REGION")
    by_region = df.groupby("region")["sales"].sum().sort_values(ascending=False)
    biggest = by_region.max()
    for region, value in by_region.items():
        bar = "#" * int(30 * value / biggest)
        print(f"  {region:<6} {money(value):>14}  {paint(bar, '35')}")


def statistics(df):
    title("STATISTICS SUMMARY (NumPy)")
    s = df["sales"].to_numpy()
    p25, p50, p75, p90 = np.percentile(s, [25, 50, 75, 90])
    corr = np.corrcoef(df["quantity"].to_numpy(), s)[0, 1]
    print(f"  Records            : {s.size:,}")
    print(f"  Total revenue      : {money(s.sum())}")
    print(f"  Mean sale          : {money(np.mean(s))}")
    print(f"  Median sale        : {money(np.median(s))}")
    print(f"  Std deviation      : {money(np.std(s))}")
    print(f"  25th / 75th pct    : {money(p25)} / {money(p75)}")
    print(f"  90th percentile    : {money(p90)}")
    print(f"  Quantity vs sales  : correlation {corr:.2f}")


def weekday_analysis(df):
    title("SALES BY WEEKDAY")
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day = df.groupby("weekday")["sales"].sum().reindex(order).fillna(0)
    biggest = by_day.max() or 1
    for day, value in by_day.items():
        bar = "#" * int(30 * value / biggest)
        print(f"  {day:<10} {money(value):>14}  {paint(bar, '34')}")
    print(f"\n  Strongest day: {paint(by_day.idxmax(), '1;32')}")


def export_report(df):
    title("EXPORT")
    path = "monthly_report.csv"
    monthly_report(df).to_csv(path, index_label="month")
    print(f"  Monthly report saved to {paint(path, '1;32')}")


# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #
MENU = [
    ("1", "Highest single sale", highest_sale),
    ("2", "Lowest single sale", lowest_sale),
    ("3", "Best month (total revenue)", best_month),
    ("4", "Worst month (total revenue)", worst_month),
    ("5", "Full monthly report", full_monthly_report),
    ("6", "Look up one month (max / min / total)", month_lookup),
    ("7", "Top 5 products", top_products),
    ("8", "Sales by region", sales_by_region),
    ("9", "Statistics summary", statistics),
    ("10", "Sales by weekday", weekday_analysis),
    ("11", "Export monthly report to CSV", export_report),
    ("12", "Refresh data from API", None),
    ("0", "Exit", None),
]


def show_menu():
    title("SALES ANALYZER")
    for key, label, _ in MENU:
        print(f"  [{paint(key.rjust(2), '1;33')}]  {label}")


def main():
    df = load_data()
    actions = {key: func for key, _, func in MENU}

    while True:
        show_menu()
        try:
            choice = input("\nPress a number and hit Enter: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if choice == "0":
            print("Bye! Happy analysing.")
            break
        if choice == "12":
            df = load_data()
        elif choice in actions and actions[choice]:
            actions[choice](df)
        else:
            print(paint("  Invalid choice, please pick a number from the menu.", "31"))

        try:
            input("\nPress Enter to return to the menu ...")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()
