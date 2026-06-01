import logo from "../assets/ap_logo.png";

import {
    deleteConversation,
} from "../conversations";

export default function Sidebar({

    currentUser,

    conversations,

    selectedId,

    onSelect,

    onNewChat,

    setPage,

    page,

}) {

    return (

        <aside className="sidebar">

            <div className="sidebar-top">

                <div className="sidebar-logo">

                    <img
                        src={logo}
                        alt="AP Government"
                    />

                </div>

                <button
                    className="new-chat-btn"
                    onClick={onNewChat}
                >

                    + New Conversation

                </button>

                {/* Navigation */}

                <div className="sidebar-title">

                    Navigation

                </div>

                <div

                    className={
                        page === "chat"
                            ? "nav-item active"
                            : "nav-item"
                    }

                    onClick={() =>
                        setPage("chat")
                    }

                >

                    💬 Chats

                </div>

                {

                    currentUser?.role === "admin" && (

                        <div

                            className={
                                page === "users"
                                    ? "nav-item active"
                                    : "nav-item"
                            }

                            onClick={() =>
                                setPage("users")
                            }

                        >

                            👥 Users

                        </div>

                    )

                }

                {
                    currentUser?.role === "admin" && (

                        <div

                            className={
                                page === "documents"
                                    ? "nav-item active"
                                    : "nav-item"
                            }

                            onClick={() =>
                                setPage(
                                    "documents"
                                )
                            }

                        >

                            📄 Documents

                        </div>

                    )
                }

                <div className="sidebar-title">

                    Recent Conversations

                </div>

                <div className="conversation-list">

                    {

                        conversations.map(
                            (chat) => (

                                <div

                                    key={chat.id}

                                    className={
                                        selectedId === chat.id
                                            ? "history active"
                                            : "history"
                                    }

                                >

                                    <div className="chat-row">

                                        <span
                                            onClick={() =>
                                                onSelect(chat.id)
                                            }
                                        >

                                            {chat.title}

                                        </span>

                                        <button

                                            className="delete-chat"

                                            onClick={async e => {

                                                e.stopPropagation();

                                                await deleteConversation(
                                                    chat.id
                                                );

                                                window.location.reload();

                                            }}

                                        >

                                            ×

                                        </button>

                                    </div>

                                </div>

                            )
                        )

                    }

                </div>

            </div>

            <div className="sidebar-bottom">

                <div className="sidebar-user">

                    <div className="avatar">

                        {

                            currentUser?.username
                                ?.charAt(0)
                                ?.toUpperCase()

                        }

                    </div>

                    <div>

                        <div className="user-name">

                            {currentUser?.username}

                        </div>

                        <div className="user-role">

                            {currentUser?.role}

                        </div>

                    </div>

                </div>

                <button

                    className="logout-btn"

                    onClick={() => {

                        localStorage.clear();

                        window.location.reload();

                    }}

                >

                    Logout

                </button>

            </div>

        </aside>

    );

}