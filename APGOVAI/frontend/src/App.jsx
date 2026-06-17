import { useEffect, useState } from "react";

import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import Login from "./pages/Login";
import Users from "./pages/Users";
import Documents
  from "./pages/Documents";

import { sendMessage } from "./api";
import LanguageToggle from "./components/LanguageToggle";

import {
  createConversation,
  getConversations,
  getMessages,
} from "./conversations";

import {
  DEFAULT_LANGUAGE,
  LANGUAGES,
  getInitialLanguage,
  getText,
} from "./i18n";

import { getCurrentUser } from "./user";
import { getChatLanguages } from "./api";

import cm from "./assets/cm.png";
import deputy from "./assets/deputy_cm.png";
import minister from "./assets/it_minister.png";

import "./styles.css";
import Sidebar from "./components/Sidebar";

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

  const [language, setLanguage] =
    useState(getInitialLanguage);

  const [languageOptions,
    setLanguageOptions] =
    useState(LANGUAGES);

  const t = getText(language);

  function updateLanguage(nextLanguage) {
    const supported = languageOptions.some(
      option => option.code === nextLanguage
    );
    const resolvedLanguage = supported
      ? nextLanguage
      : DEFAULT_LANGUAGE;

    localStorage.setItem(
      "language",
      resolvedLanguage
    );

    setLanguage(resolvedLanguage);

  }

  useEffect(() => {

    if (!token) {

      return;

    }

    loadConversations();

    loadUser();

    loadLanguages();

  }, [token]);

  async function loadLanguages() {
    try {
      const data = await getChatLanguages();
      const options = Array.isArray(data?.languages)
        ? data.languages
            .filter(
              option =>
                option &&
                typeof option.code === "string" &&
                typeof option.label === "string"
            )
            .map(
              option => ({
                code: option.code,
                label: option.label,
              })
            )
        : [];

      if (options.length > 0) {
        setLanguageOptions(options);

        if (
          !options.some(
            option => option.code === language
          )
        ) {
          const fallback =
            options.some(
              option =>
                option.code === DEFAULT_LANGUAGE
            )
              ? DEFAULT_LANGUAGE
              : options[0].code;

          updateLanguage(fallback);
        }
      }
    } catch {
      // Keep the bundled defaults so the app remains usable if the endpoint is unavailable.
      setLanguageOptions(LANGUAGES);
    }
  }

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

        language,

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
        language={language}
        onLanguageChange={
          updateLanguage
        }
        languageOptions={languageOptions}
        t={t}
      />

    );

  }

  if (page === "users") {
    return (
      <Users
        setPage={setPage}
        language={language}
        onLanguageChange={
          updateLanguage
        }
        languageOptions={languageOptions}
        t={t}
      />
    );
  }

  if (page === "documents") {
    return (
      <Documents
        setPage={setPage}
        language={language}
        onLanguageChange={
          updateLanguage
        }
        languageOptions={languageOptions}
        t={t}
      />
    );
  }

  return (

    <div
      className="layout"
      lang={language}
    >

      <Sidebar
        currentUser={user}
        conversations={conversations}
        selectedId={selectedConversation}
        onSelect={selectConversation}
        onNewChat={createNewChat}
        setPage={setPage}
        page={page}
        t={t}
      />

      <div className="main">

        <header className="header">

          <div className="brand">

            <div>

              <h1>APGovAI</h1>

              <p className="subtitle">
                {t.app.subtitle}
              </p>

            </div>

          </div>

          <div className="header-actions">

            <LanguageToggle
              language={language}
              onChange={updateLanguage}
              label={t.common.language}
              compact
              options={languageOptions}
            />

            <div className="leaders">

            <div>

              <img
                src={cm}
                alt=""
              />

              <span>
                {t.leaders.chiefMinister}
              </span>

            </div>

            <div>

              <img
                src={deputy}
                alt=""
              />

              <span>
                {t.leaders.deputyChiefMinister}
              </span>

            </div>

            <div>

              <img
                src={minister}
                alt=""
              />

              <span>
                {t.leaders.itMinister}
              </span>

            </div>

            </div>

          </div>

        </header>

        <section className="chat">

          {

            messages.length === 0 && (

              <div className="hero">

                <h2>
                  {t.app.title}
                </h2>

                <p>
                  {
                    t.app.description
                  }
                </p>

              </div>

            )

          }

          <ChatWindow
            messages={messages}
            loading={loading}
            t={t}
          />

          <ChatInput
            loading={loading}
            onSend={handleSend}
            placeholder={
              t.app.placeholder
            }
            sendLabel={t.chat.send}
          />

        </section>

      </div>

    </div>

  );

}
