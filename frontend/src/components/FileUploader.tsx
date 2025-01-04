import React, { useState } from 'react';
import axios from 'axios';

export default function FileUploader(props) {
    const [files, setFiles] = useState([]);
    const [text, setText] = useState(String);
    const [title, setTitle] = useState(String)
    
    const handleFileChange = (e) => {
        setFiles(e.target.files)
    };

    const handleTextChange = (e) => {
        setText(e.target.value);
    }

    const handleTitleChange = (e) => {
        setTitle(e.target.value);
    }

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

    const handleTextUpload = () => {
        const data = {title, text};
        axios.post('http://127.0.0.1:5000/text', data)

        setTitle('')
        setText('')
    }

    const handleFileDownload = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/download', {
              responseType: 'blob', // Important for handling binary data
            });
      
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
      
            link.setAttribute('download', 'output.xlsx'); 
            document.body.appendChild(link);
            link.click();

            link.remove();
            window.URL.revokeObjectURL(url);
          } catch (error) {
            console.error('Error downloading the file:', error);
          }
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
                <div>
                    <textarea
                        id="uploadTitle"
                        name='uploadTitle'
                        placeholder='Enter Title'
                        value={title}
                        onChange={handleTitleChange}
                    />
                    <textarea
                        // type="text"
                        id="uploadText"
                        name="uploadText"
                        placeholder="Enter Text"
                        value={text}
                        onChange={handleTextChange}
                    />
                </div>
            )}

            {files &&
                <button 
                    className="upload-button"
                    onClick={props.isPDF ? handleFileUpload : handleTextUpload}
                    >Upload
                </button>
            }

            <button
                className='file-download-button'
                onClick={handleFileDownload}
            >
                Generate File
            </button>
        </div>
    )
}