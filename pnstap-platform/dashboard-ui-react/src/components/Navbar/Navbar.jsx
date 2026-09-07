import { FiBell, FiSearch } from "react-icons/fi";
import "./Navbar.css";

export default function Navbar() {

    const now = new Date();

    const hour = now.getHours();

    let greeting = "Good Evening";

    if (hour < 12) greeting = "Good Morning";
    else if (hour < 18) greeting = "Good Afternoon";

    const today = now.toLocaleDateString("en-US", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
    });

    return (
        <header className="navbar">

            <div className="navbar-left">

                <span className="navbar-greeting">
                    {greeting}
                </span>

                <h2>Mission Control</h2>

                <small>{today}</small>

            </div>

            <div className="navbar-center">

                <div className="command-search">

                    <FiSearch />

                    <input
                        type="text"
                        placeholder="Ask Lyromi or search..."
                    />

                </div>

            </div>

            <div className="navbar-right">

                <button className="icon-btn">
                    <FiBell />
                </button>

                <div className="pulse">

                    <span className="pulse-dot"></span>

                    <span>Pulse Healthy</span>

                </div>

            </div>

        </header>
    );
}