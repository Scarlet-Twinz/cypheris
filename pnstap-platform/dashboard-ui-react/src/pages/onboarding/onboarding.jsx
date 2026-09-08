import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./onboarding.css";
import logo from "../../assets/logo/cypheris-logo.jpg";

const choices = [
  { id: "demo", n: "01", title: "Explore the demo environment", label: "FASTEST PATH", text: "Open a controlled synthetic security environment and explore Sentinel, Context, Risk, Investigations and LYROMI before connecting infrastructure." },
  { id: "connect", n: "02", title: "Connect my environment", label: "BRING YOUR DATA", text: "Choose Docker, Kubernetes, AWS, cloud or API onboarding and generate the authenticated setup flow for your environment." },
  { id: "later", n: "03", title: "I'll connect it later", label: "SKIP FOR NOW", text: "Enter the workspace with honest empty states. You can return to Integrations whenever you are ready to connect telemetry." },
];

export default function Onboarding(){
  const navigate=useNavigate();
  const user=useMemo(()=>{try{return JSON.parse(localStorage.getItem("user"))||{}}catch{return {}}},[]);
  const company=useMemo(()=>{try{return JSON.parse(localStorage.getItem("company"))||{}}catch{return {}}},[]);
  const [choice,setChoice]=useState("demo");
  const firstName=user.name?.trim()?.split(/\s+/)[0]||"there";
  const continueFlow=()=>{
    if(choice==="demo"){localStorage.setItem("cypheris_demo_mode","true");navigate("/demo");return;}
    if(choice==="later"){localStorage.setItem("cypheris_onboarding_complete","true");navigate("/workspace");return;}
    navigate("/install-sensor?mode=connect");
  };
  return <main className="onboarding-page"><div className="onboarding-grid"/><header className="onboarding-topbar"><div className="onboarding-brand"><div className="onboarding-brand-mark"><img src={logo} alt="Cypheris"/></div><div><strong>CYPHERIS</strong><span>Powered by PNSTAP™</span></div></div><div className="initializing-state"><span className="pulse-dot"/>14-DAY TRIAL / WORKSPACE READY</div></header><section className="onboarding-content"><div className="onboarding-heading"><span className="onboarding-eyebrow">WELCOME TO CYPHERIS</span><h1>Start with the <span>security picture.</span></h1><p>Welcome, {firstName}. Your workspace for <strong>{company.name||"your organization"}</strong> is ready. You do not need infrastructure connected before you can evaluate Cypheris.</p></div><div className="trial-banner"><div><span>14-DAY FREE TRIAL</span><strong>Explore first. Connect when ready.</strong></div><div><small>NO CREDIT CARD REQUIRED</small><small>DEMO DATA IS CLEARLY LABELED</small></div></div><div className="connection-section"><div className="connection-heading"><div><span>STEP 01 / GET STARTED</span><h2>How do you want to experience Cypheris?</h2></div><div className="selection-status"><span className="status-dot"/>1 PATH SELECTED</div></div><div className="method-grid">{choices.map(item=><button key={item.id} type="button" className={`method-card ${choice===item.id?"active":""}`} onClick={()=>setChoice(item.id)}><div className="method-top"><span className="method-number">{item.n}</span><span className="recommended">{item.label}</span></div><span className="method-label">CYPHERIS</span><h3>{item.title}</h3><p>{item.text}</p><div className="method-footer"><span>{choice===item.id?"SELECTED":"CHOOSE THIS PATH"}</span><span className={`radio ${choice===item.id?"checked":""}`}>{choice===item.id?"✓":""}</span></div></button>)}</div><div className="security-note"><div className="security-symbol">◇</div><div><strong>Your environment remains under your control.</strong><p>Connecting a sensor or integration is optional during evaluation. You can start with synthetic demo data or an honest empty workspace.</p></div><div className="selected-method"><span>NEXT</span><strong>{choices.find(x=>x.id===choice)?.title}</strong></div></div><div className="onboarding-actions"><button type="button" className="back-button" onClick={()=>navigate("/")}>← Back</button><button type="button" className="continue-button" onClick={continueFlow}><span>{choice==="connect"?"Continue to Environment Setup":choice==="demo"?"Explore Cypheris Demo":"Enter Workspace"}</span><b>→</b></button></div></div></section><footer className="onboarding-footer"><span>CYPHERIS COMMAND FABRIC</span><span>PNSTAP™ SECURITY ENGINE</span><span>LYROMI INTELLIGENCE</span></footer></main>;
}
