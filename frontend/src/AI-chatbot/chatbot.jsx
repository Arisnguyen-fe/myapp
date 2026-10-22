import { useState, useRef, useEffect } from "react";
import { TbMessageChatbotFilled } from "react-icons/tb";
import ChatForm from './components/ChatForm';
import ChatMessage from './components/ChatMessage';
import '../styles/chatbot.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const ChatBot = () => {
  const [chatHistory, setChatHistory] = useState([]);
  const chatBodyRef = useRef();

  const generateBotResponse = async (history) => {
    const updateHistory = (text) => {
      setChatHistory(prev => [...prev.filter(msg => msg.text !== "Thinking..."), { role: "model", text }]);
    }
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history.map(({ role, text }) => ({ role, text })) })
    };

    try {
      // Call our backend, which holds the Gemini API key and forwards the request
      const response = await fetch(`${API_URL}/chatbot/chat`, requestOptions);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Something went wrong!");

      const apiResponseText = data.reply.replace(/\*\*(.*?)\*\*/g, "$1").trim();
      updateHistory(apiResponseText);
    } catch (error) {
      console.log(error);
      updateHistory("Sorry, I can't answer right now. Please try again later.");
    };
  };
  
  // Auto scroll down in chat history when receiving bot's response
  useEffect(() => {
    chatBodyRef.current.scrollTo({ top: chatBodyRef.current.scrollHeight, behavior: "smooth" });
  }, [chatHistory]);

  return (
    <div className="chatbot-popup">
      {/* Chatbot header */}
      <div className="chat-header">
        <div className="header-info">
          <TbMessageChatbotFilled size={50} />
          <h2 className="logo-text">Chatbot</h2>
        </div>
        <button className="material-symbols-rounded">
          keyboard_arrow_down
        </button>
      </div>

      {/* Chatbot body */}
      <div ref={chatBodyRef} className="chat-body">
        <div className="message bot-message">
          <TbMessageChatbotFilled size={45} />
          <p className="message-text">
            Hey there, How can I help you today?
          </p>
        </div>

        {chatHistory.map((chat, index) => (
          <ChatMessage key={index} chat={chat} />
        ))}
      </div>

      {/* Chat Footer */}
      <div className="chat-footer">
        <ChatForm
          chatHistory={chatHistory}
          setChatHistory={setChatHistory}
          generateBotResponse={generateBotResponse}
        />
      </div>
    </div>
  );
};

export default ChatBot
