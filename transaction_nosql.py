import time
from datetime import datetime
from pymongo import MongoClient, ReturnDocument

# --- SYSTEM WITH CONCURRENCY CONTROL (ATOMIC) ---
def buy_good(user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    # Start the clock
    start_time = time.time()
    
    # ATOMIC: Check and Update happen in ONE step inside the DB
    result = db.inventory_good.find_one_and_update(
        {"item_id": 1, "quantity": {"$gt": 0}},
        {"$inc": {"quantity": -1}},
        return_document=ReturnDocument.AFTER
    )
    
    # Calculate latency in milliseconds
    latency_ms = (time.time() - start_time) * 1000

    if result:
        db.orders_good.insert_one({
            "user_id": user_id, 
            "timestamp": datetime.now(),
            "latency_ms": latency_ms # Store telemetry
        })
    client.close()

# --- SYSTEM WITHOUT CONCURRENCY CONTROL (RACE CONDITION) ---
def buy_bad(user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]
    
    # Start the clock
    start_time = time.time()
    
    # NON-ATOMIC: Step 1: Read
    item = db.inventory_bad.find_one({"item_id": 1})
    
    if item and item["quantity"] > 0:
        new_qty = item["quantity"] - 1
        # Step 2: Update
        db.inventory_bad.update_one({"item_id": 1}, {"$set": {"quantity": new_qty}})
        
        # Calculate latency in milliseconds
        latency_ms = (time.time() - start_time) * 1000
        
        db.orders_bad.insert_one({
            "user_id": user_id, 
            "timestamp": datetime.now(),
            "latency_ms": latency_ms # Store telemetry
        })
    client.close()