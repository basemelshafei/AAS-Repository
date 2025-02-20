# data_logic.py

import uuid
import json
from config import MIR_SUBMODEL_TEMPLATE, KUKA_SUBMODEL_TEMPLATE

def ensure_aas_structure_mir(conn, data):
    """
    Ensures the AAS and related submodels/elements exist for a MiR robot.
    """
    _ensure_aas_structure(conn, data, MIR_SUBMODEL_TEMPLATE)


def ensure_aas_structure_kuka(conn, data):
    """
    Ensures the AAS and related submodels/elements exist for a KUKA robot.
    """
    _ensure_aas_structure(conn, data, KUKA_SUBMODEL_TEMPLATE)


def _ensure_aas_structure(conn, data, submodel_template):
    """
    Generic function to ensure the AAS and related submodels/elements exist for a given template.
    """
    aas_id = data["serial_number"]
    aas_name = data["robot_name"]
    aas_description = f"AAS for {aas_name}"

    with conn.cursor() as cur:
        # Ensure AAS exists
        cur.execute("SELECT id FROM aas WHERE id = %s", (aas_id,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO aas (id, name, description) VALUES (%s, %s, %s)",
                (aas_id, aas_name, aas_description)
            )

        # Ensure submodels and submodel_elements
        for submodel_name, keys in submodel_template.items():
            # Check if submodel for this AAS and title exists
            cur.execute("SELECT id FROM submodel WHERE aas_id = %s AND title = %s", (aas_id, submodel_name))
            row = cur.fetchone()
            if row is None:
                sm_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO submodel (id, aas_id, title, semantic_id)
                    VALUES (%s, %s, %s, %s)
                """, (sm_id, aas_id, submodel_name, f"http://omnifactory-assets.com/{submodel_name}"))
            else:
                sm_id = row[0]

            # Ensure elements for this submodel
            cur.execute("SELECT key, id FROM submodel_element WHERE submodel_id = %s", (sm_id,))
            existing_keys = {r[0]: r[1] for r in cur.fetchall()}

            for k in keys:
                if k not in existing_keys:
                    elem_uuid = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO submodel_element (id, submodel_id, key, value, value_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (elem_uuid, sm_id, k, None, "string"))

        conn.commit()


def store_data_point_mir(conn, data):
    """
    Stores a data point for a MiR robot.
    """
    _store_data_point(conn, data, MIR_SUBMODEL_TEMPLATE)


def store_data_point_kuka(conn, data):
    """
    Stores a data point for a KUKA robot.
    """
    _store_data_point(conn, data, KUKA_SUBMODEL_TEMPLATE)


def _store_data_point(conn, data, submodel_template):
    """
    Generic function to store a data point for a given template.
    """
    aas_id = data["serial_number"]

    with conn.cursor() as cur:
        for submodel_name, keys in submodel_template.items():
            # Find the submodel_id for this AAS and submodel_name
            cur.execute("SELECT id FROM submodel WHERE aas_id = %s AND title = %s", (aas_id, submodel_name))
            row = cur.fetchone()
            if not row:
                continue
            sm_id = row[0]

            # Get current elements
            cur.execute("SELECT key, id FROM submodel_element WHERE submodel_id = %s", (sm_id,))
            key_to_id = {r[0]: r[1] for r in cur.fetchall()}

            for k in keys:
                if k in data:
                    v = data[k]
                    value_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                    elem_id = key_to_id[k]

                    hist_id = str(uuid.uuid4())
                    # Insert history
                    cur.execute("""
                        INSERT INTO submodel_element_history (id, submodel_element_id, value, recorded_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (hist_id, elem_id, value_str))

                    # Update current value
                    cur.execute("UPDATE submodel_element SET value = %s WHERE id = %s", (value_str, elem_id))

        conn.commit()
