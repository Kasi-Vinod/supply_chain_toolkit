# product_segmentation_app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepInFrame
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ----------------------- Core Logic -----------------------
def _pct_bins_classifier(pct: float, a_pct: float, b_pct: float) -> str:
    if pct <= a_pct:
        return "A"
    elif pct <= a_pct + b_pct:
        return "B"
    return "C"

def product_segmentation(
    df: pd.DataFrame,
    item_col: str,
    sales_col: str,
    revenue_col: str,
    a_pct: float = 70,
    b_pct: float = 20,
) -> pd.DataFrame:
    dfp = df[[item_col, sales_col, revenue_col]].copy()
    dfp = dfp.rename(
        columns={item_col: "Item", sales_col: "SalesQty", revenue_col: "Revenue"}
    )

    dfp["SalesQty"] = pd.to_numeric(dfp["SalesQty"], errors="coerce").fillna(0)
    dfp["Revenue"] = pd.to_numeric(dfp["Revenue"], errors="coerce").fillna(0)

    items = dfp.groupby("Item", as_index=False).agg({"SalesQty": "sum", "Revenue": "sum"})
    items = items.sort_values("SalesQty", ascending=False).reset_index(drop=True)

    total_sales = items["SalesQty"].sum()
    items["CumulPct_Sales"] = np.where(
        total_sales > 0, 100.0 * items["SalesQty"].cumsum() / total_sales, 0.0
    )
    items["ABC_Sales"] = items["CumulPct_Sales"].apply(
        lambda p: _pct_bins_classifier(p, a_pct, b_pct)
    )

    items["CumulPct_Revenue_withinSales"] = 0.0
    items["ABC_Revenue_withinSales"] = "C"
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

    items["Final_Class"] = items["ABC_Sales"] + "-" + items["ABC_Revenue_withinSales"]
    return items

# ----------------------- PDF Builder -----------------------
def fmt_int(x):
    try:
        return f"{int(round(float(x))):,}"
    except Exception:
        return str(x)

def build_inputs_block(styles, a_pct, b_pct, count_items, cell_width):
    # C cutoff is implied as 100 - A - B
    c_pct = max(0, 100 - a_pct - b_pct)

    title = Paragraph("Inputs Used", styles["Heading3"])
    data = [
        ["A% cutoff", f"{a_pct}%"],
        ["B% cutoff", f"{b_pct}%"],
        ["C% cutoff", f"{c_pct}%"],
        ["Total Items", f"{count_items}"],
    ]
    t = Table(data, colWidths=[cell_width * 0.55, cell_width * 0.45])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    return KeepInFrame(cell_width, 9999, [title, Spacer(1, 6), t], mode="shrink")

def build_sales_block(styles, total_sales, a_sales, b_sales, c_sales, cell_width):
    title = Paragraph("Sales Summary", styles["Heading3"])
    data = [
        ["Total Sales", fmt_int(total_sales)],
        ["A Sales", fmt_int(a_sales)],
        ["B Sales", fmt_int(b_sales)],
        ["C Sales", fmt_int(c_sales)],
    ]
    t = Table(data, colWidths=[cell_width * 0.55, cell_width * 0.45])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        # make the first row a little more prominent
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9edf7")),
    ]))
    return KeepInFrame(cell_width, 9999, [title, Spacer(1, 6), t], mode="shrink")

def build_revenue_block(styles, total_rev, rev_map, cell_width):
    title = Paragraph("Revenue Summary", styles["Heading3"])

    # Arrange as 3 pair-columns (label,value | label,value | label,value)
    # Header row with "Total Revenue" label spanning 4 cells, value spanning 2 cells (no empties).
    header = [["Total Revenue", fmt_int(total_rev), "", "", "", ""]]

    # rows
    order_grid = [
        ("A-A", "A-B", "A-C"),
        ("B-A", "B-B", "B-C"),
        ("C-A", "C-B", "C-C"),
    ]
    rows = []
    for triple in order_grid:
        r = []
        for cls in triple:
            r.extend([cls, fmt_int(rev_map.get(cls, 0))])
        rows.append(r)

    data = header + rows
    t = Table(data, colWidths=[cell_width/6.0]*6)
    t_style = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9edf7")),
        # span the label across first 4 header cells, value across last 2 header cells
        ("SPAN", (0, 0), (3, 0)),
        ("SPAN", (4, 0), (5, 0)),
    ])
    t.setStyle(t_style)

    return KeepInFrame(cell_width, 9999, [title, Spacer(1, 6), t], mode="shrink")

