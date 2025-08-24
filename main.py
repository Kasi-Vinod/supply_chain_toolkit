# main.py
import streamlit as st

st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide"
)

# ---- CSS Styling ----
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        .stMetric {background: #f9f9f9; border-radius: 12px; padding: 10px;}
        .card {
            padding: 20px; border-radius: 15px;
            background-color: #ffffff;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        .hero {
            padding: 20px; border-radius: 15px;
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
            color: white; font-size: 18px;
        }
        .roadmap-item {
            padding: 8px; margin: 5px 0;
            border-radius: 8px; font-weight: 500;
        }
        .done {background: #e6f9ed; color: #1a7f37;}
        .progress {background: #fff5e6; color: #b26a00;}
        .future {background: #f0f0f0; color: #555;}
    </style>
""", unsafe_allow_html=True)

# ---- HEADER ----
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("vk_logo.png", width=80)
    except Exception:
        pass
with col_title:
    st.title("🚀 Supply Chain Decision Support Platform")
    st.caption("Analytics-driven insights to optimize inventory, customers, and suppliers.")

# ---- HERO ----
st.markdown("""
<div class="hero">
    <h3>Smarter Supply Chain Decisions 📊</h3>
    Leverage analytics to <b>optimize inventory</b>, <b>segment customers</b>, and <b>prioritize suppliers</b>.  
    <br>👉 Start with one of the modules below, or try with demo data.  
</div>
""", unsafe_allow_html=True)

st.divider()

# ---- METRICS ROW ----
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📌 Toolkit")
    st.metric("Modules Live", "2 / 5", "on track")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Roadmap Progress")
    st.progress(0.4, text="40% complete")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Data Supported")
    st.metric("Formats", "CSV, Excel", "more coming soon")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ---- MODULE CARDS ----
st.subheader("🧰 Available Modules")
t1, t2 = st.columns(2)

with t1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📦 Inventory Toolkit (EOQ)")
    st.write("Optimize stock levels with EOQ models: **order sizes, cycle times, costs, and discounts.**")
    st.page_link("pages/1_Inventory_Toolkit_EOQ.py", label="Open EOQ Toolkit →", icon="📦")
    st.markdown('</div>', unsafe_allow_html=True)

with t2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧩 Segmentation Toolkit")
    st.write("Prioritize **products, customers, and suppliers** with frameworks: **ABC, MCABC, Kraljic, profitability.**")
    st.page_link("pages/2_Segmentation_Toolkit.py", label="Open Segmentation →", icon="🧭")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ---- ROADMAP ----
st.subheader("📍 Detailed Roadmap")
r1, r2 = st.columns(2)

with r1:
    st.markdown('<div class="roadmap-item done">✅ EOQ Toolkit (Inventory Optimization)</div>', unsafe_allow_html=True)
    st.markdown('<div class="roadmap-item done">✅ Segmentation Toolkit (ABC, MCABC, Kraljic, Profitability)</div>', unsafe_allow_html=True)
    st.markdown('<div class="roadmap-item progress">🔄 Demand Forecasting (in development)</div>', unsafe_allow_html=True)

with r2:
    st.markdown('<div class="roadmap-item future">⏳ S&OP Planning (next release)</div>', unsafe_allow_html=True)
    st.markdown('<div class="roadmap-item future">⏳ Network Optimization (future roadmap)</div>', unsafe_allow_html=True)

st.divider()

# ---- FOOTER ----
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("© 2025 Supply Chain Decision Support Platform • Developed by Vinod Kasi • v1.0")
with col_f2:
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/vinodkasi/)"
    )
