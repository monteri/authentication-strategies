import { useAuth0 } from "@auth0/auth0-react";

const AuthZero = () => {
  const { user, loginWithPopup, logout, isAuthenticated, isLoading, getIdTokenClaims } = useAuth0();

  const getToken = async () => {
    const res = await getIdTokenClaims()
    console.log(res)
  }

  const handleLogin = async () => {
    try {
      await loginWithPopup();
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  const handleLogout = () => {
    logout();
  };

  getToken().then(r => {
    console.log(r)
  })

  return (
    <div>
      <h1>Auth0 Demo</h1>
      {isLoading ? (
        <div>Loading...</div>
      ) : isAuthenticated ? (
        <>
          <h3>Welcome, {user.nickname}!</h3>
          <button onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <button onClick={handleLogin}>Login with Auth0</button>
      )}
    </div>
  );
};

export default AuthZero;