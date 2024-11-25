from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection with all required parameters
MONGO_URI = os.getenv('MONGODB_URI')
try:
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        retryWrites=True
    )
    
    # Initialize DB and collection without immediate connection test
    db = client.blockchain_db
    collection = db.transactions
    print("MongoDB client initialized")
    
except Exception as e:
    print(f"Error initializing MongoDB client: {e}")
    raise

@app.get("/")
async def read_root():
    try:
        # Test connection when root endpoint is accessed
        client.admin.command('ping')
        return {"status": "ok", "message": "Server is running and connected to MongoDB"}
    except Exception as e:
        print(f"Connection test failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to database")

@app.get("/transactions")
async def get_transactions():
    try:
        transactions = list(collection.find())
        return {"transactions": [
            {**{k: str(v) if k == '_id' else v for k, v in t.items()}}
            for t in transactions
        ]}
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))