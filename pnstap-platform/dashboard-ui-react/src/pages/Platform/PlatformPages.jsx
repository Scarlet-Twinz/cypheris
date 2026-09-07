import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./PlatformPages.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const navigation = [
    ["Overview", "/workspace"],
    ["Security", "/workspace/security"],
    ["Alerts", "/workspace/alerts"],
    ["Network", "/workspace/network"],
    ["Assets", "/workspace/assets"],
    ["Sensors", "/workspace/sensors"],
    ["Intelligence", "/workspace/intelligence"],
    ["LYROMI", "/workspace/lyromi"],
    ["Incidents", "/workspace/incidents"],
    ["Reports", "/workspace/reports"],
    ["Integrations", "/workspace/integrations"],
    ["Notifications", "/workspace/notifications"],
    ["Team", "/workspace/team"],
    ["Billing", "/workspace/billing"],
    ["Settings", "/workspace/settings"],
    ["Audit", "/workspace/audit"],
    ["API", "/workspace/api"],
];

function token() {
    return localStorage.getItem("cypheris_access_token");
}

async function api(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
            ...(options.headers || {}),
        },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Request failed.");
    return data;
}

function Shell({ children }) {
    const location = useLocation();
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("cypheris_user") || "null");
    const company = JSON.parse(localStorage.getItem("cypheris_company") || "null");
    const [collapsed, setCollapsed] = useState(false);

    useEffect(() => {
        if (!token()) navigate("/login", { replace: true });
    }, [navigate]);

    const logout = () => {
        localStorage.removeItem("cypheris_access_token");
        localStorage.removeItem("cypheris_token_type");
        localStorage.removeItem("cypheris_user");
        localStorage.removeItem("cypheris_company");
        navigate("/login");
    };

    return (
        <div className={`platform-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
            <aside className="platform-sidebar">
                <Link className="platform-brand" to="/">
                    <span className="brand-mark">CY</span>
                    <span><strong>Cypheris</strong><small>Security Fabric</small></span>
                </Link>
                <div className="workspace-label">COMMAND CENTER</div>
                <nav>
                    {navigation.map(([label, path]) => (
                        <Link key={path} className={location.pathname === path ? "active" : ""} to={path}>
                            <span className="nav-glyph">{label.slice(0, 1)}</span><span>{label}</span>
                        </Link>
                    ))}
                </nav>
                <button className="collapse-button" onClick={() => setCollapsed(!collapsed)}>{collapsed ? ">" : "<"} Collapse</button>
            </aside>
            <section className="platform-main">
                <header className="platform-topbar">
                    <div><span className="live-dot" /> Environment online</div>
                    <div className="topbar-actions"><span>{company?.name || "Organization"}</span><span className="avatar">{(user?.name || "C").slice(0, 1).toUpperCase()}</span><button onClick={logout}>Sign out</button></div>
                </header>
                <main className="platform-content">{children}</main>
            </section>
        </div>
    );
}

function Page({ eyebrow, title, description, children, actions }) {
    return <Shell><div className="page-heading"><div><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div><div className="page-actions">{actions}</div></div>{children}</Shell>;
}

const Card = ({ title, value, meta, children }) => <section className="data-card">{title && <div className="card-head"><span>{title}</span>{meta && <small>{meta}</small>}</div>}{value && <strong className="card-value">{value}</strong>}{children}</section>;
const Table = ({ columns, rows }) => <div className="table-wrap"><table><thead><tr>{columns.map(c => <th key={c}>{c}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>) : <tr><td colSpan={columns.length} className="empty">No records yet.</td></tr>}</tbody></table></div>;

export function WorkspaceOverview() {
    const [data, setData] = useState(null);
    useEffect(() => { api("/api/dashboard/").then(setData).catch(() => setData(null)); }, []);
    const metrics = data?.metrics || {};
    return <Page eyebrow="CYPHERIS / OVERVIEW" title="Security command center" description="A unified view of your organization's security posture, telemetry and response readiness." actions={<Link className="primary-button" to="/workspace/integrations">Connect environment</Link>}>
        <div className="metric-grid"><Card title="Security score" value={`${metrics.security_score ?? "--"}%`} meta="Current posture" /><Card title="Active alerts" value={metrics.active_alerts ?? "--"} meta="Requires attention" /><Card title="Online sensors" value={metrics.online_sensors ?? "--"} meta="Live telemetry" /><Card title="Telemetry" value={metrics.telemetry_total ?? "--"} meta="Observed signals" /></div>
        <div className="two-column"><Card title="Threat posture" meta="Live"><div className="posture"><div className="posture-ring">{metrics.security_score ?? "--"}</div><div><strong>{data?.threat_level || "Monitoring"}</strong><p>Cypheris continuously correlates environment signals and exposes the events that deserve attention.</p></div></div></Card><Card title="Integration fabric" meta="Connected sources"><div className="mini-list"><span>Cloud connections <b>{metrics.cloud_integrations ?? 0}</b></span><span>API connections <b>{metrics.api_integrations ?? 0}</b></span><span>Online integrations <b>{metrics.online_integrations ?? 0}</b></span></div></Card></div>
        <Card title="Recent activity" meta="Latest security events"><Table columns={["Event", "Severity", "Time"]} rows={(data?.activity || []).slice(0, 6).map(item => [item.description || item.action || "Security activity", item.severity || "INFO", item.created_at || "Recent"])} /></Card>
    </Page>;
}

const simplePages = {
    Security: ["SECURITY / POSTURE", "Security posture", "Prioritize the controls, findings and signals shaping your current security state."],
    Alerts: ["SECURITY / ALERTS", "Alert center", "Investigate active detections and move important signals toward resolution."],
    Network: ["SECURITY / NETWORK", "Network intelligence", "Explore traffic, protocols, endpoints and unusual communication patterns."],
    Assets: ["SECURITY / ASSETS", "Asset inventory", "Maintain a living view of infrastructure and the environments connected to Cypheris."],
    Sensors: ["SECURITY / SENSORS", "Sensor fleet", "Enroll and monitor the security sensors providing visibility into your environments."],
    Intelligence: ["INTELLIGENCE", "Threat intelligence", "Turn security observations into contextual intelligence and prioritized findings."],
    Incidents: ["RESPONSE", "Incident workspace", "Organize investigations, ownership, evidence and response progress."],
    Reports: ["REPORTING", "Security reports", "Create executive and operational views of posture, incidents and activity."],
    Notifications: ["COMMUNICATIONS", "Notifications", "Review platform notifications and important organization events."],
    Team: ["ADMINISTRATION", "Team access", "Manage organization members, roles and security access."],
    Audit: ["GOVERNANCE", "Audit trail", "Review security-sensitive actions across your organization."],
    API: ["DEVELOPER PLATFORM", "API access", "Connect Cypheris to your internal systems through controlled APIs and integrations."],
};

export function SimpleWorkspacePage({ name }) {
    const [eyebrow, title, description] = simplePages[name];
    const [query, setQuery] = useState("");
    const rows = useMemo(() => Array.from({ length: 6 }, (_, i) => [`${name} record ${i + 1}`, i % 3 === 0 ? "High" : "Normal", "Monitored", "Awaiting telemetry"]), [name]);
    return <Page eyebrow={eyebrow} title={title} description={description} actions={<button className="secondary-button" onClick={() => setQuery("")}>Reset view</button>}>
        <Card><div className="toolbar"><input value={query} onChange={e => setQuery(e.target.value)} placeholder={`Search ${name.toLowerCase()}...`} /><button className="secondary-button">Export</button><button className="primary-button">Create</button></div><Table columns={["Name", "Priority", "Status", "Context"]} rows={query ? rows.filter(r => r[0].toLowerCase().includes(query.toLowerCase())) : rows} /></Card>
        <div className="metric-grid"><Card title="Monitored" value="--" meta="Live data" /><Card title="Open" value="--" meta="Requires action" /><Card title="Resolved" value="--" meta="Historical" /><Card title="Coverage" value="--" meta="Environment" /></div>
    </Page>;
}

export function LyromiPage() {
    const [message, setMessage] = useState(""); const [reply, setReply] = useState("Ask LYROMI about your environment, an alert, or the meaning of a security signal."); const [busy, setBusy] = useState(false);
    const send = async () => { if (!message.trim()) return; setBusy(true); try { const result = await api("/api/lyromi/chat", { method: "POST", body: JSON.stringify({ message: message.trim() }) }); setReply(result.reply || "LYROMI returned no response."); setMessage(""); } catch (e) { setReply(e.message); } finally { setBusy(false); } };
    return <Page eyebrow="AI SECURITY INTELLIGENCE" title="LYROMI" description="The intelligence layer for interpreting security signals and helping teams understand what deserves attention."><div className="lyromi-grid"><Card title="LYROMI / ANALYSIS"><div className="chat-response">{reply}</div><div className="chat-input"><input value={message} onChange={e => setMessage(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} placeholder="Ask a security question..." /><button className="primary-button" disabled={busy} onClick={send}>{busy ? "Analyzing" : "Ask LYROMI"}</button></div></Card><Card title="Intelligence pipeline"><div className="pipeline"><span>01 Signal ingestion</span><span>02 Context correlation</span><span>03 LYROMI analysis</span><span>04 Human decision</span></div></Card></div></Page>;
}

export function IntegrationsPage() {
    const [items, setItems] = useState([]); const [form, setForm] = useState({ connection_name: "", environment_name: "", provider: "aws", integration_type: "cloud" }); const [message, setMessage] = useState("");
    const load = () => api("/api/integrations").then(r => setItems(r.integrations || [])).catch(() => setItems([])); useEffect(load, []);
    const create = async () => { try { const r = await api("/api/integrations/cloud", { method: "POST", body: JSON.stringify(form) }); setMessage(r.message || "Integration created."); setForm({ connection_name: "", environment_name: "", provider: "aws", integration_type: "cloud" }); load(); } catch (e) { setMessage(e.message); } };
    return <Page eyebrow="CONNECTIVITY" title="Integrations" description="Connect cloud environments, SIEM/EDR platforms and custom security sources to the Cypheris fabric."><Card title="Connect a cloud environment"><div className="form-grid"><input placeholder="Connection name" value={form.connection_name} onChange={e => setForm({...form, connection_name:e.target.value})}/><input placeholder="Environment name" value={form.environment_name} onChange={e => setForm({...form, environment_name:e.target.value})}/><select value={form.provider} onChange={e => setForm({...form, provider:e.target.value})}><option value="aws">AWS</option><option value="azure">Azure</option><option value="gcp">Google Cloud</option></select><button className="primary-button" onClick={create}>Create connection</button></div>{message && <p className="notice">{message}</p>}</Card><Card title="Connected sources"><Table columns={["Connection", "Environment", "Type", "Status"]} rows={items.map(i => [i.connection_name, i.environment_name, i.integration_type, i.status])}/></Card></Page>;
}

export function BillingPage() {
    const [data, setData] = useState(null); const [plans, setPlans] = useState(null); const [message, setMessage] = useState("");
    useEffect(() => { api("/api/billing/subscription").then(r => setData(r.subscription)).catch(() => {}); api("/api/billing/plans").then(setPlans).catch(() => {}); }, []);
    const choose = async plan => { try { const r = await api("/api/billing/select-plan", { method: "POST", body: JSON.stringify({ plan, billing_cycle: "Yearly", payment_provider: plan === "Enterprise" ? "bank_transfer" : "stripe" }) }); setData(r.subscription); setMessage(r.message); } catch(e) { setMessage(e.message); } };
    return <Page eyebrow="ACCOUNT / BILLING" title="Plans & billing" description="Seven days of full-access trial, followed by subscription activation for continued platform access."><Card title="Current subscription"><div className="subscription-banner"><strong>{data?.plan || "Free"}</strong><span>{data?.status || "Loading"}</span><b>{data?.trial_active ? `${data.trial_days_remaining} trial days remaining` : data?.annual_price ? `$${data.annual_price.toLocaleString()}/year` : "$0"}</b></div>{message && <p className="notice">{message}</p>}</Card><div className="pricing-grid">{(plans ? Object.entries(plans.plans) : []).map(([name, plan]) => <article className="pricing-card" key={name}><span>{name}</span><strong>${plan.annual_price.toLocaleString()}</strong><small>/ year</small><p>{name === "Free" ? "1 user · 7-day retention" : `${plan.user_limit >= 1000000 ? "Unlimited" : plan.user_limit + " users"} · ${plan.retention_days}-day retention`}</p><button className="primary-button" onClick={() => choose(name)}>{name === "Enterprise" ? "Contact / select" : `Choose ${name}`}</button></article>)}</div><p className="billing-note">Over-limit users are billed at $10/user/month. Stripe and PayPal are planned payment rails; Enterprise supports bank transfer. Paid activation requires provider configuration and successful payment confirmation.</p></Page>;
}

export function SettingsPage() {
    const company = JSON.parse(localStorage.getItem("cypheris_company") || "null"); const [name, setName] = useState(company?.name || ""); const [primary, setPrimary] = useState("#00E5FF"); const [secondary, setSecondary] = useState("#0A1628");
    return <Page eyebrow="ADMINISTRATION" title="Workspace settings" description="Shape how your organization's Cypheris workspace looks and behaves."><Card title="Organization identity"><div className="branding-preview"><div className="brand-preview-mark" style={{background: primary}}>CY</div><div><strong>{name || "Your organization"}</strong><p>Custom workspace identity</p></div></div><div className="form-grid"><label>Company name<input value={name} onChange={e => setName(e.target.value)}/></label><label>Primary color<input type="color" value={primary} onChange={e => setPrimary(e.target.value)}/></label><label>Secondary color<input type="color" value={secondary} onChange={e => setSecondary(e.target.value)}/></label><button className="primary-button">Save branding</button></div><p className="billing-note">Business includes organization logo + colors; Enterprise expands this into full white-label branding.</p></Card><Card title="Security preferences"><div className="preference-row"><span>Session protection</span><b>Enabled</b></div><div className="preference-row"><span>Audit logging</span><b>Enabled</b></div><div className="preference-row"><span>Security notifications</span><b>Enabled</b></div></Card></Page>;
}

export default function PlatformPages() { return null; }
