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
    """

    def generate_quest(self, economy_state):
        print(f"🧠 AI Processing: Analyzing Economy State ({economy_state['condition']})...")

        prompt = f"""
        You are the 'Grand Archivist' AI for a fantasy MMORPG.
        The game economy is currently in this state:

        - Condition: {economy_state['condition']} (Severity: {economy_state['severity']}/10)
        - Inflation Rate: {economy_state['inflation']}%

        YOUR TASK:
        Generate a 'World Event Quest' to fix this economic problem.

        OUTPUT FORMAT:
        Return ONLY a raw JSON object with:
        {{
            "title": "Quest Name",
            "flavor_text": "Lore description.",
            "objective": "Mission objective.",
            "reward": "Rewards.",
            "type": "Gold Sink" or "Stimulus"
        }}
        """

        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            return {"error": f"AI Generation Failed: {str(e)}"}

    def save_quest(self, quest_data):
        """
        Saves to BOTH Local File and MongoDB Cloud.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        quest_data["generated_at"] = timestamp

        # --- 1. Save to Local File ---
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'quests'))
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        safe_title = "".join([c if c.isalnum() else "_" for c in quest_data['title']])
        filename = f"{safe_title}_{timestamp}.json"
        full_path = os.path.join(base_path, filename)

        with open(full_path, "w") as f:
            json.dump(quest_data, f, indent=4)
        print(f"💾 LOCAL: Saved to quests/{filename}")

        # --- 2. Save to MongoDB Cloud ---
        if db_collection is not None:
            try:
                # We copy the data so we don't mess up the original dict
                quest_record = quest_data.copy()
                result = db_collection.insert_one(quest_record)
                print(f"☁️ CLOUD: Uploaded to MongoDB (ID: {result.inserted_id})")
            except Exception as e:
                print(f"❌ Cloud Upload Failed: {e}")


# --- TEST HARNESS ---
if __name__ == "__main__":
    # Simulate a Crisis
    mock_economy_data = {
        "condition": "Hyper-Inflation",
        "severity": 9,
        "inflation": 45.2,
        "sentiment": "Panic"
    }

    generator = QuestGenerator()
    quest = generator.generate_quest(mock_economy_data)

    if "error" not in quest:
        print(f"\n✨ GENERATED: {quest['title']}")
        generator.save_quest(quest)
    else:
        print(quest["error"])