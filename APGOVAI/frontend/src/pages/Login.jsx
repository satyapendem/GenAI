import { useState } from "react";

import { login } from "../auth";
import LanguageToggle from "../components/LanguageToggle";

import logo from "../assets/ap_logo.png";
import cm from "../assets/cm.png";
import deputy from "../assets/deputy_cm.png";
import minister from "../assets/it_minister.png";

export default function Login({
    onLogin,
    language,
    onLanguageChange,
    languageOptions,
    t,
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
                t.login.invalidCredentials
            );

        }

    }

    return (

        <div
            className="login-layout"
            lang={language}
        >

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
                                {t.app.subtitle}
                            </p>

                        </div>

                    </div>

                    <div className="login-side">

                        <LanguageToggle
                            language={language}
                            onChange={onLanguageChange}
                            label={t.common.language}
                            compact
                            options={languageOptions}
                        />

                        <div className="login-leaders">

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

                </div>

                <form
                    onSubmit={submit}
                    className="login-form"
                >

                    <h2>
                        {t.login.signIn}
                    </h2>

                    <input
                        placeholder={t.login.username}
                        value={username}
                        onChange={(e) =>
                            setUsername(
                                e.target.value
                            )
                        }
                    />

                    <input
                        type="password"
                        placeholder={t.login.password}
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

                    <button type="submit">
                        {t.login.login}
                    </button>

                </form>

            </div>

        </div>

    );

}
