import { useState } from "react";

import { login } from "../auth";

import logo from "../assets/ap_logo.png";
import cm from "../assets/cm.png";
import deputy from "../assets/deputy_cm.png";
import minister from "../assets/it_minister.png";

export default function Login({
    onLogin,
}) {

    const [username, setUsername] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [error, setError] =
        useState("");

    async function submit(e) {

        e.preventDefault();

        try {

            const data =
                await login(
                    username,
                    password,
                );

            localStorage.setItem(
                "token",
                data.access_token,
            );

            localStorage.setItem(
                "role",
                data.role,
            );

            onLogin(
                data.access_token
            );

        } catch {

            setError(
                "Invalid credentials"
            );

        }

    }

    return (

        <div className="login-layout">

            <div className="login-card">
                <div className="login-top">

                    <div className="login-brand">

                        <img
                            src={logo}
                            alt="AP Government"
                            className="login-logo"
                        />

                        <div>

                            <h1>APGovAI</h1>

                            <p>
                                AI Assistant for Andhra Pradesh Government
                            </p>

                        </div>

                    </div>

                    <div className="login-leaders">

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

                </div>

                <form
                    onSubmit={submit}
                    className="login-form"
                >

                    <h2>
                        Sign In
                    </h2>

                    <input
                        placeholder="Username"
                        value={username}
                        onChange={(e) =>
                            setUsername(
                                e.target.value
                            )
                        }
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) =>
                            setPassword(
                                e.target.value
                            )
                        }
                    />

                    {error && (
                        <p className="login-error">
                            {error}
                        </p>
                    )}

                    <button>
                        Login
                    </button>

                </form>

            </div>

        </div>

    );

}