import pandas as pd
import numpy as np

def _pct_bins_classifier(pct: float, a_pct: float, b_pct: float) -> str:
    """Return 'A','B','C' based on cumulative percent and thresholds a_pct, b_pct"""
    if pct <= a_pct:
        return "A"
    elif pct <= a_pct + b_pct:
        return "B"
    return "C"

def product_segmentation(df: pd.DataFrame, item_col: str, sales_col: str, revenue_col: str,
                         a_pct: float = 70, b_pct: float = 20) -> pd.DataFrame:
    """
    Product segmentation:
    - Step 1: ABC by Sales quantity (global)
    - Step 2: Within each Sales-ABC group, ABC by Revenue
    - Output: Final class like A-A, A-B, ..., C-C
    """

    # Rename columns for consistency
    dfp = df[[item_col, sales_col, revenue_col]].copy()
    dfp = dfp.rename(columns={item_col: "Item", sales_col: "SalesQty", revenue_col: "Revenue"})

    # Ensure numeric
    dfp["SalesQty"] = pd.to_numeric(dfp["SalesQty"], errors="coerce").fillna(0)
    dfp["Revenue"] = pd.to_numeric(dfp["Revenue"], errors="coerce").fillna(0)

    # Aggregate per item
    items = dfp.groupby("Item", as_index=False).agg({"SalesQty": "sum", "Revenue": "sum"})

    # ---- ABC by Sales (global) ----
    items = items.sort_values("SalesQty", ascending=False).reset_index(drop=True)
    total_sales = items["SalesQty"].sum()
    items["CumulPct_Sales"] = np.where(total_sales > 0,
                                       100.0 * items["SalesQty"].cumsum() / total_sales,
                                       0.0)
    items["ABC_Sales"] = items["CumulPct_Sales"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))

    # ---- Revenue ABC WITHIN each Sales class ----
    items["CumulPct_Revenue_withinSales"] = 0.0
    items["ABC_Revenue_withinSales"] = "C"  # default
    for grp in ["A", "B", "C"]:
        mask = items["ABC_Sales"] == grp
        sub = items.loc[mask].sort_values("Revenue", ascending=False).copy()
        tot_rev = sub["Revenue"].sum()
        if tot_rev > 0 and len(sub) > 0:
            sub["CumulPct_Revenue_withinSales"] = 100.0 * sub["Revenue"].cumsum() / tot_rev
            sub["ABC_Revenue_withinSales"] = sub["CumulPct_Revenue_withinSales"].apply(
                lambda p: _pct_bins_classifier(p, a_pct, b_pct)
            )
        else:
            sub["CumulPct_Revenue_withinSales"] = 0.0
            sub["ABC_Revenue_withinSales"] = "C"
        items.loc[sub.index, "CumulPct_Revenue_withinSales"] = sub["CumulPct_Revenue_withinSales"]
        items.loc[sub.index, "ABC_Revenue_withinSales"] = sub["ABC_Revenue_withinSales"]

    # Final class
    items["Final_Class"] = items["ABC_Sales"] + "-" + items["ABC_Revenue_withinSales"]

    return items

# Example usage:
if __name__ == "__main__":
    data = {
        "Item": ["A", "B", "C", "D", "E", "F"],
        "SalesQty": [500, 400, 300, 200, 100, 50],
        "Revenue": [10000, 8000, 6000, 4000, 2000, 1000],
    }
    df = pd.DataFrame(data)
    result = product_segmentation(df, "Item", "SalesQty", "Revenue", a_pct=70, b_pct=20)
    print(result)
