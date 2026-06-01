from pymongo import MongoClient

def setup_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flash_sale_db"]

    db["inventory_good"].drop()
    db["inventory_bad"].drop()
    db["orders_good"].drop()
    db["orders_bad"].drop()
    db["orders_waitlist"].drop() 

    db["inventory_good"].insert_one({"item_id": 1, "quantity": 10})
    db["inventory_bad"].insert_one({"item_id": 1, "quantity": 10})
    
    print("Database Reset: Ready for Comparison + Waitlist Test.")

if __name__ == "__main__":
    setup_database()