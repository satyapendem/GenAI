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

export async function createConversation() {

  const response =
    await fetch(
      `${API}/conversations`,
      {
        method: "POST",
        headers:
          authHeaders(),
      }
    );

  return response.json();

}

export async function getConversations() {

  const response =
    await fetch(
      `${API}/conversations`,
      {
        headers:
          authHeaders(),
      }
    );

  return response.json();

}

export async function getMessages(
  conversationId
) {

  const response =
    await fetch(
      `${API}/conversations/${conversationId}/messages`,
      {
        headers:
          authHeaders(),
      }
    );

  return response.json();

}

export async function deleteConversation(
  conversationId
) {

  const response =
    await fetch(

      `${API}/conversations/${conversationId}`,

      {

        method: "DELETE",

        headers:
          authHeaders(),

      }

    );

  return response.json();

}