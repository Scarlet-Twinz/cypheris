from database import get_db_connection


class EnterpriseContext:

    @staticmethod
    def build():

        context = {}

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Companies
            cur.execute("SELECT COUNT(*) FROM companies")
            context["companies"] = cur.fetchone()[0]

            # Users
            cur.execute("SELECT COUNT(*) FROM users")
            context["users"] = cur.fetchone()[0]

            # Organization
            cur.execute("""
                SELECT company_name
                FROM companies
                LIMIT 1
            """)

            row = cur.fetchone()

            context["organization"] = (
                row[0]
                if row
                else "Unknown"
            )

            cur.close()
            conn.close()

        except Exception:
            context = {
                "organization": "Unknown",
                "companies": 0,
                "users": 0
            }

        return context