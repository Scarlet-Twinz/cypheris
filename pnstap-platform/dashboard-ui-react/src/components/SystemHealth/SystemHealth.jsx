import "./SystemHealth.css";

export default function SystemHealth({ dashboard }) {

    return (

        <div className="system-health">

            <div className="system-header">

                <div>

                    <small>SYSTEM STATUS</small>

                    <h2>Infrastructure Health</h2>

                </div>

                <span className="healthy">

                    ● {dashboard.health >= 90 ? "Healthy" : "Warning"}

                </span>

            </div>

            <div className="health-grid">

                <div className="health-item">

                    <span>CPU Usage</span>

                    <strong>{dashboard.cpu_usage}%</strong>

                </div>

                <div className="health-item">

                    <span>Memory</span>

                    <strong>{dashboard.memory_usage}%</strong>

                </div>

                <div className="health-item">

                    <span>Disk</span>

                    <strong>{dashboard.disk_usage}%</strong>

                </div>

                <div className="health-item">

                    <span>Latency</span>

                    <strong>{dashboard.latency} ms</strong>

                </div>

            </div>

            <div className="sensor-section">

                <h3>Connected Sensors</h3>

                <div className="sensor">

                    <span>Head Office</span>

                    <strong className="online">
                        {dashboard.sensor_online ? "● Online" : "● Offline"}
                    </strong>

                </div>

                <div className="sensor">

                    <span>Cloud Gateway</span>

                    <strong className="online">
                        {dashboard.sensor_online ? "● Online" : "● Offline"}
                    </strong>

                </div>

                <div className="sensor">

                    <span>Branch Office</span>

                    <strong className="warning">
                        {dashboard.threat_level}
                    </strong>

                </div>

            </div>

        </div>

    );

}