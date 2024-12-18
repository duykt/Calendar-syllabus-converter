import React, { useState, useEffect } from 'react'
import Header from "./components/Header";
import ToggleButton from "./components/ToggleButton";
import Sidebar from "./components/Sidebar";
import Form from "./components/Form";

export default function App() {
  const [data, setData] = useState([{}])
  const [isPDF, setIsPDF] = useState(true);

  useEffect(() => {
      fetch("/members").then(
          res => res.json()
      ).then(
          data => {
              setData(data)
              console.log(data)
          }
      )
  }, [])

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
                <Form isPDF={isPDF}/>
            </div>
        </div>
    </div>
  )
}
