from pymongo import MongoClient, ReturnDocument
from datetime import datetime # <--- Added this for the website timestamp

def attempt_purchase(user_id):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["flash_sale_db"]
        inventory = db["inventory"]
        orders = db["orders"] # <--- Added this to access the orders collection

        # 1. ATOMIC UPDATE
        result = inventory.find_one_and_update(
            {"item_id": 1, "quantity": {"$gt": 0}}, 
            {"$inc": {"quantity": -1}},
            return_document=ReturnDocument.AFTER
        )

        if result is not None:
            # We check if the quantity was 0 or more AFTER our update
            # This ensures only the 10 people who actually changed the DB get an order record
            if result['quantity'] >= 0:
                orders.insert_one({
                    "user_id": user_id,
                    "timestamp": datetime.now()
                })
                print(f"User {user_id}: SUCCESS! | Stock Remaining: {result['quantity']}")
        else:
            print(f"User {user_id}: FAILED. | Stock is 0.")

    except Exception as e:
        print(f"User {user_id}: Error - {e}")
    finally:
        client.close()