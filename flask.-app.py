from flask import Flask, jsonify
from db_setup import get_connection

app = Flask(__name__)

@app.route('/aas/<aas_id>', methods=['GET'])
def get_aas_data(aas_id):
    """
    Fetch details of a specific AAS by its ID, including submodels and their elements.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Fetch AAS basic info
        cur.execute("SELECT id, name, description FROM aas WHERE id = %s", (aas_id,))
        aas_row = cur.fetchone()
        if not aas_row:
            return jsonify({"error": "AAS not found"}), 404

        aas_data = {
            "id": aas_row[0],
            "name": aas_row[1],
            "description": aas_row[2],
            "submodels": []
        }

        # Fetch Submodels for this AAS
        cur.execute("SELECT id, title, semantic_id FROM submodel WHERE aas_id = %s", (aas_id,))
        submodels = cur.fetchall()

        for sm_id, sm_title, sm_semantic_id in submodels:
            # Fetch elements for each submodel
            cur.execute("SELECT key, value FROM submodel_element WHERE submodel_id = %s", (sm_id,))
            elements = cur.fetchall()

            # Convert elements into a dictionary
            elements_dict = {key: value for key, value in elements}

            submodel_data = {
                "id": str(sm_id),
                "title": sm_title,
                "semantic_id": sm_semantic_id,
                "values": elements_dict
            }
            aas_data["submodels"].append(submodel_data)

        return jsonify(aas_data), 200
    finally:
        conn.close()

@app.route('/aas/<aas_id>/submodel/<submodel_name>', methods=['GET'])
def get_submodel_data(aas_id, submodel_name):
    """
    Fetch details of a specific submodel for a given AAS.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Fetch Submodel ID
        cur.execute("""
        SELECT id FROM submodel WHERE aas_id = %s AND title = %s
        """, (aas_id, submodel_name))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Submodel not found for the given AAS"}), 404
        sm_id = row[0]

        # Fetch Submodel Elements
        cur.execute("SELECT key, value FROM submodel_element WHERE submodel_id = %s", (sm_id,))
        elements = cur.fetchall()
        elements_dict = {key: value for key, value in elements}

        submodel_data = {
            "submodel_name": submodel_name,
            "values": elements_dict
        }

        return jsonify(submodel_data), 200
    finally:
        conn.close()

@app.route('/aas/<aas_id>/submodel/<submodel_name>/element/<element_key>', methods=['GET'])
def get_submodel_element(aas_id, submodel_name, element_key):
    """
    Fetch details of a specific element within a submodel for a given AAS.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Fetch Submodel ID
        cur.execute("""
        SELECT id FROM submodel WHERE aas_id = %s AND title = %s
        """, (aas_id, submodel_name))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Submodel not found for the given AAS"}), 404
        sm_id = row[0]

        # Fetch Element Data
        cur.execute("""
        SELECT key, value FROM submodel_element WHERE submodel_id = %s AND key = %s
        """, (sm_id, element_key))
        element = cur.fetchone()
        if not element:
            return jsonify({"error": "Element not found in the specified submodel"}), 404

        element_data = {"key": element[0], "value": element[1]}

        return jsonify(element_data), 200
    finally:
        conn.close()

@app.route('/aas/<aas_id>/submodel/<submodel_name>/element/<element_key>/history', methods=['GET'])
def get_submodel_element_history(aas_id, submodel_name, element_key):
    """
    Fetch the history of a specific element within a submodel for a given AAS.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Fetch Submodel ID
        cur.execute("""
        SELECT id FROM submodel WHERE aas_id = %s AND title = %s
        """, (aas_id, submodel_name))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Submodel not found for the given AAS"}), 404
        sm_id = row[0]

        # Fetch Element ID
        cur.execute("""
        SELECT id FROM submodel_element WHERE submodel_id = %s AND key = %s
        """, (sm_id, element_key))
        element = cur.fetchone()
        if not element:
            return jsonify({"error": "Element not found in the specified submodel"}), 404
        elem_id = element[0]

        # Fetch History for the Element
        cur.execute("""
        SELECT value, recorded_at FROM submodel_element_history WHERE submodel_element_id = %s ORDER BY recorded_at DESC
        """, (elem_id,))
        history = cur.fetchall()

        if not history:
            return jsonify({"error": "No history found for the specified element"}), 404

        history_data = [{"value": value, "recorded_at": recorded_at.isoformat()} for value, recorded_at in history]

        return jsonify(history_data), 200
    finally:
        conn.close()

@app.route('/aas/list', methods=['GET'])
def list_all_aas():
    """
    List all registered AASs with their basic details.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Fetch all AASs
        cur.execute("SELECT id, name, description FROM aas")
        rows = cur.fetchall()

        aas_list = [
            {"id": row[0], "name": row[1], "description": row[2]} for row in rows
        ]

        return jsonify(aas_list), 200
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
