import { Routes, Route, Navigate } from "react-router-dom";

import Home from "../pages/Home/Home";
import Login from "../pages/Login/Login";
import Signup from "../pages/Signup/Signup";
import Dashboard from "../pages/Dashboard/Dashboard";
import Onboarding from "../pages/onboarding/onboarding";
import InstallSensor from "../pages/InstallSensor/InstallSensor";
import SensorSetup from "../pages/SensorSetup/SensorSetup";
import {
    WorkspaceOverview,
    SimpleWorkspacePage,
    LyromiPage,
    IntegrationsPage,
    BillingPage,
    SettingsPage,
} from "../pages/Platform/PlatformPages";

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/install-sensor" element={<InstallSensor />} />
            <Route path="/sensor-setup" element={<SensorSetup />} />

            {/* Existing dashboard remains available while the new workspace grows around it. */}
            <Route path="/dashboard" element={<Dashboard />} />

            {/* Full multi-surface Cypheris command center. */}
            <Route path="/workspace" element={<WorkspaceOverview />} />
            <Route path="/workspace/security" element={<SimpleWorkspacePage name="Security" />} />
            <Route path="/workspace/alerts" element={<SimpleWorkspacePage name="Alerts" />} />
            <Route path="/workspace/network" element={<SimpleWorkspacePage name="Network" />} />
            <Route path="/workspace/assets" element={<SimpleWorkspacePage name="Assets" />} />
            <Route path="/workspace/sensors" element={<SimpleWorkspacePage name="Sensors" />} />
            <Route path="/workspace/intelligence" element={<SimpleWorkspacePage name="Intelligence" />} />
            <Route path="/workspace/lyromi" element={<LyromiPage />} />
            <Route path="/workspace/incidents" element={<SimpleWorkspacePage name="Incidents" />} />
            <Route path="/workspace/reports" element={<SimpleWorkspacePage name="Reports" />} />
            <Route path="/workspace/integrations" element={<IntegrationsPage />} />
            <Route path="/workspace/notifications" element={<SimpleWorkspacePage name="Notifications" />} />
            <Route path="/workspace/team" element={<SimpleWorkspacePage name="Team" />} />
            <Route path="/workspace/billing" element={<BillingPage />} />
            <Route path="/workspace/settings" element={<SettingsPage />} />
            <Route path="/workspace/audit" element={<SimpleWorkspacePage name="Audit" />} />
            <Route path="/workspace/api" element={<SimpleWorkspacePage name="API" />} />

            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
