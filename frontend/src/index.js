import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Leave this as is

// Removed index.css since it doesn't exist
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
