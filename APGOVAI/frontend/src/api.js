export async function sendMessage(
  question,
  onChunk,
) {

  const response =
    await fetch(

      "http://localhost:8000/chat",

      {

        method: "POST",

        headers: {

          "Content-Type":
            "application/json",

        },

        body: JSON.stringify({

          question,

        }),

      },

    )

  if (!response.ok) {

    throw new Error(
      "API Error"
    )

  }

  if (!response.body) {

    throw new Error(
      "No response body"
    )

  }

  const reader =
    response.body.getReader()

  const decoder =
    new TextDecoder()

  while (true) {

    const {

      done,

      value,

    } = await reader.read()

    if (done) {

      break

    }

    const chunk =
      decoder.decode(

        value,

        {

          stream: true,

        }

      )

    if (chunk) {

      onChunk(
        chunk
      )

    }

  }

}