import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import logo from "../../assets/logo/cypheris-logo.jpg";
import "./Invite.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function Invite(){
  const {token}=useParams(); const navigate=useNavigate(); const [password,setPassword]=useState(""); const [confirm,setConfirm]=useState(""); const [busy,setBusy]=useState(false); const [msg,setMsg]=useState("");
  const accept=async()=>{if(password.length<8)return setMsg("Use at least 8 characters for your password.");if(password!==confirm)return setMsg("Passwords do not match.");setBusy(true);setMsg("");try{const r=await fetch(`${API}/api/workspace/invitations/accept`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token,password})});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||"Invitation could not be accepted.");setMsg("Account created. You can now sign in.");setTimeout(()=>navigate("/login"),700)}catch(e){setMsg(e.message)}finally{setBusy(false)}};
  return <main className="invite-page"><section className="invite-card"><Link to="/" className="invite-brand"><img src={logo} alt="Cypheris"/><strong>Cypheris</strong></Link><span className="eyebrow">WORKSPACE INVITATION</span><h1>Join the security workspace.</h1><p>Create your account password to accept this organization invitation.</p><input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)}/><input type="password" placeholder="Confirm password" value={confirm} onChange={e=>setConfirm(e.target.value)}/><button className="invite-button" disabled={busy} onClick={accept}>{busy?"Creating account…":"Accept invitation"}</button>{msg&&<div className="invite-message">{msg}</div>}<Link to="/login" className="invite-back">Already have an account? Sign in</Link></section></main>
}
