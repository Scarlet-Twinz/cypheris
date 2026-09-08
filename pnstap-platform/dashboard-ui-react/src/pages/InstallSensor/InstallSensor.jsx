import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./InstallSensor.css";
import cypherisLogo from "../../assets/logo/cypheris-logo.jpg";

const API_URL = "http://127.0.0.1:8000";

const platforms = [
    { id: "windows", icon: "🪟", name: "Windows", description: "Install the Cypheris sensor on a Windows server or workstation." },
    { id: "ubuntu", icon: "🐧", name: "Ubuntu / Linux", description: "Deploy the sensor on an Ubuntu or compatible Linux environment." },
    { id: "docker", icon: "🐳", name: "Docker", description: "Run the Cypheris sensor as a containerized workload." },
    { id: "kubernetes", icon: "☸", name: "Kubernetes", description: "Deploy the Cypheris sensor inside a Kubernetes cluster." },
];
const cloudProviders = [
    { id: "aws", icon: "☁", name: "AWS", description: "Connect your Amazon Web Services environment." },
    { id: "azure", icon: "☁", name: "Azure", description: "Connect your Microsoft Azure environment." },
    { id: "gcp", icon: "☁", name: "Google Cloud", description: "Connect your Google Cloud environment." },
];
const apiPlatforms = [
    { id: "siem", icon: "◈", name: "SIEM", description: "Connect an existing security information and event platform." },
    { id: "edr", icon: "◇", name: "EDR / XDR", description: "Connect endpoint security telemetry." },
    { id: "custom", icon: "⌁", name: "Custom Security API", description: "Connect your existing security data source." },
];
const installCommands = {
    windows: `CypherisSensor.exe --enrollment-token <TOKEN>`,
    ubuntu: `curl -fsSL https://install.cypheris.io/linux | sudo bash\ncypheris-sensor enroll --token <TOKEN>`,
    docker: `docker run -d \\\n  --name cypheris-sensor \\\n  -e CYPHERIS_ENROLLMENT_TOKEN=<TOKEN> \\\n  cypheris/sensor:latest`,
    kubernetes: `kubectl create secret generic cypheris-enrollment \\\n  --from-literal=token=<TOKEN>\n\nkubectl apply -f cypheris-sensor.yaml`,
};

const getToken = () => localStorage.getItem("access_token") || localStorage.getItem("token") || "";

