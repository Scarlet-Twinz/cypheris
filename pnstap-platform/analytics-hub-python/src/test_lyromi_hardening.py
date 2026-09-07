from services.lyromi.brain.action_engine import ActionEngine
from services.lyromi.brain.task_executor import TaskExecutor
from services.lyromi.query_registry import QueryRegistry


print("========== LYROMI QUERY REGISTRY HARDENING TEST ==========")

# ---------------------------------------------------------
# Discover real database values
# ---------------------------------------------------------

companies = ActionEngine._get_company_names()
users = ActionEngine._get_user_names()

company = companies[0] if companies else None
user = users[0] if users else None

print("COMPANIES:", companies)
print("USERS:", users)

# ---------------------------------------------------------
# Tasks requiring parameters
# ---------------------------------------------------------

COMPANY_TASKS = {
    "company_detail",
    "company_security_summary",
    "company_users",
    "company_threats",
    "company_alerts",
    "company_network_summary",
    "company_subscription",
}

USER_TASKS = {
    "user_company",
    "user_detail",
}

# ---------------------------------------------------------
# Get ALL registered tasks
# ---------------------------------------------------------

tasks = list(QueryRegistry.QUERIES.keys())

print("TOTAL REGISTERED TASKS:", len(tasks))

passed = 0
failed = 0
skipped = 0

# ---------------------------------------------------------
# Test every registered task
# ---------------------------------------------------------

for task in tasks:

    print("\n" + "=" * 60)
    print("TASK:", task)

    try:

        # ---------------------------------------------
        # Company parameter
        # ---------------------------------------------

        if task in COMPANY_TASKS:

            if not company:
                print("STATUS: SKIP - no company found")
                skipped += 1
                continue

            params = (company,)

        # ---------------------------------------------
        # User parameter
        # ---------------------------------------------

        elif task in USER_TASKS:

            if not user:
                print("STATUS: SKIP - no user found")
                skipped += 1
                continue

            params = (user,)

        # ---------------------------------------------
        # No parameter
        # ---------------------------------------------

        else:

            params = ()

        # ---------------------------------------------
        # Execute task
        # ---------------------------------------------

        result = TaskExecutor.execute(
            task=task,
            question=f"Hardening test for {task}",
            params=params,
        )

        print("RESULT:", result)

        if result is None:

            print("STATUS: FAIL")
            failed += 1

        else:

            print("STATUS: PASS")
            passed += 1

    except Exception as error:

        print("STATUS: FAIL")
        print("ERROR:", error)

        failed += 1


# ---------------------------------------------------------
# Final result
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("LYROMI HARDENING RESULT")
print("=" * 60)

print("PASSED:", passed)
print("FAILED:", failed)
print("SKIPPED:", skipped)

if failed == 0:

    print("STATUS: ALL TESTS PASSED")

else:

    print("STATUS: FAILURES DETECTED")