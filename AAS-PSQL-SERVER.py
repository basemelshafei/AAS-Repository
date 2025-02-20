import random
import time
import json
import threading
import uuid
import psycopg2
from psycopg2 import sql

# ---------------- Configuration ----------------
DB_NAME = "aas_db"
DB_USER = "postgres"
DB_PASSWORD = "new_secure_password"
DB_HOST = "localhost"
DB_PORT = 5432

# Multiple submodels with separate UUIDs
OPERATIONAL_SUBMODEL_UUID = str(uuid.uuid4())
NAV_MISSION_SUBMODEL_UUID = str(uuid.uuid4())
CONFIG_SETTINGS_SUBMODEL_UUID = str(uuid.uuid4())

SUBMODELS_DEFINITION = {
    "OperationalData": {
        "uuid": OPERATIONAL_SUBMODEL_UUID,
        "keys": [
            "mode_text",
            "state_text",
            "battery_percentage",
            "battery_time_remaining",
            "velocity",
            "velocityAngular"
        ]
    },
    "NavigationAndMission": {
        "uuid": NAV_MISSION_SUBMODEL_UUID,
        "keys": [
            "mission_queue_id",
            "mission_text",
            "moved",
            "distance_to_next_target",
            "positionX",
            "positionY",
            "orientation"
        ]
    },
    "ConfigurationAndSettings": {
        "uuid": CONFIG_SETTINGS_SUBMODEL_UUID,
        "keys": [
            "joystick_low_speed_mode_enabled",
            "safety_system_muted",
            "unloadedMapChanges"
        ]
    }
}

stop_threads = False
data = {}

