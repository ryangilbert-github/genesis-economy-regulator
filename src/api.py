import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- FIXED TYPO
from pymongo import MongoClient
import certifi  # Added for SSL stability

# --- SECURE PATHING ---
# This ensures we find the .env file in the root folder, even if we run from /src
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'

# Use override=True to make sure it refreshes the variables in your terminal session
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI()

# --- SECURITY: CORS ---
# Allows your Frontend (React/Streamlit) to talk to this Python Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE CONNECTION ---
uri = os.getenv("MONGODB_URI")

print(f"🔍 DEBUG: Looking for .env at: {env_path}")
print(f"🔍 DEBUG: Does file exist? {env_path.exists()}")

if not uri:
    print("❌ ERROR: MONGODB_URI not found! Check your .env file.")
    client = None
    collection = None
else:
    try:
        # Added certifi for SSL safety
        client = MongoClient(uri, tlsCAFile=certifi.where())
        print(f"✅ Securely connected to database: {uri[:25]}...")

        # --- CRITICAL FIX: MATCH DASHBOARD DATABASE NAME ---
        db = client["genesis_economy"]  # Changed from 'genesis_db' to match Dashboard
        collection = db["quests"]
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        client = None


# Helper to fix MongoDB's "ObjectId" for the Frontend
def format_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


# --- ROUTES ---

@app.get("/")
async def root():
    return {"status": "Genesis System Online"}


@app.get("/current-quest")
async def get_quest():
    """Fetches the latest quest from the cloud database."""
    if collection is None:
        return {"error": "Database not connected"}

    # Sort by _id descending (newest first)
    quest = collection.find_one(sort=[("_id", -1)])
    return format_doc(quest)


@app.post("/run-simulation")
async def run_sim():
    """Triggers the AI simulation engine."""
    try:
        # This imports the logic from your src folder
        from src.main import run_economic_cycle
        result = run_economic_cycle()
        return {"status": "Success", "data": result}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "Error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)