const API =
    "http://localhost:8000";

export async function login(
    username,
    password,
) {

    const response =
        await fetch(
            `${API}/auth/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify({
                    username,
                    password,
                }),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {

        throw new Error();

    }
    return data;

}