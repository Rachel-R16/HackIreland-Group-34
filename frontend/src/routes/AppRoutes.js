// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import HomePage from "../components/HomePage";  // FIXED PATH
// import SelectionPage from "../components/SelectionPage";  // FIXED PATH
// import ChatbotScreen from "../components/ChatbotScreen";  // FIXED PATH

// function AppRoutes() {
//     return (
//         <Router>
//             <Routes>
//                 <Route path="/" element={<HomePage />} />
//                 <Route path="/selection" element={<SelectionPage />} />
//                 <Route path="/chatbot" element={<ChatbotScreen />} /> {/* ADD THIS ROUTE */}
//             </Routes>
//         </Router>
//     );
// }

// export default AppRoutes;

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../components/HomePage";
import SelectionPage from "../components/SelectionPage";
import ChatbotScreen from "../components/ChatbotScreen";
import UserSelection from "../components/UserSelection";
import SelectedDetails from "../components/SelectedDetails";

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/selection" element={<SelectionPage />} />
                <Route path="/chatbot" element={<ChatbotScreen />} />
                <Route path="/user-selection" element={<UserSelection />} />
                <Route path="/selected-details" element={<SelectedDetails />} />
                <Route path="*" element={<h1>404 Not Found</h1>} />
            </Routes>
        </Router>
    );
}
