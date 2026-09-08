import React, { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";
import "cesium/Build/Cesium/Widgets/widgets.css";
import cypherisLogo from "../../assets/logo/cypheris-logo.jpg";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const NAV = [
  ["Overview", "⌂"],
  ["Threat Intelligence", "⚡"],
  ["Assets", "◈"],
  ["Incidents", "!"],
  ["Analytics", "◫"],
  ["LYROMI", "✦"],
  ["Billing", "◇"],
  ["Settings", "⚙"],
];

function stored(key) {
  try { return JSON.parse(localStorage.getItem(key) || "{}"); } catch { return {}; }
}

function token() { return localStorage.getItem("access_token") || localStorage.getItem("token") || ""; }

function text(value, fallback = "") {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "object") return value.name || value.title || value.message || value.label || fallback;
  return String(value);
}

function number(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function severity(event) {
  const value = text(event?.severity || event?.level || event?.priority).toLowerCase();
  return ["critical", "high", "medium", "low"].includes(value) ? value : "info";
}

function relative(value) {
  if (!value) return "recent";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "recent";
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function greeting() {
  const hour = new Date().getHours();
  return hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
}

function Globe({ signals = [], threats = [] }) {
  const host = useRef(null);
  const viewer = useRef(null);
  const entities = useRef([]);
  const [status, setStatus] = useState("INITIALIZING");

  useEffect(() => {
    let disposed = false;
    let instance = null;
    const start = async () => {
      try {
        const Cesium = await import("cesium");
        if (disposed || !host.current) return;

        instance = new Cesium.Viewer(host.current, {
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
          scene3DOnly: true,
          terrainProvider: new Cesium.EllipsoidTerrainProvider(),
          imageryProvider: new Cesium.OpenStreetMapImageryProvider({
            url: "https://tile.openstreetmap.org/",
          }),
        });

        if (disposed) { instance.destroy(); return; }
        viewer.current = instance;
        instance.scene.backgroundColor = Cesium.Color.fromCssColorString("#050912");
        instance.scene.globe.show = true;
        instance.scene.globe.enableLighting = false;
        instance.scene.globe.baseColor = Cesium.Color.fromCssColorString("#0c1827");
        instance.scene.fog.enabled = false;
        instance.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(8, 18, 20500000),
          orientation: {
            heading: 0,
            pitch: Cesium.Math.toRadians(-90),
            roll: 0,
          },
        });
        instance.resize();
        setStatus("LIVE");
      } catch (error) {
        console.error("Cesium initialization failed:", error);
        setStatus("UNAVAILABLE");
      }
    };
    start();
    return () => {
      disposed = true;
      if (instance && !instance.isDestroyed()) instance.destroy();
      viewer.current = null;
    };
  }, []);

  useEffect(() => {
    const instance = viewer.current;
    if (!instance) return;
    let cancelled = false;
    const update = async () => {
      const Cesium = await import("cesium");
      if (cancelled || instance.isDestroyed()) return;
      entities.current.forEach((entity) => instance.entities.remove(entity));
      entities.current = [];
      const add = (item, color, size, label) => {
        const lat = number(item?.lat ?? item?.latitude);
        const lon = number(item?.lon ?? item?.lng ?? item?.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon) || (lat === 0 && lon === 0)) return;
        const entity = instance.entities.add({
          position: Cesium.Cartesian3.fromDegrees(lon, lat, 100000),
          point: {
            pixelSize: size,
            color,
            outlineColor: Cesium.Color.WHITE.withAlpha(0.8),
            outlineWidth: 2,
            disableDepthTestDistance: Number.POSITIVE_INFINITY,
          },
          label: {
            text: label,
            font: "11px Inter, Segoe UI, sans-serif",
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 3,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            pixelOffset: new Cesium.Cartesian2(0, -20),
            showBackground: true,
            backgroundColor: Cesium.Color.fromCssColorString("#07101c").withAlpha(0.85),
            disableDepthTestDistance: Number.POSITIVE_INFINITY,
          },
        });
        entities.current.push(entity);
      };
      signals.forEach((item) => add(item, Cesium.Color.CYAN.withAlpha(0.95), 8, text(item?.name || item?.sensor_name || item?.sensor, "Signal")));
      threats.forEach((item) => add(item, Cesium.Color.RED.withAlpha(0.95), 12, text(item?.title || item?.name || item?.message, "Threat")));
    };
    update();
    return () => { cancelled = true; };
  }, [signals, threats]);

  return (
    <div className="globe-host">
      <div ref={host} className="cesium-globe" />
      {status === "UNAVAILABLE" && <div className="globe-fallback">Cesium could not initialize. Check the browser console for the WebGL error.</div>}
      <div className="globe-chrome top-left"><span>GLOBAL SECURITY FIELD</span><b><i /> {status}</b></div>
      <div className="globe-chrome bottom-left"><span>{signals.length} active signals</span><span>{threats.length} critical threats</span></div>
    </div>
  );
}

