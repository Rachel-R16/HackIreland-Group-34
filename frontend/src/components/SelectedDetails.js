import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/SelectedDetails.css";
import studenticon from "../assets/studenticon.jpg";

export default function SelectedDetails() {
    const navigate = useNavigate();
    const [selectedCourses, setSelectedCourses] = useState([]);
    const [selectedFinalCourse, setSelectedFinalCourse] = useState(null);
    const [showNotification, setShowNotification] = useState(false);

    useEffect(() => {
        const storedCourses = JSON.parse(localStorage.getItem("selectedCourses")) || [];
        if (storedCourses.length > 0) {
            setSelectedCourses(storedCourses);
        } else {
            navigate("/selected-details");
        }
    }, [navigate]);

    const handleFinalSelection = (course) => {
        setSelectedFinalCourse(course);
        setShowNotification(true);
        setTimeout(() => {
            window.location.href = `https://www.google.com/search?q=${course.university}`;
        }, 2000);
    };

    return (
        
        <div className="selected-details-container">
             <div className="header">
                            <img src={studenticon} alt="Student Icon" />
                            <h1>StudyHive</h1>
                        </div>
            <h2 style={{marginTop:"70px"}}>Confirm Your Selection</h2>
            {showNotification && (
                <div className="notification">✅ Thank You! Redirecting...</div>
            )}
            <div className="courses-container">
                {selectedCourses.map((course, index) => (
                    <div key={index} className="course-card" onClick={() => handleFinalSelection(course)}>
                        <h3>{course.course}</h3>
                        <p><strong>University:</strong> {course.university}</p>
                        <p><strong>Tuition Fee:</strong> ${course.estimated_tuition_fee}</p>
                        <p><strong>Required Score:</strong> {course.required_academic_score}</p>
                        <p>Click to confirm selection</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
