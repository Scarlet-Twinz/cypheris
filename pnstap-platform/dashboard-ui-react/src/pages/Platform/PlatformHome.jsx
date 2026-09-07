import { Link } from "react-router-dom";
import "./PlatformPages.css";

const modules=[
 ["Security Command","/workspace/overview","Posture, detections, telemetry and connected environments."],
 ["Context Fabric","/workspace/context","Connect evidence, entities and change history before drawing conclusions."],
 ["Security Hub","/workspace/security","Central security posture and investigation entry point."],
 ["Alert Center","/workspace/alerts","Review evidence-backed findings by severity and status."],
 ["Investigation Workspace","/workspace/investigations","Turn findings into traceable cases with ownership and evidence."],
 ["Asset Inventory","/workspace/assets","Maintain a living view of assets observed across connected environments."],
 ["Identity Center","/workspace/identity","Track identity activity and risk signals as first-class security context."],
 ["Network Intelligence","/workspace/network","Explore observed communication and network telemetry."],
 ["Risk Graph","/workspace/risk-graph","Explore relationships between identities, findings and telemetry."],
 ["Attack Paths","/workspace/attack-paths","Prioritize paths using the evidence currently available."],
 ["Threat Intelligence","/workspace/intelligence","Enrich security observations with external context."],
 ["Security Drift","/workspace/drift","See what changed and which security context may have shifted."],
 ["Security Timeline","/workspace/timeline","Follow the chronology of signals, investigations and changes."],
 ["Evidence Fabric","/workspace/evidence","Trace conclusions back to collected records and sources."],
 ["LYROMI Intelligence","/workspace/lyromi","Ask the Cypheris intelligence layer about your security data."],
 ["Security Reports","/workspace/reports","Build executive and operational posture summaries."],
 ["Developer API","/workspace/api","Connect Cypheris to automation and customer applications."]
];
export default function PlatformHome(){return <div className="platform-shell"><aside className="platform-sidebar"><Link className="platform-brand" to="/"><span className="brand-mark">CY</span><span><strong>Cypheris</strong><small>Security Fabric</small></span></Link><div className="workspace-label">PLATFORM HOME</div><nav><Link className="active" to="/workspace">Home</Link><Link to="/workspace/context">Context Fabric</Link><Link to="/workspace/overview">Command Center</Link><Link to="/workspace/security">Security</Link><Link to="/workspace/investigations">Investigations</Link><Link to="/workspace/risk-graph">Risk Graph</Link><Link to="/workspace/integrations">Integrations</Link><Link to="/workspace/team">Team</Link><Link to="/workspace/billing">Billing</Link><Link to="/workspace/settings">Settings</Link></nav></aside><section className="platform-main"><header className="platform-topbar"><span><i className="live-dot"/>Cypheris Security Fabric</span><Link to="/workspace/overview">Open command center</Link></header><main className="platform-content"><div className="page-heading"><div><span>CYPHERIS / PLATFORM</span><h1>Security operations, connected.</h1><p>Cypheris is organized as a real product surface: specialized domains for telemetry, context, detection, response, intelligence, risk, evidence, reporting and administration.</p></div><Link className="primary-button" to="/workspace/integrations">Connect environment</Link></div><div className="platform-home-grid">{modules.map(([title,path,description],i)=><Link className="platform-module" to={path} key={path}><span className="module-index">{String(i+1).padStart(2,"0")}</span><div><strong>{title}</strong><p>{description}</p></div><b>→</b></Link>)}</div><div className="two-column"><section className="data-card"><div className="card-head"><span>Architecture</span><small>How Cypheris connects</small></div><div className="pipeline"><span>01 Collect</span><span>02 Normalize evidence</span><span>03 Connect context</span><span>04 Prioritize risk</span><span>05 Investigate</span><span>06 Explain</span><span>07 Respond &amp; verify</span></div></section><section className="data-card"><div className="card-head"><span>Product principle</span><small>Evidence over theater</small></div><p>Cypheris does not need to pretend every environment has an attack path. It becomes more useful as authorized sensors, integrations and operator evidence make the security graph more complete.</p></section></div></main></section></div>}
