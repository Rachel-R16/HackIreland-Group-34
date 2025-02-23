

// import { useLocation, useNavigate } from "react-router-dom";
// import { useState, useEffect, useRef } from "react";
// import "../styles/ChatbotScreen.css";
// import studenticon from "../assets/studenticon.jpg";
// import { User } from "@carbon/icons-react";
// import { Checkmark } from "@carbon/icons-react";

// export default function ChatbotScreen() {
//     const location = useLocation();
//     const navigate = useNavigate();
//     const { category } = location.state || {};  // Ensure category is received properly

//     const [conversation, setConversation] = useState([]);
//     const [responses, setResponses] = useState({});
//     const [userInput, setUserInput] = useState("");
//     const [sessionId, setSessionId] = useState(null);
//     const chatContainerRef = useRef(null);
//     const profileContainerRef = useRef(null);

//     // ✅ Fetch initial message from backend on page load
//     useEffect(() => {
//         const startConversation = async () => {
//             try {
//                 const response = await fetch("http://localhost:5000/start-conversation", {
//                     method: "POST",
//                     headers: { "Content-Type": "application/json" },
//                     body: JSON.stringify({ mode: category })
//                 });

//                 const data = await response.json();
//                 if (data.session_id && data.message) {
//                     setSessionId(data.session_id);
//                     setConversation([{ type: "bot", text: data.message }]); // ✅ Add first message
//                 }
//             } catch (error) {
//                 console.error("Error starting conversation:", error);
//             }
//         };

//         startConversation();
//     }, [category]);

//     useEffect(() => {
//         if (chatContainerRef.current) {
//             chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
//         }
//     }, [conversation]);

//     useEffect(() => {
//         if (profileContainerRef.current) {
//             profileContainerRef.current.scrollTop = profileContainerRef.current.scrollHeight;
//         }
//     }, [responses]);

//     // ✅ Handle user input and call continue-conversation API
//     const handleResponse = async (e) => {
//         if (e.key === "Enter" && userInput.trim() && sessionId) {
//             const userMessage = userInput.trim();
//             setConversation(prev => [...prev, { type: "user", text: userMessage }]);
//             setUserInput("");

//             try {
//                 const response = await fetch("http://localhost:5000/continue-conversation", {
//                     method: "POST",
//                     headers: { "Content-Type": "application/json" },
//                     body: JSON.stringify({ session_id: sessionId, message: userMessage })
//                 });

//                 const data = await response.json();

//                 if (data.completed) {
//                     navigate("/next-page"); // ✅ Redirect when conversation is complete
//                 } else if (data.message) {
//                     setConversation(prev => [...prev, { type: "bot", text: data.message }]);
//                 }
//             } catch (error) {
//                 console.error("Error continuing conversation:", error);
//             }
//         }
//     };

//     return (
//         <div className="chatbot-container">
//             {/* Header */}
//             <div className="header">
//                 <img src={studenticon} alt="Student Icon" />
//                 <h1>StudyHive</h1>
//             </div>

//             <div className="chat-section">
//                 {/* Profile Section (Scrollable) */}
//                 <div className="profile-section" ref={profileContainerRef}>
//                     <div className="profile-header">
//                         <User />
//                         <h2>Profile</h2>
//                     </div>
//                     <ul>
//                         {Object.entries(responses).map(([question, answer], index) => (
//                             <li key={index} className="profile-entry">
//                                 <strong>{question}</strong>
//                                 <p>{answer}</p>
//                             </li>
//                         ))}
//                     </ul>
//                     {conversation.length > 0 && (
//                         <p className="completion-check">
//                             <Checkmark /> Conversation In Progress
//                         </p>
//                     )}
//                 </div>

//                 {/* Chatbox (Scrollable) */}
//                 <div className="chat-box">
//                     <div className="chat-messages" ref={chatContainerRef}>
//                         {conversation.map((msg, index) => (
//                             <div key={index} className={`chat-message ${msg.type}`}>
//                                 {msg.text}
//                             </div>
//                         ))}
//                     </div>

