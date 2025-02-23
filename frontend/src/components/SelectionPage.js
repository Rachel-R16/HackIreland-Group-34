// // src/components/SelectionPage.js
// import { useNavigate } from "react-router-dom";
// import "../styles/SelectionPage.css";
// import studenticon from "../assets/studenticon.jpg";
// import { Course, Education, Hotel } from "@carbon/icons-react";
// import { useState } from "react";

// export default function SelectionPage() {
//     const navigate = useNavigate();
//     const [loading, setLoading] = useState(false);

//     // const handleSelection = async (category) => {
//     //     setLoading(true);
//     //     try {
//     //         const response = await fetch(`http://localhost:5000/api/questions?category=${category}`);
//     //         const data = await response.json();
//     //         navigate("/chatbot", { state: { category, questions: data } });
//     //     } catch (error) {
//     //         console.error("Error fetching data:", error);
//     //     }
//     //     setLoading(false);
//     // };
//     const handleSelection = async (category) => {
//         setLoading(true);
//         try {
//             // Mock API Response
//             const mockQuestions = {
//                 course: ["What course are you interested in?", "Do you prefer online or in-person?", "What is your budget?"],
//                 university: ["Which country are you looking to study in?", "Do you have a preferred university?", "What is your budget?"],
//                 accommodation: ["Do you prefer on-campus or off-campus?", "What is your budget range?", "Do you have any location preference?"],
//                 "discover-more": ["What are you interested in?", "Would you like suggestions on courses or universities?", "Any location preference?"],
//             };
    
//             // Use mock data instead of API response
//             const data = mockQuestions[category] || ["No questions available"];
    
//             // Navigate to ChatbotScreen with mock questions
//             navigate("/chatbot", { state: { category, questions: data } });
    
//         } catch (error) {
//             console.error("Error fetching data:", error);
//         }
//         setLoading(false);
//     };
    
//     return (
//         <div className="selection-container">
//             <div className="header">
//                 <img src={studenticon} alt="Student Icon" />
//                 <h1>StudyHive</h1>
//             </div>
//             <h2 className="selection-title">Choose Your Preference</h2>
//             <div className="selection-options">
//                 <div className="selection-card" onClick={() => handleSelection("course")}>
//                     <Course /> <span>Course</span>
//                 </div>
//                 <div className="selection-card" onClick={() => handleSelection("university")}> 
//                     <Education /> <span>University</span>
//                 </div>
//                 <div className="selection-card" onClick={() => handleSelection("accommodation")}>
//                     <Hotel /> <span>Accommodation</span>
//                 </div>
//             </div>
//             <p>OR</p>
//             <div className="all-in-one" onClick={() => handleSelection("discover-more")}>Discover More</div>
//             {loading && <p>Loading...</p>}
//         </div>
//     );
// }


// src/components/SelectionPage.js
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
            // Send mode parameter
            const response = await fetch("http://localhost:5000/start-conversation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mode: category }),
            });

            if (!response.ok) {
                throw new Error("Failed to start conversation");
            }

            const data = await response.json();

            // Navigate to ChatbotScreen with initial questions
            navigate("/chatbot", { state: { category, questions: data.questions || [] } });

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
            <p>OR</p>
            <div className="all-in-one" onClick={() => handleSelection("discover-more")}>
                Discover More
            </div>
            {loading && <p>Loading...</p>}
        </div>
    );
}