export default function InstallSensor() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const mode = searchParams.get("mode") === "cloud" ? "cloud" : searchParams.get("mode") === "api" ? "api" : "sensor";
    const company = useMemo(() => { try { return JSON.parse(localStorage.getItem("company")) || {}; } catch { return {}; } }, []);
    const user = useMemo(() => { try { return JSON.parse(localStorage.getItem("user")) || {}; } catch { return {}; } }, []);
    const [sensorName, setSensorName] = useState("");
    const [environmentName, setEnvironmentName] = useState("");
    const [environmentType, setEnvironmentType] = useState("infrastructure");
    const [platform, setPlatform] = useState("windows");
    const [cloudProvider, setCloudProvider] = useState("aws");
    const [apiPlatform, setApiPlatform] = useState("siem");
    const [apiUrl, setApiUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [enrollment, setEnrollment] = useState(null);
    const firstName = typeof user.name === "string" && user.name.trim() ? user.name.trim().split(/\s+/)[0] : "there";
    const selectedPlatform = platforms.find(item => item.id === platform);
    const selectedCloudProvider = cloudProviders.find(item => item.id === cloudProvider);
    const selectedApiPlatform = apiPlatforms.find(item => item.id === apiPlatform);
    const getPageTitle = () => mode === "cloud" ? "Connect your cloud infrastructure." : mode === "api" ? "Connect your security API." : "Connect your infrastructure.";
    const getPageDescription = () => mode === "cloud" ? <>Welcome, {firstName}. Create a secure cloud connection for your organization's environment.</> : mode === "api" ? <>Welcome, {firstName}. Create a secure integration connection for your organization's security platform.</> : <>Welcome, {firstName}. Create an enrollment for the first PNSTAP Security Sensor in your organization's environment.</>;

    const authorizedRequest = async (url, body) => {
        const token = getToken();
        if (!token) throw new Error("Your authentication session could not be found. Please sign in again.");
        return fetch(url, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(body) });
    };

    const parseResponse = async (response, fallback) => {
        let data = null;
        try { data = await response.json(); } catch { data = null; }
        if (!response.ok) {
            const message = typeof data?.detail === "string" ? data.detail : Array.isArray(data?.detail) ? data.detail.map(item => item?.msg || "Invalid information.").join(", ") : fallback;
            throw new Error(message);
        }
        return data;
    };

    const handleEnrollment = async (event) => {
        event.preventDefault();
        setError("");
        if (!company.id) return setError("Your organization session could not be found. Please sign in again.");
        if (!sensorName.trim()) return setError(mode === "sensor" ? "Please enter a sensor name." : "Please enter a connection name.");
        if (!environmentName.trim()) return setError("Please enter an environment name.");
        if (mode === "api" && !apiUrl.trim()) return setError("Please enter the security API URL.");
        setLoading(true);
        try {
            let data;
            if (mode === "sensor") {
                data = await parseResponse(await authorizedRequest(`${API_URL}/api/sensors/enroll`, { company_id: Number(company.id), sensor_name: sensorName.trim(), environment_name: environmentName.trim(), environment_type: environmentType }), "Unable to create the sensor enrollment.");
                setEnrollment(data?.enrollment || null);
            } else if (mode === "cloud") {
                data = await parseResponse(await authorizedRequest(`${API_URL}/api/integrations/cloud`, { company_id: Number(company.id), connection_name: sensorName.trim(), environment_name: environmentName.trim(), environment_type: environmentType, provider: cloudProvider }), "Unable to create the cloud connection.");
                setEnrollment(data?.integration || null);
            } else {
                data = await parseResponse(await authorizedRequest(`${API_URL}/api/integrations/api`, { company_id: Number(company.id), connection_name: sensorName.trim(), environment_name: environmentName.trim(), environment_type: environmentType, api_platform: apiPlatform, api_url: apiUrl.trim() }), "Unable to create the security API connection.");
                setEnrollment(data?.integration || null);
            }
        } catch (err) {
            console.error("CYPHERIS CONNECTION ERROR:", err);
            setError(err?.message || "Unable to connect to the Cypheris security service.");
        } finally { setLoading(false); }
    };

    const command = enrollment && mode === "sensor" ? installCommands[platform].replaceAll("<TOKEN>", enrollment.enrollment_token) : "";

    return (
        <main className="install-page">
            <div className="install-card">
                <div className="install-header">
                    <div><small>{mode === "sensor" ? "SENSOR DEPLOYMENT / STEP 02" : mode === "cloud" ? "CLOUD CONNECTION / STEP 02" : "API INTEGRATION / STEP 02"}</small><h1>{getPageTitle()}</h1><p>{getPageDescription()}</p></div>
                    <div className="install-status"><span className="status-dot" />{mode === "sensor" ? "SENSOR ENROLLMENT" : mode === "cloud" ? "CLOUD ENROLLMENT" : "API ENROLLMENT"}</div>
                </div>
                <div className="organization-banner"><div className="organization-avatar"><img className="cypheris-logo" src={cypherisLogo} alt="Cypheris" /></div><div><small>ORGANIZATION</small><strong>{company.name || "Your organization"}</strong></div><div className="organization-id">COMPANY ID<strong>{company.id || "—"}</strong></div></div>
                {!enrollment ? <form onSubmit={handleEnrollment}>
                    <section className="install-section"><div className="section-heading"><span>01</span><div><strong>{mode === "sensor" ? "Sensor identity" : "Connection identity"}</strong><small>Define the environment Cypheris will monitor.</small></div></div><div className="install-grid"><label><span>{mode === "sensor" ? "Sensor name" : "Connection name"}</span><input value={sensorName} onChange={e => setSensorName(e.target.value)} placeholder={mode === "sensor" ? "Production Sensor" : "Production Connection"} /></label><label><span>Environment name</span><input value={environmentName} onChange={e => setEnvironmentName(e.target.value)} placeholder="Production" /></label><label><span>Environment type</span><select value={environmentType} onChange={e => setEnvironmentType(e.target.value)}><option value="infrastructure">Infrastructure</option><option value="production">Production</option><option value="staging">Staging</option><option value="development">Development</option></select></label></div></section>
                    {mode === "sensor" && <section className="install-section"><div className="section-heading"><span>02</span><div><strong>Deployment target</strong><small>Choose where the sensor will run.</small></div></div><div className="choice-grid">{platforms.map(item => <button type="button" key={item.id} className={`choice-card ${platform === item.id ? "active" : ""}`} onClick={() => setPlatform(item.id)}><span>{item.icon}</span><strong>{item.name}</strong><small>{item.description}</small></button>)}</div></section>}
                    {mode === "cloud" && <section className="install-section"><div className="section-heading"><span>02</span><div><strong>Cloud provider</strong><small>Select the cloud environment.</small></div></div><div className="choice-grid">{cloudProviders.map(item => <button type="button" key={item.id} className={`choice-card ${cloudProvider === item.id ? "active" : ""}`} onClick={() => setCloudProvider(item.id)}><span>{item.icon}</span><strong>{item.name}</strong><small>{item.description}</small></button>)}</div></section>}
                    {mode === "api" && <section className="install-section"><div className="section-heading"><span>02</span><div><strong>Security platform</strong><small>Select the source and endpoint.</small></div></div><div className="choice-grid">{apiPlatforms.map(item => <button type="button" key={item.id} className={`choice-card ${apiPlatform === item.id ? "active" : ""}`} onClick={() => setApiPlatform(item.id)}><span>{item.icon}</span><strong>{item.name}</strong><small>{item.description}</small></button>)}</div><label><span>API URL</span><input type="url" value={apiUrl} onChange={e => setApiUrl(e.target.value)} placeholder="https://security.example.com/api" /></label></section>}
                    {error && <div className="install-error"><span>!</span>{error}</div>}
                    <div className="install-actions"><button type="button" onClick={() => navigate("/dashboard")}>← Back to dashboard</button><button type="submit" disabled={loading}>{loading ? "CONNECTING..." : mode === "sensor" ? "CREATE SENSOR ENROLLMENT" : "CREATE CONNECTION"}<b>→</b></button></div>
                </form> : <section className="enrollment-result"><div className="result-heading"><span>CONNECTION READY</span><h2>{mode === "sensor" ? "Sensor enrollment created." : "Integration created."}</h2><p>Your authenticated connection has been registered with Cypheris.</p></div>{command && <pre>{command}</pre>}<button type="button" onClick={() => navigate("/dashboard")}>Return to dashboard →</button></section>}
            </div>
        </main>
    );
}
