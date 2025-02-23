import React from "react";
import "../styles/HomePage.css";
import backgroundImage from "../assets/background.png";
import logoImage from "../assets/studenticon.jpg";

const HomePage = () => {
  return (
    <div className="home-container" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <div className="logo-title-container">
        <img src={logoImage} alt="Logo" className="logo" />
        <h1 className="title">StudentHive</h1>
      </div>
      <h2 className="main-heading">FIND EVERYTHING</h2>
      <div className="button-container">
        <button className="large-button">FIND COURSES</button>
        <button className="large-button">FIND UNIVERSITIES</button>
        <button className="large-button">FIND ACCOMMODATION</button>
      </div>
      <button className="large-button" style={{ top: "75%" }}>FIND EVERYTHING</button>
    </div>
  );
};

export default HomePage;
