import streamlit as st
import time
import pandas as pd
import json
import sys
import os

# --- PATH SETUP ---
# This ensures we can import from the 'src' folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.economy import Economy
from src.quest_generator import QuestGenerator

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Genesis GM Dashboard", 
    layout="wide", 
    page_icon="🐉",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .reportview-container { background: #0f172a; }
    .sidebar .sidebar-content { background: #1e293b; }
    h1, h2, h3 { color: #8b5cf6; }
    .stMetric { background-color: #1e293b; padding: 10px; border-radius: 10px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🐉 Genesis Module 2: The Neural Bridge")
st.markdown("""
**System Status:** `ONLINE` | **Persistence:** `MONGODB ATLAS` | **AI Model:** `GEMINI 1.5 FLASH`  
This dashboard visualizes the **Backend Logic**. It connects the **Economic Simulation (Mod 1)** with the **AI Quest Engine (Mod 2)**.
""")

# --- SIDEBAR: GOD POWERS ---
st.sidebar.header("⚡ Game Master Controls")
st.sidebar.info("Use these tools to force the simulation into specific states for testing.")

force_crisis = st.sidebar.checkbox("Force Economic Crisis", value=True)
crisis_type = st.sidebar.selectbox(
    "Crisis Scenario", 
    ["Hyper-Inflation", "Deflationary Spiral", "Resource Famine", "Trade War"]
)

severity_slider = st.sidebar.slider("Crisis Severity", 1, 10, 9)

st.sidebar.markdown("---")

# --- MAIN EXECUTION ---
if st.sidebar.button("▶ Run Simulation Cycle", type="primary"):
    
    # 1. VISUALIZE THE ECONOMY
    st.subheader("1. Economic Telemetry (Real-Time)")
    col1, col2, col3 = st.columns(3)
    
    # Simulate Economy Logic (Using your actual class)
    economy = Economy(start_money=150_000_000)
    
    with st.spinner("Calculating GDP & Money Supply..."):
        time.sleep(0.8) # Cinematic delay
        stats = economy.update_economy()
        
        # Override stats if "Force Crisis" is on (For Demo Purposes)
        if force_crisis:
            if crisis_type == "Hyper-Inflation":
                stats['inflation_rate'] = 15.5
                delta_color = "inverse" # Red is bad
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

    # Display Metrics
    col1.metric("Global Gold Supply", f"{stats['money_supply']:,} G", delta=f"{stats['inflation_rate']}% Inflation", delta_color="inverse")
    col2.metric("Transaction Tax", f"{stats['tax_rate']*100:.1f}%", "Auto-Adjusted")
    col3.metric("World Condition", stats['condition'].upper(), f"Severity: {severity}/10")

    # 2. VISUALIZE THE AI RESPONSE
    st.markdown("---")
    st.subheader("2. The Grand Archivist (Generative AI)")
    
    ai_col_1, ai_col_2 = st.columns([1, 2])
    
    with ai_col_1:
        st.info("The AI monitors the telemetry above. If severity > 5, it generates a Quest to fix the economy.")
        
    with ai_col_2:
        if severity > 3:
            with st.spinner(f"✨ AI Detected {crisis_type}! Generative models engaging..."):
                # Call your actual AI Class
                quest_bot = QuestGenerator()
                
                # Mock state for the AI prompt
                state = {
                    "condition": crisis_type,
                    "severity": severity,
                    "inflation": stats['inflation_rate'],
                    "sentiment": "Panic" if severity > 7 else "Concern"
                }
                
                # Generate Real AI Quest
                quest = quest_bot.generate_quest(state)
                
                if "error" not in quest:
                    # Success UI
                    st.success("✨ QUEST GENERATED & SAVED TO MONGODB")
                    
                    # Quest Card UI
                    with st.container():
                        st.markdown(f"### 📜 **{quest.get('title', 'Unknown Quest')}**")
                        st.markdown(f"> *{quest.get('flavor_text', 'No lore provided.')}*")
                        st.write(f"**🎯 Objective:** {quest.get('objective', 'None')}")
                        st.write(f"**💰 Reward:** {quest.get('reward', 'None')}")
                        st.caption(f"Quest Type: {quest.get('type', 'Standard')}")
                    
                    # Show the Raw JSON (Proof of Backend)
                    with st.expander("🔍 View Raw JSON Payload (API Output)"):
                        st.json(quest)
                else:
                    st.error(f"AI Generation Failed: {quest['error']}")
                    st.caption("Check your .env file for GOOGLE_API_KEY")
        else:
            st.success("System Stable. The Archivist remains dormant.")

# --- PERSISTENCE VIEW ---
st.markdown("---")
st.subheader("💾 Cloud Persistence Layer (MongoDB Feed)")
st.caption("This table visualizes the JSON documents currently stored in your MongoDB Atlas cluster.")

# Mock Data for Visual Demo (Until you connect real DB read function)
mock_db_data = [
    {"_id": "65cd...a1", "timestamp": "Live", "type": crisis_type if force_crisis else "Stable", "quest": "Pending...", "status": "Processing"},
    {"_id": "65cd...b2", "timestamp": "10 mins ago", "type": "Hyper-Inflation", "quest": "The Gold Hoarders", "status": "Active"},
    {"_id": "65cd...c3", "timestamp": "1 hour ago", "type": "Deflation", "quest": "Minting Crisis", "status": "Resolved"},
]
st.table(pd.DataFrame(mock_db_data))