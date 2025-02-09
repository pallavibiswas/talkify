import React from "react";
import { useNavigate } from "react-router-dom";
import "./welcome.css"; 

const Welcome = () => {
    const navigate = useNavigate();

    return (
        <div className="welcome-container">
            <div className="speech-bubble">
                <h1 className="logo-text">Talkify</h1>
                <p className="subtitle">Your Personal Speech Therapist</p>
            </div>

            
            {/* First Image on the Left */}
            <div className="image-container">
                <img src="/images/female_doctor.png" alt="Doctor" />
            </div>
            
            {/* Second Image on the Right */}
            <div className="image-container-right">
                <img src="/images/male_doctor.png" alt="Doctor" />
            </div>

            <div className="auth-buttons">
                <button className="login-btn" onClick={() => navigate('/login')}>Login</button>
                <button className="signup-btn" onClick={() => navigate('/signup')}>Sign Up</button>
            </div>
        </div>
    );
};

export default Welcome;