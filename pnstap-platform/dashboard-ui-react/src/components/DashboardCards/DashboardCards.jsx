import "./DashboardCards.css";

export default function DashboardCards({ dashboard }) {

    const cards = [

        {
            title: "Organizations",
            value: dashboard.organizations,
            suffix: "",
            status: "Registered",
            color: "#1aa8ff"
        },

        {
            title: "Users",
            value: dashboard.users,
            suffix: "",
            status: "Active",
            color: "#27d980"
        },

        {
            title: "Network Traffic",
            value: dashboard.network_traffic,
            suffix: " GB",
            status: "Live",
            color: "#ff9800"
        },

        {
            title: "AI Confidence",
            value: dashboard.ai_confidence,
            suffix: "%",
            status: "LYROMI",
            color: "#8b5cf6"
        }

    ];

    return (

        <section className="dashboard-cards">

            {

                cards.map((card, index) => (

                    <div
                        className="dashboard-card"
                        key={index}
                    >

                        <div
                            className="card-dot"
                            style={{
                                background: card.color
                            }}
                        />

                        <small>

                            {card.title}

                        </small>

                        <h2>

                            {card.value}

                            {card.suffix}

                        </h2>

                        <span>

                            {card.status}

                        </span>

                    </div>

                ))

            }

        </section>

    );

}