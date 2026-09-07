import "./ActivityTimeline.css";

export default function ActivityTimeline() {

    const activities = [

        {
            time:"09:41",
            title:"Sensor Connected",
            description:"HQ Gateway is now online."
        },

        {
            time:"09:38",
            title:"Threat Blocked",
            description:"Lyromi blocked a brute-force attempt."
        },

        {
            time:"09:31",
            title:"New Device",
            description:"Laptop-27 joined the network."
        },

        {
            time:"09:20",
            title:"AI Scan Completed",
            description:"Workspace security score updated."
        }

    ];

    return(

        <div className="activity-card">

            <div className="activity-header">

                <small>LIVE ACTIVITY</small>

                <h2>Timeline</h2>

            </div>

            {

                activities.map((item,index)=>(

                    <div
                        className="activity-item"
                        key={index}
                    >

                        <div className="activity-dot"></div>

                        <div className="activity-content">

                            <h4>{item.title}</h4>

                            <p>{item.description}</p>

                        </div>

                        <span>{item.time}</span>

                    </div>

                ))

            }

        </div>

    );

}