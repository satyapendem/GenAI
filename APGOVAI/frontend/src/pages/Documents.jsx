import {
    useEffect,
    useState,
} from "react";

import {
    FiChevronLeft,
    FiTrash2,
    FiUpload,
} from "react-icons/fi";

import {
    getDocuments,
    uploadDocument,
    deleteDocument,
} from "../documents";

import LanguageToggle from "../components/LanguageToggle";

export default function Documents({
    setPage,
    language,
    onLanguageChange,
    languageOptions,
    t,
}) {

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

    const collectionLabels = {
        gos: t.documents.governmentOrders,
        budgets: t.documents.budgets,
        reports: t.documents.reports,
        datasets: t.documents.datasets,
    };

    const statusLabels = {
        completed: t.documents.completed,
        processing: t.documents.processing,
        failed: t.documents.failed,
    };

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

        <div
            className="documents-page"
            lang={language}
        >

            <div className="page-header">

                <div className="page-actions">

                    <button
                        className="back-btn"
                        onClick={() =>
                            setPage("chat")
                        }
                        type="button"
                    >
                        <FiChevronLeft aria-hidden="true" />

                        <span>
                            {t.common.back}
                        </span>
                    </button>

                    <LanguageToggle
                        language={language}
                        onChange={onLanguageChange}
                        label={t.common.language}
                        compact
                        options={languageOptions}
                    />

                </div>

                <h2>
                    {t.documents.title}
                </h2>

            </div>

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
                        {t.documents.governmentOrders}
                    </option>

                    <option value="budgets">
                        {t.documents.budgets}
                    </option>

                    <option value="reports">
                        {t.documents.reports}
                    </option>

                    <option value="datasets">
                        {t.documents.datasets}
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
                    type="button"
                >

                    <FiUpload aria-hidden="true" />

                    <span>
                        {t.common.upload}
                    </span>

                </button>

            </div>

            <div className="documents-table-card">

                <table className="documents-table">

                    <thead>

                        <tr>

                            <th>{t.documents.file}</th>

                            <th>{t.documents.collection}</th>

                            <th>{t.documents.status}</th>

                            <th>{t.documents.action}</th>

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
                                            {
                                                collectionLabels[
                                                doc.collection
                                                ] || doc.collection
                                            }
                                        </td>

                                        <td>
                                            <span
                                                className={
                                                    `status ${doc.status}`
                                                }
                                            >
                                                {
                                                    statusLabels[
                                                    doc.status
                                                    ] || doc.status
                                                }
                                            </span>
                                        </td>

                                        <td>

                                            <button
                                                className="action-btn delete"
                                                type="button"
                                                onClick={async () => {

                                                    await deleteDocument(
                                                        doc.id
                                                    );

                                                    loadDocuments();

                                                }}
                                            >
                                                <FiTrash2 aria-hidden="true" />

                                                <span>
                                                    {t.common.delete}
                                                </span>
                                            </button>

                                        </td>

                                    </tr>

                                )
                            )
                        }

                    </tbody>

                </table>

            </div>

        </div>

    );

}
