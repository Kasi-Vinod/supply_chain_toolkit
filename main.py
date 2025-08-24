# main.py
import streamlit as st

st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide",
)

# ---------- Global styles ----------
st.markdown("""
<style>
  .block-container{padding-top:1rem;padding-bottom:1rem;padding-left:2rem;padding-right:2rem}
  h1{font-weight:800;letter-spacing:.2px;margin-bottom:.25rem}
  .subtitle{color:#6b7280;margin-top:.25rem}
  .section-hr{border:0;border-top:1px solid rgba(0,0,0,.08);margin:1rem 0}

  /* Hero Box */
  .hero{
    padding:28px 32px;
    border-radius:16px;
    color:#1f2937; /* dark gray text */
    background:linear-gradient(90deg,#bbf7d0 0%,#86efac 100%);
    box-shadow:0 6px 18px rgba(0,0,0,.08)
  }

  /* Equal height cards */
  .metric-card{
    min-height:170px;  /* same for all cards */
    display:flex;
    flex-direction:column;
    justify-content:center;
  }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
col_logo, col_title = st.columns([1, 7])
with col_logo:
    try:
        st.image("vk_logo.png", width=70)
    except Exception:
        st.write("VK")
with col_title:
    st.markdown("# 🚀 Supply Chain Decision Support Platform")
    st.markdown('<div class="subtitle">Analytics-driven insights to optimize inventory, customers, and suppliers.</div>',
                unsafe_allow_html=True)

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
  <h3 style="margin:0 0 10px 0;">Smarter Supply Chain Decisions 📊</h3>
  Leverage analytics to <b>optimize inventory</b>, <b>segment customers</b>, and <b>prioritize suppliers</b>. <br>
  👉 Start with one of the modules below, or try with demo data.
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Metrics row ----------
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📌 Toolkit")
        st.metric("Modules Live", "2 / 5", delta="on track")
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    with st.container(border=True):
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🚀 Roadmap Progress")
        st.progress(0.4, text="40% complete")
        st.markdown('</div>', unsafe_allow_html=True)

with c3:
    with st.container(border=True):
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📂 Data Supported")
        st.metric("Formats", "CSV, Excel", delta="more coming soon")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Modules ----------
st.subheader("🧰 Available Modules")
m1, m2 = st.columns(2)

with m1:
    with st.container(border=True):
        st.markdown("### 📦 Inventory Toolkit (EOQ)")
        st.write("Optimize stock levels with EOQ models: **calculate order sizes, cycle times, logistics costs, and evaluate supplier discounts.**")
        st.page_link("pages/1_Inventory_Toolkit_EOQ.py", label="Open EOQ Toolkit →", icon="📦")

with m2:
    with st.container(border=True):
        st.markdown("### 🧩 Segmentation Toolkit")
        st.write("Prioritize **products, customers, and suppliers** with data-driven frameworks: **ABC, MCABC, Kraljic, and profitability analysis.**")
        st.page_link("pages/2_Segmentation_Toolkit.py", label="Open Segmentation →", icon="🧭")

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Roadmap ----------
st.subheader("📍 Detailed Roadmap")
r1, r2 = st.columns(2)
with r1:
    st.markdown('<div class="road done">✅ EOQ Toolkit (Inventory Optimization)</div>', unsafe_allow_html=True)
    st.markdown('<div class="road done">✅ Segmentation Toolkit (ABC, MCABC, Kraljic, Profitability)</div>', unsafe_allow_html=True)
    st.markdown('<div class="road progress">🔄 Demand Forecasting (in development)</div>', unsafe_allow_html=True)
with r2:
    st.markdown('<div class="road future">⏳ S&OP Planning (next release)</div>', unsafe_allow_html=True)
    st.markdown('<div class="road future">⏳ Network Optimization (future roadmap)</div>', unsafe_allow_html=True)

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Footer ----------
f1, f2 = st.columns([3,1])
with f1:
    st.caption("© 2025 Supply Chain Decision Support Platform • Developed by Vinod Kasi • v1.0")
with f2:
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/vinodkasi/)"
    )
