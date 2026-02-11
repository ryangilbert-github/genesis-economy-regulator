import os
import json
import time
from google import genai
from dotenv import load_dotenv

# 1. Load the Secret Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ API Key not found! Did you create the .env file?")

# 2. Configure the Client
client = genai.Client(api_key=api_key)


class QuestGenerator:
    """
    The Creative Brain.
    Takes raw economic numbers and turns them into playable content.
    """

    def generate_quest(self, economy_state):
        """
        Input: A dictionary of economy data (Inflation, Tax Rate, etc.)
        Output: A JSON string containing the Quest details.
        """
        print(f"🧠 AI Processing: Analyzing Economy State ({economy_state['condition']})...")

        # --- THE PROMPT ENGINEERING ---
        prompt = f"""
        You are the 'Grand Archivist' AI for a fantasy MMORPG.
        The game economy is currently in this state:

        - Condition: {economy_state['condition']} (Severity: {economy_state['severity']}/10)
        - Inflation Rate: {economy_state['inflation']}%
        - Player Sentiment: {economy_state['sentiment']}

        YOUR TASK:
        Generate a 'World Event Quest' to fix this economic problem.

        LOGIC:
        - If Inflation is HIGH -> Create a "Gold Sink" (e.g., Donate Gold, Buy Expensive Items).
        - If Inflation is LOW (Deflation) -> Create a "Stimulus" (e.g., Loot drops increased, King gives gold).

        OUTPUT FORMAT:
        Return ONLY a raw JSON object (no markdown, no extra text) with these fields:
        {{
            "title": "Quest Name",
            "flavor_text": "Lore description of why this is happening.",
            "objective": "What players must do (e.g., 'Donate 500g').",
            "reward": "What they get (e.g., 'Title: The Philanthropist').",
            "type": "Gold Sink" or "Stimulus"
        }}
        """

        # 3. Generate Content
        try:
            # Using the stable alias to ensure free tier access
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )

            # Clean up potential markdown formatting
            raw_text = response.text
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()

            return json.loads(clean_json)
        except Exception as e:
            return {"error": f"AI Generation Failed: {str(e)}"}

    def save_quest_to_file(self, quest_data):
        """
        Saves the quest to a JSON file AND updates the Master Library.
        """
        # 1. Define Paths (Go up one level from 'src' to root)
        # This ensures it saves in genesis-economy-regulator/quests
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'quests'))

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # 2. Sanitize Title for Filename (e.g. "The Great Coin Melt" -> "The_Great_Coin_Melt")
        safe_title = "".join([c if c.isalnum() else "_" for c in quest_data['title']])
        safe_title = safe_title.replace("__", "_").strip("_")  # Clean up messy underscores

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{safe_title}_{timestamp}.json"
        full_path = os.path.join(base_path, filename)

        # 3. Save the Individual Quest File
        with open(full_path, "w") as f:
            json.dump(quest_data, f, indent=4)

        print(f"💾 SAVED: {filename}")

        # 4. Update the Master Library (Catalog)
        library_path = os.path.join(base_path, "_quest_library.json")
        library_data = []

        # Load existing library if it exists
        if os.path.exists(library_path):
            try:
                with open(library_path, "r") as lib_file:
                    library_data = json.load(lib_file)
            except json.JSONDecodeError:
                library_data = []  # Start fresh if corrupted

        # Add new quest summary to the list
        summary = {
            "id": timestamp,
            "filename": filename,
            "title": quest_data['title'],
            "type": quest_data['type'],
            "objective": quest_data['objective'],
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        library_data.append(summary)

        # Save the updated library
        with open(library_path, "w") as lib_file:
            json.dump(library_data, lib_file, indent=4)

        print(f"📚 CATALOG UPDATED: Added to {library_path}")


# --- TEST HARNESS ---
if __name__ == "__main__":
    # Simulate a "Crisis"
    mock_economy_data = {
        "condition": "Hyper-Inflation",
        "severity": 9,
        "inflation": 45.2,
        "sentiment": "Angry"
    }

    generator = QuestGenerator()
    quest = generator.generate_quest(mock_economy_data)

    # Print AND Save
    if "error" not in quest:
        print("\n✨ NEW QUEST GENERATED:")
        print(json.dumps(quest, indent=4))
        generator.save_quest_to_file(quest)
    else:
        print(quest["error"])