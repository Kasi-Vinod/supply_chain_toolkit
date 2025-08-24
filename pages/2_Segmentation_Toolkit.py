# pages/2_Segmentation_Toolkit.py
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------- Helpers ----------
def _pct_bins_classifier(pct: float, a_pct: float, b_pct: float) -> str:
    if pct <= a_pct:
        return "A"
    elif pct <= a_pct + b_pct:
        return "B"
    return "C"

def abc_analysis(df: pd.DataFrame, a_pct: float, b_pct: float) -> pd.DataFrame:
    out = df.copy()
    out["AnnualValue"] = out["Demand"] * out["UnitCost"]
    out = out.sort_values("AnnualValue", ascending=False).reset_index(drop=True)
    total = out["AnnualValue"].sum()
    if total == 0:
        out["Cumulative%"] = 0.0
    else:
        out["CumulativeValue"] = out["AnnualValue"].cumsum()
        out["Cumulative%"] = 100.0 * out["CumulativeValue"] / total
    out["ABC_Class"] = out["Cumulative%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
    return out

def mcabc_analysis(
    df: pd.DataFrame,
    a_pct: float,
    b_pct: float,
    w_value: float,
    w_lead: float,
    w_crit: float,
) -> pd.DataFrame:
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

    if not comps:
        out["Score"] = out["AnnualValue"]
    else:
        wsum = float(sum(weights))
        out["Score"] = 0.0
        for cname, w in zip(comps, weights):
            out["Score"] += (w / wsum) * out[cname]

    out = out.sort_values("Score", ascending=False).reset_index(drop=True)
    total = out["Score"].sum()
    if total == 0:
        out["Cum%"] = 0.0
    else:
        out["CumScore"] = out["Score"].cumsum()
        out["Cum%"] = 100.0 * out["CumScore"] / total
    out["MCABC_Class"] = out["Cum%"].apply(lambda p: _pct_bins_classifier(p, a_pct, b_pct))
    return out

def customer_segmentation(df: pd.DataFrame, margin_threshold: float) -> pd.DataFrame:
    out = df.copy()
    out["Profit"] = out["Revenue"] - out["CostToServe"]
    out["ProfitMargin"] = np.where(out["Revenue"] > 0, out["Profit"] / out["Revenue"], 0.0)

    agg = out.groupby("Customer", as_index=False).agg({"Revenue": "sum", "Profit": "sum"})
    agg["ProfitMargin"] = np.where(agg["Revenue"] > 0, agg["Profit"] / agg["Revenue"], 0.0)

    rev_med = agg["Revenue"].median()
    thr = margin_threshold / 100.0

    def _label(row):
        rev_high = row["Revenue"] >= rev_med
        margin_high = row["ProfitMargin"] >= thr
        if rev_high and margin_high:
            return "Key Account"
        if rev_high and not margin_high:
            return "High Rev - Low Margin"
        if (not rev_high) and margin_high:
            return "Growth / Niche"
        return "Standard"

    agg["Segment"] = agg.apply(_label, axis=1)
    return agg

def kraljic_segmentation(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    out = df.copy()[["Supplier", "ProfitImpact", "SupplyRisk"]].copy()
    def _label(row):
        hi_imp = row["ProfitImpact"] >= threshold
        hi_risk = row["SupplyRisk"] >= threshold
        if hi_imp and hi_risk: return "Strategic"
        if hi_imp and not hi_risk: return "Leverage"
        if (not hi_imp) and hi_risk: return "Bottleneck"
        return "Non-Critical"
    out["Segment"] = out.apply(_label, axis=1)
    return out

def _download_df_button(df: pd.DataFrame, filename: str, label: str):
    st.download_button(label, data=df.to_csv(index=False), file_name=filename, mime="text/csv")

# ---------- Header ----------
col1, col2 = st.columns([1, 6])
with col1:
    try:
        st.image("vk_logo.png", width=80)
    except Exception:
        pass
with col2:
    st.title("Segmentation Toolkit")
    st.caption("Products: ABC/MCABC • Customers: Profitability • Suppliers: Kraljic")

# ---------- Tabs ----------
tab_prod, tab_cust, tab_sup = st.tabs([
    "📦 Product Segmentation (ABC & MCABC)",
    "👥 Customer Segmentation",
    "🤝 Supplier Segmentation"
])

# -------------------- Product Tab --------------------
with tab_prod:
    st.subheader("Upload Product Data (CSV or Excel)")
    f = st.file_uploader("Products file", type=["csv","xlsx"], key="prod_upload")

    colA, colB = st.columns(2)
    with colA:
        a_pct = st.slider("A coverage %", 50, 80, 70)
    with colB:
        b_pct = st.slider("B coverage %", 10, 30, 20)

    st.markdown("**Weights for MCABC** (set to 0 to ignore a factor)")
    w1, w2, w3 = st.columns(3)
    with w1:
        w_val = st.number_input("Weight: Value (Demand×Cost)", 0.0, 1.0, 0.5, step=0.05)
    with w2:
        w_lead = st.number_input("Weight: Lead Time", 0.0, 1.0, 0.3, step=0.05)
    with w3:
        w_crit = st.number_input("Weight: Criticality", 0.0, 1.0, 0.2, step=0.05)

    run = st.button("Run Product Analysis")
    if run:
        if f is None:
            st.error("Please upload a Products CSV/Excel first.")
        else:
            try:
                pdf = pd.read_excel(f) if f.name.endswith(".xlsx") else pd.read_csv(f)
            except Exception as e:
                st.error(f"Could not read file: {e}")
                pdf = None

            if pdf is not None:
                needed = {"Item","Demand","UnitCost"}
                if not needed.issubset(pdf.columns):
                    st.error(f"Missing required columns: {sorted(list(needed - set(pdf.columns)))}")
                else:
                    # ABC
                    abc_df = abc_analysis(pdf, a_pct, b_pct)
                    st.markdown("### ABC Results")
                    st.dataframe(abc_df[["Item","Demand","UnitCost","AnnualValue","Cumulative%","ABC_Class"]], use_container_width=True)

                    # Pareto
                    st.markdown("**Pareto (Annual Value & Cumulative %)**")
                    fig, ax1 = plt.subplots()
                    topN = min(30, len(abc_df))
                    ax1.bar(abc_df["Item"].head(topN), abc_df["AnnualValue"].head(topN))
                    ax1.set_xlabel("Item (top N)")
                    ax1.set_ylabel("Annual Value")
                    ax2 = ax1.twinx()
                    ax2.plot(abc_df["Item"].head(topN), abc_df["Cumulative%"].head(topN), marker="o")
                    ax2.set_ylabel("Cumulative %")
                    plt.xticks(rotation=90)
                    st.pyplot(fig, clear_figure=True)

                    # MCABC
                    mc_df = mcabc_analysis(pdf, a_pct, b_pct, w_val, w_lead, w_crit)
                    st.markdown("### Multi-Criteria ABC (MCABC) Results")
                    show_cols = ["Item","Score","MCABC_Class"]
                    extra_cols = [c for c in ["AnnualValue","LeadTime","Criticality"] if c in mc_df.columns]
                    st.dataframe(mc_df[show_cols + extra_cols], use_container_width=True)

                    # Distribution bars
                    st.markdown("**Class Distribution (ABC vs MCABC)**")
                    c1, c2 = st.columns(2)
                    with c1:
                        counts = abc_df["ABC_Class"].value_counts().reindex(["A","B","C"]).fillna(0)
                        fig2, ax = plt.subplots()
                        ax.bar(counts.index.astype(str), counts.values)
                        ax.set_title("ABC Counts")
                        st.pyplot(fig2, clear_figure=True)
                    with c2:
                        counts2 = mc_df["MCABC_Class"].value_counts().reindex(["A","B","C"]).fillna(0)
                        fig3, ax3 = plt.subplots()
                        ax3.bar(counts2.index.astype(str), counts2.values)
                        ax3.set_title("MCABC Counts")
                        st.pyplot(fig3, clear_figure=True)

                    st.markdown("---")
                    _download_df_button(abc_df, "product_ABC_results.csv", "Download ABC results (CSV)")
                    _download_df_button(mc_df, "product_MCABC_results.csv", "Download MCABC results (CSV)")

# -------------------- Customer Tab --------------------
with tab_cust:
    st.subheader("Upload Customer Data (CSV or Excel)")
    fc = st.file_uploader("Customers file", type=["csv","xlsx"], key="cust_upload")

    margin_thr = st.slider("Profit margin threshold (%)", 5, 50, 20)
    runc = st.button("Run Customer Analysis")
    if runc:
        if fc is None:
            st.error("Please upload a Customers CSV/Excel first.")
        else:
            try:
                cdf = pd.read_excel(fc) if fc.name.endswith(".xlsx") else pd.read_csv(fc)
            except Exception as e:
                st.error(f"Could not read file: {e}")
                cdf = None
            if cdf is not None:
                needed = {"Customer","Revenue","CostToServe"}
                if not needed.issubset(cdf.columns):
                    st.error(f"Missing required columns: {sorted(list(needed - set(cdf.columns)))}")
                else:
                    seg = customer_segmentation(cdf, margin_thr)
                    st.markdown("### Customer Segments")
                    st.dataframe(seg, use_container_width=True)

                    # Scatter: Revenue vs Profit Margin
                    st.markdown("**Revenue vs Profit Margin (%)**")
                    fig, ax = plt.subplots()
                    ax.scatter(seg["Revenue"], seg["ProfitMargin"]*100)
                    ax.set_xlabel("Revenue")
                    ax.set_ylabel("Profit Margin (%)")
                    ax.set_title("Customer Segmentation Matrix")
                    st.pyplot(fig, clear_figure=True)

                    st.markdown("---")
                    _download_df_button(seg, "customer_segments.csv", "Download customer segments (CSV)")

# -------------------- Supplier Tab --------------------
with tab_sup:
    st.subheader("Upload Supplier Data (CSV or Excel)")
    fs = st.file_uploader("Suppliers file", type=["csv","xlsx"], key="sup_upload")

    thr = st.slider("Kraljic threshold (1..10 scale)", 1.0, 10.0, 5.0, step=0.5)
    runs = st.button("Run Supplier Analysis")
    if runs:
        if fs is None:
            st.error("Please upload a Suppliers CSV/Excel first.")
        else:
            try:
                sdf = pd.read_excel(fs) if fs.name.endswith(".xlsx") else pd.read_csv(fs)
            except Exception as e:
                st.error(f"Could not read file: {e}")
                sdf = None
            if sdf is not None:
                needed = {"Supplier","ProfitImpact","SupplyRisk"}
                if not needed.issubset(sdf.columns):
                    st.error(f"Missing required columns: {sorted(list(needed - set(sdf.columns)))}")
                else:
                    seg = kraljic_segmentation(sdf, thr)
                    st.markdown("### Supplier Segments (Kraljic)")
                    st.dataframe(seg, use_container_width=True)

                    # Kraljic 2x2
                    st.markdown("**Kraljic Matrix (Impact vs Risk)**")
                    fig, ax = plt.subplots()
                    for name, grp in seg.groupby("Segment"):
                        ax.scatter(grp["ProfitImpact"], grp["SupplyRisk"], label=name)
                    ax.axvline(thr, linestyle="--")
                    ax.axhline(thr, linestyle="--")
                    ax.set_xlabel("Profit Impact")
                    ax.set_ylabel("Supply Risk")
                    ax.legend()
                    st.pyplot(fig, clear_figure=True)

                    st.markdown("---")
                    _download_df_button(seg, "supplier_segments.csv", "Download supplier segments (CSV)")

# -------- Optional: sample template download --------
with st.expander("Need a template? Download a 3-sheet Excel with sample columns"):
    sample_products = pd.DataFrame({
        "Item": ["P1","P2","P3","P4","P5"],
        "Demand": [500, 400, 200, 300, 800],
        "UnitCost": [100, 50, 30, 20, 5],
        "LeadTime": [2, 3, 10, 15, 20],
        "Criticality": [5, 4, 3, 2, 1],
    })
    sample_customers = pd.DataFrame({
        "Customer": ["C1","C2","C3","C4","C5"],
        "Revenue": [200000, 150000, 50000, 20000, 10000],
        "CostToServe": [80000, 50000, 30000, 15000, 9000],
    })
    sample_suppliers = pd.DataFrame({
        "Supplier": ["S1","S2","S3","S4"],
        "ProfitImpact": [9, 8, 3, 2],
        "SupplyRisk": [8, 3, 8, 2],
    })

    import xlsxwriter
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        sample_products.to_excel(writer, sheet_name="Products", index=False)
        sample_customers.to_excel(writer, sheet_name="Customers", index=False)
        sample_suppliers.to_excel(writer, sheet_name="Suppliers", index=False)
    st.download_button(
        "Download template (xlsx)",
        data=buf.getvalue(),
        file_name="segmentation_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
