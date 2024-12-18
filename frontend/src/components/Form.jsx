import React from "react-dom";

export default function Form(props) {
    return (
        <div className="content-forms">
            {
                props.isPDF && 
                <input type="file" id="uploadPDF" name="uploadPDF" accept=".pdf"/>
            }

            {
                !props.isPDF && 
                <textarea type="text" id="uploadText" name="uploadText" placeholder="Enter Textipi"></textarea>
            }
        </div>
    )
}