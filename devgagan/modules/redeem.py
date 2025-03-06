import random
import string
import pymongo
import os
from pyrogram import Client, filters
from dotenv import load_dotenv

# .env फाइल से कॉन्फ़िग लोड करें
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB कनेक्शन सेटअप
client = pymongo.MongoClient(MONGO_URI)
db = client["telegram_bot"]
redeem_codes_collection = db["redeem_codes"]
premium_users_collection = db["premium_users"]

# ✅ Owner ID सेट करें (आपका ID: 7792539085)
OWNER_ID = 7792539085

# ✅ Redeem Code जनरेट करने वाला फंक्शन
def generate_redeem_code(length=6):
    """अल्फान्यूमेरिक रिडीम कोड जनरेट करें"""
    characters = string.ascii_uppercase + string.digits  # A-Z और 0-9
    return ''.join(random.choices(characters, k=length))

# ✅ /redeem कमांड
@Client.on_message(filters.command("redeem") & filters.private)
def redeem_code(client, message):
    user_id = message.from_user.id
    command_parts = message.text.split(" ")

    if len(command_parts) < 2:
        message.reply_text("⚠️ कृपया सही फ़ॉर्मेट में कोड दर्ज करें: `/redeem YOURCODE`")
        return

    redeem_code = command_parts[1]

    # MongoDB में कोड खोजें
    code_data = redeem_codes_collection.find_one({"code": redeem_code})

    if not code_data:
        message.reply_text("❌ यह कोड अमान्य है या पहले ही उपयोग किया जा चुका है।")
        return

    # यूज़र को प्रीमियम लिस्ट में जोड़ें
    premium_users_collection.insert_one({"user_id": user_id, "redeemed_code": redeem_code})

    # उपयोग किए गए कोड को हटाएं
    redeem_codes_collection.delete_one({"code": redeem_code})

    message.reply_text("✅ आपका कोड सफलतापूर्वक रिडीम हो गया! अब आप प्रीमियम सुविधाओं का आनंद ले सकते हैं।")

# ✅ /generate_code (सिर्फ OWNER के लिए)
@Client.on_message(filters.command("generate_code") & filters.user(OWNER_ID))
def generate_code_command(client, message):
    new_code = generate_redeem_code()
    
    # MongoDB में कोड सेव करें
    redeem_codes_collection.insert_one({"code": new_code})
    
    message.reply_text(f"✅ नया रिडीम कोड बनाया गया: `{new_code}`\n\nइसे अपने यूजर्स को भेजें!")