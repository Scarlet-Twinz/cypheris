class QueryRegistry:

    QUERIES = {

        # ============================================================
        # COMPANIES
        # ============================================================

        "company_count": """
            SELECT COUNT(*) AS company_count
            FROM companies;
        """,

        "company_list": """
            SELECT
                company_name,
                industry,
                country,
                subscription_plan,
                status
            FROM companies
            ORDER BY company_name;
        """,

        "company_detail": """
            SELECT
                company_name,
                industry,
                country,
                email,
                phone,
                website,
                subscription_plan,
                status,
                created_at
            FROM companies
            WHERE LOWER(company_name) = LOWER(%s);
        """,

        "active_company_list": """
            SELECT
                company_name,
                country,
                status
            FROM companies
            WHERE LOWER(status) = 'active'
            ORDER BY company_name;
        """,

        "inactive_company_count": """
            SELECT COUNT(*) AS inactive_company_count
            FROM companies
            WHERE LOWER(status) = 'inactive';
        """,

        "company_user_count": """
            SELECT
                c.company_name,
                COUNT(u.id) AS user_count
            FROM companies c
            LEFT JOIN users u
                ON u.company_id = c.id
            GROUP BY c.id, c.company_name
            ORDER BY user_count DESC, c.company_name;
        """,

        "top_company_by_users": """
            SELECT
                c.company_name,
                COUNT(u.id) AS user_count
            FROM companies c
            LEFT JOIN users u
                ON u.company_id = c.id
            GROUP BY c.id, c.company_name
            ORDER BY user_count DESC, c.company_name
            LIMIT 1;
        """,

        "company_security_summary": """
            SELECT
                c.company_name,
                c.status,
                COUNT(DISTINCT u.id) AS user_count,
                COUNT(DISTINCT t.id) AS threat_count,
                COUNT(DISTINCT a.id) AS alert_count
            FROM companies c
            LEFT JOIN users u
                ON u.company_id = c.id
            LEFT JOIN threats t
                ON t.company_id = c.id
            LEFT JOIN alerts a
                ON a.company_id = c.id
            WHERE LOWER(c.company_name) = LOWER(%s)
            GROUP BY c.id, c.company_name, c.status;
        """,

        # ============================================================
        # USERS
        # ============================================================

        "user_count": """
            SELECT COUNT(*) AS user_count
            FROM users;
        """,

        "user_list": """
            SELECT
                full_name,
                email,
                role,
                status,
                last_login
            FROM users
            ORDER BY full_name;
        """,

        "active_user_count": """
            SELECT COUNT(*) AS active_user_count
            FROM users
            WHERE LOWER(status) = 'active';
        """,

        "inactive_user_count": """
            SELECT COUNT(*) AS inactive_user_count
            FROM users
            WHERE LOWER(status) = 'inactive';
        """,

        "admin_count": """
            SELECT COUNT(*) AS admin_count
            FROM users
            WHERE LOWER(role) = 'admin';
        """,

        "user_company": """
            SELECT
                u.full_name AS user_name,
                u.email,
                u.role,
                u.status AS user_status,
                u.last_login,
                c.company_name,
                c.country,
                c.status AS company_status
            FROM users u
            INNER JOIN companies c
                ON u.company_id = c.id
            WHERE LOWER(u.full_name) = LOWER(%s);
        """,

        "user_detail": """
            SELECT
                u.full_name,
                u.email,
                u.phone_number,
                u.role,
                u.status,
                u.last_login,
                u.created_at,
                c.company_name,
                c.country,
                c.status AS company_status
            FROM users u
            INNER JOIN companies c
                ON u.company_id = c.id
            WHERE LOWER(u.full_name) = LOWER(%s);
        """,

        "company_users": """
            SELECT
                u.full_name,
                u.email,
                u.role,
                u.status,
                u.last_login
            FROM users u
            INNER JOIN companies c
                ON u.company_id = c.id
            WHERE LOWER(c.company_name) = LOWER(%s)
            ORDER BY u.full_name;
        """,

        # ============================================================
        # THREATS
        # ============================================================

        "threat_count": """
            SELECT COUNT(*) AS threat_count
            FROM threats;
        """,

        "threat_list": """
            SELECT
                t.title,
                t.severity,
                t.status,
                t.description,
                t.detected_at,
                c.company_name
            FROM threats t
            INNER JOIN companies c
                ON t.company_id = c.id
            ORDER BY t.detected_at DESC;
        """,

        "critical_threat_count": """
            SELECT COUNT(*) AS critical_threat_count
            FROM threats
            WHERE LOWER(severity) = 'critical';
        """,

        "high_threat_count": """
            SELECT COUNT(*) AS high_threat_count
            FROM threats
            WHERE LOWER(severity) = 'high';
        """,

        "active_threat_count": """
            SELECT COUNT(*) AS active_threat_count
            FROM threats
            WHERE LOWER(status) IN ('active', 'open');
        """,

        "recent_threats": """
            SELECT
                t.title,
                t.severity,
                t.status,
                t.description,
                t.detected_at,
                c.company_name
            FROM threats t
            INNER JOIN companies c
                ON t.company_id = c.id
            ORDER BY t.detected_at DESC
            LIMIT 10;
        """,

        "company_threats": """
            SELECT
                t.title,
                t.severity,
                t.status,
                t.description,
                t.detected_at
            FROM threats t
            INNER JOIN companies c
                ON t.company_id = c.id
            WHERE LOWER(c.company_name) = LOWER(%s)
            ORDER BY t.detected_at DESC;
        """,

        # ============================================================
        # ALERTS
        # ============================================================

        "alert_count": """
            SELECT COUNT(*) AS alert_count
            FROM alerts;
        """,

        "critical_alert_count": """
            SELECT COUNT(*) AS critical_alert_count
            FROM alerts
            WHERE LOWER(severity) = 'critical';
        """,

        "active_alert_count": """
            SELECT COUNT(*) AS active_alert_count
            FROM alerts
            WHERE LOWER(status) IN ('active', 'open');
        """,

        "alert_list": """
            SELECT
                a.alert_type,
                a.severity,
                a.description,
                a.status,
                a.created_at,
                c.company_name
            FROM alerts a
            INNER JOIN companies c
                ON a.company_id = c.id
            ORDER BY a.created_at DESC;
        """,

        "company_alerts": """
            SELECT
                a.alert_type,
                a.severity,
                a.description,
                a.status,
                a.created_at
            FROM alerts a
            INNER JOIN companies c
                ON a.company_id = c.id
            WHERE LOWER(c.company_name) = LOWER(%s)
            ORDER BY a.created_at DESC;
        """,

        # ============================================================
        # NETWORK
        # ============================================================

        "network_summary": """
            SELECT
                COUNT(*) AS flow_count,
                COALESCE(SUM(packets), 0) AS total_packets,
                COALESCE(SUM(bytes), 0) AS total_bytes,
                COALESCE(AVG(duration), 0) AS average_duration
            FROM network_flows;
        """,

        "top_source_ips": """
            SELECT
                source_ip,
                COUNT(*) AS flow_count,
                COALESCE(SUM(bytes), 0) AS total_bytes
            FROM network_flows
            GROUP BY source_ip
            ORDER BY total_bytes DESC
            LIMIT 10;
        """,

        "top_destination_ips": """
            SELECT
                destination_ip,
                COUNT(*) AS flow_count,
                COALESCE(SUM(bytes), 0) AS total_bytes
            FROM network_flows
            GROUP BY destination_ip
            ORDER BY total_bytes DESC
            LIMIT 10;
        """,

        "protocol_statistics": """
            SELECT
                protocol,
                COUNT(*) AS flow_count,
                COALESCE(SUM(packets), 0) AS total_packets,
                COALESCE(SUM(bytes), 0) AS total_bytes
            FROM network_flows
            GROUP BY protocol
            ORDER BY total_bytes DESC;
        """,

        "recent_network_flows": """
            SELECT
                source_ip,
                destination_ip,
                protocol,
                packets,
                bytes,
                duration,
                detected_at
            FROM network_flows
            ORDER BY detected_at DESC
            LIMIT 20;
        """,

        "company_network_summary": """
            SELECT
                c.company_name,
                COUNT(n.id) AS flow_count,
                COALESCE(SUM(n.packets), 0) AS total_packets,
                COALESCE(SUM(n.bytes), 0) AS total_bytes
            FROM companies c
            LEFT JOIN network_flows n
                ON n.company_id = c.id
            WHERE LOWER(c.company_name) = LOWER(%s)
            GROUP BY c.company_name;
        """,

        # ============================================================
        # DASHBOARD / SECURITY POSTURE
        # ============================================================

        "dashboard_summary": """
            SELECT
                organization_health,
                threat_level,
                cpu_usage,
                memory_usage,
                disk_usage,
                ai_confidence,
                network_traffic,
                packets_per_second,
                latency,
                sensor_online,
                last_analysis
            FROM dashboard_metrics
            ORDER BY last_analysis DESC
            LIMIT 1;
        """,

        "security_posture": """
            SELECT
                organization_health,
                threat_level,
                ai_confidence,
                network_traffic,
                packets_per_second,
                latency,
                sensor_online,
                last_analysis
            FROM dashboard_metrics
            ORDER BY last_analysis DESC
            LIMIT 1;
        """,

        # ============================================================
        # BILLING / SUBSCRIPTIONS
        # ============================================================

        "subscription_summary": """
            SELECT
                c.company_name,
                s.plan,
                s.billing_cycle,
                s.user_limit,
                s.current_users,
                s.annual_price,
                s.renewal_date,
                s.status
            FROM subscriptions s
            INNER JOIN companies c
                ON s.company_id = c.id
            ORDER BY c.company_name;
        """,

        "company_subscription": """
            SELECT
                c.company_name,
                s.plan,
                s.billing_cycle,
                s.user_limit,
                s.current_users,
                s.annual_price,
                s.renewal_date,
                s.status
            FROM subscriptions s
            INNER JOIN companies c
                ON s.company_id = c.id
            WHERE LOWER(c.company_name) = LOWER(%s);
        """,

        "over_limit_companies": """
            SELECT
                c.company_name,
                s.plan,
                s.user_limit,
                s.current_users,
                (s.current_users - s.user_limit) AS extra_users,
                s.annual_price,
                s.renewal_date
            FROM subscriptions s
            INNER JOIN companies c
                ON s.company_id = c.id
            WHERE s.current_users > s.user_limit
            ORDER BY extra_users DESC;
        """,

        # ============================================================
        # NOTIFICATIONS
        # ============================================================

        "unread_notification_count": """
            SELECT COUNT(*) AS unread_notification_count
            FROM notifications
            WHERE is_read = FALSE;
        """,

        "recent_notifications": """
            SELECT
                title,
                message,
                is_read,
                created_at
            FROM notifications
            ORDER BY created_at DESC
            LIMIT 10;
        """,

        # ============================================================
        # AUDIT
        # ============================================================

        "recent_audit_logs": """
            SELECT
                a.action,
                a.ip_address,
                a.created_at,
                u.full_name,
                c.company_name
            FROM audit_logs a
            LEFT JOIN users u
                ON a.user_id = u.id
            LEFT JOIN companies c
                ON a.company_id = c.id
            ORDER BY a.created_at DESC
            LIMIT 20;
        """,

        # ============================================================
        # REPORT
        # ============================================================

        "report": """
            SELECT
                organization_health,
                threat_level,
                cpu_usage,
                memory_usage,
                disk_usage,
                ai_confidence,
                network_traffic,
                packets_per_second,
                latency,
                sensor_online,
                last_analysis
            FROM dashboard_metrics
            ORDER BY last_analysis DESC
            LIMIT 1;
        """
    }

    @staticmethod
    def get(name):
        return QueryRegistry.QUERIES.get(name)