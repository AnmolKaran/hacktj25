import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Chatbot from './Chatbot';
import Realtime from './Realtime';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/realtime" element={<Realtime />} />
      </Routes>
    </Router>
  );
}

function Home() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const fullTitle = "Welcome to PinPoint";
  const [fadeIn, setFadeIn] = useState(false);
  const [buttonFadeIn, setButtonFadeIn] = useState(false);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setTitle(fullTitle.slice(0, i + 1));
      i++;
      if (i >= fullTitle.length) clearInterval(interval);
    }, 75);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setTimeout(() => {
      setFadeIn(true);
      setButtonFadeIn(true);
    }, 1000);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-blue-500 to-teal-400 text-gray-800 p-8 cursor-default">
      <h1 className="text-7xl font-bold text-white mb-12 font-sans inline-block">
        <span className="typing-text">{title}</span><span className="caret"></span>
      </h1>
      <div className={`transition-opacity duration-1000 ${fadeIn ? 'opacity-100' : 'opacity-0'}`}>
        <div className="flex gap-16 mb-10">
          <Button
            text="ChatBot"
            onClick={() => navigate('/chatbot')}
            bgColor="bg-blue-700"
            hoverColor="hover:bg-blue-800"
            fadeIn={buttonFadeIn}
          />
          <Button
            text="Real Time"
            onClick={() => navigate('/realtime')}
            bgColor="bg-teal-700"
            hoverColor="hover:bg-teal-800"
            fadeIn={buttonFadeIn}
          />
        </div>
      </div>
      <footer className="mt-12 text-center text-gray-100 text-base">
        <p>Created by Soham Jain, Shaurya Jain, Anmol Karan, and Jason Hao</p>
      </footer>
    </div>
  );
}

function Button({ text, onClick, bgColor, hoverColor, fadeIn }) {
  return (
    <button
      onClick={onClick}
      className={`${bgColor} ${hoverColor} text-white font-semibold text-xl py-5 px-16 rounded-full transition-all transform hover:scale-105 shadow-lg ${fadeIn ? 'opacity-100' : 'opacity-0'} transition-opacity duration-1000`}
    >
      {text}
    </button>
  );
}

export default App;
