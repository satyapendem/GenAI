import { useEffect, useState } from "react";

import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import Login from "./pages/Login";
import Users from "./pages/Users";
import Documents
  from "./pages/Documents";

import { sendMessage } from "./api";

import {
  createConversation,
  getConversations,
  getMessages,
} from "./conversations";

import { getCurrentUser } from "./user";

import logo from "./assets/ap_logo.png";
import cm from "./assets/cm.png";
import deputy from "./assets/deputy_cm.png";
import minister from "./assets/it_minister.png";

import "./styles.css";
import Sidebar from "./components/Sidebar";

const CONTENT = {
  subtitle:
    "AI Assistant for Andhra Pradesh Government",

  title:
    "How can I help you today?",

  description:
    "Ask APGovAI about Government Orders, Budgets, Policies, Circulars, Reports and Acts.",

  placeholder:
    "Ask APGovAI...",
};

export default function App() {

  const [token, setToken] =
    useState(
      localStorage.getItem(
        "token"
      )
    );

  const [loading, setLoading] =
    useState(false);

  const [messages, setMessages] =
    useState([]);

  const [conversations,
    setConversations] =
    useState([]);

  const [
    selectedConversation,
    setSelectedConversation,
  ] = useState(null);

  const [user, setUser] =
    useState(null);

  const [page, setPage] = useState("chat");

  useEffect(() => {

    if (!token) {

      return;

    }

    loadConversations();

    loadUser();

  }, [token]);

  async function loadUser() {

    const data =
      await getCurrentUser();

    setUser(data);

  }

  async function loadConversations() {

    const chats =
      await getConversations();

    setConversations(
      chats
    );

    if (
      chats.length > 0
    ) {

      selectConversation(
        chats[0].id
      );

    }

  }

  async function createNewChat() {

    const chat =
      await createConversation();

    setConversations(
      prev => [
        chat,
        ...prev,
      ]
    );

    setSelectedConversation(
      chat.id
    );

    setMessages([]);

  }

  async function selectConversation(
    conversationId
  ) {

    const msgs =
      await getMessages(
        conversationId
      );

    setSelectedConversation(
      conversationId
    );

    setMessages(
      msgs.map(
        msg =>

          msg.role === "user"

            ? {
              role: "user",
              text:
                msg.content,
            }

            : {
              role:
                "assistant",
              answer:
                msg.content,
            }
      )
    );

  }

  async function handleSend(
    question
  ) {

    if (
      !selectedConversation
    ) {

      return;

    }

    setLoading(true);

    setMessages(
      prev => [

        ...prev,

        {
          role: "user",
          text: question,
        },

        {
          role:
            "assistant",
          answer: "",
        },

      ]
    );

    try {

      await sendMessage(

        selectedConversation,

        question,

        chunk => {

          setMessages(
            prev => {

              const updated =
                [...prev];

              const last =
                updated[
                updated.length - 1
                ];

              updated[
                updated.length - 1
              ] = {

                role:
                  "assistant",

                answer:
                  (
                    last?.answer
                    || ""
                  ) + chunk,

              };

              return updated;

            }
          );

        }

      );

    } finally {

      setLoading(false);

    }

  }

  if (!token) {

    return (

      <Login
        onLogin={
          setToken
        }
      />

    );

  }

  if (page === "users") {
    return (
      <Users setPage={setPage} />
    );
  }

  if (page === "documents") {
    return (
      <Documents setPage={setPage} />
    );
  }

  return (

    <div className="layout">

      <Sidebar
        currentUser={user}
        conversations={conversations}
        selectedId={selectedConversation}
        onSelect={selectConversation}
        onNewChat={createNewChat}
        setPage={setPage}
        page={page}
      />

      <div className="main">

        <header className="header">

          <div className="brand">

            <div>

              <h1>APGovAI</h1>

              <p className="subtitle">
                AI Assistant for Andhra Pradesh Government
              </p>

            </div>

          </div>

          <div className="leaders">

            <div>

              <img
                src={cm}
                alt=""
              />

              <span>
                Chief Minister
              </span>

            </div>

            <div>

              <img
                src={deputy}
                alt=""
              />

              <span>
                Deputy CM
              </span>

            </div>

            <div>

              <img
                src={minister}
                alt=""
              />

              <span>
                IT Minister
              </span>

            </div>

          </div>

        </header>

        <section className="chat">

          {

            messages.length === 0 && (

              <div className="hero">

                <h2>
                  {CONTENT.title}
                </h2>

                <p>
                  {
                    CONTENT.description
                  }
                </p>

              </div>

            )

          }

          <ChatWindow
            messages={messages}
            loading={loading}
          />

          <ChatInput
            loading={loading}
            onSend={handleSend}
            placeholder={
              CONTENT.placeholder
            }
          />

        </section>

      </div>

    </div>

  );

}