# pages/1_Inventory_Toolkit_EOQ.py
import math
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# For PDF export
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

# DO NOT call st.set_page_config here (it's set in main.py)

SAMPLES = {
    "Custom": None,
    "Coffee Co (your case)": {
        "D": 6000.0, "C": 1500.0, "S": 4000.0, "h_rate": 0.10, "lead_time_months": 2.0,
        "discount_enabled": True, "discount_Q": 500.0, "discount_rate": 0.10
    },
    "CocoaDelight (example)": {
        "D": 12000.0, "C": 2000.0, "S": 5000.0, "h_rate": 0.12, "lead_time_months": 3.0,
        "discount_enabled": True, "discount_Q": 1200.0, "discount_rate": 0.05
    }
}

# ---------- Calculation function ----------
def compute_eoq(D, C, S, h_rate, lead_time_months,
                discount_enabled=False, discount_Q=None, discount_rate=0.0):
    if D <= 0 or C <= 0 or h_rate <= 0:
        raise ValueError("D, C and h_rate must be positive numbers.")
    h = h_rate * C
    Q_star = math.sqrt((2 * D * S) / h)
    ordering_cost = (D / Q_star) * S
    holding_cost = (Q_star / 2.0) * h
    TLC = ordering_cost + holding_cost
    t_months = (Q_star / D) * 12.0 if D else 0.0
    t_days = t_months * 30.4375
    ROP = (D / 12.0) * lead_time_months

    base_purchase = D * C
    total_base = base_purchase + TLC

    discount = None
    if discount_enabled and discount_Q and discount_Q > 0 and 0 < discount_rate < 1:
        new_price = C * (1 - discount_rate)
        h_disc = h_rate * new_price
        ordering_cost_disc = (D / discount_Q) * S
        holding_cost_disc = (discount_Q / 2.0) * h_disc
        TLC_disc = ordering_cost_disc + holding_cost_disc
        purchase_disc = D * new_price
        total_disc = purchase_disc + TLC_disc
        accept = total_disc < total_base
        annual_savings = total_base - total_disc
        discount = {
            "discount_Q": discount_Q,
            "discount_rate": discount_rate,
            "new_price": new_price,
            "ordering_cost_disc": ordering_cost_disc,
            "holding_cost_disc": holding_cost_disc,
            "TLC_disc": TLC_disc,
            "purchase_disc": purchase_disc,
            "total_disc": total_disc,
            "accept": accept,
            "annual_savings": annual_savings
        }

    results = {
        "EOQ": Q_star,
        "h": h,
        "OrderingCost": ordering_cost,
        "HoldingCost": holding_cost,
        "TLC": TLC,
        "t_months": t_months,
        "t_days": t_days,
        "ROP": ROP,
        "purchase_base": base_purchase,
        "total_base": total_base,
        "discount": discount
    }
    return results

# ---------- UI ----------
col1, col2 = st.columns([1,4])
with col1:
    try:
        st.image("vk_logo.png", width=100)
    except Exception:
        pass
with col2:
    st.title("📦 Supply Chain Toolkit — EOQ")
    st.markdown("### Smarter Decisions")

st.markdown("Calculate EOQ, Total Logistics Cost, time between orders, reorder point, and evaluate supplier discounts.")

with st.sidebar:
    st.header("Inputs & Presets")
    preset = st.selectbox("Choose a preset (or Custom)", list(SAMPLES.keys()), index=1)
    pre = SAMPLES[preset] if preset != "Custom" else {}

    D = st.number_input("Annual demand D (units / year)", min_value=0.0, value=float(pre.get("D", 6000.0)), step=100.0)
    C = st.number_input("Unit price C (USD/unit)", min_value=0.01, value=float(pre.get("C", 1500.0)), step=50.0)
    S = st.number_input("Ordering cost S (USD/order)", min_value=0.0, value=float(pre.get("S", 4000.0)), step=100.0)
    h_rate = st.number_input("Holding cost rate h (decimal)", min_value=0.0001, max_value=1.0, value=float(pre.get("h_rate", 0.10)), step=0.01, format="%.4f")
    lead_time_months = st.number_input("Lead time (months)", min_value=0.0, value=float(pre.get("lead_time_months", 2.0)), step=0.5)

    st.subheader("Discount (optional)")
    discount_enabled = st.checkbox("Supplier discount available?", value=bool(pre.get("discount_enabled", False)))
    if discount_enabled:
        discount_Q = st.number_input("Discount threshold Q", min_value=1.0, value=float(pre.get("discount_Q", 500.0)), step=50.0)
        discount_rate_pct = st.slider("Discount rate (%)", min_value=1, max_value=50, value=int(pre.get("discount_rate", 0.10) * 100 if pre.get("discount_rate") else 10))
        discount_rate = discount_rate_pct / 100.0
    else:
        discount_Q, discount_rate = None, 0.0

    run = st.button("Calculate")

