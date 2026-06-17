const API =
  "http://localhost:8000";

export async function getChatLanguages() {
  const response = await fetch(`${API}/chat/languages`);

  if (!response.ok) {
    throw new Error("Failed to load chat languages");
  }

  return response.json();
}

export async function sendMessage(
  conversationId,
  question,
  language,
  onChunk,
) {

  const requestedLanguage =
    language || "auto";

  const response =
    await fetch(
      `${API}/chat`,
      {
        method: "POST",

        headers: {

          Authorization:
            `Bearer ${
              localStorage.getItem(
                "token"
              )
            }`,

          "Content-Type":
            "application/json",

        },

        body: JSON.stringify({

          conversation_id:
            conversationId,

          question,

          language:
            requestedLanguage,

        }),

      }
    );

  if (!response.ok) {

    const message =
      await response.text();

    throw new Error(
      message || "Chat request failed"
    );

  }

  if (!response.body) {

    throw new Error(
      "No response"
    );

  }

  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();

  while (true) {

    const {
      done,
      value,
    } = await reader.read();

    if (done) {

      break;

    }

    const chunk =
      decoder.decode(
        value,
        {
          stream: true,
        }
      );

    onChunk(chunk);

  }

}
