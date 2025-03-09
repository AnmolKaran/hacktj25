import React, { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import './GrokChat.css';

function GrokChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sidebarVideo, setSidebarVideo] = useState(null);

  const handleSend = () => {
    if (input.trim() === '') return;
    const newMessage = { text: input, sender: 'user' };
    setMessages([...messages, newMessage]);
    setInput('');

    setTimeout(() => {
      const botMessage = { text: `Grok says: ${input} is fascinating!`, sender: 'bot' };
      setMessages((prev) => [...prev, botMessage]);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (!file || !file.type.startsWith('video/mp4')) return; // Only allow MP4

    const reader = new FileReader();
    reader.onload = (e) => {
      const videoDataUrl = e.target.result;
      // Add a text message to the chat indicating the upload
      const newMessage = { text: 'Uploaded an MP4 video', sender: 'user' };
      setMessages([...messages, newMessage]);
      // Set the video to display in the sidebar
      setSidebarVideo(videoDataUrl);

      // Simulate bot response
      setTimeout(() => {
        const botMessage = {
          text: "Grok says: Cool video! It’s now playing in the sidebar.",
          sender: 'bot',
        };
        setMessages((prev) => [...prev, botMessage]);
      }, 1000);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="grok-chat-container">
      <PanelGroup direction="horizontal">
        {/* Sidebar Panel with Uploaded Video */}
        <Panel defaultSize={25} minSize={20} className="sidebar-panel">
          <div className="sidebar-content">
            <h3>Grok's View</h3>
            <div className="video-wrapper">
              {sidebarVideo ? (
                <video
                  src={sidebarVideo}
                  controls
                  className="sidebar-video"
                  muted
                  playsInline
                  autoPlay
                  loop
                />
              ) : (
                <p className="no-video">Upload an MP4 to see it here!</p>
              )}
            </div>
            <p>Video footage</p>
          </div>
        </Panel>

        {/* Resize Handle */}
        <PanelResizeHandle className="resize-handle" />

        {/* Main Chat Panel */}
        <Panel defaultSize={75} minSize={50} className="chat-panel">
          <div className="chat-header">
            <h2>Grok Chat</h2>
          </div>
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}
              >
                {msg.text && <span>{msg.text}</span>}
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
            />
            <label className="upload-button">
              <input
                type="file"
                accept="video/mp4"
                onChange={handleVideoUpload}
                style={{ display: 'none' }}
              />
              <span>Upload MP4</span>
            </label>
            <button onClick={handleSend}>Send</button>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}

export default GrokChat;