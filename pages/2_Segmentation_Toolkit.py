# pages/2_Segmentation_Toolkit.py
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Segmentation Toolkit (Single-sheet)", page_icon="📊", layout="wide")

# ---------- Helpers ----------
def _pct_bins_classifier(pct: float, a_pct: float, b_pct: float) -> str:
    """Return 'A','B','C' based on cumulative percent and thresholds a_pct, b_pct"""
    if pct <= a_pct:
        return "A"
    elif pct <= a_pct + b_pct:
        return "B"
    return "C"

def abc_on_column(df: pd.DataFrame, key_col: str, value_col: str, a_pct: float, b_pct: float) -> pd.DataFrame:
    """Compute ABC ranking of unique key_col using sum(value_col). Returns dataframe with cumulative% and ABC class."""
    agg = df.groupby(key_col, as_index=False)[value_col].sum().rename(columns={value_col: "Value"})
    agg = agg.sort_values("Value", ascending=False).reset_index(drop=True)
    total = agg["Value"].sum()
    agg["Cumulative%"] = np.where(total > 0, 100.0 * agg["Value"].cumsum() / total, 0.0)
    agg["ABC"] = agg["Cumulative%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
    return agg

def export_pdf(title, df, figs):
    """Create a simple PDF: title + first 20 rows of df + list of matplotlib figs."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))

    # Data Table (first 20 rows)
    head = df.head(20).copy()
    data = [head.columns.tolist()] + head.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.grey),
                               ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
                               ("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("GRID",(0,0),(-1,-1),0.5,colors.black),
                               ("FONTSIZE",(0,0),(-1,-1),8)]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Plots
    for fig in figs:
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format="png", bbox_inches="tight")
        img_buf.seek(0)
        elements.append(Image(img_buf, width=400, height=250))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buf.seek(0)
    return buf

def df_to_excel_bytes(dfs_dict: dict):
    """Accepts dict of sheet_name->df and returns bytes of an Excel file."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        for name, df in dfs_dict.items():
            # Excel sheet names limited to 31 chars
            df.to_excel(writer, sheet_name=name[:31], index=False)
    buf.seek(0)
    return buf

# ---------------- UI: Title + file upload ----------------
st.title("Segmentation Toolkit — single-sheet input")
st.markdown(
    "Upload one Excel file that contains a single table with all required columns. "
    "Map columns in the sidebar and run Product / Customer / Supplier segmentation."
)

uploaded_file = st.file_uploader("Upload Excel file (single sheet table)", type=["xlsx"], accept_multiple_files=False)

# Sidebar for controls & mapping
st.sidebar.header("Column mapping & params")

if uploaded_file is None:
    st.info("Upload a single-sheet Excel file (one table). After upload, map the columns in the sidebar.")
    st.stop()

# Read uploaded file (first sheet)
try:
    df = pd.read_excel(uploaded_file, sheet_name=0)
except Exception as e:
    st.error(f"Could not read Excel file: {e}")
    st.stop()

if df.empty:
    st.error("Uploaded sheet is empty.")
    st.stop()

sample_cols = df.columns.tolist()

st.sidebar.markdown("**Preview of uploaded table (first 5 rows)**")
st.sidebar.dataframe(df.head())

# Column mapping (allow the user to select which columns correspond to required fields)
st.sidebar.markdown("---")
st.sidebar.subheader("Map your columns (choose the appropriate column names)")

item_col = st.sidebar.selectbox("Item / SKU column (for Product segmentation)", options=["(none)"] + sample_cols, index=(1 if "Item" in sample_cols else 0))
sales_col = st.sidebar.selectbox("Sales quantity column (for Product ABC)", options=["(none)"] + sample_cols, index=(1 if "SalesQty" in sample_cols else 0))
revenue_col = st.sidebar.selectbox("Revenue column (for Product/Totals)", options=["(none)"] + sample_cols, index=(1 if "Revenue" in sample_cols else 0))

customer_col = st.sidebar.selectbox("Customer column (for Customer segmentation)", options=["(none)"] + sample_cols, index=(1 if "Customer" in sample_cols else 0))
# default cust_rev_col to revenue_col if present
default_cust_rev_index = sample_cols.index("Revenue") if "Revenue" in sample_cols else 0
cust_rev_col = st.sidebar.selectbox("Customer revenue column (optional - defaults to Revenue)", options=["(none)"] + sample_cols, index=default_cust_rev_index + 1 if "Revenue" in sample_cols else 0)
cost_col = st.sidebar.selectbox("CostToServe / Cost column (optional, for Profit)", options=["(none)"] + sample_cols, index=0)

supplier_col = st.sidebar.selectbox("Supplier column (for Supplier segmentation)", options=["(none)"] + sample_cols, index=(1 if "Supplier" in sample_cols else 0))
profitimpact_col = st.sidebar.selectbox("ProfitImpact column (for Kraljic)", options=["(none)"] + sample_cols, index=0)
supplyrisk_col = st.sidebar.selectbox("SupplyRisk column (for Kraljic)", options=["(none)"] + sample_cols, index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("ABC thresholds")
a_pct = st.sidebar.slider("A % cutoff (percent)", min_value=10, max_value=90, value=70, step=1)
b_pct = st.sidebar.slider("B % cutoff (percent)", min_value=5, max_value=40, value=20, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("PDF / Excel export options")
include_plots_in_pdf = st.sidebar.checkbox("Include plots in PDF", value=True)

# ---------------- Tile navigation ----------------
if "selected_tile" not in st.session_state:
    st.session_state.selected_tile = "Product"

cols = st.columns(3)
tile_labels = ["Product", "Customer", "Supplier"]
tile_icons = {"Product": "📦", "Customer": "👥", "Supplier": "🤝"}

def render_tile(label, idx):
    selected = (st.session_state.selected_tile == label)
    color = "#4CAF50" if selected else "#f0f0f0"
    text_color = "white" if selected else "black"
    with cols[idx]:
        if st.button(f"{tile_icons[label]} {label}", key=f"tile_{label}", use_container_width=True):
            st.session_state.selected_tile = label
        st.markdown(
            f"""
            <div style='text-align:center;
                        background-color:{color};
                        color:{text_color};
                        padding:10px;
                        border-radius:10px;
                        margin-top:-15px;
                        font-weight:bold;'>{label}</div>
            """,
            unsafe_allow_html=True,
        )

for i, lab in enumerate(tile_labels):
    render_tile(lab, i)

st.markdown("---")

# ---------------- Segmentation logic ----------------
selected = st.session_state.selected_tile

def col_selected(name):
    return name != "(none)"

# --- PRODUCT SEGMENTATION ---
if selected == "Product":
    st.header("Product segmentation")
    st.markdown("ABC by **Sales quantity** + ABC by **Revenue (within each Sales-ABC group)** → combined classes (A-A ... C-C).")

    if not (col_selected(item_col) and col_selected(sales_col) and col_selected(revenue_col)):
        st.warning("Please map Item, Sales quantity and Revenue columns in the sidebar to run Product segmentation.")
    else:
        st.write("Parameters:")
        st.write(f"- A % cutoff = **{a_pct}%**, B % cutoff = **{b_pct}%**")
        if st.button("Run Product segmentation"):
            # Prepare dataframe
            dfp = df[[item_col, sales_col, revenue_col]].copy()
            dfp = dfp.rename(columns={item_col: "Item", sales_col: "SalesQty", revenue_col: "Revenue"})

            # Ensure numeric
            dfp["SalesQty"] = pd.to_numeric(dfp["SalesQty"], errors="coerce").fillna(0)
            dfp["Revenue"] = pd.to_numeric(dfp["Revenue"], errors="coerce").fillna(0)

            # Aggregate per item
            items = dfp.groupby("Item", as_index=False).agg({"SalesQty":"sum","Revenue":"sum"})

            # ---- ABC by Sales (global) ----
            items = items.sort_values("SalesQty", ascending=False).reset_index(drop=True)
            total_sales = items["SalesQty"].sum()
            items["CumulPct_Sales"] = np.where(total_sales>0, 100.0 * items["SalesQty"].cumsum() / total_sales, 0.0)
            items["ABC_Sales"] = items["CumulPct_Sales"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))

            # ---- Revenue ABC WITHIN each Sales class (A/B/C) ----
            items["CumulPct_Revenue_withinSales"] = 0.0
            items["ABC_Revenue_withinSales"] = "C"  # default
            for grp in ["A","B","C"]:
                mask = items["ABC_Sales"] == grp
                sub = items.loc[mask].sort_values("Revenue", ascending=False).copy()
                tot_rev = sub["Revenue"].sum()
                if tot_rev > 0 and len(sub) > 0:
                    sub["CumulPct_Revenue_withinSales"] = 100.0 * sub["Revenue"].cumsum() / tot_rev
                    sub["ABC_Revenue_withinSales"] = sub["CumulPct_Revenue_withinSales"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
                else:
                    sub["CumulPct_Revenue_withinSales"] = 0.0
                    sub["ABC_Revenue_withinSales"] = "C"
                # write back to main
                items.loc[sub.index, "CumulPct_Revenue_withinSales"] = sub["CumulPct_Revenue_withinSales"]
                items.loc[sub.index, "ABC_Revenue_withinSales"] = sub["ABC_Revenue_withinSales"]

            # Final class
            items["Final_Class"] = items["ABC_Sales"] + "-" + items["ABC_Revenue_withinSales"]

            st.subheader("Result (preview)")
            st.dataframe(items.sort_values(["ABC_Sales","ABC_Revenue_withinSales","Revenue"], ascending=[True,True,False]).reset_index(drop=True))

            # Plots
            figs = []
            # Pareto-like: SalesQty cumulative %
 + revenue bars
            fig1, ax1 = plt.subplots(figsize=(9, 3.5))
            top = items.sort_values("Revenue", ascending=False).head(30)
            ax1.bar(range(len(top)), top["Revenue"])
            ax1.set_xticks(range(len(top)))
            ax1.set_xticklabels(top["Item"], rotation=60, ha="right", fontsize=8)
            ax1.set_title("Top items by Revenue (top 30)")
            st.pyplot(fig1); figs.append(fig1)

            # Count of each Final_Class (ensure all 9 combos appear)
            fig2, ax2 = plt.subplots(figsize=(6, 3))
            order = ["A-A","A-B","A-C","B-A","B-B","B-C","C-A","C-B","C-C"]
            counts = items["Final_Class"].value_counts().reindex(order).fillna(0)
            counts.plot(kind="bar", ax=ax2)
            ax2.set_title("Counts by Final Class (SalesABC - RevenueWithinSalesABC)")
            st.pyplot(fig2); figs.append(fig2)

            # Show breakdown table for sanity
            st.markdown("**Breakdown by Sales class**")
            st.dataframe(items.groupby(["ABC_Sales","ABC_Revenue_withinSales"]).size().rename("Count").reset_index())

            # Download Excel
            excel_bytes = df_to_excel_bytes({"Product_Segmentation": items})
            st.download_button("⬇️ Download segmentation (Excel)", data=excel_bytes, file_name="product_segmentation.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # Download PDF (first 20 rows + plots)
            pdf_buf = export_pdf("Product Segmentation", items, figs if include_plots_in_pdf else [])
            st.download_button("⬇️ Download PDF", data=pdf_buf, file_name="product_segmentation.pdf", mime="application/pdf")

# --- CUSTOMER SEGMENTATION ---
elif selected == "Customer":
    st.header("Customer segmentation")
    st.markdown("Per-customer ABC on Revenue (or mapped Customer revenue column). Also shows ProfitMargin if Cost column mapped.")

    if not col_selected(customer_col):
        st.warning("Please map a Customer column in the sidebar to run Customer segmentation.")
    else:
        if not col_selected(cust_rev_col):
            st.warning("Please map a Revenue column for Customer segmentation (customer revenue).")
        else:
            if st.button("Run Customer segmentation"):
                dfc = df[[customer_col, cust_rev_col]].copy().rename(columns={customer_col: "Customer", cust_rev_col: "Revenue"})
                dfc["Revenue"] = pd.to_numeric(dfc["Revenue"], errors="coerce").fillna(0)

                cust_agg = abc_on_column(dfc, "Customer", "Revenue", a_pct, b_pct)
                cust_agg = cust_agg.rename(columns={"Value": "TotalRevenue", "ABC": "ABC_Revenue", "Cumulative%":"CumulPct_Revenue"})

                # ProfitMargin if cost column provided
                figs = []
                if col_selected(cost_col) and cost_col in df.columns:
                    dfc2 = df[[customer_col, cust_rev_col, cost_col]].copy().rename(columns={customer_col: "Customer", cust_rev_col: "Revenue", cost_col: "Cost"})
                    dfc2["Revenue"] = pd.to_numeric(dfc2["Revenue"], errors="coerce").fillna(0)
                    dfc2["Cost"] = pd.to_numeric(dfc2["Cost"], errors="coerce").fillna(0)
                    agg = dfc2.groupby("Customer", as_index=False).agg({"Revenue":"sum","Cost":"sum"})
                    agg["Profit"] = agg["Revenue"] - agg["Cost"]
                    agg["ProfitMargin"] = np.where(agg["Revenue"]>0, agg["Profit"]/agg["Revenue"], 0.0)
                    cust_agg = pd.merge(cust_agg, agg[["Customer","Profit","ProfitMargin"]], on="Customer", how="left").fillna(0)

                st.subheader("Customer ABC (preview)")
                st.dataframe(cust_agg.sort_values("TotalRevenue", ascending=False).reset_index(drop=True))

                # Scatter plot Revenue vs ProfitMargin (if available)
                if "ProfitMargin" in cust_agg.columns:
                    figc, axc = plt.subplots(figsize=(6,4))
                    axc.scatter(cust_agg["TotalRevenue"], cust_agg["ProfitMargin"]*100)
                    axc.set_xlabel("TotalRevenue")
                    axc.set_ylabel("ProfitMargin (%)")
                    axc.set_title("Revenue vs ProfitMargin")
                    st.pyplot(figc); figs.append(figc)

                # bar of ABC classes
                figcb, axcb = plt.subplots(figsize=(6,3))
                cust_agg["ABC_Revenue"].value_counts().reindex(["A","B","C"]).fillna(0).plot(kind="bar", ax=axcb)
                axcb.set_title("Customers by ABC (Revenue)")
                st.pyplot(figcb); figs.append(figcb)

                excel_bytes = df_to_excel_bytes({"Customer_Segmentation": cust_agg})
                st.download_button("⬇️ Download Customer segmentation (Excel)", data=excel_bytes, file_name="customer_segmentation.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                pdf_buf = export_pdf("Customer Segmentation", cust_agg, figs if include_plots_in_pdf else [])
                st.download_button("⬇️ Download PDF", data=pdf_buf, file_name="customer_segmentation.pdf", mime="application/pdf")

# --- SUPPLIER SEGMENTATION ---
elif selected == "Supplier":
    st.header("Supplier segmentation (Kraljic-style)")
    st.markdown("Requires mapping of Supplier, ProfitImpact, and SupplyRisk columns (or else the app will explain what's missing).")

    if not col_selected(supplier_col):
        st.warning("Please map a Supplier column in the sidebar to run Supplier segmentation.")
    elif not (col_selected(profitimpact_col) and col_selected(supplyrisk_col)):
        st.warning("For Kraljic-style segmentation map ProfitImpact and SupplyRisk columns in the sidebar (both required).")
    else:
        thr = st.slider("Threshold for high/low (same scale as your ProfitImpact and SupplyRisk)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
        if st.button("Run Supplier segmentation"):
            dfs = df[[supplier_col, profitimpact_col, supplyrisk_col]].copy().rename(columns={supplier_col: "Supplier", profitimpact_col: "ProfitImpact", supplyrisk_col: "SupplyRisk"})
            # ensure numeric
            dfs["ProfitImpact"] = pd.to_numeric(dfs["ProfitImpact"], errors="coerce").fillna(0)
            dfs["SupplyRisk"] = pd.to_numeric(dfs["SupplyRisk"], errors="coerce").fillna(0)

            seg = dfs.groupby("Supplier", as_index=False).agg({"ProfitImpact":"mean","SupplyRisk":"mean"})
            def _label_row(r):
                hi_imp = r["ProfitImpact"] >= thr
                hi_risk = r["SupplyRisk"] >= thr
                if hi_imp and hi_risk:
                    return "Strategic"
                if hi_imp and not hi_risk:
                    return "Leverage"
                if not hi_imp and hi_risk:
                    return "Bottleneck"
                return "Non-Critical"
            seg["Segment"] = seg.apply(_label_row, axis=1)

            st.subheader("Supplier segmentation (preview)")
            st.dataframe(seg.sort_values(["ProfitImpact","SupplyRisk"], ascending=False).reset_index(drop=True))

            # Scatter plot Kraljic matrix
            figs = []
            fig, ax = plt.subplots(figsize=(6,5))
            for name, g in seg.groupby("Segment"):
                ax.scatter(g["ProfitImpact"], g["SupplyRisk"], label=name, s=50)
            ax.axvline(thr, linestyle="--"); ax.axhline(thr, linestyle="--")
            ax.set_xlabel("ProfitImpact"); ax.set_ylabel("SupplyRisk")
            ax.set_title("Kraljic matrix (ProfitImpact vs SupplyRisk)")
            ax.legend()
            st.pyplot(fig); figs.append(fig)

            excel_bytes = df_to_excel_bytes({"Supplier_Segmentation": seg})
            st.download_button("⬇️ Download Supplier segmentation (Excel)", data=excel_bytes, file_name="supplier_segmentation.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            pdf_buf = export_pdf("Supplier Segmentation", seg, figs if include_plots_in_pdf else [])
            st.download_button("⬇️ Download PDF", data=pdf_buf, file_name="supplier_segmentation.pdf", mime="application/pdf")

# Footer
st.markdown("---")
st.caption("Segmentation Toolkit — single-sheet mode. If you want the app adapted to specific company rules (weights, criticality scales, or different MCABC logic), tell me which columns / weights you'd like and I'll update the code.")
