import React from 'react'
import ReactDOM from 'react-dom/client'
// IMPORTANT: CoreUI CSS must be imported here
import '@coreui/coreui/dist/css/coreui.min.css' 
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)