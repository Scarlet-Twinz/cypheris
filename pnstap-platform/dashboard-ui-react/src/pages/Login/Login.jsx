import { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { FiArrowRight, FiEye, FiEyeOff, FiShield, FiActivity } from "react-icons/fi";

import logo from "../../assets/logo/cypheris-logo.jpg";
import "./Login.css";

export default function Login() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        email: "",
        password: "",
    });

    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData((prev) => ({
            ...prev,
            [e.target.name]: e.target.value,
        }));
    };

    const handleLogin = async (e) => {
        e.preventDefault();

        if (loading) return;

        setLoading(true);

        try {
            const response = await axios.post(
                "http://127.0.0.1:8000/auth/login",
                formData
            );

            localStorage.setItem(
                "access_token",
                response.data.access_token
            );

            localStorage.setItem(
                "user",
                JSON.stringify(response.data.user)
            );

            localStorage.setItem(
                "company",
                JSON.stringify(response.data.company)
            );

            navigate("/dashboard");
        } catch (error) {
            alert(
                error.response?.data?.detail ||
                "Unable to sign in. Please check your credentials."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="auth-page login-page">

            <div className="auth-noise"></div>

            <div className="auth-orbit orbit-one"></div>
            <div className="auth-orbit orbit-two"></div>

            <section className="auth-showcase">

                <div className="showcase-top">
                    <Link to="/" className="brand">
                        <img src={logo} alt="Cypheris" />
                        <span>Cypheris</span>
                    </Link>

                    <div className="secure-indicator">
                        <span className="secure-dot"></span>
                        SYSTEM SECURE
                    </div>
                </div>

                <div className="showcase-content">

                    <div className="eyebrow">
                        <FiShield />
                        ENTERPRISE SECURITY INTELLIGENCE
                    </div>

                    <h1>
                        Your infrastructure.
                        <br />
                        <span>Decoded.</span>
                    </h1>

                    <p>
                        Cypheris continuously transforms your company's
                        infrastructure signals into security intelligence,
                        protection and decisions you can act on.
                    </p>

                    <div className="security-visual">

                        <div className="visual-core">
                            <div className="core-ring ring-a"></div>
                            <div className="core-ring ring-b"></div>
                            <div className="core-ring ring-c"></div>

                            <div className="core-center">
                                <FiShield />
                                <small>CY</small>
                            </div>
                        </div>

                        <div className="signal signal-one">
                            <span></span>
                            SENSOR
                        </div>

                        <div className="signal signal-two">
                            <span></span>
                            TELEMETRY
                        </div>

                        <div className="signal signal-three">
                            <span></span>
                            LYROMI
                        </div>

                        <div className="visual-line line-one"></div>
                        <div className="visual-line line-two"></div>
                        <div className="visual-line line-three"></div>
                    </div>

                    <div className="showcase-stats">
                        <div>
                            <strong>24/7</strong>
                            <span>Continuous Intelligence</span>
                        </div>

                        <div>
                            <strong>AI</strong>
                            <span>Security Analysis</span>
                        </div>

                        <div>
                            <strong>LIVE</strong>
                            <span>Infrastructure Visibility</span>
                        </div>
                    </div>

                </div>

                <div className="showcase-footer">
                    <span>Powered by PNSTAP™</span>
                    <span>Cypheris Security Intelligence Platform</span>
                </div>

            </section>

            <section className="auth-panel">

                <div className="auth-panel-inner">

                    <div className="mobile-brand">
                        <img src={logo} alt="Cypheris" />
                        <span>Cypheris</span>
                    </div>

                    <div className="auth-heading">
                        <div className="heading-icon">
                            <FiActivity />
                        </div>

                        <span className="heading-label">
                            COMMAND ACCESS
                        </span>

                        <h2>Welcome back.</h2>

                        <p>
                            Enter your credentials to access your
                            Cypheris command center.
                        </p>
                    </div>

                    <form
                        className="auth-form"
                        onSubmit={handleLogin}
                    >

                        <label>
                            <span>Work email</span>

                            <input
                                type="email"
                                name="email"
                                placeholder="you@company.com"
                                value={formData.email}
                                onChange={handleChange}
                                autoComplete="email"
                                required
                            />
                        </label>

                        <label>
                            <span>Password</span>

                            <div className="password-field">

                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    placeholder="Enter your password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    autoComplete="current-password"
                                    required
                                />

                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() =>
                                        setShowPassword(!showPassword)
                                    }
                                    aria-label={
                                        showPassword
                                            ? "Hide password"
                                            : "Show password"
                                    }
                                >
                                    {showPassword
                                        ? <FiEyeOff />
                                        : <FiEye />}
                                </button>

                            </div>
                        </label>

                        <div className="form-options">
                            <span className="session-status">
                                <span></span>
                                Secure session
                            </span>

                            <button
                                type="button"
                                className="forgot-button"
                                onClick={() =>
                                    alert(
                                        "Password recovery will be connected next."
                                    )
                                }
                            >
                                Forgot password?
                            </button>
                        </div>

                        <button
                            type="submit"
                            className="auth-submit"
                            disabled={loading}
                        >
                            <span>
                                {loading
                                    ? "Authenticating..."
                                    : "Enter Command Center"}
                            </span>

                            {!loading && <FiArrowRight />}
                        </button>

                    </form>

                    <div className="auth-divider">
                        <span>NEW TO CYPHERIS?</span>
                    </div>

                    <Link
                        to="/signup"
                        className="secondary-auth-button"
                    >
                        Create your organization
                        <FiArrowRight />
                    </Link>

                    <div className="auth-security-note">
                        <FiShield />

                        <span>
                            Your connection is protected by
                            enterprise-grade authentication.
                        </span>
                    </div>

                </div>

            </section>

        </main>
    );
}