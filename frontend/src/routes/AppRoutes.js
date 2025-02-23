import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "../components/HomePage";  // FIXED PATH
import SelectionPage from "../components/SelectionPage";  // FIXED PATH
import ChatbotScreen from "../components/ChatbotScreen";  // FIXED PATH

function AppRoutes() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/selection" element={<SelectionPage />} />
                <Route path="/chatbot" element={<ChatbotScreen />} /> {/* ADD THIS ROUTE */}
            </Routes>
        </Router>
    );
}

export default AppRoutes;