def create_picture_style_pdf(result_df: pd.DataFrame, a_pct: int, b_pct: int) -> BytesIO:
    """
    Build ONE concise A4 page with three side-by-side blocks,
    perfectly aligned to margins and with equal widths — matching the photo layout.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36,  # nice printable area
    )

    styles = getSampleStyleSheet()
    # Slightly tighter heading for compact layout
    styles.add(ParagraphStyle(name="Heading3", parent=styles["Heading3"], spaceAfter=4, spaceBefore=0))

    # Metrics
    total_sales = float(result_df["SalesQty"].sum())
    sales_split = result_df.groupby("ABC_Sales")["SalesQty"].sum().reindex(["A", "B", "C"]).fillna(0.0)
    a_sales = float(sales_split["A"])
    b_sales = float(sales_split["B"])
    c_sales = float(sales_split["C"])

    total_rev = float(result_df["Revenue"].sum())
    rev_split = (
        result_df.groupby("Final_Class")["Revenue"]
        .sum()
        .reindex(["A-A", "A-B", "A-C", "B-A", "B-B", "B-C", "C-A", "C-B", "C-C"])
        .fillna(0.0)
        .to_dict()
    )

    # Three equal blocks across content width
    content_width = doc.width  # == A4 width - margins
    col_width = content_width / 3.0

    # Build each block (as KeepInFrame flowables)
    left_block  = build_inputs_block(styles, a_pct, b_pct, len(result_df), col_width)
    middle_block = build_revenue_block(styles, total_rev, rev_split, col_width)
    right_block = build_sales_block(styles, total_sales, a_sales, b_sales, c_sales, col_width)

    # Title
    today = datetime.today().strftime("%Y-%m-%d")
    title = Paragraph(f"ABC Segmentation — Summary (as per provided layout) — {today}", styles["Title"])
    subtitle = Paragraph("Generated by Segmentation Toolkit | Confidential", styles["Normal"])
    story = [title, subtitle, Spacer(1, 16)]

    # Parent 3-column table to align borders and equalize widths/heights
    parent = Table(
        [[left_block, middle_block, right_block]],
        colWidths=[col_width, col_width, col_width],
    )
    parent.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # no outer grid: the blocks themselves have their own grids
    ]))

    story.append(parent)
    # Done — single concise page
    doc.build(story)
    buf.seek(0)
    return buf

# ----------------------- Streamlit UI -----------------------
st.set_page_config(page_title="Product Segmentation (ABC Analysis)", page_icon="📦", layout="wide")
st.title("📦 Product Segmentation — ABC Analysis with Subcategories")

st.markdown(
    """
    Upload an Excel file with **Item**, **SalesQty**, **Revenue** columns.
    The PDF will match your requested layout: three aligned blocks (Inputs • Revenue • Sales) on **one A4 page**.
    """
)

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    st.sidebar.header("Parameters")
    item_col = st.sidebar.selectbox("Item Column", df.columns, index=0)
    sales_col = st.sidebar.selectbox("Sales Quantity Column", df.columns, index=1)
    revenue_col = st.sidebar.selectbox("Revenue Column", df.columns, index=2)
    a_pct = st.sidebar.slider("A % cutoff", 10, 90, 70, 1)
    b_pct = st.sidebar.slider("B % cutoff", 5, 40, 20, 1)

    if st.button("Run Product Segmentation"):
        result = product_segmentation(df, item_col, sales_col, revenue_col, a_pct, b_pct)

        st.subheader("Segmentation Result (first 20 rows)")
        st.dataframe(result.head(20))

        # Light UI charts (kept in app, not in PDF)
        figs = []
        fig1, ax1 = plt.subplots()
        result["Final_Class"].value_counts().reindex(
            ["A-A", "A-B", "A-C", "B-A", "B-B", "B-C", "C-A", "C-B", "C-C"]
        ).fillna(0).plot(kind="bar", ax=ax1, rot=0, title="Final Class Distribution")
        st.pyplot(fig1); figs.append(fig1)

        # Build the one-page PDF exactly like the picture layout
        pdf_buf = create_picture_style_pdf(result, a_pct, b_pct)
        st.download_button(
            "📑 Download PDF (One-Page Summary)",
            data=pdf_buf,
            file_name="ABC_Segmentation_Summary.pdf",
            mime="application/pdf",
        )
else:
    st.info("📥 Please upload an Excel file to proceed.")
