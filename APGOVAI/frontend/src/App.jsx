import { useEffect, useState } from "react";

import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

import { sendMessage } from "./api";

import logo from "./assets/ap_logo.png";
import cm from "./assets/cm.png";
import deputy from "./assets/deputy_cm.png";
import minister from "./assets/it_minister.png";

import "./styles.css";

const CONTENT = {
  subtitle: "AI Assistant for Andhra Pradesh Government",
  title: "How can I help you today?",
  description:
    "Ask APGovAI about Government Orders, Budgets, Policies, Circulars, Reports and Acts.",
  placeholder: "Ask APGovAI...",
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const storedHistory = localStorage.getItem("apgovai_history");

    if (storedHistory) {
      setHistory(JSON.parse(storedHistory));
    }
  }, []);

  async function handleSend(question) {
    if (!question.trim()) {
      return;
    }

    setLoading(true);

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: question,
      },
      {
        role: "assistant",
        answer: "",
      },
    ]);

    try {
      await sendMessage(question, (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];

          const lastMessage =
            updated[updated.length - 1];

          updated[updated.length - 1] = {
            role: "assistant",
            answer:
              (lastMessage?.answer || "") +
              chunk,
          };

          return updated;
        });
      });

      const updatedHistory = [
        {
          question,
          time: new Date().toLocaleString(),
        },
        ...history,
      ];

      setHistory(updatedHistory);

      localStorage.setItem(
        "apgovai_history",
        JSON.stringify(updatedHistory)
      );
    } catch (error) {
      console.error("Chat Error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <h3>Chats</h3>

        {history.map((chat, index) => (
          <div
            key={index}
            className="history"
          >
            {chat.question}
          </div>
        ))}
      </aside>

      {/* Main Content */}
      <div className="main">
        {/* Header */}
        <header className="header">
          <div className="brand">
            <img
              src={logo}
              alt="APGovAI"
              className="logo"
            />

            <div>
              <h1>APGovAI</h1>

              <p className="subtitle">
                {CONTENT.subtitle}
              </p>
            </div>
          </div>

          <div className="leaders">
            <div>
              <img
                src={cm}
                alt="Chief Minister"
              />
              <span>
                Chief Minister
              </span>
            </div>

            <div>
              <img
                src={deputy}
                alt="Deputy CM"
              />
              <span>
                Deputy CM
              </span>
            </div>

            <div>
              <img
                src={minister}
                alt="IT Minister"
              />
              <span>
                IT Minister
              </span>
            </div>
          </div>
        </header>

        {/* Chat Section */}
        <section className="chat">
          {messages.length === 0 && (
            <div className="hero">
              <h2>{CONTENT.title}</h2>

              <p>
                {CONTENT.description}
              </p>
            </div>
          )}

          <ChatWindow
            messages={messages}
            loading={loading}
          />

          <ChatInput
            loading={loading}
            onSend={handleSend}
            placeholder={CONTENT.placeholder}
          />
        </section>
      </div>
    </div>
  );
}