def create_tables_if_not_exist(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS aas (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS submodel (
            id UUID PRIMARY KEY,
            aas_id VARCHAR(255) REFERENCES aas(id),
            title VARCHAR(255),
            semantic_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS submodel_element (
            id UUID PRIMARY KEY,
            submodel_id UUID REFERENCES submodel(id),
            key VARCHAR(255),
            value TEXT,
            value_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS submodel_element_history (
            id UUID PRIMARY KEY,
            submodel_element_id UUID REFERENCES submodel_element(id),
            value TEXT,
            recorded_at TIMESTAMP DEFAULT NOW()
        );
        """)

        conn.commit()

def ensure_aas_structure(conn, data):
    """
    Adjusted to use data dictionary:
    - aas_id is data["serial_number"]
    - aas_name is data["robot_name"]
    description remains static.
    """
    with conn.cursor() as cur:
        aas_id = data["serial_number"]
        aas_name = data["robot_name"]
        aas_description = "AAS for MiR robot"

        # Check if AAS exists by this ID
        cur.execute("SELECT id FROM aas WHERE id = %s", (aas_id,))
        if cur.fetchone() is None:
            # Insert AAS record from asset data
            cur.execute(
                "INSERT INTO aas (id, name, description) VALUES (%s, %s, %s)",
                (aas_id, aas_name, aas_description)
            )

        # Ensure each submodel and submodel_element exists
        for submodel_name, info in SUBMODELS_DEFINITION.items():
            sm_id = info["uuid"]
            cur.execute("SELECT id FROM submodel WHERE id = %s", (sm_id,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO submodel (id, aas_id, title, semantic_id) VALUES (%s, %s, %s, %s)",
                            (sm_id, aas_id, submodel_name, f"http://example.com/{submodel_name}"))

            # Check existing elements
            existing_keys = {}
            cur.execute("SELECT key, id FROM submodel_element WHERE submodel_id = %s", (sm_id,))
            for row in cur.fetchall():
                existing_keys[row[0]] = row[1]

            # Insert submodel_elements for keys if missing
            for k in info["keys"]:
                if k not in existing_keys:
                    elem_uuid = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO submodel_element (id, submodel_id, key, value, value_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (elem_uuid, sm_id, k, None, "string"))

        conn.commit()

def store_data_point(conn, data):
    """
    For each submodel and key, insert into history and update current value.
    """
    with conn.cursor() as cur:
        for submodel_name, info in SUBMODELS_DEFINITION.items():
            sm_id = info["uuid"]
            cur.execute("SELECT key, id FROM submodel_element WHERE submodel_id = %s", (sm_id,))
            key_to_id = {row[0]: row[1] for row in cur.fetchall()}

            for k in info["keys"]:
                if k not in data:
                    continue
                v = data[k]
                if isinstance(v, (dict, list)):
                    value_str = json.dumps(v)
                else:
                    value_str = str(v)

                elem_id = key_to_id.get(k)
                if elem_id:
                    hist_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO submodel_element_history (id, submodel_element_id, value, recorded_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (hist_id, elem_id, value_str))

                    cur.execute("""
                        UPDATE submodel_element SET value = %s WHERE id = %s
                    """, (value_str, elem_id))

        conn.commit()

def generate_random_data():
    d = {
        "joystick_low_speed_mode_enabled": random.choice([True, False]),
        "mission_queue_url": "http://example.com/mission_queue",
        "mode_id": random.randint(1, 10),
        "moved": random.randint(0, 1000),
        "mission_queue_id": random.randint(1, 100),
        "robot_name": f"Robot-60",
        "joystick_web_session_id": f"Session-{random.randint(1, 100)}",
        "uptime": random.randint(0, 10000),
        "errors": random.choice([[], ["Error 1", "Error 2"]]),
        "unloaded_map_changes": random.randint(0, 5),
        "distance_to_next_target": round(random.uniform(0, 10), 2),
        "serial_number": f"SN-8888",
        "mode_key_state": random.choice(["STATE1", "STATE2"]),
        "battery_percentage": round(random.uniform(0, 100), 2),
        "map_id": random.randint(1, 10),
        "safety_system_muted": random.choice([True, False]),
        "mission_text": "Mission in progress",
        "state_text": "Active",
        "velocity": round(random.uniform(0, 2), 2),
        "footprint": "Normal",
        "user_prompt": "No prompt",
        "allowed_methods": ["GET", "POST"],
        "robot_model": "MiR100",
        "mode_text": "Operational",
        "session_id": f"Session-{random.randint(100, 999)}",
        "state_id": random.randint(1, 5),
        "battery_time_remaining": random.randint(0, 120),
        "position": {"x": round(random.uniform(0, 100), 2), "y": round(random.uniform(0, 100), 2)}
    }

    # Add constants and derived fields for submodels
    d["velocityAngular"] = 0.0
    d["orientation"] = 0.0
    d["positionX"] = d["position"]["x"]
    d["positionY"] = d["position"]["y"]
    d["unloadedMapChanges"] = bool(d["unloaded_map_changes"])

    return d

def simulated_data():
    global data, stop_threads
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    create_tables_if_not_exist(conn)

    # Generate initial data
    data = generate_random_data()
    # Now ensure AAS structure with the current data
    ensure_aas_structure(conn, data)
    # Store initial data point
    store_data_point(conn, data)
    print("Data:", data)

    while not stop_threads:
        data = generate_random_data()
        store_data_point(conn, data)
        print("Data:", data)
        time.sleep(2)

    conn.close()

def structured_data():
    global stop_threads, data
    while not stop_threads:
        aas_data = {
            "AssetAdministrationShell": {
                "identification": {
                    "idShort": data.get("robot_name", "Unknown"),
                    "id": data.get("serial_number", "Unknown"),
                    "model": data.get("robot_model", "Unknown")
                },
                "submodels": [
                    {
                        "idShort": "OperationalData",
                        "values": {
                            "mode": data.get("mode_text"),
                            "state": data.get("state_text"),
                            "batteryPercentage": data.get("battery_percentage"),
                            "batteryTimeRemaining": data.get("battery_time_remaining"),
                            "velocityLinear": data.get("velocity"),
                            "velocityAngular": data.get("velocityAngular", 0.0)
                        }
                    },
                    {
                        "idShort": "NavigationAndMission",
                        "values": {
                            "missionQueueId": data.get("mission_queue_id"),
                            "missionText": data.get("mission_text"),
                            "moved": data.get("moved"),
                            "distanceToNextTarget": data.get("distance_to_next_target"),
                            "positionX": data.get("positionX", 0.0),
                            "positionY": data.get("positionY", 0.0),
                            "orientation": data.get("orientation", 0.0)
                        }
                    },
                    {
                        "idShort": "ConfigurationAndSettings",
                        "values": {
                            "joystickLowSpeedModeEnabled": data.get("joystick_low_speed_mode_enabled"),
                            "safetySystemMuted": data.get("safety_system_muted"),
                            "unloadedMapChanges": data.get("unloadedMapChanges")
                        }
                    }
                ]
            }
        }
        #print("AAS Data:", json.dumps(aas_data, indent=4))
        time.sleep(2)

# Create and start threads for each function
thread1 = threading.Thread(target=simulated_data)
thread2 = threading.Thread(target=structured_data)

thread1.start()
thread2.start()

# Run until interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_threads = True
    thread1.join()
    thread2.join()
    print("\nProgram interrupted and stopped safely.")
