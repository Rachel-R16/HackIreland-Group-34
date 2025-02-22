import React, { useEffect, useState } from 'react';
import './styles.css';

export default function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('http://localhost:5001/api/test')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => setMessage(data.message))
      .catch(error => {
        console.error('Fetch error:', error);
        setMessage('Error connecting to backend');
      });
  }, []);

  return (
    <div className="app">
      <h1>Hello World!</h1>
      <p>Welcome to our HackIreland project</p>
      <h1>Frontend</h1>
      <p>Backend message: {message}</p>
    </div>
  );
}
