
//debug
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
    const [userInput, setUserInput] = useState("");
    const [sessionId, setSessionId] = useState(null);
    const [profileCompleted, setProfileCompleted] = useState(false);
    const [profileData, setProfileData] = useState(null);
    const chatContainerRef = useRef(null);
    const profileContainerRef = useRef(null);

    useEffect(() => {
        const startConversation = async () => {
            console.log("🔵 Starting conversation...");
            try {
                const response = await fetch("http://localhost:5000/start-conversation", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mode: category })
                });

                const data = await response.json();
                console.log("✅ Start conversation response:", data);

                if (data.session_id && data.message) {
                    setSessionId(data.session_id);
                    setConversation([{ type: "bot", text: data.message }]);
                }
            } catch (error) {
                console.error("❌ Error starting conversation:", error);
            }
        };

        startConversation();
    }, [category]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [conversation]);

    const handleResponse = async (e) => {
        if (e.key === "Enter" && userInput.trim() && sessionId && !profileCompleted) {
            const userMessage = userInput.trim();
            setConversation(prev => [...prev, { type: "user", text: userMessage }]);
            setUserInput("");

            try {
                console.log("📤 Sending user input:", { session_id: sessionId, message: userMessage });

                const response = await fetch("http://localhost:5000/continue-conversation", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: sessionId, message: userMessage })
                });

                const data = await response.json();
                console.log("🟡 Continue conversation response:", data);

                if (data.completed) {
                    console.log("✅ Profile completed received from backend!");
                    setProfileCompleted(true);
                    setProfileData(data.profile);
                } else if (data.message) {
                    setConversation(prev => [...prev, { type: "bot", text: data.message }]);
                }
            } catch (error) {
                console.error("❌ Error continuing conversation:", error);
            }
        }
    };

    const handleNext = async () => {
        if (!profileData) {
            console.error("❌ Error: Profile data is missing!");
            return;
        }

        // ✅ Ensure Payload Format Matches Exactly
        const formattedProfile = {
            data: {
                academic_score: profileData.academic_score,
                preferred_countries: Array.isArray(profileData.preferred_countries) ? profileData.preferred_countries : [],
                areas_of_interest: Array.isArray(profileData.areas_of_interest) ? profileData.areas_of_interest : [],
                budget_range: {
                    min: profileData.budget_range?.min ?? 0,
                    max: profileData.budget_range?.max ?? 0
                }
            }
        };

        console.log("📤 Sending profile data to recommend-courses API:", JSON.stringify(formattedProfile, null, 2));

        try {
            const recommendationResponse = await fetch("http://localhost:5000/recommend-courses", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formattedProfile)
            });

            console.log("🟡 Waiting for recommendations response...");

            if (!recommendationResponse.ok) {
                throw new Error(`API Error: ${recommendationResponse.status}`);
            }

            const recommendations = await recommendationResponse.json();
            console.log("✅ Recommendations API response:", recommendations);

            if (recommendations.recommendations && recommendations.recommendations.length > 0) {
                console.log("💾 Storing recommendations in localStorage...");
                localStorage.setItem("recommendations", JSON.stringify(recommendations.recommendations));

                console.log("➡️ Navigating to /user-selection");
                navigate("/user-selection");
            } else {
                console.error("❌ No recommendations received from API! Double-check payload structure.");
                console.log("⚠️ Navigating to /user-selection even if recommendations are empty.");
                navigate("/user-selection"); // ✅ Ensure navigation happens even if response is empty
            }
        } catch (error) {
            console.error("❌ Error fetching recommendations:", error);
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
                    {profileCompleted ? (
                        <>
                            <p className="completion-check">
                                <Checkmark /> Profile Completed
                            </p>
                            <button onClick={handleNext} className="next-button">Next</button>
                        </>
                    ) : (
                        <p className="in-progress">Conversation In Progress</p>
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
                            disabled={profileCompleted}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
