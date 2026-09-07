import { Routes, Route, Navigate } from "react-router-dom";

import Home from "../pages/Home/Home";
import Login from "../pages/Login/Login";
import Signup from "../pages/Signup/Signup";
import Dashboard from "../pages/Dashboard/Dashboard";
import Onboarding from "../pages/onboarding/onboarding";
import InstallSensor from "../pages/InstallSensor/InstallSensor";
import SensorSetup from "../pages/SensorSetup/SensorSetup";

export default function AppRoutes() {
    return (
        <Routes>

            {/* PUBLIC HOMEPAGE */}
            <Route
                path="/"
                element={<Home />}
            />

            {/* AUTHENTICATION */}
            <Route
                path="/login"
                element={<Login />}
            />

            <Route
                path="/signup"
                element={<Signup />}
            />

            {/* APPLICATION */}
            <Route
                path="/onboarding"
                element={<Onboarding />}
            />

            <Route
                path="/install-sensor"
                element={<InstallSensor />}
            />

            <Route
                path="/sensor-setup"
                element={<SensorSetup />}
            />

            <Route
                path="/dashboard"
                element={<Dashboard />}
            />

            {/* UNKNOWN URL */}
            <Route
                path="*"
                element={<Navigate to="/" replace />}
            />

        </Routes>
    );
}