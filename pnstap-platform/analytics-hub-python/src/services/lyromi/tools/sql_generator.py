from ..ollama import Ollama


class SQLGenerator:

    @staticmethod
    def generate(question: str, schema: str):

        system_prompt = f"""
You convert English questions into PostgreSQL.
Database Schema:
{schema}
Rules:

Return ONE SQL statement only.
Return SELECT statements only.
Never CREATE.
Never DROP.
Never ALTER.
Never INSERT.
Never UPDATE.
Never DELETE.
Never TRUNCATE.
Never GRANT.
Never REVOKE.
Never explain anything.
Never use markdown.
Never use code fences.
Never include comments.
Examples:
Question:
How many companies do we have?
SQL:
SELECT COUNT(*) AS company_count FROM companies;
Question:
List all companies.
SQL:
SELECT * FROM companies;
Question:
How many users do we have?
SQL:
SELECT COUNT(*) AS user_count FROM users;
"""
        sql = Ollama.ask(
            system_prompt=system_prompt,
            message=question,
            history=[]
        )

        if not sql:
            raise ValueError("SQL generator returned an empty response.")

        sql = sql.strip()

        # Remove markdown code fences if the model adds them.
        sql = sql.replace("```sql", "")
        sql = sql.replace("```SQL", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

        # Find the beginning of the SELECT statement
        # if the model accidentally adds text before it.
        select_position = sql.upper().find("SELECT")

        if select_position == -1:
            raise ValueError("LYROMI did not generate a SELECT statement.")

        sql = sql[select_position:].strip()

        # Remove a trailing semicolon only if there is extra text after it.
        if ";" in sql:
            sql = sql.split(";", 1)[0].strip() + ";"

        # Final safety check.
        if not sql.upper().startswith("SELECT"):
            raise ValueError("Only SELECT statements are allowed.")

        print("\n========== AI GENERATED SQL ==========")
        print(sql)
        print("======================================\n")

        return sql
