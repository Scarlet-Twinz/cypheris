import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./onboarding.css";
import logo from "../../assets/logo/cypheris-logo.jpg";

const methods = [
    {
        id: "sensor",
        number: "01",
        icon: "◈",
        title: "PNSTAP Security Sensor",
        label: "FULL VISIBILITY",
        description:
            "Deploy a lightweight Cypheris sensor inside your infrastructure. Sentinel can then observe devices, traffic and security events.",
        meta: "Recommended",
    },
    {
        id: "cloud",
        number: "02",
        icon: "☁",
        title: "Cloud Infrastructure",
        label: "CLOUD",
        description:
            "Connect your cloud environment and continuously evaluate your security posture across supported infrastructure.",
        meta: "AWS • AZURE • GCP",
    },
    {
        id: "api",
        number: "03",
        icon: "⌁",
        title: "Security API",
        label: "API",
        description:
            "Connect an existing security platform or data source through the Cypheris integration layer.",
        meta: "INTEGRATION LAYER",
    },
];

export default function Onboarding() {
    const navigate = useNavigate();

    const user = useMemo(() => {
        try {
            return JSON.parse(localStorage.getItem("user")) || {};
        } catch {
            return {};
        }
    }, []);

    const company = useMemo(() => {
        try {
            return JSON.parse(localStorage.getItem("company")) || {};
        } catch {
            return {};
        }
    }, []);

    const [selectedMethod, setSelectedMethod] = useState("sensor");

    const selected = methods.find(
        (method) => method.id === selectedMethod
    );

    const handleContinue = () => {
        /*
         * Every integration now enters the same controlled
         * setup pipeline.
         *
         * The selected mode is preserved in the URL so the
         * next screen knows whether this is:
         *
         * sensor
         * cloud
         * api
         */
        navigate(`/install-sensor?mode=${selectedMethod}`);
    };

    const firstName =
        user.name?.trim()?.split(/\s+/)[0] || "there";

    return (
        <main className="onboarding-page">
            <div className="onboarding-grid" />
            <div className="onboarding-glow glow-a" />
            <div className="onboarding-glow glow-b" />

            <header className="onboarding-topbar">
                <div className="onboarding-brand">
                    <div className="onboarding-brand-mark">
                        <img src={logo} alt="Cypheris" />
                    </div>

                    <div>
                        <strong>CYPHERIS</strong>
                        <span>Powered by PNSTAP™</span>
                    </div>
                </div>

                <div className="initializing-state">
                    <span className="pulse-dot" />
                    COMMAND CENTER INITIALIZING
                </div>
            </header>

            <section className="onboarding-content">
                <div className="onboarding-heading">
                    <span className="onboarding-eyebrow">
                        ORGANIZATION INITIALIZATION
                    </span>

                    <h1>
                        Bring your
                        <span> infrastructure </span>
                        into focus.
                    </h1>

                    <p>
                        Welcome, {firstName}. Your Cypheris workspace for{" "}
                        <strong>
                            {company.name || "your organization"}
                        </strong>{" "}
                        has been created. The next step is connecting the
                        environment you want Cypheris to protect.
                    </p>
                </div>

                <div className="organization-strip">
                    <div className="organization-identity">
                        <div className="organization-avatar">
                            {company.name?.charAt(0)?.toUpperCase() || "C"}
                        </div>

                        <div>
                            <span>YOUR ORGANIZATION</span>
                            <strong>
                                {company.name || "Your organization"}
                            </strong>
                        </div>
                    </div>

                    <div className="organization-flow">
                        <div className="flow-item active">
                            <b>C</b>
                            <span>CYPHERIS INTELLIGENCE</span>
                        </div>

                        <i>→</i>

                        <div className="flow-item">
                            <b>Ψ</b>
                            <span>LYROMI</span>
                        </div>
                    </div>
                </div>

                <div className="connection-section">
                    <div className="connection-heading">
                        <div>
                            <span>STEP 01 / CONNECTION</span>

                            <h2>
                                How should Cypheris see your environment?
                            </h2>
                        </div>

                        <div className="selection-status">
                            <span className="status-dot" />
                            1 METHOD SELECTED
                        </div>
                    </div>

                    <div className="method-grid">
                        {methods.map((method) => {
                            const active =
                                selectedMethod === method.id;

                            return (
                                <button
                                    key={method.id}
                                    type="button"
                                    className={`method-card ${
                                        active ? "active" : ""
                                    }`}
                                    onClick={() =>
                                        setSelectedMethod(method.id)
                                    }
                                >
                                    <div className="method-top">
                                        <span className="method-number">
                                            {method.number}
                                        </span>

                                        <span className="method-icon">
                                            {method.icon}
                                        </span>

                                        {method.meta === "Recommended" && (
                                            <span className="recommended">
                                                Recommended
                                            </span>
                                        )}
                                    </div>

                                    <span className="method-label">
                                        {method.label}
                                    </span>

                                    <h3>{method.title}</h3>

                                    <p>{method.description}</p>

                                    <div className="method-footer">
                                        <span>{method.meta}</span>

                                        <span
                                            className={`radio ${
                                                active ? "checked" : ""
                                            }`}
                                        >
                                            {active && "✓"}
                                        </span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    <div className="security-note">
                        <div className="security-symbol">◇</div>

                        <div>
                            <strong>
                                Your infrastructure stays yours.
                            </strong>

                            <p>
                                Cypheris establishes a secure connection before
                                security telemetry is processed.
                            </p>
                        </div>

                        <div className="selected-method">
                            <span>SELECTED</span>

                            <strong>
                                {selected?.title}
                            </strong>
                        </div>
                    </div>

                    <div className="onboarding-actions">
                        <button
                            type="button"
                            className="back-button"
                            onClick={() => navigate("/")}
                        >
                            ← Back
                        </button>

                        <button
                            type="button"
                            className="continue-button"
                            onClick={handleContinue}
                        >
                            <span>Continue to Setup</span>
                            <b>→</b>
                        </button>
                    </div>
                </div>
            </section>

            <footer className="onboarding-footer">
                <span>CYPHERIS COMMAND FABRIC</span>
                <span>PNSTAP™ SECURITY ENGINE</span>
                <span>LYROMI INTELLIGENCE</span>
            </footer>
        </main>
    );
}