import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "../Sidebar/Sidebar";

import "./MainLayout.css";

export default function MainLayout({ children }) {
    const [collapsed, setCollapsed] = useState(() => {
        return localStorage.getItem("cypheris_sidebar_collapsed") === "true";
    });

    useEffect(() => {
        localStorage.setItem(
            "cypheris_sidebar_collapsed",
            String(collapsed)
        );
    }, [collapsed]);

    return (
        <div
            className={`app-layout ${
                collapsed ? "sidebar-collapsed" : ""
            }`}
        >
            <Sidebar
                collapsed={collapsed}
                setCollapsed={setCollapsed}
            />

            <main className="app-main">
                <div className="app-content">
                    {children || <Outlet />}
                </div>
            </main>
        </div>
    );
}