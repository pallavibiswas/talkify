import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignUp from './SignUp';
import Login from './Login';
import Section from './Section';
import Welcome from './Welcome'; 

const App = () => {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/welcome" element={<Welcome />} /> 
          <Route path="/section" element={<Section />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/" element={<Welcome />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;