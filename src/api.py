import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors imppip install pipreqsort CORSMiddleware
from pymongo import MongoClient

# --- SECURE PATHING ---
# This ensures we find the .env file in the root folder, even if we run from /src
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'

# Use override=True to make sure it refreshes the variables in your terminal session
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI()

# --- SECURITY: CORS ---
# Allows your React Frontend (5173) to talk to this Python Backend (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE CONNECTION ---
# Standardized to MONGODB_URI to match your .env file
uri = os.getenv("MONGODB_URI")

print(f"🔍 DEBUG: Looking for .env at: {env_path}")
print(f"🔍 DEBUG: Does file exist? {env_path.exists()}")

if not uri:
    print("❌ ERROR: MONGODB_URI not found! Check the spelling in your .env file.")
else:
    # Safely show the start of the URI to confirm it's loaded
    print(f"✅ Securely connected to database: {uri[:25]}...")

client = MongoClient(uri)
db = client["genesis_db"]
collection = db["quests"]

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
    quest = collection.find_one(sort=[("_id", -1)])
    return format_doc(quest)

@app.post("/run-simulation")
async def run_sim():
    """Triggers the AI simulation engine."""
    try:
        from src.main import run_economic_cycle
        result = run_economic_cycle()
        return {"status": "Success", "data": result}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "Error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)