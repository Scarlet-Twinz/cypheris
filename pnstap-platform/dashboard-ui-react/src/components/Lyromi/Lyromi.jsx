import { useState } from "react";
import logo from "../../assets/logo/cypheris-logo.jpg";
import "./Lyromi.css";

import { chatWithLyromi } from "../../services/dashboardService";

export default function Lyromi({ dashboard }) {

    const [message, setMessage] = useState("");
    const [typing, setTyping] = useState(false);

    const [chat, setChat] = useState([
        {
            sender: "lyromi",
            text: dashboard?.lyromi_message || ""
        }
    ]);

    const sendMessage = async () => {

        if (!message.trim()) return;

        const userMessage = message;

        setChat(prev => [
            ...prev,
            {
                sender: "user",
                text: userMessage
            }
        ]);

        setMessage("");
        setTyping(true);

        try {

            const response = await chatWithLyromi(userMessage);

            setTyping(false);

            setChat(prev => [
                ...prev,
                {
                    sender: "lyromi",
                    text: response.reply
                }
            ]);

        } catch {

            setTyping(false);

            setChat(prev => [
                ...prev,
                {
                    sender: "lyromi",
                    text: "Unable to contact Lyromi."
                }
            ]);

        }

    };

    return (

        <div className="lyromi-container">

            <div className="lyromi-header">

                <img
                    src={logo}
                    alt="Cypheris Logo"
                    className="lyromi-logo"
                />

                <h2>LYROMI</h2>

                <span>Enterprise AI Security Analyst</span>

                <small>Powered by PNSTAP™</small>

            </div>

            <div className="lyromi-chat">

                {chat.map((msg, index) => (

                    <div
                        key={index}
                        className={
                            msg.sender === "user"
                                ? "user-bubble"
                                : "lyromi-bubble"
                        }
                    >

                        <div className="bubble-title">

                            {msg.sender === "user" ? "YOU" : "LYROMI"}

                        </div>

                        <p>{msg.text}</p>

                    </div>

                ))}

                {typing && (

                    <div className="lyromi-bubble">

                        <div className="bubble-title">

                            LYROMI

                        </div>

                        <p>Thinking...</p>

                    </div>

                )}

            </div>

            <div className="lyromi-input-area">

                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask Lyromi anything..."
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            sendMessage();
                        }
                    }}
                />

                <button onClick={sendMessage}>

                    Send

                </button>

            </div>

        </div>

    );

}