import React, { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import './GrokChat.css';
import axios from "axios";

function GrokChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sidebarVideo, setSidebarVideo] = useState(null); // null or {type: 'mp4'|'youtube', url: string}
  const [chips, setChips] = useState([]);
  const [ableToChat, setAbleToChat] = useState(false);

  const handleSend = async () => {
    if (input.trim() === '') return;

    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=)?([A-Za-z0-9_-]{11})/;
    const isYoutubeUrl = youtubeRegex.test(input.trim());

    if (isYoutubeUrl) {
      setAbleToChat(true);
      const videoId = input.match(youtubeRegex)[5];
      const youtubeEmbedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&playlist=${videoId}`;
      const newMessage = { text: 'Shared a YouTube video', sender: 'user' };
      setMessages([...messages, newMessage]);
      setSidebarVideo({ type: 'youtube', url: youtubeEmbedUrl });
      setInput('');

      const botMessage = {
        text: "Uploading YouTube video. This may take a few minutes...",
        sender: 'bot',
      };
      setMessages((prev) => [...prev, botMessage]);

      const response = await axios.post(
        "http://127.0.0.1:8000/upload_video_url",
        {"url": youtubeEmbedUrl},
        {
          headers: { "Content-Type": "application/json" }
        }
      );
      console.log(response);

      const botMessage2 = {
        text: "Uploaded! Your YouTube video is now playing in the sidebar.",
        sender: 'bot',
      };
      setMessages((prev) => [...prev, botMessage2]);
    } else {
      if (ableToChat) {
        const newMessage = { text: input, sender: 'user' };
        setMessages([...messages, newMessage]);
        setInput('');

        const response = await axios.post(
          "http://127.0.0.1:8000/chat",
          { "chat": input, "mode": "spoken" },
          {
            headers: { "Content-Type": "application/json" }
          }
        );
        console.log(response.data.player);

        const botMessage2 = { text: "Found it! Here's the clip from the video: ", sender: 'bot', videoUrl: response.data.player };
        setMessages((prev) => [...prev, botMessage2]);
      } else {
        const newMessage = { text: input, sender: 'user' };
        setMessages([...messages, newMessage]);
        setInput('');

        setTimeout(() => {
          const botMessage = { text: `${input} is fascinating!`, sender: 'bot' };
          setMessages((prev) => [...prev, botMessage]);
        }, 1000);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="grok-chat-container">
      <PanelGroup direction="horizontal">
        <Panel defaultSize={25} minSize={20} className="sidebar-panel">
          <div className="sidebar-content">
            <h3>View</h3>
            <div className="video-wrapper">
              {sidebarVideo ? (
                sidebarVideo.type === 'mp4' ? (
                  <video src={sidebarVideo.url} controls className="sidebar-video" muted playsInline autoPlay loop />
                ) : (
                  <iframe src={sidebarVideo.url} className="sidebar-video" frameBorder="0" allow="autoplay; encrypted-media" allowFullScreen />
                )
              ) : (
                <p className="no-video">Upload an MP4 or paste a YouTube URL!</p>
              )}
            </div>
            <p>Video footage</p>
          </div>
        </Panel>

        <PanelResizeHandle className="resize-handle" />

        <Panel defaultSize={75} minSize={50} className="chat-panel">
          <div className="chat-header">
            <h2>Chat</h2>
          </div>
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                {msg.text && <span>{msg.text}</span>}
                {msg.videoUrl && (
                  <a href={msg.videoUrl} target="_blank" rel="noopener noreferrer">{msg.videoUrl}</a>
                )}
              </div>
            ))}
          </div>
          <div className="chat-input">
            <textarea
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything or paste a YouTube URL..."
            />
            <button onClick={handleSend}>Send</button>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}

export default GrokChat;
