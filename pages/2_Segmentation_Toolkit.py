# product_segmentation_app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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

# ---------- PDF Generation ----------
def create_picture_style_pdf(result_df, a_pct, b_pct):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    # Use custom heading style to avoid KeyError
    if "CustomHeading3" not in styles:
        styles.add(ParagraphStyle(name="CustomHeading3",
                                  parent=styles["Heading3"],
                                  spaceAfter=6,
                                  spaceBefore=6))

    # --- Sales Summary ---
    total_sales = result_df["SalesQty"].sum()
    sales_split = result_df.groupby("ABC_Sales")["SalesQty"].sum().to_dict()
    sales_data = [
        ["Total Sales", f"{total_sales:,.0f}", "A Sales", f"{sales_split.get('A',0):,.0f}"],
        ["B Sales", f"{sales_split.get('B',0):,.0f}", "C Sales", f"{sales_split.get('C',0):,.0f}"]
    ]
    elements.append(Paragraph("Sales Summary", styles["CustomHeading3"]))
    sales_table = Table(sales_data, colWidths=[100, 100, 100, 100])
    sales_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("ALIGN", (0,0), (-1,-1), "CENTER")
    ]))
    elements.append(sales_table)
    elements.append(Spacer(1,12))

    # --- Revenue Summary ---
    total_rev = result_df["Revenue"].sum()
    rev_split = result_df.groupby("Final_Class")["Revenue"].sum().to_dict()
    rev_rows = [["Total Revenue", f"{total_rev:,.0f}"]]
    subcats = sorted(rev_split.keys())
    for i in range(0, len(subcats), 2):
        row = []
        for j in range(2):
            if i+j < len(subcats):
                sc = subcats[i+j]
                row += [sc, f"{rev_split[sc]:,.0f}"]
        rev_rows.append(row)
    elements.append(Paragraph("Revenue Summary", styles["CustomHeading3"]))
    rev_table = Table(rev_rows, colWidths=[80,100,80,100])
    rev_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("ALIGN", (0,0), (-1,-1), "CENTER")
    ]))
    elements.append(rev_table)
    elements.append(Spacer(1,12))

    # --- Inputs Used ---
    inputs_data = [
        ["A % Cutoff", f"{a_pct}%", "B % Cutoff", f"{b_pct}%", "Total Items", f"{len(result_df):,.0f}"]
    ]
    elements.append(Paragraph("Inputs Used", styles["CustomHeading3"]))
    inputs_table = Table(inputs_data, colWidths=[80,80,80,80,80,80])
    inputs_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
        ("ALIGN", (0,0), (-1,-1), "CENTER")
    ]))
    elements.append(inputs_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Product Segmentation (ABC Analysis)", page_icon="📦", layout="wide")
st.title("📦 Product Segmentation — ABC Analysis with Subcategories")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.dataframe(df.head())

    item_col = st.sidebar.selectbox("Item Column", options=df.columns, index=0)
    sales_col = st.sidebar.selectbox("Sales Quantity Column", options=df.columns, index=1)
    revenue_col = st.sidebar.selectbox("Revenue Column", options=df.columns, index=2)

    a_pct = st.sidebar.slider("A % cutoff", min_value=10, max_value=90, value=70, step=1)
    b_pct = st.sidebar.slider("B % cutoff", min_value=5, max_value=40, value=20, step=1)

    if st.button("Run Product Segmentation"):
        result = product_segmentation(df, item_col, sales_col, revenue_col, a_pct, b_pct)
        st.subheader("Segmentation Result")
        st.dataframe(result)

        # PDF download
        pdf_buf = create_picture_style_pdf(result, a_pct, b_pct)
        st.download_button(
            "⬇️ Download PDF Report",
            data=pdf_buf,
            file_name="abc_segmentation_report.pdf",
            mime="application/pdf"
        )
else:
    st.info("📥 Please upload an Excel file to proceed.")
