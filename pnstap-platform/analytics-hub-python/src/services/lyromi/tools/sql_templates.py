class SQLTemplates:

    TEMPLATES = {

        "company_count":
        "SELECT COUNT(*) AS count FROM companies;",

        "user_count":
        "SELECT COUNT(*) AS count FROM users;",

        "list_companies":
        """
        SELECT
            company_name,
            country,
            status
        FROM companies;
        """,

        "list_users":
        """
        SELECT
            full_name,
            role,
            status
        FROM users;
        """,

        "organization_summary":
        """
        SELECT
            c.company_name,
            COUNT(DISTINCT u.id) AS users,
            COUNT(DISTINCT t.id) AS threats,
            dm.organization_health,
            dm.cpu_usage,
            dm.memory_usage,
            dm.disk_usage
        FROM companies c
        LEFT JOIN users u ON u.company_id = c.id
        LEFT JOIN threats t ON t.company_id = c.id
        LEFT JOIN dashboard_metrics dm ON dm.company_id = c.id
        GROUP BY
            c.company_name,
            dm.organization_health,
            dm.cpu_usage,
            dm.memory_usage,
            dm.disk_usage;
        """,

        "security_posture":
        """
        SELECT
            organization_health,
            cpu_usage,
            memory_usage,
            disk_usage
        FROM dashboard_metrics;
        """,

        "threats":
        """
        SELECT
            title,
            severity,
            status
        FROM threats;
        """
    }