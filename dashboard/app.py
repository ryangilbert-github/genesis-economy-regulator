import streamlit as st
import pandas as pd
import time
import sys
import os

# ==========================================
# 0. PROFESSIONAL IMPORTS
# ==========================================
# Add parent directory to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Logic from our professional 'src' folder
from src.economy import Economy
from src.central_bank import CentralBankAI

# ==========================================
# 1. THE DASHBOARD UI
# ==========================================
st.set_page_config(page_title="Genesis Economy AI", layout="wide")

st.title("💰 Genesis Module 1: AI Central Banker")
st.markdown("""
**System Architecture:** Control Theory & Feedback Loops.
Compare different AI Models (Strategies) to see how they handle economic stress.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Choose Your AI")
ai_strategy = st.sidebar.selectbox(
    "AI Model Strategy",
    ("⚖️ Balanced (Standard)", "🦅 The Hawk (Aggressive)", "🕊️ The Dove (Conservative)", "🙈 Laissez-Faire (No AI)")
)

# Dynamic Description based on selection
if "Laissez" in ai_strategy:
    st.sidebar.warning("⚠️ No Regulation. Inflation will likely spiral.")
elif "Hawk" in ai_strategy:
    st.sidebar.success("🦅 Aggressive. Will tax heavily at the slightest sign of trouble.")
elif "Dove" in ai_strategy:
    st.sidebar.info("🕊️ Passive. Will let inflation run hot before acting.")
else:
    st.sidebar.success("⚖️ Balanced. A mix of reaction speed and stability.")

st.sidebar.header("2. Simulation Settings")
simulation_days = st.sidebar.slider("Duration (Days)", 100, 500, 365)

st.sidebar.header("3. Stress Tests")

# A. The Gold Rush (Trend Event)
st.sidebar.subheader("🌊 Gold Rush (Trend)")
gold_rush_active = st.sidebar.checkbox("Trigger Gold Rush")
if gold_rush_active:
    gold_rush_start = st.sidebar.slider("Start Day", 50, 200, 100)
    gold_rush_intensity = st.sidebar.slider("Intensity (x Normal Income)", 2.0, 10.0, 5.0)
else:
    gold_rush_start = 0
    gold_rush_intensity = 1.0

# B. The Whale Deposit (Impulse Event)
st.sidebar.subheader("🐳 Whale Deposit (Impulse)")
whale_active = st.sidebar.checkbox("Trigger Whale Deposit")
if whale_active:
    whale_day = st.sidebar.slider("Drop Day", 50, 250, 150)
    whale_amount = st.sidebar.number_input("Amount (Gold)", 500000, 10000000, 2000000)
else:
    whale_day = -1
    whale_amount = 0

st.sidebar.markdown("---")
run_btn = st.sidebar.button("📉 Run Simulation", type="primary")

# --- MAIN EXECUTION ---
if run_btn:
    # 1. Initialize Objects
    world = Economy()
    ai = CentralBankAI(ai_strategy)

    # 2. Data Containers
    history = []
    progress_bar = st.progress(0)

    # 3. Layout: Two Columns for Charts
    col1, col2 = st.columns(2)
    chart1 = col1.empty()
    chart2 = col2.empty()

    # 4. Simulation Loop
    for day in range(simulation_days):

        # A. DAILY INCOME (The Faucet)
        daily_print = 10000

        # Apply Gold Rush Multiplier
        if gold_rush_active and (gold_rush_start <= day <= gold_rush_start + 60):
            daily_print = daily_print * gold_rush_intensity

        world.inject_money(daily_print)

        # Apply Whale Event
        if whale_active and day == whale_day:
            world.inject_money(whale_amount)
            st.toast(f"💸 DAY {day}: WHALE DEPOSIT DETECTED! +{whale_amount:,} Gold")

        # B. PLAYER TRADING
        # 20% of money moves hands every day
        trade_volume = world.money_supply * 0.20
        world.transaction(trade_volume)

        # C. AI DECISION
        new_tax = ai.decide_policy(world)

        # D. RECORD DATA
        history.append({
            "Day": day,
            "Total Money Supply": world.money_supply,
            "Target Baseline": world.inflation_target,
            "Tax Rate": world.tax_rate
        })

        # E. VISUALIZE (Every 5 frames to speed up rendering)
        if day % 5 == 0:
            df = pd.DataFrame(history)

            with chart1:
                # Plot Money vs Target
                st.subheader(f"Inflation Monitor")
                st.line_chart(
                    df.set_index("Day")[["Total Money Supply", "Target Baseline"]],
                    color=["#FF4B4B", "#00FF00"]  # Red vs Green
                )

            with chart2:
                # Plot Tax Rate
                st.subheader(f"AI Tax Policy")
                st.line_chart(
                    df.set_index("Day")["Tax Rate"],
                    color=["#FF00FF"]  # Magenta
                )

            progress_bar.progress((day + 1) / simulation_days)
            time.sleep(0.005)  # Tiny delay for smooth animation

    # --- FINAL REPORT ---
    st.success("Simulation Complete.")

    # CSV Download
    df_final = pd.DataFrame(history)
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download Report (CSV)",
        data=csv,
        file_name='genesis_economy_report.csv',
        mime='text/csv',
    )

    # Final Score
    final_money = history[-1]["Total Money Supply"]
    if final_money < world.inflation_target * 1.5:
        st.success(f"✅ AI SUCCESS: {ai_strategy} stabilized the economy.")
    else:
        st.error(f"⚠️ AI FAILURE: {ai_strategy} failed to contain inflation.")

else:
    st.info("👈 Select an AI Strategy and Stress Tests, then click 'Run Simulation'.")