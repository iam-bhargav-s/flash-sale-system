import time
from datetime import datetime
from pymongo import MongoClient, ReturnDocument

def buy_good(user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    start_time = time.time()
    
    # ATOMIC CONDITION: Only update if quantity > 0
    result = db.inventory_good.find_one_and_update(
        {"item_id": 1, "quantity": {"$gt": 0}},
        {"$inc": {"quantity": -1}},
        return_document=ReturnDocument.AFTER
    )
    
    latency_ms = (time.time() - start_time) * 1000

    if result:
        # Success path
        db.orders_good.insert_one({
            "user_id": user_id, 
            "timestamp": datetime.now(),
            "latency_ms": latency_ms
        })
    else:
        # --- NEW: WAITLIST HANDLING FOR REJECTIONS ---
        # Find out how many people are already in the waitlist to determine queue number
        current_queue_position = db.orders_waitlist.count_documents({}) + 1
        
        db.orders_waitlist.insert_one({
            "user_id": user_id,
            "timestamp": datetime.now(),
            "queue_number": current_queue_position
        })
        # ---------------------------------------------
        
    client.close()

def buy_bad(user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    start_time = time.time()
    item = db.inventory_bad.find_one({"item_id": 1})
    
    if item and item["quantity"] > 0:
        new_qty = item["quantity"] - 1
        db.inventory_bad.update_one({"item_id": 1}, {"$set": {"quantity": new_qty}})
        
        latency_ms = (time.time() - start_time) * 1000
        
        db.orders_bad.insert_one({
            "user_id": user_id, 
            "timestamp": datetime.now(),
            "latency_ms": latency_ms
        })
    client.close()