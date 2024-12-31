import React, { ChangeEvent, useState } from 'react';
import axios from 'axios';

type UploadStatus = "idle" | "uploading" | "success" | "error";

export default function FileUploader(props) {
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<UploadStatus>("idle")    

    function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    }

    async function handleFileUpload() {
        if (!file) return;

        setStatus("uploading");

        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post("https://httpbin.org/post", formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            })

            setStatus("success");
        } catch {
            setStatus("error")
        };
    }
    
    return (
        <div className="content-forms">
            {props.isPDF ? (
                <input
                    type="file"
                    id="uploadPDF"
                    name="uploadPDF"
                    accept=".pdf"
                    onChange={handleFileChange}
                />
            ) : (
                <textarea
                    // type="text"
                    id="uploadText"
                    name="uploadText"
                    placeholder="Enter Text"
                />
            )}
            {file && (
                <div>
                    <p>File name: {file.name}</p>
                    <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p>Type: {file.type}</p>
                </div>
            )}
            {file && status !== "uploading" && 
                <button 
                    className="upload-button"
                    onClick={handleFileUpload}
                    >Upload
                </button>
            }
        </div>
    )
}