import React from "react";

export default function Sidebar(props) {
    const getFileIcon = (type) => {
        switch (type) {
            case "pdf":
                return "/pdf.png"
            case "txt":
                return "/txt.png"
        }
    }
    console.log(props.files)
    return (
        <div className="sidebar">
            {props.files.map((file, index) => (
                <div key={index}>
                    <img
                        src={getFileIcon(file.type)}
                        alt={file.type}
                        className="file-icon"
                    />
                    <p>{file.name}</p>
                </div>
            ))}
        </div>
    )
}
