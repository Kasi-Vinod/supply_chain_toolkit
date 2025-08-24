# pages/1_Inventory_Toolkit_EOQ.py
import math
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# For PDF export
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

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

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("EOQ (units)", f"{res['EOQ']:.2f}")
            st.metric("Reorder Point (ROP)", f"{res['ROP']:.2f}")
        with col2:
            st.metric("Total Logistics Cost (USD/yr)", f"{res['TLC']:.2f}")
            st.metric("Ordering Cost (USD/yr)", f"{res['OrderingCost']:.2f}")
        with col3:
            st.metric("Holding Cost (USD/yr)", f"{res['HoldingCost']:.2f}")
            st.metric("Time between orders", f"{res['t_months']:.2f} mo (~{res['t_days']:.0f} days)")

        st.markdown("---")
        st.markdown("## 📊 Visualizations")

        # --- Top Row ---
        col_top_left, col_top_right = st.columns(2)

        # EOQ Cost Curve
        with col_top_left:
            st.subheader("EOQ Cost Curve")

            Q = np.linspace(1, res["EOQ"]*3, 500)   # Focus around EOQ
            OrderingCost = (D / Q) * S
            HoldingCost = (Q / 2) * res["h"]
            TotalCost = OrderingCost + HoldingCost + (D * C)

            fig1, ax1 = plt.subplots()
            ax1.plot(Q, OrderingCost, color="red", label="Ordering cost", linewidth=2)
            ax1.plot(Q, HoldingCost, color="green", label="Carrying cost", linewidth=2)
            ax1.plot(Q, TotalCost, color="blue", label="Total cost", linewidth=2)
            ax1.axvline(x=res["EOQ"], color="orange", linestyle="--", linewidth=2)
            ax1.scatter(res["EOQ"], (D / res["EOQ"]) * S + (res["EOQ"]/2) * res["h"] + D*C, 
                        color="orange", s=60, zorder=5)
            ax1.text(res["EOQ"], (D / res["EOQ"]) * S + (res["EOQ"]/2) * res["h"] + D*C,
                     f"  EOQ = {int(res['EOQ'])}", color="orange", fontsize=10, va="bottom")
            ax1.set_xlabel("Reorder quantity (Q)")
            ax1.set_ylabel("Annual cost")
            ax1.set_title("EOQ Cost Curve")
            ax1.legend(frameon=False)
            st.pyplot(fig1)

        # Inventory vs Time (Sawtooth)
        with col_top_right:
            st.subheader("Inventory over Time (ROP & Cycle)")
            months = list(range(13))
            inventory = []
            Q = res["EOQ"]
            ROP = res["ROP"]
            level = Q
            for m in months:
                if level <= ROP:
                    level = Q
                inventory.append(level)
                level -= D / 12
            fig2 = plt.figure()
            plt.step(months, inventory, where="post", label="Inventory Level")
            plt.axhline(ROP, color="red", linestyle="--", label=f"ROP = {ROP:.0f}")
            plt.xlabel("Time (months)")
            plt.ylabel("Inventory Level")
            plt.title("Inventory Sawtooth Pattern")
            plt.legend()
            st.pyplot(fig2)

        # --- Bottom Row ---
        col_bottom_left, col_bottom_right = st.columns(2)

        # TLC Breakdown
        with col_bottom_left:
            st.subheader("TLC Breakdown (Annual Costs)")
            labels = ["Ordering Cost", "Holding Cost", "Total Logistics Cost"]
            values = [res["OrderingCost"], res["HoldingCost"], res["TLC"]]
            fig3, ax3 = plt.subplots()
            bars = ax3.bar(labels, values, color=["skyblue", "orange", "green"])
            ax3.set_ylabel("USD / year")
            ax3.set_title("Cost Components Breakdown")
            for bar in bars:
                yval = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2, yval + (0.01 * yval),
                         f"{yval:,.0f}", ha='center', va='bottom',
                         fontsize=10, fontweight='bold')
            st.pyplot(fig3)

        # Discount Analysis
        with col_bottom_right:
            st.subheader("Discount Analysis")
            if res["discount"]:
                d = res["discount"]
                labels = [f"Base EOQ ({res['EOQ']:.0f})", f"Discount Q ({d['discount_Q']:.0f})"]
                values = [res["total_base"], d["total_disc"]]
                fig4, ax4 = plt.subplots()
                bars = ax4.bar(labels, values, color=["blue", "green"])
                ax4.set_ylabel("USD / year")
                ax4.set_title("Base vs Discount Scenario")
                for bar in bars:
                    yval = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2, yval + (0.01 * yval),
                             f"{yval:,.0f}", ha='center', va='bottom',
                             fontsize=10, fontweight='bold')
                st.pyplot(fig4)
                if d["accept"]:
                    st.success(f"✅ Accept discount: Savings = {d['annual_savings']:.2f} USD/yr")
                else:
                    st.warning("❌ Base EOQ is cheaper — do not accept discount.")
            else:
                fig4 = None
                st.info("No discount scenario enabled.")

        # --- Downloads ---
        st.markdown("---")
        results_text = (
            f"EOQ: {res['EOQ']:.2f}\n"
            f"TLC: {res['TLC']:.2f}\n"
            f"Ordering cost: {res['OrderingCost']:.2f}\n"
            f"Holding cost: {res['HoldingCost']:.2f}\n"
            f"Time between orders (months): {res['t_months']:.2f}\n"
            f"Time between orders (days): {res['t_days']:.0f}\n"
            f"ROP: {res['ROP']:.2f}\n"
        )
        st.download_button("Download results (text)", data=results_text, file_name="supply_chain_results.txt")

        df = pd.DataFrame([{
            "EOQ": res['EOQ'], "TLC": res['TLC'], "OrderingCost": res['OrderingCost'],
            "HoldingCost": res['HoldingCost'], "t_months": res['t_months'], "t_days": res['t_days'],
            "ROP": res['ROP'], "purchase_base": res['purchase_base'], "total_base": res['total_base']
        }])
        csv_io = io.StringIO()
        df.to_csv(csv_io, index=False)
        st.download_button("Download results (CSV)", data=csv_io.getvalue(), file_name="supply_chain_results.csv")

        # ---------- PDF EXPORT ----------
        def create_pdf(res, figs):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # --- Summary ---
            summary_text = f"""
            <b>EOQ Analysis Report</b><br/>
            EOQ for this scenario is <b>{res['EOQ']:.0f} units</b>, 
            with a total logistics cost of <b>{res['TLC']:.0f} USD/yr</b>. 
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
                if fig:
                    img_buf = io.BytesIO()
                    fig.savefig(img_buf, format='png', dpi=150, bbox_inches="tight")
                    img_buf.seek(0)
                    elements.append(Image(img_buf, width=6*inch, height=3.5*inch))
                    elements.append(Spacer(1, 0.2*inch))

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            return pdf

        figs = [fig1, fig2, fig3]
        if fig4:
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
else:
    st.info("Enter inputs in the sidebar and press **Calculate**.")
