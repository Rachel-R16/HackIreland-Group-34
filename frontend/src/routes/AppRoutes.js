import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../components/HomePage";
import ChatbotScreen from "../components/ChatbotScreen";
import SelectedDetails from "../components/SelectedDetails";

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/chatbot" element={<ChatbotScreen />} />
                <Route path="/selected-details" element={<SelectedDetails />} />
                <Route path="*" element={<h1>404 Not Found</h1>} />
            </Routes>
        </Router>
    );
}
