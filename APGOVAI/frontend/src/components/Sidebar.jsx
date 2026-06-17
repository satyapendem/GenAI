import {
    FiFileText,
    FiLogOut,
    FiMessageSquare,
    FiPlus,
    FiTrash2,
    FiUsers,
} from "react-icons/fi";

import logo from "../assets/ap_logo.png";

import {
    deleteConversation,
} from "../conversations";

import {
    getRoleLabel,
} from "../i18n";

export default function Sidebar({
    currentUser,
    conversations,
    selectedId,
    onSelect,
    onNewChat,
    setPage,
    page,
    t,
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
                    type="button"
                >

                    <FiPlus aria-hidden="true" />

                    <span>
                        {t.sidebar.newConversation}
                    </span>

                </button>

                <div className="sidebar-title">
                    {t.sidebar.navigation}
                </div>

                <button
                    className={
                        page === "chat"
                            ? "nav-item active"
                            : "nav-item"
                    }
                    onClick={() =>
                        setPage("chat")
                    }
                    type="button"
                >

                    <FiMessageSquare aria-hidden="true" />

                    <span>
                        {t.sidebar.chats}
                    </span>

                </button>

                {
                    currentUser?.role === "admin" && (
                        <button
                            className={
                                page === "users"
                                    ? "nav-item active"
                                    : "nav-item"
                            }
                            onClick={() =>
                                setPage("users")
                            }
                            type="button"
                        >

                            <FiUsers aria-hidden="true" />

                            <span>
                                {t.sidebar.users}
                            </span>

                        </button>
                    )
                }

                {
                    currentUser?.role === "admin" && (
                        <button
                            className={
                                page === "documents"
                                    ? "nav-item active"
                                    : "nav-item"
                            }
                            onClick={() =>
                                setPage("documents")
                            }
                            type="button"
                        >

                            <FiFileText aria-hidden="true" />

                            <span>
                                {t.sidebar.documents}
                            </span>

                        </button>
                    )
                }

                <div className="sidebar-title">
                    {t.sidebar.recentConversations}
                </div>

                <div className="conversation-list">

                    {
                        conversations.map(chat => (
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
                                        type="button"
                                        title={
                                            t.sidebar.deleteConversation
                                        }
                                        aria-label={
                                            t.sidebar.deleteConversation
                                        }
                                        onClick={async e => {

                                            e.stopPropagation();

                                            await deleteConversation(
                                                chat.id
                                            );

                                            window.location.reload();

                                        }}
                                    >
                                        <FiTrash2 aria-hidden="true" />
                                    </button>

                                </div>

                            </div>
                        ))
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
                            {
                                currentUser?.role
                                    ? getRoleLabel(currentUser.role, t)
                                    : ""
                            }
                        </div>

                    </div>

                </div>

                <button
                    className="logout-btn"
                    type="button"
                    onClick={() => {

                        localStorage.clear();

                        window.location.reload();

                    }}
                >

                    <FiLogOut aria-hidden="true" />

                    <span>
                        {t.sidebar.logout}
                    </span>

                </button>

            </div>

        </aside>

    );

}