//                     {/* Fixed Input Box at Bottom */}
//                     <div className="chat-input">
//                         <input
//                             type="text"
//                             placeholder="Type your response..."
//                             value={userInput}
//                             onChange={(e) => setUserInput(e.target.value)}
//                             onKeyDown={handleResponse}
//                         />
//                     </div>
//                 </div>
//             </div>
//         </div>
//     );
// }



//
import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import "../styles/ChatbotScreen.css";
import studenticon from "../assets/studenticon.jpg";
import { User } from "@carbon/icons-react";
import { Checkmark } from "@carbon/icons-react";

export default function ChatbotScreen() {
    const location = useLocation();
    const navigate = useNavigate();
    const { category } = location.state || {};

    const [conversation, setConversation] = useState([]);
    const [responses, setResponses] = useState(JSON.parse(localStorage.getItem("userProfile")) || {});
    const [userInput, setUserInput] = useState("");
    const [sessionId, setSessionId] = useState(null);
    const [profileCompleted, setProfileCompleted] = useState(false);
    const chatContainerRef = useRef(null);
    const profileContainerRef = useRef(null);

    useEffect(() => {
        const startConversation = async () => {
            try {
                const response = await fetch("http://localhost:5000/start-conversation", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mode: category })
                });

                const data = await response.json();
                if (data.session_id && data.message) {
                    setSessionId(data.session_id);
                    setConversation([{ type: "bot", text: data.message }]);
                }
            } catch (error) {
                console.error("Error starting conversation:", error);
            }
        };

        startConversation();
    }, [category]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [conversation]);

    useEffect(() => {
        if (profileContainerRef.current) {
            profileContainerRef.current.scrollTop = profileContainerRef.current.scrollHeight;
        }
    }, [responses]);

    const handleResponse = async (e) => {
        if (e.key === "Enter" && userInput.trim() && sessionId) {
            const userMessage = userInput.trim();
            setConversation(prev => [...prev, { type: "user", text: userMessage }]);
            setUserInput("");

            try {
                const response = await fetch("http://localhost:5000/continue-conversation", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: sessionId, message: userMessage })
                });

                const data = await response.json();

                if (data.completed) {
                    setProfileCompleted(true);
                    localStorage.setItem("userProfile", JSON.stringify(responses));

                    const payload = { data: responses };
                    const recommendationResponse = await fetch("http://localhost:5000/recommend-courses", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });

                    const recommendations = await recommendationResponse.json();
                    localStorage.setItem("recommendations", JSON.stringify(recommendations.recommendations));
                    navigate("/user-selection");

                } else if (data.message) {
                    setConversation(prev => [...prev, { type: "bot", text: data.message }]);
                }

                // Update responses in local state and local storage
                const updatedResponses = { ...responses, userMessage };
                setResponses(updatedResponses);
                localStorage.setItem("userProfile", JSON.stringify(updatedResponses));

            } catch (error) {
                console.error("Error continuing conversation:", error);
            }
        }
    };

    return (
        <div className="chatbot-container">
            <div className="header">
                <img src={studenticon} alt="Student Icon" />
                <h1>StudyHive</h1>
            </div>

            <div className="chat-section">
                <div className="profile-section" ref={profileContainerRef}>
                    <div className="profile-header">
                        <User />
                        <h2>Profile</h2>
                    </div>
                    <ul>
                        {Object.entries(responses).map(([key, value], index) => (
                            <li key={index} className="profile-entry">
                                <strong>{key}:</strong> {Array.isArray(value) ? value.join(", ") : value}
                            </li>
                        ))}
                    </ul>
                    {profileCompleted && (
                        <p className="completion-check">
                            <Checkmark /> Profile Completed
                        </p>
                    )}
                </div>

                <div className="chat-box">
                    <div className="chat-messages" ref={chatContainerRef}>
                        {conversation.map((msg, index) => (
                            <div key={index} className={`chat-message ${msg.type}`}>
                                {msg.text}
                            </div>
                        ))}
                    </div>

                    <div className="chat-input">
                        <input
                            type="text"
                            placeholder="Type your response..."
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyDown={handleResponse}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
