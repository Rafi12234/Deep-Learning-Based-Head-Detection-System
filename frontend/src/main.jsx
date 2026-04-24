import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';
import { DetectionProvider } from './context/DetectionContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <DetectionProvider>
        <App />
      </DetectionProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
