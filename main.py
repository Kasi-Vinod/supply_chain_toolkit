# main.py
import streamlit as st
import os

st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide"
)

# ---- HEADER / BRANDING ----
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("vk_logo.png", width=90)
    except Exception:
        pass
with col_title:
    st.title("Supply Chain Decision Support Platform")
    st.caption("Analytics-driven insights to optimize inventory, customers, and suppliers.")

st.divider()

# ---- HERO SECTION ----
hero_left, hero_right = st.columns([2, 1])
with hero_left:
    st.markdown(
        """
### Smarter Supply Chain Decisions 📊  
Leverage analytics to **optimize inventory**, **segment customers**, and **prioritize suppliers**.  

👉 Start with one of the modules below, or try with demo data.  
        """
    )
# Removed "Get Started with EOQ" button
# Removed banner image placeholder/info box

st.divider()

# ---- IMPACT METRICS ----
st.subheader("📌 Toolkit at a Glance")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Modules Live", "2 / 5", delta="on track")
with m2:
    st.progress(0.4, text="Roadmap completion 40%")
with m3:
    st.metric("Data Supported", "CSV, Excel", delta="more coming soon")

st.divider()

# ---- MODULE CARDS ----
st.subheader("🧰 Available Modules")
t1, t2 = st.columns(2)

with t1:
    with st.container(border=True):
        st.subheader("📦 Inventory Toolkit (EOQ)")
        st.write(
            "Optimize stock levels with EOQ models: **calculate order sizes, cycle times, "
            "logistics costs, and evaluate supplier discounts.**"
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
            "Prioritize **products, customers, and suppliers** with data-driven frameworks: "
            "**ABC, MCABC, Kraljic, and profitability analysis.**"
        )
        st.page_link(
            "pages/2_Segmentation_Toolkit.py",
            label="Open Segmentation →",
            icon="🧭"
        )

st.divider()

# ---- ROADMAP SECTION ----
st.subheader("🚀 Roadmap")
st.markdown(
    """
- ✅ **EOQ Toolkit** (Inventory Optimization)  
- ✅ **Segmentation Toolkit** (ABC, MCABC, Kraljic, Profitability)  
- 🔄 **Demand Forecasting** (in development)  
- ⏳ **S&OP Planning** (next release)  
- ⏳ **Network Optimization** (future roadmap)  
    """
)

st.divider()

# ---- FOOTER ----
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("© 2025 Supply Chain Decision Support Platform • Developed by Vinod Kasi • v1.0")
with col_f2:
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/vinodkasi/)"
    )
