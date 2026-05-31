from pymongo import MongoClient, ReturnDocument
from datetime import datetime

# --- SYSTEM WITH CONCURRENCY CONTROL (ATOMIC) ---
def buy_good(user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    # ATOMIC: Check and Update happen in ONE step inside the DB
    result = db.inventory_good.find_one_and_update(
        {"item_id": 1, "quantity": {"$gt": 0}},
        {"$inc": {"quantity": -1}},
        return_document=ReturnDocument.AFTER
    )
    if result:
        db.orders_good.insert_one({"user_id": user_id, "timestamp": datetime.now()})
    client.close()

# --- SYSTEM WITHOUT CONCURRENCY CONTROL (RACE CONDITION) ---
def buy_bad(user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    # NON-ATOMIC: Step 1: Read
    item = db.inventory_bad.find_one({"item_id": 1})
    
    # Step 2: Python checks the value (This is where the race condition happens!)
    if item["quantity"] > 0:
        new_qty = item["quantity"] - 1
        # Step 3: Update
        db.inventory_bad.update_one({"item_id": 1}, {"$set": {"quantity": new_qty}})
        db.orders_bad.insert_one({"user_id": user_id, "timestamp": datetime.now()})
    client.close()