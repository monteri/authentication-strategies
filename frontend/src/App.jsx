import { useState } from 'react';
import Token from "./Token";
import AuthZero from "./AuthZero";
import TwoFA from "./TwoFA";

import './App.css';

function App() {
  const [tab, setTab] = useState('auth0')

  return (
    <div>
      <button onClick={() => setTab('auth0')}>Auth0</button>
      <button onClick={() => setTab('token')}>Token Based</button>
      <button onClick={() => setTab('2fa')}>2FA</button>
      {tab === 'auth0' && <AuthZero />}
      {tab === 'token' && <Token />}
      {tab === '2fa' && <TwoFA />}
    </div>
  )
}

export default App;
