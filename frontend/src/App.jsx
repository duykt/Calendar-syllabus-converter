import React, { useState } from 'react'
import Header from "./components/Header";
import ToggleButton from "./components/ToggleButton";
import Sidebar from "./components/Sidebar";
import FileUploader from "./components/FileUploader.tsx";

export default function App() {
  const [isPDF, setIsPDF] = useState(true);

  function handleChange() {
    setIsPDF(!isPDF);
  }

  return (
    <div className="container">
        <Header />
        <div className="content">
            <Sidebar />
            <div className="content-main">
                <ToggleButton handleChange={handleChange}/>
                <FileUploader isPDF={isPDF}/>
            </div>
        </div>
    </div>
  )
}
