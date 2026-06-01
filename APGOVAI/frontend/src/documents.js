const API =
  "http://localhost:8000";

function headers() {

  return {

    Authorization:
      `Bearer ${
        localStorage.getItem(
          "token"
        )
      }`

  };

}

export async function getDocuments() {

  const response =
    await fetch(

      `${API}/documents`,

      {
        headers:
          headers(),
      }

    );

  return response.json();

}

export async function uploadDocument(
  file,
  collection,
) {

  const form =
    new FormData();

  form.append(
    "file",
    file
  );

  const response =
    await fetch(

      `${API}/documents/upload?collection=${collection}`,

      {

        method: "POST",

        headers:
          headers(),

        body: form,

      }

    );

  return response.json();

}

export async function deleteDocument(
  id,
) {

  const response =
    await fetch(

      `${API}/documents/${id}`,

      {

        method: "DELETE",

        headers:
          headers(),

      }

    );

  return response.json();

}