import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import "./Dashboard.css";
import "cesium/Build/Cesium/Widgets/widgets.css";

import cypherisLogo from "../../assets/logo/cypheris-logo.jpg";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  console.warn(
    "VITE_API_BASE_URL is not configured. Add it to your frontend .env file."
  );
}

/* ============================================================
   HELPERS
   ============================================================ */

const safeString = (value, fallback = "") => {
  if (value === null || value === undefined) {
    return fallback;
  }

  if (typeof value === "string") {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => safeString(item))
      .filter(Boolean)
      .join(", ");
  }

  if (typeof value === "object") {
    return (
      value.name ||
      value.title ||
      value.label ||
      value.message ||
      value.text ||
      value.location ||
      value.id ||
      fallback
    );
  }

  return fallback;
};

const numericValue = (value, fallback = 0) => {
  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : fallback;
};

const getSeverity = (event) => {
  const severity = safeString(
    event?.severity ||
      event?.level ||
      event?.priority ||
      ""
  ).toLowerCase();

  if (severity === "critical") return "critical";
  if (severity === "high") return "high";
  if (severity === "medium") return "medium";
  if (severity === "low") return "low";

  return "info";
};

const getGreeting = () => {
  const hour = new Date().getHours();

  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";

  return "Good evening";
};

/* ============================================================
   CESIUM GLOBE
   ============================================================ */

