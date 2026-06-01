const API =
  "http://localhost:8000";

export async function getCurrentUser() {

  const response =
    await fetch(
      `${API}/users/me`,
      {

        headers: {

          Authorization:
            `Bearer ${
              localStorage.getItem(
                "token"
              )
            }`

        }

      }
    );

  return response.json();

}