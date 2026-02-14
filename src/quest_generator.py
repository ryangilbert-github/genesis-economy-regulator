import os
import json
import time
import certifi
from google import genai
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Load Secrets
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# 2. Configure Gemini AI
if not api_key:
    raise ValueError("❌ API Key not found!")
client = genai.Client(api_key=api_key)

# 3. Configure MongoDB (The Cloud Brain)
if not mongo_uri:
    print("⚠️ MongoDB URI not found in .env. Cloud saving disabled.")
    db_collection = None
else:
    try:
        # ca=certifi.where() fixes SSL errors on some machines
        mongo_client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
        db = mongo_client["genesis_economy"]  # Database Name
        db_collection = db["quests"]  # Collection (Folder) Name
        print("✅ Connected to MongoDB Cloud!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        db_collection = None


class QuestGenerator:
    """
    The Creative Brain.
    Generates quests and saves them to Local Disk AND Cloud Database.
    Implements 'Model Cascading' to ensure 100% uptime.
    """

    def generate_quest(self, economy_state):
        print(f"🧠 AI Processing: Analyzing Economy State ({economy_state['condition']})...")

        # --- CONTEXT INJECTION (The Math Fix) ---
        # We calculate a "Sensible Target" so the AI doesn't hallucinate 100 Billion Gold
        total_money = economy_state.get('money_supply', 1000000)  # Default to 1M if missing
        target_sink = int(total_money * 0.15)  # Target 15% removal

        prompt = f"""
        You are the 'Grand Archivist' AI for a fantasy MMORPG.
        The game economy is currently in this state:

        - Global Money Supply: {total_money:,} Gold
        - Condition: {economy_state['condition']} (Severity: {economy_state['severity']}/10)
        - Inflation Rate: {economy_state['inflation']}%

        YOUR TASK:
        Generate a 'World Event Quest' to fix this economic problem.

        MATH RULES:
        - If this is a GOLD SINK (Inflation), the objective must require players to collectively contribute roughly {target_sink:,} Gold (approx 15% of supply).
        - DO NOT ask for more gold than exists in the Global Money Supply.
        - If this is a STIMULUS (Deflation), rewards should inject roughly {target_sink:,} Gold.

        OUTPUT FORMAT:
        Return ONLY a raw JSON object with:
        {{
            "title": "Quest Name",
            "flavor_text": "Lore description.",
            "objective": "Mission objective (mentioning approx {target_sink:,} Gold).",
            "reward": "Rewards.",
            "type": "Gold Sink" or "Stimulus"
        }}
        """

        # --- MODEL CASCADE ARCHITECTURE ---
        # We try these models in order based on your "check_models.py" results
        models_to_try = [
            'gemini-2.0-flash',  # 1. Primary
            'gemini-2.0-flash-lite',  # 2. Backup
            'gemini-flash-latest'  # 3. Safety Net
        ]

        for model_name in models_to_try:
            try:
                print(f"🤖 Attempting generation with model: {model_name}...")

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                # If we get here, it worked! Clean and return.
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                quest_data = json.loads(clean_json)

                # --- SUCCESS: SAVE IT IMMEDIATELY ---
                self.save_quest(quest_data)
                return quest_data

            except Exception as e:
                # If error is 503 (Server Overload) or 429 (Rate Limit), continue to next model
                if "503" in str(e) or "429" in str(e):
                    print(f"⚠️ {model_name} is busy/rate-limited. Falling back...")
                    time.sleep(1)  # Short pause before switching models
                    continue
                elif "404" in str(e):
                    print(f"❌ {model_name} not found. Skipping...")
                    continue
                else:
                    # If it's a real error (like Auth), print it but keep trying other models
                    print(f"❌ Error with {model_name}: {e}")
                    continue

        # --- FALLBACK PROTOCOL (If ALL models fail) ---
        print("❌ ALL AI MODELS OFFLINE. Engaging Emergency Protocol.")
        timestamp = time.strftime("%H:%M:%S")

        fallback_quest = {
            "title": "⚠️ Emergency Protocol: The Silent Aether",
            "flavor_text": f"The Grand Archivist is temporarily severed from the Neural Cloud at {timestamp}. Automated failsafe protocols have been initiated.",
            "objective": "Deposit 1,000 Gold into the Void Bank immediately.",
            "reward": "System Stability Token",
            "type": "Fallback Mechanism",
            "generated_at": time.strftime("%Y%m%d-%H%M%S")
        }

        self.save_quest(fallback_quest)
        return fallback_quest

    def save_quest(self, quest_data):
        """
        Saves to BOTH Local File and MongoDB Cloud.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        # Ensure timestamp is in the data
        if "generated_at" not in quest_data:
            quest_data["generated_at"] = timestamp

        # --- 1. Save to Local File ---
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'quests'))
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Sanitize filename
        safe_title = "".join([c if c.isalnum() else "_" for c in quest_data['title']])
        filename = f"{safe_title}_{timestamp}.json"
        full_path = os.path.join(base_path, filename)

        with open(full_path, "w") as f:
            json.dump(quest_data, f, indent=4)
        print(f"💾 LOCAL: Saved to quests/{filename}")

        # --- 2. Save to MongoDB Cloud ---
        if db_collection is not None:
            try:
                quest_record = quest_data.copy()
                result = db_collection.insert_one(quest_record)
                print(f"☁️ CLOUD: Uploaded to MongoDB (ID: {result.inserted_id})")
            except Exception as e:
                print(f"❌ Cloud Upload Failed: {e}")


if __name__ == "__main__":
    # Test Run
    gen = QuestGenerator()
    print(gen.generate_quest({"condition": "Test", "severity": 5, "inflation": 10}))