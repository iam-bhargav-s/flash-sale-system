import threading
from transaction_nosql import buy_good, buy_bad

def run_test(target_func, label):
    print(f"Starting {label} Sale...")
    threads = []
    for i in range(100):
        t = threading.Thread(target=target_func, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    run_test(buy_bad, "UNCONTROLLED (BAD)")
    run_test(buy_good, "CONTROLLED (GOOD)")