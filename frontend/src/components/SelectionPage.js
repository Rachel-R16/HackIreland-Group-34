import { useNavigate } from "react-router-dom";
import "../styles/SelectionPage.css";
import studenticon from "../assets/studenticon.jpg";
import { Course, Education, Hotel } from "@carbon/icons-react";
import { useState } from "react";

export default function SelectionPage() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSelection = async (category) => {
        setLoading(true);
        try {
            // Map frontend categories to backend profile types
            const profileTypeMap = {
                'course': 'course_profile',
                'university': 'university_profile',
                'accommodation': 'accommodation_profile',
                'discover-more': 'general'
            };

            const response = await fetch("http://localhost:5000/start-conversation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    profile_type: profileTypeMap[category]
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to start conversation");
            }

            const data = await response.json();

            // Navigate to ChatbotScreen with initial questions and profile type
            navigate("/chatbot", { 
                state: { 
                    category, 
                    profile_type: profileTypeMap[category],
                    questions: data.questions || [] 
                } 
            });

        } catch (error) {
            console.error("Error fetching data:", error);
        }
        setLoading(false);
    };

    return (
        <div className="selection-container">
            <div className="header">
                <img src={studenticon} alt="Student Icon" />
                <h1>StudyHive</h1>
            </div>
            <h2 className="selection-title">Choose Your Preference</h2>
            <div className="selection-options">
                <div className="selection-card" onClick={() => handleSelection("course")}>
                    <Course /> <span>Course</span>
                </div>
                <div className="selection-card" onClick={() => handleSelection("university")}>
                    <Education /> <span>University</span>
                </div>
                <div className="selection-card" onClick={() => handleSelection("accommodation")}>
                    <Hotel /> <span>Accommodation</span>
                </div>
            </div>
            <p>Instead</p>
            <div className="all-in-one" onClick={() => handleSelection("discover-more")}>
                Discover More
            </div>
            {loading && <p>Loading...</p>}
              {/* Footer (Fixed at Bottom) */}
              <footer className="home-footer">
                <p>&copy; {new Date().getFullYear()} StudyHive. All Rights Reserved.</p>
            </footer>
        </div>
        
    );
}
