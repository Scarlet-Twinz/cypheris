import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./InstallSensor.css";
import cypherisLogo from "../../assets/logo/cypheris-logo.jpg";

const API_URL = "http://127.0.0.1:8000";

const platforms = [
    {
        id: "windows",
        icon: "🪟",
        name: "Windows",
        description:
            "Install the Cypheris sensor on a Windows server or workstation.",
    },
    {
        id: "ubuntu",
        icon: "🐧",
        name: "Ubuntu / Linux",
        description:
            "Deploy the sensor on an Ubuntu or compatible Linux environment.",
    },
    {
        id: "docker",
        icon: "🐳",
        name: "Docker",
        description:
            "Run the Cypheris sensor as a containerized workload.",
    },
    {
        id: "kubernetes",
        icon: "☸",
        name: "Kubernetes",
        description:
            "Deploy the Cypheris sensor inside a Kubernetes cluster.",
    },
];

const cloudProviders = [
    {
        id: "aws",
        icon: "☁",
        name: "AWS",
        description:
            "Connect your Amazon Web Services environment.",
    },
    {
        id: "azure",
        icon: "☁",
        name: "Azure",
        description:
            "Connect your Microsoft Azure environment.",
    },
    {
        id: "gcp",
        icon: "☁",
        name: "Google Cloud",
        description:
            "Connect your Google Cloud environment.",
    },
];

const apiPlatforms = [
    {
        id: "siem",
        icon: "◈",
        name: "SIEM",
        description:
            "Connect an existing security information and event platform.",
    },
    {
        id: "edr",
        icon: "◇",
        name: "EDR / XDR",
        description:
            "Connect endpoint security telemetry.",
    },
    {
        id: "custom",
        icon: "⌁",
        name: "Custom Security API",
        description:
            "Connect your existing security data source.",
    },
];

const installCommands = {
    windows: `CypherisSensor.exe --enrollment-token <TOKEN>`,

    ubuntu: `curl -fsSL https://install.cypheris.io/linux | sudo bash
cypheris-sensor enroll --token <TOKEN>`,

    docker: `docker run -d \\
  --name cypheris-sensor \\
  -e CYPHERIS_ENROLLMENT_TOKEN=<TOKEN> \\
  cypheris/sensor:latest`,

    kubernetes: `kubectl create secret generic cypheris-enrollment \\
  --from-literal=token=<TOKEN>

kubectl apply -f cypheris-sensor.yaml`,
};

