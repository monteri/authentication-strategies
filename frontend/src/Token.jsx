import { useState } from "react";

const Token = () => {
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const login = async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Make a POST request to the server to get the JWT token
    try {
      const response = await fetch('http://localhost:8000/api/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.status !== 200) {
        setError(`Login error: ${data.error}`)
      } else {
        setError('')
      }
      // Save the token to localStorage
      localStorage.setItem('jwtToken', data.token);
      setToken(data.token);
    } catch (error) {
      setError(`Login error: ${error}`)
      console.error('Login error:', error);
    }
  };

  // Function to handle data access
  const accessData = async () => {
    const token = localStorage.getItem('jwtToken');

    try {
      const response = await fetch('http://localhost:8000/api/data-access/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setData(data);
    } catch (error) {
      setError(`Data access error: ${error}`)
      console.error('Data access error:', error);
    }
  };

  // Function to handle logout
  const logout = () => {
    localStorage.removeItem('jwtToken');
    setToken(null);
    setData(null);
  };

  return (
    <div>
      <div>
        <h1>JWT Authentication Demo</h1>
        <div>
          <h2>Login</h2>
          <input type="text" id="username" placeholder="Username" />
          <input type="password" id="password" placeholder="Password" />
          <button onClick={login}>Login</button>
          {error && <p>{error}</p>}
        </div>
        <div>
          Token: {token}
        </div>
        <div>
          <h2>Data Access</h2>
          <button onClick={accessData}>Access Data</button>
          {data && <div>{JSON.stringify(data)}</div>}
        </div>
        <div>
          <button onClick={logout}>Logout</button>
        </div>
      </div>
    </div>
  );
}

export default Token;