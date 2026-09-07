import "./SensorStatus.css";

export default function SensorStatus() {

    const sensors = [

        {
            name:"HQ Gateway",
            status:"Online",
            cpu:"18%",
            latency:"2 ms"
        },

        {
            name:"Branch Office",
            status:"Online",
            cpu:"23%",
            latency:"5 ms"
        },

        {
            name:"AWS Europe",
            status:"Warning",
            cpu:"71%",
            latency:"21 ms"
        },

        {
            name:"Azure Backup",
            status:"Offline",
            cpu:"--",
            latency:"--"
        }

    ];

    return(

        <div className="sensor-status">

            <div className="sensor-header">

                <div>

                    <small>LIVE SENSOR STATUS</small>

                    <h2>Sensors</h2>

                </div>

                <span>4 Total</span>

            </div>

            {

                sensors.map((sensor,index)=>(

                    <div
                        className="sensor-row"
                        key={index}
                    >

                        <div>

                            <h4>{sensor.name}</h4>

                            <small>{sensor.status}</small>

                        </div>

                        <div>

                            <strong>{sensor.cpu}</strong>

                            <small>CPU</small>

                        </div>

                        <div>

                            <strong>{sensor.latency}</strong>

                            <small>Latency</small>

                        </div>

                    </div>

                ))

            }

        </div>

    );

}