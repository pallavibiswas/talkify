import React, { useState } from 'react';
import { auth, db } from './firebase'; 
import { createUserWithEmailAndPassword } from 'firebase/auth'; 
import { doc, setDoc } from 'firebase/firestore'; 
import { Link, useNavigate } from 'react-router-dom'; 
import './styles.css';

const SignUp = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [FName, setFName] = useState('');
  const [LName, setLName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = auth.currentUser;

      if (user) {
        await setDoc(doc(db, 'Users', user.uid), {
          email: user.email,
          firstName: FName,
          lastName: LName,
        });

        console.log("User signed up successfully!");
        navigate("/section", { state: { firstName: FName } });
      }
    } catch (error) {
      setError(error.message);
      console.error("SignUp error:", error.message);
    }
  };

  return (
    <div className="login-container">
      {/* Left Side - SignUp Form */}
      <div className="left-panel">
        <h2>Sign Up</h2>
        <p>
          Already have an account? <Link to="/login" className="link">Login</Link>
        </p>

        {error && <p className="error-message">{error}</p>}

        <form className="login-form" onSubmit={handleSubmit}>
          <label>First Name</label>
          <input
            type="text"
            placeholder="First Name"
            value={FName}
            onChange={(e) => setFName(e.target.value)}
            required
          />

          <label>Last Name</label>
          <input
            type="text"
            placeholder="Last Name"
            value={LName}
            onChange={(e) => setLName(e.target.value)}
            required
          />

          <label>Email Address</label>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          
          <label>Password</label>
          <input
            type="password"
            placeholder="Enter 6 characters or more"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength="6"
          />

          <button type="submit">Sign Up</button>
        </form>
      </div>

      {/* Right Side - Two Separate Images with Spacing */}
    </div>
  );
};

export default SignUp;
