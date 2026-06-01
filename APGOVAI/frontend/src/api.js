const API =
  "http://localhost:8000";

export async function sendMessage(
  conversationId,
  question,
  onChunk,
) {

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

        }),

      }
    );

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