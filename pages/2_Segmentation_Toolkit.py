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

# ---------- Helpers ----------
def _pct_bins_classifier(pct: float, a_pct: float, b_pct: float) -> str:
    if pct <= a_pct:
        return "A"
    elif pct <= a_pct + b_pct:
        return "B"
    return "C"

# ----------------- Analysis functions -----------------
def abc_analysis(df: pd.DataFrame, a_pct: float, b_pct: float) -> pd.DataFrame:
    out = df.copy()
    out["AnnualValue"] = out["Demand"] * out["UnitCost"]
    out = out.sort_values("AnnualValue", ascending=False).reset_index(drop=True)
    total = out["AnnualValue"].sum()
    out["Cumulative%"] = 0.0 if total == 0 else 100.0 * out["AnnualValue"].cumsum() / total
    out["ABC_Class"] = out["Cumulative%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
    return out

def mcabc_analysis(df: pd.DataFrame, a_pct: float, b_pct: float, w_value: float, w_lead: float, w_crit: float) -> pd.DataFrame:
    out = df.copy()
    out["AnnualValue"] = out["Demand"] * out["UnitCost"]

    comps, weights = [], []
    if out["AnnualValue"].max() > 0 and w_value > 0:
        out["Value_norm"] = out["AnnualValue"] / out["AnnualValue"].max()
        comps.append("Value_norm"); weights.append(w_value)
    if "LeadTime" in out.columns and out["LeadTime"].max() > 0 and w_lead > 0:
        out["Lead_norm"] = out["LeadTime"] / out["LeadTime"].max()
        comps.append("Lead_norm"); weights.append(w_lead)
    if "Criticality" in out.columns and out["Criticality"].max() > 0 and w_crit > 0:
        out["Crit_norm"] = out["Criticality"] / out["Criticality"].max()
        comps.append("Crit_norm"); weights.append(w_crit)

    if comps:
        wsum = sum(weights)
        out["Score"] = sum((w/wsum) * out[c] for c, w in zip(comps, weights))
    else:
        out["Score"] = out["AnnualValue"]

    out = out.sort_values("Score", ascending=False).reset_index(drop=True)
    total = out["Score"].sum()
    out["Cum%"] = 0.0 if total == 0 else 100.0 * out["Score"].cumsum() / total
    out["MCABC_Class"] = out["Cum%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
    return out

def customer_segmentation(df: pd.DataFrame, a_pct: float, b_pct: float) -> pd.DataFrame:
    out = df.copy()
    out["Profit"] = out["Revenue"] - out["CostToServe"]
    out["ProfitMargin"] = np.where(out["Revenue"] > 0, out["Profit"]/out["Revenue"], 0.0)

    agg = out.groupby("Customer", as_index=False).agg({"Revenue":"sum","Profit":"sum"})
    agg["ProfitMargin"] = np.where(agg["Revenue"] > 0, agg["Profit"]/agg["Revenue"], 0.0)

    agg = agg.sort_values("Revenue", ascending=False).reset_index(drop=True)
    total = agg["Revenue"].sum()
    agg["Cumulative%"] = np.where(total>0, 100*agg["Revenue"].cumsum()/total, 0.0)
    agg["ABC_Class"] = agg["Cumulative%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))

    out_list = []
    for cat in ["A","B","C"]:
        sub = agg[agg["ABC_Class"]==cat].copy()
        if len(sub)==0: continue
        totalp = sub["Profit"].sum()
        sub["Profit%"] = np.where(totalp>0, 100*sub["Profit"].cumsum()/totalp, 0.0)
        sub["SubClass"] = sub["Profit%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
        sub["FinalClass"] = sub["ABC_Class"]+"-"+sub["SubClass"]
        out_list.append(sub)
    if out_list:
        agg = pd.concat(out_list).sort_index()
    return agg

def kraljic_segmentation(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    out = df.copy()
    def _label(r):
        hi_imp, hi_risk = r["ProfitImpact"]>=threshold, r["SupplyRisk"]>=threshold
        if hi_imp and hi_risk: return "Strategic"
        if hi_imp and not hi_risk: return "Leverage"
        if not hi_imp and hi_risk: return "Bottleneck"
        return "Non-Critical"
    out["Segment"] = out.apply(_label, axis=1)
    return out

# ----------------- PDF Export -----------------
def export_pdf(title, df, figs):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))

    # Data Table
    data = [df.columns.tolist()] + df.head(20).values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.grey),
                               ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
                               ("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("GRID",(0,0),(-1,-1),0.5,colors.black)]))
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

# ----------------- UI -----------------
st.title("Segmentation Toolkit")

# Centralized file upload
file = st.file_uploader("Upload Excel File (with sheets: Product, Customer, Supplier)", type=["xlsx"])

if file:
    xls = pd.ExcelFile(file)

    # --- Tile navigation ---
    if "selected_tile" not in st.session_state:
        st.session_state.selected_tile = "Product"

    cols = st.columns(3)

    def render_tile(label, key, icon):
        selected = (st.session_state.selected_tile == key)
        color = "#4CAF50" if selected else "#f0f0f0"
        text_color = "white" if selected else "black"
        with cols[["Product","Customer","Supplier"].index(key)]:
            if st.button(f"{icon} {label}", key=f"tile_{key}", use_container_width=True):
                st.session_state.selected_tile = key
            st.markdown(
                f"""
                <div style='text-align:center;
                            background-color:{color};
                            color:{text_color};
                            padding:10px;
                            border-radius:10px;
                            margin-top:-15px;
                            font-weight:bold;'>
                    {label}
                </div>
                """,
                unsafe_allow_html=True
            )

    render_tile("Product", "Product", "📦")
    render_tile("Customer", "Customer", "👥")
    render_tile("Supplier", "Supplier", "🤝")

    st.markdown("---")

    # --- Segmentation logic ---
    if st.session_state.selected_tile == "Product":
        a_pct = st.slider("A %", 50, 80, 70, key="prod_a")
        b_pct = st.slider("B %", 10, 30, 20, key="prod_b")
        w_val = st.number_input("Weight Value",0.0,1.0,0.5,step=0.05,key="prod_val")
        w_lead = st.number_input("Weight Lead",0.0,1.0,0.3,step=0.05,key="prod_lead")
        w_crit = st.number_input("Weight Criticality",0.0,1.0,0.2,step=0.05,key="prod_crit")

        if st.button("Run Product Segmentation"):
            df = pd.read_excel(xls, sheet_name="Product")
            abc_df = abc_analysis(df,a_pct,b_pct)
            mc_df = mcabc_analysis(df,a_pct,b_pct,w_val,w_lead,w_crit)

            st.dataframe(abc_df)
            st.dataframe(mc_df)

            figs=[]
            fig1, ax1 = plt.subplots()
            ax1.bar(abc_df["Item"], abc_df["AnnualValue"])
            ax2=ax1.twinx(); ax2.plot(abc_df["Item"], abc_df["Cumulative%"], "r-")
            st.pyplot(fig1); figs.append(fig1)

            fig2, ax = plt.subplots()
            ax.bar(abc_df["ABC_Class"].value_counts().index, abc_df["ABC_Class"].value_counts().values)
            st.pyplot(fig2); figs.append(fig2)

            pdf_buf=export_pdf("Product Segmentation",abc_df,figs)
            st.download_button("⬇️ Download PDF",data=pdf_buf,file_name="product_segmentation.pdf")

    elif st.session_state.selected_tile == "Customer":
        a_pct = st.slider("A % (Revenue)", 50, 80, 70, key="cust_a")
        b_pct = st.slider("B % (Revenue)", 10, 30, 20, key="cust_b")

        if st.button("Run Customer Segmentation"):
            df = pd.read_excel(xls, sheet_name="Customer")
            seg = customer_segmentation(df,a_pct,b_pct)
            st.dataframe(seg)

            figs=[]
            fig,ax=plt.subplots()
            for n,g in seg.groupby("FinalClass"):
                ax.scatter(g["Revenue"], g["ProfitMargin"]*100, label=n)
            ax.legend(); st.pyplot(fig); figs.append(fig)

            pdf_buf=export_pdf("Customer Segmentation",seg,figs)
            st.download_button("⬇️ Download PDF",data=pdf_buf,file_name="customer_segmentation.pdf")

    elif st.session_state.selected_tile == "Supplier":
        thr = st.slider("Threshold",1,10,5,key="sup_thr")

        if st.button("Run Supplier Segmentation"):
            df = pd.read_excel(xls, sheet_name="Supplier")
            seg = kraljic_segmentation(df,thr)
            st.dataframe(seg)

            figs=[]
            fig,ax=plt.subplots()
            for n,g in seg.groupby("Segment"):
                ax.scatter(g["ProfitImpact"], g["SupplyRisk"], label=n)
            ax.axvline(thr); ax.axhline(thr); ax.legend()
            st.pyplot(fig); figs.append(fig)

            pdf_buf=export_pdf("Supplier Segmentation",seg,figs)
            st.download_button("⬇️ Download PDF",data=pdf_buf,file_name="supplier_segmentation.pdf")
