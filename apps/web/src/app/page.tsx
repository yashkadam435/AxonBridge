'use client';

import React, { useState, useEffect } from 'react';

/* ================================================================
   AxonBridge — Landing / Login Page
   Premium enterprise login with animated gradient background
   ================================================================ */

export default function Home() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [showMFA, setShowMFA] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, mfa_code: mfaCode || undefined }),
      });

      const data = await res.json();

      if (!res.ok) {
        if (data.error_code === 'MFA_REQUIRED') {
          setShowMFA(true);
          setIsLoading(false);
          return;
        }
        throw new Error(data.message || 'Login failed');
      }

      // Store tokens
      localStorage.setItem('axb_access_token', data.access_token);
      localStorage.setItem('axb_refresh_token', data.refresh_token);

      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Animated gradient background */}
      <div style={styles.gradientBg} />
      
      {/* Floating orbs */}
      <div style={{ ...styles.orb, ...styles.orb1 }} />
      <div style={{ ...styles.orb, ...styles.orb2 }} />
      <div style={{ ...styles.orb, ...styles.orb3 }} />

      {/* Grid pattern overlay */}
      <div style={styles.gridPattern} />

      {/* Main content */}
      <div style={{
        ...styles.content,
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(20px)',
      }}>
        {/* Left side — branding */}
        <div style={styles.brandingSide}>
          <div style={styles.logoContainer}>
            <div style={styles.logoIcon}>
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="12" fill="url(#logoGrad)" />
                <path d="M14 24L22 16L30 24L22 32Z" fill="white" opacity="0.9" />
                <path d="M22 16L34 24L22 32" stroke="white" strokeWidth="2" fill="none" opacity="0.6" />
                <defs>
                  <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">
                    <stop stopColor="#3B82F6" />
                    <stop offset="1" stopColor="#06B6D4" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div>
              <h1 style={styles.logoText}>AxonBridge</h1>
              <p style={styles.logoSubtext}>Healthcare Automation Platform</p>
            </div>
          </div>

          <div style={styles.brandingContent}>
            <h2 style={styles.brandingTitle}>
              Universal Agentic<br />
              <span style={styles.gradientText}>Automation Layer</span>
            </h2>
            <p style={styles.brandingDescription}>
              AI-powered middleware that operates on top of any existing HIS/EHR system — 
              without requiring API access, vendor cooperation, or system replacement.
            </p>

            <div style={styles.featureList}>
              {[
                { icon: '🔒', text: 'HIPAA Compliant & Data Sovereign' },
                { icon: '🤖', text: 'Vision-Based Browser Automation' },
                { icon: '🌐', text: '30+ Languages at Launch' },
                { icon: '👨‍⚕️', text: 'Human-in-the-Loop Safety' },
              ].map((feature, i) => (
                <div key={i} style={{
                  ...styles.featureItem,
                  animationDelay: `${(i + 1) * 100}ms`,
                }}>
                  <span style={styles.featureIcon}>{feature.icon}</span>
                  <span style={styles.featureText}>{feature.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right side — login form */}
        <div style={styles.loginSide}>
          <div style={styles.loginCard}>
            <div style={styles.loginHeader}>
              <h2 style={styles.loginTitle}>Welcome back</h2>
              <p style={styles.loginSubtitle}>Sign in to your AxonBridge account</p>
            </div>

            <form onSubmit={handleLogin} style={styles.form}>
              {error && (
                <div style={styles.errorAlert}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              <div style={styles.inputGroup}>
                <label style={styles.label} htmlFor="email">Email Address</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="clinician@hospital.org"
                  required
                  style={styles.input}
                />
              </div>

              <div style={styles.inputGroup}>
                <label style={styles.label} htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  style={styles.input}
                />
              </div>

              {showMFA && (
                <div style={{ ...styles.inputGroup, animation: 'fadeInUp 0.3s ease-out' }}>
                  <label style={styles.label} htmlFor="mfa">MFA Code</label>
                  <input
                    id="mfa"
                    type="text"
                    value={mfaCode}
                    onChange={(e) => setMfaCode(e.target.value)}
                    placeholder="6-digit code"
                    maxLength={6}
                    style={{ ...styles.input, letterSpacing: '0.5em', textAlign: 'center' as const }}
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                style={{
                  ...styles.submitButton,
                  opacity: isLoading ? 0.7 : 1,
                }}
              >
                {isLoading ? (
                  <span style={styles.loadingDots}>
                    <span style={{ ...styles.dot, animationDelay: '0s' }} />
                    <span style={{ ...styles.dot, animationDelay: '0.2s' }} />
                    <span style={{ ...styles.dot, animationDelay: '0.4s' }} />
                  </span>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>

            <div style={styles.loginFooter}>
              <p style={styles.footerText}>
                Protected by enterprise-grade encryption
              </p>
              <div style={styles.complianceBadges}>
                <span style={styles.badge}>HIPAA</span>
                <span style={styles.badge}>GDPR</span>
                <span style={styles.badge}>SOC 2</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   Inline Styles (using CSS-in-JS for component scoping)
   ================================================================ */
const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    position: 'relative',
    overflow: 'hidden',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  gradientBg: {
    position: 'absolute',
    inset: 0,
    background: 'linear-gradient(135deg, #0B1120 0%, #111827 30%, #0F172A 60%, #0B1120 100%)',
    zIndex: 0,
  },
  orb: {
    position: 'absolute',
    borderRadius: '50%',
    filter: 'blur(80px)',
    zIndex: 1,
    animation: 'pulse 6s ease-in-out infinite',
  },
  orb1: {
    width: '400px',
    height: '400px',
    background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
    top: '-100px',
    right: '-100px',
  },
  orb2: {
    width: '300px',
    height: '300px',
    background: 'radial-gradient(circle, rgba(6, 182, 212, 0.12) 0%, transparent 70%)',
    bottom: '-50px',
    left: '-50px',
    animationDelay: '2s',
  },
  orb3: {
    width: '200px',
    height: '200px',
    background: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%)',
    top: '40%',
    left: '30%',
    animationDelay: '4s',
  },
  gridPattern: {
    position: 'absolute',
    inset: 0,
    backgroundImage: `
      linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px)
    `,
    backgroundSize: '40px 40px',
    zIndex: 1,
  },
  content: {
    position: 'relative',
    zIndex: 10,
    display: 'flex',
    maxWidth: '1100px',
    width: '100%',
    margin: '0 auto',
    padding: '2rem',
    gap: '4rem',
    alignItems: 'center',
    transition: 'opacity 0.6s ease-out, transform 0.6s ease-out',
  },
  brandingSide: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '2rem',
  },
  logoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  logoIcon: {},
  logoText: {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#F1F5F9',
    letterSpacing: '-0.02em',
  },
  logoSubtext: {
    fontSize: '0.75rem',
    color: '#64748B',
    fontWeight: 500,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.1em',
  },
  brandingContent: {
    marginTop: '1rem',
  },
  brandingTitle: {
    fontSize: '2.5rem',
    fontWeight: 800,
    color: '#F1F5F9',
    lineHeight: 1.2,
    letterSpacing: '-0.03em',
  },
  gradientText: {
    background: 'linear-gradient(135deg, #3B82F6, #06B6D4)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  brandingDescription: {
    marginTop: '1.25rem',
    fontSize: '1.05rem',
    color: '#94A3B8',
    lineHeight: 1.7,
    maxWidth: '460px',
  },
  featureList: {
    marginTop: '2rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.75rem',
  },
  featureItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.6rem 0.9rem',
    borderRadius: '0.5rem',
    background: 'rgba(30, 41, 59, 0.5)',
    border: '1px solid rgba(51, 65, 85, 0.3)',
    animation: 'fadeInUp 0.5s ease-out forwards',
    opacity: 0,
  },
  featureIcon: {
    fontSize: '1.2rem',
  },
  featureText: {
    color: '#CBD5E1',
    fontSize: '0.9rem',
    fontWeight: 500,
  },
  loginSide: {
    flex: '0 0 420px',
    display: 'flex',
    justifyContent: 'center',
  },
  loginCard: {
    width: '100%',
    maxWidth: '420px',
    padding: '2.5rem',
    borderRadius: '1rem',
    background: 'rgba(17, 24, 39, 0.8)',
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(51, 65, 85, 0.4)',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
  },
  loginHeader: {
    marginBottom: '2rem',
    textAlign: 'center' as const,
  },
  loginTitle: {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#F1F5F9',
  },
  loginSubtitle: {
    marginTop: '0.5rem',
    fontSize: '0.875rem',
    color: '#64748B',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1.25rem',
  },
  errorAlert: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.75rem 1rem',
    borderRadius: '0.5rem',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: '#F87171',
    fontSize: '0.875rem',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.375rem',
  },
  label: {
    fontSize: '0.8rem',
    fontWeight: 600,
    color: '#94A3B8',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  input: {
    padding: '0.75rem 1rem',
    borderRadius: '0.5rem',
    border: '1px solid rgba(51, 65, 85, 0.5)',
    background: 'rgba(30, 41, 59, 0.6)',
    color: '#F1F5F9',
    fontSize: '0.95rem',
    outline: 'none',
    transition: 'border-color 0.2s, box-shadow 0.2s',
    width: '100%',
  },
  submitButton: {
    marginTop: '0.5rem',
    padding: '0.875rem',
    borderRadius: '0.5rem',
    border: 'none',
    background: 'linear-gradient(135deg, #3B82F6, #2563EB)',
    color: 'white',
    fontSize: '0.95rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'opacity 0.2s, transform 0.2s, box-shadow 0.2s',
    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '48px',
  },
  loadingDots: {
    display: 'flex',
    gap: '6px',
    alignItems: 'center',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'white',
    animation: 'dotPulse 1.4s ease-in-out infinite',
    display: 'inline-block',
  },
  loginFooter: {
    marginTop: '2rem',
    textAlign: 'center' as const,
    paddingTop: '1.5rem',
    borderTop: '1px solid rgba(51, 65, 85, 0.3)',
  },
  footerText: {
    fontSize: '0.75rem',
    color: '#64748B',
  },
  complianceBadges: {
    marginTop: '0.75rem',
    display: 'flex',
    justifyContent: 'center',
    gap: '0.5rem',
  },
  badge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    background: 'rgba(34, 197, 94, 0.1)',
    border: '1px solid rgba(34, 197, 94, 0.2)',
    color: '#4ADE80',
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.05em',
  },
};
