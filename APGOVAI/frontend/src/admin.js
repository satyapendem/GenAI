const API =
  "http://localhost:8000";

function authHeaders() {

  return {

    Authorization:
      `Bearer ${
        localStorage.getItem(
          "token"
        )
      }`,

    "Content-Type":
      "application/json",

  };

}

export async function getUsers() {

  const response =
    await fetch(

      `${API}/admin/users`,

      {
        headers:
          authHeaders(),
      }

    );

  return response.json();

}

export async function createUser(
  username,
  password,
  role,
) {

  const response =
    await fetch(

      `${API}/admin/users`,

      {

        method: "POST",

        headers:
          authHeaders(),

        body: JSON.stringify({

          username,
          password,
          role,

        }),

      }

    );

  return response.json();

}