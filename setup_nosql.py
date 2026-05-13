from pymongo import MongoClient

def setup_database():
    try:
        # 1. Connect to the MongoDB server running in Docker
        client = MongoClient("mongodb://localhost:27017/")
        
        # 2. Access (or create) a database and a collection
        db = client["flash_sale_db"]
        inventory = db["inventory"]

        # 3. Clean start: Delete any existing data
        inventory.delete_many({})

        # 4. Create your 'Document' (The NoSQL version of a Row)
        flash_sale_item = {
            "item_id": 1,
            "name": "Limited Edition Sneakers",
            "quantity": 10  # Only 10 in stock!
        }

        # 5. Insert it
        inventory.insert_one(flash_sale_item)
        
        print("--- NoSQL Setup Complete ---")
        print(f"Inserted: {flash_sale_item['name']} with {flash_sale_item['quantity']} in stock.")
        
    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    setup_database()