import React from "react-dom";

export default function ToggleButton(props) {
    return (
        <div>
            <input type="checkbox" id="toggle" className="toggleCheckbox" onClick={props.handleChange}>
            </input>
            <label for="toggle" className="toggleContainer">
                <div>PDF</div>
                <div>Text</div>
            </label>
        </div>
    ) 
}
