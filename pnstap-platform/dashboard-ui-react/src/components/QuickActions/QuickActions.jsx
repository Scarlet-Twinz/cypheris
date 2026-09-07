import "./QuickActions.css";

export default function QuickActions() {

    const actions = [

        "Run AI Scan",
        "Deploy Sensor",
        "View Threats",
        "Generate Report",
        "Investigate Incident",
        "Open Mission Map"

    ];

    return(

        <div className="quick-actions">

            <small>COMMAND CENTER</small>

            <h2>Quick Actions</h2>

            <div className="action-grid">

                {

                    actions.map((action,index)=>(

                        <button
                            key={index}
                            className="action-btn"
                        >

                            {action}

                        </button>

                    ))

                }

            </div>

        </div>

    );

}