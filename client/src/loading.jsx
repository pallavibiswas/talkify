import React, { useState } from "react";
import "./loading.css"; // Ensure the CSS file is linked correctly

const Loading = () => {
  // Array of different texts
  const messages = [
    "Speak with clarity, and your words will be heard.",
    "Slow down, your message is worth savoring.",
    "A well-timed pause speaks louder than words.",
    "Confidence in speech starts with confidence in silence.",
    "Use your voice as a tool, not just a sound.",
    "I’m learning every day, just like you!"
  ];

  const [text, setText] = useState(messages[0]); // Initialize with the first message
  const [index, setIndex] = useState(0); // Keep track of the current index in the array

  // Function to change the text when the image is clicked
  const handleImageClick = () => {
    const nextIndex = (index + 1) % messages.length; // Cycle through messages
    setText(messages[nextIndex]); // Update the text
    setIndex(nextIndex); // Update the index
  };

  return (
    <div className="loading-container">
      {/* Heading for waiting message */}
      <h1>Please wait until the model loads! Click the girl for general tips!</h1>

      <p>{text}</p> {/* Display current text */}
      <img
        src="girl.png"  // Replace with your image path
        alt="Click me"
        className="loading-image"
        onClick={handleImageClick} // Trigger text change on click
      />
    </div>
  );
};

export default Loading;
