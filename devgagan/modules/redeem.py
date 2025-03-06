from datetime import datetime, timedelta
import random
import string
from pymongo import MongoClient
from config import MONGO_URL

# MongoDB कनेक्शन सेटअप करें
client = MongoClient(MONGO_URL)
db = client["telegram_bot"]  # अपना डेटाबेस नाम यहाँ डालें
codes_collection = db["redeem_codes"]

def generate_code(expiry: str = None):
    """नया रिडीम कोड बनाएं और MongoDB में सेव करें"""
    
    # 6-अंकों का रैंडम कोड बनाएं
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Expiry Time सेट करें
    if expiry == "1h":
        expiry_time = datetime.utcnow() + timedelta(hours=1)
    elif expiry == "1d":
        expiry_time = datetime.utcnow() + timedelta(days=1)
    else:
        expiry_time = None  # कोई एक्सपायरी नहीं

    # MongoDB में कोड सेव करें
    codes_collection.insert_one({"code": code, "expiry": expiry_time, "redeemed": False})
    
    if expiry_time:
        return f"✅ नया रिडीम कोड: `{code}`\n⏳ एक्सपायरी: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    else:
        return f"✅ नया रिडीम कोड: `{code}`\n🔓 कोई एक्सपायरी नहीं"

def redeem_code(user_id: int, code: str):
    """कोड को रिडीम करें और एक्सपायरी चेक करें"""
    
    # MongoDB से कोड खोजें
    code_data = codes_collection.find_one({"code": code})

    if not code_data:
        return "❌ कोड अमान्य है!"
    
    if code_data["redeemed"]:
        return "❌ यह कोड पहले ही उपयोग किया जा चुका है!"

    if code_data["expiry"] and datetime.utcnow() > code_data["expiry"]:
        # एक्सपायर्ड कोड को डिलीट करें
        codes_collection.delete_one({"code": code})
        return "❌ यह कोड एक्सपायर हो चुका है!"

    # कोड को रिडीम करें
    codes_collection.update_one({"code": code}, {"$set": {"redeemed": True}})
    return "✅ आपका कोड सफलतापूर्वक रिडीम हो गया!"

def delete_expired_codes():
    """एक्सपायरी टाइम के बाद कोड्स को हटाएं"""
    now = datetime.utcnow()
    result = codes_collection.delete_many({"expiry": {"$lt": now}})
    return f"🗑️ {result.deleted_count} एक्सपायर्ड कोड्स डिलीट किए गए!"