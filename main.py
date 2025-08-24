# main.py
import streamlit as st

st.set_page_config(
    page_title="Supply Chain Toolkit",
    page_icon="📦",
    layout="wide",
)

# ---------- Global styles (compact + modern) ----------
st.markdown("""
<style>
  .block-container {
    padding-top: 2rem !important; /* extra top space to avoid cut-off */
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
  }
  h1, h2, h3 {
    margin-top: 0.5rem !important;
  }
  .subtitle {
    color:#6b7280;
    margin-top:.25rem
  }
  .section-hr {
    border:0;
    border-top:1px solid rgba(0,0,0,.08);
    margin:1rem 0
  }
  .hero {
    padding:22px 28px;
    border-radius:16px;
    color:#1a1a1a;
    background: #d4f5d0; /* light green background */
    box-shadow:0 6px 18px rgba(0,0,0,.08);
  }
  .road {padding:10px 12px;border-radius:10px;margin:.25rem 0;font-weight:500}
  .road.done{background:#e8f7ee;color:#1a7f37}
  .road.progress{background:#fff3e0;color:#9a5b00}
  .road.future{background:#f2f3f5;color:#545b6b}
  .soft{opacity:.7}
</style>
""", unsafe_allow_html=True)

# ---------- Header / Branding ----------
col_logo, col_title = st.columns([1, 7])
with col_logo:
    try:
        st.image("vk_logo.png", width=70)
    except Exception:
        st.write("VK")
with col_title:
    st.markdown("## 🚀 Supply Chain Decision Support Platform")
    st.markdown('<div class="subtitle">Analytics-driven insights to optimize inventory, customers, and suppliers.</div>',
                unsafe_allow_html=True)

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
  <h3 style="margin:0 0 6px 0;">Smarter Supply Chain Decisions 📊</h3>
  Leverage analytics to <b>optimize inventory</b>, <b>segment customers</b>, and <b>prioritize suppliers</b>. <br>
  👉 Start with one of the modules below, or try with demo data.
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

# ---------- Metrics row ----------
c1, c2, c3 = st.columns([1,1,1])
with c1:
    with st.container(border=True):
        st.subheader("📌 Toolkit")
        st.metric("Modules Live", "2 / 5", delta="on track")

with c2:
    with st.container(border=True):
        st.subheader("🚀 Roadmap Progress")
        st.progress(0.4, text="40% complete")

with c3:
    with st.container(border=True):
        st.subheader("📂 Data Supported")
        st.metric("Formats", "CSV, Excel", delta="more coming soon")

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
