import React, { useState } from 'react';
import { Activity, AlertCircle, Loader } from 'lucide-react';
import { loginUser, registerUser } from '../services/api';

// Mode: 'login' | 'signup'
export function AuthView({ initialMode = 'login', onLoginSuccess, onBackToHome }) {
  const [mode, setMode] = useState(initialMode);

  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // Sign up form state
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupConfirm, setSignupConfirm] = useState('');
  const [signupError, setSignupError] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);

  // ─── Login Handler ────────────────────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setLoginLoading(true);
    try {
      const user = await loginUser(loginEmail.trim(), loginPassword);
      // Persist session to localStorage
      localStorage.setItem('med_user', JSON.stringify(user));
      onLoginSuccess(user);
    } catch (err) {
      const msg = err.message || 'Login failed';
      if (msg.toLowerCase().includes('not found') || msg.toLowerCase().includes('sign up')) {
        setLoginError("No account found with this email. Please Sign Up first.");
      } else if (msg.toLowerCase().includes('password') || msg.toLowerCase().includes('incorrect')) {
        setLoginError("Incorrect password. Please try again.");
      } else {
        setLoginError(msg);
      }
    } finally {
      setLoginLoading(false);
    }
  };

  // ─── Sign Up Handler ──────────────────────────────────────────────────────────
  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupError('');

    if (signupPassword !== signupConfirm) {
      setSignupError("Passwords do not match.");
      return;
    }
    if (signupPassword.length < 6) {
      setSignupError("Password must be at least 6 characters.");
      return;
    }

    setSignupLoading(true);
    try {
      const user = await registerUser(signupName.trim(), signupEmail.trim(), signupPassword);
      // Auto login after registration
      localStorage.setItem('med_user', JSON.stringify(user));
      onLoginSuccess(user);
    } catch (err) {
      const msg = err.message || 'Registration failed';
      if (msg.toLowerCase().includes('already exists') || msg.toLowerCase().includes('log in')) {
        setSignupError("An account with this email already exists. Please Log In.");
      } else {
        setSignupError(msg);
      }
    } finally {
      setSignupLoading(false);
    }
  };

  const sharedPageWrap = {
    backgroundColor: '#f8fafc',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '32px',
  };

  const cardStyle = {
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    border: '1px solid #e2e8f0',
    boxShadow: '0 4px 24px -6px rgba(37, 99, 235, 0.10)',
    padding: '40px 36px',
    width: '100%',
    maxWidth: '420px',
  };

  const inputStyle = {
    width: '100%',
    padding: '11px 14px',
    borderRadius: '8px',
    border: '1px solid #cbd5e1',
    fontSize: '0.92rem',
    outline: 'none',
    boxSizing: 'border-box',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.85rem',
    fontWeight: '600',
    color: '#334155',
    marginBottom: '6px',
  };

  // ─── Logo Header ──────────────────────────────────────────────────────────────
  const Logo = () => (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', marginBottom: '28px', cursor: 'pointer' }} onClick={onBackToHome}>
      <div style={{ width: '44px', height: '44px', backgroundColor: '#2563eb', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
        <Activity size={26} />
      </div>
      <span style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>AI Medical Report Assistant</span>
    </div>
  );

  // ─── LOGIN PAGE ───────────────────────────────────────────────────────────────
  if (mode === 'login') {
    return (
      <div style={sharedPageWrap}>
        <Logo />
        <div style={cardStyle}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>Welcome Back</h1>
          <p style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: '24px' }}>Sign in to your account to continue</p>

          {loginError && (
            <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '8px', padding: '10px 14px', marginBottom: '16px', display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
              <AlertCircle size={16} color="#dc2626" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <span style={{ fontSize: '0.85rem', color: '#dc2626' }}>{loginError}</span>
                {loginError.includes('Sign Up') && (
                  <span
                    style={{ display: 'block', marginTop: '4px', fontSize: '0.82rem', color: '#2563eb', fontWeight: '600', cursor: 'pointer' }}
                    onClick={() => { setLoginError(''); setMode('signup'); }}
                  >
                    → Create Account
                  </span>
                )}
              </div>
            </div>
          )}

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={labelStyle}>Email</label>
              <input
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder="your@email.com"
                style={inputStyle}
                required
                autoFocus
              />
            </div>

            <div>
              <label style={labelStyle}>Password</label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="Enter password"
                style={inputStyle}
                required
              />
              <div style={{ textAlign: 'right', marginTop: '6px' }}>
                <span style={{ fontSize: '0.8rem', color: '#2563eb', cursor: 'pointer' }}>Forgot Password?</span>
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '12px', marginTop: '4px', fontSize: '0.95rem' }}
              disabled={loginLoading}
            >
              {loginLoading ? <><Loader size={16} className="spin-icon" /> Signing in...</> : 'Login'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.88rem', color: '#64748b' }}>
            New user?{' '}
            <span
              style={{ color: '#2563eb', fontWeight: '600', cursor: 'pointer' }}
              onClick={() => { setLoginError(''); setMode('signup'); }}
            >
              Create Account
            </span>
          </div>
        </div>
      </div>
    );
  }

  // ─── SIGN UP PAGE ─────────────────────────────────────────────────────────────
  return (
    <div style={sharedPageWrap}>
      <Logo />
      <div style={cardStyle}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>Create Account</h1>
        <p style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: '24px' }}>Start managing your family's health records</p>

        {signupError && (
          <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '8px', padding: '10px 14px', marginBottom: '16px', display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
            <AlertCircle size={16} color="#dc2626" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <span style={{ fontSize: '0.85rem', color: '#dc2626' }}>{signupError}</span>
              {signupError.includes('Log In') && (
                <span
                  style={{ display: 'block', marginTop: '4px', fontSize: '0.82rem', color: '#2563eb', fontWeight: '600', cursor: 'pointer' }}
                  onClick={() => { setSignupError(''); setMode('login'); }}
                >
                  → Go to Login
                </span>
              )}
            </div>
          </div>
        )}

        <form onSubmit={handleSignup} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={labelStyle}>Full Name</label>
            <input
              type="text"
              value={signupName}
              onChange={(e) => setSignupName(e.target.value)}
              placeholder="Your full name"
              style={inputStyle}
              required
              autoFocus
            />
          </div>

          <div>
            <label style={labelStyle}>Email</label>
            <input
              type="email"
              value={signupEmail}
              onChange={(e) => setSignupEmail(e.target.value)}
              placeholder="your@email.com"
              style={inputStyle}
              required
            />
          </div>

          <div>
            <label style={labelStyle}>Password</label>
            <input
              type="password"
              value={signupPassword}
              onChange={(e) => setSignupPassword(e.target.value)}
              placeholder="At least 6 characters"
              style={inputStyle}
              required
            />
          </div>

          <div>
            <label style={labelStyle}>Confirm Password</label>
            <input
              type="password"
              value={signupConfirm}
              onChange={(e) => setSignupConfirm(e.target.value)}
              placeholder="Repeat password"
              style={inputStyle}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '12px', marginTop: '4px', fontSize: '0.95rem' }}
            disabled={signupLoading}
          >
            {signupLoading ? <><Loader size={16} className="spin-icon" /> Creating account...</> : 'Sign Up'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.88rem', color: '#64748b' }}>
          Already have an account?{' '}
          <span
            style={{ color: '#2563eb', fontWeight: '600', cursor: 'pointer' }}
            onClick={() => { setSignupError(''); setMode('login'); }}
          >
            Login
          </span>
        </div>
      </div>
    </div>
  );
}

export default AuthView;
