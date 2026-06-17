import {
    useEffect,
    useState,
} from "react";

import {
    FiChevronLeft,
    FiUserPlus,
} from "react-icons/fi";

import {
    getUsers,
    createUser,
} from "../admin";

import LanguageToggle from "../components/LanguageToggle";

import {
    getRoleLabel,
} from "../i18n";

export default function Users({
    setPage,
    language,
    onLanguageChange,
    languageOptions,
    t,
}) {

    const [
        users,
        setUsers,
    ] = useState([]);

    const [
        username,
        setUsername,
    ] = useState("");

    const [
        password,
        setPassword,
    ] = useState("");

    const [
        role,
        setRole,
    ] = useState("user");

    async function loadUsers() {

        const data =
            await getUsers();

        setUsers(data);

    }

    useEffect(() => {

        loadUsers();

    }, []);

    async function handleCreate() {

        if (
            !username ||
            !password
        ) {
            return;
        }

        await createUser(
            username,
            password,
            role,
        );

        setUsername("");
        setPassword("");
        setRole("user");

        loadUsers();

    }

    return (

        <div
            className="users-page"
            lang={language}
        >

            <div className="page-header">

                <div className="page-actions">

                    <button
                        className="back-btn"
                        onClick={() =>
                            setPage("chat")
                        }
                        type="button"
                    >
                        <FiChevronLeft aria-hidden="true" />

                        <span>
                            {t.common.back}
                        </span>
                    </button>

                    <LanguageToggle
                        language={language}
                        onChange={onLanguageChange}
                        label={t.common.language}
                        compact
                        options={languageOptions}
                    />

                </div>

                <h2>
                    {t.users.title}
                </h2>

            </div>

            <div className="create-user-card">

                <h3>
                    {t.users.createUser}
                </h3>

                <input
                    placeholder={t.users.username}
                    value={username}
                    onChange={e =>
                        setUsername(
                            e.target.value
                        )
                    }
                />

                <input
                    type="password"
                    placeholder={t.users.password}
                    value={password}
                    onChange={e =>
                        setPassword(
                            e.target.value
                        )
                    }
                />

                <select
                    value={role}
                    onChange={e =>
                        setRole(
                            e.target.value
                        )
                    }
                >

                    <option value="user">
                        {t.users.user}
                    </option>

                    <option value="admin">
                        {t.users.admin}
                    </option>

                </select>

                <button
                    onClick={handleCreate}
                    type="button"
                >
                    <FiUserPlus aria-hidden="true" />

                    <span>
                        {t.users.createUser}
                    </span>
                </button>

            </div>

            <div className="users-table-card">

                <table>

                    <thead>

                        <tr>

                            <th>
                                {t.users.username}
                            </th>

                            <th>
                                {t.users.role}
                            </th>

                            <th>
                                {t.users.status}
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {users.map(user => (

                            <tr key={user.id}>

                                <td>
                                    {user.username}
                                </td>

                                <td>
                                    {getRoleLabel(user.role, t)}
                                </td>

                                <td>

                                    {
                                        user.is_active
                                            ? t.users.active
                                            : t.users.disabled
                                    }

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>

    );

}
