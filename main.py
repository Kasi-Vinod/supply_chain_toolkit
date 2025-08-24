# main.py
import streamlit as st

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
    st.caption("EOQ • Segmentation • (more coming soon)")

# ---- Hero section ----
st.markdown("""
Welcome to your one-stop toolkit for smarter supply chain decisions.  
Use the tiles below to jump into **Inventory (EOQ)** and **Segmentation**.  
""")

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("Ready-made analyses", "2", delta="modular")
with kpi2:
    st.metric("Files supported", "CSV, Excel")
with kpi3:
    st.metric("Visuals", "Pareto • Sawtooth • Kraljic")

st.divider()

# ---- Tiles ----
t1, t2 = st.columns(2)

with t1:
    st.subheader("📦 Inventory Toolkit (EOQ)")
    st.write("Calculate EOQ, total logistics cost, reorder point, cycle time, and discount checks.")
    st.page_link("pages/1_Inventory_Toolkit_EOQ.py", label="Open EOQ Toolkit →", icon="📦")

with t2:
    st.subheader("🧩 Segmentation Toolkit")
    st.write("Segment **Products (ABC & MCABC)**, **Customers (profitability)**, and **Suppliers (Kraljic)**.")
    st.page_link("pages/2_Segmentation_Toolkit.py", label="Open Segmentation →", icon="🧭")

st.divider()
st.caption("Tip: add more features by dropping new files in the `pages/` folder.")
