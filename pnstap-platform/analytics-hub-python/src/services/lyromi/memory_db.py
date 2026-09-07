from database import get_db_connection


class MemoryDB:

    @staticmethod
    def save(user_id, key, value):

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if memory already exists
        cur.execute(
            """
            SELECT id
            FROM lyromi_memory
            WHERE user_id=%s
            AND memory_key=%s
            LIMIT 1
            """,
            (user_id, key),
        )

        row = cur.fetchone()

        if row:

            cur.execute(
                """
                UPDATE lyromi_memory
                SET memory_value=%s,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=%s
                """,
                (
                    value,
                    row["id"],
                ),
            )

        else:

            cur.execute(
                """
                INSERT INTO lyromi_memory
                (
                    user_id,
                    memory_key,
                    memory_value
                )
                VALUES (%s,%s,%s)
                """,
                (
                    user_id,
                    key,
                    value,
                ),
            )

        conn.commit()

        cur.close()
        conn.close()

    @staticmethod
    def get(user_id, key):

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT memory_value
            FROM lyromi_memory
            WHERE user_id=%s
            AND memory_key=%s
            LIMIT 1
            """,
            (
                user_id,
                key,
            ),
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:
            return row["memory_value"]

        return None

    @staticmethod
    def get_all(user_id):

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                memory_key,
                memory_value
            FROM lyromi_memory
            WHERE user_id=%s
            ORDER BY memory_key
            """,
            (user_id,),
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    @staticmethod
    def delete(user_id, key):

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM lyromi_memory
            WHERE user_id=%s
            AND memory_key=%s
            """,
            (
                user_id,
                key,
            ),
        )

        conn.commit()

        cur.close()
        conn.close()