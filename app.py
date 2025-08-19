# app.py
import math
import io
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Supply Chain Inventory Toolkit", page_icon="📦", layout="wide")

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
    t_days = t_months * 30.4375  # average days per month
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
st.title("📦 Supply Chain Inventory Toolkit")
st.markdown("Calculate EOQ, Total Logistics Cost, time between orders, reorder point, and evaluate supplier discounts.")

with st.sidebar:
    st.header("Inputs & Presets")
    preset = st.selectbox("Choose a preset (or Custom)", list(SAMPLES.keys()), index=1)
    if preset != "Custom":
        pre = SAMPLES[preset]
    else:
        pre = {}

    D = st.number_input("Annual demand D (units / tons / qty per year)", min_value=0.0, value=float(pre.get("D", 6000.0)), step=100.0, format="%.2f")
    C = st.number_input("Unit price C (USD/unit)", min_value=0.01, value=float(pre.get("C", 1500.0)), step=50.0, format="%.2f")
    S = st.number_input("Ordering cost S (USD/order)", min_value=0.0, value=float(pre.get("S", 4000.0)), step=100.0, format="%.2f")
    h_rate = st.number_input("Holding cost rate h (decimal, e.g. 0.10)", min_value=0.0001, max_value=1.0, value=float(pre.get("h_rate", 0.10)), step=0.01, format="%.4f")
    lead_time_months = st.number_input("Lead time (months)", min_value=0.0, value=float(pre.get("lead_time_months", 2.0)), step=0.5, format="%.2f")

    st.subheader("Discount (optional)")
    discount_enabled = st.checkbox("Supplier discount available?", value=bool(pre.get("discount_enabled", False)))
    if discount_enabled:
        discount_Q = st.number_input("Discount threshold Q (order quantity required)", min_value=1.0, value=float(pre.get("discount_Q", 500.0)), step=50.0, format="%.2f")
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
            st.metric("Reorder Point (ROP, units)", f"{res['ROP']:.2f}")
        with col2:
            st.metric("Total Logistics Cost (TLC, USD/yr)", f"{res['TLC']:.2f}")
            st.metric("Ordering Cost (USD/yr)", f"{res['OrderingCost']:.2f}")
        with col3:
            st.metric("Holding Cost (USD/yr)", f"{res['HoldingCost']:.2f}")
            st.metric("Time between orders", f"{res['t_months']:.2f} months (~{res['t_days']:.0f} days)")

        st.markdown("---")
        st.subheader("Detailed cost numbers")
        st.write(f"- Unit holding cost h = h_rate * C = {res['h']:.2f} USD/unit/year")
        st.write(f"- Annual purchase cost (base) = {res['purchase_base']:.2f} USD")
        st.write(f"- Total annual cost at EOQ (purchase + TLC) = {res['total_base']:.2f} USD")

        if res["discount"]:
            d = res["discount"]
            st.markdown("### Discount scenario analysis")
            st.write(f"- Discount Q required = {d['discount_Q']:.2f}")
            st.write(f"- Discount rate = {d['discount_rate']*100:.2f}% → new price = {d['new_price']:.2f} USD/unit")
            st.write(f"- TLC at discount Q = {d['TLC_disc']:.2f} USD/yr")
            st.write(f"- Purchase cost at discount = {d['purchase_disc']:.2f} USD/yr")
            st.write(f"- **Total annual cost (discount)** = {d['total_disc']:.2f} USD/yr")
            st.write(f"- **Annual savings** = {d['annual_savings']:.2f} USD/yr")
            if d['accept']:
                st.success("✅ Accept the discount — total annual cost is LOWER than base.")
            else:
                st.warning("❌ Do NOT accept the discount — total annual cost is HIGHER than base.")

        st.markdown("---")
        st.subheader("EOQ cost curve (ordering + holding)")
        Q_star = res["EOQ"]
        q_max = max(100, int(Q_star * 4))
        Qs = list(range(1, q_max + 1))
        costs = [(D * S / q) + (q * res["h"] / 2.0) for q in Qs]

        fig = plt.figure()
        plt.plot(Qs, costs)
        plt.axvline(Q_star, linestyle="--")
        if discount_enabled and discount_Q:
            plt.axvline(discount_Q, linestyle=":")
        plt.xlabel("Order quantity Q")
        plt.ylabel("Annual logistics cost (USD)")
        plt.title("Ordering + Holding cost curve")
        st.pyplot(fig)

        # Download results
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

        # CSV version
        df = pd.DataFrame([{
            "EOQ": res['EOQ'], "TLC": res['TLC'], "OrderingCost": res['OrderingCost'],
            "HoldingCost": res['HoldingCost'], "t_months": res['t_months'], "t_days": res['t_days'],
            "ROP": res['ROP'], "purchase_base": res['purchase_base'], "total_base": res['total_base']
        }])
        csv_io = io.StringIO()
        df.to_csv(csv_io, index=False)
        st.download_button("Download results (CSV)", data=csv_io.getvalue(), file_name="supply_chain_results.csv")

    except Exception as e:
        st.error(f"Error during calculation: {e}")
else:
    st.info("Enter inputs in the sidebar and press **Calculate**.")
