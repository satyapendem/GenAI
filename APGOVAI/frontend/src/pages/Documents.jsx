import {
    useEffect,
    useState,
} from "react";

import {

    getDocuments,

    uploadDocument,

    deleteDocument,

} from "../documents";

export default function Documents({setPage}) {

    const [
        documents,
        setDocuments,
    ] = useState([]);

    const [
        file,
        setFile,
    ] = useState(null);

    const [
        collection,
        setCollection,
    ] = useState("gos");

    async function loadDocuments() {

        const data =
            await getDocuments();

        setDocuments(data);

    }

    useEffect(() => {

        loadDocuments();

    }, []);

    async function upload() {

        if (!file) return;

        await uploadDocument(

            file,

            collection,

        );

        setFile(null);

        loadDocuments();

    }

    return (

        <div className="documents-page">
            <button
                className="back-btn"
                onClick={() =>
                    setPage("chat")
                }
            >
                ← Back
            </button>
            <h2>
                Document Management
            </h2>

            <div className="upload-card">

                <select

                    value={collection}

                    onChange={e =>
                        setCollection(
                            e.target.value
                        )
                    }

                >

                    <option value="gos">
                        Government Orders
                    </option>

                    <option value="budgets">
                        Budgets
                    </option>

                    <option value="reports">
                        Reports
                    </option>

                    <option value="datasets">
                        Datasets
                    </option>

                </select>

                <input

                    type="file"

                    onChange={e =>
                        setFile(
                            e.target.files[0]
                        )
                    }

                />

                <button
                    onClick={upload}
                >

                    Upload

                </button>

            </div>

            <table>

                <thead>

                    <tr>

                        <th>File</th>

                        <th>Collection</th>

                        <th>Status</th>

                        <th>Action</th>

                    </tr>

                </thead>

                <tbody>

                    {

                        documents.map(
                            doc => (

                                <tr
                                    key={doc.id}
                                >

                                    <td>
                                        {doc.filename}
                                    </td>

                                    <td>
                                        {doc.collection}
                                    </td>

                                    <td>
                                        {doc.status}
                                    </td>

                                    <td>

                                        <button

                                            onClick={async () => {

                                                await deleteDocument(
                                                    doc.id
                                                );

                                                loadDocuments();

                                            }}

                                        >

                                            Delete

                                        </button>

                                    </td>

                                </tr>

                            )
                        )

                    }

                </tbody>

            </table>

        </div>

    );

}