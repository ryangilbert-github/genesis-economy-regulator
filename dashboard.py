import streamlit as st
import time
import pandas as pd
import json
import sys
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

# --- PATH SETUP ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.economy import Economy
from src.quest_generator import QuestGenerator

# --- CONFIGURATION ---
load_dotenv()

st.set_page_config(
    page_title="Genesis GM Dashboard",
    layout="wide",
    page_icon="🐉",
    initial_sidebar_state="expanded"
)

# --- HEADER ---
st.title("🐉 Genesis Module 2: The Neural Bridge")
st.markdown("""
**System Status:** `ONLINE` | **Persistence:** `MONGODB ATLAS` | **AI Model:** `GEMINI 1.5 FLASH`  
This dashboard visualizes the **Backend Logic**. It connects the **Economic Simulation (Mod 1)** with the **AI Quest Engine (Mod 2)**.
""")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚡ Game Master Controls")
force_crisis = st.sidebar.checkbox("Force Economic Crisis", value=True)
crisis_type = st.sidebar.selectbox(
    "Crisis Scenario",
    ["Hyper-Inflation", "Deflationary Spiral", "Resource Famine", "Trade War"]
)
severity_slider = st.sidebar.slider("Crisis Severity", 1, 10, 9)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Clear Dashboard"):
    st.rerun()

# --- MAIN EXECUTION ---
if st.sidebar.button("▶ Run Simulation Cycle", type="primary"):

    # 1. VISUALIZE THE ECONOMY
    st.subheader("1. Economic Telemetry (Real-Time)")
    col1, col2, col3 = st.columns(3)

    economy = Economy(start_money=150_000_000)

    with st.spinner("Calculating GDP & Money Supply..."):
        time.sleep(0.5)
        stats = economy.update_economy()

        # Override stats for Demo
        if force_crisis:
            if crisis_type == "Hyper-Inflation":
                stats['inflation_rate'] = 15.5
                delta_color = "inverse"
            elif crisis_type == "Deflationary Spiral":
                stats['inflation_rate'] = -5.2
                delta_color = "inverse"
            else:
                stats['inflation_rate'] = 2.1
                delta_color = "normal"
            stats['condition'] = crisis_type
            severity = severity_slider
        else:
            stats['inflation_rate'] = 2.5
            stats['condition'] = "Stable"
            severity = 0

    col1.metric("Global Gold Supply", f"{stats['money_supply']:,} G", delta=f"{stats['inflation_rate']}% Inflation",
                delta_color="inverse")
    col2.metric("Transaction Tax", f"{stats['tax_rate'] * 100:.1f}%", "Auto-Adjusted")
    col3.metric("World Condition", stats['condition'].upper(), f"Severity: {severity}/10")

    # 2. VISUALIZE THE AI RESPONSE
    st.markdown("---")
    st.subheader("2. The Grand Archivist (Generative AI)")

    ai_col_1, ai_col_2 = st.columns([1, 2])

    with ai_col_1:
        st.info("The AI monitors telemetry. If Severity > 5, it generates a Quest to fix the economy.")

    with ai_col_2:
        if severity > 3:
            with st.spinner(f"✨ AI Detected {crisis_type}! Generative models engaging..."):
                quest_bot = QuestGenerator()

                state = {
                    "condition": crisis_type,
                    "severity": severity,
                    "inflation": stats['inflation_rate'],
                    "money_supply": stats['money_supply'],  # <--- ADD THIS LINE
                    "sentiment": "Panic"
                }

                # Generate Quest
                quest = quest_bot.generate_quest(state)

                if "error" not in quest:
                    # --- CRITICAL FIX: SAVE TO DB ---
                    # quest_bot.save_quest(quest)  # This adds the timestamp!

                    st.success("✨ QUEST GENERATED & SAVED TO MONGODB")

                    # Quest Card UI
                    with st.container():
                        st.markdown(f"### 📜 **{quest.get('title', 'Unknown Quest')}**")
                        st.caption(f"📅 Created At: {quest.get('generated_at', 'Just now')}")
                        st.markdown(f"> *{quest.get('flavor_text', 'No lore provided.')}*")
                        st.write(f"**🎯 Objective:** {quest.get('objective', 'None')}")
                        st.write(f"**💰 Reward:** {quest.get('reward', 'None')}")

                    with st.expander("🔍 View Raw JSON"):
                        st.json(quest)
                else:
                    st.error(f"AI Generation Failed: {quest['error']}")
        else:
            st.success("System Stable. The Archivist remains dormant.")

# --- PERSISTENCE VIEW (REAL DATA) ---
st.markdown("---")
st.subheader("💾 Cloud Persistence Layer (MongoDB Feed)")

col_db_1, col_db_2 = st.columns([4, 1])
with col_db_1:
    st.caption("Live feed of the last 10 generated quests saved to the database.")
with col_db_2:
    if st.button("🔄 Refresh Feed"):
        st.rerun()

mongo_uri = os.getenv("MONGODB_URI")

if not mongo_uri:
    st.error("❌ MONGODB_URI not found in .env file.")
else:
    try:
        client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
        db = client["genesis_economy"]
        collection = db["quests"]

        # Fetch last 10 documents
        cursor = collection.find().sort("_id", -1).limit(10)

        data = []
        for doc in cursor:
            data.append({
                "Timestamp": doc.get("generated_at", "N/A"),  # NEW COLUMN
                "Quest Title": doc.get("title", "Unknown"),
                "Condition": doc.get("type", "N/A"),
                "Objective": doc.get("objective", "N/A")[:60] + "..."
            })

        if data:
            st.table(pd.DataFrame(data))
        else:
            st.info("📭 Database is empty.")

    except Exception as e:
        st.error(f"❌ Database Connection Failed: {e}")