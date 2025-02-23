import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/UserSelection.css";
import studenticon from "../assets/studenticon.jpg";

export default function UserSelection() {
    const navigate = useNavigate();
    const [recommendations, setRecommendations] = useState([]);
    const [selectedCourses, setSelectedCourses] = useState([]);

    useEffect(() => {
        const storedRecommendations = JSON.parse(localStorage.getItem("recommendations")) || [];
        setRecommendations(storedRecommendations);
    }, []);

    const handleSelect = (course) => {
        setSelectedCourses(prev => {
            if (prev.some(selected => selected.course === course.course)) {
                return prev.filter(selected => selected.course !== course.course);
            } else {
                return [...prev, course];
            }
        });
    };

    const handleNext = () => {
        if (selectedCourses.length > 0) {
            localStorage.setItem("selectedCourses", JSON.stringify(selectedCourses));
            navigate("/selected-details");
        } else {
            alert("Please select at least one course before proceeding.");
        }
    };

    return (
        <div className="user-selection-container">
            <div className="header">
                <img src={studenticon} alt="Student Icon" />
                <h1>StudyHive</h1>
            </div>

            <div className="recommendations-section">
                <h2>Recommended Courses</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Select</th>
                            <th>Course</th>
                            <th>University</th>
                            <th>Tuition Fee</th>
                            <th>Required Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recommendations.length > 0 ? (
                            recommendations.map((rec, index) => (
                                <tr key={index}>
                                    <td>
                                        <input
                                            type="checkbox"
                                            checked={selectedCourses.some(selected => selected.course === rec.course)}
                                            onChange={() => handleSelect(rec)}
                                        />
                                    </td>
                                    <td>{rec.course}</td>
                                    <td>{rec.university}</td>
                                    <td>${rec.estimated_tuition_fee}</td>
                                    <td>{rec.required_academic_score}</td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5">No recommendations available</td>
                            </tr>
                        )}
                    </tbody>
                </table>
                <button className="next-button" onClick={handleNext}>Next</button>
            </div>
        </div>
    );
}
