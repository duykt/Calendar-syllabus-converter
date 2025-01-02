import React, { useState } from 'react';
import axios from 'axios';

export default function FileUploader(props) {
    const [files, setFiles] = useState([]);
    
    const handleFileChange = (e) => {
        setFiles(e.target.files)
    };

    const handleFileUpload = (e) => {
        e.preventDefault();
        const formData = new FormData();
        for (const file of files) {
            formData.append("files", file);
        }
        axios.post('http://127.0.0.1:5000/files', formData, {
            headers: {
                'Content-Type': "multipart/form-data",
            },
        })
    };
    
    return (
        <div className="content-forms">
            {props.isPDF ? (
                <input
                    id="uploadPDF"
                    name="uploadPDF"
                    type="file"
                    multiple
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

            {files &&
                <button 
                    className="upload-button"
                    onClick={handleFileUpload}
                    >Upload
                </button>
            }
        </div>
    )
}