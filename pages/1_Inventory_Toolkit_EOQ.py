# app.py
import math
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.set_page_config(page_title="Supply Chain Inventory Toolkit", layout="wide")

SAMPLES = {
    "Custom": None,
    "Coffee Co (your case)": {
        "D": 6000.0, "C": 1500.0, "S": 100.0, "i": 0.15, "L": 3.0, "sigma": 50.0,
        "Discounts": [(1000, 95), (2000, 90), (3000, 85)]
    }
}

st.title("📦 Supply Chain Inventory Toolkit (EOQ Model)")

sample_choice = st.selectbox("Choose a sample case:", list(SAMPLES.keys()))

if sample_choice == "Custom":
    D = st.number_input("Annual Demand (units)", value=1000.0, step=100.0)
    C = st.number_input("Unit Cost ($)", value=10.0, step=1.0)
    S = st.number_input("Ordering Cost ($ per order)", value=50.0, step=10.0)
    i = st.number_input("Annual Holding Rate (as fraction)", value=0.2, step=0.01)
    L = st.number_input("Lead Time (months)", value=2.0, step=1.0)
    sigma = st.number_input("Std Dev of Demand (units/month)", value=20.0, step=5.0)
    Discounts = []
else:
    case = SAMPLES[sample_choice]
    D, C, S, i, L, sigma = case["D"], case["C"], case["S"], case["i"], case["L"], case["sigma"]
    Discounts = case["Discounts"]

run = st.button("Run EOQ Analysis")

if run:
    try:
        H = C * i
        EOQ = math.sqrt((2 * D * S) / H)
        num_orders = D / EOQ
        t = EOQ / D * 12
        t_days = t * 30
        OrderingCost = num_orders * S
        HoldingCost = EOQ/2 * H
        TLC = OrderingCost + HoldingCost
        ROP = (D/12 * L) + (sigma * math.sqrt(L))

        res = {
            "EOQ": EOQ, "TLC": TLC, "OrderingCost": OrderingCost, "HoldingCost": HoldingCost,
            "ROP": ROP, "t_months": t, "t_days": t_days
        }

        # ---- Graphs ----
        # 1. Cost vs Q
        Qs = np.linspace(1, EOQ*3, 100)
        TCs = (D/Qs)*S + (Qs/2)*H
        fig1, ax1 = plt.subplots()
        ax1.plot(Qs, TCs, label="Total Cost")
        ax1.axvline(EOQ, color="r", linestyle="--", label=f"EOQ={EOQ:.0f}")
        ax1.set_xlabel("Order Quantity (Q)")
        ax1.set_ylabel("Cost ($)")
        ax1.set_title("Total Cost vs Order Quantity")
        ax1.legend()
        st.pyplot(fig1)

        # 2. Inventory sawtooth
        fig2, ax2 = plt.subplots()
        time = np.linspace(0, t, 100)
        inventory = EOQ * (1 - time/t)
        ax2.plot(time, inventory)
        ax2.set_title("Inventory Cycle")
        ax2.set_xlabel("Time (months)")
        ax2.set_ylabel("Inventory Level")
        st.pyplot(fig2)

        # 3. Service level safety stock
        z = 1.65
        SS = z * sigma * math.sqrt(L)
        fig3, ax3 = plt.subplots()
        ax3.bar(["ROP", "Safety Stock"], [ROP, SS])
        ax3.set_title("Reorder Point & Safety Stock")
        st.pyplot(fig3)

        res["discount"] = False
        if Discounts:
            res["discount"] = True
            fig4, ax4 = plt.subplots()
            qs = []
            costs = []
            for q, price in Discounts:
                H_disc = price * i
                EOQ_disc = math.sqrt((2*D*S)/H_disc)
                cost_disc = (D/EOQ_disc)*S + (EOQ_disc/2)*H_disc + D*price
                qs.append(EOQ_disc)
                costs.append(cost_disc)
            ax4.plot(qs, costs, marker="o")
            ax4.set_title("Quantity Discounts Effect")
            st.pyplot(fig4)

        # ---------- PDF EXPORT ----------
        def create_pdf(res, figs):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # --- Summary ---
            summary_text = f"""
            <b>EOQ Analysis Report</b><br/>
            EOQ for this scenario is <b>{res['EOQ']:.0f} units</b>, with a total logistics cost of 
            <b>{res['TLC']:.0f} USD/yr</b>. 
            Recommended reorder point (ROP) is <b>{res['ROP']:.0f}</b>.
            """
            elements.append(Paragraph(summary_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))

            # --- Key Metrics ---
            metrics_text = f"""
            EOQ: {res['EOQ']:.2f}<br/>
            Total Logistics Cost: {res['TLC']:.2f}<br/>
            Ordering Cost: {res['OrderingCost']:.2f}<br/>
            Holding Cost: {res['HoldingCost']:.2f}<br/>
            Reorder Point: {res['ROP']:.2f}<br/>
            Time between orders: {res['t_months']:.2f} months (~{res['t_days']:.0f} days)
            """
            elements.append(Paragraph(metrics_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))

            # --- Figures ---
            for fig in figs:
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png', dpi=150, bbox_inches="tight")
                img_buf.seek(0)
                elements.append(Image(img_buf, width=6*inch, height=3.5*inch))
                elements.append(Spacer(1, 0.2*inch))

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            return pdf

        # Collect figs
        figs = [fig1, fig2, fig3]
        if res["discount"]:
            figs.append(fig4)

        pdf_bytes = create_pdf(res, figs)

        st.download_button(
            label="📄 Download Full Report (PDF)",
            data=pdf_bytes,
            file_name="EOQ_Report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error during calculation: {e}")
