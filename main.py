# main.py
import streamlit as st

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide"
)

# ---------------- Header ----------------
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

# ---------------- Hero Section ----------------
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

# ---------------- Impact Metrics ----------------
st.subheader("📌 Toolkit at a Glance")

# Custom CSS for equal cards
st.markdown("""
    <style>
    .metric-card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 15px;
        background: #fff;
        text-align: center;
        height: 140px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .progress-container {
        background:#eee;
        border-radius:5px;
        height:8px;
        width:100%;
        margin-top:8px;
    }
    .progress-bar {
        background:#ff6600;
        height:8px;
        border-radius:5px;
    }
    </style>
""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
    <div class="metric-card">
        <h4>📌 Toolkit</h4>
        <p>Modules Live</p>
        <h2>2 / 5</h2>
        <span style="color:green; font-weight:bold;">⬆ on track</span>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-card">
        <h4>🚀 Roadmap Progress</h4>
        <p>40% complete</p>
        <div class="progress-container">
            <div class="progress-bar" style="width:40%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card">
        <h4>📂 Data Supported</h4>
        <p>Formats</p>
        <h3>CSV, Excel</h3>
        <span style="color:green; font-weight:bold;">⬆ more coming soon</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------- Module Cards ----------------
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

# ---------------- Roadmap ----------------
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

# ---------------- Footer ----------------
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("© 2025 Supply Chain Decision Support Platform • Developed by Vinod Kasi • v1.0")
with col_f2:
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/vinodkasi/)"
    )
