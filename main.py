from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection with SSL settings
MONGO_URI = os.getenv('MONGODB_URI')

try:
    # Initialize MongoDB client with simpler SSL settings
    client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    db = client["blockchain_db"]
    collection = db["transactions"]
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

# Helper function to convert MongoDB document to dict with string ID
def serialize_doc(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Server is running"}

@app.get("/transactions")
async def get_transactions():
    try:
        transactions = list(collection.find())
        return {"transactions": [serialize_doc(txn) for txn in transactions]}
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))