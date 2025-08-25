import math
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# For PDF export
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

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
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("vk_logo.png", width=100)
    except Exception:
        pass
with col2:
    st.title("📦 Supply Chain Toolkit — EOQ")
    st.markdown("### Smarter Decisions")

st.markdown("Calculate EOQ, Total Logistics Cost, time between orders, reorder point, and evaluate supplier discounts.")

# --- Mode selector (Calculator <-> How-to guide) ---
with st.sidebar:
    view_mode = st.radio("Select view", ["Calculator", "How to use"], index=0)
    st.markdown("Select **How to use** for a guided, step-by-step walkthrough of the tool.")

# If user selected the How-to guide, show an interactive stepper and textual guidance
if view_mode == "How to use":
    steps = [
        {
            "title": "Overview",
            "body": (
                "This EOQ (Economic Order Quantity) toolkit helps you find the optimal order size (Q*) that balances ordering and holding costs. "
                "It computes: EOQ, Ordering cost, Holding cost, Total Logistics Cost (TLC = ordering + holding), Reorder Point (ROP), cycle time, and evaluates supplier discounts."
            )
        },
        {
            "title": "Enter inputs",
            "body": (
                "1. **Annual demand D** — units per year (e.g. 6000).\n"
                "2. **Unit price C** — price per unit in USD.\n"
                "3. **Ordering cost S** — fixed cost per order (USD).\n"
                "4. **Holding cost rate h** — decimal fraction of unit price per year (e.g. 0.10 for 10%). The tool converts this to \$ carrying cost per unit: `h * C`.\n"
                "5. **Lead time (months)** — supplier lead time in months (used to calculate ROP = demand during lead time).\n"
                "Use the **Choose a preset** dropdown in the sidebar to quickly load example inputs (Coffee Co or CocoaDelight), or pick **Custom** to enter your own numbers."
            )
        },
        {
            "title": "Run calculation",
            "body": (
                "After filling inputs in the sidebar, click **Calculate**.\n"
                "Top-line metrics appear immediately: EOQ, ROP, TLC, Ordering & Holding costs, and cycle time.\n"
                "If you enable a supplier discount, the tool will calculate the annual total cost if you adopt the discount (including lower purchase cost + adjusted TLC) and tell you whether the discount is beneficial (\`accept\` = True)."
            )
        },
        {
            "title": "Interpret the outputs",
            "body": (
                "• **EOQ**: recommended order size Q* that minimizes annual ordering + holding costs.\n"
                "• **Ordering Cost**: yearly cost from placing orders = (D / Q) * S at Q = EOQ.\n"
                "• **Holding Cost**: yearly carrying cost = (Q / 2) * h (where h = h_rate * C).\n"
                "• **TLC (shown)**: ordering + holding (purchase cost is shown separately as `purchase_base`).\n"
                "• **ROP**: demand during lead time (no safety stock in this basic model) = (D/12) * lead_time_months.\n"
                "• **Cycle time**: how often you should place orders (months and days).\n"
                "Use the **EOQ Cost Curve** to visually confirm the EOQ (where ordering and holding curves cross and total cost is minimized). The **Inventory over Time** plot shows the sawtooth inventory pattern where you receive EOQ when inventory hits ROP."
            )
        },
        {
            "title": "Discount analysis",
            "body": (
                "If a supplier offers a lower unit price for orders >= Q_threshold, enable Discount and enter the threshold and rate.\n"
                "The tool estimates total annual cost under that policy (purchase + ordering/holding at the threshold quantity) and compares it to the base policy.\n"
                "If `accept` is True, the discounted policy reduces annual totals and is recommended from a pure cost perspective — but also consider cash flow and storage capacity before accepting."
            )
        },
        {
            "title": "Export the report",
            "body": (
                "Click **Download One-Page Report (PDF)** to get a concise report that includes: summary, inputs, results table, and the graphs.\n"
                "Useful for sharing with procurement/supply chain stakeholders."
            )
        },
        {
            "title": "Examples & quick tips",
            "body": (
                "• *Coffee Co (your case)* preset: D=6000, C=1500, S=4000, h_rate=10%, lead time=2 months, discount threshold=500 @ 10%.\n"
                "• If EOQ < discount threshold but the discounted `total_disc` < `total_base`, then ordering at the discount quantity may be optimal despite a larger order size.\n"
                "• Common pitfall: negative/zero values for D, C or h_rate will raise an error — make sure numbers are positive and realistic.\n"
                "• To include safety stock, add a buffer to ROP (not implemented in this basic EOQ page)."
            )
        }
    ]

    if 'howto_step' not in st.session_state:
        st.session_state['howto_step'] = 0

    step_idx = st.session_state['howto_step']

    st.header("How to use — EOQ Toolkit (guided)")
    st.caption("Use the previous / next buttons to walk through the guide. When you're ready, switch the view in the left sidebar back to 'Calculator'.")

    # simple progress indicator
    total = len(steps)
    st.progress(int((step_idx + 1) / total * 100))

    st.subheader(f"Step {step_idx + 1}: {steps[step_idx]['title']}")
    st.markdown(steps[step_idx]['body'], unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    if c1.button("← Previous", disabled=(step_idx == 0)):
        st.session_state['howto_step'] = max(0, step_idx - 1)
        st.experimental_rerun()

    if c3.button("Next →", disabled=(step_idx == total - 1)):
        st.session_state['howto_step'] = min(total - 1, step_idx + 1)
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("**Quick checklist**:\n\n- Open the sidebar and select a preset or Custom.\n- Enter realistic numeric inputs.\n- Click **Calculate**.\n- Read the EOQ, ROP, and TLC.\n- Inspect graphs and discount analysis.\n- Click the PDF button to export a one-page report.")

else:
    # ---------- Original Calculator UI (unchanged behavior) ----------
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

            # --- Metrics ---
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

            # --- Graphs (UNCHANGED) ---
            col_top_left, col_top_right = st.columns(2)

            # EOQ Cost Curve
            with col_top_left:
                st.subheader("EOQ Cost Curve")
                Q = np.linspace(1, res["EOQ"] * 3, 500)
                OrderingCost = (D / Q) * S
                HoldingCost = (Q / 2) * res["h"]
                TotalCost = OrderingCost + HoldingCost + (D * C)

                fig1, ax1 = plt.subplots()
                ax1.plot(Q, OrderingCost, label="Ordering cost", linewidth=2)
                ax1.plot(Q, HoldingCost, label="Carrying cost", linewidth=2)
                ax1.plot(Q, TotalCost, label="Total cost", linewidth=2)
                ax1.axvline(x=res["EOQ"], color="orange", linestyle="--", linewidth=2)
                ax1.scatter(res["EOQ"], (D / res["EOQ"]) * S + (res["EOQ"]/2) * res["h"] + D*C,
                            color="orange", s=60, zorder=5)
                ax1.set_xlabel("Reorder quantity (Q)")
                ax1.set_ylabel("Annual cost")
                ax1.set_title("EOQ Cost Curve")
                ax1.legend(frameon=False)
                st.pyplot(fig1)

            # Inventory vs Time
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

            # TLC Breakdown
            col_bottom_left, col_bottom_right = st.columns(2)
            with col_bottom_left:
                st.subheader("TLC Breakdown")
                labels = ["Ordering Cost", "Holding Cost", "TLC"]
                values = [res["OrderingCost"], res["HoldingCost"], res["TLC"]]
                fig3, ax3 = plt.subplots()
                bars = ax3.bar(labels, values)
                for bar in bars:
                    yval = bar.get_height()
                    ax3.text(bar.get_x()+bar.get_width()/2, yval+(0.01*yval),
                             f"{yval:,.0f}", ha='center', va='bottom')
                st.pyplot(fig3)

            # Discount Analysis
            with col_bottom_right:
                st.subheader("Discount Analysis")
                if res["discount"]:
                    d = res["discount"]
                    labels = [f"Base EOQ ({res['EOQ']:.0f})", f"Discount Q ({d['discount_Q']:.0f})"]
                    values = [res["total_base"], d["total_disc"]]
                    fig4, ax4 = plt.subplots()
                    bars = ax4.bar(labels, values)
                    for bar in bars:
                        yval = bar.get_height()
                        ax4.text(bar.get_x()+bar.get_width()/2, yval+(0.01*yval),
                                 f"{yval:,.0f}", ha='center', va='bottom')
                    st.pyplot(fig4)
                else:
                    fig4 = None

            # --- PDF Export ---
            st.markdown("---")

            def header_footer(canvas, doc):
                width, height = A4
                canvas.setStrokeColor(colors.grey)
                canvas.line(30, height-60, width-30, height-60)  # Header border
                canvas.line(30, 40, width-30, 40)                # Footer border

                try:
                    canvas.drawImage("vk_logo.png", 30, height-50, width=50, height=30, preserveAspectRatio=True, mask='auto')
                except:
                    pass
                canvas.setFont("Helvetica-Bold", 12)
                canvas.drawCentredString(width/2, height-40, "EOQ Analysis Report")
                canvas.setFont("Helvetica", 9)
                canvas.drawRightString(width-40, height-40, pd.Timestamp.today().strftime("%Y-%m-%d"))
                canvas.setFont("Helvetica", 8)
                canvas.drawCentredString(width/2, 25, "Generated by Supply Chain Toolkit | Confidential")

            def create_pdf(res, figs):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4,
                                        topMargin=80, bottomMargin=60,
                                        leftMargin=30, rightMargin=30)
                styles = getSampleStyleSheet()
                elements = []

                # --- Summary ---
                elements.append(Paragraph("<b>Summary</b>", styles['Heading2']))
                summary_text = f"""
                EOQ is <b>{res['EOQ']:.0f} units</b>, TLC <b>{res['TLC']:.0f} USD/yr</b>,
                ROP <b>{res['ROP']:.0f} units</b>.
                """
                elements.append(Paragraph(summary_text, styles['Normal']))
                elements.append(Spacer(1, 0.2*inch))

                # --- Inputs ---
                elements.append(Paragraph("<b>Inputs Used</b>", styles['Heading2']))
                inputs_data = [
                    ["Annual Demand", f"{D:.0f}", "Unit Price", f"{C:.2f}"],
                    ["Ordering Cost", f"{S:.2f}", "Holding Rate", f"{h_rate:.2%}"],
                    ["Lead Time", f"{lead_time_months:.1f}", "Discount Enabled", str(discount_enabled)],
                    ["Discount Q", f"{discount_Q:.0f}" if discount_enabled else "—",
                     "Discount Rate", f"{discount_rate:.0%}" if discount_enabled else "—"]
                ]
                t_inputs = Table(inputs_data, colWidths=[1.6*inch]*4)
                t_inputs.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('BACKGROUND',(0,0),(-1,0),colors.lightblue),
                    ('FONTSIZE',(0,0),(-1,-1),8),
                    ('ALIGN',(0,0),(-1,-1),'CENTER')
                ]))
                elements.append(t_inputs)
                elements.append(Spacer(1, 0.2*inch))

                # --- Results ---
                elements.append(Paragraph("<b>Results</b>", styles['Heading2']))
                results_data = [
                    ["EOQ", f"{res['EOQ']:.2f}", "TLC", f"{res['TLC']:.2f}"],
                    ["Ordering Cost", f"{res['OrderingCost']:.2f}", "Holding Cost", f"{res['HoldingCost']:.2f}"],
                    ["ROP", f"{res['ROP']:.2f}", "Cycle Time", f"{res['t_months']:.2f} mo (~{res['t_days']:.0f} d)"]
                ]
                t_results = Table(results_data, colWidths=[1.6*inch]*4)
                t_results.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('BACKGROUND',(0,0),(-1,0),colors.lightgreen),
                    ('FONTSIZE',(0,0),(-1,-1),8),
                    ('ALIGN',(0,0),(-1,-1),'CENTER')
                ]))
                elements.append(t_results)
                elements.append(Spacer(1, 0.2*inch))

                # --- Graphs ---
                elements.append(Paragraph("<b>Graphs</b>", styles['Heading2']))
                row, count = [], 0
                for fig in figs:
                    if fig:
                        img_buf = io.BytesIO()
                        fig.savefig(img_buf, format='png', dpi=120, bbox_inches="tight")
                        img_buf.seek(0)
                        row.append(Image(img_buf, width=3.2*inch, height=2.3*inch))
                        count += 1
                        if count % 2 == 0:
                            elements.append(Table([row], colWidths=[3.2*inch]*2))
                            elements.append(Spacer(1, 0.1*inch))
                            row = []
                if row:
                    elements.append(Table([row], colWidths=[3.2*inch]*len(row)))

                doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
                pdf = buffer.getvalue()
                buffer.close()
                return pdf

            figs = [fig1, fig2, fig3]
            if fig4:
                figs.append(fig4)

            pdf_bytes = create_pdf(res, figs)

            st.download_button(
                label="📄 Download One-Page Report (PDF)",
                data=pdf_bytes,
                file_name="EOQ_Report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error during calculation: {e}")
    else:
        st.info("Enter inputs in the sidebar and press **Calculate**.")
