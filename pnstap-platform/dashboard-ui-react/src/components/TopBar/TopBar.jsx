import {
    FiSearch,
    FiBell,
    FiSettings
} from "react-icons/fi";

import "./TopBar.css";

export default function TopBar() {

    return (

        <header className="topbar">

            <div className="search-box">

                <FiSearch />

                <input
                    type="text"
                    placeholder="Search organizations, users, reports..."
                />

            </div>

            <div className="topbar-right">

                <button className="icon-btn">

                    <FiBell />

                    <span></span>

                </button>

                <button className="icon-btn">

                    <FiSettings />

                </button>

                <div className="admin-profile">

                    <div className="admin-avatar">

                        A

                    </div>

                    <div>

                        <h4>Administrator</h4>

                        <small>Super Admin</small>

                    </div>

                </div>

            </div>

        </header>

    );

}