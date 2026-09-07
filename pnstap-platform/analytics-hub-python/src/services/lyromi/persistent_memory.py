from database import get_db_connection


class PersistentMemory:

    @staticmethod
    def save(user_id: int, key: str, value: str):

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO lyromi_memory
            (user_id, memory_key, memory_value)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, memory_key)
            DO UPDATE SET
            memory_value = EXCLUDED.memory_value,
            updated_at = CURRENT_TIMESTAMP;
        """, (user_id, key, value))

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def load(user_id: int, key: str):

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT memory_value
            FROM lyromi_memory
            WHERE user_id=%s
            AND memory_key=%s;
        """, (user_id, key))

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:
            return row["memory_value"]

        return None