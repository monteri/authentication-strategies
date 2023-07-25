import { useState } from "react";
import axios from "axios";

const TwoFA = () => {
  const [screen, setScreen] = useState(0)
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState('')
  const [userId, setUserId] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/api/login_2fa/", {
        username,
        password,
      });
     if (response.status === 200) {
        setScreen(1)
        setUserId(response.data.user_id)
        setError('')
      } else {
        setError(response.data.error)
      }
    } catch (error) {
      setError(error.response.data.error)
      console.error("Login error:", error);
    }
  };

  const handleSetup = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/api/setup_2fa/", {
        phone,
        user_id: userId,
      });
      if (response.status === 200) {
        setScreen(2)
        setError('')
      } else {
        setError(response.data.error)
      }
    } catch (error) {
      setError(error.response.data.error)
      console.error("2FA setup error:", error);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/api/verify_2fa/", {
        user_id: userId,
        code,
      });
      if (response.status === 200) {
        setScreen(3)
        setError('')
      } else {
        setError(response.data.error)
      }
    } catch (error) {
      setError(error.response.data.error)
      console.error("2FA verification error:", error);
    }
  };

  return (
    <div>
      {screen === 0 && (
        <>
          <h2>Login</h2>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Login</button>
            {error && <div>{error}</div>}
          </form>
        </>
      )}
      {screen === 1 && (
        <>
          <h2>Two-Factor Authentication Setup</h2>
          <form onSubmit={handleSetup}>
            <input
              type="text"
              placeholder="Phone Number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <button type="submit">Setup 2FA</button>
            {error && <div>{error}</div>}
          </form>
        </>
      )}
      {screen === 2 && (
        <>
          <h2>Two-Factor Authentication Verification</h2>
          <form onSubmit={handleVerify}>
            <input
              type="text"
              placeholder="Verification Code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <button type="submit">Verify</button>
            {error && <div>{error}</div>}
          </form>
        </>
      )}
      {screen === 3 && (
        <>
          <h3>Successful login</h3>
          <button onClick={() => setScreen(0)}>Reset</button>
        </>
      )}
    </div>
  );
};

export default TwoFA;