import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import logo from "../../assets/logo/cypheris-logo.jpg";
import "./Home.css";

export default function Home() {
    const navigate = useNavigate();
    const [scrolled, setScrolled] = useState(false);
    const [activeStory, setActiveStory] = useState(0);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 30);
        };

        window.addEventListener("scroll", handleScroll);

        return () => {
            window.removeEventListener("scroll", handleScroll);
        };
    }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            setActiveStory((current) => (current + 1) % 4);
        }, 3500);

        return () => clearInterval(interval);
    }, []);

    const scrollToStory = () => {
        document
            .getElementById("story")
            ?.scrollIntoView({ behavior: "smooth" });
    };

    const scrollToHow = () => {
        document
            .getElementById("how-it-works")
            ?.scrollIntoView({ behavior: "smooth" });
    };

    const storySteps = [
        {
            number: "01",
            title: "Connect",
            label: "Your environment enters the picture",
            description:
                "Connect your organization, infrastructure and security sensors to Cypheris. No more security information scattered across disconnected systems.",
            icon: "⌁",
        },
        {
            number: "02",
            title: "Observe",
            label: "Cypheris watches the environment",
            description:
                "Sensors continuously collect security signals from your environment and send them into the Cypheris security engine.",
            icon: "◉",
        },
        {
            number: "03",
            title: "Understand",
            label: "LYROMI turns signals into intelligence",
            description:
                "LYROMI analyzes what is happening, identifies patterns and converts technical security events into information your team can actually understand.",
            icon: "✦",
        },
        {
            number: "04",
            title: "Respond",
            label: "Your organization moves with clarity",
            description:
                "Threats become visible, priorities become clearer and your security team can investigate and respond from one command center.",
            icon: "↗",
        },
    ];

    const metrics = [
        {
            value: "24/7",
            label: "Continuous visibility",
        },
        {
            value: "AI",
            label: "Security intelligence",
        },
        {
            value: "01",
            label: "Unified command center",
        },
        {
            value: "∞",
            label: "Signals understood",
        },
    ];

    return (
        <div className="home-page">

            {/* =====================================================
                NAVIGATION
            ====================================================== */}

            <header className={`home-nav ${scrolled ? "nav-scrolled" : ""}`}>

                <div className="nav-brand">

                    <img
                        src={logo}
                        alt="Cypheris"
                        className="nav-logo"
                    />

                    <div className="brand-copy">
                        <strong>Cypheris</strong>
                        <span>Decode Your Security</span>
                    </div>

                </div>

                <nav className="desktop-nav">

                    <button onClick={scrollToStory}>
                        Why Cypheris
                    </button>

                    <button onClick={scrollToHow}>
                        How It Works
                    </button>

                    <button
                        onClick={() =>
                            document
                                .getElementById("intelligence")
                                ?.scrollIntoView({
                                    behavior: "smooth",
                                })
                        }
                    >
                        LYROMI
                    </button>

                </nav>

                <div className="nav-actions">

                    <Link
                        to="/login"
                        className="nav-login"
                    >
                        Sign In
                    </Link>

                    <Link
                        to="/signup"
                        className="nav-cta"
                    >
                        Start Securely
                        <span>→</span>
                    </Link>

                </div>

            </header>


            {/* =====================================================
                HERO
            ====================================================== */}

            <main>

                <section className="hero">

                    <div className="hero-grid"></div>

                    <div className="hero-glow hero-glow-one"></div>
                    <div className="hero-glow hero-glow-two"></div>

                    <div className="hero-content">

                        <div className="status-pill">
                            <span className="status-dot"></span>
                            CYPHERIS SECURITY FABRIC ONLINE
                        </div>

                        <h1>
                            Security isn't a dashboard.
                            <span>
                                It's knowing what happens next.
                            </span>
                        </h1>

                        <p className="hero-description">
                            Cypheris transforms scattered security signals
                            into one intelligent command center — giving
                            organizations continuous visibility, AI-powered
                            analysis and a clearer path from detection to
                            response.
                        </p>

                        <div className="hero-buttons">

                            <button
                                className="hero-primary"
                                onClick={() => navigate("/signup")}
                            >
                                <span>Build Your Security Command Center</span>
                                <strong>→</strong>
                            </button>

                            <button
                                className="hero-secondary"
                                onClick={scrollToStory}
                            >
                                <span className="play-icon">▶</span>
                                See how Cypheris works
                            </button>

                        </div>

                        <div className="hero-trust">

                            <div className="trust-line"></div>

                            <span>
                                BUILT FOR MODERN ORGANIZATIONS
                            </span>

                            <div className="trust-line"></div>

                        </div>

                    </div>


                    {/* COMMAND CENTER VISUAL */}

                    <div className="hero-command">

                        <div className="command-window">

                            <div className="window-top">

                                <div className="window-dots">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>

                                <div className="window-title">
                                    CYPHERIS / COMMAND CENTER
                                </div>

                                <div className="window-live">
                                    <i></i>
                                    LIVE
                                </div>

                            </div>

                            <div className="command-body">

                                <div className="command-header">

                                    <div>
                                        <small>SECURITY POSTURE</small>
                                        <strong>96.4%</strong>
                                    </div>

                                    <div className="command-health">
                                        <span>●</span>
                                        Environment monitored
                                    </div>

                                </div>

                                <div className="security-orbit">

                                    <div className="orbit orbit-one"></div>
                                    <div className="orbit orbit-two"></div>
                                    <div className="orbit orbit-three"></div>

                                    <div className="orbit-core">

                                        <img
                                            src={logo}
                                            alt="Cypheris"
                                        />

                                        <span>CY</span>

                                    </div>

                                    <div className="signal signal-one">
                                        <b>HQ</b>
                                    </div>

                                    <div className="signal signal-two">
                                        <b>01</b>
                                    </div>

                                    <div className="signal signal-three">
                                        <b>AI</b>
                                    </div>

                                    <div className="signal signal-four">
                                        <b>24</b>
                                    </div>

                                </div>

                                <div className="command-stats">

                                    <div>
                                        <span>Threats</span>
                                        <strong>04</strong>
                                        <small>requiring attention</small>
                                    </div>

                                    <div>
                                        <span>Signals</span>
                                        <strong>18.7K</strong>
                                        <small>processed today</small>
                                    </div>

                                    <div>
                                        <span>AI Confidence</span>
                                        <strong>99.2%</strong>
                                        <small>LYROMI analysis</small>
                                    </div>

                                </div>

                                <div className="command-event">

                                    <div className="event-icon">✦</div>

                                    <div>
                                        <small>LYROMI DETECTION</small>
                                        <p>
                                            An unusual authentication pattern
                                            requires investigation.
                                        </p>
                                    </div>

                                    <span className="event-arrow">→</span>

                                </div>

                            </div>

                        </div>

                        <div className="floating-card floating-threat">

                            <span className="floating-icon danger">
                                !
                            </span>

                            <div>
                                <small>THREAT DETECTED</small>
                                <strong>Suspicious activity</strong>
                            </div>

                            <span className="pulse"></span>

                        </div>

                        <div className="floating-card floating-ai">

                            <span className="floating-icon ai">
                                ✦
                            </span>

                            <div>
                                <small>LYROMI</small>
                                <strong>Analysis complete</strong>
                            </div>

                            <span className="confidence">
                                99%
                            </span>

                        </div>

                    </div>

                </section>


                {/* =====================================================
                    STORY INTRO
                ====================================================== */}

                <section
                    className="story-intro"
                    id="story"
                >

                    <div className="section-eyebrow">
                        THE CYPHERIS STORY
                    </div>

                    <h2>
                        Your security environment is
                        <span> telling a story.</span>
                    </h2>

                    <p>
                        The problem is that the story is usually scattered
                        across alerts, devices, logs, sensors and tools.
                        Cypheris brings those signals together so your
                        organization can understand what is actually
                        happening.
                    </p>

                </section>


                {/* =====================================================
                    STORY JOURNEY
                ====================================================== */}

                <section className="story-section">

                    <div className="story-navigation">

                        {storySteps.map((step, index) => (

                            <button
                                key={step.number}
                                className={
                                    activeStory === index
                                        ? "story-nav-item active"
                                        : "story-nav-item"
                                }
                                onClick={() =>
                                    setActiveStory(index)
                                }
                            >

                                <span>{step.number}</span>

                                <div>
                                    <strong>{step.title}</strong>
                                    <small>{step.label}</small>
                                </div>

                            </button>

                        ))}

                    </div>

                    <div className="story-display">

                        <div className="story-display-number">
                            {storySteps[activeStory].number}
                        </div>

                        <div className="story-display-content">

                            <div className="story-icon">
                                {storySteps[activeStory].icon}
                            </div>

                            <span className="story-label">
                                {storySteps[activeStory].label}
                            </span>

                            <h3>
                                {storySteps[activeStory].title}
                            </h3>

                            <p>
                                {storySteps[activeStory].description}
                            </p>

                            <div className="story-progress">

                                {storySteps.map((_, index) => (

                                    <span
                                        key={index}
                                        className={
                                            index <= activeStory
                                                ? "filled"
                                                : ""
                                        }
                                    ></span>

                                ))}

                            </div>

                        </div>

                        <div className="story-visual">

                            <div className="visual-grid"></div>

                            <div className="visual-ring ring-a"></div>
                            <div className="visual-ring ring-b"></div>

                            <div className="visual-center">

                                <img
                                    src={logo}
                                    alt="Cypheris"
                                />

                                <strong>
                                    {storySteps[activeStory].title}
                                </strong>

                                <small>
                                    SECURITY INTELLIGENCE
                                </small>

                            </div>

                        </div>

                    </div>

                </section>


                {/* =====================================================
                    METRICS
                ====================================================== */}

                <section className="metrics-section">

                    {metrics.map((metric) => (

                        <div
                            className="metric"
                            key={metric.label}
                        >

                            <strong>{metric.value}</strong>

                            <span>{metric.label}</span>

                        </div>

                    ))}

                </section>


                {/* =====================================================
                    HOW IT WORKS
                ====================================================== */}

                <section
                    className="how-section"
                    id="how-it-works"
                >

                    <div className="how-header">

                        <div>
                            <span className="section-eyebrow">
                                FROM CONNECTION TO CLARITY
                            </span>

                            <h2>
                                One security journey.
                                <span> One command center.</span>
                            </h2>
                        </div>

                        <p>
                            Cypheris is designed around the way security
                            actually happens — observe the environment,
                            understand the signals, prioritize what matters
                            and act.
                        </p>

                    </div>

                    <div className="how-grid">

                        <article className="how-card">

                            <div className="how-number">
                                01
                            </div>

                            <div className="how-icon">
                                ◌
                            </div>

                            <h3>
                                Connect your organization
                            </h3>

                            <p>
                                Create your Cypheris workspace and connect
                                the infrastructure you want to monitor.
                            </p>

                            <div className="how-mini">
                                <span>ORGANIZATION</span>
                                <strong>CONNECTED</strong>
                            </div>

                        </article>


                        <article className="how-card featured">

                            <div className="how-number">
                                02
                            </div>

                            <div className="how-icon">
                                ◉
                            </div>

                            <h3>
                                Deploy your sensors
                            </h3>

                            <p>
                                Sensors become the eyes of your security
                                environment, continuously sending signals
                                into the Cypheris engine.
                            </p>

                            <div className="sensor-map">

                                <span className="map-node node-a"></span>
                                <span className="map-node node-b"></span>
                                <span className="map-node node-c"></span>
                                <span className="map-line line-a"></span>
                                <span className="map-line line-b"></span>

                            </div>

                        </article>


                        <article className="how-card">

                            <div className="how-number">
                                03
                            </div>

                            <div className="how-icon">
                                ✦
                            </div>

                            <h3>
                                Let LYROMI understand
                            </h3>

                            <p>
                                AI turns raw security signals into a
                                contextual security picture your team can
                                act on.
                            </p>

                            <div className="ai-wave">

                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>

                            </div>

                        </article>


                        <article className="how-card">

                            <div className="how-number">
                                04
                            </div>

                            <div className="how-icon">
                                ↗
                            </div>

                            <h3>
                                Respond with confidence
                            </h3>

                            <p>
                                Investigate threats, understand system
                                health and make decisions from one
                                intelligent command center.
                            </p>

                            <div className="response-status">
                                <span></span>
                                RESPONSE READY
                            </div>

                        </article>

                    </div>

                </section>


                {/* =====================================================
                    LYROMI INTELLIGENCE
                ====================================================== */}

                <section
                    className="intelligence-section"
                    id="intelligence"
                >

                    <div className="intelligence-visual">

                        <div className="ai-grid"></div>

                        <div className="ai-core">

                            <div className="ai-core-ring"></div>

                            <div className="ai-core-inner">
                                <img
                                    src={logo}
                                    alt="Cypheris"
                                />
                                <span>LYROMI</span>
                            </div>

                        </div>

                        <div className="ai-signal signal-top">
                            THREAT ANALYSIS
                        </div>

                        <div className="ai-signal signal-right">
                            BEHAVIOR PATTERN
                        </div>

                        <div className="ai-signal signal-bottom">
                            SECURITY CONTEXT
                        </div>

                    </div>


                    <div className="intelligence-content">

                        <span className="section-eyebrow">
                            THE INTELLIGENCE LAYER
                        </span>

                        <h2>
                            Meet
                            <span> LYROMI.</span>
                        </h2>

                        <p className="intelligence-lead">
                            Not another chatbot sitting beside your
                            dashboard. LYROMI is designed as the intelligence
                            layer inside the Cypheris security environment.
                        </p>

                        <div className="intelligence-list">

                            <div>
                                <span>01</span>
                                <div>
                                    <strong>See the signal</strong>
                                    <p>
                                        Understand what changed inside the
                                        environment.
                                    </p>
                                </div>
                            </div>

                            <div>
                                <span>02</span>
                                <div>
                                    <strong>Understand the context</strong>
                                    <p>
                                        Connect events instead of treating
                                        every alert as an isolated problem.
                                    </p>
                                </div>
                            </div>

                            <div>
                                <span>03</span>
                                <div>
                                    <strong>Explain what matters</strong>
                                    <p>
                                        Turn technical security information
                                        into clear intelligence.
                                    </p>
                                </div>
                            </div>

                        </div>

                        <button
                            className="intelligence-button"
                            onClick={() => navigate("/signup")}
                        >
                            Enter the Cypheris command center
                            <span>→</span>
                        </button>

                    </div>

                </section>


                {/* =====================================================
                    SECURITY STORY
                ====================================================== */}

                <section className="security-story">

                    <div className="security-story-header">

                        <span className="section-eyebrow">
                            WHEN SOMETHING CHANGES
                        </span>

                        <h2>
                            From a strange signal
                            <span> to a clear decision.</span>
                        </h2>

                        <p>
                            Imagine an unusual authentication pattern appears
                            in your environment. Cypheris doesn't simply show
                            you another red alert. It gives the event context.
                        </p>

                    </div>

                    <div className="incident-flow">

                        <div className="incident-step">

                            <span>01</span>

                            <div className="incident-icon">
                                ?
                            </div>

                            <small>SIGNAL</small>

                            <strong>
                                Unusual login pattern
                            </strong>

                        </div>

                        <div className="flow-arrow">
                            →
                        </div>

                        <div className="incident-step">

                            <span>02</span>

                            <div className="incident-icon">
                                ◉
                            </div>

                            <small>ANALYSIS</small>

                            <strong>
                                LYROMI connects the signals
                            </strong>

                        </div>

                        <div className="flow-arrow">
                            →
                        </div>

                        <div className="incident-step">

                            <span>03</span>

                            <div className="incident-icon">
                                !
                            </div>

                            <small>PRIORITY</small>

                            <strong>
                                Threat requires attention
                            </strong>

                        </div>

                        <div className="flow-arrow">
                            →
                        </div>

                        <div className="incident-step final">

                            <span>04</span>

                            <div className="incident-icon">
                                ✓
                            </div>

                            <small>RESPONSE</small>

                            <strong>
                                Your team knows what to do
                            </strong>

                        </div>

                    </div>

                </section>


                {/* =====================================================
                    FINAL CTA
                ====================================================== */}

                <section className="final-cta">

                    <div className="cta-glow"></div>

                    <div className="cta-content">

                        <div className="cta-logo">

                            <img
                                src={logo}
                                alt="Cypheris"
                            />

                        </div>

                        <span className="section-eyebrow">
                            YOUR SECURITY STORY STARTS HERE
                        </span>

                        <h2>
                            Stop watching security
                            <span> from the sidelines.</span>
                        </h2>

                        <p>
                            Build your Cypheris command center, connect your
                            organization and start turning security signals
                            into intelligence.
                        </p>

                        <div className="cta-actions">

                            <button
                                className="hero-primary"
                                onClick={() => navigate("/signup")}
                            >
                                Create your organization
                                <strong>→</strong>
                            </button>

                            <button
                                className="cta-text-button"
                                onClick={() => navigate("/login")}
                            >
                                Already have an organization?
                                <span>Sign in</span>
                            </button>

                        </div>

                    </div>

                    <div className="cta-footer">

                        <div className="footer-brand">

                            <img
                                src={logo}
                                alt="Cypheris"
                            />

                            <div>
                                <strong>Cypheris</strong>
                                <span>
                                    Decode Your Security
                                </span>
                            </div>

                        </div>

                        <span>
                            Powered by PNSTAP™
                        </span>

                        <span>
                            © {new Date().getFullYear()} Cypheris
                        </span>

                    </div>

                </section>

            </main>

        </div>
    );
}