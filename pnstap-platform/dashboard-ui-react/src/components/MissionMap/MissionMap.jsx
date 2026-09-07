import "./MissionMap.css";

export default function MissionMap() {

    const locations = [

        { name:"Lagos", x:"18%", y:"58%" },

        { name:"London", x:"47%", y:"23%" },

        { name:"New York", x:"24%", y:"32%" },

        { name:"Dubai", x:"63%", y:"40%" },

        { name:"Singapore", x:"82%", y:"63%" }

    ];

    return (

        <div className="mission-map">

            <div className="map-header">

                <div>

                    <small>GLOBAL SENSOR NETWORK</small>

                    <h2>Mission Map</h2>

                </div>

                <span>5 Active</span>

            </div>

            <div className="map-area">

                {

                    locations.map((location,index)=>(

                        <div
                            key={index}
                            className="map-point"
                            style={{
                                left:location.x,
                                top:location.y
                            }}
                        >

                            <div className="pulse"></div>

                            <span>{location.name}</span>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}