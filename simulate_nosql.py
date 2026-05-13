import threading
from transaction_nosql import attempt_purchase

if __name__ == "__main__":
    print("!!! THE FLASH SALE IS STARTING NOW !!!")
    
    threads = []
    
    # Create 100 users
    for i in range(50):
        t = threading.Thread(target=attempt_purchase, args=(i,))
        threads.append(t)

    # Launch them all at once
    for t in threads:
        t.start()

    # Wait for the sale to finish
    for t in threads:
        t.join()

    print("\nSale Over.")