function Activity({ items }) {
  return (
    <section className="activity-panel">
      <div className="section-head">
        <div><span>LIVE TELEMETRY</span><h2>Security activity</h2></div>
        <span className="head-live"><i /> LIVE</span>
      </div>
      <div className="activity-stream">
        {items.length === 0 ? (
          <div className="empty-activity"><span>◌</span><strong>Waiting for telemetry</strong><small>Connected sensors and integrations will appear here as events arrive.</small></div>
        ) : items.slice(0, 8).map((event, index) => (
          <div className={`activity-row ${severity(event)}`} key={event.id || event.event_id || index}>
            <i className="activity-marker" />
            <div><strong>{text(event.title || event.alert_type || event.message, "Security event")}</strong><small>{text(event.description || event.location || event.source, "Cypheris security network")}</small></div>
            <time>{relative(event.timestamp || event.created_at || event.detected_at)}</time>
          </div>
        ))}
      </div>
    </section>
  );
}

function Lyromi({ userName }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    const value = input.trim();
    if (!value || loading) return;
    setMessages((current) => [...current, { role: "user", text: value }]);
    setInput("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/lyromi/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
        },
        body: JSON.stringify({ message: value }),
      });
      let data = {};
      try { data = await response.json(); } catch { data = {}; }
      if (!response.ok) throw new Error(data?.detail || "LYROMI could not process the request.");
      setMessages((current) => [...current, { role: "lyromi", text: text(data?.reply || data?.response, "LYROMI returned no analysis.") }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "lyromi", text: error.message || "LYROMI is temporarily unavailable." }]);
    } finally { setLoading(false); }
  };

  return (
    <section className="lyromi-panel">
      <div className="section-head">
        <div><span>INTELLIGENCE ENGINE</span><h2>LYROMI</h2></div>
        <span className="head-live ai"><i /> READY</span>
      </div>
      <div className="lyromi-body">
        <div className="lyromi-identity">
          <img src={cypherisLogo} alt="Cypheris" />
          <div><strong>LYROMI</strong><small>Cypheris Intelligence Engine</small></div>
          <span className="lyromi-online">ONLINE</span>
        </div>
        <div className="chat-stream">
          {messages.length === 0 && (
            <div className="chat-welcome">
              <img src={cypherisLogo} alt="Cypheris" />
              <strong>{greeting()}, {userName || "Operator"}.</strong>
              <p>Ask LYROMI about the security context in your Cypheris workspace.</p>
            </div>
          )}
          {messages.map((message, index) => (
            <div className={`chat-message ${message.role}`} key={index}>
              {message.role === "lyromi" && <img src={cypherisLogo} alt="LYROMI" />}
              <div><span>{message.role === "user" ? "YOU" : "LYROMI"}</span><p>{message.text}</p></div>
            </div>
          ))}
          {loading && <div className="chat-message lyromi"><img src={cypherisLogo} alt="LYROMI" /><div><span>LYROMI</span><p className="typing">Analyzing security context…</p></div></div>}
        </div>
        <div className="lyromi-composer">
          <input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === "Enter" && send()} placeholder="Ask LYROMI about your environment…" aria-label="Ask LYROMI" />
          <button type="button" onClick={send} disabled={!input.trim() || loading}>{loading ? "…" : "→"}</button>
        </div>
      </div>
    </section>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const user = stored("user");
  const company = stored("company");
  const [collapsed, setCollapsed] = useState(false);
  const [time, setTime] = useState(new Date());
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token()) { navigate("/login", { replace: true }); return undefined; }
    const clock = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(clock);
  }, [navigate]);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/dashboard/`, { headers: { Authorization: `Bearer ${token()}` } });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload?.detail || "Unable to load security telemetry.");
        if (active) { setData(payload?.data || payload); setError(""); }
      } catch (err) { if (active) setError(err.message || "Unable to synchronize security telemetry."); }
    };
    load();
    const refresh = setInterval(load, 30000);
    return () => { active = false; clearInterval(refresh); };
  }, []);

  const activity = Array.isArray(data?.activity) ? data.activity : [];
  const threats = activity.filter((item) => severity(item) === "critical");
  const signalCount = number(data?.telemetry?.network_flows) + number(data?.telemetry?.notifications) + number(data?.telemetry?.sensors);
  const initials = text(user?.name || user?.full_name, "Operator").slice(0, 1).toUpperCase();
  const threatCounts = useMemo(() => ["critical", "high", "medium", "low"].map((level) => ({ level, count: activity.filter((item) => severity(item) === level).length })), [activity]);

  const logout = () => {
    ["access_token", "token", "user", "company"].forEach((key) => localStorage.removeItem(key));
    navigate("/login", { replace: true });
  };

  if (error && !data) return <div className="dashboard-state"><strong>CYTHERIS CONTROL PLANE</strong><span>{error}</span><button onClick={() => window.location.reload()}>RETRY</button></div>;

  return (
    <div className={`cypheris-dashboard ${collapsed ? "is-collapsed" : ""}`}>
      <aside className="sidebar">
        <div className="brand"><img src={cypherisLogo} alt="Cypheris" /><div><strong>CYPHERIS</strong><small>DECODE YOUR SECURITY</small></div></div>
        <div className="workspace-label"><span>WORKSPACE</span><strong>{text(company?.name || company?.company_name, "Security workspace")}</strong></div>
        <nav>{NAV.map(([label, icon], index) => <button key={label} className={index === 0 ? "active" : ""} type="button"><span>{icon}</span><b>{label}</b></button>)}</nav>
        <div className="sidebar-bottom"><div className="system-state"><i /> SYSTEM ONLINE</div><button className="logout" type="button" onClick={logout}>⏻ <b>Sign Out</b></button></div>
        <button className="collapse" type="button" onClick={() => setCollapsed((value) => !value)} aria-label="Toggle sidebar">{collapsed ? "→" : "←"}</button>
      </aside>

      <main className="dashboard-main">
        <header className="topbar">
          <div><span>COMMAND CENTER</span><em>/</em><strong>SECURITY OVERVIEW</strong></div>
          <div className="topbar-right"><span className="live"><i /> LIVE</span><time>{time.toLocaleTimeString()}</time><span className="avatar">{initials}</span></div>
        </header>

        <div className="dashboard-content">
          <section className="hero">
            <div><span className="eyebrow">CYBERSECURITY OPERATIONS</span><h1>{greeting()}, <mark>{text(user?.name || user?.full_name, "Operator")}</mark></h1><p>One security field. One operational picture.</p><small>Cypheris correlates telemetry, context, relationships and risk into a single command surface.</small></div>
            <div className="health"><i /><div><span>CONTROL PLANE</span><strong>{error ? "DEGRADED" : "OPERATIONAL"}</strong></div></div>
          </section>

          <section className="metric-strip">
            <div><span>ACTIVE THREATS</span><strong className="danger">{number(data?.threats)}</strong><small>requiring attention</small></div>
            <div><span>SECURITY SCORE</span><strong>{number(data?.security_score)}%</strong><small>current posture</small></div>
            <div><span>EVENTS</span><strong>{number(data?.events).toLocaleString()}</strong><small>observed signals</small></div>
            <div><span>SENSORS</span><strong>{number(data?.integrations?.sensors)}</strong><small>connected sources</small></div>
            <div><span>ONLINE SOURCES</span><strong>{number(data?.integrations?.online)}</strong><small>active integrations</small></div>
          </section>

          <section className="command-layout">
            <Globe signals={data?.signals || []} threats={threats} />
            <Activity items={activity} />
          </section>

          <section className="intelligence-layout">
            <Lyromi userName={text(user?.name || user?.full_name, "Operator")} />
            <div className="posture-panel">
              <div className="section-head"><div><span>RISK POSTURE</span><h2>Security distribution</h2></div><strong>{number(data?.security_score)}%</strong></div>
              <div className="posture-bars">{threatCounts.map(({ level, count }) => <div key={level}><div><span>{level}</span><b>{count}</b></div><div className="bar"><i className={level} style={{ width: `${Math.min(100, count * 12)}%` }} /></div></div>)}</div>
              <div className="posture-foot"><span>TELEMETRY SOURCES</span><strong>{signalCount}</strong><small>Signals currently represented in the command plane</small></div>
            </div>
          </section>

          <footer><span>CYPHERIS · PNSTAP SECURITY ENGINE</span><span>TELEMETRY → CONTEXT → RISK → RESPONSE</span></footer>
        </div>
      </main>
    </div>
  );
}
