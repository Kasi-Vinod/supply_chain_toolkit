# main.py
import streamlit as st
import os

st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide"
)

# ---- Header / branding ----
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("vk_logo.png", width=90)
    except Exception:
        pass
with col_title:
    st.title("Supply Chain Analytics Toolkit")
    st.caption("Smarter decisions with EOQ • Segmentation • (more coming soon)")

# ---- Optional banner ----
try:
    st.image("banner_supply_chain.png", use_container_width=True)
except Exception:
    st.markdown("")

# ---- Hero section ----
st.markdown(
    """
Welcome to your one-stop toolkit for smarter supply chain decisions.  
Use the **cards below** to explore modules like **Inventory (EOQ)** and **Segmentation**.
    """
)

# ---- KPI Section (card style) ----
k1, k2, k3 = st.columns(3)
with k1:
    st.container(border=True).metric("Ready-made analyses", "2", delta="modular")
with k2:
    st.container(border=True).metric("Files supported", "CSV, Excel")
with k3:
    st.container(border=True).metric("Visuals", "Pareto • Sawtooth • Kraljic")

st.divider()

# ---- Tiles ----
t1, t2 = st.columns(2)

with t1:
    with st.container(border=True):
        st.subheader("📦 Inventory Toolkit (EOQ)")
        st.write(
            "Calculate EOQ, total logistics cost, reorder point, cycle time, and discount checks."
        )
        st.page_link(
            "pages/1_Inventory_Toolkit_EOQ.py",
            label="Open EOQ Toolkit →",
            icon="📦"
        )

with t2:
    with st.container(border=True):
        st.subheader("🧩 Segmentation Toolkit")
        st.write(
            "Segment **Products (ABC & MCABC)**, **Customers (profitability)**, and **Suppliers (Kraljic)**."
        )
        st.page_link(
            "pages/2_Segmentation_Toolkit.py",
            label="Open Segmentation →",
            icon="🧭"
        )

st.divider()

# ---- Roadmap / What's Next ----
st.info("🚀 Coming soon: Demand Forecasting • S&OP Planning • Network Optimization")

# ---- Footer ----
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("© 2025 Supply Chain Analytics Toolkit • Developed by Vinod Kasi")
with col_f2:
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-Repo-black?logo=github)](https://github.com/yourrepo)"
    )
