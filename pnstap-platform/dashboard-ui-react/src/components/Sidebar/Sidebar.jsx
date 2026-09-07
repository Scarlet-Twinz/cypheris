import {
    FiActivity,
    FiAlertTriangle,
    FiArchive,
    FiBarChart2,
    FiBell,
    FiBox,
    FiChevronLeft,
    FiChevronRight,
    FiCpu,
    FiDatabase,
    FiFileText,
    FiGrid,
    FiLayers,
    FiLogOut,
    FiMenu,
    FiSearch,
    FiSettings,
    FiShield,
    FiUsers,
    FiWifi,
    FiZap
} from "react-icons/fi";

import { useLocation, useNavigate } from "react-router-dom";

import "./Sidebar.css";

export default function Sidebar({ collapsed, setCollapsed }) {
    const navigate = useNavigate();
    const location = useLocation();

    const user = JSON.parse(
        localStorage.getItem("user") || "{}"
    );

    const company = JSON.parse(
        localStorage.getItem("company") || "{}"
    );

    const organizationName =
        company.name ||
        company.organization_name ||
        "Organization";

    const userName =
        user.name ||
        user.full_name ||
        user.email ||
        "User";

    const userRole =
        user.role ||
        user.job_title ||
        "Security Administrator";

    const getInitials = (name) => {
        if (!name) return "U";

        const parts = name
            .trim()
            .split(/\s+/)
            .filter(Boolean);

        if (parts.length === 1) {
            return parts[0].slice(0, 2).toUpperCase();
        }

        return (
            parts[0][0] +
            parts[parts.length - 1][0]
        ).toUpperCase();
    };

    const isActive = (path) => {
        if (path === "/dashboard") {
            return location.pathname === "/dashboard";
        }

        return location.pathname.startsWith(path);
    };

    const navigateTo = (path) => {
        navigate(path);
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        localStorage.removeItem("company");
        localStorage.removeItem("cypherisOrganization");

        navigate("/login", {
            replace: true
        });
    };

    const sections = [
        {
            label: "COMMAND",
            items: [
                {
                    label: "Mission Control",
                    icon: FiGrid,
                    path: "/dashboard"
                }
            ]
        },

        {
            label: "INFRASTRUCTURE",
            items: [
                {
                    label: "Sensors",
                    icon: FiWifi,
                    path: "/sensors"
                },
                {
                    label: "Environments",
                    icon: FiLayers,
                    path: "/environments"
                },
                {
                    label: "Assets",
                    icon: FiBox,
                    path: "/assets"
                }
            ]
        },

        {
            label: "INTELLIGENCE",
            items: [
                {
                    label: "Threats",
                    icon: FiShield,
                    path: "/threats"
                },
                {
                    label: "Events",
                    icon: FiActivity,
                    path: "/events"
                },
                {
                    label: "Investigations",
                    icon: FiSearch,
                    path: "/investigations"
                },
                {
                    label: "LYROMI",
                    icon: FiCpu,
                    path: "/lyromi"
                }
            ]
        },

        {
            label: "OPERATIONS",
            items: [
                {
                    label: "Incidents",
                    icon: FiAlertTriangle,
                    path: "/incidents"
                },
                {
                    label: "Reports",
                    icon: FiFileText,
                    path: "/reports"
                },
                {
                    label: "Audit",
                    icon: FiArchive,
                    path: "/audit"
                }
            ]
        },

        {
            label: "ORGANIZATION",
            items: [
                {
                    label: "Organizations",
                    icon: FiDatabase,
                    path: "/organizations"
                },
                {
                    label: "Users & Access",
                    icon: FiUsers,
                    path: "/users"
                },
                {
                    label: "Billing",
                    icon: FiBarChart2,
                    path: "/billing"
                },
                {
                    label: "Integrations",
                    icon: FiZap,
                    path: "/integrations"
                },
                {
                    label: "Settings",
                    icon: FiSettings,
                    path: "/settings"
                }
            ]
        }
    ];

    return (
        <aside
            className={`sidebar ${
                collapsed ? "collapsed" : ""
            }`}
        >
            <div className="sidebar-brand">
                <button
                    type="button"
                    className="sidebar-toggle"
                    onClick={() =>
                        setCollapsed(!collapsed)
                    }
                    aria-label={
                        collapsed
                            ? "Expand sidebar"
                            : "Collapse sidebar"
                    }
                >
                    {collapsed ? (
                        <FiChevronRight />
                    ) : (
                        <FiChevronLeft />
                    )}
                </button>

                <div className="brand-mark">
                    <img
                        src="/src/assets/logo/cypheris-logo.jpg"
                        alt="Cypheris"
                    />
                </div>

                <div className="brand-copy">
                    <strong>CYPHERIS</strong>
                    <span>SECURITY FABRIC</span>
                </div>
            </div>

            {!collapsed && (
                <div className="workspace-context">
                    <span className="workspace-label">
                        ACTIVE ORGANIZATION
                    </span>

                    <strong>
                        {organizationName}
                    </strong>

                    <span className="workspace-status">
                        <i />
                        Control plane connected
                    </span>
                </div>
            )}

            <nav className="sidebar-navigation">
                {sections.map((section) => (
                    <div
                        className="sidebar-section"
                        key={section.label}
                    >
                        {!collapsed && (
                            <div className="sidebar-section-label">
                                {section.label}
                            </div>
                        )}

                        {section.items.map((item) => {
                            const Icon = item.icon;
                            const active = isActive(
                                item.path
                            );

                            return (
                                <button
                                    key={item.path}
                                    type="button"
                                    className={`sidebar-item ${
                                        active
                                            ? "active"
                                            : ""
                                    }`}
                                    onClick={() =>
                                        navigateTo(
                                            item.path
                                        )
                                    }
                                    title={
                                        collapsed
                                            ? item.label
                                            : undefined
                                    }
                                >
                                    <Icon />

                                    {!collapsed && (
                                        <span>
                                            {item.label}
                                        </span>
                                    )}

                                    {active &&
                                        !collapsed && (
                                            <i className="active-indicator" />
                                        )}
                                </button>
                            );
                        })}
                    </div>
                ))}
            </nav>

            <div className="sidebar-bottom">
                {!collapsed && (
                    <button
                        type="button"
                        className="sidebar-alerts"
                        onClick={() =>
                            navigateTo(
                                "/notifications"
                            )
                        }
                    >
                        <FiBell />

                        <span>
                            Notifications
                        </span>

                        <i />
                    </button>
                )}

                <div className="sidebar-user">
                    <div className="user-avatar">
                        {getInitials(userName)}
                    </div>

                    {!collapsed && (
                        <div className="user-details">
                            <strong>
                                {userName}
                            </strong>

                            <span>
                                {userRole}
                            </span>
                        </div>
                    )}
                </div>

                <button
                    type="button"
                    className="sidebar-logout"
                    onClick={logout}
                    title={
                        collapsed
                            ? "Sign out"
                            : undefined
                    }
                >
                    <FiLogOut />

                    {!collapsed && (
                        <span>Sign out</span>
                    )}
                </button>
            </div>
        </aside>
    );
}