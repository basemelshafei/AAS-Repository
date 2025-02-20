from MiR_Data import mir_thread
from KUKA_AAS import kuka_thread
import threading
import time

stop_threads = False

if __name__ == "__main__":
    mir = threading.Thread(target=mir_thread)
    kuka = threading.Thread(target=kuka_thread)

    mir.start()
    kuka.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_threads = True
        mir.join()
        kuka.join()
        print("\nStopped MiR and KUKA data generation threads safely.")
