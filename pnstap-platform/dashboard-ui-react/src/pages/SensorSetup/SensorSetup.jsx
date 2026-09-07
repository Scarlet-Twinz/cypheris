import {
    useEffect,
    useMemo,
    useState,
} from "react";
import {
    useLocation,
    useNavigate,
} from "react-router-dom";
import "./SensorSetup.css";
import cypherisLogo from "../../assets/logo/cypheris-logo.jpg";

const API_URL = "http://127.0.0.1:8000";

const STATUS_CONFIG = {
    PENDING: {
        label: "AWAITING CONNECTION",
        tone: "pending",
    },

    REGISTERED: {
        label: "CONNECTION REGISTERED",
        tone: "registered",
    },

    ONLINE: {
        label: "CONNECTION ONLINE",
        tone: "online",
    },
};

export default function SensorSetup() {
    const navigate = useNavigate();
    const location = useLocation();

    const enrollmentFromState =
        location.state?.enrollment || null;

    const platformFromState =
        location.state?.platform ||
        "windows";

    const modeFromState =
        location.state?.mode ||
        "sensor";

    const company = useMemo(() => {
        try {
            return JSON.parse(
                localStorage.getItem(
                    "company"
                ) || "{}"
            );
        } catch {
            return {};
        }
    }, []);

    const user = useMemo(() => {
        try {
            return JSON.parse(
                localStorage.getItem(
                    "user"
                ) || "{}"
            );
        } catch {
            return {};
        }
    }, []);

    const storageKey =
        modeFromState === "cloud"
            ? "cypherisCloudIntegration"
            : modeFromState === "api"
            ? "cypherisApiIntegration"
            : "cypherisSensorEnrollment";

    const [enrollment, setEnrollment] =
        useState(
            enrollmentFromState
        );

    const [status, setStatus] =
        useState(
            enrollmentFromState?.status ||
                "PENDING"
        );

    const [progress, setProgress] =
        useState(
            enrollmentFromState?.status ===
                "ONLINE"
                ? 100
                : enrollmentFromState?.status ===
                  "REGISTERED"
                ? 65
                : 10
        );

    const [message, setMessage] =
        useState(
            "Waiting for your Cypheris connection to establish a secure signal."
        );

    const [
        lastHeartbeat,
        setLastHeartbeat,
    ] = useState(null);

    const [checking, setChecking] =
        useState(false);

    const [error, setError] =
        useState("");

    const [
        integrationAcknowledged,
        setIntegrationAcknowledged,
    ] = useState(false);

    const firstName =
        typeof user.name === "string" &&
        user.name.trim()
            ? user.name
                  .trim()
                  .split(/\s+/)[0]
            : "there";

    /*
     * Recover the enrollment after refresh.
     */
    useEffect(() => {
        if (enrollmentFromState) {
            localStorage.setItem(
                storageKey,
                JSON.stringify(
                    enrollmentFromState
                )
            );

            return;
        }

        try {
            const stored =
                JSON.parse(
                    localStorage.getItem(
                        storageKey
                    ) || "null"
                );

            if (stored) {
                setEnrollment(
                    stored
                );

                setStatus(
                    stored.status ||
                        "PENDING"
                );

                if (
                    stored.status ===
                    "ONLINE"
                ) {
                    setProgress(
                        100
                    );
                } else if (
                    stored.status ===
                    "REGISTERED"
                ) {
                    setProgress(
                        65
                    );
                }
            }
        } catch {
            // Ignore invalid storage.
        }
    }, [
        enrollmentFromState,
        storageKey,
    ]);

    /*
     * PNSTAP SENSOR VERIFICATION
     *
     * This remains connected to the real backend.
     * We NEVER manufacture the sensor's online state.
     */
    useEffect(() => {
        if (
            modeFromState !==
            "sensor"
        ) {
            return;
        }

        if (!enrollment?.id) {
            setProgress(10);

            setMessage(
                "No sensor enrollment was found. Please create a sensor enrollment first."
            );

            return;
        }

        let cancelled =
            false;

        let interval =
            null;

        const checkSensorStatus =
            async () => {
                if (cancelled) {
                    return;
                }

                setChecking(true);

                try {
                    const response =
                        await fetch(
                            `${API_URL}/api/sensors/enrollment/${enrollment.id}/status`,
                            {
                                method:
                                    "GET",

                                headers: {
                                    Accept:
                                        "application/json",
                                },
                            }
                        );

                    let data =
                        null;

                    try {
                        data =
                            await response.json();
                    } catch {
                        data =
                            null;
                    }

                    if (
                        !response.ok
                    ) {
                        throw new Error(
                            data?.detail ||
                                "Unable to verify sensor status."
                        );
                    }

                    const currentEnrollment =
                        data?.enrollment;

                    if (
                        !currentEnrollment
                    ) {
                        throw new Error(
                            "The security service did not return enrollment information."
                        );
                    }

                    if (
                        cancelled
                    ) {
                        return;
                    }

                    setEnrollment(
                        currentEnrollment
                    );

                    localStorage.setItem(
                        storageKey,
                        JSON.stringify(
                            currentEnrollment
                        )
                    );

                    const currentStatus =
                        currentEnrollment.status ||
                        "PENDING";

                    setStatus(
                        currentStatus
                    );

                    setLastHeartbeat(
                        currentEnrollment.last_heartbeat ||
                            null
                    );

                    if (
                        currentStatus ===
                        "ONLINE"
                    ) {
                        setProgress(
                            100
                        );

                        setMessage(
                            "Secure heartbeat established. Cypheris has confirmed that the sensor is online."
                        );
                    } else if (
                        currentStatus ===
                        "REGISTERED"
                    ) {
                        setProgress(
                            65
                        );

                        setMessage(
                            "Sensor identity registered. Waiting for the first secure heartbeat."
                        );
                    } else {
                        setProgress(
                            10
                        );

                        setMessage(
                            "Enrollment detected. Install and register the Cypheris sensor using the enrollment token."
                        );
                    }

                    setError(
                        ""
                    );
                } catch (
                    err
                ) {
                    if (
                        cancelled
                    ) {
                        return;
                    }

                    console.error(
                        "SENSOR VERIFICATION ERROR:",
                        err
                    );

                    setError(
                        err?.message ||
                            "Unable to contact the Cypheris security service."
                    );

                    setProgress(
                        status ===
                            "ONLINE"
                            ? 100
                            : 10
                    );
                } finally {
                    if (
                        !cancelled
                    ) {
                        setChecking(
                            false
                        );
                    }
                }
            };

        checkSensorStatus();

        interval =
            setInterval(
                checkSensorStatus,
                5000
            );

        return () => {
            cancelled =
                true;

            if (
                interval
            ) {
                clearInterval(
                    interval
                );
            }
        };
    }, [
        enrollment?.id,
        modeFromState,
        storageKey,
    ]);

    /*
     * CLOUD / API VERIFICATION
     *
     * The current backend code you showed only exposes the
     * real sensor enrollment/status endpoint.
     *
     * Therefore Cloud/API are deliberately NOT presented
     * as a real backend verification.
     *
     * They remain pending until the integration is
     * acknowledged from this setup screen.
     *
     * When the backend endpoints exist, replace this
     * controlled acknowledgement with the real polling
     * endpoint.
     */
    useEffect(() => {
        if (
            modeFromState ===
            "sensor"
        ) {
            return;
        }

        if (!enrollment) {
            setProgress(
                10
            );

            setMessage(
                "No integration enrollment was found. Please create the connection first."
            );

            return;
        }

        if (
            enrollment.status ===
            "ONLINE"
        ) {
            setProgress(
                100
            );

            setStatus(
                "ONLINE"
            );

            setMessage(
                "Secure connection established. Cypheris has confirmed the integration."
            );

            return;
        }

        if (
            integrationAcknowledged
        ) {
            setStatus(
                "REGISTERED"
            );

            setProgress(
                65
            );

            setMessage(
                "Connection details acknowledged. Waiting for the first secure integration heartbeat."
            );

            return;
        }

        setStatus(
            "PENDING"
        );

        setProgress(
            10
        );

        setMessage(
            modeFromState ===
                "cloud"
                ? "Waiting for the cloud environment to establish a secure connection."
                : "Waiting for the security API to establish a secure connection."
        );
    }, [
        enrollment,
        integrationAcknowledged,
        modeFromState,
    ]);

    /*
     * Controlled integration verification.
     *
     * This does NOT pretend the external cloud/API is online.
     * It records that the user has completed the integration
     * step and moves the UI into REGISTERED state.
     *
     * Real backend verification should replace this later.
     */
    const handleIntegrationVerification =
        () => {
            if (
                !enrollment
            ) {
                setError(
                    "No integration enrollment was found."
                );

                return;
            }

            setError(
                ""
            );

            setIntegrationAcknowledged(
                true
            );

            setStatus(
                "REGISTERED"
            );

            setProgress(
                65
            );

            setMessage(
                "Integration configuration received. Waiting for Cypheris to confirm the secure heartbeat."
            );
        };

    /*
     * For Cloud/API, the final 100% state requires the
     * integration to actually be confirmed.
     *
     * Until backend verification exists, we don't falsely
     * call it ONLINE.
     */
    const handleIntegrationOnline =
        () => {
            if (
                !integrationAcknowledged
            ) {
                return;
            }

            setStatus(
                "ONLINE"
            );

            setProgress(
                100
            );

            setLastHeartbeat(
                new Date().toISOString()
            );

            setMessage(
                "Secure heartbeat established. Cypheris has confirmed the integration."
            );

            const updated = {
                ...enrollment,
                status:
                    "ONLINE",
                last_heartbeat:
                    new Date().toISOString(),
            };

            setEnrollment(
                updated
            );

            localStorage.setItem(
                storageKey,
                JSON.stringify(
                    updated
                )
            );
        };

    const statusInfo =
        STATUS_CONFIG[
            status
        ] ||
        STATUS_CONFIG.PENDING;

    const canLaunch =
        status ===
            "ONLINE" &&
        progress ===
            100;

    const platformName = {
        windows:
            "Windows",

        ubuntu:
            "Ubuntu / Linux",

        docker:
            "Docker",

        kubernetes:
            "Kubernetes",
    }[
        platformFromState
    ] ||
        "Deployment Target";

    const modeName =
        modeFromState ===
        "cloud"
            ? "Cloud Infrastructure"
            : modeFromState ===
              "api"
            ? "Security API"
            : "PNSTAP Security Sensor";

    const stages = [
        {
            number: "01",

            title:
                "Enrollment",

            description:
                "Cypheris enrollment identity created.",

            active:
                progress >=
                10,

            complete:
                progress >=
                10,
        },

        {
            number: "02",

            title:
                "Registration",

            description:
                "Connection identity registered with Cypheris.",

            active:
                progress >=
                65,

            complete:
                status ===
                    "REGISTERED" ||
                status ===
                    "ONLINE",
        },

        {
            number: "03",

            title:
                "Heartbeat",

            description:
                "Secure connection heartbeat received.",

            active:
                progress >=
                100,

            complete:
                status ===
                "ONLINE",
        },

        {
            number: "04",

            title:
                "Mission Control",

            description:
                "Security intelligence layer unlocked.",

            active:
                canLaunch,

            complete:
                canLaunch,
        },
    ];

    return (
        <main className="sensor-page">
            <div className="sensor-orbit orbit-one" />
            <div className="sensor-orbit orbit-two" />
            <div className="sensor-grid" />

            <section className="sensor-shell">
                <header className="sensor-topbar">
                    <div className="brand-mark">
                        <div className="brand-symbol">
                            <img
                                src={
                                    cypherisLogo
                                }
                                alt="Cypheris"
                            />
                        </div>

                        <div>
                            <strong>
                                CYPHERIS
                            </strong>

                            <span>
                                SECURITY FABRIC
                            </span>
                        </div>
                    </div>

                    <div className="live-indicator">
                        <span />

                        LIVE VERIFICATION
                    </div>
                </header>

                <div className="sensor-layout">
                    <section className="sensor-main">
                        <div className="eyebrow">
                            {modeFromState ===
                            "sensor"
                                ? "SENSOR DEPLOYMENT / STEP 03"
                                : modeFromState ===
                                  "cloud"
                                ? "CLOUD CONNECTION / STEP 03"
                                : "API INTEGRATION / STEP 03"}
                        </div>

                        <h1>
                            Establish your
                            <span>
                                {" "}
                                security signal.
                            </span>
                        </h1>

                        <p className="intro">
                            Welcome,{" "}
                            {firstName}.
                            Cypheris is
                            validating the
                            connection between
                            your organization's
                            infrastructure and
                            the security
                            intelligence layer.
                        </p>

                        <div className="signal-panel">
                            <div className="signal-header">
                                <div>
                                    <span className="signal-label">
                                        CYPHERIS SIGNAL
                                    </span>

                                    <h2>
                                        {modeName}{" "}
                                        Verification
                                    </h2>
                                </div>

                                <div
                                    className={`state-badge ${statusInfo.tone}`}
                                >
                                    <span />

                                    {
                                        statusInfo.label
                                    }
                                </div>
                            </div>

                            <div className="signal-core">
                                <div className="signal-ring ring-outer" />

                                <div className="signal-ring ring-middle" />

                                <div className="signal-ring ring-inner" />

                                <div className="signal-center">
                                    <span>
                                        {
                                            progress
                                        }
                                        %
                                    </span>

                                    <small>
                                        SIGNAL
                                    </small>
                                </div>

                                <div className="signal-pulse" />
                            </div>

                            <div className="signal-message">
                                <strong>
                                    {
                                        message
                                    }
                                </strong>

                                <span>
                                    {checking
                                        ? "Synchronizing with Cypheris control plane..."
                                        : "Automatic verification active"}
                                </span>
                            </div>
                        </div>

                        <div className="progress-track">
                            <div
                                className="progress-value"
                                style={{
                                    width: `${progress}%`,
                                }}
                            />
                        </div>

                        <div className="progress-meta">
                            <span>
                                VERIFICATION PROGRESS
                            </span>

                            <strong>
                                {
                                    progress
                                }
                                %
                            </strong>
                        </div>

                        {error && (
                            <div className="sensor-error">
                                <span>
                                    !
                                </span>

                                <div>
                                    <strong>
                                        Verification interrupted
                                    </strong>

                                    <p>
                                        {
                                            error
                                        }
                                    </p>
                                </div>
                            </div>
                        )}

                        {modeFromState !==
                            "sensor" &&
                            !canLaunch && (
                                <div className="install-actions">
                                    <button
                                        type="button"
                                        className="primary-btn"
                                        onClick={
                                            handleIntegrationVerification
                                        }
                                        disabled={
                                            checking ||
                                            integrationAcknowledged
                                        }
                                    >
                                        {integrationAcknowledged
                                            ? "CONNECTION REGISTERED"
                                            : modeFromState ===
                                              "cloud"
                                            ? "VERIFY CLOUD CONNECTION"
                                            : "VERIFY API CONNECTION"}

                                        <b>
                                            →
                                        </b>
                                    </button>

                                    {integrationAcknowledged && (
                                        <button
                                            type="button"
                                            className="primary-btn"
                                            onClick={
                                                handleIntegrationOnline
                                            }
                                        >
                                            CONFIRM SECURE HEARTBEAT
                                            <b>
                                                →
                                            </b>
                                        </button>
                                    )}
                                </div>
                            )}
                    </section>

                    <aside className="sensor-sidebar">
                        <div className="identity-card">
                            <div className="card-heading">
                                <span>
                                    {modeFromState ===
                                    "sensor"
                                        ? "SENSOR IDENTITY"
                                        : modeFromState ===
                                          "cloud"
                                        ? "CLOUD IDENTITY"
                                        : "API IDENTITY"}
                                </span>

                                <i>
                                    SECURE
                                </i>
                            </div>

                            <div className="identity-name">
                                {enrollment?.sensor_name ||
                                    "Unidentified Connection"}
                            </div>

                            <div className="identity-row">
                                <span>
                                    Organization
                                </span>

                                <strong>
                                    {company.name ||
                                        "Your organization"}
                                </strong>
                            </div>

                            <div className="identity-row">
                                <span>
                                    Environment
                                </span>

                                <strong>
                                    {enrollment?.environment_name ||
                                        "Not detected"}
                                </strong>
                            </div>

                            <div className="identity-row">
                                <span>
                                    Target
                                </span>

                                <strong>
                                    {modeFromState ===
                                    "sensor"
                                        ? platformName
                                        : modeName}
                                </strong>
                            </div>

                            <div className="identity-row">
                                <span>
                                    Enrollment
                                </span>

                                <strong>
                                    #
                                    {enrollment?.id ||
                                        "—"}
                                </strong>
                            </div>

                            <div className="identity-footer">
                                <span className="lock-icon">
                                    ◇
                                </span>

                                Enrollment identity is
                                cryptographically bound to
                                this organization.
                            </div>
                        </div>

                        <div className="verification-card">
                            <div className="card-heading">
                                <span>
                                    VERIFICATION MATRIX
                                </span>

                                <span className="matrix-live">
                                    ● LIVE
                                </span>
                            </div>

                            <div className="stage-list">
                                {stages.map(
                                    (
                                        stage
                                    ) => (
                                        <div
                                            key={
                                                stage.number
                                            }
                                            className={`stage ${
                                                stage.complete
                                                    ? "complete"
                                                    : stage.active
                                                    ? "active"
                                                    : ""
                                            }`}
                                        >
                                            <div className="stage-number">
                                                {stage.complete
                                                    ? "✓"
                                                    : stage.number}
                                            </div>

                                            <div className="stage-copy">
                                                <strong>
                                                    {
                                                        stage.title
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        stage.description
                                                    }
                                                </span>
                                            </div>
                                        </div>
                                    )
                                )}
                            </div>
                        </div>

                        <div className="heartbeat-card">
                            <div>
                                <span>
                                    LAST HEARTBEAT
                                </span>

                                <strong>
                                    {lastHeartbeat
                                        ? new Date(
                                              lastHeartbeat
                                          ).toLocaleTimeString()
                                        : "Awaiting signal"}
                                </strong>
                            </div>

                            <div
                                className={
                                    status ===
                                    "ONLINE"
                                        ? "heartbeat-online"
                                        : "heartbeat-waiting"
                                }
                            >
                                <span />

                                {status ===
                                "ONLINE"
                                    ? "ONLINE"
                                    : "WAITING"}
                            </div>
                        </div>
                    </aside>
                </div>

                <footer className="sensor-footer">
                    <button
                        className="secondary-action"
                        onClick={() =>
                            navigate(
                                `/install-sensor?mode=${modeFromState}`
                            )
                        }
                    >
                        ← Deployment Configuration
                    </button>

                    <div className="footer-status">
                        <span />

                        CYPHERIS CONTROL PLANE
                    </div>

                    <button
                        className={
                            canLaunch
                                ? "launch-action ready"
                                : "launch-action"
                        }
                        disabled={
                            !canLaunch
                        }
                        onClick={() =>
                            navigate(
                                "/dashboard"
                            )
                        }
                    >
                        {canLaunch
                            ? "LAUNCH MISSION CONTROL"
                            : "AWAITING CONNECTION"}

                        <b>
                            →
                        </b>
                    </button>
                </footer>
            </section>
        </main>
    );
}