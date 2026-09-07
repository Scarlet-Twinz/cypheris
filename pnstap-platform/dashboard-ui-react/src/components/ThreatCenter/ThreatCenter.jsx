import "./ThreatCenter.css";

export default function ThreatCenter({ threats = [] }) {

    return (

        <div className="threat-center">

            <div className="threat-header">

                <div>

                    <small>LIVE SECURITY EVENTS</small>

                    <h2>Threat Center</h2>

                </div>

                <span>{threats.length} Active</span>

            </div>

            {threats.map((item, index) => (

                <div
                    key={index}
                    className="threat-item"
                >

                    <div
                        className={`threat-dot ${item.severity.toLowerCase()}`}
                    />

                    <div className="threat-info">

                        <h4>{item.title}</h4>

                        <p>{item.status}</p>

                    </div>

                    <small>
                        {new Date(item.detected_at).toLocaleString()}
                    </small>

                </div>

            ))}

        </div>

    );

}