import React from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import background from "../assets/background.png";
import logo from "../assets/studenticon.jpg";
import { Course, Education, Hotel } from "@carbon/icons-react";
import { useState } from "react";

const SelectionPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSelection = async (category) => {
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/start-conversation", {
        mode: category,
      });
      navigate("/chatbot", { state: { category, questions: response.data.questions || [] } });
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    setLoading(false);
  };

  return (
    <div
      className="h-screen w-screen flex flex-col items-center justify-center text-white relative"
      style={{
        backgroundImage: `url(${background})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div className="absolute top-6 flex flex-col items-center">
        <img src={logo} alt="StudentHive" className="h-10 w-10 object-contain" />
        <h1 className="text-lg font-semibold mt-2">StudyHive</h1>
      </div>

      <h1 className="text-4xl font-bold mb-10 text-center">Choose Your Preference</h1>

      <div className="flex gap-6 mb-6">
        <button className="px-6 py-3 bg-gray-500 hover:bg-gray-600 rounded-md text-md flex items-center gap-2" onClick={() => handleSelection("course")}>
          <Course /> Course
        </button>
        <button className="px-6 py-3 bg-gray-500 hover:bg-gray-600 rounded-md text-md flex items-center gap-2" onClick={() => handleSelection("university")}>
          <Education /> University
        </button>
        <button className="px-6 py-3 bg-gray-500 hover:bg-gray-600 rounded-md text-md flex items-center gap-2" onClick={() => handleSelection("accommodation")}>
          <Hotel /> Accommodation
        </button>
      </div>

      <p>Instead</p>
      <button className="mt-6 px-8 py-3 bg-gray-600 hover:bg-gray-700 rounded-md text-lg" onClick={() => handleSelection("discover-more")}>Discover More</button>
      {loading && <p>Loading...</p>}

      <footer className="absolute bottom-4 text-center text-sm text-gray-300">
        <p>&copy; {new Date().getFullYear()} StudyHive. All Rights Reserved.</p>
      </footer>
    </div>
  );
};

export default SelectionPage;
