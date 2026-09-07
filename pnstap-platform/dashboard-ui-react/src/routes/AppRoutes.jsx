import { Routes, Route, Navigate } from "react-router-dom";
import Home from "../pages/Home/Home";
import Login from "../pages/Login/Login";
import Signup from "../pages/Signup/Signup";
import Dashboard from "../pages/Dashboard/Dashboard";
import Onboarding from "../pages/onboarding/onboarding";
import InstallSensor from "../pages/InstallSensor/InstallSensor";
import SensorSetup from "../pages/SensorSetup/SensorSetup";
import { Overview, Simple, Sensors, Integrations, Lyromi, Billing, Settings, Team, Audit } from "../pages/Platform/WorkspacePages";
import { SecurityHub, RiskGraph, Compliance, AttackPaths } from "../pages/Platform/AdvancedPages";
import { Alerts, Network, Assets, Intelligence, Notifications } from "../pages/Platform/OperationalPages";
import { Incidents, Reports, Api } from "../pages/Platform/DeepPages";

export default function AppRoutes(){return <Routes>
    <Route path="/" element={<Home/>}/>
    <Route path="/login" element={<Login/>}/>
    <Route path="/signup" element={<Signup/>}/>
    <Route path="/onboarding" element={<Onboarding/>}/>
    <Route path="/install-sensor" element={<InstallSensor/>}/>
    <Route path="/sensor-setup" element={<SensorSetup/>}/>
    <Route path="/dashboard" element={<Dashboard/>}/>
    <Route path="/workspace" element={<Overview/>}/>
    <Route path="/workspace/security" element={<SecurityHub/>}/>
    <Route path="/workspace/alerts" element={<Alerts/>}/>
    <Route path="/workspace/network" element={<Network/>}/>
    <Route path="/workspace/assets" element={<Assets/>}/>
    <Route path="/workspace/sensors" element={<Sensors/>}/>
    <Route path="/workspace/intelligence" element={<Intelligence/>}/>
    <Route path="/workspace/risk-graph" element={<RiskGraph/>}/>
    <Route path="/workspace/attack-paths" element={<AttackPaths/>}/>
    <Route path="/workspace/compliance" element={<Compliance/>}/>
    <Route path="/workspace/lyromi" element={<Lyromi/>}/>
    <Route path="/workspace/incidents" element={<Incidents/>}/>
    <Route path="/workspace/reports" element={<Reports/>}/>
    <Route path="/workspace/integrations" element={<Integrations/>}/>
    <Route path="/workspace/notifications" element={<Notifications/>}/>
    <Route path="/workspace/team" element={<Team/>}/>
    <Route path="/workspace/billing" element={<Billing/>}/>
    <Route path="/workspace/settings" element={<Settings/>}/>
    <Route path="/workspace/audit" element={<Audit/>}/>
    <Route path="/workspace/api" element={<Api/>}/>
    <Route path="*" element={<Navigate to="/" replace/>}/>
</Routes>}
