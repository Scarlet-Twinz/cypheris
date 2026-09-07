import {
    ResponsiveContainer,
    AreaChart,
    Area,
    CartesianGrid,
    Tooltip,
    XAxis,
    YAxis
} from "recharts";

import "./RevenueChart.css";

const data = [

    { time:"00:00", traffic:45 },

    { time:"02:00", traffic:52 },

    { time:"04:00", traffic:48 },

    { time:"06:00", traffic:61 },

    { time:"08:00", traffic:74 },

    { time:"10:00", traffic:83 },

    { time:"12:00", traffic:96 },

    { time:"14:00", traffic:118 },

    { time:"16:00", traffic:132 },

    { time:"18:00", traffic:121 },

    { time:"20:00", traffic:144 },

    { time:"22:00", traffic:158 }

];

export default function RevenueChart(){

    return(

        <div className="traffic-card">

            <div className="traffic-header">

                <div>

                    <small>

                        LIVE NETWORK TRAFFIC

                    </small>

                    <h2>

                        158 MB/s

                    </h2>

                </div>

                <span className="live-badge">

                    ● LIVE

                </span>

            </div>

            <div className="chart-wrapper">

                <ResponsiveContainer
                    width="100%"
                    height={320}
                >

                    <AreaChart data={data}>

                        <defs>

                            <linearGradient
                                id="trafficGradient"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >

                                <stop
                                    offset="0%"
                                    stopColor="#1aa8ff"
                                    stopOpacity={0.65}
                                />

                                <stop
                                    offset="100%"
                                    stopColor="#1aa8ff"
                                    stopOpacity={0}
                                />

                            </linearGradient>

                        </defs>

                        <CartesianGrid
                            stroke="#1d3959"
                            strokeDasharray="4 4"
                        />

                        <XAxis
                            dataKey="time"
                            stroke="#89a5ca"
                        />

                        <YAxis
                            stroke="#89a5ca"
                        />

                        <Tooltip />

                        <Area
                            type="monotone"
                            dataKey="traffic"
                            stroke="#1aa8ff"
                            strokeWidth={3}
                            fill="url(#trafficGradient)"
                        />

                    </AreaChart>

                </ResponsiveContainer>

            </div>

            <div className="traffic-stats">

                <div>

                    <strong>42K</strong>

                    <span>Packets/sec</span>

                </div>

                <div>

                    <strong>2 ms</strong>

                    <span>Latency</span>

                </div>

                <div>

                    <strong>68%</strong>

                    <span>TCP Traffic</span>

                </div>

                <div>

                    <strong>99.8%</strong>

                    <span>Availability</span>

                </div>

            </div>

        </div>

    );

}