const Globe = ({
  signals = [],
  threats = [],
}) => {
  const globeRef = useRef(null);
  const viewerRef = useRef(null);
  const entitiesRef = useRef([]);

  /*
   * Create Cesium viewer ONCE.
   *
   * IMPORTANT:
   * This is intentionally using a minimal Cesium
   * configuration first so we can verify that the
   * Cesium WebGL viewer itself constructs correctly.
   */
  useEffect(() => {
    let cancelled = false;

    const createViewer = async () => {
      try {
        const Cesium = await import("cesium");

        if (cancelled || !globeRef.current) {
          return;
        }

        /*
         * Minimal Cesium configuration.
         *
         * We are deliberately NOT using:
         * - fromWorldImagery()
         * - custom imagery layers
         * - lighting
         * - atmosphere
         *
         * until the basic viewer is confirmed working.
         */
        const viewer = new Cesium.Viewer(
          globeRef.current,
          {
            animation: false,
            timeline: false,
            fullscreenButton: false,
            geocoder: false,
            homeButton: false,
            sceneModePicker: false,
            navigationHelpButton: false,
            baseLayerPicker: false,
            infoBox: false,
            selectionIndicator: false,

            terrainProvider:
              new Cesium.EllipsoidTerrainProvider(),

            baseLayer: false,
          }
        );

        if (cancelled) {
          viewer.destroy();
          return;
        }

        viewer.scene.backgroundColor =
          Cesium.Color.fromCssColorString(
            "#050A14"
          );

        viewer.camera.setView({
          destination:
            Cesium.Cartesian3.fromDegrees(
              0,
              20,
              20000000
            ),

          orientation: {
            heading: 0,

            pitch:
              Cesium.Math.toRadians(-90),

            roll: 0,
          },
        });

        viewerRef.current = viewer;
      } catch (error) {
        console.error(
          "Cesium initialization failed:",
          error
        );
      }
    };

    createViewer();

    return () => {
      cancelled = true;

      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  /*
   * Update globe entities without recreating viewer.
   */
  useEffect(() => {
    const updateEntities = async () => {
      const viewer = viewerRef.current;

      if (!viewer) {
        return;
      }

      const Cesium = await import("cesium");

      /*
       * Remove previous dynamic entities.
       */
      entitiesRef.current.forEach((entity) => {
        viewer.entities.remove(entity);
      });

      entitiesRef.current = [];

      /*
       * Signals.
       */
      signals.forEach((signal) => {
        const lat = numericValue(
          signal?.lat ??
            signal?.latitude,
          NaN
        );

        const lon = numericValue(
          signal?.lon ??
            signal?.lng ??
            signal?.longitude,
          NaN
        );

        if (
          !Number.isFinite(lat) ||
          !Number.isFinite(lon)
        ) {
          return;
        }

        const entity =
          viewer.entities.add({
            position:
              Cesium.Cartesian3.fromDegrees(
                lon,
                lat,
                100000
              ),

            point: {
              pixelSize: 9,

              color:
                Cesium.Color.CYAN.withAlpha(
                  0.95
                ),

              outlineColor:
                Cesium.Color.WHITE.withAlpha(
                  0.65
                ),

              outlineWidth: 2,

              disableDepthTestDistance:
                Number.POSITIVE_INFINITY,
            },

            label: {
              text: safeString(
                signal?.name ||
                  signal?.sensor_name ||
                  signal?.sensor ||
                  "Signal"
              ),

              font:
                "12px Inter, Segoe UI, sans-serif",

              fillColor:
                Cesium.Color.WHITE,

              outlineColor:
                Cesium.Color.BLACK,

              outlineWidth: 3,

              style:
                Cesium.LabelStyle
                  .FILL_AND_OUTLINE,

              pixelOffset:
                new Cesium.Cartesian2(
                  0,
                  -20
                ),

              showBackground: true,

              backgroundColor:
                Cesium.Color.BLACK.withAlpha(
                  0.55
                ),

              disableDepthTestDistance:
                Number.POSITIVE_INFINITY,
            },
          });

        entitiesRef.current.push(entity);
      });

      /*
       * Threats.
       */
      threats.forEach((threat) => {
        const lat = numericValue(
          threat?.lat ??
            threat?.latitude,
          NaN
        );

        const lon = numericValue(
          threat?.lon ??
            threat?.lng ??
            threat?.longitude,
          NaN
        );

        if (
          !Number.isFinite(lat) ||
          !Number.isFinite(lon)
        ) {
          return;
        }

        const entity =
          viewer.entities.add({
            position:
              Cesium.Cartesian3.fromDegrees(
                lon,
                lat,
                120000
              ),

            point: {
              pixelSize: 13,

              color:
                Cesium.Color.RED.withAlpha(
                  0.95
                ),

              outlineColor:
                Cesium.Color.RED.withAlpha(
                  0.4
                ),

              outlineWidth: 4,

              disableDepthTestDistance:
                Number.POSITIVE_INFINITY,
            },

            label: {
              text: safeString(
                threat?.title ||
                  threat?.name ||
                  threat?.message ||
                  "Threat"
              ),

              font:
                "12px Inter, Segoe UI, sans-serif",

              fillColor:
                Cesium.Color.RED,

              outlineColor:
                Cesium.Color.BLACK,

              outlineWidth: 3,

              style:
                Cesium.LabelStyle
                  .FILL_AND_OUTLINE,

              pixelOffset:
                new Cesium.Cartesian2(
                  0,
                  -25
                ),

              showBackground: true,

              backgroundColor:
                Cesium.Color.BLACK.withAlpha(
                  0.6
                ),

              disableDepthTestDistance:
                Number.POSITIVE_INFINITY,
            },
          });

        entitiesRef.current.push(entity);
      });
    };

    updateEntities();
  }, [signals, threats]);

  return (
    <div
      ref={globeRef}
      className="cesium-globe"
    />
  );
};

/* ============================================================
   MAIN DASHBOARD
   ============================================================ */

const Dashboard = () => {
  const navigate = useNavigate();

  const [sidebarCollapsed, setSidebarCollapsed] =
    useState(false);

  const [userName, setUserName] =
    useState("Operator");

  const [companyName, setCompanyName] =
    useState("");

  const [time, setTime] =
    useState(new Date());

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);

  const [metrics, setMetrics] =
    useState({
      users: 0,
      activeUsers: 0,
      threats: 0,
      incidents: 0,
      events: 0,
      securityScore: 0,
    });

  const [activity, setActivity] =
    useState([]);

  const [signals, setSignals] =
    useState([]);

  const [integrations, setIntegrations] =
    useState({
      sensors: 0,
      clouds: 0,
      apis: 0,
    });

  const [threatFeed, setThreatFeed] =
    useState([]);

  const [resources, setResources] =
    useState(null);

  const [lyromiMessages, setLyromiMessages] =
    useState([]);

  const [lyromiInput, setLyromiInput] =
    useState("");

  const [lyromiLoading, setLyromiLoading] =
    useState(false);

  /* ==========================================================
     AUTH
     ========================================================== */

  const getToken = useCallback(() => {
    return (
      localStorage.getItem(
        "access_token"
      ) ||
      localStorage.getItem("token") ||
      ""
    );
  }, []);

  const getCompanyId = useCallback(() => {
    try {
      const company = JSON.parse(
        localStorage.getItem(
          "company"
        ) || "{}"
      );

      return (
        company.id ||
        company.company_id ||
        null
      );
    } catch {
      return null;
    }
  }, []);

  /* ==========================================================
     FETCH DASHBOARD
     ========================================================== */

  const fetchDashboard = useCallback(
    async () => {
      try {
        const token = getToken();

        if (!token) {
          navigate("/login");
          return;
        }

        if (!API_BASE_URL) {
          throw new Error(
            "VITE_API_BASE_URL is not configured."
          );
        }

        const headers = {
          Authorization:
            `Bearer ${token}`,
        };

        const dashboardRes =
          await axios.get(
            `${API_BASE_URL}/api/dashboard/`,
            { headers }
          );

        const dashboardData =
          dashboardRes.data?.data ||
          dashboardRes.data ||
          {};

        setMetrics({
          users: numericValue(
            dashboardData.users ??
              dashboardData.total_users
          ),

          activeUsers:
            numericValue(
              dashboardData.active_users
            ),

          threats:
            numericValue(
              dashboardData.threats ??
                dashboardData.threat_count
            ),

          incidents:
            numericValue(
              dashboardData.incidents
            ),

          events:
            numericValue(
              dashboardData.events ??
                dashboardData.event_count
            ),

          securityScore:
            numericValue(
              dashboardData.security_score ??
                dashboardData.score
            ),
        });

        const nextActivity =
          Array.isArray(
            dashboardData.activity
          )
            ? dashboardData.activity
            : Array.isArray(
                dashboardData.recent_activity
              )
            ? dashboardData.recent_activity
            : [];

        const nextSignals =
          Array.isArray(
            dashboardData.signals
          )
            ? dashboardData.signals
            : [];

        setActivity(nextActivity);
        setSignals(nextSignals);

        /*
         * Backend-provided threat feed only.
         */
        setThreatFeed(
          Array.isArray(
            dashboardData.threat_feed
          )
            ? dashboardData.threat_feed
            : Array.isArray(
                dashboardData.threats_feed
              )
            ? dashboardData.threats_feed
            : []
        );

        /*
         * Backend-provided resources only.
         */
        setResources(
          dashboardData.resources ||
            dashboardData.system_resources ||
            null
        );

        /*
         * Integrations.
         */
        const companyId =
          getCompanyId();

        if (companyId) {
          const integrationsRes =
            await axios.get(
              `${API_BASE_URL}/api/integrations/company/${companyId}`,
              { headers }
            );

          const integrationsData =
            integrationsRes.data?.integrations ||
            integrationsRes.data ||
            [];

          let sensorCount = 0;
          let cloudCount = 0;
          let apiCount = 0;

          if (
            Array.isArray(
              integrationsData
            )
          ) {
            integrationsData.forEach(
              (integration) => {
                const type =
                  safeString(
                    integration?.type
                  ).toUpperCase();

                if (
                  type === "SENSOR" ||
                  type === "PNSTAP SENSOR"
                ) {
                  sensorCount++;
                } else if (
                  type === "CLOUD"
                ) {
                  cloudCount++;
                } else if (
                  type === "API" ||
                  type === "SECURITY API"
                ) {
                  apiCount++;
                }
              }
            );
          }

          setIntegrations({
            sensors: sensorCount,
            clouds: cloudCount,
            apis: apiCount,
          });
        }

        setError(null);
      } catch (err) {
        console.error(
          "Dashboard synchronization error:",
          err
        );

        setError(
          err?.message ||
            "Unable to synchronize security data."
        );
      } finally {
        setLoading(false);
      }
    },
    [
      getToken,
      getCompanyId,
      navigate,
    ]
  );

  /* ==========================================================
     LYROMI
     ========================================================== */

  const sendLyromiMessage =
    async () => {
      const message =
        lyromiInput.trim();

      if (!message || lyromiLoading) {
        return;
      }

      setLyromiMessages(
        (current) => [
          ...current,
          {
            from: "user",
            text: message,
          },
        ]
      );

      setLyromiInput("");
      setLyromiLoading(true);

      try {
        const token =
          getToken();

        const response =
          await axios.post(
            `${API_BASE_URL}/api/lyromi/chat`,
            {
              message,
            },
            {
              headers: {
                "Content-Type":
                  "application/json",

                Authorization:
                  `Bearer ${token}`,
              },
            }
          );

        const reply =
          response.data?.reply ||
          response.data?.response ||
          response.data?.message ||
          "LYROMI received your request.";

        setLyromiMessages(
          (current) => [
            ...current,
            {
              from: "lyromi",
              text: safeString(
                reply,
                "LYROMI received your request."
              ),
            },
          ]
        );
      } catch (err) {
        console.error(
          "LYROMI error:",
          err
        );

        setLyromiMessages(
          (current) => [
            ...current,
            {
              from: "lyromi",
              text:
                err?.response?.data
                  ?.detail ||
                err?.message ||
                "LYROMI is temporarily unavailable.",
            },
          ]
        );
      } finally {
        setLyromiLoading(false);
      }
    };

  /* ==========================================================
     EFFECTS
     ========================================================== */

  useEffect(() => {
    try {
      const user = JSON.parse(
        localStorage.getItem(
          "user"
        ) || "{}"
      );

      setUserName(
        user.name ||
          user.full_name ||
          user.fullName ||
          "Operator"
      );

      setCompanyName(
        user.company_name ||
          user.company ||
          ""
      );
    } catch {
      setUserName("Operator");
    }

    fetchDashboard();

    const dashboardInterval =
      setInterval(
        fetchDashboard,
        30000
      );

    const clockInterval =
      setInterval(
        () =>
          setTime(
            new Date()
          ),
        1000
      );

    return () => {
      clearInterval(
        dashboardInterval
      );

      clearInterval(
        clockInterval
      );
    };
  }, [fetchDashboard]);

  /* ==========================================================
     LOGOUT
     ========================================================== */

  const handleLogout =
    () => {
      localStorage.removeItem(
        "access_token"
      );

      localStorage.removeItem(
        "token"
      );

      localStorage.removeItem(
        "user"
      );

      localStorage.removeItem(
        "company"
      );

      navigate("/login");
    };

  const handleRefresh =
    () => {
      setLoading(true);
      fetchDashboard();
    };

  /* ==========================================================
     THREAT CALCULATIONS
     ========================================================== */

  const severityCounts =
    activity.reduce(
      (counts, event) => {
        const severity =
          getSeverity(event);

        if (
          severity ===
            "critical" ||
          severity === "high" ||
          severity === "medium" ||
          severity === "low"
        ) {
          counts[severity]++;
        }

        return counts;
      },
      {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      }
    );

  const severityTotal =
    Object.values(
      severityCounts
    ).reduce(
      (sum, value) =>
        sum + value,
      0
    );

  const severityPercent =
    (severity) => {
      if (!severityTotal) {
        return 0;
      }

      return Math.round(
        (severityCounts[
          severity
        ] /
          severityTotal) *
          100
      );
    };

  /* ==========================================================
     GRAPH DATA
     ========================================================== */

  const graphPoints =
    activity
      .slice(0, 20)
      .map(
        (event, index) => {
          const severity =
            getSeverity(event);

          const weight =
            severity ===
            "critical"
              ? 100
              : severity ===
                "high"
              ? 75
              : severity ===
                "medium"
              ? 50
              : severity ===
                "low"
              ? 25
              : 15;

          const x =
            activity.length <= 1
              ? 200
              : (index /
                  (activity.length -
                    1)) *
                400;

          const y =
            100 -
            (weight *
              0.75);

          return {
            x,
            y,
          };
        }
      );

  const graphPolyline =
    graphPoints
      .map(
        ({ x, y }) =>
          `${x},${y}`
      )
      .join(" ");

  /* ==========================================================
     RENDER
     ========================================================== */

  if (loading) {
    return (
      <div className="cypheris-dashboard loading-screen">
        <div>
          SYNCHRONIZING CONTROL PLANE
          <span className="loading-dots">
            ...
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cypheris-dashboard error-screen">
        <div className="error-content">
          <div className="error-icon">
            !
          </div>

          <h2>
            BACKEND CONNECTION WARNING
          </h2>

          <p>{error}</p>

          <button
            onClick={
              handleRefresh
            }
          >
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="cypheris-dashboard">

      {/* ======================================================
          SIDEBAR
          ====================================================== */}

      <aside
        className={`sidebar ${
          sidebarCollapsed
            ? "collapsed"
            : ""
        }`}
      >
        <div className="sidebar-brand">
          <img
            src={cypherisLogo}
            alt="Cypheris"
            className="brand-logo"
          />

          {!sidebarCollapsed && (
            <span className="brand-name">
              CYPHERIS
            </span>
          )}
        </div>

        <nav className="sidebar-nav">
          <ul>
            <li className="active">
              <span className="nav-icon">
                ⌂
              </span>

              {!sidebarCollapsed && (
                <span>
                  Overview
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ⚡
              </span>

              {!sidebarCollapsed && (
                <span>
                  Threat Intelligence
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ◈
              </span>

              {!sidebarCollapsed && (
                <span>
                  Assets
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ◫
              </span>

              {!sidebarCollapsed && (
                <span>
                  Companies
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                !
              </span>

              {!sidebarCollapsed && (
                <span>
                  Incidents
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ◒
              </span>

              {!sidebarCollapsed && (
                <span>
                  Analytics
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ✦
              </span>

              {!sidebarCollapsed && (
                <span>
                  LYROMI
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ◇
              </span>

              {!sidebarCollapsed && (
                <span>
                  Billing
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ⚙
              </span>

              {!sidebarCollapsed && (
                <span>
                  Settings
                </span>
              )}
            </li>

            <li>
              <span className="nav-icon">
                ?
              </span>

              {!sidebarCollapsed && (
                <span>
                  Help & Support
                </span>
              )}
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <button
            onClick={
              handleLogout
            }
            className="logout-btn"
          >
            <span className="nav-icon">
              ⏻
            </span>

            {!sidebarCollapsed && (
              <span>
                Sign Out
              </span>
            )}
          </button>
        </div>

        <button
          type="button"
          className="sidebar-toggle"
          aria-label={
            sidebarCollapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
          onClick={() =>
            setSidebarCollapsed(
              (current) =>
                !current
            )
          }
        >
          {sidebarCollapsed
            ? "→"
            : "←"}
        </button>
      </aside>

      {/* ======================================================
          MAIN CONTENT
          ====================================================== */}

      <main className="main-content">

        {/* HEADER */}

        <header className="dashboard-header">
          <div className="header-left">
            <h1>
              {getGreeting()},{" "}
              <span className="user-name">
                {userName}
              </span>
            </h1>

            {companyName && (
              <span className="company-badge">
                {companyName}
              </span>
            )}
          </div>

          <div className="header-center">
            <span className="live-badge">
              ● LIVE
            </span>

            <span className="header-time">
              {time.toLocaleTimeString()}
            </span>
          </div>

          <div className="header-right">
            <button
              type="button"
              className="header-btn"
              aria-label="Search"
            >
              ⌕
            </button>

            <button
              type="button"
              className="header-btn"
              aria-label="Notifications"
            >
              ◌
            </button>

            <button
              type="button"
              className="profile-btn"
              aria-label="Profile"
            >
              <span className="profile-avatar">
                {userName
                  .charAt(0)
                  .toUpperCase()}
              </span>
            </button>
          </div>
        </header>

        {/* KPI STRIP */}

        <div className="kpi-strip">
          <div className="kpi-card">
            <span className="kpi-label">
              SENSORS
            </span>

            <span className="kpi-value">
              {integrations.sensors}
            </span>
          </div>

          <div className="kpi-card">
            <span className="kpi-label">
              CLOUD
            </span>

            <span className="kpi-value">
              {integrations.clouds}
            </span>
          </div>

          <div className="kpi-card">
            <span className="kpi-label">
              API SOURCES
            </span>

            <span className="kpi-value">
              {integrations.apis}
            </span>
          </div>

          <div className="kpi-card">
            <span className="kpi-label">
              THREATS
            </span>

            <span className="kpi-value threat">
              {metrics.threats}
            </span>
          </div>

          <div className="kpi-card">
            <span className="kpi-label">
              SECURITY SCORE
            </span>

            <span className="kpi-value score">
              {metrics.securityScore}
              %
            </span>
          </div>
        </div>

        {/* ====================================================
            GLOBE + ACTIVITY
            ==================================================== */}

        <div className="dashboard-grid">

          <div className="globe-container">

            <Globe
              signals={signals}
              threats={activity.filter(
                (event) =>
                  getSeverity(
                    event
                  ) ===
                  "critical"
              )}
            />

            <div className="globe-overlay">
              <span className="globe-status">
                GLOBAL SECURITY MAP
              </span>

              <span className="globe-live">
                ● LIVE
              </span>
            </div>

            <div className="globe-footer">
              <span>
                {signals.length}{" "}
                active signals
              </span>

              <span>
                {metrics.threats}{" "}
                threats
              </span>
            </div>

          </div>

          {/* ACTIVITY */}

          <div className="activity-panel">

            <h3>
              REAL-TIME ACTIVITY
            </h3>

            <div className="activity-list">

              {activity.length === 0 ? (
                <div className="empty-state">
                  WAITING FOR TELEMETRY
                </div>
              ) : (
                activity
                  .slice(0, 7)
                  .map(
                    (
                      event,
                      index
                    ) => {

                      const severity =
                        getSeverity(
                          event
                        );

                      return (
                        <div
                          key={
                            event.id ||
                            event.event_id ||
                            index
                          }
                          className={`activity-item ${severity}`}
                        >

                          <span className="activity-dot" />

                          <div className="activity-content">

                            <span className="activity-title">
                              {safeString(
                                event.title ||
                                  event.message ||
                                  event.name,
                                "Security event"
                              )}
                            </span>

                            <span className="activity-location">
                              {safeString(
                                event.location ||
                                  event.source ||
                                  event.origin,
                                "Unknown source"
                              )}
                            </span>

                            <span className="activity-time">
                              {safeString(
                                event.timestamp ||
                                  event.created_at ||
                                  event.time,
                                "Recent"
                              )}
                            </span>

                          </div>

                        </div>
                      );
                    }
                  )
              )}

            </div>

          </div>

        </div>

        {/* ====================================================
            BOTTOM GRID
            ==================================================== */}

        <div className="bottom-grid">

          {/* LYROMI */}

          <div className="lyromi-panel">

            <div className="lyromi-header">

              <div className="lyromi-mark">
                ✦
              </div>

              <div>

                <h4>
                  LYROMI
                </h4>

                <small>
                  Cypheris Intelligence Layer
                </small>

              </div>

              <span className="lyromi-status">
                ● ONLINE
              </span>

            </div>

            <div className="lyromi-messages">

              {lyromiMessages.length === 0 ? (

                <div className="lyromi-empty">

                  <div className="lyromi-empty-mark">
                    ✦
                  </div>

                  <strong>
                    Ask LYROMI
                  </strong>

                  <span>
                    Your Cypheris intelligence layer
                    is ready.
                  </span>

                </div>

              ) : (

                lyromiMessages.map(
                  (
                    msg,
                    index
                  ) => (

                    <div
                      key={index}
                      className={`lyromi-msg ${msg.from}`}
                    >

                      <span className="lyromi-avatar">
                        {msg.from ===
                        "lyromi"
                          ? "✦"
                          : "YOU"}
                      </span>

                      <p>
                        {safeString(
                          msg.text
                        )}
                      </p>

                    </div>

                  )
                )

              )}

              {lyromiLoading && (

                <div className="lyromi-msg lyromi">

                  <span className="lyromi-avatar">
                    ✦
                  </span>

                  <p className="typing">
                    ...
                  </p>

                </div>

              )}

            </div>

            <div className="lyromi-input-area">

              <input
                type="text"
                placeholder="Ask LYROMI..."
                value={
                  lyromiInput
                }
                onChange={(event) =>
                  setLyromiInput(
                    event.target
                      .value
                  )
                }
                onKeyDown={(
                  event
                ) => {
                  if (
                    event.key ===
                    "Enter"
                  ) {
                    sendLyromiMessage();
                  }
                }}
              />

              <button
                type="button"
                onClick={
                  sendLyromiMessage
                }
                disabled={
                  lyromiLoading
                }
              >
                {lyromiLoading
                  ? "..."
                  : "Send"}
              </button>

            </div>

          </div>

          {/* SECURITY GRAPH */}

          <div className="graph-panel">

            <h4>
              SECURITY OVERVIEW
            </h4>

            <div className="graph-container">

              {graphPoints.length > 0 ? (

                <svg
                  viewBox="0 0 400 100"
                  className="security-graph"
                  preserveAspectRatio="none"
                >

                  <polyline
                    points={
                      graphPolyline
                    }
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    opacity="0.7"
                  />

                  {graphPoints.map(
                    (
                      point,
                      index
                    ) => (

                      <circle
                        key={index}
                        cx={
                          point.x
                        }
                        cy={
                          point.y
                        }
                        r="2"
                        fill="currentColor"
                      />

                    )
                  )}

                </svg>

              ) : (

                <div className="empty-state">
                  TELEMETRY STREAM
                </div>

              )}

            </div>

          </div>

          {/* THREAT DISTRIBUTION */}

          <div className="threat-distribution">

            <h4>
              THREAT CATEGORIES
            </h4>

            <div className="threat-bars">

              {[
                "critical",
                "high",
                "medium",
                "low",
              ].map(
                (severity) => {

                  const percentage =
                    severityPercent(
                      severity
                    );

                  return (

                    <div
                      className="threat-bar"
                      key={
                        severity
                      }
                    >

                      <span>
                        {severity
                          .charAt(
                            0
                          )
                          .toUpperCase() +
                          severity.slice(
                            1
                          )}
                      </span>

                      <div className="bar-bg">

                        <div
                          className={`bar-fill ${severity}`}
                          style={{
                            width: `${percentage}%`,
                          }}
                        />

                      </div>

                      <span>
                        {percentage}%
                      </span>

                    </div>

                  );
                }
              )}

            </div>

          </div>

        </div>

        {/* ====================================================
            RESOURCES + THREAT FEED
            ==================================================== */}

        {(resources ||
          threatFeed.length >
            0) && (

          <div className="footer-grid">

            {resources && (

              <div className="system-resources">

                <h4>
                  SYSTEM RESOURCES
                </h4>

                {Object.entries(
                  resources
                ).map(
                  ([
                    name,
                    value,
                  ]) => {

                    const percentage =
                      Math.min(
                        100,
                        Math.max(
                          0,
                          numericValue(
                            value
                          )
                        )
                      );

                    return (

                      <div
                        className="resource-bar"
                        key={
                          name
                        }
                      >

                        <span>
                          {safeString(
                            name
                          )}
                        </span>

                        <div className="resource-bg">

                          <div
                            className="resource-fill"
                            style={{
                              width: `${percentage}%`,
                            }}
                          />

                        </div>

                        <span>
                          {percentage}%
                        </span>

                      </div>

                    );
                  }
                )}

              </div>

            )}

            {threatFeed.length >
              0 && (

              <div className="threat-feed">

                <h4>
                  THREAT INTELLIGENCE FEED
                </h4>

                <div className="feed-items">

                  {threatFeed
                    .slice(0, 6)
                    .map(
                      (
                        item,
                        index
                      ) => {

                        const severity =
                          getSeverity(
                            item
                          );

                        return (

                          <div
                            key={
                              item.id ||
                              item.event_id ||
                              index
                            }
                            className={`feed-item ${severity}`}
                          >

                            {safeString(
                              item.title ||
                                item.message ||
                                item.text ||
                                item.name,
                              "Threat intelligence update"
                            )}

                          </div>

                        );

                      }
                    )}

                </div>

              </div>

            )}

          </div>

        )}

      </main>

    </div>
  );
};

export default Dashboard;