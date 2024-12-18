import React from "react-dom";
import logo from "./icon.jpg"

export default function Header() {
    return (
        <header className="header">
            <img src={logo} id="logo" alt="logo"/>
            <div className="header-content">
                <h1>Convert Syllabus to Calendar</h1>
            </div>   
        </header>
    )
}
