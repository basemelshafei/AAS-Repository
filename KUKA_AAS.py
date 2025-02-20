import threading
import time
import random
from db_setup import get_connection
from data_logic import ensure_aas_structure_kuka, store_data_point_kuka
from config import KUKA_SUBMODEL_TEMPLATE

stop_threads = False

def generate_kuka_data():
    """
    Generates simulated data for a KUKA robotic arm.
    """
    return {
        "serial_number": "SN-KUKA1234",
        "robot_name": "KUKA-ARM-01",
        "battery_state": random.choice(["Charging", "Discharging", "Full"]),
        "robot_runtime": random.randint(0, 10000),
        "velocity": round(random.uniform(0, 2), 2),
        "acceleration": round(random.uniform(0, 5), 2),
        "load": round(random.uniform(0, 50), 2),
        "position": f"X:{round(random.uniform(0, 100), 2)} Y:{round(random.uniform(0, 100), 2)} Z:{round(random.uniform(0, 100), 2)}",
        "tool_status": random.choice(["Active", "Idle", "Error"]),
        "orientation": f"Yaw:{round(random.uniform(0, 360), 2)} Pitch:{round(random.uniform(-180, 180), 2)} Roll:{round(random.uniform(-180, 180), 2)}",
        "number_of_missions": random.randint(0, 10),
        "timer": f"{random.randint(0, 24)}:{random.randint(0, 59)}:{random.randint(0, 59)}",
        "motion_state": random.choice(["Running", "Stopped"]),
        "distance_to_next": round(random.uniform(0, 20), 2),
        "program_state": random.choice(["Running", "Paused", "Completed"])
    }

def process_kuka_data():
    """
    Collects and stores KUKA data in the AAS database.
    """
    conn = get_connection()
    try:
        # Generate data
        data = generate_kuka_data()

        # Ensure AAS structure exists
        ensure_aas_structure_kuka(conn, data)

        # Store the data point
        store_data_point_kuka(conn, data)
    finally:
        conn.close()

def kuka_thread():
    global stop_threads
    while not stop_threads:
        process_kuka_data()
        time.sleep(2)

if __name__ == "__main__":
    thread = threading.Thread(target=kuka_thread)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_threads = True
        thread.join()
        print("\nKUKA data generation stopped safely.")
