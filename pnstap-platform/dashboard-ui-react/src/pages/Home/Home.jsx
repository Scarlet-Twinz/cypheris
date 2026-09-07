import { Link } from "react-router-dom";
import logo from "../../assets/logo/cypheris-logo.jpg";
import "./Home.css";

const capabilities = [
  ["01", "Connect", "Bring authorized sensors, cloud environments and security integrations into one workspace."],
  ["02", "Contextualize", "Correlate assets, identities, network observations, alerts and evidence instead of treating them as isolated records."],
  ["03", "Prioritize", "Use risk context, attack paths and choke points to focus attention where the available evidence matters most."],
  ["04", "Investigate", "Move from detection into an investigation workspace with evidence, timeline, ownership and response state."],
  ["05", "Understand change", "Security Drift shows what changed, when it changed and which part of the environment was affected."],
  ["06", "Explain", "LYROMI is grounded in the workspace data so its answers can point back to security context rather than inventing events."],
];

const productAreas = [
  ["Security Command", "/workspace/overview"], ["Context Fabric", "/workspace/context"],
  ["Risk Graph", "/workspace/risk-graph"], ["Investigations", "/workspace/investigations"],
  ["Identity Center", "/workspace/identity"], ["Security Drift", "/workspace/drift"],
  ["Security Timeline", "/workspace/timeline"], ["Evidence Fabric", "/workspace/evidence"],
  ["LYROMI Intelligence", "/workspace/lyromi"], ["Integrations", "/workspace/integrations"],
  ["Reports", "/workspace/reports"], ["Developer API", "/workspace/api"],
];

export default function Home() {
  return (
    <div className="home-page">
      <header className="home-nav">
        <Link to="/" className="home-brand"><img src={logo} alt="Cypheris" /><span><strong>Cypheris</strong><small>Decode Your Security</small></span></Link>
        <nav><a href="#platform">Platform</a><a href="#how">How it works</a><a href="#intelligence">LYROMI</a><a href="#architecture">Architecture</a></nav>
        <div className="home-actions"><Link to="/login" className="home-login">Sign in</Link><Link to="/signup" className="home-cta">Create workspace <span>→</span></Link></div>
      </header>

      <main>
        <section className="home-hero">
          <div className="hero-grid" />
          <div className="hero-copy">
            <div className="eyebrow"><i /> SECURITY INTELLIGENCE PLATFORM</div>
            <h1>See the security story.<br /><span>Understand what changed.</span></h1>
            <p>Cypheris connects authorized telemetry, security integrations and organizational context into an evidence-backed security fabric built for investigation, prioritization and response.</p>
            <div className="hero-actions"><Link to="/signup" className="home-cta large">Create your workspace <span>→</span></Link><a href="#platform" className="home-outline">Explore the platform</a></div>
            <div className="hero-note"><span>NO FABRICATED SECURITY DATA</span><span>·</span><span>AUTHENTICATED WORKSPACES</span><span>·</span><span>EVIDENCE FIRST</span></div>
          </div>
          <div className="hero-console" aria-label="Cypheris platform architecture preview">
            <div className="console-top"><span className="console-dot" /><span>CYPHERIS / SECURITY FABRIC</span><b>CONTEXT</b></div>
            <div className="console-map"><div className="map-ring ring-1" /><div className="map-ring ring-2" /><div className="map-ring ring-3" /><div className="map-node center"><img src={logo} alt="" /><strong>CY</strong><small>WORKSPACE</small></div><div className="map-node node-a"><strong>ASSET</strong><small>inventory</small></div><div className="map-node node-b"><strong>IDENTITY</strong><small>access</small></div><div className="map-node node-c"><strong>TELEMETRY</strong><small>sensor</small></div><div className="map-node node-d"><strong>FINDING</strong><small>evidence</small></div></div>
            <div className="console-bottom"><span>01 Connect</span><span>02 Correlate</span><span>03 Prioritize</span><span>04 Investigate</span></div>
          </div>
        </section>

        <section className="principle-strip"><div><strong>Security signals</strong><span>become connected context</span></div><div><strong>Connected context</strong><span>becomes defensible priority</span></div><div><strong>Defensible priority</strong><span>becomes an investigation</span></div></section>

        <section className="home-section" id="platform">
          <div className="section-heading"><div><span className="eyebrow">THE CYPHERIS MODEL</span><h2>Not another alert wall.</h2></div><p>Cypheris is structured around the questions a security team actually needs to answer: what is connected, what changed, what matters, why it matters and what evidence supports the conclusion?</p></div>
          <div className="capability-grid">{capabilities.map(([n,title,text]) => <article key={n}><span>{n}</span><h3>{title}</h3><p>{text}</p></article>)}</div>
        </section>

        <section className="home-section dark-section" id="how">
          <div className="section-heading"><div><span className="eyebrow">FROM SIGNAL TO DECISION</span><h2>One continuous security workflow.</h2></div><p>The product does not require every environment to look active. Empty states are honest until a customer connects a source.</p></div>
          <div className="workflow"><div><span>01</span><strong>Collect</strong><p>Authorized sensors and integrations provide observations.</p></div><div><span>02</span><strong>Connect</strong><p>Assets, identities, findings and activity form relationships.</p></div><div><span>03</span><strong>Prioritize</strong><p>Risk context surfaces the most meaningful relationships.</p></div><div><span>04</span><strong>Investigate</strong><p>Evidence and timeline give analysts a defensible case.</p></div><div><span>05</span><strong>Respond</strong><p>Ownership, status and reporting carry the case forward.</p></div></div>
        </section>

        <section className="home-section" id="intelligence"><div className="lyromi-panel"><div><span className="eyebrow">LYROMI / CONTEXTUAL INTELLIGENCE</span><h2>AI that starts with your evidence.</h2><p>LYROMI is designed to reason over the information Cypheris actually has access to. If the workspace does not contain the evidence needed to answer a question, the system should say so instead of manufacturing a security event.</p><Link to="/signup" className="home-cta">Build a workspace for LYROMI <span>→</span></Link></div><div className="ai-card"><div className="ai-line"><i /> CONTEXT AVAILABLE</div><div className="ai-question">“What changed before this investigation?”</div><div className="ai-answer">Timeline + drift + evidence can be correlated here once your environment provides the relevant records.</div><div className="ai-footer">GROUNDED RESPONSE MODEL</div></div></div></section>

        <section className="home-section" id="architecture"><div className="section-heading"><div><span className="eyebrow">PLATFORM SURFACE</span><h2>Every major domain has a home.</h2></div><p>The workspace is intentionally modular so Cypheris can grow into a web platform, installable desktop component and mobile companion without turning the product into one oversized screen.</p></div><div className="product-area-grid">{productAreas.map(([name,path]) => <Link key={path} to={path}><span>{name}</span><b>→</b></Link>)}</div></section>

        <section className="home-final"><span className="eyebrow">CYPHERIS SECURITY FABRIC</span><h2>Build the security picture before you make the decision.</h2><p>Connect an authorized environment and let the evidence shape what Cypheris shows you.</p><Link to="/signup" className="home-cta large">Create workspace <span>→</span></Link></section>
      </main>
      <footer className="home-footer"><Link to="/"><img src={logo} alt="Cypheris" /></Link><span>Cypheris · Decode Your Security</span><div><Link to="/login">Sign in</Link><Link to="/signup">Create workspace</Link></div></footer>
    </div>
  );
}
