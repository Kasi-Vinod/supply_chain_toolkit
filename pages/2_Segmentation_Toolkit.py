# product_segmentation_app.py
import streamlit as st
import pandas as pd
import numpy as np

# ---------- Helper ----------
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
    items["CumulPct_Sales"] = np.where(
        total_sales > 0,
        100.0 * items["SalesQty"].cumsum() / total_sales,
        0.0
    )
    items["ABC_Sales"] = items["CumulPct_Sales"].apply(
        lambda p: _pct_bins_classifier(p, a_pct, b_pct)
    )

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

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Product Segmentation (ABC Analysis)", page_icon="📦", layout="wide")
st.title("📦 Product Segmentation — ABC Analysis with Subcategories")

st.markdown(
    """
    Upload an Excel file containing **Item, SalesQty, and Revenue** columns.
    The app will:
    1. Perform ABC analysis on Sales Quantity.
    2. Segment each Sales class (A/B/C) further into sub-groups based on Revenue.
    3. Produce final categories like `A-A`, `A-B`, `B-C`, etc.
    """
)

# Upload file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Could not read Excel file: {e}")
        st.stop()

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    # Column mapping
    st.sidebar.header("Column Mapping")
    item_col = st.sidebar.selectbox("Item Column", options=df.columns, index=0)
    sales_col = st.sidebar.selectbox("Sales Quantity Column", options=df.columns, index=1)
    revenue_col = st.sidebar.selectbox("Revenue Column", options=df.columns, index=2)

    # Parameters
    st.sidebar.header("Parameters")
    a_pct = st.sidebar.slider("A % cutoff", min_value=10, max_value=90, value=70, step=1)
    b_pct = st.sidebar.slider("B % cutoff", min_value=5, max_value=40, value=20, step=1)

    if st.button("Run Product Segmentation"):
        result = product_segmentation(df, item_col, sales_col, revenue_col, a_pct, b_pct)

        st.subheader("Segmentation Result")
        st.dataframe(result)

        # Download segmented data
        @st.cache_data
        def convert_df_to_excel(df):
            return df.to_excel(index=False, engine="xlsxwriter")

        st.download_button(
            label="⬇️ Download Result (Excel)",
            data=result.to_csv(index=False).encode("utf-8"),
            file_name="product_segmentation.csv",
            mime="text/csv",
        )

else:
    st.info("📥 Please upload an Excel file to proceed.")
