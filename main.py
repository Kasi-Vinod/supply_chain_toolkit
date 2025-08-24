# main.py
import streamlit as st
import os

st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide"
)

# ---- CSS to Reduce Padding (fit all content in one screen) ----
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---- HEADER / BRANDING ----
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("vk_logo.png", width=80)
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

st.divider()

# ---- IMPACT METRICS ROW ----
col1, col2, col3 = st.columns([1, 1.2, 1])
with col1:
    st.subheader("📌 Toolkit at a Glance")
    st.metric("Modules Live", "2 / 5", delta="on track")

with col2:
    st.subheader("🚀 Roadmap Progress")
    st.progress(0.4, text="40% complete")

with col3:
    st.subheader("📂 Data Supported")
    st.metric("Formats", "CSV, Excel", delta="more coming soon")

st.divider()

# ---- MODULE CARDS ROW ----
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

# ---- ROADMAP DETAILS ----
st.subheader("📍 Detailed Roadmap")
roadmap_col1, roadmap_col2 = st.columns(2)
with roadmap_col1:
    st.markdown(
        """
- ✅ **EOQ Toolkit** (Inventory Optimization)  
- ✅ **Segmentation Toolkit** (ABC, MCABC, Kraljic, Profitability)  
- 🔄 **Demand Forecasting** (in development)  
        """
    )
with roadmap_col2:
    st.markdown(
        """
- ⏳ **S&OP Planning** (next release)  
- ⏳ **Network Optimization** (future roadmap)  
        """
    )

st.divider()

# ---- FOOTER ----
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("© 2025 Supply Chain Decision Support Platform • Developed by Vinod Kasi • v1.0")
with col_f2:
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/vinodkasi/)"
    )
