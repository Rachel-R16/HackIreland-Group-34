import { useNavigate } from "react-router-dom";
import "../styles/HomePage.css";
import studenticon from "../assets/studenticon.jpg";

export default function HomePage() {
    const navigate = useNavigate();

    return (
        <div className="home-container">
            <div className="home-content">
                <div className="home-left">
                    <img src={studenticon} alt="Student Vector" />
                </div>
                <div className="home-right">
                    <h1 className="home-title">StudyHive</h1>
                    <p className="home-description">Your perfect uni, course & stay – in one place!</p>
                    <button className="home-button" onClick={() => navigate("/selection")}>
                        Get Started
                    </button>
                </div>
            </div>

           
            <footer className="home-footer">
                <p>&copy; {new Date().getFullYear()} StudyHive. All Rights Reserved.</p>
            </footer>
        </div>
    );
}
