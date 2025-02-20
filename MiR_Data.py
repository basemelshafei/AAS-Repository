import threading
import time
import random
from db_setup import get_connection
from data_logic import ensure_aas_structure_mir, store_data_point_mir
from config import MIR_SUBMODEL_TEMPLATE

stop_threads = False

def generate_mir_data():
    """
    Generates simulated data for a MiR robot.
    """
    return {
        "serial_number": "SN-MIR1234",
        "robot_name": "MiR-100",
        "mode_text": "Operational",
        "state_text": "Active",
        "battery_percentage": round(random.uniform(0, 100), 2),
        "battery_time_remaining": random.randint(0, 120),
        "velocity": round(random.uniform(0, 2), 2),
        "velocityAngular": round(random.uniform(-1, 1), 2),
        "mission_queue_id": random.randint(0, 10),
        "mission_text": "Delivery in progress",
        "moved": random.randint(0, 1000),
        "distance_to_next_target": round(random.uniform(0, 10), 2),
        "positionX": round(random.uniform(0, 100), 2),
        "positionY": round(random.uniform(0, 100), 2),
        "orientation": round(random.uniform(0, 360), 2),
        "joystick_low_speed_mode_enabled": random.choice([True, False]),
        "safety_system_muted": random.choice([True, False]),
        "unloadedMapChanges": random.randint(0, 5)
    }

def process_mir_data():
    """
    Collects and stores MiR data in the AAS database.
    """
    conn = get_connection()
    try:
        # Generate data
        data = generate_mir_data()

        # Ensure AAS structure exists
        ensure_aas_structure_mir(conn, data)

        # Store the data point
        store_data_point_mir(conn, data)
    finally:
        conn.close()

def mir_thread():
    global stop_threads
    while not stop_threads:
        process_mir_data()
        time.sleep(2)

if __name__ == "__main__":
    thread = threading.Thread(target=mir_thread)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_threads = True
        thread.join()
        print("\nMiR data generation stopped safely.")
