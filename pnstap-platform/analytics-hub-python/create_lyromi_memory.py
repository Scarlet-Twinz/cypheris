import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS lyromi_memory (

    id SERIAL PRIMARY KEY,

    user_id INTEGER,

    memory_key VARCHAR(100) NOT NULL,

    memory_value TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()

cur.close()
conn.close()

print("✅ LYROMI memory table created successfully.")