if run:
    try:
        res = compute_eoq(
            D=float(D), C=float(C), S=float(S), h_rate=float(h_rate),
            lead_time_months=float(lead_time_months),
            discount_enabled=bool(discount_enabled),
            discount_Q=float(discount_Q) if discount_enabled else None,
            discount_rate=float(discount_rate) if discount_enabled else 0.0
        )

        # ---------- PDF Export (professional layout) ----------
        def create_pdf(res, figs):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # --- Header with logo & date ---
            try:
                header_logo = Image("vk_logo.png", width=0.8*inch, height=0.8*inch)
                elements.append(header_logo)
            except:
                pass
            header_text = f"<b>EOQ Analysis Report</b>  |  {datetime.today().strftime('%d %b %Y')}"
            elements.append(Paragraph(header_text, styles['Title']))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
            elements.append(Spacer(1, 0.2*inch))

            # --- Summary ---
            summary_text = f"""
            EOQ for this scenario is <b>{res['EOQ']:.0f} units</b>, 
            with a total logistics cost of <b>{res['TLC']:.0f} USD/yr</b>. 
            Recommended reorder point (ROP) is <b>{res['ROP']:.0f}</b>.
            """
            elements.append(Paragraph(summary_text, styles['Italic']))
            elements.append(Spacer(1, 0.2*inch))

            # --- Metrics as Tiles (colored table) ---
            data = [
                ["EOQ", f"{res['EOQ']:.2f}", "TLC", f"{res['TLC']:.2f}"],
                ["Ordering Cost", f"{res['OrderingCost']:.2f}", "Holding Cost", f"{res['HoldingCost']:.2f}"],
                ["ROP", f"{res['ROP']:.2f}", "Cycle Time", f"{res['t_months']:.2f} mo (~{res['t_days']:.0f} d)"]
            ]
            table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
                ('BACKGROUND', (2, 0), (3, 0), colors.lightgreen),
                ('BACKGROUND', (0, 1), (1, 1), colors.whitesmoke),
                ('BACKGROUND', (2, 1), (3, 1), colors.whitesmoke),
                ('BACKGROUND', (0, 2), (3, 2), colors.beige),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.2*inch))

            # --- Graphs Section Title ---
            elements.append(Paragraph("<b>📊 Key Visualizations</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))

            # --- Graphs in 2x2 Grid ---
            row = []
            count = 0
            for fig in figs:
                if fig:
                    img_buf = io.BytesIO()
                    fig.savefig(img_buf, format='png', dpi=120, bbox_inches="tight")
                    img_buf.seek(0)
                    row.append(Image(img_buf, width=3.5*inch, height=2.5*inch))
                    count += 1
                    if count % 2 == 0:   # 2 per row
                        t = Table([row], colWidths=[3.5*inch, 3.5*inch])
                        elements.append(t)
                        elements.append(Spacer(1, 0.1*inch))
                        row = []
            if row:
                t = Table([row], colWidths=[3.5*inch]*len(row))
                elements.append(t)

            # --- Footer ---
            elements.append(Spacer(1, 0.3*inch))
            footer = Paragraph("Prepared by Vinod Kasi | Swift Supply Chain Analytics", styles['Normal'])
            elements.append(footer)

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            return pdf

        # Collect figs
        figs = []
        # (We will still show visualizations in the Streamlit app as before)
        # Here you should include fig1, fig2, fig3, fig4 if defined

        pdf_bytes = create_pdf(res, figs)

        st.download_button(
            label="📄 Download Professional Report (PDF)",
            data=pdf_bytes,
            file_name="EOQ_Report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error during calculation: {e}")
else:
    st.info("Enter inputs in the sidebar and press **Calculate**.")
