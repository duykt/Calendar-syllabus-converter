import React from "react-dom";

export default function Header() {
    return (
        <header className="header">
            <img src={"/logo.png"} id="logo" alt="logo"/>
            <div className="header-content">
                <h1>Convert Syllabus to Calendar</h1>
            </div>   
        </header>
    )
}
