from psycopg2.extras import RealDictCursor

from database import get_db_connection


class DatabaseTool:

    @staticmethod
    def execute(query: str, params=None):

        conn = get_db_connection()

        if conn is None:
            return None

        cur = None

        try:

            cur = conn.cursor(
                cursor_factory=RealDictCursor
            )

            # -------------------------------------------------
            # Execute query safely
            # -------------------------------------------------

            if params:

                cur.execute(
                    query,
                    params
                )

            else:

                cur.execute(query)

            rows = cur.fetchall()

            return rows

        except Exception as error:

            print(
                f"Database query failed: {error}"
            )

            try:
                conn.rollback()

            except Exception:
                pass

            return None

        finally:

            if cur is not None:
                cur.close()

            conn.close()