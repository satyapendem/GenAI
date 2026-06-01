import {
    useEffect,
    useState,
} from "react";

import {
    getUsers,
    createUser,
} from "../admin";

export default function Users({setPage}) {

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

        <div className="users-page">

            <div className="page-header">
                <button
                    className="back-btn"
                    onClick={() =>
                        setPage("chat")
                    }
                >
                    ← Back
                </button>
                <h2>
                    User Management
                </h2>

            </div>

            <div className="create-user-card">

                <h3>
                    Create User
                </h3>

                <input
                    placeholder="Username"
                    value={username}
                    onChange={e =>
                        setUsername(
                            e.target.value
                        )
                    }
                />

                <input
                    type="password"
                    placeholder="Password"
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
                        User
                    </option>

                    <option value="admin">
                        Admin
                    </option>

                </select>

                <button
                    onClick={handleCreate}
                >
                    Create User
                </button>

            </div>

            <div className="users-table-card">

                <table>

                    <thead>

                        <tr>

                            <th>
                                Username
                            </th>

                            <th>
                                Role
                            </th>

                            <th>
                                Status
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
                                    {user.role}
                                </td>

                                <td>

                                    {
                                        user.is_active
                                            ? "Active"
                                            : "Disabled"
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