export default function InstallSensor() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const mode =
        searchParams.get("mode") === "cloud"
            ? "cloud"
            : searchParams.get("mode") === "api"
            ? "api"
            : "sensor";

    const company = useMemo(() => {
        try {
            const storedCompany = localStorage.getItem("company");

            if (!storedCompany) {
                return {};
            }

            const parsedCompany = JSON.parse(storedCompany);

            if (
                !parsedCompany ||
                typeof parsedCompany !== "object"
            ) {
                return {};
            }

            return parsedCompany;
        } catch (error) {
            console.error(
                "Unable to read company information:",
                error
            );

            return {};
        }
    }, []);

    const user = useMemo(() => {
        try {
            const storedUser = localStorage.getItem("user");

            if (!storedUser) {
                return {};
            }

            const parsedUser = JSON.parse(storedUser);

            if (
                !parsedUser ||
                typeof parsedUser !== "object"
            ) {
                return {};
            }

            return parsedUser;
        } catch (error) {
            console.error(
                "Unable to read user information:",
                error
            );

            return {};
        }
    }, []);

    const [sensorName, setSensorName] = useState("");
    const [environmentName, setEnvironmentName] = useState("");
    const [environmentType, setEnvironmentType] =
        useState("infrastructure");

    const [platform, setPlatform] =
        useState("windows");

    const [cloudProvider, setCloudProvider] =
        useState("aws");

    const [apiPlatform, setApiPlatform] =
        useState("siem");

    const [apiUrl, setApiUrl] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    const [enrollment, setEnrollment] =
        useState(null);

    const firstName =
        typeof user.name === "string" &&
        user.name.trim()
            ? user.name.trim().split(/\s+/)[0]
            : "there";

    const selectedPlatform =
        platforms.find(
            (item) => item.id === platform
        );

    const selectedCloudProvider =
        cloudProviders.find(
            (item) => item.id === cloudProvider
        );

    const selectedApiPlatform =
        apiPlatforms.find(
            (item) => item.id === apiPlatform
        );

    const getPageTitle = () => {
        if (mode === "cloud") {
            return "Connect your cloud infrastructure.";
        }

        if (mode === "api") {
            return "Connect your security API.";
        }

        return "Connect your infrastructure.";
    };

    const getPageDescription = () => {
        if (mode === "cloud") {
            return (
                <>
                    Welcome, {firstName}. Create a secure cloud connection
                    for your organization's environment.
                </>
            );
        }

        if (mode === "api") {
            return (
                <>
                    Welcome, {firstName}. Create a secure integration
                    connection for your organization's security platform.
                </>
            );
        }

        return (
            <>
                Welcome, {firstName}. Create an enrollment for the first
                PNSTAP Security Sensor in your organization's environment.
            </>
        );
    };

    // ============================================================
    // SENSOR
    // ============================================================

    const createSensorEnrollment = async () => {
        const response = await fetch(
            `${API_URL}/api/sensors/enroll`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify({
                    company_id: Number(company.id),

                    sensor_name:
                        sensorName.trim(),

                    environment_name:
                        environmentName.trim(),

                    environment_type:
                        environmentType,
                }),
            }
        );

        let data = null;

        try {
            data = await response.json();
        } catch {
            data = null;
        }

        if (!response.ok) {
            let message =
                "Unable to create the sensor enrollment.";

            if (
                typeof data?.detail ===
                "string"
            ) {
                message = data.detail;
            } else if (
                Array.isArray(data?.detail)
            ) {
                message =
                    data.detail
                        .map((item) =>
                            typeof item ===
                            "string"
                                ? item
                                : item?.msg ||
                                  "Invalid enrollment information."
                        )
                        .join(", ");
            }

            throw new Error(message);
        }

        if (
            !data ||
            typeof data !== "object"
        ) {
            throw new Error(
                "The security service returned an invalid response."
            );
        }

        if (!data.enrollment) {
            throw new Error(
                "The enrollment was not returned by the security service."
            );
        }

        return data.enrollment;
    };

    // ============================================================
    // CLOUD
    // ============================================================

    const createCloudEnrollment = async () => {
        const response = await fetch(
            `${API_URL}/api/integrations/cloud`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify({
                    company_id: Number(company.id),

                    connection_name:
                        sensorName.trim(),

                    environment_name:
                        environmentName.trim(),

                    environment_type:
                        environmentType,

                    provider:
                        cloudProvider,
                }),
            }
        );

        let data = null;

        try {
            data = await response.json();
        } catch {
            data = null;
        }

        if (!response.ok) {
            let message =
                "Unable to create the cloud connection.";

            if (
                typeof data?.detail ===
                "string"
            ) {
                message = data.detail;
            } else if (
                Array.isArray(data?.detail)
            ) {
                message =
                    data.detail
                        .map((item) =>
                            typeof item ===
                            "string"
                                ? item
                                : item?.msg ||
                                  "Invalid cloud connection information."
                        )
                        .join(", ");
            }

            throw new Error(message);
        }

        if (
            !data ||
            typeof data !== "object"
        ) {
            throw new Error(
                "The security service returned an invalid cloud response."
            );
        }

        if (!data.integration) {
            throw new Error(
                "The cloud integration was not returned by the security service."
            );
        }

        return data.integration;
    };

    // ============================================================
    // SECURITY API
    // ============================================================

    const createApiEnrollment = async () => {
        const response = await fetch(
            `${API_URL}/api/integrations/api`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify({
                    company_id: Number(company.id),

                    connection_name:
                        sensorName.trim(),

                    environment_name:
                        environmentName.trim(),

                    environment_type:
                        environmentType,

                    api_platform:
                        apiPlatform,

                    api_url:
                        apiUrl.trim(),
                }),
            }
        );

        let data = null;

        try {
            data = await response.json();
        } catch {
            data = null;
        }

        if (!response.ok) {
            let message =
                "Unable to create the security API connection.";

            if (
                typeof data?.detail ===
                "string"
            ) {
                message = data.detail;
            } else if (
                Array.isArray(data?.detail)
            ) {
                message =
                    data.detail
                        .map((item) =>
                            typeof item ===
                            "string"
                                ? item
                                : item?.msg ||
                                  "Invalid security API information."
                        )
                        .join(", ");
            }

            throw new Error(message);
        }

        if (
            !data ||
            typeof data !== "object"
        ) {
            throw new Error(
                "The security service returned an invalid API response."
            );
        }

        if (!data.integration) {
            throw new Error(
                "The API integration was not returned by the security service."
            );
        }

        return data.integration;
    };

    // ============================================================
    // FORM SUBMISSION
    // ============================================================

    const handleEnrollment = async (event) => {
        event.preventDefault();

        setError("");

        if (!company.id) {
            setError(
                "Your organization session could not be found. Please sign in again."
            );
            return;
        }

        if (!sensorName.trim()) {
            setError(
                mode === "sensor"
                    ? "Please enter a sensor name."
                    : "Please enter a connection name."
            );
            return;
        }

        if (!environmentName.trim()) {
            setError(
                "Please enter an environment name."
            );
            return;
        }

        if (
            mode === "api" &&
            !apiUrl.trim()
        ) {
            setError(
                "Please enter the security API URL."
            );
            return;
        }

        setLoading(true);

        try {
            let createdEnrollment;

            if (mode === "sensor") {
                createdEnrollment =
                    await createSensorEnrollment();
            } else if (mode === "cloud") {
                createdEnrollment =
                    await createCloudEnrollment();
            } else {
                createdEnrollment =
                    await createApiEnrollment();
            }

            console.log(
                "CYPHERIS CONNECTION CREATED:",
                createdEnrollment
            );

            setEnrollment(
                createdEnrollment
            );
        } catch (err) {
            console.error(
                "CYPHERIS CONNECTION ERROR:",
                err
            );

            setError(
                err?.message ||
                    "Unable to connect to the Cypheris security service."
            );
        } finally {
            setLoading(false);
        }
    };

    const command =
        enrollment &&
        mode === "sensor"
            ? installCommands[
                  platform
              ].replaceAll(
                  "<TOKEN>",
                  enrollment.enrollment_token
              )
            : "";

    return (
        <main className="install-page">
            <div className="install-card">

                <div className="install-header">

                    <div>

                        <small>
                            {mode === "sensor"
                                ? "SENSOR DEPLOYMENT / STEP 02"
                                : mode === "cloud"
                                ? "CLOUD CONNECTION / STEP 02"
                                : "API INTEGRATION / STEP 02"}
                        </small>

                        <h1>
                            {getPageTitle()}
                        </h1>

                        <p>
                            {getPageDescription()}
                        </p>

                    </div>

                    <div className="install-status">

                        <span className="status-dot" />

                        {mode === "sensor"
                            ? "SENSOR ENROLLMENT"
                            : mode === "cloud"
                            ? "CLOUD ENROLLMENT"
                            : "API ENROLLMENT"}

                    </div>

                </div>

                <div className="organization-banner">

                    <div className="organization-avatar">

                        <img
                            className="cypheris-logo"
                            src={cypherisLogo}
                            alt="Cypheris"
                        />

                    </div>

                    <div>

                        <small>
                            ORGANIZATION
                        </small>

                        <strong>
                            {company.name ||
                                "Your organization"}
                        </strong>

                    </div>

                    <div className="organization-id">

                        COMPANY ID

                        <strong>
                            {company.id || "—"}
                        </strong>

                    </div>

                </div>

                {!enrollment ? (

                    <form
                        onSubmit={
                            handleEnrollment
                        }
                    >

                        <section className="install-section">

                            <div className="section-heading">

                                <span>
                                    01
                                </span>

                                <div>

                                    <strong>
                                        {mode === "sensor"
                                            ? "Sensor identity"
                                            : mode === "cloud"
                                            ? "Cloud connection identity"
                                            : "API connection identity"}
                                    </strong>

                                    <small>
                                        Identify the environment
                                        this connection will
                                        monitor.
                                    </small>

                                </div>

                            </div>

                            <div className="form-grid">

                                <label className="field">

                                    <span>
                                        {mode ===
                                        "sensor"
                                            ? "Sensor name"
                                            : "Connection name"}
                                    </span>

                                    <input
                                        type="text"
                                        value={
                                            sensorName
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setSensorName(
                                                event
                                                    .target
                                                    .value
                                            )
                                        }
                                        placeholder={
                                            mode ===
                                            "sensor"
                                                ? "Production Sensor"
                                                : mode ===
                                                  "cloud"
                                                ? "Production Cloud"
                                                : "Security Integration"
                                        }
                                    />

                                </label>

                                <label className="field">

                                    <span>
                                        Environment name
                                    </span>

                                    <input
                                        type="text"
                                        value={
                                            environmentName
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setEnvironmentName(
                                                event
                                                    .target
                                                    .value
                                            )
                                        }
                                        placeholder="Production Infrastructure"
                                    />

                                </label>

                                <label className="field field-full">

                                    <span>
                                        Environment type
                                    </span>

                                    <select
                                        value={
                                            environmentType
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setEnvironmentType(
                                                event
                                                    .target
                                                    .value
                                            )
                                        }
                                    >

                                        <option value="infrastructure">
                                            Infrastructure
                                        </option>

                                        <option value="production">
                                            Production
                                        </option>

                                        <option value="development">
                                            Development
                                        </option>

                                        <option value="staging">
                                            Staging
                                        </option>

                                        <option value="datacenter">
                                            Data Center
                                        </option>

                                    </select>

                                </label>

                            </div>

                        </section>

                        {mode === "sensor" && (

                            <section className="install-section">

                                <div className="section-heading">

                                    <span>
                                        02
                                    </span>

                                    <div>

                                        <strong>
                                            Deployment target
                                        </strong>

                                        <small>
                                            Select where the PNSTAP
                                            sensor will run.
                                        </small>

                                    </div>

                                </div>

                                <div className="platform-grid">

                                    {platforms.map(
                                        (item) => (

                                            <button
                                                key={
                                                    item.id
                                                }
                                                type="button"
                                                className={
                                                    platform ===
                                                    item.id
                                                        ? "platform-card active"
                                                        : "platform-card"
                                                }
                                                onClick={() =>
                                                    setPlatform(
                                                        item.id
                                                    )
                                                }
                                            >

                                                <span className="platform-icon">
                                                    {
                                                        item.icon
                                                    }
                                                </span>

                                                <span className="platform-name">
                                                    {
                                                        item.name
                                                    }
                                                </span>

                                                <span className="platform-description">
                                                    {
                                                        item.description
                                                    }
                                                </span>

                                                <span className="platform-radio">
                                                    {platform ===
                                                    item.id
                                                        ? "✓"
                                                        : ""}
                                                </span>

                                            </button>

                                        )
                                    )}

                                </div>

                            </section>

                        )}

                        {mode === "cloud" && (

                            <section className="install-section">

                                <div className="section-heading">

                                    <span>
                                        02
                                    </span>

                                    <div>

                                        <strong>
                                            Cloud provider
                                        </strong>

                                        <small>
                                            Select the cloud
                                            environment Cypheris
                                            will evaluate.
                                        </small>

                                    </div>

                                </div>

                                <div className="platform-grid">

                                    {cloudProviders.map(
                                        (item) => (

                                            <button
                                                key={
                                                    item.id
                                                }
                                                type="button"
                                                className={
                                                    cloudProvider ===
                                                    item.id
                                                        ? "platform-card active"
                                                        : "platform-card"
                                                }
                                                onClick={() =>
                                                    setCloudProvider(
                                                        item.id
                                                    )
                                                }
                                            >

                                                <span className="platform-icon">
                                                    {
                                                        item.icon
                                                    }
                                                </span>

                                                <span className="platform-name">
                                                    {
                                                        item.name
                                                    }
                                                </span>

                                                <span className="platform-description">
                                                    {
                                                        item.description
                                                    }
                                                </span>

                                                <span className="platform-radio">
                                                    {cloudProvider ===
                                                    item.id
                                                        ? "✓"
                                                        : ""}
                                                </span>

                                            </button>

                                        )
                                    )}

                                </div>

                            </section>

                        )}

                        {mode === "api" && (

                            <section className="install-section">

                                <div className="section-heading">

                                    <span>
                                        02
                                    </span>

                                    <div>

                                        <strong>
                                            Security platform
                                        </strong>

                                        <small>
                                            Select the source that
                                            Cypheris will connect to.
                                        </small>

                                    </div>

                                </div>

                                <div className="platform-grid">

                                    {apiPlatforms.map(
                                        (item) => (

                                            <button
                                                key={
                                                    item.id
                                                }
                                                type="button"
                                                className={
                                                    apiPlatform ===
                                                    item.id
                                                        ? "platform-card active"
                                                        : "platform-card"
                                                }
                                                onClick={() =>
                                                    setApiPlatform(
                                                        item.id
                                                    )
                                                }
                                            >

                                                <span className="platform-icon">
                                                    {
                                                        item.icon
                                                    }
                                                </span>

                                                <span className="platform-name">
                                                    {
                                                        item.name
                                                    }
                                                </span>

                                                <span className="platform-description">
                                                    {
                                                        item.description
                                                    }
                                                </span>

                                                <span className="platform-radio">
                                                    {apiPlatform ===
                                                    item.id
                                                        ? "✓"
                                                        : ""}
                                                </span>

                                            </button>

                                        )
                                    )}

                                </div>

                                <label className="field field-full">

                                    <span>
                                        Security API URL
                                    </span>

                                    <input
                                        type="url"
                                        value={apiUrl}
                                        onChange={(
                                            event
                                        ) =>
                                            setApiUrl(
                                                event
                                                    .target
                                                    .value
                                            )
                                        }
                                        placeholder="https://security.example.com/api"
                                    />

                                </label>

                            </section>

                        )}

                        {error && (

                            <div className="install-error">

                                <span>
                                    !
                                </span>

                                {error}

                            </div>

                        )}

                        <div className="install-actions">

                            <button
                                type="button"
                                className="back-button"
                                onClick={() =>
                                    navigate(
                                        "/onboarding"
                                    )
                                }
                            >
                                ← Back
                            </button>

                            <button
                                type="submit"
                                className="primary-btn"
                                disabled={
                                    loading
                                }
                            >

                                {loading
                                    ? "CREATING CONNECTION..."
                                    : mode ===
                                      "sensor"
                                    ? "CREATE SENSOR ENROLLMENT"
                                    : mode ===
                                      "cloud"
                                    ? "CREATE CLOUD CONNECTION"
                                    : "CREATE API CONNECTION"}

                                <b>
                                    →
                                </b>

                            </button>

                        </div>

                    </form>

                ) : (

                    <section className="enrollment-created">

                        <div className="success-icon">
                            ✓
                        </div>

                        <small>
                            {mode === "sensor"
                                ? "ENROLLMENT CREATED"
                                : mode === "cloud"
                                ? "CLOUD CONNECTION CREATED"
                                : "API CONNECTION CREATED"}
                        </small>

                        <h2>
                            {mode ===
                            "sensor"
                                ? "Your sensor is ready for registration."
                                : mode ===
                                  "cloud"
                                ? "Your cloud connection is ready for verification."
                                : "Your security API connection is ready for verification."}
                        </h2>

                        <p>
                            {mode ===
                            "sensor"
                                ? "The organization enrollment has been created. Install the sensor on your selected platform and use the enrollment token below to register it."
                                : mode ===
                                  "cloud"
                                ? "The cloud connection has been created. Use the connection credential to establish the environment connection before Cypheris verifies the integration."
                                : "The API connection has been created. Use the connection credential with your security platform before Cypheris verifies the integration."}
                        </p>

                        <div className="enrollment-details">

                            <div>

                                <span>
                                    {mode ===
                                    "sensor"
                                        ? "Sensor"
                                        : "Connection"}
                                </span>

                                <strong>
                                    {
                                        enrollment.connection_name ||
                                        enrollment.sensor_name
                                    }
                                </strong>

                            </div>

                            <div>

                                <span>
                                    Environment
                                </span>

                                <strong>
                                    {
                                        enrollment.environment_name
                                    }
                                </strong>

                            </div>

                            <div>

                                <span>
                                    Status
                                </span>

                                <strong>
                                    {
                                        enrollment.status
                                    }
                                </strong>

                            </div>

                            <div>

                                <span>
                                    {mode === "sensor"
                                        ? "Enrollment ID"
                                        : "Connection ID"}
                                </span>

                                <strong>
                                    #
                                    {
                                        enrollment.id
                                    }
                                </strong>

                            </div>

                        </div>

                        <div className="token-box">

                            <span>
                                {mode ===
                                "sensor"
                                    ? "ENROLLMENT TOKEN"
                                    : "CONNECTION CREDENTIAL"}
                            </span>

                            <code>
                                {
                                    enrollment.enrollment_token
                                }
                            </code>

                        </div>

                        {mode === "sensor" && (

                            <div className="command-box">

                                <div className="command-header">

                                    <div>

                                        <span>
                                            INSTALLATION TARGET
                                        </span>

                                        <h3>

                                            {
                                                selectedPlatform?.icon
                                            }{" "}

                                            {
                                                selectedPlatform?.name
                                            }

                                        </h3>

                                    </div>

                                    <span className="pending-badge">
                                        PENDING
                                    </span>

                                </div>

                                <pre>
                                    {command}
                                </pre>

                            </div>

                        )}

                        {mode !== "sensor" && (

                            <div className="command-box">

                                <div className="command-header">

                                    <div>

                                        <span>
                                            CONNECTION TARGET
                                        </span>

                                        <h3>

                                            {mode ===
                                            "cloud"
                                                ? selectedCloudProvider?.icon
                                                : selectedApiPlatform?.icon}{" "}

                                            {mode ===
                                            "cloud"
                                                ? selectedCloudProvider?.name
                                                : selectedApiPlatform?.name}

                                        </h3>

                                    </div>

                                    <span className="pending-badge">
                                        PENDING
                                    </span>

                                </div>

                                <pre>
                                    {mode ===
                                    "cloud"
                                        ? `Provider: ${enrollment.provider || selectedCloudProvider?.name}
Connection ID: ${enrollment.id}
Credential: ${enrollment.enrollment_token}`
                                        : `Platform: ${enrollment.api_platform || selectedApiPlatform?.name}
API URL: ${enrollment.api_url}
Connection ID: ${enrollment.id}
Credential: ${enrollment.enrollment_token}`}
                                </pre>

                            </div>

                        )}

                        <div className="security-note">

                            <span>
                                ◇
                            </span>

                            <div>

                                <strong>
                                    Secure enrollment
                                </strong>

                                <p>
                                    This connection is tied to
                                    your organization and remains
                                    pending until the environment
                                    registers successfully.
                                </p>

                            </div>

                        </div>

                        <div className="install-actions">

                            <button
                                type="button"
                                className="back-button"
                                onClick={() =>
                                    navigate(
                                        "/onboarding"
                                    )
                                }
                            >
                                ← Back
                            </button>

                            <button
                                type="button"
                                className="primary-btn"
                                onClick={() =>
                                    navigate(
                                        "/sensor-setup",
                                        {
                                            state: {
                                                enrollment,
                                                platform,
                                                mode,
                                            },
                                        }
                                    )
                                }
                            >

                                CONTINUE TO{" "}

                                {mode ===
                                "sensor"
                                    ? "SENSOR VERIFICATION"
                                    : mode ===
                                      "cloud"
                                    ? "CLOUD VERIFICATION"
                                    : "API VERIFICATION"}

                                <b>
                                    →
                                </b>

                            </button>

                        </div>

                    </section>

                )}

            </div>
        </main>
    );
}