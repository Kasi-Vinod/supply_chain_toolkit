# main.py
import streamlit as st

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="SCM Segmentation Toolkit",
    page_icon="📊",
    layout="wide"
)

# ---------------- Custom CSS ----------------
st.markdown("""
    <style>
    /* Background & font */
    body {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Card styling */
    .card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        background-color: #fff;
        height: 160px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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


# ---------------- Header ----------------
st.title("📊 SCM Segmentation Toolkit")
st.markdown("Your one-stop solution for **supply chain segmentation, analysis, and reporting**.")


# ---------------- Dashboard Cards ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h4>📌 Toolkit</h4>
        <p>Modules Live</p>
        <h2>2 / 5</h2>
        <span style="color:green; font-weight:bold;">⬆ on track</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h4>🚀 Roadmap Progress</h4>
        <p>40% complete</p>
        <div class="progress-container">
            <div class="progress-bar" style="width:40%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h4>📂 Data Supported</h4>
        <p>Formats</p>
        <h3>CSV, Excel</h3>
        <span style="color:green; font-weight:bold;">⬆ more coming soon</span>
    </div>
    """, unsafe_allow_html=True)


# ---------------- Main Content ----------------
st.subheader("📑 About the Toolkit")
st.write("""
This toolkit helps you segment and analyze supply chain data with ease.  
Upload your datasets, explore segmentation strategies, and generate automated reports.
""")

# Example file uploader
uploaded_file = st.file_uploader("📥 Upload your dataset (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    # You can add pandas code here to process the file


# ---------------- Footer ----------------
st.markdown("<br><hr><center>Built with ❤️ using Streamlit</center>", unsafe_allow_html=True)
