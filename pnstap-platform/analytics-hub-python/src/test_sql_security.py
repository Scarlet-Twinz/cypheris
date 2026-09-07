from services.lyromi.tools.sql_executor import SQLExecutor


tests = [
    "CREATE TABLE test(id INT);",
    "DELETE FROM users;",
    "DROP TABLE users;",
    "UPDATE users SET status='Inactive';",
    "ALTER TABLE users ADD COLUMN test INT;",
    "TRUNCATE users;",
    "GRANT ALL ON users TO test;",
    "REVOKE ALL ON users FROM test;",
]


print("\n========== SQL SECURITY TEST ==========\n")


for sql in tests:

    try:

        result = SQLExecutor.execute(sql)

        print("FAILED TO BLOCK:")
        print(sql)
        print("RESULT:", result)
        print()

    except Exception as error:

        print("BLOCKED:")
        print(sql)
        print("REASON:", error)
        print()


print("=======================================\n")