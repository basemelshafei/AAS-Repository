# db_setup.py

import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

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

create_tables_if_not_exist(get_connection())