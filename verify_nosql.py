from pymongo import MongoClient

def verify_results():
    try:
        # Connect to the database
        client = MongoClient("mongodb://localhost:27017/")
        db = client["flash_sale_db"]
        inventory = db["inventory"]

        # Fetch the item
        item = inventory.find_one({"item_id": 1})

        if item:
            print("\n--- FINAL DATABASE AUDIT ---")
            print(f"Product: {item['name']}")
            print(f"Final Quantity in DB: {item['quantity']}")
            
            if item['quantity'] == 0:
                print("Result: SUCCESS. No overselling occurred.")
            elif item['quantity'] < 0:
                print("Result: FAILURE. Race condition detected (Negative Stock).")
            else:
                print(f"Result: {item['quantity']} items left. Not all items were sold.")
            print("---------------------------\n")
        else:
            print("Error: Item not found in database. Did you run setup_nosql.py?")

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    verify_results()